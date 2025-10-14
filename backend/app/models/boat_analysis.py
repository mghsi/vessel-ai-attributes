from datetime import datetime
from typing import Dict, Any, Optional


class BoatAnalysis:
    """Simple data class to represent boat analysis results"""
    
    def __init__(self, image_filename: str, boat_brand: str = "", boat_model: str = ""):
        self.image_filename = image_filename
        self.boat_brand = boat_brand or ""
        self.boat_model = boat_model or ""
        
        # Analysis results
        self.boat_type: Optional[str] = None
        self.length: Optional[str] = None
        self.width: Optional[str] = None
        self.beam: Optional[str] = None
        self.aux: Optional[str] = None
        self.commercial: Optional[str] = None
        
        # Error handling
        self.error_message: Optional[str] = None
        self.error_code: Optional[str] = None
        
        # Metadata
        self.created_at = datetime.utcnow()
        self.processing_time: Optional[float] = None
    
    def __repr__(self):
        brand_model = f"{self.boat_brand} {self.boat_model}".strip()
        return f'<BoatAnalysis: {brand_model if brand_model else "Unknown vessel"}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for JSON serialization"""
        if self.error_message:
            return {
                "ERROR": self.error_message,
                "CODE": self.error_code or "UNKNOWN"
            }
        
        return {
            "Boat Type": self.boat_type,
            "Length": self.length,
            "Width": self.width,
            "Beam": self.beam,
            "Aux": self.aux,
            "Commercial": self.commercial
        }
    
    @classmethod
    def create_from_analysis(cls, image_filename: str, boat_brand: str = "", boat_model: str = "", analysis_result: Dict[str, Any] = None):
        """Create a new BoatAnalysis instance from analysis results"""
        analysis = cls(image_filename, boat_brand, boat_model)
        
        if not analysis_result:
            analysis.error_message = "No analysis result provided"
            analysis.error_code = "SYS003"
            return analysis
        
        if 'ERROR' in analysis_result:
            analysis.error_message = analysis_result['ERROR']
            analysis.error_code = analysis_result.get('CODE', 'UNKNOWN')
        else:
            analysis.boat_type = analysis_result.get('Boat Type')
            analysis.length = analysis_result.get('Length')
            analysis.width = analysis_result.get('Width')
            analysis.beam = analysis_result.get('Beam')
            analysis.aux = analysis_result.get('Aux')
            analysis.commercial = analysis_result.get('Commercial')
        
        return analysis
