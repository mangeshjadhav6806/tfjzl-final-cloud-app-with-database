# Online Course Assessment App

A Django implementation of the final project assessment: course lessons, mock-exam questions and choices, submissions, and scored exam results.

## Run locally

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Open `http://127.0.0.1:8000/admin/` to add courses, lessons, questions, and choices. Create a Django user and matching Learner record, then visit `/courses/<course-id>/` to take the mock exam. Questions are graded against their configured point values; passing is 70%.

## Tests

```powershell
py manage.py test
```