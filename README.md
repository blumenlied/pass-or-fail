# Intelligent Student Performance Predictor

The Intelligent Student Performance Predictor is a web-based application designed to empower faculty with actionable, AI-driven insights. By analyzing student performance data, our system predicts the likelihood of success in upcoming certification exams, enabling targeted interventions and fostering a more supportive learning environment.

![image](https://github.com/user-attachments/assets/079ecfe1-1968-4ca2-a432-7abfd8288e91)

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Backend Setup & Running](#backend-setup--running)
- [Frontend Setup & Running](#frontend-setup--running)
- [Usage](#usage)
- [License](#license)

## Features

-   **AI-Powered Predictions:** Predicts student success in certification exams using an ensemble machine learning model.
-   **Insightful Dashboard:** Visualizes overall student performance and key metrics.
-   **Comprehensive Student Management:** Add, view, edit, and delete student records.
-   **Individual & Class Predictions:** Generate predictions for single students or entire classes.
-   **Secure Faculty Login:** Role-based access for faculty members.
-   **Help & Documentation:** In-app user guide and FAQs.

## Technology Stack

-   **Backend:**
    -   Python 3.8+
    -   FastAPI (ASGI Framework)
    -   SQLAlchemy (ORM)
    -   Uvicorn (ASGI Server)
    -   Pydantic (Data Validation)
    -   python-jose & passlib (Authentication & Hashing)
    -   Database: SQLite
-   **Frontend:**
    -   SvelteKit (Svelte Framework)
    -   Tailwind CSS (Utility-first CSS)
    -   Flowbite Svelte (UI Components)
    -   TypeScript
-   **Machine Learning:**
    -   Pandas, NumPy, Scikit-learn
    -   Joblib (for model persistence)

## Prerequisites

-   **Python:** Version 3.8 or higher.
-   **Node.js:** Version 18.x or higher (for SvelteKit).
-   **npm, yarn, or pnpm:** Node.js package manager.
-   **Git:** Version control system.

## Project Structure (Simplified)

```
.
├── backend/
│   ├── app/                  # Main FastAPI application code
│   │   ├── auth/
│   │   ├── crud/
│   │   ├── ml/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config.py         # (Optional config if not just .env)
│   │   └── main.py           # FastAPI app instance
│   ├── venv/                 # Virtual environment (ignored by Git)
│   ├── .env                  # Local environment variables (ignored by Git)
│   ├── .env.example          # Example environment variables
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   ├── routes/
│   │   └── app.html
│   ├── static/
│   ├── node_modules/         # (ignored by Git)
│   ├── package.json
│   ├── svelte.config.js
│   └── tailwind.config.js
├── .gitignore
└── README.md
```

## Backend Setup & Running

This section guides you through setting up and running the Python FastAPI backend.

### 1. Navigate to Backend Directory
Ensure you are in the root of the cloned repository.
```bash
cd backend
```

### 2. Create and Activate Virtual Environment
Using `venv` (recommended):
```bash
python3 -m venv venv  # Use python3 if python maps to Python 2
source venv/bin/activate  # On macOS/Linux
# OR
# .\venv\Scripts\activate    # On Windows (Command Prompt or PowerShell)
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
-   **For SQLite (as in example `.env`):** The database file (`school_data.db`) will be created automatically in the `backend` directory when the application first runs and attempts a database operation, provided SQLAlchemy is set up to create tables (often true for simple models without a separate migration step).
-   **For PostgreSQL/MySQL:**
    1.  Ensure your database server is installed and running.
    2.  Create the database (e.g., `yourdatabase`) and user (`youruser`) as specified in your `DATABASE_URL`.
    3.  If you are using a database migration tool like Alembic, run the migrations to create the schema:
        ```bash
        # Example for Alembic - ensure alembic.ini is configured
        # alembic upgrade head
        ```
        *(If you are not using migrations and not using SQLite, you might need a script or manual process to create your database tables based on your SQLAlchemy models before the first run).*

### 5. Run the Backend Server
From the `backend` directory (with your virtual environment activated):
```bash
uvicorn app.main:app --reload
```
The backend API will typically be available at `http://localhost:8000`.
You can usually access the auto-generated API documentation (Swagger UI) at `http://localhost:8000/docs`.

## Frontend Setup & Running

This section guides you through setting up and running the SvelteKit frontend.

### 1. Navigate to Frontend Directory
From the project root:
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
# OR for other package managers:
# yarn install
# pnpm install
```

### 3. Configure Environment Variables (If Any)
Currently, the frontend is configured to make API calls directly to `http://localhost:8000`. If you need to change this (e.g., for different environments or if the backend port changes), you would typically:
- For SvelteKit, use public environment variables (e.g., `VITE_API_BASE_URL` in a `.env` file in the `frontend` directory) and access them in your code via `import.meta.env.VITE_API_BASE_URL`.
- Create a `frontend/.env.example` if you add such variables.
*(For this project's current setup, direct API calls to the backend's default port are assumed in development).*

### 4. Run the Frontend Development Server
From the `frontend` directory:
```bash
npm run dev
```
The frontend application will typically be available at `http://localhost:5173`.

### Note for Windows PowerShell Users
If the `npm run dev` command fails with an error like "running scripts is disabled on this system":
1.  Open PowerShell **as Administrator**.
2.  Execute the command: `Set-ExecutionPolicy RemoteSigned`
3.  When prompted, type `Y` (or `A`) and press Enter to confirm the change.

## Usage

1.  **Start Both Servers:** Ensure both the backend (Uvicorn) and frontend (SvelteKit dev server) are running.
2.  **Access the Application:** Open your web browser and navigate to the frontend URL (e.g., `http://localhost:5173`).
3.  **Login Page:** You will be directed to the landing page. Click the "Faculty Login" button to go to `http://localhost:5173/login`. Use faculty credentials to log in.
4.  **Dashboard:** After successful login, you will be redirected to the dashboard, which displays an overview of student performance.
5.  **Management Page (`/students`):** Navigate here to add, view, edit, or delete student records.
6.  **Prediction Page (`/prediction` - *if created*):** Access this page to generate pass/fail predictions for students or classes.
7.  **Help Page (`/help`):** Find the user guide, general FAQs, and developer setup information.
