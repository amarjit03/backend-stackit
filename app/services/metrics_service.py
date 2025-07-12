from typing import List, Dict
from datetime import datetime, timedelta
from app.models.user import User
from app.models.question import Question
from app.models.answer import Answer
from app.models.vote import Vote
from app.models.comment import Comment
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MetricsService:
    
    @staticmethod
    async def get_user_metrics(user_id: str) -> Dict:
        """Get comprehensive metrics for a user"""
        user = await User.get(user_id)
        if not user:
            return None
        
        # Count user's questions
        total_questions = await Question.find(Question.user_id == user_id).count()
        
        # Count user's answers
        total_answers = await Answer.find(Answer.user_id == user_id).count()
        
        # Count accepted answers
        accepted_answers = await Answer.find({
            "user_id": user_id,
            "is_accepted": True
        }).count()
        
        # Count user's comments
        total_comments = await Comment.find(Comment.user_id == user_id).count()
        
        # Calculate votes received on user's answers
        user_answers = await Answer.find(Answer.user_id == user_id).to_list()
        total_votes_received = 0
        for answer in user_answers:
            votes = await Vote.find(Vote.answer_id == answer.id).to_list()
            total_votes_received += sum(vote.value for vote in votes)
        
        # Calculate reputation score
        reputation_score = (
            total_questions * 5 +
            total_answers * 10 +
            accepted_answers * 25 +
            max(0, total_votes_received) * 2 +
            total_comments * 1
        )
        
        # Get last activity (most recent question, answer, or comment)
        last_activity = None
        recent_question = await Question.find(Question.user_id == user_id)\
            .sort(-Question.created_at).limit(1).to_list()
        recent_answer = await Answer.find(Answer.user_id == user_id)\
            .sort(-Answer.created_at).limit(1).to_list()
        recent_comment = await Comment.find(Comment.user_id == user_id)\
            .sort(-Comment.created_at).limit(1).to_list()
        
        activities = []
        if recent_question:
            activities.append(recent_question[0].created_at)
        if recent_answer:
            activities.append(recent_answer[0].created_at)
        if recent_comment:
            activities.append(recent_comment[0].created_at)
        
        if activities:
            last_activity = max(activities)
        
        return {
            "user_id": user_id,
            "username": user.username,
            "email": user.email,
            "total_questions": total_questions,
            "total_answers": total_answers,
            "total_votes_received": total_votes_received,
            "total_comments": total_comments,
            "accepted_answers": accepted_answers,
            "reputation_score": reputation_score,
            "join_date": user.created_at,
            "last_activity": last_activity
        }
    
    @staticmethod
    async def get_popular_users(limit: int = 20) -> List[Dict]:
        """Get most popular users by reputation score"""
        users = await User.find_all().to_list()
        user_metrics = []
        
        for user in users:
            metrics = await MetricsService.get_user_metrics(user.id)
            if metrics:
                user_metrics.append({
                    "user_id": user.id,
                    "username": user.username,
                    "reputation_score": metrics["reputation_score"],
                    "total_questions": metrics["total_questions"],
                    "total_answers": metrics["total_answers"],
                    "accepted_answers": metrics["accepted_answers"],
                    "total_votes_received": metrics["total_votes_received"]
                })
        
        # Sort by reputation score
        user_metrics.sort(key=lambda x: x["reputation_score"], reverse=True)
        return user_metrics[:limit]
    
    @staticmethod
    async def get_question_metrics(question_id: str) -> Dict:
        """Get comprehensive metrics for a question"""
        question = await Question.get(question_id)
        if not question:
            return None
        
        user = await User.get(question.user_id)
        if not user:
            return None
        
        # Count answers
        answer_count = await Answer.find(Answer.question_id == question_id).count()
        
        # Calculate vote score for all answers
        answers = await Answer.find(Answer.question_id == question_id).to_list()
        vote_score = 0
        for answer in answers:
            votes = await Vote.find(Vote.answer_id == answer.id).to_list()
            vote_score += sum(vote.value for vote in votes)
        
        # Count comments on all answers
        comment_count = 0
        for answer in answers:
            comment_count += await Comment.find(Comment.answer_id == answer.id).count()
        
        # Check if has accepted answer
        has_accepted_answer = await Answer.find_one({
            "question_id": question_id,
            "is_accepted": True
        }) is not None
        
        # Get last activity (most recent answer or comment)
        last_activity = question.created_at
        if answers:
            latest_answer = max(answers, key=lambda x: x.created_at)
            last_activity = max(last_activity, latest_answer.created_at)
        
        return {
            "question_id": question_id,
            "title": question.title,
            "user_id": question.user_id,
            "username": user.username,
            "view_count": 0,  # Would need to implement view tracking
            "answer_count": answer_count,
            "vote_score": vote_score,
            "comment_count": comment_count,
            "has_accepted_answer": has_accepted_answer,
            "created_at": question.created_at,
            "last_activity": last_activity,
            "tags": question.tags
        }
    
    @staticmethod
    async def get_popular_questions(limit: int = 20, time_period: str = "all") -> List[Dict]:
        """Get most popular questions by engagement score"""
        # Define time filter
        time_filter = {}
        if time_period == "week":
            week_ago = datetime.utcnow() - timedelta(days=7)
            time_filter = {"created_at": {"$gte": week_ago}}
        elif time_period == "month":
            month_ago = datetime.utcnow() - timedelta(days=30)
            time_filter = {"created_at": {"$gte": month_ago}}
        
        questions = await Question.find(time_filter).to_list()
        question_metrics = []
        
        for question in questions:
            metrics = await MetricsService.get_question_metrics(question.id)
            if metrics:
                # Calculate engagement score
                engagement_score = (
                    metrics["answer_count"] * 10 +
                    metrics["vote_score"] * 5 +
                    metrics["comment_count"] * 2 +
                    (50 if metrics["has_accepted_answer"] else 0)
                )
                
                question_metrics.append({
                    "question_id": question.id,
                    "title": question.title,
                    "username": metrics["username"],
                    "view_count": metrics["view_count"],
                    "answer_count": metrics["answer_count"],
                    "vote_score": metrics["vote_score"],
                    "engagement_score": engagement_score,
                    "created_at": question.created_at,
                    "tags": question.tags
                })
        
        # Sort by engagement score
        question_metrics.sort(key=lambda x: x["engagement_score"], reverse=True)
        return question_metrics[:limit]
    
    @staticmethod
    async def get_top_questions(limit: int = 20) -> List[Dict]:
        """Get top questions by vote score"""
        return await MetricsService.get_popular_questions(limit, "all")
    
    @staticmethod
    async def get_trending_questions(limit: int = 20) -> List[Dict]:
        """Get trending questions from the last week"""
        return await MetricsService.get_popular_questions(limit, "week")
    
    @staticmethod
    async def get_engagement_stats() -> Dict:
        """Get overall platform engagement statistics"""
        total_users = await User.find_all().count()
        total_questions = await Question.find_all().count()
        total_answers = await Answer.find_all().count()
        total_votes = await Vote.find_all().count()
        total_comments = await Comment.find_all().count()
        
        # Activity today
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        questions_today = await Question.find({
            "created_at": {"$gte": today}
        }).count()
        
        answers_today = await Answer.find({
            "created_at": {"$gte": today}
        }).count()
        
        # Active users today (users who posted questions, answers, or comments)
        active_user_ids = set()
        
        today_questions = await Question.find({"created_at": {"$gte": today}}).to_list()
        for q in today_questions:
            active_user_ids.add(q.user_id)
        
        today_answers = await Answer.find({"created_at": {"$gte": today}}).to_list()
        for a in today_answers:
            active_user_ids.add(a.user_id)
        
        today_comments = await Comment.find({"created_at": {"$gte": today}}).to_list()
        for c in today_comments:
            active_user_ids.add(c.user_id)
        
        active_users_today = len(active_user_ids)
        
        return {
            "total_users": total_users,
            "total_questions": total_questions,
            "total_answers": total_answers,
            "total_votes": total_votes,
            "total_comments": total_comments,
            "active_users_today": active_users_today,
            "questions_today": questions_today,
            "answers_today": answers_today
        }
    
    @staticmethod
    async def get_user_activity(user_id: str) -> Dict:
        """Get user activity for the current week"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        user = await User.get(user_id)
        if not user:
            return None
        
        questions_this_week = await Question.find({
            "user_id": user_id,
            "created_at": {"$gte": week_ago}
        }).count()
        
        answers_this_week = await Answer.find({
            "user_id": user_id,
            "created_at": {"$gte": week_ago}
        }).count()
        
        comments_this_week = await Comment.find({
            "user_id": user_id,
            "created_at": {"$gte": week_ago}
        }).count()
        
        # Count votes given this week
        votes_this_week = await Vote.find({
            "user_id": user_id,
            "created_at": {"$gte": week_ago}
        }).count()
        
        # Calculate activity score
        activity_score = (
            questions_this_week * 5 +
            answers_this_week * 3 +
            comments_this_week * 1 +
            votes_this_week * 0.5
        )
        
        return {
            "user_id": user_id,
            "username": user.username,
            "questions_this_week": questions_this_week,
            "answers_this_week": answers_this_week,
            "votes_this_week": votes_this_week,
            "comments_this_week": comments_this_week,
            "activity_score": activity_score
        }
    
    @staticmethod
    async def get_most_active_users(limit: int = 20) -> List[Dict]:
        """Get most active users this week"""
        users = await User.find_all().to_list()
        user_activities = []
        
        for user in users:
            activity = await MetricsService.get_user_activity(user.id)
            if activity and activity["activity_score"] > 0:
                user_activities.append(activity)
        
        # Sort by activity score
        user_activities.sort(key=lambda x: x["activity_score"], reverse=True)
        return user_activities[:limit]

