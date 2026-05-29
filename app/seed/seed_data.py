from app.db.session import SessionLocal
from app.models.course import Course
from app.models.topic import Topic
from app.models.learning_resource import LearningResource
from app.models.question import Question


def get_or_create_course(db):
    course = db.query(Course).filter(
        Course.moodle_course_id == 1001
    ).first()

    if course:
        return course

    course = Course(
        moodle_course_id=1001,
        name="English Adaptive Learning Course",
        shortname="ENG-AI-1001",
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


def get_or_create_topics(db, course):
    topic_names = [
        {
            "name": "Grammar",
            "description": "Ngữ pháp tiếng Anh cơ bản và nâng cao.",
        },
        {
            "name": "Vocabulary",
            "description": "Từ vựng học thuật và từ vựng thông dụng.",
        },
        {
            "name": "Reading",
            "description": "Kỹ năng đọc hiểu văn bản tiếng Anh.",
        },
        {
            "name": "Listening",
            "description": "Kỹ năng nghe hiểu tiếng Anh.",
        },
    ]

    topics = {}

    for item in topic_names:
        topic = db.query(Topic).filter(
            Topic.course_id == course.id,
            Topic.name == item["name"],
        ).first()

        if not topic:
            topic = Topic(
                course_id=course.id,
                name=item["name"],
                description=item["description"],
            )
            db.add(topic)
            db.commit()
            db.refresh(topic)

        topics[item["name"]] = topic

    return topics


def seed_learning_resources(db, course, topics):
    resources = [
        {
            "topic": "Grammar",
            "title": "Ôn tập thì hiện tại hoàn thành",
            "type": "lesson",
            "url": "https://example.com/grammar-present-perfect",
            "difficulty": "easy",
            "description": "Bài học giúp củng cố kiến thức về thì hiện tại hoàn thành.",
        },
        {
            "topic": "Grammar",
            "title": "Luyện tập ngữ pháp mức trung bình",
            "type": "quiz",
            "url": "https://example.com/grammar-medium-quiz",
            "difficulty": "medium",
            "description": "Bài luyện tập ngữ pháp mức trung bình.",
        },
        {
            "topic": "Vocabulary",
            "title": "Từ vựng học thuật cơ bản",
            "type": "lesson",
            "url": "https://example.com/academic-vocabulary-basic",
            "difficulty": "easy",
            "description": "Bài học về các từ vựng học thuật thường gặp.",
        },
        {
            "topic": "Vocabulary",
            "title": "Luyện tập từ vựng nâng cao",
            "type": "quiz",
            "url": "https://example.com/vocabulary-hard-quiz",
            "difficulty": "hard",
            "description": "Bài luyện tập từ vựng mức khó.",
        },
        {
            "topic": "Reading",
            "title": "Kỹ năng đọc tìm ý chính",
            "type": "lesson",
            "url": "https://example.com/reading-main-idea",
            "difficulty": "easy",
            "description": "Bài học về cách xác định ý chính trong đoạn văn.",
        },
        {
            "topic": "Listening",
            "title": "Nghe hiểu hội thoại ngắn",
            "type": "lesson",
            "url": "https://example.com/listening-short-conversation",
            "difficulty": "easy",
            "description": "Bài học luyện nghe hội thoại ngắn.",
        },
    ]

    for item in resources:
        topic = topics[item["topic"]]

        existing = db.query(LearningResource).filter(
            LearningResource.course_id == course.id,
            LearningResource.topic_id == topic.id,
            LearningResource.title == item["title"],
        ).first()

        if existing:
            continue

        resource = LearningResource(
            course_id=course.id,
            topic_id=topic.id,
            title=item["title"],
            type=item["type"],
            url=item["url"],
            difficulty=item["difficulty"],
            description=item["description"],
        )

        db.add(resource)

    db.commit()


def seed_questions(db, course, topics):
    questions = [
        {
            "topic": "Grammar",
            "content": "Choose the correct sentence: I have lived here ___ 2020.",
            "difficulty": "easy",
            "correct_answer": "since",
            "explanation": "Dùng 'since' với mốc thời gian cụ thể.",
        },
        {
            "topic": "Grammar",
            "content": "Choose the correct form: She ___ already finished her homework.",
            "difficulty": "easy",
            "correct_answer": "has",
            "explanation": "Chủ ngữ 'She' dùng 'has' trong thì hiện tại hoàn thành.",
        },
        {
            "topic": "Grammar",
            "content": "Choose the best option: If I ___ more time, I would travel more.",
            "difficulty": "medium",
            "correct_answer": "had",
            "explanation": "Câu điều kiện loại 2 dùng quá khứ đơn ở mệnh đề if.",
        },
        {
            "topic": "Grammar",
            "content": "Identify the correct inversion: Rarely ___ such a beautiful performance.",
            "difficulty": "hard",
            "correct_answer": "have I seen",
            "explanation": "Sau trạng từ phủ định 'Rarely' cần đảo ngữ.",
        },
        {
            "topic": "Vocabulary",
            "content": "Choose the synonym of 'important'.",
            "difficulty": "easy",
            "correct_answer": "significant",
            "explanation": "'Significant' có nghĩa là quan trọng/đáng kể.",
        },
        {
            "topic": "Vocabulary",
            "content": "Choose the best word: The results were highly ___.",
            "difficulty": "medium",
            "correct_answer": "predictable",
            "explanation": "'Predictable' nghĩa là có thể dự đoán được.",
        },
        {
            "topic": "Vocabulary",
            "content": "Choose the word closest in meaning to 'ubiquitous'.",
            "difficulty": "hard",
            "correct_answer": "present everywhere",
            "explanation": "'Ubiquitous' nghĩa là có mặt ở khắp nơi.",
        },
        {
            "topic": "Reading",
            "content": "What is the main idea of a paragraph?",
            "difficulty": "easy",
            "correct_answer": "the central point",
            "explanation": "Main idea là ý chính hoặc thông điệp trung tâm của đoạn văn.",
        },
        {
            "topic": "Reading",
            "content": "Which reading strategy is used to find specific information quickly?",
            "difficulty": "medium",
            "correct_answer": "scanning",
            "explanation": "Scanning là kỹ năng đọc lướt để tìm thông tin cụ thể.",
        },
        {
            "topic": "Listening",
            "content": "What should learners focus on when listening for gist?",
            "difficulty": "easy",
            "correct_answer": "general meaning",
            "explanation": "Listening for gist là nghe để hiểu ý chính chung.",
        },
    ]

    for item in questions:
        topic = topics[item["topic"]]

        existing = db.query(Question).filter(
            Question.course_id == course.id,
            Question.topic_id == topic.id,
            Question.content == item["content"],
        ).first()

        if existing:
            continue

        question = Question(
            course_id=course.id,
            topic_id=topic.id,
            content=item["content"],
            difficulty=item["difficulty"],
            correct_answer=item["correct_answer"],
            explanation=item["explanation"],
            source="backend",
            moodle_question_id=None,
        )

        db.add(question)

    db.commit()


def run_seed():
    db = SessionLocal()

    try:
        course = get_or_create_course(db)
        topics = get_or_create_topics(db, course)

        seed_learning_resources(db, course, topics)
        seed_questions(db, course, topics)

        print("Seed data completed successfully.")
        print(f"Course: {course.name} - ID: {course.id}")
        print(f"Topics: {', '.join(topics.keys())}")

    finally:
        db.close()


if __name__ == "__main__":
    run_seed()