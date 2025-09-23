# PETS - FastAPI Project Template

A modern FastAPI application template with clean architecture, built using Poetry for dependency management.

## 📖 Description

This is a FastAPI web application template that provides a solid foundation for building REST APIs. The project follows best practices for Python web development and includes:

- **FastAPI Framework**: High-performance, easy-to-use web framework for building APIs
- **Clean Architecture**: Well-organized project structure with separated concerns
- **Modern Python**: Uses Python 3.9+ with type hints and modern features
- **Test Endpoint**: Includes a `/test` endpoint for template demonstration and connectivity testing
- **Docker Support**: Complete containerization setup with Docker and Docker Compose
- **Poetry**: Modern dependency management and packaging tool

## 🏗️ Project Structure

```
pets/
├── pets/                    # Main application package
│   ├── db/                  # Database configurations and models
│   │   ├── dao/            # Data Access Objects
│   │   └── models/         # Database models
│   ├── services/           # External services integration
│   ├── settings.py         # Application configuration
│   ├── web/                # Web layer
│   │   ├── api/            # API routes and handlers
│   │   │   ├── docs/       # Documentation endpoints
│   │   │   ├── monitoring/ # Health check and monitoring
│   │   │   └── test/       # Test endpoint for demonstration
│   │   ├── application.py  # FastAPI app configuration
│   │   └── lifespan.py     # App lifecycle management
│   └── __main__.py         # Application entry point
├── tests/                  # Test suite
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── pyproject.toml         # Project dependencies and metadata
└── README.md              # This file
```

## 🛠️ Prerequisites

- **Python 3.9+**: Make sure you have Python 3.9 or higher installed
- **Poetry**: Install Poetry for dependency management

  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

- **Docker** (optional): For containerized deployment

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd pets
```

### 2. Install Dependencies

```bash
# Install all dependencies using Poetry
poetry install

# Activate the virtual environment
poetry shell
```

### 3. Environment Configuration

**Important**: Copy the example environment file and update it with your settings:

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file to configure your environment:

```bash
# Basic Application Settings
PETS_HOST=127.0.0.1
PETS_PORT=8000
PETS_ENVIRONMENT=dev

# DynamoDB Configuration
PETS_DYNAMODB_ENDPOINT_URL=http://localhost:8001  # For local development
PETS_AWS_REGION=eu-west-1

# AWS Secrets Manager (Configurable)
PETS_USE_SECRETS_MANAGER=True
```

**Security Note**:

- **Never commit AWS credentials to version control**
- **Flexible credential management**: Choose between Secrets Manager or environment variables
- **For local development**: Fake credentials are automatically used (no setup needed)
- **Production options**: Use either Secrets Manager or environment variables based on your deployment
- The `.env` file is already in `.gitignore` to prevent accidental commits

### 🏷️ Environment Variable Naming Convention

This application uses **Pydantic BaseSettings** with a specific naming convention for environment variables.

#### Naming Rules

| **Setting Field** | **Environment Variable** | **Description** |
|-------------------|--------------------------|-----------------|
| `host` | `PETS_HOST` | Application host address |
| `port` | `PETS_PORT` | Application port number |
| `environment` | `PETS_ENVIRONMENT` | Environment (dev/lambda) |
| `log_level` | `PETS_LOG_LEVEL` | Logging level |
| `dynamodb_endpoint_url` | `PETS_DYNAMODB_ENDPOINT_URL` | DynamoDB endpoint |
| `aws_region` | `PETS_AWS_REGION` | AWS region |
| `use_secrets_manager` | `PETS_USE_SECRETS_MANAGER` | Enable/disable Secrets Manager |
| `dynamodb_secret_name` | `PETS_DYNAMODB_SECRET_NAME` | Secret name in AWS |

#### Convention Pattern

```python
# Pattern: PETS_<FIELD_NAME_IN_UPPERCASE>
# Field in settings.py: snake_case
# Environment variable: PETS_SNAKE_CASE_IN_UPPERCASE

# Examples:
dynamodb_endpoint_url  →  PETS_DYNAMODB_ENDPOINT_URL
use_secrets_manager    →  PETS_USE_SECRETS_MANAGER
log_level             →  PETS_LOG_LEVEL
```

#### Configuration Priority (Highest to Lowest)

1. **Environment Variables** (e.g., `PETS_HOST=0.0.0.0`)
2. **`.env` file** (local development)
3. **Default values** (defined in `settings.py`)

#### Examples

```bash
# Local Development (.env file)
PETS_HOST=127.0.0.1
PETS_PORT=8000
PETS_ENVIRONMENT=dev
PETS_USE_SECRETS_MANAGER=false

