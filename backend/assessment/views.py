# backend/assessment/views.py
import logging
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

# Configure logging
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
        prompt = f"Generate {question_count} {assessment_type} questions about {topic}. For each question, provide the correct answer and, if it's a multiple-choice question, provide 3 incorrect options."

        # Prepare the payload for the API request
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
            # Call the Google Generative Language API
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GOOGLE_GENERATIVE_AI_MODEL}:generateContent"
            headers = {"Content-Type": "application/json"}
            response = requests.post(api_url, json=payload, headers=headers, params={"key": settings.GOOGLE_GENERATIVE_AI_API_KEY})

            if response.status_code == 200:
                result = response.json()
                generated_text = result['candidates'][0]['content']['parts'][0]['text']
                

                # TODO: Parse the result and create Assessment, Question, and Answer objects

                return Response({"result": generated_text}, status=status.HTTP_200_OK)
            else:
                logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                return Response({"error": f"API request failed: {response.text}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
