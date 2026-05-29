from sqlalchemy.orm import Session

from app.models.chatbot_log import ChatbotLog
from app.models.course import Course
from app.models.learning_profile import LearningProfile
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.services.learning_profile_service import LearningProfileService
from app.services.recommendation_service import RecommendationService


class ChatbotService:
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
    def detect_intent(message: str) -> str:
        text = message.lower().strip()

        weak_keywords = [
            "yếu",
            "chưa tốt",
            "kém",
            "sai nhiều",
            "phần nào",
            "mảng nào",
            "topic nào",
        ]

        recommendation_keywords = [
            "học gì",
            "học tiếp",
            "ôn gì",
            "luyện gì",
            "gợi ý",
            "đề xuất",
            "nên học",
            "nên làm",
        ]

        score_keywords = [
            "điểm",
            "kết quả",
            "tiến độ",
            "analytics",
            "thống kê",
            "bao nhiêu",
        ]

        strong_keywords = [
            "mạnh",
            "tốt phần nào",
            "giỏi phần nào",
            "làm tốt",
        ]

        if any(keyword in text for keyword in weak_keywords):
            return "weak_topics"

        if any(keyword in text for keyword in recommendation_keywords):
            return "recommendations"

        if any(keyword in text for keyword in score_keywords):
            return "analytics"

        if any(keyword in text for keyword in strong_keywords):
            return "strong_topics"

        return "general"

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
    def build_weak_topics_answer(profile: LearningProfile) -> str:
        weak_topics = profile.weak_topics_json or {}
        mastery = profile.mastery_json or {}

        if not mastery:
            return (
                "Hiện tại bạn chưa có đủ dữ liệu học tập để xác định điểm yếu. "
                "Bạn hãy làm một bài quiz trước để hệ thống phân tích năng lực nhé."
            )

        if not weak_topics:
            return (
                "Hiện tại hệ thống chưa phát hiện chủ đề nào quá yếu. "
                "Bạn có thể tiếp tục luyện tập để duy trì kết quả học tập."
            )

        topic_texts = []

        for topic in weak_topics:
            mastery_value = mastery.get(topic, 0)
            percent = int(mastery_value * 100)
            topic_texts.append(f"{topic} ({percent}%)")

        return (
            "Bạn đang cần cải thiện các chủ đề sau: "
            + ", ".join(topic_texts)
            + ". Hệ thống khuyến nghị bạn nên ôn lại kiến thức nền và làm bài luyện tập mức dễ/trung bình cho các chủ đề này."
        )

    @staticmethod
    def build_strong_topics_answer(profile: LearningProfile) -> str:
        strong_topics = profile.strong_topics_json or {}
        mastery = profile.mastery_json or {}

        if not mastery:
            return (
                "Hiện tại bạn chưa có đủ dữ liệu học tập để xác định điểm mạnh. "
                "Bạn hãy làm thêm quiz để hệ thống đánh giá chính xác hơn."
            )

        if not strong_topics:
            return (
                "Hiện tại hệ thống chưa xác định được chủ đề nổi trội rõ ràng. "
                "Bạn nên tiếp tục luyện tập thêm để tăng độ tin cậy của kết quả."
            )

        topic_texts = []

        for topic in strong_topics:
            mastery_value = mastery.get(topic, 0)
            percent = int(mastery_value * 100)
            topic_texts.append(f"{topic} ({percent}%)")

        return (
            "Bạn đang làm tốt các chủ đề: "
            + ", ".join(topic_texts)
            + ". Bạn có thể thử các bài luyện tập khó hơn để nâng cao năng lực."
        )

    @staticmethod
    def build_recommendation_answer(
        db: Session,
        moodle_user_id: int,
        moodle_course_id: int,
    ) -> str:
        user, course, recommendations = RecommendationService.generate_recommendations(
            db=db,
            moodle_user_id=moodle_user_id,
            moodle_course_id=moodle_course_id,
        )

        if not user or not course:
            return "Không tìm thấy thông tin học viên hoặc khóa học."

        if not recommendations:
            return (
                "Hiện tại hệ thống chưa có gợi ý học tập phù hợp. "
                "Bạn hãy làm thêm quiz để hệ thống có dữ liệu phân tích tốt hơn."
            )

        lines = ["Dựa trên kết quả học tập hiện tại, bạn nên ưu tiên:"]

        for index, item in enumerate(recommendations[:3], start=1):
            lines.append(f"{index}. {item.title} - {item.reason}")

        return "\n".join(lines)

    @staticmethod
    def build_analytics_answer(
        db: Session,
        moodle_user_id: int,
        moodle_course_id: int,
    ) -> str:
        user, course, result = AnalyticsService.get_student_analytics(
            db=db,
            moodle_user_id=moodle_user_id,
            moodle_course_id=moodle_course_id,
        )

        if not user:
            return "Không tìm thấy thông tin học viên."

        if not course:
            return "Không tìm thấy thông tin khóa học."

        if not result:
            return "Hiện tại chưa có dữ liệu học tập để thống kê."

        return (
            f"Thống kê học tập hiện tại của bạn:\n"
            f"- Điểm trung bình: {result['average_score']}\n"
            f"- Số lần làm bài: {result['total_attempts']}\n"
            f"- Tỷ lệ trả lời đúng: {result['accuracy_rate']}%\n"
            f"- Tiến độ ước tính: {result['completion_rate']}%\n"
            f"- Trình độ hiện tại: {result['overall_level']}"
        )

    @staticmethod
    def build_general_answer(profile: LearningProfile) -> str:
        overall_level = profile.overall_level or "beginner"
        weak_topics = profile.weak_topics_json or []

        if weak_topics:
            return (
                f"Bạn đang ở mức {overall_level}. "
                f"Các chủ đề nên ưu tiên cải thiện là: {', '.join(weak_topics)}. "
                f"Bạn có thể hỏi: 'Em nên học gì tiếp?' để nhận gợi ý cụ thể."
            )

        return (
            f"Bạn đang ở mức {overall_level}. "
            f"Bạn có thể hỏi tôi về điểm yếu, tiến độ học tập hoặc bài học nên học tiếp."
        )

    @staticmethod
    def ask(
        db: Session,
        moodle_user_id: int,
        moodle_course_id: int,
        message: str,
    ):
        user, course = ChatbotService.get_user_and_course(
            db=db,
            moodle_user_id=moodle_user_id,
            moodle_course_id=moodle_course_id,
        )

        if not user or not course:
            return user, course, None, None

        profile = ChatbotService.get_or_create_profile(
            db=db,
            user_id=user.id,
            course_id=course.id,
        )

        intent = ChatbotService.detect_intent(message)

        if intent == "weak_topics":
            answer = ChatbotService.build_weak_topics_answer(profile)

        elif intent == "strong_topics":
            answer = ChatbotService.build_strong_topics_answer(profile)

        elif intent == "recommendations":
            answer = ChatbotService.build_recommendation_answer(
                db=db,
                moodle_user_id=moodle_user_id,
                moodle_course_id=moodle_course_id,
            )

        elif intent == "analytics":
            answer = ChatbotService.build_analytics_answer(
                db=db,
                moodle_user_id=moodle_user_id,
                moodle_course_id=moodle_course_id,
            )

        else:
            answer = ChatbotService.build_general_answer(profile)

        log = ChatbotLog(
            user_id=user.id,
            course_id=course.id,
            message=message,
            answer=answer,
            intent=intent,
        )

        db.add(log)
        db.commit()
        db.refresh(log)

        return user, course, answer, intent