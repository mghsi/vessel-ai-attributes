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
        self.LENGTH: Optional[str] = None
        self.BEAM: Optional[str] = None
        self.WEIGHT: Optional[str] = None
        self.hull_coating: Optional[str] = None
        self.AUX: Optional[str] = None
        self.COMMERCIAL: Optional[str] = None
        self.energy_producers: Optional[str] = None
        self.energy_consumers: Optional[str] = None
        self.vessel_age: Optional[str] = None
        self.equipment_age: Optional[str] = None
        self.equipment_condition: Optional[str] = None
        self.FUEL_TYPE: Optional[str] = None

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
            return {"ERROR": self.error_message, "CODE": self.error_code or "UNKNOWN"}

        return {
            "HULL_TYPE": self.boat_type,
            "LENGTH": self.LENGTH,
            "BEAM": self.BEAM,
            "WEIGHT": self.WEIGHT,
            "HULL_COATING": self.hull_coating,
            "AUX": self.AUX,
            "COMMERCIAL": self.COMMERCIAL,
            "ENERGY_PRODUCERS": self.energy_producers,
            "ENERGY_CONSUMERS": self.energy_consumers,
            "VESSEL_AGE": self.vessel_age,
            "EQUIPMENT_AGE": self.equipment_age,
            "EQUIPMENT_CONDITION": self.equipment_condition,
            "FUEL_TYPE": self.FUEL_TYPE,
        }

    @classmethod
    def create_from_analysis(
        cls,
        image_filename: str,
        boat_brand: str = "",
        boat_model: str = "",
        analysis_result: Dict[str, Any] = None,
    ):
        """Create a new BoatAnalysis instance from analysis results"""
        analysis = cls(image_filename, boat_brand, boat_model)

        if not analysis_result:
            analysis.error_message = "No analysis result provided"
            analysis.error_code = "SYS003"
            return analysis

        if "ERROR" in analysis_result:
            analysis.error_message = analysis_result["ERROR"]
            analysis.error_code = analysis_result.get("CODE", "UNKNOWN")
        else:
            analysis.boat_type = analysis_result.get("HULL_TYPE")
            analysis.LENGTH = analysis_result.get("LENGTH")
            analysis.BEAM = analysis_result.get("BEAM")
            analysis.WEIGHT = analysis_result.get("WEIGHT")
            analysis.hull_coating = analysis_result.get("HULL_COATING")
            analysis.AUX = analysis_result.get("AUX")
            analysis.COMMERCIAL = analysis_result.get("COMMERCIAL")
            analysis.energy_producers = analysis_result.get("ENERGY_PRODUCERS")
            analysis.energy_consumers = analysis_result.get("ENERGY_CONSUMERS")
            analysis.vessel_age = analysis_result.get("VESSEL_AGE")
            analysis.equipment_age = analysis_result.get("EQUIPMENT_AGE")
            analysis.equipment_condition = analysis_result.get("EQUIPMENT_CONDITION")
            analysis.FUEL_TYPE = analysis_result.get("FUEL_TYPE")

        return analysis
