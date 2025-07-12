# StackIt - Q&A Forum Platform Backend

A minimal question-and-answer platform backend built with FastAPI and MongoDB.

## Features

- **User Management**: Registration, authentication, and user profiles
- **Questions & Answers**: Create, read, update, and delete questions and answers
- **Voting System**: Upvote and downvote answers
- **Tagging**: Organize questions with tags
- **Notifications**: Real-time notifications for user interactions
- **MCQ Quiz System**: LLM-based multiple choice questions on selected topics
- **Comments & Threading**: Nested comments on answers for deeper discussions
- **Popularity Metrics**: User reputation, question engagement, and leaderboards
- **Rich Text Support**: Support for rich text formatting in questions and answers

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB with Motor (async driver)
- **ODM**: Beanie
- **Authentication**: JWT tokens
- **Password Hashing**: bcrypt

## Project Structure

```
stackit-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── users.py         # User management endpoints
│   │       ├── questions.py     # Question endpoints
│   │       ├── answers.py       # Answer endpoints
│   │       ├── votes.py         # Voting endpoints
│   │       ├── tags.py          # Tag endpoints
│   │       ├── notifications.py # Notification endpoints
│   │       └── mcq.py           # MCQ quiz endpoints
│   ├── core/
│   │   ├── config.py            # Application configuration
│   │   ├── security.py          # Security utilities
│   │   └── auth.py              # Authentication dependencies
│   ├── db/
│   │   └── database.py          # Database connection
│   ├── models/                  # Database models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   ├── utils/
│   │   └── logger.py            # Logging utility
│   └── main.py                  # FastAPI application
├── logs/                        # Application logs
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables example
├── run.py                       # Application runner
└── README.md                    # This file
```

## Setup Instructions

### 1. Clone and Navigate

```bash
cd stackit-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Update the `.env` file with your MongoDB connection string and other settings:

```env
MONGODB_URL=mongodb+srv://your-connection-string
DATABASE_NAME=stackit_db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 5. Run the Application

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/token` - OAuth2 token endpoint
- `GET /api/v1/auth/me` - Get current user info

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/{user_id}` - Get user by ID

### Questions
- `POST /api/v1/questions/` - Create question
- `GET /api/v1/questions/` - Get questions (with filtering)
- `GET /api/v1/questions/{question_id}` - Get specific question
- `PUT /api/v1/questions/{question_id}` - Update question
- `DELETE /api/v1/questions/{question_id}` - Delete question

### Answers
- `POST /api/v1/answers/` - Create answer
- `GET /api/v1/answers/question/{question_id}` - Get answers for question
- `PUT /api/v1/answers/{answer_id}` - Update answer
- `DELETE /api/v1/answers/{answer_id}` - Delete answer
- `POST /api/v1/answers/accept` - Accept answer

### Voting
- `POST /api/v1/votes/` - Vote on answer
- `GET /api/v1/votes/answer/{answer_id}/stats` - Get vote statistics
- `DELETE /api/v1/votes/answer/{answer_id}` - Remove vote

### Tags
- `GET /api/v1/tags/` - Get all tags
- `GET /api/v1/tags/popular` - Get popular tags
- `GET /api/v1/tags/search` - Search tags
- `GET /api/v1/tags/{tag_name}` - Get tag details

### Notifications
- `GET /api/v1/notifications/` - Get user notifications
- `GET /api/v1/notifications/stats` - Get notification statistics
- `PUT /api/v1/notifications/{notification_id}/read` - Mark as read
- `PUT /api/v1/notifications/mark-all-read` - Mark all as read

### MCQ Quiz
- `POST /api/v1/mcq/quiz` - Create new quiz
- `GET /api/v1/mcq/quiz/{quiz_id}/questions` - Get quiz questions
- `POST /api/v1/mcq/quiz/submit` - Submit quiz answers
- `GET /api/v1/mcq/my-quizzes` - Get user's quizzes
- `GET /api/v1/mcq/topics` - Get available topics

### Comments & Threading
- `POST /api/v1/comments/` - Create comment on answer
- `GET /api/v1/comments/answer/{answer_id}` - Get comments for answer
- `GET /api/v1/comments/answer/{answer_id}/threads` - Get nested comment threads
- `PUT /api/v1/comments/{comment_id}` - Update comment
- `DELETE /api/v1/comments/{comment_id}` - Delete comment and replies
- `POST /api/v1/comments/{comment_id}/reply` - Reply to comment

### Metrics & Analytics
- `GET /api/v1/metrics/users/popular` - Get popular users by reputation
- `GET /api/v1/metrics/users/active` - Get most active users this week
- `GET /api/v1/metrics/users/{user_id}` - Get user metrics
- `GET /api/v1/metrics/questions/popular` - Get popular questions
- `GET /api/v1/metrics/questions/top` - Get top questions by votes
- `GET /api/v1/metrics/questions/trending` - Get trending questions
- `GET /api/v1/metrics/engagement` - Get platform engagement stats
- `GET /api/v1/metrics/leaderboard/reputation` - Get reputation leaderboard
- `GET /api/v1/metrics/leaderboard/activity` - Get activity leaderboard

## User Roles

- **Guest**: Can view questions and answers
- **User**: Can register, login, post questions/answers, vote
- **Admin**: Can moderate content and access admin endpoints

## Core Features

### Rich Text Editor Support
Questions and answers support rich text formatting including:
- Bold, Italic, Strikethrough
- Numbered lists, Bullet points
- Emoji insertion
- Hyperlink insertion
- Image upload
- Text alignment

### Voting & Answer Acceptance
- Users can upvote/downvote answers
- Question owners can mark one answer as accepted
- Vote statistics are tracked and displayed

### Notification System
Users receive notifications for:
- Someone answers their question
- Someone comments on their answer
- Someone mentions them using @username
- Their answer receives votes

### MCQ Quiz System
- LLM-based multiple choice questions
- Topics include Python, JavaScript, React, and more
- Automatic scoring and statistics tracking
- User progress tracking per topic

### Comments & Threading System
- Nested comments on answers for deeper discussions
- Reply to specific comments to create threads
- Recursive comment deletion (deletes all replies)
- Comment search and user comment history

### Popularity Metrics & Analytics
- User reputation scoring based on activity and engagement
- Question popularity based on votes, answers, and comments
- Leaderboards for top users by reputation and activity
- Platform engagement statistics
- Trending questions and popular content discovery

## Development

### Adding New Features

1. Create models in `app/models/`
2. Create schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Create API endpoints in `app/api/v1/`
5. Update the router in `app/api/v1/__init__.py`

### Database

The application uses MongoDB with Beanie ODM. Models are automatically indexed and validated.

### Logging

All application logs are written to `logs/app.log` and also displayed in the console.

## Production Deployment

1. Set `DEBUG=False` in environment variables
2. Use a production WSGI server like Gunicorn
3. Set up proper MongoDB connection with authentication
4. Configure proper CORS origins
5. Set up SSL/TLS certificates
6. Use environment variables for sensitive configuration

## License

This project is open source and available under the MIT License.

