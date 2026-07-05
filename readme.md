# JanMitra

JanMitra is an AI-powered public development intelligence platform that transforms fragmented citizen complaints into consolidated, prioritized, and actionable development proposals.

Instead of treating every citizen complaint as an isolated request, JanMitra uses Google Gemini to understand multiple complaints, identify similar development needs, consolidate them into common issues, comparatively prioritize those issues, and generate proposed solutions with estimated budgets.

The generated development proposals are sent to an MP review dashboard for approval or modification. Approved proposals are then published through a transparent public development portal.

JanMitra was developed for the GDG WOW Visakhapatnam 2026 Hackathon.

---

## Problem Statement

Citizen development complaints are often fragmented across different platforms, languages, locations, and communication channels.

For example, citizens may submit complaints such as:

```text
"Water supply stopped near Court Road."

"Pipe burst in Ward 11."

"No water since morning near Court Road."

"Main water line damaged near Court Road."
```

Although these complaints may describe the same underlying development problem, traditional complaint systems usually store them as separate requests.

This creates several problems:

- Duplicate complaints must be manually identified.
- Decision makers receive large unstructured complaint lists.
- Development priorities are difficult to compare.
- Citizen impact is difficult to estimate.
- Proposed solutions require manual research.
- Budget estimation is disconnected from complaint processing.
- Citizens have limited visibility into development decisions.

JanMitra converts these fragmented complaints into structured development intelligence.

---

# How JanMitra Works

The complete JanMitra workflow is:

```text
Citizen
   ↓
Creates Development Request
   ↓
DRAFT
   ↓
Submits Request
   ↓
READY_FOR_AI
   ↓
AI Worker Detects Queued Requests
   ↓
Gemini Complaint Consolidation
   ↓
Consolidated Development Issues
   ↓
Gemini Comparative Prioritization
   ↓
Priority Score
Priority Reasoning
Affected Population Estimate
   ↓
Gemini Development Proposal Generation
   ↓
Proposed Solution
Proposed Budget
Budget Reasoning
Implementation Plan
Expected Impact
Estimated Duration
   ↓
PENDING_MP_REVIEW
   ↓
MP Dashboard
   ├── Approve Proposal
   │
   └── Edit and Approve Proposal
   ↓
APPROVED / APPROVED_WITH_CHANGES
   ↓
Public Development Portal
```

---

# Core Features

## Citizen Development Requests

Citizens can create development requests describing public infrastructure or development problems.

A request can contain:

- Title
- Description
- Language
- Locality
- Ward
- District
- State
- Latitude
- Longitude
- Images
- Video
- Audio

Requests initially remain in the `DRAFT` state.

Citizens can modify draft requests before submission.

After submission, the request enters the AI processing queue.

---

## Firebase Authentication

JanMitra uses Firebase Authentication for browser-side user authentication.

The frontend authenticates the user using Firebase.

Firebase generates an ID token.

The frontend sends the token to the Django API:

```text
Authorization: Bearer <firebase-id-token>
```

The Django backend verifies the Firebase token using the Firebase Admin SDK.

The authenticated Firebase identity is mapped to a JanMitra user.

---

## Role-Based Access Control

JanMitra currently defines four roles:

```text
CLIENT
MANAGEMENT
MP
ADMIN
```

### CLIENT

Represents a citizen.

CLIENT users can:

- Create development requests
- Update draft requests
- Upload request evidence
- Remove request evidence
- Submit requests
- View their submitted requests

### MANAGEMENT

Reserved for management-side development workflows.

Management users can access intelligence issue APIs.

The complete management dashboard is planned as future scope.

### MP

Represents an MP or authorized public decision maker.

MP users can:

- View AI-generated development proposals
- Inspect consolidated citizen problems
- Review AI priority reasoning
- Review proposed solutions
- Review proposed budgets
- Approve proposals
- Modify and approve proposals

### ADMIN

Administrative role with elevated backend permissions.

---

# AI Intelligence Pipeline

The intelligence pipeline is implemented inside the Django `intelligence` application.

The pipeline contains three major Gemini stages.

---

## Stage 1: Complaint Consolidation

Citizen requests with the status:

```text
READY_FOR_AI
```

are collected as a batch.

The complaints are sent to Gemini.

Gemini analyzes:

- Complaint meaning
- Development need
- Location
- Category
- Subcategory
- Language
- Semantic similarity

