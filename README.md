# 🚤 Boat Analyzer AI - Backend API

AI-powered boat image analysis service with Flask backend using GitHub Models API.

## 🌟 Features

### Backend API (Flask)
- **AI-Powered Analysis**: Uses GitHub Models API for boat image analysis
- **Boat Classification**: Categorizes boats into types (Flat Bottom, Multi-hull, Pontoon, RHIB, Semi-Displacement, V-Bottom)
- **Dimension Estimation**: Provides length, width, and beam measurements in feet
- **Usage Detection**: Determines commercial vs recreational use and auxiliary features
- **RESTful API**: Clean REST endpoints for integration
- **CORS Enabled**: Configured for cross-origin requests
- **Error Handling**: Comprehensive error handling with structured responses

### Development
- **Docker Support**: Full containerized development environment
- **Hot Reload**: Backend supports live reloading in development
- **No Database**: Simplified proof-of-concept without persistence

## 🏗️ Architecture

Flask-based REST API for boat image analysis:

```
vessel-ai-attributes/
├── backend/                   # Flask API Server
│   ├── app/
│   │   ├── controllers/      # Business logic controllers
│   │   ├── models/          # Data models (no database)
│   │   ├── services/        # Service layer for external APIs
│   │   ├── views/           # API routes and blueprints
│   │   └── app_factory.py   # Flask application factory
│   ├── config/              # Configuration management
│   ├── data/                # Sample data files
│   ├── uploads/             # Image upload directory
│   ├── main.py              # Application entry point
│   └── pyproject.toml       # Python dependencies
├── docker-compose.yml        # Development environment
├── Dockerfile               # Backend container image
└── .env.docker              # Environment configuration
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- GitHub Personal Access Token with Models API access

### Development Setup

1. **Configure environment:**
   ```bash
   cp backend/example.env .env.docker
   # Edit .env.docker and add your GitHub PAT
   ```

2. **Start the development environment:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - **Backend API**: http://localhost:5001
   - **Health Check**: http://localhost:5001/api/v1/health

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GITHUB_PAT
   ```

4. **Run the application:**
   ```bash
   uv run python main.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /api/v1/health
```

### Analyze Boat Image
```
POST /api/v1/analyze
Content-Type: multipart/form-data

Parameters:
- image: Image file (required)
- brand: Boat brand (optional)
- model: Boat model (optional)
```

**Response Format:**
```json
{
  "Boat Type": "V-Bottom",
  "Length": "30",
  "Width": "10", 
  "Beam": "9",
  "Aux": "YES",
  "Commercial": "NO"
}
```

**Error Response:**
```json
{
  "ERROR": "Description of error",
  "CODE": "ERROR_CODE"
}
```

## Usage Examples

### Using curl:
```bash
# Health check
curl http://localhost:5001/api/v1/health

# Analyze a boat image with brand and model
curl -X POST http://localhost:5001/api/v1/analyze \
  -F "image=@boat_image.jpg" \
  -F "brand=SeaCraft" \
  -F "model=X123"

# Analyze a boat image with just the image (brand and model optional)
curl -X POST http://localhost:5001/api/v1/analyze \
  -F "image=@boat_image.jpg"
```

### Using Python requests:
```python
import requests

# Analyze boat image with brand and model
with open('boat_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5001/api/v1/analyze',
        files={'image': f},
        data={'brand': 'SeaCraft', 'model': 'X123'}
    )
    result = response.json()
    print(result)

# Analyze boat image with just the image (brand and model optional)
with open('boat_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5001/api/v1/analyze',
        files={'image': f}
    )
    result = response.json()
    print(result)
```

## Configuration

Environment variables in `.env`:

- `GITHUB_PAT`: GitHub Personal Access Token (required)
- `FLASK_ENV`: Environment (development/production)
- `FLASK_DEBUG`: Enable debug mode (True/False)
- `SECRET_KEY`: Flask secret key

## Error Codes

| Code | Description |
|------|-------------|
| IMG001 | Image is unclear |
| IMG002 | Invalid image format |
| IMG003 | Failed to save image |
| IMG004 | Failed to process image |
| REQ001 | No image file provided |
| REQ002 | No image file selected |
| CFG001 | AI service not configured |
| API### | AI model API errors |
| NET001 | Network error |
| SYS### | System errors |

## Test the API

You can test the API using one of the boat images in your workspace:

```bash
# Test with brand and model (if you have these images)
curl -X POST http://localhost:5001/api/v1/analyze \
  -F "image=@CATALINA_2585_QL_PONTOON.jpg" \
  -F "brand=Catalina" \
  -F "model=2585 QL"

# Test with just an image (brand and model are optional)
curl -X POST http://localhost:5001/api/v1/analyze \
  -F "image=@boat_image.jpg"

# Test with any boat image you have
curl -X POST http://localhost:5001/api/v1/analyze \
  -F "image=@your_boat_image.jpg"
```

## Development

### Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Code formatting:
```bash
black .
```

### Type checking:
```bash
mypy .
```

## Project Structure Details

- **Models**: Simple data classes for boat analysis results
- **Controllers**: Business logic and request handling  
- **Services**: External API integration and image processing
- **Views**: Route definitions and request/response handling
- **Config**: Environment-specific configuration management

## Notes

This is a proof-of-concept version without database persistence. Analysis results are logged to console for debugging but not stored permanently. For production use, consider adding database storage for analysis history and results.

## License

This project is licensed under the MIT License.
