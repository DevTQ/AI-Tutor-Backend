from sqlalchemy.orm import Session

from app.models.attempt import QuestionAttempt
from app.models.learning_profile import LearningProfile
from app.models.topic import Topic


class LearningProfileService:
    @staticmethod
    def calculate_mastery(db: Session, user_id: int, course_id: int) -> dict:
        """
        Tính mastery theo từng topic:
        mastery = số câu đúng / tổng số câu đã làm
        """

        rows = (
            db.query(
                Topic.id,
                Topic.name,
                QuestionAttempt.is_correct,
            )
            .join(QuestionAttempt, QuestionAttempt.topic_id == Topic.id)
            .join(QuestionAttempt.quiz_attempt)
            .filter(
                QuestionAttempt.quiz_attempt.has(
                    user_id=user_id,
                    course_id=course_id,
                )
            )
            .all()
        )

        topic_stats = {}

        for topic_id, topic_name, is_correct in rows:
            if topic_name not in topic_stats:
                topic_stats[topic_name] = {
                    "correct": 0,
                    "total": 0,
                }

            topic_stats[topic_name]["total"] += 1

            if is_correct:
                topic_stats[topic_name]["correct"] += 1

        mastery = {}

        for topic_name, stat in topic_stats.items():
            total = stat["total"]
            correct = stat["correct"]

            mastery[topic_name] = round(correct / total, 2) if total > 0 else 0

        return mastery

    @staticmethod
    def classify_profile(mastery: dict) -> tuple[str, list, list]:
        """
        Phân loại trình độ tổng thể, topic yếu, topic mạnh.
        """

        if not mastery:
            return "beginner", [], []

        weak_topics = []
        strong_topics = []

        for topic_name, value in mastery.items():
            if value < 0.5:
                weak_topics.append(topic_name)
            elif value >= 0.75:
                strong_topics.append(topic_name)

        average_mastery = sum(mastery.values()) / len(mastery)

        if average_mastery < 0.5:
            overall_level = "beginner"
        elif average_mastery < 0.75:
            overall_level = "intermediate"
        else:
            overall_level = "advanced"

        return overall_level, weak_topics, strong_topics

    @staticmethod
    def update_learning_profile(db: Session, user_id: int, course_id: int) -> LearningProfile:
        mastery = LearningProfileService.calculate_mastery(
            db=db,
            user_id=user_id,
            course_id=course_id,
        )

        overall_level, weak_topics, strong_topics = LearningProfileService.classify_profile(
            mastery=mastery,
        )

        profile = (
            db.query(LearningProfile)
            .filter(
                LearningProfile.user_id == user_id,
                LearningProfile.course_id == course_id,
            )
            .first()
        )

        if not profile:
            profile = LearningProfile(
                user_id=user_id,
                course_id=course_id,
                overall_level=overall_level,
                mastery_json=mastery,
                weak_topics_json=weak_topics,
                strong_topics_json=strong_topics,
            )
            db.add(profile)
        else:
            profile.overall_level = overall_level
            profile.mastery_json = mastery
            profile.weak_topics_json = weak_topics
            profile.strong_topics_json = strong_topics

        db.commit()
        db.refresh(profile)

        return profile