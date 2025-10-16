import base64
import json
import os
import time
from typing import Dict, Any, Optional
import requests
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


class ImageProcessingService:
    """Service to handle image processing operations"""

    @staticmethod
    def validate_image(file: FileStorage, allowed_extensions: set) -> bool:
        """Validate if the uploaded file is a valid image"""
        if not file or not file.filename:
            return False

        return (
            "." in file.filename
            and file.filename.rsplit(".", 1)[1].lower() in allowed_extensions
        )

    @staticmethod
    def save_image(file: FileStorage, upload_folder: str) -> str:
        """Save uploaded image to the specified folder"""
        filename = secure_filename(file.filename)
        # Add timestamp to avoid filename conflicts
        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename

    @staticmethod
    def encode_image_to_base64(filepath: str) -> str:
        """Encode image file to base64 string"""
        with open(filepath, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


class BoatAnalysisService:
    """Service to handle boat analysis using AI models"""

    def __init__(self, github_pat: str, api_url: str, model: str):
        self.github_pat = github_pat
        self.api_url = api_url
        self.model = model
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_pat}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }

    def analyze_boat(
        self, image_base64: str, boat_brand: str = "", boat_model: str = ""
    ) -> Dict[str, Any]:
        """Analyze boat image using AI model"""
        try:
            prompt = self._build_analysis_prompt(boat_brand, boat_model)
            payload = self._build_payload(image_base64, prompt)

            response = requests.post(self.api_url, headers=self.headers, json=payload)

            if response.status_code != 200:
                return {
                    "ERROR": f"AI model API call failed: {response.text}",
                    "CODE": f"API{response.status_code}",
                }

            result = response.json()
            return self._parse_model_response(result)

        except requests.exceptions.RequestException as e:
            return {
                "ERROR": f"Network error during analysis: {str(e)}",
                "CODE": "NET001",
            }
        except Exception as e:
            return {
                "ERROR": f"Unexpected error during analysis: {str(e)}",
                "CODE": "SYS001",
            }

    def _build_analysis_prompt(self, boat_brand: str, boat_model: str) -> str:
        """Build the analysis prompt for the AI model"""
        brand_info = (
            f"Boat Brand: {boat_brand}" if boat_brand else "Boat Brand: Unknown"
        )
        model_info = (
            f"Boat Model: {boat_model}" if boat_model else "Boat Model: Unknown"
        )

        return f"""
Analyze the provided image of a boat to determine specific characteristics and usage details.

{brand_info}
{model_info}

Your task is to classify the HULL_TYPE, measure its dimensions, determine its usage and AUXiliary features, and predict the FUEL_TYPE based primarily on the visual analysis of the image. If brand and model information is provided, use it as additional context, but rely mainly on what you can observe in the image.

Steps:
1. **Identify HULL_TYPE**: Examine the image to classify the boat into one of the following types: Flat Bottom, Multi-hull, Pontoon, RHIB, Semi-Displacement, or V-Bottom.
2. **Measure Dimensions**: Determine the LENGTH and BEAM of the boat in feet. Note: BEAM is the width of the boat at its widest point.
3. **Estimate WEIGHT**: Provide an estimated WEIGHT of the vessel in pounds based on its size, type, and construction.
4. **Assess HULL_COATING**: Evaluate the HULL_COATING condition (low, medium, or high quality/condition).
5. **Determine Usage**: Assess if the boat is used for COMMERCIAL purposes.
6. **Check for AUXiliary Features**: Identify if the boat has any AUXiliary features (YES/NO).
7. **Predict FUEL_TYPE**: Based on the boat's size, type, visible features, and any brand/model information, predict the most likely fuel type from: gasoline, marineDiesel, hybrid, electric, or other.
8. **Identify Energy Equipment**: 
   - ENERGY_PRODUCERS: List visible energy-producing equipment (e.g., solar panels, generators, wind turbines)
   - ENERGY_CONSUMERS: List visible energy-consuming equipment (e.g., lights, electronics, motors)
9. **Assess EQUIPMENT_CONDITION**:
   - VESSEL_AGE: Estimate age category (0-5, 5-10, 10-20, 20-30, 30+ years)
   - EQUIPMENT_AGE: Estimate EQUIPMENT_AGE category (0-5, 5-10, 10-20, 20-30, 30+ years)
   - EQUIPMENT_CONDITION: Overall EQUIPMENT_CONDITION (poor, fair, good, excellent)
10. **Error Handling**: If the image is unclear, not a boat, or if any other issue prevents analysis, provide an error response.

Output Format:
The output should be a JSON object with the following structure:

```json
{{
  "HULL_TYPE": "<TYPE>",
  "LENGTH": "<LENGTH>",
  "BEAM": "<BEAM>",
  "WEIGHT": "<WEIGHT_IN_POUNDS>",
  "HULL_COATING": "<low|medium|high>",
  "AUX": "<YES/NO>",
  "COMMERCIAL": "<YES/NO>",
  "FUEL_TYPE": "<gasoline|marineDiesel|hybrid|electric|other>",
  "ENERGY_PRODUCERS": "<EQUIPMENT_LIST>",
  "ENERGY_CONSUMERS": "<EQUIPMENT_LIST>",
  "VESSEL_AGE": "<0-5|5-10|10-20|20-30|30+>",
  "EQUIPMENT_AGE": "<0-5|5-10|10-20|20-30|30+>",
  "EQUIPMENT_CONDITION": "<poor|fair|good|excellent>"
}}
```

If an error occurs, use the following format:

```json
{{
  "ERROR": "<description>",
  "CODE": "<CODE>"
}}
```

Notes:
- Ensure all measurements are in feet.
- Use the provided model and brand information to assist in determining the boat's characteristics.
- For FUEL_TYPE prediction, consider boat size (smaller boats typically use gasoline, larger commercial vessels often use marine diesel), visible features (solar panels may indicate hybrid/electric), and boat type.
- Consider edge cases where the image may not clearly depict a boat or where the model and brand information is insufficient.
- Return ONLY the JSON object, no additional text.
"""

    def _build_payload(self, image_base64: str, prompt: str) -> Dict[str, Any]:
        """Build the payload for the AI model API"""
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert boat analyzer. Analyze boat images and return structured JSON data only.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                    ],
                },
            ],
            "max_tokens": 500,
            "temperature": 0.1,
        }

    def _parse_model_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the response from the AI model"""
        try:
            if "choices" not in response or not response["choices"]:
                return {
                    "ERROR": "Invalid response format from AI model",
                    "CODE": "PARSE001",
                }

            content = response["choices"][0]["message"]["content"].strip()

            # Try to extract JSON from the response
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            # Parse JSON
            analysis_result = json.loads(content)

            # Validate the response structure
            if "ERROR" in analysis_result:
                return analysis_result

            required_fields = [
                "HULL_TYPE",
                "LENGTH",
                "BEAM",
                "WEIGHT",
                "HULL_COATING",
                "AUX",
                "COMMERCIAL",
                "FUEL_TYPE",
                "ENERGY_PRODUCERS",
                "ENERGY_CONSUMERS",
                "VESSEL_AGE",
                "EQUIPMENT_AGE",
                "EQUIPMENT_CONDITION",
            ]
            for field in required_fields:
                if field not in analysis_result:
                    return {
                        "ERROR": f"Missing required field: {field}",
                        "CODE": "PARSE002",
                    }

            return analysis_result

        except json.JSONDecodeError:
            return {
                "ERROR": "Failed to parse AI model response as JSON",
                "CODE": "PARSE003",
            }
        except Exception as e:
            return {
                "ERROR": f"Error parsing model response: {str(e)}",
                "CODE": "PARSE004",
            }
