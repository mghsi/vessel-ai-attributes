from flask import Blueprint, jsonify
from app.controllers.boat_analysis_controller import BoatAnalysisController

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'boat-analyzer',
        'version': '1.0.0'
    })

@api_bp.route('/analyze', methods=['POST'])
def analyze_boat():
    """
    Analyze a boat image
    
    Expected form data:
    - image: Image file (required)
    - brand: Boat brand (optional)
    - model: Boat model (optional)
    
    Returns:
    JSON object with boat characteristics or error information
    """
    return BoatAnalysisController.analyze_boat()

@api_bp.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'ERROR': 'File too large. Maximum size is 16MB.',
        'CODE': 'SIZE001'
    }), 413

@api_bp.errorhandler(400)
def bad_request(e):
    """Handle bad request errors"""
    return jsonify({
        'ERROR': 'Bad request',
        'CODE': 'REQ003'
    }), 400

@api_bp.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({
        'ERROR': 'Internal server error',
        'CODE': 'SYS004'
    }), 500
