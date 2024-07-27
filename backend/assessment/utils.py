import chromadb
from langchain_community.vectorstores import Chroma
import google.generativeai as genai
import os
from pypdf import PdfReader
import re

import json

def get_chroma_client():
    return chromadb.Client()

def load_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

def split_text(text):
    return [i for i in re.split('\n\n', text) if i.strip()]

class GeminiEmbeddingFunction:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "models/embedding-001"

    def __call__(self, texts):
        embeddings = []
        for text in texts:
            result = genai.embed_content(model=self.model, content=text, task_type="retrieval_document", title="Custom query")
            embeddings.append(result["embedding"])
        return embeddings

def process_document(file_path, topic):
    # Initialize ChromaDB client
    client = get_chroma_client()
    
    # Load the document
    document_content = load_pdf(file_path)
    
    # Split the text into chunks
    chunked_text = split_text(document_content)
    
    # Initialize embeddings provider
    embedding_function = GeminiEmbeddingFunction()
    
    # Initialize Chroma collection
    collection_name = f"{topic}_collection"
    collection = Chroma(client=client, collection_name=collection_name, embedding_function=embedding_function)
    
    # Add document chunks to ChromaDB collection
    collection.add_texts(chunked_text)

    return collection


def generate_questions(topic, assessment_type, collection=None, question_count=5):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')

    if assessment_type == 'mcq':
        prompt_template = (
            f"Generate {question_count} {assessment_type} questions about {{topic}} in JSON format. "
            f"Each question should have a 'text' field for the question, an 'options' field for the answer options, "
            f"and a 'correct_answer' field for the correct answer. If it's a multiple-choice question, 'options' should include the correct answer and 3 incorrect options."
        )
    elif assessment_type == 'true_false':
        prompt_template = (
            f"Generate {question_count} {assessment_type} questions about {{topic}} in JSON format. "
            f"Each question should have a 'text' field for the question and a 'correct_answer' field which should be 'True' or 'False'."
        )
    elif assessment_type == 'fill_in_blank':
        prompt_template = (
            f"Generate {question_count} {assessment_type} questions about {{topic}} in JSON format. "
            f"Each question should have a 'text' field for the question with blanks represented by underscores and a 'correct_answer' field with the correct answer to fill in the blanks."
        )
    elif assessment_type == 'short_answer':
        prompt_template = (
            f"Generate {question_count} short answer questions about {{topic}} in JSON format. "
            f"Each question should have a 'text' field for the question and a 'correct_answer' field for the correct answer."
        )
    elif assessment_type == 'long_answer':
        prompt_template = (
            f"Generate {question_count} long answer questions about {{topic}} in JSON format. "
            f"Each question should have a 'text' field for the question and a 'correct_answer' field for the correct answer."
        )
    else:
        raise ValueError(f"Unsupported assessment type: {assessment_type}")

    if collection:
        # Retrieve relevant passages from the collection
        results = collection.similarity_search(topic, k=3)
        context = "\n".join([doc.page_content for doc in results])
        prompt = f"Based on the following context about {topic}, {prompt_template.format(topic=topic)}\n\nContext:\n{context}\n\nQuestions:"
    else:
        prompt = prompt_template.format(topic=topic)

    response = model.generate_content(prompt)
    
    try:
        questions = json.loads(response.text)
        for question in questions:
            question['type'] = assessment_type
        return questions
    except json.JSONDecodeError:
        # If JSON parsing fails, return the raw text
        return [{'text': response.text, 'type': assessment_type}]