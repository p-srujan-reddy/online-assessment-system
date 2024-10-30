# backend/assessment/views.py

import json
import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional, Union
import pinecone
from pinecone import Pinecone, ServerlessSpec

import chromadb
from asgiref.sync import sync_to_async
import asyncio
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from functools import wraps
from google import generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
    CSVLoader,
)

from .models import UploadedFile

# Configure logging
logger = logging.getLogger(__name__)

# Configure Google Generative AI
os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
# os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
# pinecone.init(api_key=os.environ["PINECONE_API_KEY"], environment="us-east-1")
INDEX_NAME = "document-embeddings"
VECTOR_DIMENSION = 768
VECTOR_METRIC = "cosine"
NAMESPACE = "documents"  # Namespace for document embeddings

if INDEX_NAME in pc.list_indexes().names():
    pc.delete_index(INDEX_NAME)

def init_pinecone():
    try:
        existing_indexes = pc.list_indexes().names()
        if INDEX_NAME not in existing_indexes:
            pc.create_index(
                name=INDEX_NAME,
                dimension=VECTOR_DIMENSION,  # This will now create index with correct dimension
                metric=VECTOR_METRIC,
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            while not pc.describe_index(INDEX_NAME).status['ready']:
                time.sleep(1)
        else:
            # Check if existing index has correct dimension
            index_info = pc.describe_index(INDEX_NAME)
            if index_info.dimension != VECTOR_DIMENSION:
                logger.error(f"Existing index dimension ({index_info.dimension}) does not match required dimension ({VECTOR_DIMENSION})")
                # You may want to delete and recreate the index here, or handle this case differently
                raise ValueError("Index dimension mismatch")
    except Exception as e:
        logger.error(f"Error initializing Pinecone index: {e}")
        raise



init_pinecone()

# Type definitions
JsonDict = Dict[str, Any]
QuestionType = (
    str  # "mcq" | "true_false" | "fill_in_blank" | "short_answer" | "long_answer"
)


def async_view(view_func: Callable) -> Callable:
    """Decorator to handle async views in Django REST Framework"""

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return asyncio.run(view_func(request, *args, **kwargs))

    return wrapper


# Utility Functions
async def generate_gemini_embeddings(
    content: Union[str, List[str]],
    title: str = "",
    model: str = "models/embedding-001",  # Updated to the correct model name
    task_type: str = "retrieval_document",
) -> Optional[List[float]]:
    """Generate embeddings using Google's Gemini embedding model"""
    try:
        # Handle single string or list of strings
        if isinstance(content, list):
            # Process multiple texts
            embeddings = []
            for text in content:
                result = await sync_to_async(genai.embed_content)(
                    model=model, content=text, task_type=task_type, title=title
                )
                embedding = result["embedding"]
                # Verify embedding dimension
                if len(embedding) != VECTOR_DIMENSION:
                    raise ValueError(f"Generated embedding dimension {len(embedding)} does not match expected {VECTOR_DIMENSION}")
                embeddings.append(embedding)
            return embeddings
        else:
            # Process single text
            result = await sync_to_async(genai.embed_content)(
                model=model, content=content, task_type=task_type, title=title
            )
            embedding = result["embedding"]
            # Verify embedding dimension
            if len(embedding) != VECTOR_DIMENSION:
                raise ValueError(f"Generated embedding dimension {len(embedding)} does not match expected {VECTOR_DIMENSION}")
            return embedding
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return None


async def make_api_request(prompt: str) -> Optional[str]:
    """Make API request to Google's Generative AI"""
    try:
        model_instance = genai.GenerativeModel(
            model_name=settings.GOOGLE_GENERATIVE_AI_MODEL
        )

        if asyncio.iscoroutinefunction(model_instance.generate_content):
            response = await model_instance.generate_content(prompt)
        else:
            response = await sync_to_async(model_instance.generate_content)(prompt)

        return response.text.strip()
    except Exception as e:
        logger.error(f"API request error: {e}")
        return None


def parse_generated_text(
    generated_text: str, assessment_type: QuestionType
) -> List[JsonDict]:
    """Parse generated text into structured question format"""
    try:
        if generated_text.startswith("```") and generated_text.endswith("```"):
            generated_text = generated_text.strip("```json").strip()

        questions = json.loads(generated_text)
        for question in questions:
            question["type"] = assessment_type
        return questions
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return []


async def process_answer(answer: JsonDict, topic: str) -> JsonDict:
    """Process and score individual answers"""
    try:
        question_type = answer.get("type")
        question_text = answer.get("text")
        user_answer = answer.get("user_answer")
        correct_answer = answer.get("correct_answer")

        if not all([question_type, question_text, user_answer, correct_answer]):
            return {"score": 0, "is_correct": False, "verified_by_llm": False}

        prompt = (
            f"Evaluate the following answer's correctness:\n"
            f"Topic: {topic}\n"
            f"Question Type: {question_type}\n"
            f"Question: {question_text}\n"
            f"Correct Answer: {correct_answer}\n"
            f"User's Answer: {user_answer}\n"
            f"Provide a probability score between 0 and 1. Return only the number."
        )

        score_text = await make_api_request(prompt)
        if score_text is not None:
            try:
                score = float(score_text)
                is_correct = score >= 0.5
                return {
                    "score": 1 if is_correct else 0,
                    "is_correct": is_correct,
                    "verified_by_llm": True,
                }
            except ValueError:
                logger.error(f"Score conversion error: {score_text}")

        return {"score": 0, "is_correct": False, "verified_by_llm": False}
    except Exception as e:
        logger.error(f"Error processing answer: {e}")
        return {"score": 0, "is_correct": False, "verified_by_llm": False}


async def process_documents(documents: List[Any]) -> None:
    """Process and embed documents for storage"""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        texts = [chunk.page_content for chunk in chunks]

        # Generate embeddings for all texts
        embeddings = await generate_gemini_embeddings(texts)
        if not embeddings:
            raise ValueError("Failed to generate embeddings")

        # Verify all embeddings have correct dimension
        for i, embedding in enumerate(embeddings):
            if len(embedding) != VECTOR_DIMENSION:
                raise ValueError(f"Embedding {i} has incorrect dimension: {len(embedding)}")

        while not pc.describe_index(INDEX_NAME).status["ready"]:
            time.sleep(1)
        
        # Get Pinecone index
        index = pc.Index(INDEX_NAME)

        # Prepare vectors for upsert
        vectors = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            vectors.append({
                "id": f"doc_{i}",
                "values": embedding,
                "metadata": {"text": text}
            })

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            try:
                await sync_to_async(index.upsert)(
                    vectors=batch,
                    namespace=NAMESPACE
                )
            except Exception as e:
                logger.error(f"Error upserting batch {i//batch_size}: {e}")
                raise

    except Exception as e:
        logger.error(f"Error processing documents: {e}")
        raise


async def generate_prompt(
    assessment_type: QuestionType, question_count: int, topic: str, context: str
) -> str:
    """Generate appropriate prompt based on assessment type"""
    prompt_templates = {
        "mcq": (
            f"Generate {question_count} multiple choice questions about {topic} in JSON format. "
            f"Context: {context}\n"
            f"Include 'text' field for questions, 'options' array with 4 choices, "
            f"and 'correct_answer' matching one option."
        ),
        "true_false": (
            f"Generate {question_count} true/false questions about {topic} in JSON format. "
            f"Context: {context}\n"
            f"Include 'text' field and 'correct_answer' field with 'True' or 'False'."
        ),
        "fill_in_blank": (
            f"Generate {question_count} fill-in-the-blank questions about {topic} in JSON format. "
            f"Context: {context}\n"
            f"Use 'text' field with '_____' for blanks and 'correct_answer' field."
        ),
        "short_answer": (
            f"Generate {question_count} short answer questions about {topic} in JSON format. "
            f"Context: {context}\n"
            f"Include 'text' field and 'correct_answer' field with brief answers."
        ),
        "long_answer": (
            f"Generate {question_count} long answer questions about {topic} in JSON format. "
            f"Context: {context}\n"
            f"Include 'text' field and 'correct_answer' field with detailed answers."
        ),
    }
    return prompt_templates.get(assessment_type, "")


class GenerateAssessmentView(APIView):
    @async_view
    async def post(self, request: HttpRequest) -> Response:
        try:
            topic = request.data.get("topic")
            assessment_type = request.data.get("assessmentType")
            question_count = request.data.get("questionCount")

            if not all([topic, assessment_type, question_count]):
                return Response(
                    {"error": "Missing required fields"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate embedding for the topic using Pinecone's inference API
            topic_embeddings = await generate_gemini_embeddings([topic])
            if not topic_embeddings:
                return Response(
                    {"error": "Failed to generate embeddings"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Query Pinecone
            index = pc.Index(INDEX_NAME)
            query_response = await sync_to_async(index.query)(
                vector=topic_embeddings[0],
                top_k=3,
                namespace=NAMESPACE,
                include_metadata=True
            )

            # Extract relevant texts from query results
            context = " ".join([
                match['metadata']['text']
                for match in query_response['matches']
            ]) if query_response['matches'] else ""

            # Continue with question generation...
            prompt = await generate_prompt(assessment_type, question_count, topic, context)
            generated_text = await make_api_request(prompt)

            if generated_text is None:
                return Response(
                    {"error": "Failed to generate questions"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            questions = parse_generated_text(generated_text, assessment_type)
            
            return Response(
                {
                    "questions": questions,
                    "assessmentType": assessment_type
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error in GenerateAssessmentView: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ScoreAnswersView(APIView):
    """View for scoring assessment answers"""

    @async_view
    async def post(self, request: HttpRequest) -> Response:
        try:
            answers = request.data.get("answers")
            topic = request.data.get("topic")

            if not answers or not topic:
                return Response(
                    {"error": "Missing required fields"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tasks = [process_answer(answer, topic) for answer in answers]
            results = await asyncio.gather(*tasks)
            total_score = sum(result["score"] for result in results)

            return Response(
                {"total_score": total_score, "results": results},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error in ScoreAnswersView: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @async_view
    async def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        try:
            files = request.FILES.getlist("documents")
            topic = request.data.get("topic")

            if not files:
                return Response(
                    {"error": "No files provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # First, verify Pinecone index dimensions
            index_info = pc.describe_index(INDEX_NAME)
            if index_info.dimension != VECTOR_DIMENSION:
                logger.error(f"Index dimension mismatch. Index: {index_info.dimension}, Expected: {VECTOR_DIMENSION}")
                return Response(
                    {"error": "Index dimension mismatch. Please recreate the index with correct dimensions."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            @sync_to_async
            def save_file(file):
                uploaded_file = UploadedFile.objects.create(file=file)
                return uploaded_file

            # Process files
            processed_files = []
            failed_files = []
            
            for file in files:
                try:
                    uploaded_file = await save_file(file)
                    file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
                    
                    loader = None
                    if file.content_type == "application/pdf":
                        loader = UnstructuredPDFLoader(file_path)
                    elif file.content_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                        loader = UnstructuredWordDocumentLoader(file_path)
                    elif file.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                        loader = UnstructuredExcelLoader(file_path)
                    elif file.content_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                        loader = UnstructuredPowerPointLoader(file_path)
                    elif file.content_type == "text/csv":
                        loader = CSVLoader(file_path)
                    else:
                        failed_files.append({"file": file.name, "error": "Unsupported file type"})
                        continue

                    documents = await sync_to_async(loader.load)()
                    await process_documents(documents)
                    processed_files.append(file.name)
                    
                except Exception as e:
                    logger.error(f"Error processing file {file.name}: {e}")
                    failed_files.append({"file": file.name, "error": str(e)})

            return Response({
                "message": "File processing completed",
                "processed_files": processed_files,
                "failed_files": failed_files
            }, status=status.HTTP_200_OK if processed_files else status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Error in FileUploadView: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )