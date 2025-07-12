from typing import List, Optional, Dict
from fastapi import HTTPException, status
import random
from app.models.mcq import MCQQuiz, MCQQuestion
from app.schemas.mcq import MCQQuizCreate, QuizSubmission, QuizAnswer
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MCQService:
    
    # Sample questions for different topics
    SAMPLE_QUESTIONS = {
        "python": [
            {
                "question_text": "What is the output of print(type([]))?",
                "option_a": "<class 'list'>",
                "option_b": "<class 'array'>",
                "option_c": "list",
                "option_d": "array",
                "correct_option": "A"
            },
            {
                "question_text": "Which of the following is used to define a function in Python?",
                "option_a": "function",
                "option_b": "def",
                "option_c": "define",
                "option_d": "func",
                "correct_option": "B"
            },
            {
                "question_text": "What does the len() function return?",
                "option_a": "Length of an object",
                "option_b": "Type of an object",
                "option_c": "Value of an object",
                "option_d": "Memory address",
                "correct_option": "A"
            },
            {
                "question_text": "Which operator is used for exponentiation in Python?",
                "option_a": "^",
                "option_b": "**",
                "option_c": "exp",
                "option_d": "pow",
                "correct_option": "B"
            },
            {
                "question_text": "What is the correct way to create a dictionary in Python?",
                "option_a": "dict = []",
                "option_b": "dict = ()",
                "option_c": "dict = {}",
                "option_d": "dict = <>",
                "correct_option": "C"
            }
        ],
        "javascript": [
            {
                "question_text": "Which method is used to add an element to the end of an array?",
                "option_a": "push()",
                "option_b": "add()",
                "option_c": "append()",
                "option_d": "insert()",
                "correct_option": "A"
            },
            {
                "question_text": "What does 'typeof null' return in JavaScript?",
                "option_a": "null",
                "option_b": "undefined",
                "option_c": "object",
                "option_d": "string",
                "correct_option": "C"
            },
            {
                "question_text": "Which keyword is used to declare a constant in JavaScript?",
                "option_a": "var",
                "option_b": "let",
                "option_c": "const",
                "option_d": "final",
                "correct_option": "C"
            },
            {
                "question_text": "What is the correct way to write a JavaScript array?",
                "option_a": "var colors = 'red', 'green', 'blue'",
                "option_b": "var colors = ['red', 'green', 'blue']",
                "option_c": "var colors = (1:'red', 2:'green', 3:'blue')",
                "option_d": "var colors = 1 = ('red'), 2 = ('green'), 3 = ('blue')",
                "correct_option": "B"
            },
            {
                "question_text": "How do you write 'Hello World' in an alert box?",
                "option_a": "alertBox('Hello World');",
                "option_b": "msg('Hello World');",
                "option_c": "alert('Hello World');",
                "option_d": "msgBox('Hello World');",
                "correct_option": "C"
            }
        ],
        "react": [
            {
                "question_text": "What is JSX?",
                "option_a": "A JavaScript library",
                "option_b": "A syntax extension for JavaScript",
                "option_c": "A database",
                "option_d": "A CSS framework",
                "correct_option": "B"
            },
            {
                "question_text": "Which method is used to create components in React?",
                "option_a": "React.createComponent()",
                "option_b": "React.createElement()",
                "option_c": "createComponent()",
                "option_d": "Both A and B",
                "correct_option": "B"
            },
            {
                "question_text": "What is the purpose of useState hook?",
                "option_a": "To manage component state",
                "option_b": "To handle side effects",
                "option_c": "To optimize performance",
                "option_d": "To handle routing",
                "correct_option": "A"
            },
            {
                "question_text": "Which of the following is used to pass data to a component?",
                "option_a": "state",
                "option_b": "props",
                "option_c": "arguments",
                "option_d": "parameters",
                "correct_option": "B"
            },
            {
                "question_text": "What does the useEffect hook do?",
                "option_a": "Manages state",
                "option_b": "Handles side effects",
                "option_c": "Creates components",
                "option_d": "Handles events",
                "correct_option": "B"
            }
        ]
    }
    
    @staticmethod
    async def create_quiz(quiz_data: MCQQuizCreate, user_id: str) -> MCQQuiz:
        """Create a new quiz for a user"""
        quiz = MCQQuiz(
            user_id=user_id,
            topic=quiz_data.topic.lower()
        )
        
        await quiz.insert()
        
        # Generate questions for the quiz
        await MCQService.generate_questions_for_quiz(quiz.id, quiz.topic)
        
        # Update total questions count
        question_count = await MCQQuestion.find(MCQQuestion.quiz_id == quiz.id).count()
        quiz.total_questions = question_count
        await quiz.save()
        
        logger.info(f"Quiz created: {quiz.id} for user {user_id} on topic {quiz.topic}")
        return quiz
    
    @staticmethod
    async def generate_questions_for_quiz(quiz_id: str, topic: str, num_questions: int = 5):
        """Generate questions for a quiz based on topic"""
        topic_lower = topic.lower()
        
        if topic_lower not in MCQService.SAMPLE_QUESTIONS:
            # If topic not found, use a mix of all available questions
            all_questions = []
            for questions in MCQService.SAMPLE_QUESTIONS.values():
                all_questions.extend(questions)
            selected_questions = random.sample(all_questions, min(num_questions, len(all_questions)))
        else:
            available_questions = MCQService.SAMPLE_QUESTIONS[topic_lower]
            selected_questions = random.sample(available_questions, min(num_questions, len(available_questions)))
        
        for question_data in selected_questions:
            question = MCQQuestion(
                quiz_id=quiz_id,
                **question_data
            )
            await question.insert()
    
    @staticmethod
    async def get_quiz_by_id(quiz_id: str) -> Optional[MCQQuiz]:
        """Get quiz by ID"""
        return await MCQQuiz.get(quiz_id)
    
    @staticmethod
    async def get_quiz_questions(quiz_id: str) -> List[Dict]:
        """Get questions for a quiz (without correct answers)"""
        questions = await MCQQuestion.find(MCQQuestion.quiz_id == quiz_id).to_list()
        
        # Return questions without correct answers
        quiz_questions = []
        for question in questions:
            quiz_questions.append({
                "id": question.id,
                "question_text": question.question_text,
                "option_a": question.option_a,
                "option_b": question.option_b,
                "option_c": question.option_c,
                "option_d": question.option_d
            })
        
        return quiz_questions
    
    @staticmethod
    async def submit_quiz(submission: QuizSubmission, user_id: str) -> Dict:
        """Submit quiz answers and calculate score"""
        quiz = await MCQQuiz.get(submission.quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        if quiz.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to submit this quiz"
            )
        
        if quiz.completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quiz already completed"
            )
        
        # Get all questions for the quiz
        questions = await MCQQuestion.find(MCQQuestion.quiz_id == submission.quiz_id).to_list()
        question_dict = {q.id: q for q in questions}
        
        # Calculate score
        correct_count = 0
        correct_answers = []
        
        for answer in submission.answers:
            question = question_dict.get(answer.question_id)
            if question and question.correct_option == answer.selected_option:
                correct_count += 1
            if question:
                correct_answers.append(question.correct_option)
        
        # Update quiz
        quiz.score = correct_count
        quiz.completed = True
        await quiz.save()
        
        percentage = (correct_count / len(questions)) * 100 if questions else 0
        passed = percentage >= 70
        
        result = {
            "quiz_id": submission.quiz_id,
            "score": correct_count,
            "total_questions": len(questions),
            "percentage": round(percentage, 2),
            "correct_answers": correct_answers,
            "user_answers": submission.answers,
            "passed": passed
        }
        
        logger.info(f"Quiz submitted: {submission.quiz_id} by user {user_id}, score: {correct_count}/{len(questions)}")
        return result
    
    @staticmethod
    async def get_user_quizzes(user_id: str, skip: int = 0, limit: int = 20) -> List[MCQQuiz]:
        """Get quizzes for a user"""
        quizzes = await MCQQuiz.find(MCQQuiz.user_id == user_id)\
            .sort(-MCQQuiz.created_at)\
            .skip(skip)\
            .limit(limit)\
            .to_list()
        return quizzes
    
    @staticmethod
    async def get_available_topics() -> List[str]:
        """Get list of available quiz topics"""
        return list(MCQService.SAMPLE_QUESTIONS.keys())
    
    @staticmethod
    async def get_topic_stats(user_id: str, topic: str) -> Dict:
        """Get statistics for a topic for a user"""
        quizzes = await MCQQuiz.find({
            "user_id": user_id,
            "topic": topic.lower(),
            "completed": True
        }).to_list()
        
        if not quizzes:
            return {
                "topic": topic,
                "total_quizzes": 0,
                "average_score": 0,
                "best_score": 0,
                "completion_rate": 0
            }
        
        total_quizzes = len(quizzes)
        total_score = sum(quiz.score for quiz in quizzes)
        total_possible = sum(quiz.total_questions for quiz in quizzes)
        best_score = max(quiz.score for quiz in quizzes)
        
        average_score = (total_score / total_possible) * 100 if total_possible > 0 else 0
        completion_rate = 100  # All quizzes in this query are completed
        
        return {
            "topic": topic,
            "total_quizzes": total_quizzes,
            "average_score": round(average_score, 2),
            "best_score": best_score,
            "completion_rate": completion_rate
        }

