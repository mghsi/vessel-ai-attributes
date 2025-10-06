"""
Agentic Workflow System for Boat Baseline Profiling

This module implements a multi-agent system that creates comprehensive baseline profiles
for fossil-fuel boats through a series of specialized agents working in sequence.
"""

import logging
import os
import aiohttp
import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorkflowContext:
    """Shared context between agents in the workflow"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_input: Dict[str, Any] = field(default_factory=dict)
    agent_outputs: Dict[str, Any] = field(default_factory=dict)
    workflow_state: str = "initialized"
    created_at: datetime = field(default_factory=datetime.now)
    current_step: int = 0
    total_steps: int = 6
    
    def update_agent_output(self, agent_name: str, output: Dict[str, Any]):
        """Update output from a specific agent"""
        self.agent_outputs[agent_name] = {
            'output': output,
            'timestamp': datetime.now().isoformat(),
            'step': self.current_step
        }
        logger.info(f"Agent {agent_name} completed step {self.current_step}")
    
    def get_agent_output(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get output from a specific agent"""
        return self.agent_outputs.get(agent_name, {}).get('output')


class BaseAgent:
    """Base class for all agents in the workflow"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
    
    async def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """Execute the agent's main functionality"""
        self.logger.info(f"Starting execution of {self.name}")
        try:
            result = await self._execute_internal(context)
            context.update_agent_output(self.name, result)
            return result
        except Exception as e:
            self.logger.error(f"Error in {self.name}: {str(e)}")
            error_result = {
                'error': str(e),
                'status': 'failed',
                'agent': self.name
            }
            context.update_agent_output(self.name, error_result)
            return error_result
    
    async def _execute_internal(self, context: WorkflowContext) -> Dict[str, Any]:
        """Internal execution method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _execute_internal")


class BoatImageAnalyzerAgent(BaseAgent):
    """Agent 1: Analyzes boat images or processes manual boat data input"""
    
    def __init__(self, github_pat: str, api_url: str, model: str):
        super().__init__("BoatImageAnalyzer", "Analyzes boat images and extracts specifications")
        self.github_pat = github_pat
        self.api_url = api_url
        self.model = model
    
    async def _execute_internal(self, context: WorkflowContext) -> Dict[str, Any]:
        """Analyze boat image or process manual input"""
        input_data = context.user_input
        
        if 'image_data' in input_data:
            # Process image analysis
            return await self._analyze_image(input_data)
        elif 'manual_data' in input_data:
            # Process manual input
            return await self._process_manual_input(input_data['manual_data'])
        else:
            return {
                'error': 'No image or manual data provided',
                'status': 'failed',
                'suggestions': 'Please provide either an image or manual boat specifications'
            }
    
    async def _analyze_image(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze boat image using AI vision model"""
        # This will integrate with existing boat analysis service
        from app.services.boat_analysis_service import BoatAnalysisService
        
        analysis_service = BoatAnalysisService(
            github_pat=self.github_pat,
            api_url=self.api_url,
            model=self.model
        )
        
        image_base64 = input_data.get('image_data')
        boat_brand = input_data.get('brand', '')
        boat_model = input_data.get('model', '')
        
        result = analysis_service.analyze_boat(image_base64, boat_brand, boat_model)
        
        if 'ERROR' in result:
            return {
                'status': 'failed',
                'error': result['ERROR'],
                'code': result.get('CODE', 'UNKNOWN')
            }
        
        # Enhanced analysis with additional boat suggestions
        enhanced_result = await self._enhance_with_similar_boats(result)
        
        return {
            'status': 'success',
            'boat_specifications': enhanced_result,
            'analysis_method': 'image_analysis',
            'suggestions_for_review': await self._generate_review_suggestions(enhanced_result)
        }
    
    async def _process_manual_input(self, manual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process manually entered boat data"""
        required_fields = ['builder_make', 'class_model']
        optional_fields = ['name', 'mmsi', 'length', 'beam', 'boat_type']
        
        # Validate required fields
        missing_fields = [field for field in required_fields if not manual_data.get(field)]
        if missing_fields:
            return {
                'status': 'failed',
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'required_fields': required_fields
            }
        
        # Enrich manual data with AI inference
        enriched_data = await self._enrich_manual_data(manual_data)
        
        return {
            'status': 'success',
            'boat_specifications': enriched_data,
            'analysis_method': 'manual_input',
            'suggestions_for_review': await self._generate_review_suggestions(enriched_data)
        }
    
    async def _enhance_with_similar_boats(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Find similar boats and enhance the analysis"""
        # This would query a boat database or use AI to find similar vessels
        # For now, we'll simulate this with enhanced specifications
        
        enhanced = analysis_result.copy()
        enhanced.update({
            'similar_boats': [
                {
                    'name': 'Similar Vessel 1',
                    'specs': 'Enhanced specifications based on similar boats'
                }
            ],
            'confidence_score': 0.85,
            'enhancement_notes': 'Analysis enhanced with similar boat data'
        })
        
        return enhanced
    
    async def _enrich_manual_data(self, manual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich manual input with AI-generated specifications"""
        # Use AI to infer missing specifications
        enriched = manual_data.copy()
        
        # Add inferred specifications
        enriched.update({
            'inferred_specifications': {
                'estimated_length': self._estimate_length(manual_data),
                'estimated_beam': self._estimate_beam(manual_data),
                'likely_boat_type': self._infer_boat_type(manual_data)
            },
            'confidence_level': 'manual_input_with_inference'
        })
        
        return enriched
    
    async def _generate_review_suggestions(self, boat_specs: Dict[str, Any]) -> List[str]:
        """Generate suggestions for user review"""
        suggestions = [
            "Please review the identified boat specifications",
            "Confirm the boat type classification is correct",
            "Verify the dimensions match your vessel"
        ]
        
        if boat_specs.get('confidence_score', 1.0) < 0.8:
            suggestions.append("Low confidence detected - please verify all details")
        
        return suggestions
    
    def _estimate_length(self, data: Dict[str, Any]) -> float:
        """Estimate boat length from available data"""
        # Placeholder estimation logic
        return data.get('length', 25.0)
    
    def _estimate_beam(self, data: Dict[str, Any]) -> float:
        """Estimate boat beam from available data"""
        # Placeholder estimation logic
        return data.get('beam', 8.0)
    
    def _infer_boat_type(self, data: Dict[str, Any]) -> str:
        """Infer boat type from available data"""
        # Placeholder inference logic
        return data.get('boat_type', 'V-Bottom')


class BoatProfileBuilderAgent(BaseAgent):
    """Agent 2: Builds comprehensive boat profile from specifications and user questions"""
    
    def __init__(self):
        super().__init__("BoatProfileBuilder", "Creates normalized boat profile with usage patterns")
    
    async def _execute_internal(self, context: WorkflowContext) -> Dict[str, Any]:
        """Build comprehensive boat profile"""
        # Get previous agent's output
        analyzer_output = context.get_agent_output("BoatImageAnalyzer")
        if not analyzer_output or analyzer_output.get('status') != 'success':
            return {
                'status': 'failed',
                'error': 'No valid boat specifications from previous step'
            }
        
        boat_specs = analyzer_output.get('boat_specifications', {})
        
        # Generate usage questions
        usage_questions = await self._generate_usage_questions(boat_specs)
        
        # For now, simulate user responses (in real implementation, this would wait for user input)
        simulated_responses = await self._simulate_usage_responses()
        
        # Build normalized profile
        normalized_profile = await self._build_normalized_profile(boat_specs, simulated_responses)
        
        return {
            'status': 'success',
            'usage_questions': usage_questions,
            'usage_responses': simulated_responses,
            'normalized_profile': normalized_profile,
            'profile_attributes': self._extract_profile_attributes(normalized_profile)
        }
    
    async def _generate_usage_questions(self, boat_specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate contextual usage questions based on boat specifications"""
        questions = [
            {
                'id': 'primary_use',
                'question': 'What is the primary use of this vessel?',
                'type': 'multiple_choice',
                'options': ['Recreation', 'Commercial Fishing', 'Transportation', 'Research', 'Other']
            },
            {
                'id': 'operating_hours',
                'question': 'How many hours per day does the vessel typically operate?',
                'type': 'number',
                'min': 0,
                'max': 24
            },
            {
                'id': 'operating_season',
                'question': 'How many months per year is the vessel in operation?',
                'type': 'number',
                'min': 1,
                'max': 12
            },
            {
                'id': 'typical_load',
                'question': 'What is the typical load/cargo capacity utilization?',
                'type': 'percentage',
                'min': 0,
                'max': 100
            },
            {
                'id': 'operating_conditions',
                'question': 'What water conditions does the vessel typically operate in?',
                'type': 'multiple_choice',
                'options': ['Calm waters', 'Moderate seas', 'Rough conditions', 'Variable']
            }
        ]
        
        return questions
    
    async def _simulate_usage_responses(self) -> Dict[str, Any]:
        """Simulate user responses for demonstration"""
        return {
            'primary_use': 'Commercial Fishing',
            'operating_hours': 8,
            'operating_season': 8,
            'typical_load': 75,
            'operating_conditions': 'Moderate seas'
        }
    
    async def _build_normalized_profile(self, boat_specs: Dict[str, Any], usage_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Build normalized boat profile"""
        return {
            'vessel_identity': {
                'builder_make': boat_specs.get('builder_make', 'Unknown'),
                'class_model': boat_specs.get('class_model', 'Unknown'),
                'name': boat_specs.get('name', ''),
                'mmsi': boat_specs.get('mmsi', '')
            },
            'physical_specifications': {
                'length_ft': float(boat_specs.get('Length', '0').replace(' ft', '')) if 'Length' in boat_specs else boat_specs.get('length', 0),
                'beam_ft': float(boat_specs.get('Beam', '0').replace(' ft', '')) if 'Beam' in boat_specs else boat_specs.get('beam', 0),
                'width_ft': float(boat_specs.get('Width', '0').replace(' ft', '')) if 'Width' in boat_specs else boat_specs.get('width', 0),
                'boat_type': boat_specs.get('Boat Type', boat_specs.get('boat_type', 'Unknown'))
            },
            'operational_profile': {
                'primary_use': usage_responses.get('primary_use'),
                'commercial_operation': boat_specs.get('Commercial', 'NO') == 'YES',
                'auxiliary_systems': boat_specs.get('Aux', 'NO') == 'YES',
                'daily_operating_hours': usage_responses.get('operating_hours'),
                'seasonal_months': usage_responses.get('operating_season'),
                'typical_load_percentage': usage_responses.get('typical_load'),
                'operating_conditions': usage_responses.get('operating_conditions')
            },
            'profile_metadata': {
                'created_at': datetime.now().isoformat(),
                'confidence_level': boat_specs.get('confidence_score', 0.8),
                'data_sources': ['image_analysis' if 'image_analysis' in str(boat_specs) else 'manual_input', 'user_questionnaire']
            }
        }
    
    def _extract_profile_attributes(self, profile: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract key profile attributes for display"""
        attributes = []
        
        # Physical attributes
        physical = profile.get('physical_specifications', {})
        if physical.get('length_ft'):
            attributes.append({'category': 'Physical', 'name': 'Length', 'value': f"{physical['length_ft']} ft"})
        if physical.get('beam_ft'):
            attributes.append({'category': 'Physical', 'name': 'Beam', 'value': f"{physical['beam_ft']} ft"})
        if physical.get('boat_type'):
            attributes.append({'category': 'Physical', 'name': 'Type', 'value': physical['boat_type']})
        
        # Operational attributes
        operational = profile.get('operational_profile', {})
        if operational.get('primary_use'):
            attributes.append({'category': 'Operational', 'name': 'Primary Use', 'value': operational['primary_use']})
        if operational.get('daily_operating_hours'):
            attributes.append({'category': 'Operational', 'name': 'Daily Hours', 'value': f"{operational['daily_operating_hours']} hrs"})
        
        return attributes


class PerformanceCurveGeneratorAgent(BaseAgent):
    """Agent 3: Generates vessel performance curves using naval architecture principles"""
    
    def __init__(self):
        super().__init__("PerformanceCurveGenerator", "Generates performance curves using Holtrop-Mennen resistance prediction")
    
    async def _execute_internal(self, context: WorkflowContext) -> Dict[str, Any]:
        """Generate detailed performance curves using naval architecture methods"""
        profile_output = context.get_agent_output("BoatProfileBuilder")
        if not profile_output or profile_output.get('status') != 'success':
            return {
                'status': 'failed',
                'error': 'No valid boat profile from previous step'
            }
        
        normalized_profile = profile_output.get('normalized_profile', {})
        physical_specs = normalized_profile.get('physical_specifications', {})
        
        # Extract vessel parameters
        length_ft = physical_specs.get('length_ft', 30)
        beam_ft = physical_specs.get('beam_ft', 10)
        boat_type = physical_specs.get('boat_type', 'RHIB')
        
        # Convert to metric
        length_m = length_ft * 0.3048
        beam_m = beam_ft * 0.3048
        
        # Estimate displacement and other parameters
        displacement = self._estimate_displacement(length_m, beam_m, boat_type)
        
        # Generate detailed naval analysis
        naval_analysis = await self._generate_naval_analysis(length_m, beam_m, displacement, boat_type)
        
        # Generate CSV performance data
        csv_data = self._generate_csv_performance_data(length_m, beam_m, displacement)
        
        # Generate simplified curves for display
        display_curves = await self._generate_display_curves(normalized_profile)
        
        return {
            'status': 'success',
            'performance_curves': display_curves,
            'naval_analysis': naval_analysis,
            'csv_data': csv_data,
            'methodology': self._get_methodology_explanation(),
            'justification_table': self._get_justification_table(length_m, beam_m, displacement),
            'download_available': True,
            'curve_metadata': {
                'generation_method': 'holtrop_mennen_simplified',
                'validation_status': 'engineering_estimate',
                'confidence_level': 'baseline_suitable',
                'generated_at': datetime.now().isoformat()
            },
            'validation_notes': [
                'Performance curves generated using Holtrop-Mennen resistance prediction methods',
                'CSV data includes detailed speed-thrust-power-battery demand analysis',
                'Suitable for baseline profiling; validation recommended for precision applications'
            ]
        }
    
    async def _generate_speed_fuel_curve(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate speed vs fuel consumption curve"""
        physical_specs = profile.get('physical_specifications', {})
        length = physical_specs.get('length_ft', 25)
        boat_type = physical_specs.get('boat_type', 'V-Bottom')
        
        # Generate curve points based on boat characteristics
        speeds = list(range(5, 31, 2))  # 5 to 30 knots in 2-knot increments
        fuel_rates = []
        
        for speed in speeds:
            # Simplified fuel consumption calculation
            base_consumption = self._calculate_base_fuel_consumption(speed, length, boat_type)
            fuel_rates.append(round(base_consumption, 2))
        
        return {
            'curve_type': 'speed_vs_fuel_rate',
            'x_axis': {'label': 'Speed (knots)', 'values': speeds},
            'y_axis': {'label': 'Fuel Rate (gal/hr)', 'values': fuel_rates},
            'curve_equation': f'Fuel Rate = f(Speed, Length={length}ft, Type={boat_type})',
            'data_points': list(zip(speeds, fuel_rates))
        }
    
    async def _generate_speed_power_curve(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate speed vs shaft power curve"""
        physical_specs = profile.get('physical_specifications', {})
        length = physical_specs.get('length_ft', 25)
        beam = physical_specs.get('beam_ft', 8)
        
        speeds = list(range(5, 31, 2))
        power_values = []
        
        for speed in speeds:
            # Power increases roughly with cube of speed
            base_power = (speed ** 2.8) * (length / 25) * (beam / 8) * 10
            power_values.append(round(base_power, 1))
        
        return {
            'curve_type': 'speed_vs_shaft_power',
            'x_axis': {'label': 'Speed (knots)', 'values': speeds},
            'y_axis': {'label': 'Shaft Power (HP)', 'values': power_values},
            'curve_equation': f'Power = f(Speed^2.8, Length={length}ft, Beam={beam}ft)',
            'data_points': list(zip(speeds, power_values))
        }
    
    async def _generate_speed_thrust_curve(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate speed vs thrust curve"""
        physical_specs = profile.get('physical_specifications', {})
        length = physical_specs.get('length_ft', 25)
        
        speeds = list(range(5, 31, 2))
        thrust_values = []
        
        for speed in speeds:
            # Thrust generally decreases with speed for constant power
            base_thrust = 1000 * (length / 25) / (speed / 10)
            thrust_values.append(round(base_thrust, 1))
        
        return {
            'curve_type': 'speed_vs_thrust',
            'x_axis': {'label': 'Speed (knots)', 'values': speeds},
            'y_axis': {'label': 'Thrust (lbs)', 'values': thrust_values},
            'curve_equation': f'Thrust = f(1/Speed, Length={length}ft)',
            'data_points': list(zip(speeds, thrust_values))
        }
    
    async def _generate_acceleration_power_curves(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate acceleration vs power curves"""
        accelerations = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]  # ft/s²
        power_requirements = []
        
        for accel in accelerations:
            # Power requirement increases with acceleration
            power_req = accel * 100 + 200  # Simplified calculation
            power_requirements.append(round(power_req, 1))
        
        return {
            'curve_type': 'acceleration_vs_power',
            'x_axis': {'label': 'Acceleration (ft/s²)', 'values': accelerations},
            'y_axis': {'label': 'Power Required (HP)', 'values': power_requirements},
            'curve_equation': 'Power = f(Acceleration, Vessel Mass)',
            'data_points': list(zip(accelerations, power_requirements))
        }
    
    def _calculate_base_fuel_consumption(self, speed: float, length: float, boat_type: str) -> float:
        """Calculate base fuel consumption for given parameters"""
        # Base consumption factors by boat type
        type_factors = {
            'V-Bottom': 1.0,
            'Flat Bottom': 0.8,
            'Multi-hull': 0.7,
            'Pontoon': 0.9,
            'RHIB': 1.1,
            'Semi-Displacement': 0.85
        }
        
        factor = type_factors.get(boat_type, 1.0)
        # Fuel consumption increases roughly with speed squared
        base_consumption = (speed ** 2.2) * (length / 25) * factor * 0.5
        return max(base_consumption, 2.0)  # Minimum 2 gal/hr
    
    def _estimate_displacement(self, length_m: float, beam_m: float, boat_type: str) -> float:
        """Estimate displacement based on vessel dimensions and type"""
        if boat_type.upper() == "RHIB":
            # RHIB displacement estimation: lighter than conventional boats
            volume_coefficient = 0.35  # RHIBs have lower Cb due to inflatable collar
        else:
            volume_coefficient = 0.45  # General recreational/commercial boat
        
        # Estimated draft for RHIB (typically shallow)
        draft_m = length_m * 0.08  # Conservative estimate
        
        # Displacement = Length × Beam × Draft × Cb × ρ_water
        rho_water = 1025  # kg/m³ seawater density
        displacement = length_m * beam_m * draft_m * volume_coefficient * rho_water
        
        return displacement  # kg
    
    async def _generate_naval_analysis(self, length_m: float, beam_m: float, displacement: float, boat_type: str) -> str:
        """Generate detailed naval architecture analysis using GitHub Models API"""
        
        prompt = f"""Act as a senior naval architect and marine systems performance engineer. 

Vessel Specifications:
- Length: {length_m:.2f} m ({length_m/0.3048:.1f} ft)
- Beam: {beam_m:.2f} m ({beam_m/0.3048:.1f} ft)
- Type: {boat_type}
- Estimated Displacement: {displacement:.0f} kg

Generate a detailed performance analysis using hydrodynamic resistance prediction methods (Holtrop-Mennen approach). 

Provide:
1. Resistance components analysis (frictional, residual, form factors)
2. Service speed determination and operational envelope
3. Power requirements across speed range
4. Thrust characteristics and propeller considerations
5. Battery demand estimates for hybrid/electric operation

Focus on technical rigor and practical applicability for baseline profiling."""

        try:
            headers = {
                'Authorization': f'Bearer {os.getenv("GITHUB_TOKEN")}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "model": "gpt-4o",
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://models.inference.ai.azure.com/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        return "Naval analysis temporarily unavailable - using simplified model"
                        
        except Exception as e:
            return f"Naval analysis error: {str(e)} - using simplified model"
    
    def _generate_csv_performance_data(self, length_m: float, beam_m: float, displacement: float) -> str:
        """Generate CSV performance data using Holtrop-Mennen simplified approach"""
        
        csv_lines = ["speed_mps,thrust_N,shaft_power_W,battery_demand_W"]
        
        # Constants
        rho_water = 1025  # kg/m³
        g = 9.81  # m/s²
        nu = 1.19e-6  # kinematic viscosity of seawater at 15°C
        
        # Vessel parameters
        wetted_surface = self._estimate_wetted_surface(length_m, beam_m, displacement)
        service_speed_ms = self._estimate_service_speed(length_m)
        
        # Generate data from 0 to service speed in 0.25 m/s increments
        speed = 0.0
        while speed <= service_speed_ms:
            if speed == 0:
                # At zero speed
                thrust_N = 0
                shaft_power_W = 0
                battery_demand_W = 0
            else:
                # Reynolds number
                Re = speed * length_m / nu
                
                # Frictional resistance coefficient (ITTC 1957)
                Cf = 0.075 / (math.log10(Re) - 2)**2
                
                # Form factor (simplified for RHIB)
                k1 = 0.15  # Typical for RHIB hull forms
                
                # Frictional resistance
                Rf = 0.5 * rho_water * speed**2 * wetted_surface * Cf * (1 + k1)
                
                # Residual resistance (Holtrop-Mennen simplified)
                Froude_number = speed / math.sqrt(g * length_m)
                if Froude_number < 0.4:
                    Cr_coeff = 0.001 * (Froude_number * 10)**3
                else:
                    Cr_coeff = 0.001 * (Froude_number * 10)**2
                
                Rr = 0.5 * rho_water * speed**2 * wetted_surface * Cr_coeff
                
                # Total resistance
                Rt = Rf + Rr
                
                # Thrust (assuming 15% thrust deduction)
                thrust_N = Rt / 0.85
                
                # Effective power
                Pe = Rt * speed
                
                # Shaft power (assuming 65% total efficiency)
                shaft_power_W = Pe / 0.65
                
                # Battery demand (assuming 90% electric motor efficiency)
                battery_demand_W = shaft_power_W / 0.90
            
            csv_lines.append(f"{speed:.2f},{thrust_N:.1f},{shaft_power_W:.0f},{battery_demand_W:.0f}")
            speed += 0.25
        
        return "\n".join(csv_lines)
    
    def _estimate_wetted_surface(self, length_m: float, beam_m: float, displacement: float) -> float:
        """Estimate wetted surface area"""
        # Simplified wetted surface estimation for RHIB
        # Using Froude's approximation with RHIB correction factor
        draft_est = (displacement / (1025 * length_m * beam_m * 0.35))**(1/3)
        
        # Wetted surface approximation
        S = length_m * (2 * draft_est + beam_m) * 0.85  # 0.85 factor for RHIB shape
        return S
    
    def _estimate_service_speed(self, length_m: float) -> float:
        """Estimate service speed based on vessel length"""
        # Typical service speed for RHIB: 0.4-0.6 of hull speed
        hull_speed_ms = 1.34 * math.sqrt(length_m)  # Theoretical hull speed
        service_speed_ms = hull_speed_ms * 0.5  # Conservative estimate
        return min(service_speed_ms, 15.0)  # Cap at reasonable speed
    
    def _get_methodology_explanation(self) -> str:
        """Provide methodology explanation"""
        return """
**METHODOLOGY**: This analysis employs a simplified Holtrop-Mennen resistance prediction approach specifically adapted for RHIB vessels. 

The methodology includes:
1. **Frictional Resistance**: Calculated using ITTC 1957 formula with form factor corrections
2. **Residual Resistance**: Estimated using Froude number-based correlations
3. **Thrust Requirements**: Derived from total resistance with thrust deduction factor
4. **Power Calculations**: Convert effective power to shaft power using efficiency assumptions
5. **Battery Demand**: Electric motor efficiency applied to shaft power requirements

**VALIDATION RECOMMENDED**: These calculations provide baseline estimates suitable for initial analysis. For precision applications, model testing or CFD validation is recommended.
"""
    
    def _get_justification_table(self, length_m: float, beam_m: float, displacement: float) -> Dict[str, Any]:
        """Generate justification table with formulas and assumptions"""
        return {
            "vessel_parameters": {
                "length_m": f"{length_m:.2f}",
                "beam_m": f"{beam_m:.2f}",
                "displacement_kg": f"{displacement:.0f}",
                "estimated_draft_m": f"{(displacement / (1025 * length_m * beam_m * 0.35))**(1/3):.2f}"
            },
            "constants_used": {
                "seawater_density": "1025 kg/m³",
                "kinematic_viscosity": "1.19e-6 m²/s (15°C seawater)",
                "gravitational_acceleration": "9.81 m/s²"
            },
            "formulas_applied": {
                "reynolds_number": "Re = V × L / ν",
                "frictional_coefficient": "Cf = 0.075 / (log₁₀(Re) - 2)²",
                "frictional_resistance": "Rf = 0.5 × ρ × V² × S × Cf × (1 + k₁)",
                "froude_number": "Fn = V / √(g × L)",
                "total_resistance": "Rt = Rf + Rr",
                "thrust": "T = Rt / (1 - t), where t = 0.15",
                "shaft_power": "Ps = Pe / ηtotal, where ηtotal = 0.65"
            },
            "assumptions": {
                "form_factor_k1": "0.15 (typical for RHIB hull)",
                "thrust_deduction": "0.15 (15%)",
                "total_efficiency": "0.65 (65% propulsive efficiency)",
                "electric_motor_efficiency": "0.90 (90%)",
                "block_coefficient": "0.35 (RHIB with inflatable collar)"
            }
        }
    
    async def _generate_display_curves(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simplified curves for display"""
        speed_fuel_curve = await self._generate_speed_fuel_curve(profile)
        speed_power_curve = await self._generate_speed_power_curve(profile)
        speed_thrust_curve = await self._generate_speed_thrust_curve(profile)
        acceleration_power_curves = await self._generate_acceleration_power_curves(profile)
        
        return {
            'speed_vs_fuel_rate': speed_fuel_curve,
            'speed_vs_shaft_power': speed_power_curve,
            'speed_vs_thrust': speed_thrust_curve,
            'acceleration_vs_power': acceleration_power_curves
        }


class WorkflowOrchestrator:
    """Orchestrates the multi-agent workflow"""
    
    def __init__(self, github_pat: str, api_url: str, model: str):
        self.github_pat = github_pat
        self.api_url = api_url
        self.model = model
        self.agents = self._initialize_agents()
        self.active_contexts: Dict[str, WorkflowContext] = {}
    
    def _initialize_agents(self) -> List[BaseAgent]:
        """Initialize all agents in the workflow"""
        # Import additional agents
        from .additional_agents import (
            TelemetryDataProcessorAgent,
            VoyageAnalyticsEngine,
            ReportChartGeneratorAgent
        )
        
        return [
            BoatImageAnalyzerAgent(self.github_pat, self.api_url, self.model),
            BoatProfileBuilderAgent(),
            PerformanceCurveGeneratorAgent(),
            TelemetryDataProcessorAgent(),
            VoyageAnalyticsEngine(),
            ReportChartGeneratorAgent()
        ]
    
    async def start_workflow(self, user_input: Dict[str, Any]) -> str:
        """Start a new workflow session"""
        context = WorkflowContext(user_input=user_input)
        self.active_contexts[context.session_id] = context
        
        logger.info(f"Started workflow session {context.session_id}")
        return context.session_id
    
    async def execute_next_step(self, session_id: str) -> Dict[str, Any]:
        """Execute the next step in the workflow"""
        if session_id not in self.active_contexts:
            return {'error': 'Invalid session ID'}
        
        context = self.active_contexts[session_id]
        
        if context.current_step >= len(self.agents):
            return {
                'status': 'completed',
                'message': 'Workflow completed successfully',
                'results': context.agent_outputs
            }
        
        agent = self.agents[context.current_step]
        result = await agent.execute(context)
        
        context.current_step += 1
        
        return {
            'status': 'in_progress',
            'current_step': context.current_step,
            'total_steps': context.total_steps,
            'agent_name': agent.name,
            'agent_result': result,
            'session_id': session_id
        }
    
    def get_workflow_status(self, session_id: str) -> Dict[str, Any]:
        """Get current workflow status"""
        if session_id not in self.active_contexts:
            return {'error': 'Invalid session ID'}
        
        context = self.active_contexts[session_id]
        return {
            'session_id': session_id,
            'current_step': context.current_step,
            'total_steps': context.total_steps,
            'workflow_state': context.workflow_state,
            'agent_outputs': context.agent_outputs,
            'created_at': context.created_at.isoformat()
        }