Similar complaints are consolidated into a single development issue.

Example:

```text
Complaint 1:
"Water supply stopped near Court Road."

Complaint 2:
"Pipe burst in Ward 11."

Complaint 3:
"No water since morning near Court Road."

                    ↓

Consolidated Issue:

Water Pipe Burst Causing Supply Disruption
```

Gemini returns structured JSON validated using Pydantic models.

Each original citizen complaint remains linked to the consolidated issue through the `IssueProblem` relationship.

The relationship stores:

```text
similarity_score
ai_reasoning
linked_at
```

This means JanMitra never loses the original citizen request.

The system preserves the relationship:

```text
Citizen Problem
      ↓
IssueProblem
      ↓
Consolidated Issue
```

---

## Stage 2: Comparative Development Prioritization

After consolidation, JanMitra comparatively analyzes the resulting development issues.

Gemini evaluates the issue list and generates:

- Priority score
- Priority reasoning
- Estimated affected population

The priority score is stored as a value from the AI prioritization process.

Example:

```text
Issue:
Water Pipe Burst Causing Supply Disruption

Priority Score:
85.00

Estimated Affected Population:
2500

Priority Reasoning:
The disruption affects essential water access for a
large residential population and requires urgent repair.
```

Issues are stored in priority order.

The issue status progresses through the intelligence workflow.

```text
IDENTIFIED
    ↓
PRIORITIZED
    ↓
PROPOSAL_READY
    ↓
PENDING_MP_REVIEW
```

---

## Stage 3: Development Proposal Generation

For prioritized development issues, Gemini generates an actionable development proposal.

The generated proposal can contain:

- Proposed solution
- Proposed budget
- Budget reasoning
- Implementation plan
- Expected impact
- Estimated implementation duration

Example:

```text
Issue:
Water Pipe Burst Causing Supply Disruption

Proposed Solution:
Expedited repair and replacement of the burst water
pipe section, including excavation, damaged pipe
replacement, and road surface restoration.

Proposed Budget:
₹1,20,000

Estimated Duration:
7 days
```

The proposal is stored as a `DevelopmentProposal`.

The proposal is then moved to:

```text
PENDING_MP_REVIEW
```

and becomes visible on the MP dashboard.

---

# MP Review Workflow

The MP dashboard displays AI-generated development proposals.

The MP can inspect:

- Development issue title
- Consolidated issue summary
- Development category
- Location
- Priority score
- Priority reasoning
- Estimated affected population
- Number of linked citizen complaints
- Original citizen complaint evidence
- AI-proposed solution
- Proposed budget
- Budget reasoning
- Implementation plan
- Expected impact
- Estimated implementation duration

The MP has two current actions.

---

## Approve Proposal

The MP can approve the AI-generated proposal without modification.

The AI-proposed solution and budget become the final approved values.

The proposal status becomes:

```text
APPROVED
```

---

## Edit and Approve

The MP can modify:

- Final development solution
- Final development budget

The modified values are stored as the final approved proposal.

The proposal status becomes:

```text
APPROVED_WITH_CHANGES
```

The original AI-generated proposal remains available in the database.

This allows the system to distinguish between:

```text
AI Proposed Decision
```

and:

```text
MP Final Decision
```

---

# Public Development Portal

Approved development proposals become visible through the public development portal.

The public portal does not require authentication.

The portal displays:

- Approved projects
- Development category
- Development issue
- Issue summary
- Location
- Priority score
- Estimated affected population
- Approved development solution
- Approved budget
- Approval status

The public dashboard also calculates:

- Total approved projects
- Total public investment
- Estimated people impacted

Citizens can search projects and filter projects by category.

The objective is to create a transparent connection between:

```text
Citizen Request
      ↓
Development Intelligence
      ↓
Public Decision
      ↓
Public Visibility
```

---

# Automated AI Worker

JanMitra includes a Django management command that automatically processes queued citizen requests.

The worker is located at:

```text
backend/intelligence/management/commands/run_ai_worker.py
```

The worker periodically checks for problems with:

```text
READY_FOR_AI
```

When queued problems are found, the worker runs the complete intelligence pipeline.

```text
READY_FOR_AI Problems
        ↓
run_full_intelligence_pipeline()
        ↓
Complaint Consolidation
        ↓
Issue Prioritization
        ↓
Proposal Generation
```

The worker allows JanMitra to process citizen complaints without manually triggering the AI API.

