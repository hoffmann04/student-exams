from django.urls import path
from .views import AllExams, ExamListView, SubmitExamView, SubmissionResultView, SubmissionResultByStudentAndExamView

app_name='quiz'

urlpatterns = [
    path('', AllExams.as_view(), name='exam'),
    # path('full/', ExamView.as_view(), name='exam_full'),
    path('full/', ExamListView.as_view(), name='exam-full'),
    path('submit-exam/', SubmitExamView.as_view(), name='submit-exam'),
    path('submission/<int:pk>/results/', SubmissionResultView.as_view(), name='submission-results-by-id'),
    path(
        'submission/results/student/<int:student_id>/exam/<int:exam_id>/',
        SubmissionResultByStudentAndExamView.as_view(),
        name='submission-results-by-student-and-exam'
    ),
]
