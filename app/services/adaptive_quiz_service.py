from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.learning_profile import LearningProfile
from app.models.question import Question
from app.models.topic import Topic
from app.models.user import User
from app.services.learning_profile_service import LearningProfileService


class AdaptiveQuizService:
    DIFFICULTY_ORDER = ["easy", "medium", "hard"]

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
    def normalize_difficulty(difficulty: str | None) -> str:
        if difficulty not in AdaptiveQuizService.DIFFICULTY_ORDER:
            return "easy"

        return difficulty

    @staticmethod
    def increase_difficulty(current_difficulty: str) -> str:
        current_difficulty = AdaptiveQuizService.normalize_difficulty(current_difficulty)

        index = AdaptiveQuizService.DIFFICULTY_ORDER.index(current_difficulty)

        if index < len(AdaptiveQuizService.DIFFICULTY_ORDER) - 1:
            return AdaptiveQuizService.DIFFICULTY_ORDER[index + 1]

        return current_difficulty

    @staticmethod
    def decrease_difficulty(current_difficulty: str) -> str:
        current_difficulty = AdaptiveQuizService.normalize_difficulty(current_difficulty)

        index = AdaptiveQuizService.DIFFICULTY_ORDER.index(current_difficulty)

        if index > 0:
            return AdaptiveQuizService.DIFFICULTY_ORDER[index - 1]

        return current_difficulty

    @staticmethod
    def choose_topic(profile: LearningProfile, requested_topic: str | None) -> str | None:
        """
        Nếu người dùng truyền topic thì dùng topic đó.
        Nếu không truyền topic thì ưu tiên topic yếu nhất theo mastery.
        """

        if requested_topic:
            return requested_topic

        mastery = profile.mastery_json or {}

        if not mastery:
            return None

        sorted_topics = sorted(
            mastery.items(),
            key=lambda item: item[1],
        )

        return sorted_topics[0][0] if sorted_topics else None

    @staticmethod
    def choose_difficulty(
        profile: LearningProfile,
        topic_name: str | None,
        current_difficulty: str | None,
        last_answer_correct: bool | None,
    ) -> tuple[str, str]:
        """
        Rule MVP:
        - Nếu có last_answer_correct:
            đúng -> tăng độ khó
            sai -> giảm độ khó
        - Nếu chưa có last_answer_correct:
            dựa trên mastery topic
        """

        current_difficulty = AdaptiveQuizService.normalize_difficulty(current_difficulty)

        if last_answer_correct is True:
            next_difficulty = AdaptiveQuizService.increase_difficulty(current_difficulty)

            return (
                next_difficulty,
                f"Học viên trả lời đúng câu mức {current_difficulty}, hệ thống tăng độ khó lên {next_difficulty}.",
            )

        if last_answer_correct is False:
            next_difficulty = AdaptiveQuizService.decrease_difficulty(current_difficulty)

            return (
                next_difficulty,
                f"Học viên trả lời sai câu mức {current_difficulty}, hệ thống giảm độ khó xuống {next_difficulty}.",
            )

        mastery = profile.mastery_json or {}

        if topic_name and topic_name in mastery:
            mastery_value = mastery[topic_name]

            if mastery_value < 0.5:
                return (
                    "easy",
                    f"Mastery của học viên ở chủ đề {topic_name} thấp, hệ thống chọn câu mức easy.",
                )

            if mastery_value < 0.75:
                return (
                    "medium",
                    f"Mastery của học viên ở chủ đề {topic_name} ở mức trung bình, hệ thống chọn câu mức medium.",
                )

            return (
                "hard",
                f"Mastery của học viên ở chủ đề {topic_name} tốt, hệ thống chọn câu mức hard.",
            )

        return (
            current_difficulty,
            f"Chưa đủ dữ liệu mastery, hệ thống giữ độ khó hiện tại là {current_difficulty}.",
        )

    @staticmethod
    def find_question(
        db: Session,
        course_id: int,
        topic_name: str | None,
        difficulty: str,
    ) -> Question | None:
        query = (
            db.query(Question)
            .join(Topic, Topic.id == Question.topic_id)
            .filter(
                Question.course_id == course_id,
                Question.difficulty == difficulty,
            )
        )

        if topic_name:
            query = query.filter(Topic.name == topic_name)

        question = query.first()

        if question:
            return question

        # Nếu không có câu đúng difficulty thì lấy câu bất kỳ theo topic.
        fallback_query = (
            db.query(Question)
            .join(Topic, Topic.id == Question.topic_id)
            .filter(Question.course_id == course_id)
        )

        if topic_name:
            fallback_query = fallback_query.filter(Topic.name == topic_name)

        return fallback_query.first()

    @staticmethod
    def get_next_question(
        db: Session,
        moodle_user_id: int,
        moodle_course_id: int,
        topic: str | None,
        current_difficulty: str | None,
        last_answer_correct: bool | None,
    ):
        user, course = AdaptiveQuizService.get_user_and_course(
            db=db,
            moodle_user_id=moodle_user_id,
            moodle_course_id=moodle_course_id,
        )

        if not user or not course:
            return user, course, None, None

        profile = AdaptiveQuizService.get_or_create_profile(
            db=db,
            user_id=user.id,
            course_id=course.id,
        )

        selected_topic = AdaptiveQuizService.choose_topic(
            profile=profile,
            requested_topic=topic,
        )

        selected_difficulty, reason = AdaptiveQuizService.choose_difficulty(
            profile=profile,
            topic_name=selected_topic,
            current_difficulty=current_difficulty,
            last_answer_correct=last_answer_correct,
        )

        question = AdaptiveQuizService.find_question(
            db=db,
            course_id=course.id,
            topic_name=selected_topic,
            difficulty=selected_difficulty,
        )

        return user, course, question, reason