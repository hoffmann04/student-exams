from django.db import models

from question.models import Question
from student.models import Student


class Exam(models.Model):
    name = models.CharField(max_length=100)
    questions = models.ManyToManyField(Question, through='ExamQuestion', related_name='questions')

    def __str__(self):
        return self.name


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('exam', 'number')
        ordering = ['number']

    def __str__(self):
        return f'{self.question} - {self.exam}'


class ExamSubmission(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure that the student can only submit once for a given exam.
        constraints = [
            models.UniqueConstraint('exam', 'student', name='unique_exam_student'),
        ]

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.submitted_at}"

class Answer(models.Model):
    submission = models.ForeignKey(ExamSubmission, on_delete=models.CASCADE, related_name='answers')
    # Here it can also be used the ExamQuestion model instead of Question directly
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_alternative_id = models.IntegerField()  # Stores the alternative selected by the user
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer by {self.submission.student} for {self.question}"
