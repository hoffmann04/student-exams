from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Exam, ExamQuestion, ExamSubmission, Answer
from question.models import Question, Alternative
from student.models import Student


class AllExamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'name']


class AlternativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternative
        fields = ['id', 'content', 'option'] # Do not send is_correct, there's no need


class QuestionSerializer(serializers.ModelSerializer):
    alternatives = AlternativeSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'content', 'alternatives']


class ExamQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = ExamQuestion
        fields = ['id', 'number', 'question']


class ExamSerializer(serializers.ModelSerializer):
    questions = ExamQuestionSerializer(source='examquestion_set', many=True)

    class Meta:
        model = Exam
        fields = ['id', 'name', 'questions']


class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all(), source='question')
    selected_alternative_id = serializers.IntegerField()

    class Meta:
        model = Answer
        fields = ['question_id', 'selected_alternative_id']


class ExamSubmissionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source='student')
    exam_id = serializers.PrimaryKeyRelatedField(queryset=Exam.objects.all(), source='exam')

    class Meta:
        model = ExamSubmission
        fields = ['student_id', 'exam_id', 'answers']

    def validate(self, data):
        # Check if a submission already exists for the student and exam
        student = data['student']
        exam = data['exam']
        if ExamSubmission.objects.filter(student=student, exam=exam).exists():
            raise ValidationError("A submission already exists for this student and exam.")

        # Validate if the questions in the answers belong to the exam
        exam_questions = set(exam.questions.values_list('id', flat=True))
        answer_question_ids = {answer['question'].id for answer in data['answers']}
        invalid_questions = answer_question_ids - exam_questions
        if invalid_questions:
            raise ValidationError(f"Questions {invalid_questions} do not belong to the exam.")

        return data

    def create(self, validated_data):
        # Extract answers from validated data
        answers_data = validated_data.pop('answers')
        # Create the submission
        submission = ExamSubmission.objects.create(**validated_data)

        # Create the associated answers
        for answer_data in answers_data:
            question = answer_data['question']
            selected_alternative_id = answer_data['selected_alternative_id']
            is_correct = Alternative.objects.filter(
                id=selected_alternative_id, 
                question=question, 
                is_correct=True
            ).exists()

            Answer.objects.create(
                submission=submission,
                question=question,
                selected_alternative_id=selected_alternative_id,
                is_correct=is_correct
            )
        return submission


class SubmissionResultSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()
    total_correct = serializers.SerializerMethodField()
    percentage_correct = serializers.SerializerMethodField()

    class Meta:
        model = ExamSubmission
        fields = ['id', 'exam', 'student', 'answers', 'total_correct', 'percentage_correct']

    def get_answers(self, obj):
        answers_list = []
        for answer in obj.answers.all():
            correct_alternative = answer.question.alternatives.filter(is_correct=True).first()
            selected_alternative = answer.question.alternatives.filter(id=answer.selected_alternative_id).first()

            # Let's return the selected and the correct answer content
            # This data can be used in the front-end to help the student know the correct answer
            answers_list.append({
                "question": answer.question.content,
                "selected_alternative_id": answer.selected_alternative_id,
                "selected_alternative_content": selected_alternative.content if selected_alternative else None,
                "is_correct": answer.is_correct,
                "correct_alternative_content": correct_alternative.content if correct_alternative else None,
            })
        return answers_list

    def get_total_correct(self, obj):
        return obj.answers.filter(is_correct=True).count()

    def get_percentage_correct(self, obj):
        total_questions = obj.answers.count()
        total_correct = self.get_total_correct(obj)
        if total_questions == 0:
            return 0
        return round((total_correct / total_questions) * 100, 2)

class AllSubmissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSubmission
        fields = ['id', 'exam', 'student', 'submitted_at']
