from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Exam, ExamQuestion, ExamSubmission, Answer
from question.models import Question, Alternative
from student.models import Student

# Create your tests here.

class ExamSubmissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create student
        self.student = Student.objects.create_user(username="test_student", password="password", email="test@student.com")

        # Create exam
        self.exam = Exam.objects.create(name="Sample Exam")

        # Create questions
        self.question1 = Question.objects.create(content="What is 2 + 2?")
        self.question2 = Question.objects.create(content="What is the capital of France?")

         # Add questions to exam using ExamQuestion
        ExamQuestion.objects.create(exam=self.exam, question=self.question1, number=1)
        ExamQuestion.objects.create(exam=self.exam, question=self.question2, number=2)

        # Create alternatives
        self.alternative1_q1 = Alternative.objects.create(question=self.question1, content="4", option=1, is_correct=True)
        self.alternative2_q1 = Alternative.objects.create(question=self.question1, content="5", option=2, is_correct=False)
        self.alternative1_q2 = Alternative.objects.create(question=self.question2, content="Paris", option=1, is_correct=True)
        self.alternative2_q2 = Alternative.objects.create(question=self.question2, content="Berlin", option=2, is_correct=False)

        # Authentication setup
        self.client.force_authenticate(user=self.student)

        # Define endpoint URLs
        self.submission_url = "/exam/submit-exam/"
        self.submission_results = '/exam/submission/'

    def test_create_submission_success(self):
        payload = {
            "exam_id": self.exam.id,
            "student_id": self.student.id,
            "answers": [
                {"question_id": self.question1.id, "selected_alternative_id": self.alternative1_q1.id},
                {"question_id": self.question2.id, "selected_alternative_id": self.alternative1_q2.id},
            ],
        }
        response = self.client.post(self.submission_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExamSubmission.objects.count(), 1)

    def test_duplicate_submission_validation(self):
        # Create an initial submission
        ExamSubmission.objects.create(student=self.student, exam=self.exam)

        # Attempt to create another submission for the same student and exam
        payload = {
            "exam_id": self.exam.id,
            "student_id": self.student.id,
            "answers": [
                {"question_id": self.question1.id, "selected_alternative_id": self.alternative1_q1.id},
                {"question_id": self.question2.id, "selected_alternative_id": self.alternative1_q2.id},
            ],
        }
        response = self.client.post(self.submission_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("A submission already exists", str(response.data))

    def test_invalid_questions_validation(self):
        # Create a question not linked to the exam
        unrelated_question = Question.objects.create(content="What is the color of the sky?")

        payload = {
            "exam_id": self.exam.id,
            "student_id": self.student.id,
            "answers": [
                {"question_id": unrelated_question.id, "selected_alternative_id": 1},
                {"question_id": self.question2.id, "selected_alternative_id": self.alternative1_q2.id},
            ],
        }
        response = self.client.post(self.submission_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("do not belong to the exam", str(response.data))

    def test_get_submission_results(self):
        # Create a submission and answers
        submission = ExamSubmission.objects.create(student=self.student, exam=self.exam)
        Answer.objects.create(submission=submission, question=self.question1, selected_alternative_id=1, is_correct=True)
        Answer.objects.create(submission=submission, question=self.question2, selected_alternative_id=2, is_correct=False)

        response = self.client.get(f"{self.submission_results}{submission.id}/results/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_correct", response.data)
        self.assertEqual(response.data["total_correct"], 1)
        self.assertEqual(response.data["percentage_correct"], 50.0)
