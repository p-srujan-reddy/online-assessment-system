# backend/assessment/views.py
import logging
import re
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

logger = logging.getLogger(__name__)

class GenerateAssessmentView(APIView):
    def post(self, request):
        topic = request.data.get('topic')
        assessment_type = request.data.get('assessmentType')
        question_count = request.data.get('questionCount')

        if not all([topic, assessment_type, question_count]):
            logger.error("Missing required fields in the request data")
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the prompt template
        if assessment_type == 'mcq':
            prompt = (
                f"Generate {question_count} {assessment_type} questions about {topic} in JSON format. "
                f"Each question should have a 'text' field for the question, an 'options' field for the answer options, "
                f"and a 'correct_answer' field for the correct answer. If it's a multiple-choice question, 'options' should include the correct answer and 3 incorrect options."
            )
        else:
            prompt = (
                f"Generate {question_count} short answer questions about {topic} in JSON format. "
                f"Each question should have a 'text' field for the question and a 'correct_answer' field for the correct answer."
            )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        try:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GOOGLE_GENERATIVE_AI_MODEL}:generateContent"
            headers = {"Content-Type": "application/json"}
            response = requests.post(api_url, json=payload, headers=headers, params={"key": settings.GOOGLE_GENERATIVE_AI_API_KEY})

            if response.status_code == 200:
                result = response.json()
                generated_text = result['candidates'][0]['content']['parts'][0]['text']
                questions = parse_generated_text(generated_text, assessment_type)
                return Response({"questions": questions, "assessmentType": assessment_type}, status=status.HTTP_200_OK)
            else:
                logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                return Response({"error": f"API request failed: {response.text}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def parse_generated_text(generated_text, assessment_type):
    import json
    try:
        if generated_text.startswith("```") and generated_text.endswith("```"):
            generated_text = generated_text.strip("```json").strip()
        
        questions = json.loads(generated_text)
        for question in questions:
            question['type'] = assessment_type  # Add the type to each question
        return questions
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return []
 
class ScoreShortAnswersView(APIView):
    def post(self, request):
        answers = request.data.get('answers')
        topic = request.data.get('topic')
        
        logger.debug(f"Received answers: {answers}")
        logger.debug(f"Received topic: {topic}")

        if not answers or not topic:
            logger.error("Missing required fields in the request data")
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        
        for answer in answers:
            question_type = answer.get('type')
            question_text = answer.get('text')
            user_answer = answer.get('user_answer')
            correct_answer = answer.get('correct_answer')

            logger.debug(f"Processing answer: {answer}")

            if not all([question_type, question_text, user_answer, correct_answer]):
                logger.error("Missing required fields in the answer data")
                results.append({"score": 0, "is_correct": False, "verified_by_llm": False})
                continue

            # Update prompt to evaluate relevance based on the correct answer
            prompt = (
                f"Evaluate the relevance of the following user answer to the correct answer for a given question. "
                f"Topic: {topic}\n"
                f"Question Type: {question_type}\n"
                f"Question: {question_text}\n"
                f"Correct Answer: {correct_answer}\n"
                f"User's Answer: {user_answer}\n"
                f"Provide a probability score between 0 and 1 representing how relevant the user's answer is to the correct answer. Give only probability score number"
            )

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }

            try:
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GOOGLE_GENERATIVE_AI_MODEL}:generateContent"
                headers = {"Content-Type": "application/json"}
                response = requests.post(api_url, json=payload, headers=headers, params={"key": settings.GOOGLE_GENERATIVE_AI_API_KEY})

                if response.status_code == 200:
                    result = response.json()
                    score_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    
                    logger.debug(f"score_text {score_text}")
                    
                    try:
                        # Directly convert score_text to float
                        score = float(score_text)
                        
                        # Round score to 0 or 1
                        is_correct = score >= 0.5
                        rounded_score = 1 if is_correct else 0
                        logger.debug(f"Rounded score {rounded_score}, is_correct {is_correct}")
                        
                    except ValueError:
                        logger.error(f"Failed to convert score from response: {score_text}")
                        rounded_score = 0
                        is_correct = False
                    
                    results.append({"score": rounded_score, "is_correct": is_correct, "verified_by_llm": True})
                else:
                    logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                    results.append({"score": 0, "is_correct": False, "verified_by_llm": False})

            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                results.append({"score": 0, "is_correct": False, "verified_by_llm": False})

        total_score = sum(result['score'] for result in results)
        return Response({"total_score": total_score, "results": results}, status=status.HTTP_200_OK)