---

# Technology Stack

## Frontend

- HTML5
- CSS3
- JavaScript ES Modules
- Firebase Authentication

## Backend

- Python
- Django 5.2
- Django REST Framework 3.16

## Database

- PostgreSQL
- `dj-database-url`
- `psycopg`

The current project is configured using a PostgreSQL `DATABASE_URL`.

## Artificial Intelligence

- Google Gemini
- Google GenAI Python SDK
- Pydantic structured response schemas

## Authentication

- Firebase Authentication
- Firebase Admin SDK
- Custom Django Firebase authentication class

## Media Storage

- Cloudinary

## API

- Django REST Framework
- JSON REST APIs
- Bearer token authentication

---

# Project Structure

```text
janmitra/
├── backend/
│   ├── accounts/
│   │   ├── authentication.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── problems/
│   │   ├── cloudinary_service.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── intelligence/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── run_ai_worker.py
│   │   │
│   │   ├── gemini_service.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── janmat/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── css/
│   │   ├── global.css
│   │   ├── auth.css
│   │   ├── client.css
│   │   ├── mp.css
│   │   └── public.css
│   │
│   ├── js/
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── client.js
│   │   ├── config.js
│   │   ├── firebase.js
│   │   ├── mp.js
│   │   └── public.js
│   │
│   ├── pages/
│   │   ├── client.html
│   │   ├── mp.html
│   │   └── public.html
│   │
│   └── index.html
│
├── .gitignore
└── README.md
```

---

# Prerequisites

Before running JanMitra, install:

- Python 3.13
- Git
- PostgreSQL-compatible database access
- A Firebase project
- A Gemini API key
- A Cloudinary account
- A static HTTP server or VS Code Live Server

Python 3.13 is recommended because the project was developed and tested using Python 3.13.

Check Python:

```bash
python3 --version
```

Expected:

```text
Python 3.13.x
```

---

# 1. Clone the Repository

Clone the JanMitra repository.

```bash
git clone <repository-url>
```

Enter the project directory.

```bash
cd janmitra
```

The following directories should be visible:

```text
backend
frontend
```

---

# 2. Create the Python Virtual Environment

Create a virtual environment from the project root.

```bash
python3 -m venv .venv
```

Activate the environment.

## macOS or Linux

```bash
source .venv/bin/activate
```

## Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Verify Python:

```bash
python --version
```

---

# 3. Install Backend Dependencies

Enter the backend directory.

```bash
cd backend
```

Install the required Python packages.

```bash
pip install -r requirements.txt
```

The project currently requires:

```text
Django >= 5.2, < 6.0
djangorestframework >= 3.16, < 4.0
django-cors-headers >= 4.7, < 5.0
python-dotenv >= 1.1, < 2.0
psycopg[binary] >= 3.2, < 4.0
dj-database-url >= 3.0, < 4.0
firebase-admin >= 6.8, < 8.0
cloudinary >= 1.44, < 2.0
google-genai >= 1.0
```

Verify Django:

```bash
python -m django --version
```

---

# 4. Create a PostgreSQL Database

JanMitra requires a PostgreSQL-compatible database.

You can use:

- Local PostgreSQL
- Neon
- Supabase PostgreSQL
- Railway PostgreSQL
- Another PostgreSQL provider

Obtain the PostgreSQL connection URL.

Example format:

```text
postgresql://USERNAME:PASSWORD@HOST/DATABASE?sslmode=require
```

Do not commit the database URL to Git.

---

# 5. Create a Firebase Project

Create a Firebase project from the Firebase Console.

Enable Firebase Authentication.

Navigate to:

```text
Firebase Console
    ↓
Authentication
    ↓
Sign-in method
```

Enable:

```text
Email/Password
```

JanMitra currently uses email and password authentication in the frontend.

---

# 6. Create a Firebase Web Application

Inside the Firebase project, create a Web App.

Firebase will provide a configuration similar to:

```javascript
const firebaseConfig = {
    apiKey: "...",
    authDomain: "...",
    projectId: "...",
    storageBucket: "...",
    messagingSenderId: "...",
    appId: "...",
};
```

Open:

```text
frontend/js/config.js
```

Configure:

```javascript
export const firebaseConfig = {
    apiKey: "YOUR_FIREBASE_WEB_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_FIREBASE_APP_ID",
    measurementId: "YOUR_MEASUREMENT_ID",
};
```

