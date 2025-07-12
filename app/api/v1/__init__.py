from fastapi import APIRouter
from app.api.v1 import auth, users, questions, answers, votes, tags, notifications, mcq, comments, metrics

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(questions.router)
api_router.include_router(answers.router)
api_router.include_router(votes.router)
api_router.include_router(tags.router)
api_router.include_router(notifications.router)
api_router.include_router(mcq.router)
api_router.include_router(comments.router)
api_router.include_router(metrics.router)

