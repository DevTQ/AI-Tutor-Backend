from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.learning_profile import LearningProfile
from app.models.learning_resource import LearningResource
from app.models.recommendation import Recommendation
from app.models.topic import Topic
from app.models.user import User
from app.services.learning_profile_service import LearningProfileService


class RecommendationService:
    @staticmethod
    def get_user_and_course(db: Session, moodle_user_id: int, moodle_course_id: int):
        user = (
            db.query(User)
            .filter(User.moodle_user_id == moodle_user_id)
            .first()
        )

        course = (
            db.query(Course)
            .filter(Course.moodle_course_id == moodle_course_id)
            .first()
        )

        return user, course

    @staticmethod
    def get_or_create_profile(db: Session, user_id: int, course_id: int) -> LearningProfile:
        profile = (
            db.query(LearningProfile)
            .filter(
                LearningProfile.user_id == user_id,
                LearningProfile.course_id == course_id,
            )
            .first()
        )

        if not profile:
            profile = LearningProfileService.update_learning_profile(
                db=db,
                user_id=user_id,
                course_id=course_id,
            )

        return profile

    @staticmethod
    def get_target_difficulty(mastery_value: float) -> str:
        if mastery_value < 0.5:
            return "easy"

        if mastery_value < 0.75:
            return "medium"

        return "hard"

    @staticmethod
    def build_reason(topic_name: str, mastery_value: float, difficulty: str) -> str:
        percent = int(mastery_value * 100)

        if mastery_value < 0.5:
            return (
                f"Bạn đang yếu chủ đề {topic_name} với mức độ thành thạo khoảng {percent}%. "
                f"Hệ thống gợi ý tài liệu mức {difficulty} để củng cố kiến thức nền."
            )

        if mastery_value < 0.75:
            return (
                f"Bạn đang ở mức trung bình với chủ đề {topic_name}, mức độ thành thạo khoảng {percent}%. "
                f"Hệ thống gợi ý bài luyện tập mức {difficulty} để cải thiện thêm."
            )

        return (
            f"Bạn đang học tốt chủ đề {topic_name}, mức độ thành thạo khoảng {percent}%. "
            f"Hệ thống gợi ý nội dung mức {difficulty} để nâng cao năng lực."
        )

    @staticmethod
    def find_resource(
        db: Session,
        course_id: int,
        topic_name: str,
        difficulty: str,
    ) -> LearningResource | None:
        topic = (
            db.query(Topic)
            .filter(
                Topic.course_id == course_id,
                Topic.name == topic_name,
            )
            .first()
        )

        if not topic:
            return None

        resource = (
            db.query(LearningResource)
            .filter(
                LearningResource.course_id == course_id,
                LearningResource.topic_id == topic.id,
                LearningResource.difficulty == difficulty,
            )
            .first()
        )

        if resource:
            return resource

        # Nếu không có đúng difficulty thì lấy resource bất kỳ trong topic.
        return (
            db.query(LearningResource)
            .filter(
                LearningResource.course_id == course_id,
                LearningResource.topic_id == topic.id,
            )
            .first()
        )

    @staticmethod
    def create_recommendation_if_not_exists(
        db: Session,
        user_id: int,
        course_id: int,
        resource: LearningResource,
        reason: str,
    ) -> Recommendation:
        existing = (
            db.query(Recommendation)
            .filter(
                Recommendation.user_id == user_id,
                Recommendation.course_id == course_id,
                Recommendation.resource_id == resource.id,
                Recommendation.status == "active",
            )
            .first()
        )

        if existing:
            return existing

        recommendation = Recommendation(
            user_id=user_id,
            course_id=course_id,
            resource_id=resource.id,
            type=resource.type,
            title=resource.title,
            reason=reason,
            status="active",
        )

        db.add(recommendation)
        db.commit()
        db.refresh(recommendation)

        return recommendation

    @staticmethod
    def generate_recommendations(
        db: Session,
        moodle_user_id: int,
        moodle_course_id: int,
    ) -> tuple[User | None, Course | None, list[Recommendation]]:
        user, course = RecommendationService.get_user_and_course(
            db=db,
            moodle_user_id=moodle_user_id,
            moodle_course_id=moodle_course_id,
        )

        if not user or not course:
            return user, course, []

        profile = RecommendationService.get_or_create_profile(
            db=db,
            user_id=user.id,
            course_id=course.id,
        )

        mastery = profile.mastery_json or {}

        recommendations = []

        # Nếu chưa có dữ liệu mastery thì gợi ý resource dễ đầu tiên trong course.
        if not mastery:
            resources = (
                db.query(LearningResource)
                .filter(
                    LearningResource.course_id == course.id,
                    LearningResource.difficulty == "easy",
                )
                .limit(3)
                .all()
            )

            for resource in resources:
                reason = "Bạn chưa có đủ dữ liệu học tập. Hệ thống gợi ý nội dung cơ bản để bắt đầu."
                recommendation = RecommendationService.create_recommendation_if_not_exists(
                    db=db,
                    user_id=user.id,
                    course_id=course.id,
                    resource=resource,
                    reason=reason,
                )
                recommendations.append(recommendation)

            return user, course, recommendations

        # Ưu tiên topic yếu trước, sau đó topic trung bình, rồi topic mạnh.
        sorted_topics = sorted(
            mastery.items(),
            key=lambda item: item[1],
        )

        for topic_name, mastery_value in sorted_topics:
            difficulty = RecommendationService.get_target_difficulty(mastery_value)

            resource = RecommendationService.find_resource(
                db=db,
                course_id=course.id,
                topic_name=topic_name,
                difficulty=difficulty,
            )

            if not resource:
                continue

            reason = RecommendationService.build_reason(
                topic_name=topic_name,
                mastery_value=mastery_value,
                difficulty=difficulty,
            )

            recommendation = RecommendationService.create_recommendation_if_not_exists(
                db=db,
                user_id=user.id,
                course_id=course.id,
                resource=resource,
                reason=reason,
            )

            recommendations.append(recommendation)

        return user, course, recommendations

    @staticmethod
    def format_recommendation(item: Recommendation) -> dict:
        resource = item.resource
        topic_name = resource.topic.name if resource and resource.topic else None

        return {
            "id": item.id,
            "type": item.type,
            "title": item.title,
            "reason": item.reason,
            "status": item.status,
            "resource_id": item.resource_id,
            "resource_url": resource.url if resource else None,
            "difficulty": resource.difficulty if resource else None,
            "topic": topic_name,
        }