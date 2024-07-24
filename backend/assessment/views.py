# backend/assessment/views.py
import logging
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


logger = logging.getLogger(__name__)
class ScoreShortAnswersView(APIView):
    def post(self, request):
        answers = request.data.get('answers')
        topic = request.data.get('topic')
        
        logger.debug(f"Received answers: {answers}")
        logger.debug(f"Received topic: {topic}")

        if not answers or not topic:
            logger.error("Missing required fields in the request data")
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        scores = []
        
        for answer in answers:
            question_type = answer.get('type')
            question_text = answer.get('text')
            user_answer = answer.get('user_answer')

            logger.debug(f"Processing answer: {answer}")

            if not all([question_type, question_text, user_answer]):
                logger.error("Missing required fields in the answer data")
                scores.append(0)
                continue

            prompt = f"Evaluate the following {question_type} question about {topic}.\n\nQuestion: {question_text}\nStudent's Answer: {user_answer}\nProvide a score out of 1 based on the relevance and correctness."

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
                    score = int(result['candidates'][0]['content']['parts'][0]['text'].strip())
                    scores.append(score)
                else:
                    logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                    scores.append(0)

            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                scores.append(0)

        total_score = sum(scores)
        return Response({"total_score": total_score}, status=status.HTTP_200_OK)
