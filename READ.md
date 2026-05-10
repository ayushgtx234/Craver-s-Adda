# Project Requirements & Setup

This document outlines the dependencies and setup instructions for the GraveFood System (Separated Architecture).

## 🛠️ Prerequisites
- **Python 3.10+**
- **Git** (for version control)

## 📦 Python Dependencies
The backend requires the following packages:

| Package | Purpose |
|---------|---------|
| `fastapi` | Modern, high-performance web framework for the API |
| `uvicorn` | ASGI server implementation to run the FastAPI app |
| `sqlalchemy` | SQL Toolkit and Object Relational Mapper (ORM) |
| `pydantic` | Data validation and settings management |

### Installation Command
Run the following command in your terminal:
```bash
pip install fastapi uvicorn sqlalchemy
```

## 🚀 Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd project
   ```

2. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn sqlalchemy
   ```

3. **Run the Application**:
   Use the root orchestrator script to start both Backend and Frontend:
   ```bash
   python run.py
   ```

## 🌐 Component Ports
- **Frontend**: `http://localhost:5000`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

## 📂 Project Structure
- `/backend`: FastAPI application and SQLite database.
- `/frontend`: HTML, CSS, and Vanilla JS UI.
- `run.py`: Root script to run both servers.
