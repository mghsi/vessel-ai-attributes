from flask import Blueprint, jsonify
from app.controllers.boat_analysis_controller import BoatAnalysisController
from app.controllers.agentic_workflow_controller import AgenticWorkflowController

# Create blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {"status": "healthy", "service": "boat-analyzer", "version": "1.0.0"}
    )


@api_bp.route("/analyze", methods=["POST"])
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
    return (
        jsonify({"ERROR": "File too large. Maximum size is 16MB.", "CODE": "SIZE001"}),
        413,
    )


@api_bp.errorhandler(400)
def bad_request(e):
    """Handle bad request errors"""
    return jsonify({"ERROR": "Bad request", "CODE": "REQ003"}), 400


@api_bp.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({"ERROR": "Internal server error", "CODE": "SYS004"}), 500


# Agentic Workflow Routes
@api_bp.route("/workflow/start", methods=["POST"])
def start_agentic_workflow():
    """
    Start a new agentic workflow session

    Expected JSON data:
    For image analysis:
    {
        "image_data": "base64_encoded_image",
        "brand": "optional_brand",
        "model": "optional_model"
    }

    For manual input:
    {
        "manual_data": {
            "builder_make": "required",
            "class_model": "required",
            "name": "optional",
            "mmsi": "optional",
            "length": optional_number,
            "beam": optional_number,
            "boat_type": "optional"
        }
    }
    """
    return AgenticWorkflowController.start_workflow()


@api_bp.route("/workflow/step", methods=["POST"])
def execute_workflow_step():
    """
    Execute the next step in an active workflow

    Expected JSON data:
    {
        "session_id": "workflow_session_id"
    }
    """
    return AgenticWorkflowController.execute_workflow_step()


@api_bp.route("/workflow/status", methods=["GET"])
def get_workflow_status():
    """
    Get the current status of a workflow session

    Query parameters:
    - session_id: The workflow session ID
    """
    return AgenticWorkflowController.get_workflow_status()


@api_bp.route("/workflow/execute", methods=["POST"])
def execute_full_workflow():
    """
    Execute the complete workflow from start to finish

    Expected JSON data: Same as /workflow/start

    Returns the complete results of all workflow steps
    """
    return AgenticWorkflowController.execute_full_workflow()


@api_bp.route("/workflow/performance-curves/download", methods=["GET"])
def download_performance_curves():
    """
    Download performance curves as CSV

    Query parameters:
    - session_id: The workflow session ID
    - format: CSV format type ('holtrop-mennen' or 'simple')
    """
    return AgenticWorkflowController.download_performance_csv()