The Firebase web configuration is used by the browser application.

Do not place Gemini, Django, database, Cloudinary API secret, or Firebase Admin private credentials in this file.

---

# 7. Create Firebase Admin Credentials

The Django backend verifies Firebase ID tokens using the Firebase Admin SDK.

Open the Firebase Console.

Navigate to:

```text
Project Settings
    ↓
Service Accounts
    ↓
Firebase Admin SDK
```

Generate a new private key.

A JSON service account file will be downloaded.

Create the directory:

```bash
mkdir -p firebase
```

Place the JSON file inside:

```text
backend/firebase/
```

Example:

```text
backend/firebase/firebase-adminsdk.json
```

The `firebase/` directory must remain ignored by Git.

Never publish the Firebase Admin service account JSON.

---

# 8. Create a Gemini API Key

Create a Gemini API key using Google AI Studio.

The backend uses the Google GenAI SDK.

The current intelligence pipeline uses:

```text
gemini-2.5-flash
```

Store the Gemini API key only in the backend environment file.

Never place the Gemini API key in frontend JavaScript.

---

# 9. Configure Cloudinary

Create a Cloudinary account and obtain the Cloudinary environment URL.

The value normally follows a format similar to:

```text
cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

JanMitra uses Cloudinary for citizen complaint evidence uploads.

Supported evidence types in the backend include:

```text
IMAGE
VIDEO
AUDIO
```

The current backend limits are:

```text
Maximum images per problem: 5
Maximum videos per problem: 2
Maximum audio files per problem: 1
Maximum total media size: 100 MB
```

---

# 10. Configure Backend Environment Variables

Inside the `backend` directory, create:

```text
.env
```

Example:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

DATABASE_URL=postgresql://username:password@host/database?sslmode=require

GEMINI_API_KEY=your-gemini-api-key

GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/backend/firebase/firebase-adminsdk.json

CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

The variable names above match the current backend configuration.

For `GOOGLE_APPLICATION_CREDENTIALS`, use the absolute path to the Firebase Admin service account JSON.

Example on macOS:

```env
GOOGLE_APPLICATION_CREDENTIALS=/Users/username/projects/janmitra/backend/firebase/firebase-adminsdk.json
```

Do not commit `.env`.

---

# 11. Configure Django Hosts and CORS

Open:

```text
backend/janmat/settings.py
```

For local development, ensure `ALLOWED_HOSTS` contains:

```python
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]
```

The frontend must also be allowed by CORS.

For VS Code Live Server on port `5500`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]
```

If the frontend is served from another origin, add the exact origin.

For example:

```text
http://127.0.0.1:3000
```

requires:

```python
"http://127.0.0.1:3000"
```

Do not include URL paths in `CORS_ALLOWED_ORIGINS`.

---

# 12. Configure the Frontend API URL

Open:

```text
frontend/js/config.js
```

For local development, configure:

```javascript
export const API_BASE_URL =
    "http://127.0.0.1:8000/api/v1";
```

The frontend automatically appends individual API endpoint paths to this base URL.

The current frontend routes are:

```javascript
export const ROUTES = {
    LOGIN: "../index.html",
    CLIENT: "./client.html",
    MP: "./mp.html",
    PUBLIC: "./public.html",
};
```

The current frontend roles are:

```javascript
export const USER_ROLES = {
    CLIENT: "CLIENT",
    MANAGEMENT: "MANAGEMENT",
    MP: "MP",
    ADMIN: "ADMIN",
};
```

---

# 13. Apply Django Migrations

From the `backend` directory, run:

```bash
python manage.py migrate
```

Check migration state:

```bash
python manage.py showmigrations
```

Run the Django system check:

```bash
python manage.py check
```

Expected:

```text
System check identified no issues (0 silenced).
```

---

# 14. Start the Django API

From the `backend` directory:

```bash
python manage.py runserver
```

The API should start at:

```text
http://127.0.0.1:8000/
```

Keep this terminal running.

---

# 15. Start the JanMitra AI Worker

Open a second terminal.

Enter the project directory and activate the virtual environment.

```bash
cd janmitra
source .venv/bin/activate
cd backend
```

Verify that Django discovers the AI worker:

```bash
python manage.py help
```

The command should appear under the `intelligence` application:

```text
[intelligence]
    run_ai_worker
```

Start the worker:

