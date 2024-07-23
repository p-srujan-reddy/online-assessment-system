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
        prompt = (
            f"Generate {question_count} {assessment_type} questions about {topic} in JSON format. "
            f"Each question should have a 'text' field for the question, an 'options' field for the answer options, "
            f"and a 'correct_answer' field for the correct answer. If it's a multiple-choice question, 'options' should include the correct answer and 3 incorrect options."
        )

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
                print(f"API response result: {result}")  # Add this line to inspect the structure
                
                generated_text = result['candidates'][0]['content']['parts'][0]['text']
                
                # Parse the result
                questions = parse_generated_text(generated_text)
                
                print(f"generated_text: {generated_text}")
                print(f"questions: {questions}")

                return Response({"questions": questions}, status=status.HTTP_200_OK)
            else:
                logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                return Response({"error": f"API request failed: {response.text}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def parse_generated_text(generated_text):
    import json
    try:
        # Remove code block markers if present
        if generated_text.startswith("```") and generated_text.endswith("```"):
            generated_text = generated_text.strip("```json").strip()
        
        questions = json.loads(generated_text)
        return questions
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return []

# Dummy response of the backend (for testing purposes)
API_response_result = {
    'candidates': [{
        'content': {
            'parts': [{
                'text': '```json\n[\n  {\n    "text": "What is the name of Amazon\'s cloud computing platform?",\n    "options": [\n      "AWS",\n      "Azure",\n      "Google Cloud Platform",\n      "IBM Cloud"\n    ],\n    "correct_answer": "AWS"\n  },\n  {\n    "text": "When was Amazon founded?",\n    "options": [\n      "1994",\n      "1995",\n      "1996",\n      "1997"\n    ],\n    "correct_answer": "1994"\n  },\n  {\n    "text": "Which of these is NOT an Amazon subsidiary?",\n    "options": [\n      "Whole Foods Market",\n      "IMDb",\n      "Netflix",\n      "Zappos"\n    ],\n    "correct_answer": "Netflix"\n  },\n  {\n    "text": "What is the name of Amazon\'s digital assistant?",\n    "options": [\n      "Alexa",\n      "Siri",\n      "Cortana",\n      "Google Assistant"\n    ],\n    "correct_answer": "Alexa"\n  },\n  {\n    "text": "Which of these is NOT a product category offered by Amazon?",\n    "options": [\n      "Electronics",\n      "Books",\n      "Clothing",\n      "Cars"\n    ],\n    "correct_answer": "Cars"\n  }\n]\n```'
            }]
        },
        'role': 'model'
    }],
    'usageMetadata': {'promptTokenCount': 72, 'candidatesTokenCount': 335, 'totalTokenCount': 407}
}

generated_text = API_response_result['candidates'][0]['content']['parts'][0]['text']
questions = parse_generated_text(generated_text)
print(f"generated_text: {generated_text}")
print(f"questions: {questions}")

