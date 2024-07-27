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
import os
import tempfile
from rest_framework.parsers import MultiPartParser
from django.shortcuts import render

from django.views import View

from django.core.files.storage import default_storage
from .utils import process_document, generate_questions
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


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
        use_document = request.data.get('useDocument', False)

        if not all([topic, assessment_type, question_count]):
            logger.error("Missing required fields in the request data")
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if use_document:
                # Retrieve the most recent document for this topic
                collection = process_document(f"{topic}_collection")
                questions = generate_questions(topic, assessment_type, collection, question_count)
            else:
                questions = generate_questions(topic, assessment_type, question_count=question_count)

            return Response({"questions": questions, "assessmentType": assessment_type}, status=status.HTTP_200_OK)
        except ValueError as e:
            logger.error(f"Invalid assessment type: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error generating assessment: {str(e)}")
            return Response({"error": "Failed to generate assessment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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


class UploadDocumentView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('document')
        topic = request.POST.get('topic')

        if not file:
            return JsonResponse({'error': 'No document uploaded'}, status=400)
        if not topic:
            return JsonResponse({'error': 'Topic is required'}, status=400)

        try:
            # Save the file
            file_path = default_storage.save(file.name, file)
            file_url = default_storage.url(file_path)
            
            # Process the document
            collection = process_document(file_url, topic)
            
            return JsonResponse({'message': 'Document uploaded and processed successfully'})
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return JsonResponse({'error': 'Failed to process document'}, status=500)