```bash
python manage.py run_ai_worker
```

Expected output:

```text
JanMitra AI Worker started.
Checking for citizen requests every 60 seconds.

[12:00:00] No pending citizen requests.
```

Keep this terminal running.

When citizen requests enter `READY_FOR_AI`, the worker automatically executes the intelligence pipeline.

---

# 16. Start the Frontend

JanMitra uses native HTML, CSS, and JavaScript modules.

The frontend must be served through HTTP.

Do not open `index.html` directly using a `file://` URL.

One option is VS Code Live Server.

Open the project in VS Code.

Right-click:

```text
frontend/index.html
```

Select:

```text
Open with Live Server
```

The frontend will normally open at:

```text
http://127.0.0.1:5500/frontend/index.html
```

The exact path can vary depending on the Live Server workspace root.

---

# 17. Create a Citizen Account

Open the JanMitra frontend.

Select:

```text
Create account
```

Enter an email and password.

The frontend creates the Firebase Authentication user.

After authentication, the frontend calls:

```text
GET /api/v1/auth/me/
```

The Django backend verifies the Firebase ID token.

A JanMitra user is associated with the Firebase identity.

New users use the citizen/client workflow.

The user is redirected to:

```text
client.html
```

---

# 18. Submit a Citizen Development Request

From the citizen dashboard:

1. Create a new request.
2. Enter a title.
3. Enter a problem description.
4. Add location information if available.
5. Optionally attach evidence.
6. Submit the request.

The problem workflow is:

```text
DRAFT
   ↓
Citizen Submit
   ↓
READY_FOR_AI
```

After submission, the AI worker detects the queued request.

Example worker output:

```text
Found 1 citizen request(s).
Running JanMitra intelligence pipeline...

Pipeline completed successfully.
Created issues: 1
Prioritized issues: 1
Created proposals: 1
```

---

# 19. Create an MP User for Local Testing

Public user registration currently creates a normal citizen account.

To test the MP dashboard, first create a second account through the normal Firebase registration flow.

Use a different email address.

After the account has authenticated with the backend, open the Django shell:

```bash
python manage.py shell
```

Import the user model:

```python
from accounts.models import User
```

Find the user:

```python
mp_user = User.objects.get(
    email="mp@example.com"
)
```

Change the role:

```python
mp_user.role = "MP"
mp_user.save(
    update_fields=["role"]
)
```

Verify:

```python
mp_user.refresh_from_db()

print(mp_user.email)
print(mp_user.role)
```

Expected:

```text
mp@example.com
MP
```

Exit the Django shell:

```python
exit()
```

Sign out of the frontend.

Sign in using the MP Firebase account.

The role-based frontend routing sends the MP user to:

```text
pages/mp.html
```

Changing the Django role does not create a Firebase account or Firebase password.

The MP account must first exist in Firebase Authentication.

---

# 20. Review a Development Proposal

After the AI pipeline creates a proposal, open the MP dashboard.

The proposal should appear in the proposal queue.

Open the proposal to inspect:

```text
Priority Score
Citizen Request Count
Estimated Impact
Consolidated Development Need
Priority Intelligence
AI Proposed Development Solution
Proposed Budget
Budget Reasoning
Implementation Plan
Expected Impact
Estimated Duration
Citizen Request Evidence
```

The MP can choose:

```text
Approve Proposal
```

or:

```text
Edit and Approve
```

---

# 21. Approve a Proposal

When the MP approves the proposal without modifications:

```text
PENDING_MP_REVIEW
        ↓
APPROVED
```

The AI-proposed solution and budget become the final values.

The approved proposal becomes available through the public project API.

---

# 22. Edit and Approve a Proposal

The MP can modify the proposed solution and budget.

The final values are stored separately.

The proposal becomes:

```text
APPROVED_WITH_CHANGES
```

The final MP-approved values are used by the public development portal.

---

# 23. Open the Public Development Portal

Open:

```text
frontend/pages/public.html
```

Authentication is not required.

Approved projects should appear automatically.

The public portal uses:

```text
GET /api/v1/intelligence/public/projects/
```

Project details use:

```text
GET /api/v1/intelligence/public/projects/<proposal_id>/
```

Only approved development proposals are intended for public visibility.

---

# API Reference

All API endpoints are prefixed with:

```text
/api/v1/
```

---

## Authentication API

### Get Current User

```http
GET /api/v1/auth/me/
```

