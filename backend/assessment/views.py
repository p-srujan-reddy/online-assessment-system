from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Assessment, Question, Answer
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate

class GenerateAssessmentView(APIView):
    def post(self, request):
        topic = request.data.get('topic')
        assessment_type = request.data.get('assessmentType')
        question_count = request.data.get('questionCount')

        if not all([topic, assessment_type, question_count]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize LangChain
        llm = OpenAI(temperature=0.7)

        # Create a prompt template
        prompt = PromptTemplate(
            input_variables=["topic", "assessment_type", "question_count"],
            template="Generate {question_count} {assessment_type} questions about {topic}. For each question, provide the correct answer and, if it's a multiple-choice question, provide 3 incorrect options."
        )

        # Generate questions using LangChain
        result = llm(prompt.format(topic=topic, assessment_type=assessment_type, question_count=question_count))

        # TODO: Parse the result and create Assessment, Question, and Answer objects

        # For now, we'll just return the raw result
        return Response({"result": result}, status=status.HTTP_200_OK)