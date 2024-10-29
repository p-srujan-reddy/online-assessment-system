# backend/assessment/views.py
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UploadedFile
import os
from django.conf import settings

logger = logging.getLogger(__name__)

# Utility function to make API requests
def make_api_request(prompt):
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
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return None

# Utility function to parse generated text
def parse_generated_text(generated_text, assessment_type):
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

# Utility function to process individual answers
def process_answer(answer, topic):
    question_type = answer.get('type')
    question_text = answer.get('text')
    user_answer = answer.get('user_answer')
    correct_answer = answer.get('correct_answer')

    if not all([question_type, question_text, user_answer, correct_answer]):
        return {"score": 0, "is_correct": False, "verified_by_llm": False}

    prompt = (
        f"Evaluate the relevance of the following user answer to the correct answer for a given question. "
        f"Topic: {topic}\n"
        f"Question Type: {question_type}\n"
        f"Question: {question_text}\n"
        f"Correct Answer: {correct_answer}\n"
        f"User's Answer: {user_answer}\n"
        f"Provide a probability score between 0 and 1 representing how relevant the user's answer is to the correct answer. Give only probability score number"
    )

    score_text = make_api_request(prompt)
    if score_text is not None:
        try:
            score = float(score_text)
            is_correct = score >= 0.5
            rounded_score = 1 if is_correct else 0
            return {"score": rounded_score, "is_correct": is_correct, "verified_by_llm": True}
        except ValueError:
            logger.error(f"Failed to convert score from response: {score_text}")
    return {"score": 0, "is_correct": False, "verified_by_llm": False}

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
        elif assessment_type == 'true_false':
            prompt = (
                f"Generate {question_count} {assessment_type} questions about {topic} in JSON format. "
                f"Each question should have a 'text' field for the question and a 'correct_answer' field which should be 'True' or 'False'."
            )
        elif assessment_type == 'fill_in_blank':
            prompt = (
                f"Generate {question_count} {assessment_type} questions about {topic} in JSON format. "
                f"Each question should have a 'text' field for the question with blanks represented by underscores and a 'correct_answer' field with the correct answer to fill in the blanks."
            )
        elif assessment_type == 'short_answer':
            prompt = (
                f"Generate {question_count} short answer questions about {topic} in JSON format. "
                f"Each question should have a 'text' field for the question and a 'correct_answer' field for the correct answer."
            )
        elif assessment_type == 'long_answer':
            prompt = (
                f"Generate {question_count} long answer questions about {topic} in JSON format. "
                f"Each question should have a 'text' field for the question and a 'correct_answer' field for the correct answer."
            )
        else:
            logger.error(f"Unsupported assessment type: {assessment_type}")
            return Response({"error": "Unsupported assessment type"}, status=status.HTTP_400_BAD_REQUEST)

        generated_text = make_api_request(prompt)
        print(f"generated_text {generated_text}")
        if generated_text is not None:
            questions = parse_generated_text(generated_text, assessment_type)
            print(f"questions {questions}")
            return Response({"questions": questions, "assessmentType": assessment_type}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "API request failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_answer = {executor.submit(process_answer, answer, topic): answer for answer in answers}
            for future in as_completed(future_to_answer):
                results.append(future.result())

        total_score = sum(result['score'] for result in results)
        return Response({"total_score": total_score, "results": results}, status=status.HTTP_200_OK)

class ScoreLongAnswersView(APIView):
    def post(self, request):
        answers = request.data.get('answers')
        topic = request.data.get('topic')
        
        logger.debug(f"Received answers: {answers}")
        logger.debug(f"Received topic: {topic}")

        if not answers or not topic:
            logger.error("Missing required fields in the request data")
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        results = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_answer = {executor.submit(process_answer, answer, topic): answer for answer in answers}
            for future in as_completed(future_to_answer):
                results.append(future.result())

        total_score = sum(result['score'] for result in results)
        return Response({"total_score": total_score, "results": results}, status=status.HTTP_200_OK)
    
class ScoreFillInTheBlanksView(APIView):
    def post(self, request):
        answers = request.data.get('answers')
        topic = request.data.get('topic')
        
        logger.debug(f"Received answers: {answers}")
        logger.debug(f"Received topic: {topic}")

        if not answers or not topic:
            logger.error("Missing required fields in the request data")
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        results = []

        def process_fill_in_the_blank_answer(answer, topic):
            question_text = answer.get('text')
            user_answers = answer.get('user_answer', [])
            correct_answers = answer.get('correct_answer', '').split(', ')
            
            if len(user_answers) != len(correct_answers):
                return {"score": 0, "is_correct": [False] * len(correct_answers), "verified_by_llm": False}

            is_correct_list = []
            total_score = 0

            for user_answer, correct_answer in zip(user_answers, correct_answers):
                prompt = (
                            f"Evaluate the relevance of the following user's answer to the correct answer for a given fill-in-the-blanks question. "
                            f"Analyze the question context to ensure the user's answer fits appropriately.\n"
                            f"Topic: {topic}\n"
                            f"Question Type: fill_in_the_blanks\n"
                            f"Question: {question_text}\n"
                            f"Correct Answer: {correct_answer}\n"
                            f"User's Answer: {user_answer}\n"
                            f"Provide a probability score between 0 and 1 representing how relevant the user's answer is to the correct answer. Give only the probability score number."
                        )

                score_text = make_api_request(prompt)
                print(f"score_text {score_text}")
                if score_text is not None:
                    try:
                        score = float(score_text)
                        is_correct = score >= 0.5
                        rounded_score = 1 if is_correct else 0
                        total_score += rounded_score
                        is_correct_list.append(is_correct)
                    except ValueError:
                        logger.error(f"Failed to convert score from response: {score_text}")
                        is_correct_list.append(False)
                else:
                    is_correct_list.append(False)

            return {
                "score": total_score,
                "is_correct": is_correct_list,
                "verified_by_llm": all(is_correct_list)
            }

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_answer = {executor.submit(process_fill_in_the_blank_answer, answer, topic): answer for answer in answers}
            for future in as_completed(future_to_answer):
                results.append(future.result())

        total_score = sum(result['score'] for result in results)
        print(f"total_score {total_score}")
        return Response({"total_score": total_score, "results": results}, status=status.HTTP_200_OK)



class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('documents')
        topic = request.data.get('topic')
        uploaded_files = []
        
        for file in files:
            uploaded_file = UploadedFile.objects.create(file=file)
            uploaded_files.append(uploaded_file)
            file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
            logger.info(f"File saved to: {file_path}")
            print(f"File saved to: {file_path}")  # Optional: Print to console

        return Response({'message': 'Files uploaded successfully'}, status=status.HTTP_201_CREATED)