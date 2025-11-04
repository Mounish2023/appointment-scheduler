# Aspen Dental AI Assistant - Backend

FastAPI-based backend for the AI-powered dental appointment scheduling assistant.

## Features

- **FastAPI** - Modern, fast web framework for APIs
- **SQLAlchemy** - Async ORM for PostgreSQL
- **JWT Authentication** - Secure token-based authentication
- **WebSocket Support** - Real-time communication
- **Agent Service** - AI-powered conversational assistant
- **PostgreSQL** - Robust database for data persistence

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application configuration
│   ├── database.py          # Database setup and session management
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── session.py
│   │   ├── message.py
│   │   ├── appointment.py
│   │   └── specialist_availability.py
│   ├── routes/              # API routes
│   │   ├── auth_routes.py
│   │   ├── chat_routes.py
│   │   └── websocket_routes.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── appointment_service.py
│   │   ├── websocket_service.py
│   │   └── agent_service.py
│   └── utils/               # Utilities
│       ├── security.py
│       └── logger.py
├── alembic.ini             # Database migration configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- pip or poetry

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scriptsctivate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL database**
   ```sql
   CREATE DATABASE aspen_dental;
   CREATE USER aspen_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE aspen_dental TO aspen_user;
   ```

5. **Configure environment variables**
   Create a `.env` file in the backend directory:
   ```env
   DATABASE_URL=postgresql+asyncpg://aspen_user:your_password@localhost/aspen_dental
   SECRET_KEY=your-super-secret-key-change-in-production
   DEBUG=True
   ```

6. **Initialize database**
   ```bash
   # Initialize Alembic
   alembic init alembic

   # Create initial migration
   alembic revision --autogenerate -m ""Initial migration""

   # Apply migration
   alembic upgrade head
   ```

### Running the Application

1. **Development server**
   ```bash
   python -m app.main
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Chat Sessions  
- `POST /chat/session/start` - Start new chat session
- `POST /chat/session/{session_id}/message` - Send message
- `GET /chat/session/{session_id}` - Get session with messages
- `GET /chat/sessions` - Get user's sessions

### WebSocket
- `WS /ws/{session_id}?token={jwt_token}` - Real-time communication

## WebSocket Message Format

### Client to Server
```json
{
  ""type"": ""user_message"",
  ""content"": ""I need to book an appointment""
}

{
  ""type"": ""approval_response"", 
  ""action_id"": ""book_123456"",
  ""approved"": true
}
```

### Server to Client
```json
{
  ""type"": ""agent_message"",
  ""content"": ""I can help you book an appointment..."",
  ""timestamp"": ""2025-10-12T21:00:00Z""
}

{
  ""type"": ""request_approval"",
  ""action_type"": ""book_appointment"",
  ""details"": {
    ""action_id"": ""book_123456"",
    ""date"": ""2025-10-20"",
    ""time"": ""14:00"",
    ""specialist"": ""Dr. Sarah Johnson""
  }
}
```

## Database Schema

### Users
- id (UUID, PK)
- email (String, unique)
- password_hash (String)
- full_name (String)
- phone (String, optional)
- insurance_provider (String, optional)
- created_at, updated_at (DateTime)

### Sessions
- id (UUID, PK)
- user_id (UUID, FK)
- status (Enum: active, closed)
- started_at, ended_at (DateTime)

### Messages
- id (UUID, PK)
- session_id (UUID, FK)
- sender (Enum: user, agent)
- content (Text)
- timestamp (DateTime)

### Appointments
- id (UUID, PK)
- user_id (UUID, FK)
- specialist_id (UUID, FK)
- appointment_date (DateTime)
- appointment_type (String)
- status (Enum: scheduled, modified, canceled)
- notes (Text, optional)

### Specialist Availability
- id (UUID, PK)
- specialist_name (String)
- specialty (String)
- available_date (Date)
- start_time, end_time (Time)
- is_booked (Boolean)

## Development

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings to functions and classes

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Logging
Logs are stored in the `logs/` directory:
- `app.log` - Application logs
- `error.log` - Error logs only

## Deployment

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD [""uvicorn"", ""app.main:app"", ""--host"", ""0.0.0.0"", ""--port"", ""8000""]
```

### Environment Variables (Production)
```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/aspen_dental
SECRET_KEY=production-secret-key
DEBUG=False
ALLOWED_ORIGINS=[""https://yourdomain.com""]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is proprietary software for Aspen Dental.
