from sqlalchemy.orm import Session

from app.models.attempt import QuestionAttempt, QuizAttempt
from app.models.course import Course
from app.models.question import Question
from app.models.topic import Topic
from app.models.user import User
from app.schemas.moodle_schema import MoodleAttemptSyncIn
from app.services.learning_profile_service import LearningProfileService


class MoodleSyncService:
    @staticmethod
    def get_or_create_user(db: Session, payload: MoodleAttemptSyncIn) -> User:
        user = (
            db.query(User)
            .filter(User.moodle_user_id == payload.moodle_user_id)
            .first()
        )

        if not user:
            user = User(
                moodle_user_id=payload.moodle_user_id,
                fullname=payload.fullname,
                email=payload.email,
                role=payload.role or "student",
            )
            db.add(user)
        else:
            user.fullname = payload.fullname or user.fullname
            user.email = payload.email or user.email
            user.role = payload.role or user.role

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_or_create_course(db: Session, payload: MoodleAttemptSyncIn) -> Course:
        course = (
            db.query(Course)
            .filter(Course.moodle_course_id == payload.moodle_course_id)
            .first()
        )

        if not course:
            course = Course(
                moodle_course_id=payload.moodle_course_id,
                name=payload.course_name or f"Moodle Course {payload.moodle_course_id}",
                shortname=payload.course_shortname,
            )
            db.add(course)
        else:
            course.name = payload.course_name or course.name
            course.shortname = payload.course_shortname or course.shortname

        db.commit()
        db.refresh(course)

        return course

    @staticmethod
    def get_or_create_topic(db: Session, course: Course, topic_name: str) -> Topic:
        topic = (
            db.query(Topic)
            .filter(
                Topic.course_id == course.id,
                Topic.name == topic_name,
            )
            .first()
        )

        if not topic:
            topic = Topic(
                course_id=course.id,
                name=topic_name,
                description=f"Auto-created topic: {topic_name}",
            )
            db.add(topic)
            db.commit()
            db.refresh(topic)

        return topic

    @staticmethod
    def get_or_create_question(
        db: Session,
        course: Course,
        topic: Topic,
        question_data,
    ) -> Question | None:
        """
        Nếu question_id backend có sẵn thì lấy theo id.
        Nếu có moodle_question_id thì tìm theo moodle_question_id.
        Nếu chưa có thì tạo question tối giản.
        """

        if question_data.question_id:
            question = (
                db.query(Question)
                .filter(Question.id == question_data.question_id)
                .first()
            )
            if question:
                return question

        if question_data.moodle_question_id:
            question = (
                db.query(Question)
                .filter(
                    Question.course_id == course.id,
                    Question.moodle_question_id == question_data.moodle_question_id,
                )
                .first()
            )
            if question:
                return question

        if not question_data.content:
            return None

        question = Question(
            course_id=course.id,
            topic_id=topic.id,
            content=question_data.content,
            difficulty=question_data.difficulty,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            source="moodle" if question_data.moodle_question_id else "backend",
            moodle_question_id=question_data.moodle_question_id,
        )

        db.add(question)
        db.commit()
        db.refresh(question)

        return question

    @staticmethod
    def sync_attempt(db: Session, payload: MoodleAttemptSyncIn):
        user = MoodleSyncService.get_or_create_user(db, payload)
        course = MoodleSyncService.get_or_create_course(db, payload)

        # Nếu moodle_attempt_id đã tồn tại thì không tạo trùng.
        if payload.moodle_attempt_id:
            existing_attempt = (
                db.query(QuizAttempt)
                .filter(QuizAttempt.moodle_attempt_id == payload.moodle_attempt_id)
                .first()
            )

            if existing_attempt:
                profile = LearningProfileService.update_learning_profile(
                    db=db,
                    user_id=user.id,
                    course_id=course.id,
                )

                return existing_attempt, profile

        quiz_attempt = QuizAttempt(
            user_id=user.id,
            course_id=course.id,
            moodle_quiz_id=payload.moodle_quiz_id,
            moodle_attempt_id=payload.moodle_attempt_id,
            score=payload.score,
            max_score=payload.max_score,
            time_spent=payload.time_spent,
        )

        db.add(quiz_attempt)
        db.commit()
        db.refresh(quiz_attempt)

        for question_data in payload.questions:
            topic = MoodleSyncService.get_or_create_topic(
                db=db,
                course=course,
                topic_name=question_data.topic,
            )

            question = MoodleSyncService.get_or_create_question(
                db=db,
                course=course,
                topic=topic,
                question_data=question_data,
            )

            question_attempt = QuestionAttempt(
                quiz_attempt_id=quiz_attempt.id,
                question_id=question.id if question else None,
                topic_id=topic.id,
                difficulty=question_data.difficulty,
                is_correct=question_data.is_correct,
                time_spent=question_data.time_spent,
            )

            db.add(question_attempt)

        db.commit()

        profile = LearningProfileService.update_learning_profile(
            db=db,
            user_id=user.id,
            course_id=course.id,
        )

        return quiz_attempt, profile