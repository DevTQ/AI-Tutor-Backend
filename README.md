# AI Tutor Backend

Backend MVP cho đề tài:

**Xây dựng hệ thống trợ giảng AI cá nhân hóa học tập tích hợp Moodle LMS dựa trên adaptive quiz và learning analytics**

## 1. Công nghệ sử dụng

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- pgAdmin 4
- Swagger UI

## 2. Chức năng chính

Backend hiện hỗ trợ:

- Đồng bộ kết quả quiz/attempt từ Moodle hoặc dữ liệu mock
- Tính learning profile theo topic
- Recommendation engine rule-based
- Learning analytics cho học viên và khóa học
- Adaptive quiz rule-based
- Chatbot rule-based
- API key bảo vệ endpoint

## 3. Cấu trúc project

```text
ai-tutor-backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── seed/
│   ├── services/
│   ├── config.py
│   └── main.py
├── .env
├── requirements.txt
└── README.md
```

## 4. Cài đặt môi trường

Tạo môi trường ảo:
python -m venv venv

Kích hoạt môi trường ảo:
.\venv\Scripts\activate

Cài thư viện:
pip install -r requirements.txt

## Cấu hình .env
Tạo file .env:
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ai_tutor_db
API_SECRET_KEY=''
BACKEND_API_KEY=''
ENABLE_API_KEY=false

Ghi chú:
Khi dev có thể để ENABLE_API_KEY=false
Khi demo/bảo vệ nên để ENABLE_API_KEY=true

## 6. Chạy backend
uvicorn app.main:app --reload

Mở Swagger:
http://127.0.0.1:8000/docs

## 7. Seed dữ liệu mẫu
python -m app.seed.seed_data

Dữ liệu mẫu gồm:
Course: English Adaptive Learning Course
Topics: Grammar, Vocabulary, Reading, Listening
Learning resources
Questions theo difficulty: easy, medium, hard

## 8. Danh sách API chính
Moodle Sync: POST /api/moodle/sync-attempt
Learning Profile: GET /api/learning-profile/{moodle_user_id}?moodle_course_id=1001
Recommendation: GET /api/recommendations?moodle_user_id=101&moodle_course_id=1001
Analytics: GET /api/analytics/student/{moodle_user_id}?moodle_course_id=1001, GET /api/analytics/course/{moodle_course_id}
Adaptive Quiz: POST /api/adaptive-quiz/next-question
Chatbot: POST /api/chatbot/ask

## 9. Header API Key
X-API-Key: change_me

## 10. Luồng xử lý chính
Quiz attempt data
→ Sync attempt API
→ Question attempts
→ Learning profile
→ Recommendation
→ Analytics
→ Adaptive quiz
→ Chatbot

## 11. Ghi chú MVP
Hiện tại hệ thống đang ở mức MVP:
Chatbot đang rule-based
Recommendation đang rule-based
Adaptive quiz đang rule-based
Completion rate đang tạm tính theo số attempt
Chưa tích hợp Moodle plugin thật
Chưa dùng LLM/RAG

## Bước 12.4: Tạo file test API mẫu
Tạo thư mục:

```powershell
New-Item -ItemType Directory -Path docs -Force
New-Item -ItemType File -Path docs\api-test.http -Force

file: docs/api-test.http
@baseUrl = http://127.0.0.1:8000
@apiKey = change_me

### Health check
GET {{baseUrl}}/

### DB health check
GET {{baseUrl}}/health/db

### Sync attempt
POST {{baseUrl}}/api/moodle/sync-attempt
Content-Type: application/json
X-API-Key: {{apiKey}}

{
  "moodle_user_id": 101,
  "fullname": "Nguyen Van A",
  "email": "nguyenvana@example.com",
  "role": "student",
  "moodle_course_id": 1001,
  "course_name": "English Adaptive Learning Course",
  "course_shortname": "ENG-AI-1001",
  "moodle_quiz_id": 501,
  "moodle_attempt_id": 9003,
  "score": 6.5,
  "max_score": 10,
  "time_spent": 1200,
  "questions": [
    {
      "question_id": 1,
      "topic": "Grammar",
      "difficulty": "easy",
      "is_correct": true,
      "time_spent": 45
    },
    {
      "question_id": 2,
      "topic": "Grammar",
      "difficulty": "easy",
      "is_correct": false,
      "time_spent": 60
    },
    {
      "question_id": 5,
      "topic": "Vocabulary",
      "difficulty": "easy",
      "is_correct": true,
      "time_spent": 40
    },
    {
      "question_id": 8,
      "topic": "Reading",
      "difficulty": "easy",
      "is_correct": false,
      "time_spent": 70
    }
  ]
}

### Learning profile
GET {{baseUrl}}/api/learning-profile/101?moodle_course_id=1001
X-API-Key: {{apiKey}}

### Recommendations
GET {{baseUrl}}/api/recommendations?moodle_user_id=101&moodle_course_id=1001
X-API-Key: {{apiKey}}

### Student analytics
GET {{baseUrl}}/api/analytics/student/101?moodle_course_id=1001
X-API-Key: {{apiKey}}

### Course analytics
GET {{baseUrl}}/api/analytics/course/1001
X-API-Key: {{apiKey}}

### Adaptive quiz next question
POST {{baseUrl}}/api/adaptive-quiz/next-question
Content-Type: application/json
X-API-Key: {{apiKey}}

{
  "moodle_user_id": 101,
  "moodle_course_id": 1001,
  "topic": "Grammar",
  "current_difficulty": "medium",
  "last_answer_correct": false
}

### Chatbot ask weak topics
POST {{baseUrl}}/api/chatbot/ask
Content-Type: application/json
X-API-Key: {{apiKey}}

{
  "moodle_user_id": 101,
  "moodle_course_id": 1001,
  "message": "Em đang yếu phần nào?"
}

### Chatbot ask recommendation
POST {{baseUrl}}/api/chatbot/ask
Content-Type: application/json
X-API-Key: {{apiKey}}

{
  "moodle_user_id": 101,
  "moodle_course_id": 1001,
  "message": "Em nên học gì tiếp?"
}