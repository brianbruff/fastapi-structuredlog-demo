# FastAPI Structured Logging Demo

A complete example project showcasing **structured logging** in FastAPI using `structlog`, with user context capture and JSON output format.

## 🚀 Features

- **Structured Logging**: Uses `structlog` for JSON-formatted logs
- **User Context**: Automatically captures and logs user information from requests
- **Multiple Auth Methods**: Supports Basic auth, Bearer tokens, and custom headers
- **Request Tracing**: Each request gets contextual information (user, route, method, etc.)
- **Error Handling**: Comprehensive error logging with structured context
- **Poetry Management**: Modern Python dependency management
- **Full Test Coverage**: Unit tests for all components

## 📁 Project Structure

```
fastapi-structuredlog-demo/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application with endpoints
│   ├── middleware.py     # User context middleware
│   ├── logger.py         # Structured logging configuration  
│   └── dependencies.py   # FastAPI dependencies for logging
├── tests/
│   ├── __init__.py
│   └── test_logging.py   # Comprehensive tests
├── pyproject.toml        # Poetry configuration
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fastapi-structuredlog-demo
   ```

2. **Install dependencies**:
   ```bash
   poetry install --with dev
   ```

3. **Activate the virtual environment**:
   ```bash
   poetry shell
   ```

### Running the Application

**Start the FastAPI server**:
```bash
poetry run python -m app.main
```

Or using uvicorn directly:
```bash
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`

**API Documentation**: Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## 🔍 How Logging Works

### Structured Logging Configuration

The application uses `structlog` configured to output JSON logs with:
- **Timestamp**: ISO format timestamp
- **Log Level**: INFO, ERROR, DEBUG, etc.
- **Logger Name**: Module name where log originated
- **User Context**: Current user information
- **Request Context**: Route, method, request ID
- **Custom Fields**: Any additional contextual data

### User Context Injection

The `UserContextMiddleware` extracts user information from requests using:

1. **Custom Header** (simplest for demo):
   ```bash
   curl -H "X-User-Name: alice" http://127.0.0.1:8000/user-info
   ```

2. **Basic Authentication**:
   ```bash
   curl --user "johndoe:password" http://127.0.0.1:8000/protected
   ```

3. **Bearer Token** (with mock user extraction):
   ```bash
   curl -H "Authorization: Bearer user_alice_token123" http://127.0.0.1:8000/protected
   ```

### Log Context Binding

Every request automatically gets:
- `user`: Username from authentication
- `route`: API endpoint path
- `method`: HTTP method (GET, POST, etc.)
- `request_id`: Unique request identifier
- `user_agent`: Client user agent

## 📋 API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | Welcome message | No |
| `/hello/{name}` | GET | Personalized greeting | No |
| `/protected` | GET | Protected resource | Recommended |
| `/user-info` | GET | Current user information | No |
| `/simulate-error` | POST | Error simulation for testing | No |
| `/health` | GET | Health check | No |

## 🧪 Example Log Output

When you make a request with user context:

```bash
curl -H "X-User-Name: alice" http://127.0.0.1:8000/hello/world
```

The structured log output looks like:

```json
{
  "event": "Request started",
  "level": "info",
  "logger": "app.middleware",
  "method": "GET",
  "query_params": {},
  "request_id": 140234567890,
  "route": "/hello/world",
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "user": "alice",
  "user_agent": "curl/7.68.0"
}
```

```json
{
  "event": "Hello endpoint accessed",
  "level": "info", 
  "logger": "app.main",
  "method": "GET",
  "request_id": 140234567890,
  "route": "/hello/world",
  "target_name": "world",
  "timestamp": "2024-01-15T10:30:45.125789Z",
  "user": "alice",
  "user_agent": "curl/7.68.0"
}
```

```json
{
  "event": "Request completed",
  "level": "info",
  "logger": "app.middleware", 
  "method": "GET",
  "request_id": 140234567890,
  "route": "/hello/world",
  "status_code": 200,
  "timestamp": "2024-01-15T10:30:45.127234Z",
  "user": "alice",
  "user_agent": "curl/7.68.0"
}
```

## 🧪 Running Tests

**Run all tests**:
```bash
poetry run pytest
```

**Run with coverage**:
```bash
poetry run pytest --cov=app --cov-report=html
```

**Run specific test file**:
```bash
poetry run pytest tests/test_logging.py -v
```

### Test Coverage

The tests cover:
- ✅ Middleware user extraction from different auth methods
- ✅ API endpoint responses and behavior
- ✅ Structured logging configuration
- ✅ Error handling and logging
- ✅ Request context binding
- ✅ JSON log output format

## 🔧 Development

### Project Configuration

The project uses modern Poetry configuration in `pyproject.toml`:

**Main Dependencies**:
- `fastapi`: Modern web framework
- `uvicorn[standard]`: ASGI server
- `structlog`: Structured logging library
- `python-multipart`: Form data support

**Development Dependencies**:
- `pytest`: Testing framework
- `pytest-asyncio`: Async testing support
- `httpx`: HTTP client for testing

### Extending the Example

To extend this example for production use:

1. **Real Authentication**: Replace mock token parsing with actual JWT validation
2. **Database Integration**: Add user lookup from database
3. **Log Aggregation**: Send logs to ELK stack, Splunk, or CloudWatch
4. **Request Correlation**: Use proper correlation IDs across services
5. **Performance Monitoring**: Add metrics and tracing integration

## 🤝 Usage Examples

### Testing Different Auth Methods

1. **Anonymous User**:
   ```bash
   curl http://127.0.0.1:8000/user-info
   ```

2. **Custom Header**:
   ```bash
   curl -H "X-User-Name: alice" http://127.0.0.1:8000/user-info
   ```

3. **Basic Auth**:
   ```bash
   curl --user "johndoe:secret" http://127.0.0.1:8000/user-info
   ```

4. **Bearer Token**:
   ```bash
   curl -H "Authorization: Bearer user_bob_token456" http://127.0.0.1:8000/user-info
   ```

### Error Logging Example

```bash
curl -X POST http://127.0.0.1:8000/simulate-error
```

This will generate structured error logs showing the full exception context.

## 📝 License

This project is created for demonstration purposes. Feel free to use and modify as needed.

## 🙋‍♂️ Support

For questions or issues, please check the FastAPI and structlog documentation:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Structlog Documentation](https://www.structlog.org/)
