# FastAPI Demo Application

FastAPI demo application with clean architecture for user management API.

## Quick Start

### 1. Start FastAPI Server
```bash
# Start FastAPI development server
uv run uvicorn main:app --reload
```

### 2. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root Page**: http://localhost:8000/

## API Specification

### Base URL
- **Development**: `http://localhost:8000`
- **API Prefix**: `/api/v1`

### Authentication
All API endpoints (except health) require API Key authentication.

**Header:**
```
X-API-Key: demo-api-key-123
```

### Endpoints

#### 1. Health Check
```http
GET /api/v1/health
```
**Auth**: Not required  
**Description**: Check application status

#### 2. Get Users
```http
GET /api/v1/users
```
**Auth**: Required  
**Query Parameters:**
- `name` (string): Search by name (partial match)
- `min_age` (integer): Filter by minimum age
- `max_age` (integer): Filter by maximum age
- `limit` (integer, 1-100): Number of records (default: 10)
- `offset` (integer): Offset for pagination (default: 0)

**Example:**
```bash
curl -H "X-API-Key: demo-api-key-123" \
  "http://localhost:8000/api/v1/users?limit=5&name=tanaka"
```

#### 3. Get User by ID
```http
GET /api/v1/users/{user_id}
```
**Auth**: Required  
**Path Parameters:**
- `user_id` (integer): User ID

#### 4. Create User
```http
POST /api/v1/users
```
**Auth**: Required  
**Request Body:**
```json
{
  "name": "Tanaka Taro",
  "email": "tanaka@example.com", 
  "age": 30
}
```

#### 5. Update User
```http
PUT /api/v1/users/{user_id}
```
**Auth**: Required  
**Request Body:**
```json
{
  "name": "Tanaka Jiro",
  "email": "tanaka2@example.com",
  "age": 31
}
```

#### 6. Delete User
```http
DELETE /api/v1/users/{user_id}
```
**Auth**: Required

## Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov

# Run specific test categories
uv run pytest -m api    # API tests only
uv run pytest -m unit   # Unit tests only
```

## Project Structure

```
.
├── main.py                    # Application entry point
├── app/                       # Application core
│   ├── api/                   # API endpoints
│   ├── core/                  # Config, error handling, middleware
│   ├── deps/                  # Dependency injection
│   ├── domain/                # Domain entities
│   ├── infra/                 # Infrastructure layer
│   ├── ports/                 # Ports (interfaces)
│   └── usecase/               # Use case layer
├── schemas/                   # Pydantic schemas
│   ├── requests/              # Request models
│   └── responses/             # Response models
├── tests/                     # Test code
└── README.md                  # This file
```

## Architecture

This project adopts **Clean Architecture**:

- **API Layer**: FastAPI endpoints
- **Use Case Layer**: Business logic
- **Domain Layer**: Entities and business rules
- **Infrastructure Layer**: Data access implementation
- **Ports Layer**: Interface definitions

## Development Commands

```bash
# Install dependencies
uv sync

# Add new package
uv add <package>

# Start development server
uv run uvicorn main:app --reload

# Start production server
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# Enter virtual environment
uv shell
```

## Common Issues

### 1. 404 Not Found Error
**Problem**: 404 error at `http://localhost:8000/users`  
**Solution**: Correct endpoint is `http://localhost:8000/api/v1/users`

### 2. 401 Unauthorized Error
**Problem**: API Key authentication error  
**Solution**: Add `X-API-Key: demo-api-key-123` to request headers

### 3. 422 Validation Error
**Problem**: Request data validation error  
**Solution**: Check schema in API docs (/docs) and send correct data format

## Technologies Used

- **FastAPI**: High-performance web API framework
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **pytest**: Testing framework
- **uv**: Python package management

## Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [uv Documentation](https://docs.astral.sh/uv/)