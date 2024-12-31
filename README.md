# Student Exams Project
Repository containing a Django API that allow students to submit exams and check the results afterwards.

To run this project, you should have Docker installed.

To configure the project, run:

`docker compose up --build -d`.

To access the project, open the terminal and run:

`docker exec -it medway-api bash`

Inside the container you can create a superuser with the command below:

`python manage.py createsuperuser`

Then you can use the created credentials to access the Django admin: http://0.0.0.0:8000/admin/.

## Desired features:

1. The student must be able to answer an exam, sending all the answers in the same request. There is no need of any kind of authentication.

2. The sudent must be able to get the results of the submitted exam. The results must have the amount of questions that the student got right and also the percentage of correct answers.

## Development approach:

The idea was to keep it simple. It was created the models to save a student submission and its answers, the needed serializers and views. It was also created some test scenarios to cover some parts of the feature that was created.

It could be used a separate `api` folder to add the REST API related things (url.py, views.py, etc), but for the sake of simplicity it was used the pre existent files (views.py, serializers.py, etc) that the project already had.

## How to use:

To make it easier to test it was installed in this project the Djando Spectacular lib.

With this lib we can use swagger to access the endpoints to test them without needing to use an external API client.

To access it you can use the link: http://localhost:8000/api/schema/swagger-ui/

Then you can make some requests using the endpoints.

### Endpoints:

All endpoints are listed below:

### Get Method:

|Endpoint|Functionality|Method|
|--------|-------------|------|
|/exam/|Get all the existent exams|GET|
|/exam/?id=2|Get a specific exam using its id|GET|
|/exam/full/|Get all the existent exams with its questions and the respective alternatives|GET|
|/exam/full/?id=1|Get all the existent exams with its questions and the respective alternatives filtering by the exam id|GET|
|/exam/submission/<:id>/results/|Given the submission id, get a specific submission|GET|
|/exam/submission/results/student/<:student_id>/exam/<:exam_id>/|Given the student id and the exam id, get the related submission|GET|


### POST Method:

|Endpoint|Functionality|Method|JSON Fields|
|--------|-------------|------|-----------|
|/exam/submit-exam/|Submit an exam|POST|{"student_id": 1, "exam_id": 2, "answers": [{"question_id": 6, "selected_alternative_id": 23},{"question_id": 7, "selected_alternative_id": 27}, ...other answers]}|

### Tests:

The tests are in the 'tests.py' file. It was covered the following scenarios:

1. Success in the exam submission.
2. Test duplicated submission.
3. Test question that do not belong to the exam.
4. Test submission results.

To run the tests, enter in the application using `docker exec -it medway-api bash` and then run `python manage.py test`

It can be done a lot of other tests, like:

1. Test submission with missing required fields (such as student_id, exam_id, answers) and verify proper error handling.
2. Ensure the results calculation is accurate when only some answers are correct.
3. Test with an invalid or non-existent selected_alternative and ensure proper error response.
4. Test scenarios to ensure correct percentage calculation, e.g., no correct answers, all correct answers, or partial correctness.
5. Ensure the endpoint correctly handles cases where a student hasn’t submitted answers yet.
6. Test a submission containing duplicated questions in the answer dict in the resquest.
