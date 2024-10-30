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
from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
    CSVLoader,
)
from google import generativeai as genai  # Import the genai library
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from asgiref.sync import sync_to_async
import asyncio

logger = logging.getLogger(__name__)
os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])


async def generate_gemini_embeddings(
    content, title, model="models/text-embedding-004", task_type="retrieval_document"
):
    try:
        model_instance = genai.GenerativeModel(model_name=model)
        payload = {"content": content, "title": title, "task_type": task_type}

        # Check if embed_content is asynchronous
        if asyncio.iscoroutinefunction(model_instance.embed_content):
            response = await model_instance.embed_content(payload)
        else:
            response = await sync_to_async(model_instance.embed_content)(payload)

        return response.embedding
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


# Utility function to make API requests using genai
async def make_api_request(prompt):
    try:
        model_instance = genai.GenerativeModel(
            model_name=settings.GOOGLE_GENERATIVE_AI_MODEL
        )

        # Check if generate_content is asynchronous
        if asyncio.iscoroutinefunction(model_instance.generate_content):
            response = await model_instance.generate_content(prompt)
        else:
            response = await sync_to_async(model_instance.generate_content)(prompt)

        return response.text.strip()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


# Utility function to parse generated text
def parse_generated_text(generated_text, assessment_type):
    try:
        if generated_text.startswith("```") and generated_text.endswith("```"):
            generated_text = generated_text.strip("```json").strip()

        questions = json.loads(generated_text)
        for question in questions:
            question["type"] = assessment_type  # Add the type to each question
        return questions
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return []


# Utility function to process individual answers
# online-assessment-system/backend/assessment/views.py


async def process_answer(answer, topic):
    question_type = answer.get("type")
    question_text = answer.get("text")
    user_answer = answer.get("user_answer")
    correct_answer = answer.get("correct_answer")

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

    score_text = await make_api_request(prompt)
    if score_text is not None:
        try:
            score = float(score_text)
            is_correct = score >= 0.5
            rounded_score = 1 if is_correct else 0
            return {
                "score": rounded_score,
                "is_correct": is_correct,
                "verified_by_llm": True,
            }
        except ValueError:
            logger.error(f"Failed to convert score from response: {score_text}")
    return {"score": 0, "is_correct": False, "verified_by_llm": False}


def upload_document(request):
    if request.method == "POST":
        documents = []
        for file in request.FILES.getlist("documents"):
            file_name = file.name
            file_type = file.content_type

            if file_type == "application/pdf":
                loader = UnstructuredPDFLoader(file)
            elif file_type in [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/msword",
            ]:
                loader = UnstructuredWordDocumentLoader(file)
            elif (
                file_type
                == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ):
                loader = UnstructuredExcelLoader(file)
            elif (
                file_type
                == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            ):
                loader = UnstructuredPowerPointLoader(file)
            elif file_type == "text/csv":
                loader = CSVLoader(file)
            else:
                continue  # Unsupported file type

            documents.extend(loader.load())
        # Proceed to process the documents


async def process_documents(documents):
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    # Prepare texts for embedding
    texts = [chunk.page_content for chunk in chunks]

    # Initialize embeddings and ChromaDB
    embeddings = await generate_gemini_embeddings(texts, "Retrieval")
    if not embeddings:
        logger.error("Failed to generate embeddings for documents")
        return

    client = chromadb.Client(
        settings=chromadb.config.Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="online-assessment-system/backend/chroma_db",
            anonymized_telemetry=False,
        )
    )
    collection = await sync_to_async(client.get_or_create_collection)(name="documents")

    # Embed texts in batches
    if asyncio.iscoroutinefunction(embeddings.embed_documents):
        embeddings_list = await embeddings.embed_documents(texts)
    else:
        embeddings_list = await sync_to_async(embeddings.embed_documents)(texts)

    # Add embeddings to ChromaDB
    await sync_to_async(collection.add)(documents=texts, embeddings=embeddings_list)