Authentication:

```text
Firebase Bearer Token
```

Example header:

```http
Authorization: Bearer <firebase-id-token>
```

---

## Citizen Problem APIs

### List Current User Problems

```http
GET /api/v1/problems/
```

Required role:

```text
CLIENT
```

---

### Create Problem

```http
POST /api/v1/problems/
```

Required role:

```text
CLIENT
```

---

### Get Problem

```http
GET /api/v1/problems/<problem_id>/
```

---

### Update Draft Problem

```http
PATCH /api/v1/problems/<problem_id>/
```

Problems can only be modified while in the draft state.

---

### Submit Problem

```http
POST /api/v1/problems/<problem_id>/submit/
```

The submitted problem enters the AI processing workflow.

---

## Problem Media APIs

### Generate Cloudinary Upload Signature

```http
POST /api/v1/problems/<problem_id>/media/upload-signature/
```

---

### Attach Uploaded Cloudinary Asset

```http
POST /api/v1/problems/<problem_id>/media/attach/
```

---

### Delete Problem Media

```http
DELETE /api/v1/problems/<problem_id>/media/<media_id>/
```

Media modifications are restricted to draft problems.

---

## Intelligence APIs

### List Intelligence Issues

```http
GET /api/v1/intelligence/issues/
```

Required role:

```text
MANAGEMENT or ADMIN
```

---

### Get Intelligence Issue

```http
GET /api/v1/intelligence/issues/<issue_id>/
```

Required role:

```text
MANAGEMENT or ADMIN
```

---

### Run Complaint Consolidation

```http
POST /api/v1/intelligence/pipeline/consolidate/
```

Required role:

```text
MANAGEMENT or ADMIN
```

---

### Run Complete Intelligence Pipeline

```http
POST /api/v1/intelligence/pipeline/run/
```

Required role:

```text
MANAGEMENT or ADMIN
```

The complete pipeline performs:

```text
Consolidation
    ↓
Prioritization
    ↓
Proposal Generation
```

The AI worker internally runs the same intelligence workflow.

---

## MP APIs

### List MP Proposals

```http
GET /api/v1/intelligence/mp/proposals/
```

Required role:

```text
MP or ADMIN
```

---

### Get Proposal Details

```http
GET /api/v1/intelligence/mp/proposals/<proposal_id>/
```

Required role:

```text
MP or ADMIN
```

---

### Approve Proposal

```http
POST /api/v1/intelligence/mp/proposals/<proposal_id>/approve/
```

Required role:

```text
MP or ADMIN
```

---

### Approve Proposal With Changes

```http
POST /api/v1/intelligence/mp/proposals/<proposal_id>/approve-with-changes/
```

Required role:

```text
MP or ADMIN
```

---

## Public APIs

### List Approved Public Projects

```http
GET /api/v1/intelligence/public/projects/
```

Authentication is not required.

---

### Get Public Project Details

```http
GET /api/v1/intelligence/public/projects/<proposal_id>/
```

Authentication is not required.

---

# Running the Complete System

JanMitra requires three running processes during local development.

## Terminal 1 — Django API

```bash
cd janmitra
source .venv/bin/activate
cd backend

python manage.py runserver
```

## Terminal 2 — AI Worker

```bash
cd janmitra
source .venv/bin/activate
cd backend

python manage.py run_ai_worker
```

## Terminal 3 — Frontend

Serve the frontend using VS Code Live Server or another static HTTP server.

The system workflow is then fully automatic:

```text
Citizen submits request
        ↓
Problem becomes READY_FOR_AI
        ↓
AI worker detects request
        ↓
Gemini consolidates complaints
        ↓
Gemini prioritizes issues
        ↓
Gemini generates proposal
        ↓
Proposal appears on MP dashboard
        ↓
MP approves or edits proposal
        ↓
Approved project appears publicly
```

---

# Troubleshooting

## `DATABASE_URL is not configured`

The backend requires `DATABASE_URL`.

Verify that:

```text
backend/.env
```

exists.

Check:

```env
DATABASE_URL=...
```

Run Django commands from the `backend` directory.

---

## `GEMINI_API_KEY is not configured`

Add the Gemini API key to:

```text
backend/.env
```

Example:

```env
GEMINI_API_KEY=your-key
```

Restart the AI worker after changing `.env`.

---

## Firebase `auth/invalid-credential`

Verify that the user exists in:

