# Boat Analyzer API - Proof of Concept

An AI-powered Flask application that analyzes boat images to determine characteristics like type, dimensions, and usage details using GitHub Models API.

## Features

- **Image Analysis**: Upload boat images for AI-powered analysis
- **Boat Classification**: Categorizes boats into types (Flat Bottom, Multi-hull, Pontoon, RHIB, Semi-Displacement, V-Bottom)
- **Dimension Estimation**: Provides length, width, and beam measurements in feet
- **Usage Detection**: Determines commercial vs recreational use and auxiliary features
- **RESTful API**: Clean REST endpoints for integration
- **Error Handling**: Comprehensive error handling with structured responses
- **No Database**: Simplified proof-of-concept without persistence

## Architecture

The application follows the **MVC (Model-View-Controller)** pattern with clean code principles:

```
bluegrid-ai/
├── app/
│   ├── controllers/           # Business logic controllers
│   ├── models/               # Data models (no database)
│   ├── services/             # Service layer for external APIs
│   ├── views/                # API routes and blueprints
│   └── app_factory.py        # Flask application factory
├── config/
│   └── config.py             # Configuration management
├── uploads/                  # Image upload directory
├── main.py                   # Application entry point
└── pyproject.toml            # Project dependencies
```

## Quick Start

### Prerequisites

- Python 3.10+
- GitHub Personal Access Token with Models API access

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd bluegrid-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GITHUB_PAT
   ```

4. **Run the application:**
   ```bash
   python main.py
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
curl http://localhost:5000/api/v1/health

# Analyze a boat image
curl -X POST http://localhost:5000/api/v1/analyze \
  -F "image=@boat_image.jpg" \
  -F "brand=SeaCraft" \
  -F "model=X123"
```

### Using Python requests:
```python
import requests

# Analyze boat image
with open('boat_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/v1/analyze',
        files={'image': f},
        data={'brand': 'SeaCraft', 'model': 'X123'}
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
# Using CATALINA 2585 QL PONTOON.jpg
curl -X POST http://localhost:5000/api/v1/analyze \
  -F "image=@CATALINA 2585 QL PONTOON.jpg" \
  -F "brand=Catalina" \
  -F "model=2585 QL"

# Using PHOTON P300.jpg
curl -X POST http://localhost:5000/api/v1/analyze \
  -F "image=@PHOTON P300.jpg" \
  -F "brand=Photon" \
  -F "model=P300"
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