class GenerateAssessmentView(APIView):
    async def post(self, request):
        topic = request.data.get("topic")
        assessment_type = request.data.get("assessmentType")
        question_count = request.data.get("questionCount")
        if not all([topic, assessment_type, question_count]):
            logger.error("Missing required fields in the request data")
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Retrieve relevant documents from ChromaDB
        embeddings = await generate_gemini_embeddings(topic, "Retrieval")
        if not embeddings:
            return Response(
                {"error": "Failed to generate embeddings"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        client = chromadb.Client(
            settings=chromadb.config.Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="online-assessment-system/backend/chroma_db",
                anonymized_telemetry=False,
            )
        )
        collection = await sync_to_async(client.get_collection)(name="documents")

        # Check if collection.query is asynchronous
        if asyncio.iscoroutinefunction(collection.query):
            results = await collection.query(
                query_embeddings=[embeddings], n_results=3, include=["documents"]
            )
        else:
            results = await sync_to_async(collection.query)(
                query_embeddings=[embeddings], n_results=3, include=["documents"]
            )

        context = " ".join(results["documents"])

        # Create the prompt template
        if assessment_type == "mcq":
            prompt = (
                f"Generate {question_count} {assessment_type} questions about {topic} in JSON format. "
                f"Consider and use the following context to generate the questions and answers required on the {topic}: \n {context}"
                f"Each question should have a 'text' field for the question, an 'options' field for the answer options, "
                f"and a 'correct_answer' field for the correct answer. If it's a multiple-choice question, 'options' should include the correct answer and 3 incorrect options."
            )
        elif assessment_type == "true_false":
            prompt = (
                f"Generate {question_count} {assessment_type} questions about {topic} in JSON format. "
                f"Consider and use the following context to generate the questions and answers required on the {topic}: \n {context}"
                f"Each question should have a 'text' field for the question and a 'correct_answer' field which should be 'True' or 'False'."
            )
        elif assessment_type == "fill_in_blank":
            prompt = (
                f"Generate {question_count} {assessment_type} questions about {topic} in JSON format. "
                f"Consider and use the following context to generate the questions and answers required on the {topic}: \n {context}"
                f"Each question should have a 'text' field for the question with blanks represented by underscores and a 'correct_answer' field with the correct answer to fill in the blanks."
            )
        elif assessment_type == "short_answer":
            prompt = (
                f"Generate {question_count} short answer questions about {topic} in JSON format. "
                f"Consider and use the following context to generate the questions and answers required on the {topic}: \n {context}"
                f"Each question should have a 'text' field for the question and a 'correct_answer' field for the correct answer."
            )
        elif assessment_type == "long_answer":
            prompt = (
                f"Generate {question_count} long answer questions about {topic} in JSON format. "
                f"Consider and use the following context to generate the questions and answers required on the {topic}: \n {context}"
                f"Each question should have a 'text' field for the question and a 'correct_answer' field for the correct answer."
            )
        else:
            logger.error(f"Unsupported assessment type: {assessment_type}")
            return Response(
                {"error": "Unsupported assessment type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        generated_text = await make_api_request(prompt)
        print(f"generated_text {generated_text}")
        if generated_text is not None:
            questions = parse_generated_text(generated_text, assessment_type)
            print(f"questions {questions}")
            return Response(
                {"questions": questions, "assessmentType": assessment_type},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "API request failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ScoreShortAnswersView(APIView):
    async def post(self, request):
        answers = request.data.get("answers")
        topic = request.data.get("topic")

        logger.debug(f"Received answers: {answers}")
        logger.debug(f"Received topic: {topic}")

        if not answers or not topic:
            logger.error("Missing required fields in the request data")
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        tasks = [process_answer(answer, topic) for answer in answers]
        results = await asyncio.gather(*tasks)

        total_score = sum(result["score"] for result in results)
        return Response(
            {"total_score": total_score, "results": results}, status=status.HTTP_200_OK
        )


class ScoreLongAnswersView(APIView):
    async def post(self, request):
        answers = request.data.get("answers")
        topic = request.data.get("topic")

        logger.debug(f"Received answers: {answers}")
        logger.debug(f"Received topic: {topic}")

        if not answers or not topic:
            logger.error("Missing required fields in the request data")
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        tasks = [process_answer(answer, topic) for answer in answers]
        results = await asyncio.gather(*tasks)

        total_score = sum(result["score"] for result in results)
        return Response(
            {"total_score": total_score, "results": results}, status=status.HTTP_200_OK
        )


class ScoreFillInTheBlanksView(APIView):
    async def post(self, request):
        answers = request.data.get("answers")
        topic = request.data.get("topic")

        logger.debug(f"Received answers: {answers}")
        logger.debug(f"Received topic: {topic}")

        if not answers or not topic:
            logger.error("Missing required fields in the request data")
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        results = []

        async def process_fill_in_the_blank_answer(answer, topic):
            question_text = answer.get("text")
            user_answers = answer.get("user_answer", [])
            correct_answers = answer.get("correct_answer", "").split(", ")

            # Retrieve relevant documents
            embeddings = await generate_gemini_embeddings(topic, "Retrieval")
            if not embeddings:
                return {
                    "score": 0,
                    "is_correct": [False] * len(correct_answers),
                    "verified_by_llm": False,
                }
            client = chromadb.Client(
                settings=chromadb.config.Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory="online-assessment-system/backend/chroma_db",
                    anonymized_telemetry=False,
                )
            )
            collection = await sync_to_async(client.get_collection)(name="documents")
            
            # Check if collection.query is asynchronous
            if asyncio.iscoroutinefunction(collection.query):
                results = await collection.query(
                    query_embeddings=[embeddings], n_results=5, include=["documents"]
                )
            else:
                results = await sync_to_async(collection.query)(
                    query_embeddings=[embeddings], n_results=5, include=["documents"]
                )

            context = " ".join(results["documents"])

            if len(user_answers) != len(correct_answers):
                return {
                    "score": 0,
                    "is_correct": [False] * len(correct_answers),
                    "verified_by_llm": False,
                }

            is_correct_list = []
            total_score = 0

            for user_answer, correct_answer in zip(user_answers, correct_answers):
                prompt = (
                    f"Evaluate the relevance of the following user's answer to the correct answer for a given fill-in-the-blanks question. "
                    f"Also Consider the following context of the question to ensure the user's answer fits appropriately: \n{context}"
                    f"Analyze the question context to ensure the user's answer fits appropriately.\n"
                    f"Topic: {topic}\n"
                    f"Question Type: fill_in_the_blanks\n"
                    f"Question: {question_text}\n"
                    f"Correct Answer: {correct_answer}\n"
                    f"User's Answer: {user_answer}\n"
                    f"Provide a probability score between 0 and 1 representing how relevant the user's answer is to the correct answer. Give only the probability score number."
                )

                score_text = await make_api_request(prompt)
                print(f"score_text {score_text}")
                if score_text is not None:
                    try:
                        score = float(score_text)
                        is_correct = score >= 0.5
                        rounded_score = 1 if is_correct else 0
                        total_score += rounded_score
                        is_correct_list.append(is_correct)
                    except ValueError:
                        logger.error(
                            f"Failed to convert score from response: {score_text}"
                        )
                        is_correct_list.append(False)
                else:
                    is_correct_list.append(False)

            return {
                "score": total_score,
                "is_correct": is_correct_list,
                "verified_by_llm": all(is_correct_list),
            }

        tasks = [process_fill_in_the_blank_answer(answer, topic) for answer in answers]
        results = await asyncio.gather(*tasks)

        total_score = sum(result["score"] for result in results)
        print(f"total_score {total_score}")
        return Response(
            {"total_score": total_score, "results": results}, status=status.HTTP_200_OK
        )


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("documents")
        topic = request.data.get("topic")
        uploaded_files = []

        for file in files:
            uploaded_file = UploadedFile.objects.create(file=file)
            uploaded_files.append(uploaded_file)
            file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
            logger.info(f"File saved to: {file_path}")
            print(f"File saved to: {file_path}")  # Optional: Print to console

        return Response(
            {"message": "Files uploaded successfully"}, status=status.HTTP_201_CREATED
        )