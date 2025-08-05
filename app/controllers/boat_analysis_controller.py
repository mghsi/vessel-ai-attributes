import os
import time
from flask import request, jsonify, current_app
from app.models.boat_analysis import BoatAnalysis
from app.services.boat_analysis_service import ImageProcessingService, BoatAnalysisService


class BoatAnalysisController:
    """Controller to handle boat analysis requests"""
    
    @staticmethod
    def analyze_boat():
        """Handle POST request to analyze a boat image"""
        try:
            # Validate request
            validation_error = BoatAnalysisController._validate_request()
            if validation_error:
                return validation_error
            
            # Extract request data
            image_file = request.files['image']
            boat_brand = request.form.get('brand', '').strip()
            boat_model = request.form.get('model', '').strip()
            
            # Validate image
            if not ImageProcessingService.validate_image(
                image_file, 
                current_app.config['ALLOWED_EXTENSIONS']
            ):
                return jsonify({
                    'ERROR': 'Invalid image file. Allowed formats: png, jpg, jpeg, gif, bmp, webp',
                    'CODE': 'IMG002'
                }), 400
            
            # Save image
            try:
                filename = ImageProcessingService.save_image(
                    image_file, 
                    current_app.config['UPLOAD_FOLDER']
                )
            except Exception as e:
                return jsonify({
                    'ERROR': f'Failed to save image: {str(e)}',
                    'CODE': 'IMG003'
                }), 500
            
            # Process image
            start_time = time.time()
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            try:
                image_base64 = ImageProcessingService.encode_image_to_base64(filepath)
            except Exception as e:
                return jsonify({
                    'ERROR': f'Failed to process image: {str(e)}',
                    'CODE': 'IMG004'
                }), 500
            
            # Analyze boat
            analysis_service = BoatAnalysisService(
                github_pat=current_app.config['GITHUB_PAT'],
                api_url=current_app.config['GITHUB_API_URL'],
                model=current_app.config['DEFAULT_MODEL']
            )
            
            analysis_result = analysis_service.analyze_boat(
                image_base64, 
                boat_brand, 
                boat_model
            )
            
            processing_time = time.time() - start_time
            
            # Create analysis object for logging (optional - just for debugging)
            boat_analysis = BoatAnalysis.create_from_analysis(
                filename, 
                boat_brand, 
                boat_model, 
                analysis_result
            )
            boat_analysis.processing_time = processing_time
            
            # Log to console for debugging
            current_app.logger.info(f"Analysis completed in {processing_time:.2f}s for {filename}")
            current_app.logger.info(f"Result: {analysis_result}")
            
            # Return result
            status_code = 200 if 'ERROR' not in analysis_result else 400
            return jsonify(analysis_result), status_code
            
        except Exception as e:
            current_app.logger.error(f"Unexpected error in analyze_boat: {str(e)}")
            return jsonify({
                'ERROR': 'Internal server error',
                'CODE': 'SYS002'
            }), 500
    
    @staticmethod
    def _validate_request():
        """Validate the incoming request"""
        if 'image' not in request.files:
            return jsonify({
                'ERROR': 'No image file provided',
                'CODE': 'REQ001'
            }), 400
        
        if not request.files['image'].filename:
            return jsonify({
                'ERROR': 'No image file selected',
                'CODE': 'REQ002'
            }), 400
        
        if not current_app.config.get('GITHUB_PAT'):
            return jsonify({
                'ERROR': 'AI service not configured',
                'CODE': 'CFG001'
            }), 500
        
        return None
