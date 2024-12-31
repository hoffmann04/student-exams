from django.urls import path
from .views import (AllExamsView, 
                    ExamListView, 
                    SubmitExamView, 
                    SubmissionResultView, 
                    SubmissionResultByStudentAndExamView, 
                    AllSubmissionsView)

app_name='quiz'

urlpatterns = [
    path('', AllExamsView.as_view(), name='exam'),
    path('full/', ExamListView.as_view(), name='exam-full'),
    path('submit-exam/', SubmitExamView.as_view(), name='submit-exam'),
    path('submission/results/', AllSubmissionsView.as_view(), name='all-submission-results'),
    path('submission/results/<int:pk>/', SubmissionResultView.as_view(), name='submission-results-by-id'),
    path(
        'submission/results/student/<int:student_id>/exam/<int:exam_id>/',
        SubmissionResultByStudentAndExamView.as_view(),
        name='submission-results-by-student-and-exam'
    ),
]