```text
Firebase Console
    ↓
Authentication
    ↓
Users
```

Changing a Django user's role does not create a Firebase Authentication account.

The email and password must belong to an existing Firebase user.

---

## Firebase Authentication Works but API Returns 401

Verify that the frontend sends:

```http
Authorization: Bearer <firebase-id-token>
```

Verify the Firebase Admin service account path:

```env
GOOGLE_APPLICATION_CREDENTIALS=...
```

Ensure the service account belongs to the same Firebase project used by the frontend.

---

## Django Returns `DisallowedHost`

Add the hostname to:

```python
ALLOWED_HOSTS
```

inside:

```text
backend/janmat/settings.py
```

Restart Django.

---

## Browser Reports a CORS Error

Add the exact frontend origin to:

```python
CORS_ALLOWED_ORIGINS
```

Example:

```python
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
]
```

Restart Django.

---

## AI Worker Command Is Not Found

Verify the structure:

```text
intelligence/
└── management/
    ├── __init__.py
    └── commands/
        ├── __init__.py
        └── run_ai_worker.py
```

Both `__init__.py` files must exist.

Verify:

```bash
python manage.py help
```

The command should appear under:

```text
[intelligence]
```

---

## AI Worker Finds No Problems

Inspect problem statuses:

```bash
python manage.py shell
```

Then:

```python
from problems.models import Problem

list(
    Problem.objects.values(
        "id",
        "title",
        "status",
    )
)
```

The AI worker processes problems with:

```text
READY_FOR_AI
```

---

## Proposal Does Not Appear on MP Dashboard

Verify that the AI worker created a proposal.

Open the Django shell:

```python
from intelligence.models import DevelopmentProposal

list(
    DevelopmentProposal.objects.values(
        "id",
        "status",
    )
)
```

A proposal waiting for MP review should have:

```text
PENDING_MP_REVIEW
```

Also verify that the logged-in Django user has:

```text
role = MP
```

---

## Approved Project Does Not Appear Publicly

Verify the proposal status.

Public projects require an approved proposal state.

Expected:

```text
APPROVED
```

or:

```text
APPROVED_WITH_CHANGES
```

Refresh the public portal after approval.

---

# Security Notes

Never commit:

```text
backend/.env
backend/firebase/
Firebase Admin service account JSON
Gemini API keys
Cloudinary API secrets
PostgreSQL credentials
Django SECRET_KEY
```

The Firebase web configuration is used by browser-side Firebase initialization.

Server-side authorization is enforced by Django.

The Django backend verifies Firebase identity tokens and applies JanMitra role permissions.

The browser must never receive:

```text
GEMINI_API_KEY
CLOUDINARY_API_SECRET
DATABASE_URL
SECRET_KEY
Firebase Admin private key
```

---

# Current Limitations

JanMitra is a hackathon prototype.

The current AI worker processes queued complaints in batches.

Complaints arriving in the same batch can be consolidated together.

A complaint arriving in a later AI batch is not yet semantically matched against previously created issues.

For example:

```text
Batch 1:
3 Court Road water complaints
        ↓
Issue A

Batch 2:
1 new Court Road water complaint
        ↓
May create Issue B
```

A future intelligence stage should compare new complaints against active existing issues before creating a new issue.

The current prototype also does not yet include:

- Proposal rejection
- Complete management dashboard
- Constituency-based MP assignment
- Project execution tracking
- Project completion verification
- Citizen notifications
- Public progress updates

---

# Future Scope

Planned extensions include:

- Cross-batch existing issue matching
- Complaint spam and abuse detection
- Management verification workflow
- Proposal rejection and revision
- Constituency-aware routing
- MP-specific issue queues
- Geographic issue clustering
- Interactive development maps
- Project implementation tracking
- Contractor and department assignment
- Development milestone tracking
- Budget utilization tracking
- Citizen status notifications
- Public project progress timelines
- Government dataset integration
- Historical development analytics
- AI-based development trend detection

---

# Hackathon

JanMitra was developed for the GDG WOW Visakhapatnam 2026 Hackathon.

The project demonstrates how generative AI can transform fragmented citizen complaints into consolidated development intelligence and connect citizen needs with structured public decision-making.

The core concept is:

```text
Many Citizen Voices
        ↓
One Development Intelligence Layer
        ↓
Prioritized Public Decisions
        ↓
Transparent Development
```