# AWS Lambda (Environment Variables)
PETS_ENVIRONMENT=lambda
PETS_USE_SECRETS_MANAGER=true
PETS_DYNAMODB_SECRET_NAME=pets/dynamodb
PETS_AWS_REGION=us-east-1
```

#### How It Works

The application automatically:

- **Reads `.env` file** (if present) for local development
- **Reads environment variables** (always, with higher priority)
- **Applies defaults** for missing values
- **Validates types** (string, int, bool, enum)

This means the same codebase works seamlessly in:

- ✅ Local development (with `.env` file)
- ✅ Docker containers (with environment variables)
- ✅ AWS Lambda (with Lambda environment variables)
- ✅ Any cloud platform (with environment variables)

### 🔐 Credential Management Options

#### AWS Secrets Manager (Recommended for Production)

Set `PETS_USE_SECRETS_MANAGER=true` and create a secret:
ort PETS_AWS_SECRET_ACCESS_KEY="..."

### 🎯 Credential Resolution Flow

The application uses this logic:

**Local Development:**

- Always uses fake credentials (regardless of `PETS_USE_SECRETS_MANAGER` setting)

**AWS Lambda:**

- If `PETS_USE_SECRETS_MANAGER=True`: Secrets Manager → Error if not found
- If `PETS_USE_SECRETS_MANAGER=False`: Environment variables

## 🏃‍♂️ Running the Application

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI**: <http://localhost:8000/api/docs>
- **ReDoc**: <http://localhost:8000/api/redoc>
- **OpenAPI JSON**: <http://localhost:8000/api/openapi.json>

## 🔍 Available Endpoints

### Health Check

- **GET** `/api/health` - Application health status

### Test Endpoint

- **POST** `/api/test` - Test endpoint for demonstration

  ```json
  // Request body
  {
    "message": "Hello, World!"
  }
  
  // Response
  {
    "message": "Hello, World!"
  }
  ```

## 🧪 Running Tests

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/test_test.py

# Run tests in verbose mode
poetry run pytest -v
```

## 🐳 Docker Deployment

### Production Build

```bash
# Build the Docker image
docker build -t pets-app .

# Run the container
docker run -p 8000:8000 pets-app
```

### Development with Docker Compose

```bash
# Start with auto-reload for development
docker-compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build

# Rebuild when dependencies change
docker-compose build
```

## ⚡ AWS Lambda Deployment

This application supports serverless deployment to AWS Lambda using **Mangum** as a bridge/adapter.

**Important**: You continue building your FastAPI app normally. Mangum simply acts as a bridge when deployed to Lambda.

### How It Works

1. **Your FastAPI app stays the same** - no Lambda-specific code needed
2. **Mangum acts as a bridge** - converts Lambda events to ASGI format
3. **Deploy your normal FastAPI app** to Lambda seamlessly

### Lambda Bridge File

The project includes a simple bridge at `lambda_handler.py`:

```python
# This is the ONLY Lambda-specific file you need
from mangum import Mangum
from pets.web.application import get_app

app = get_app()  # Your normal FastAPI app
handler = Mangum(app, lifespan="off")  # Mangum bridge
```

### Deployment Options

#### Option 1: AWS SAM (Recommended)

Create a `template.yaml` file:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  PetsApi:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: lambda_handler.handler
      Runtime: python3.9
      Environment:
        Variables:
          PETS_ENVIRONMENT: lambda
      Events:
        ApiGateway:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

Deploy with:

```bash
# Build and deploy
sam build
sam deploy --guided
```

#### Option 2: Serverless Framework

Create a `serverless.yml` file:

```yaml
service: pets-api

provider:
  name: aws
  runtime: python3.9
  environment:
    PETS_ENVIRONMENT: lambda

functions:
  app:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

Deploy with:

```bash
serverless deploy
```

#### Option 3: Manual ZIP Deployment

```bash
# Install dependencies
poetry export -f requirements.txt --output requirements.txt
pip install -r requirements.txt -t ./package

# Package the application
cp -r pets ./package/
cd package && zip -r ../pets-lambda.zip . && cd ..

# Upload to Lambda via AWS CLI or Console
aws lambda update-function-code \
  --function-name pets-api \
  --zip-file fileb://pets-lambda.zip
```

### Lambda Environment Variables

Set these environment variables in your Lambda function:

```bash
PETS_ENVIRONMENT=lambda
PETS_LOG_LEVEL=INFO
# Add database and other configuration as needed
```

## ⚙️ Configuration

The application can be configured using environment variables. All variables should be prefixed with `PETS_`:

- `PETS_HOST`: Server host (default: 127.0.0.1)
- `PETS_PORT`: Server port (default: 8000)
- `PETS_ENVIRONMENT`: Environment mode (dev/prod)
- `PETS_LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

## 🤝 Development

This project uses:

- **FastAPI**: Web framework
- **Pydantic**: Data validation and serialization
- **Poetry**: Dependency management
- **Pytest**: Testing framework
- **Docker**: Containerization

### Adding New Endpoints

1. Create new modules in `pets/web/api/`
2. Follow the existing pattern (schema.py, views.py, **init**.py)
3. Register routes in `pets/web/api/router.py`
4. Add tests in the `tests/` directory
