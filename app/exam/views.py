from rest_framework import generics
from rest_framework.response import Response
from .models import Exam, ExamSubmission
from .serializers import (AllExamsSerializer, 
                          ExamSerializer, 
                          ExamSubmissionSerializer, 
                          SubmissionResultSerializer, 
                          AllSubmissionsSerializer)
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from rest_framework import status
from drf_spectacular.utils import extend_schema

# Create your views here.


class AllExamsView(generics.ListAPIView):
    serializer_class = AllExamsSerializer
    queryset = Exam.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('id',)


class ExamListView(generics.ListAPIView):
    queryset = Exam.objects.prefetch_related(
        'examquestion_set__question__alternatives'
    )
    serializer_class = ExamSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('id',)


class SubmitExamView(APIView):
    @extend_schema(
        methods=("POST",),
        description="Receives the data that the user will send to submit an exam.",
        request=ExamSubmissionSerializer,
        responses=ExamSubmissionSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = ExamSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionResultView(generics.RetrieveAPIView):
    queryset = ExamSubmission.objects.prefetch_related('answers__question')
    serializer_class = SubmissionResultSerializer

    def get(self, request, *args, **kwargs):
        try:
            submission = self.get_object()
            serializer = self.get_serializer(submission)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ExamSubmission.DoesNotExist:
            return Response(
                {"detail": "Submission not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class SubmissionResultByStudentAndExamView(APIView):
    def get(self, request, student_id, exam_id, *args, **kwargs):
        try:
            submission = ExamSubmission.objects.get(student_id=student_id, exam_id=exam_id)
            serializer = SubmissionResultSerializer(submission)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ExamSubmission.DoesNotExist:
            return Response(
                {"detail": "Submission not found for the given student and exam."},
                status=status.HTTP_404_NOT_FOUND
            )

class AllSubmissionsView(generics.ListAPIView):
    serializer_class = AllSubmissionsSerializer
    queryset = ExamSubmission.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('id',)
