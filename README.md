# Yelp Prototype

A full-stack Yelp-like application with a **FastAPI** backend, **React + Vite** frontend, **MySQL** database, and an **AI-powered restaurant assistant** built with LangChain and Tavily.

---

## Project Structure

```
Yelp-Prototype/
├── backend/          # FastAPI Python backend
│   ├── main.py
│   ├── database.py
│   ├── requirements.txt
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   └── services/
└── frontend/         # React + Vite frontend
    ├── src/
    ├── package.json
    └── vite.config.js
```

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **MySQL** (running locally or via a cloud provider)

---

## Backend Setup

### 1. Create and activate a virtual environment

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

Create a file named `.env` inside the `backend/` directory with the following variables:

```env
# MySQL connection string
DATABASE_URL=mysql+pymysql://<user>:<password>@localhost:3306/<database_name>

# JWT secret key (any long random string)
SECRET_KEY=your_secret_key_here

# Google Gemini API key (used by LangChain with Gemini 2.0 Flash)
GOOGLE_API_KEY=your_google_gemini_api_key

# Tavily API key (used by the AI assistant for web search)
TAVILY_API_KEY=your_tavily_api_key
```

> **Tip:** Create the MySQL database first:
> ```sql
> CREATE DATABASE yelp_prototype;
> ```
> SQLAlchemy will create all tables automatically on first run.

### 4. Create the uploads directory

```bash
mkdir -p backend/uploads
```

### 5. Run the backend server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**.  
Interactive API docs (Swagger UI): **http://localhost:8000/docs**

---

## Frontend Setup

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Start the development server

```bash
npm run dev
```

The frontend will be available at **http://localhost:5173**.

---

## Features

- **User & Owner authentication** — JWT-based signup/login for both customers and restaurant owners
- **Restaurant listings** — Browse, search, and filter restaurants
- **Reviews** — Submit and view restaurant reviews
- **Favourites** — Save favourite restaurants
- **AI Assistant** — LangChain + LangGraph powered chatbot using **Gemini 2.0 Flash** that recommends restaurants and searches the web via Tavily

---

## API Overview

| Prefix | Description |
|---|---|
| `/auth/user` | Customer signup & login |
| `/auth/owner` | Owner signup & login |
| `/users` | User profile management |
| `/owners` | Owner profile management |
| `/restaurants` | Restaurant CRUD |
| `/reviews` | Review CRUD |
| `/ai-assistant` | AI restaurant recommendation chat |

---

## Running Both Servers Concurrently

Open two terminal tabs and run:

**Terminal 1 — Backend:**
```bash
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend && npm run dev
```

---

## Lab 2 JMeter Plans

JMeter assets for Lab 2 are included:

- `jmeter/week3-login-smoke.jmx` — initial 10-user smoke check for login
- `jmeter/week4-load-suite.jmx` — Week 4 load suite for 100-500 users

Guides:

- `docs/jmeter-week3.md`
- `docs/jmeter-week4.md`

Typical Week 4 run example:

```bash
jmeter -n -t jmeter/week4-load-suite.jmx -JTHREADS=300 -JRAMP_UP=60 -JLOOPS=2 -JBASE_HOST=localhost -JBASE_PORT=8001 -l jmeter/results/week4/load-300.csv
```
