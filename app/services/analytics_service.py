from sqlalchemy.orm import Session

from app.models.attempt import QuestionAttempt, QuizAttempt
from app.models.course import Course
from app.models.learning_profile import LearningProfile
from app.models.topic import Topic
from app.models.user import User
from app.services.learning_profile_service import LearningProfileService


class AnalyticsService:
    @staticmethod
    def get_student_analytics(
        db: Session,
        moodle_user_id: int,
        moodle_course_id: int,
    ):
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

        if not user or not course:
            return user, course, None

        attempts = (
            db.query(QuizAttempt)
            .filter(
                QuizAttempt.user_id == user.id,
                QuizAttempt.course_id == course.id,
            )
            .all()
        )

        total_attempts = len(attempts)

        if total_attempts > 0:
            scores = [
                attempt.score
                for attempt in attempts
                if attempt.score is not None
            ]
            average_score = round(sum(scores) / len(scores), 2) if scores else 0
        else:
            average_score = 0

        question_attempts = (
            db.query(QuestionAttempt)
            .join(QuizAttempt, QuizAttempt.id == QuestionAttempt.quiz_attempt_id)
            .filter(
                QuizAttempt.user_id == user.id,
                QuizAttempt.course_id == course.id,
            )
            .all()
        )

        total_questions = len(question_attempts)
        correct_questions = len([qa for qa in question_attempts if qa.is_correct])

        accuracy_rate = (
            round(correct_questions / total_questions * 100, 2)
            if total_questions > 0
            else 0
        )

        profile = (
            db.query(LearningProfile)
            .filter(
                LearningProfile.user_id == user.id,
                LearningProfile.course_id == course.id,
            )
            .first()
        )

        if not profile:
            profile = LearningProfileService.update_learning_profile(
                db=db,
                user_id=user.id,
                course_id=course.id,
            )

        # MVP: completion_rate tạm tính theo số attempt.
        # Sau này tích hợp Moodle thật sẽ lấy course completion/activity completion.
        completion_rate = min(total_attempts * 20, 100)

        result = {
            "user_id": user.id,
            "course_id": course.id,
            "average_score": average_score,
            "completion_rate": completion_rate,
            "total_attempts": total_attempts,
            "total_questions": total_questions,
            "correct_questions": correct_questions,
            "accuracy_rate": accuracy_rate,
            "overall_level": profile.overall_level if profile else None,
            "topic_mastery": profile.mastery_json if profile else {},
            "weak_topics": profile.weak_topics_json if profile else [],
            "strong_topics": profile.strong_topics_json if profile else [],
        }

        return user, course, result

    @staticmethod
    def get_course_analytics(
        db: Session,
        moodle_course_id: int,
    ):
        course = (
            db.query(Course)
            .filter(Course.moodle_course_id == moodle_course_id)
            .first()
        )

        if not course:
            return None, None

        attempts = (
            db.query(QuizAttempt)
            .filter(QuizAttempt.course_id == course.id)
            .all()
        )

        total_attempts = len(attempts)

        scores = [
            attempt.score
            for attempt in attempts
            if attempt.score is not None
        ]

        average_score = round(sum(scores) / len(scores), 2) if scores else 0

        student_ids = {
            attempt.user_id
            for attempt in attempts
        }

        total_students = len(student_ids)

        profiles = (
            db.query(LearningProfile)
            .filter(LearningProfile.course_id == course.id)
            .all()
        )

        low_performance_students = len([
            profile
            for profile in profiles
            if profile.overall_level == "beginner"
        ])

        topic_rows = (
            db.query(
                Topic.name,
                QuestionAttempt.is_correct,
            )
            .join(QuestionAttempt, QuestionAttempt.topic_id == Topic.id)
            .join(QuizAttempt, QuizAttempt.id == QuestionAttempt.quiz_attempt_id)
            .filter(QuizAttempt.course_id == course.id)
            .all()
        )

        topic_stats_map = {}

        for topic_name, is_correct in topic_rows:
            if topic_name not in topic_stats_map:
                topic_stats_map[topic_name] = {
                    "total_questions": 0,
                    "correct_questions": 0,
                }

            topic_stats_map[topic_name]["total_questions"] += 1

            if is_correct:
                topic_stats_map[topic_name]["correct_questions"] += 1

        topic_stats = []

        for topic_name, stat in topic_stats_map.items():
            total = stat["total_questions"]
            correct = stat["correct_questions"]

            accuracy_rate = round(correct / total * 100, 2) if total > 0 else 0

            topic_stats.append({
                "topic": topic_name,
                "total_questions": total,
                "correct_questions": correct,
                "accuracy_rate": accuracy_rate,
            })

        topic_stats_sorted = sorted(
            topic_stats,
            key=lambda item: item["accuracy_rate"],
        )

        most_failed_topics = [
            item["topic"]
            for item in topic_stats_sorted
            if item["accuracy_rate"] < 50
        ][:3]

        result = {
            "course_id": course.id,
            "total_students": total_students,
            "total_attempts": total_attempts,
            "average_score": average_score,
            "low_performance_students": low_performance_students,
            "most_failed_topics": most_failed_topics,
            "topic_stats": topic_stats,
        }

        return course, result