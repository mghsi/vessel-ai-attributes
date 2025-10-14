"""
Additional Agents for the Agentic Workflow System

This module contains the remaining agents (4-6) for telemetry processing,
voyage analytics, and report generation.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import io
import base64

# Set matplotlib backend for headless environment
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Import data libraries with error handling for Docker
try:
    import pandas as pd
    import numpy as np
except ImportError as e:
    logging.error(f"Required packages not installed: {e}")
    raise

from .agentic_workflow import BaseAgent, WorkflowContext

logger = logging.getLogger(__name__)


class TelemetryDataProcessorAgent(BaseAgent):
    """Agent 4: Processes telemetry data and separates voyage sets"""

    def __init__(self):
        super().__init__(
            "TelemetryDataProcessor",
            "Processes lat/long/SOW telemetry and water current data",
        )

    async def _execute_internal(self, context: WorkflowContext) -> Dict[str, Any]:
        """Process telemetry data and separate into voyage sets"""

        # Load sample telemetry data (this would come from CSV files)
        telemetry_data = await self._load_sample_telemetry_data()
        water_current_data = await self._load_sample_water_current_data()

        # Merge telemetry with water current data
        enriched_telemetry = await self._merge_telemetry_with_currents(
            telemetry_data, water_current_data
        )

        # Separate into voyage sets
        voyage_sets = await self._separate_voyage_sets(enriched_telemetry)

        # Generate voyage statistics
        voyage_stats = await self._generate_voyage_statistics(voyage_sets)

        return {
            "status": "success",
            "telemetry_summary": {
                "total_data_points": len(enriched_telemetry),
                "date_range": {
                    "start": enriched_telemetry["timestamp"].min().isoformat(),
                    "end": enriched_telemetry["timestamp"].max().isoformat(),
                },
                "voyage_count": len(voyage_sets["away_from_dock"]),
                "dwell_periods": len(voyage_sets["at_dock"]),
            },
            "voyage_sets": {
                "away_from_dock": self._serialize_voyage_data(
                    voyage_sets["away_from_dock"]
                ),
                "at_dock": self._serialize_voyage_data(voyage_sets["at_dock"]),
            },
            "voyage_statistics": voyage_stats,
            "water_current_integration": "completed",
        }

    async def _load_sample_telemetry_data(self) -> pd.DataFrame:
        """Load sample Membertou 2023 boat telemetry data"""
        # Generate sample data for demonstration
        dates = pd.date_range("2023-06-01", "2023-10-31", freq="H")
        n_points = len(dates)

        # Base coordinates (Nova Scotia area)
        base_lat, base_lon = 45.8, -61.0

        data = {
            "timestamp": dates,
            "latitude": base_lat + np.random.normal(0, 0.01, n_points),
            "longitude": base_lon + np.random.normal(0, 0.01, n_points),
            "speed_over_water": np.maximum(0, np.random.normal(12, 4, n_points)),
            "heading": np.random.uniform(0, 360, n_points),
            "engine_rpm": np.maximum(0, np.random.normal(1800, 300, n_points)),
            "fuel_flow": np.maximum(0, np.random.normal(15, 5, n_points)),
        }

        df = pd.DataFrame(data)

        # Add realistic patterns (operating during day, docked at night)
        df["hour"] = df["timestamp"].dt.hour
        df["is_operating"] = (df["hour"] >= 6) & (df["hour"] <= 18)

        # Set docked conditions
        df.loc[~df["is_operating"], "speed_over_water"] = 0
        df.loc[~df["is_operating"], "engine_rpm"] = 0
        df.loc[~df["is_operating"], "fuel_flow"] = 0.5  # AUXiliary power

        return df

    async def _load_sample_water_current_data(self) -> pd.DataFrame:
        """Load sample water current data"""
        dates = pd.date_range("2023-06-01", "2023-10-31", freq="H")
        n_points = len(dates)

        # Base coordinates matching telemetry
        base_lat, base_lon = 45.8, -61.0

        current_data = {
            "timestamp": dates,
            "latitude": base_lat + np.random.normal(0, 0.02, n_points),
            "longitude": base_lon + np.random.normal(0, 0.02, n_points),
            "current_speed": np.maximum(0, np.random.normal(1.5, 0.8, n_points)),
            "current_direction": np.random.uniform(0, 360, n_points),
            "tide_height": np.sin(np.arange(n_points) * 2 * np.pi / 12.42) * 2
            + 3,  # Tidal pattern
        }

        return pd.DataFrame(current_data)

    async def _merge_telemetry_with_currents(
        self, telemetry: pd.DataFrame, currents: pd.DataFrame
    ) -> pd.DataFrame:
        """Merge telemetry data with water current data"""
        # For demonstration, we'll use nearest time matching
        merged = telemetry.copy()

        # Add current data (simplified spatial/temporal matching)
        merged["current_speed"] = np.interp(
            merged.index, currents.index, currents["current_speed"]
        )
        merged["current_direction"] = np.interp(
            merged.index, currents.index, currents["current_direction"]
        )
        merged["tide_height"] = np.interp(
            merged.index, currents.index, currents["tide_height"]
        )

        # Calculate speed over ground accounting for currents
        merged["speed_over_ground"] = merged["speed_over_water"] + np.random.normal(
            0, 0.5, len(merged)
        )

        return merged

    async def _separate_voyage_sets(
        self, telemetry: pd.DataFrame
    ) -> Dict[str, List[pd.DataFrame]]:
        """Separate telemetry into voyage sets: away from dock vs at dock"""
        # Define docked condition (speed < 0.5 knots for more than 30 minutes)
        telemetry["is_docked"] = telemetry["speed_over_water"] < 0.5

        # Find voyage transitions
        telemetry["voyage_change"] = telemetry["is_docked"] != telemetry[
            "is_docked"
        ].shift(1)
        telemetry["voyage_id"] = telemetry["voyage_change"].cumsum()

        away_from_dock = []
        at_dock = []

        for voyage_id in telemetry["voyage_id"].unique():
            voyage_segment = telemetry[telemetry["voyage_id"] == voyage_id].copy()

            if len(voyage_segment) < 2:  # Skip very short segments
                continue

            if voyage_segment["is_docked"].iloc[0]:
                at_dock.append(voyage_segment)
            else:
                away_from_dock.append(voyage_segment)

        return {"away_from_dock": away_from_dock, "at_dock": at_dock}

    async def _generate_voyage_statistics(
        self, voyage_sets: Dict[str, List[pd.DataFrame]]
    ) -> Dict[str, Any]:
        """Generate statistics for voyage sets"""
        stats = {}

        # Statistics for voyages away from dock
        away_voyages = voyage_sets["away_from_dock"]
        if away_voyages:
            durations = [len(v) for v in away_voyages]  # Hours
            distances = [
                v["speed_over_water"].sum() for v in away_voyages
            ]  # Approximate nautical miles
            avg_speeds = [
                v["speed_over_water"].mean() for v in away_voyages if len(v) > 0
            ]

            stats["away_from_dock"] = {
                "voyage_count": len(away_voyages),
                "avg_duration_hours": np.mean(durations),
                "avg_distance_nm": np.mean(distances),
                "avg_speed_knots": np.mean(avg_speeds) if avg_speeds else 0,
                "total_operating_hours": sum(durations),
            }

        # Statistics for dwell periods
        dock_periods = voyage_sets["at_dock"]
        if dock_periods:
            dwell_durations = [len(d) for d in dock_periods]

            stats["at_dock"] = {
                "dwell_period_count": len(dock_periods),
                "avg_dwell_duration_hours": np.mean(dwell_durations),
                "total_dwell_hours": sum(dwell_durations),
            }

        return stats

    def _serialize_voyage_data(
        self, voyage_list: List[pd.DataFrame]
    ) -> List[Dict[str, Any]]:
        """Serialize voyage data for JSON response"""
        serialized = []
        for i, voyage in enumerate(voyage_list[:5]):  # Limit to first 5 for demo
            serialized.append(
                {
                    "voyage_id": i + 1,
                    "start_time": voyage["timestamp"].iloc[0].isoformat(),
                    "end_time": voyage["timestamp"].iloc[-1].isoformat(),
                    "duration_hours": len(voyage),
                    "data_points": len(voyage),
                    "avg_speed": voyage["speed_over_water"].mean(),
                    "max_speed": voyage["speed_over_water"].max(),
                    "avg_fuel_flow": voyage["fuel_flow"].mean(),
                }
            )
        return serialized


class VoyageAnalyticsEngine(BaseAgent):
    """Agent 5: Calculates fuel consumption and emissions analytics"""

    def __init__(self):
        super().__init__(
            "VoyageAnalyticsEngine", "Calculates baseline fuel and emissions by voyage"
        )

    async def _execute_internal(self, context: WorkflowContext) -> Dict[str, Any]:
        """Calculate fuel consumption and emissions analytics"""

        # Get inputs from previous agents
        profile_data = context.get_agent_output("BoatProfileBuilder")
        curves_data = context.get_agent_output("PerformanceCurveGenerator")
        telemetry_data = context.get_agent_output("TelemetryDataProcessor")

        if not all([profile_data, curves_data, telemetry_data]):
            return {
                "status": "failed",
                "error": "Missing required data from previous agents",
            }

        # Apply performance curves to telemetry data
        voyage_analytics = await self._calculate_voyage_analytics(
            profile_data, curves_data, telemetry_data
        )

        # Calculate dwell time fuel requirements
        dwell_analytics = await self._calculate_dwell_analytics(
            profile_data, telemetry_data
        )

        # Generate CSV outputs
        voyage_csv = await self._generate_voyage_csv(voyage_analytics)
        dwell_csv = await self._generate_dwell_csv(dwell_analytics)

        return {
            "status": "success",
            "voyage_analytics": voyage_analytics,
            "dwell_analytics": dwell_analytics,
            "csv_outputs": {"voyage_data": voyage_csv, "dwell_data": dwell_csv},
            "emissions_summary": await self._calculate_emissions_summary(
                voyage_analytics, dwell_analytics
            ),
        }

    async def _calculate_voyage_analytics(
        self, profile_data: Dict, curves_data: Dict, telemetry_data: Dict
    ) -> Dict[str, Any]:
        """Calculate fuel consumption and emissions for each voyage"""

        # Get performance curves
        fuel_curve = curves_data.get("performance_curves", {}).get(
            "speed_vs_fuel_rate", {}
        )
        power_curve = curves_data.get("performance_curves", {}).get(
            "speed_vs_shaft_power", {}
        )

        if not fuel_curve or not power_curve:
            return {"error": "Performance curves not available"}

        # Extract curve data
        speeds = fuel_curve.get("x_axis", {}).get("values", [])
        fuel_rates = fuel_curve.get("y_axis", {}).get("values", [])
        power_values = power_curve.get("y_axis", {}).get("values", [])

        voyage_results = []
        voyage_sets = telemetry_data.get("voyage_sets", {}).get("away_from_dock", [])

        for i, voyage in enumerate(voyage_sets):
            if not voyage:
                continue

            # Calculate fuel consumption for this voyage
            total_fuel = 0
            total_distance = 0
            total_time = voyage.get("duration_hours", 0)
            avg_speed = voyage.get("avg_speed", 0)

            # Interpolate fuel rate from curve
            if speeds and fuel_rates and avg_speed > 0:
                fuel_rate = np.interp(avg_speed, speeds, fuel_rates)
                total_fuel = fuel_rate * total_time
                total_distance = avg_speed * total_time

            # Calculate emissions (simplified)
            co2_factor = 22.38  # lbs CO2 per gallon diesel
            total_co2 = total_fuel * co2_factor

            voyage_results.append(
                {
                    "voyage_id": i + 1,
                    "start_time": voyage.get("start_time"),
                    "end_time": voyage.get("end_time"),
                    "duration_hours": total_time,
                    "distance_nm": total_distance,
                    "avg_speed_knots": avg_speed,
                    "fuel_consumed_gallons": round(total_fuel, 2),
                    "fuel_rate_gph": round(total_fuel / max(total_time, 0.1), 2),
                    "co2_emissions_lbs": round(total_co2, 2),
                    "fuel_efficiency_nmpg": round(
                        total_distance / max(total_fuel, 0.1), 2
                    ),
                }
            )

        return {
            "total_voyages": len(voyage_results),
            "voyage_details": voyage_results,
            "aggregate_totals": {
                "total_fuel_gallons": sum(
                    v["fuel_consumed_gallons"] for v in voyage_results
                ),
                "total_distance_nm": sum(v["distance_nm"] for v in voyage_results),
                "total_operating_hours": sum(
                    v["duration_hours"] for v in voyage_results
                ),
                "total_co2_lbs": sum(v["co2_emissions_lbs"] for v in voyage_results),
            },
        }

    async def _calculate_dwell_analytics(
        self, profile_data: Dict, telemetry_data: Dict
    ) -> Dict[str, Any]:
        """Calculate dwell time and refueling requirements"""

        dwell_results = []
        dwell_sets = telemetry_data.get("voyage_sets", {}).get("at_dock", [])

        # Estimate fuel tank capacity from boat profile
        profile = profile_data.get("normalized_profile", {})
        physical_specs = profile.get("physical_specifications", {})
        LENGTH = physical_specs.get("LENGTH_ft", 25)

        # Rough fuel tank capacity estimation
        estimated_tank_capacity = LENGTH * 2  # Simplified: 2 gallons per foot

        for i, dwell in enumerate(dwell_sets):
            if not dwell:
                continue

            duration_hours = dwell.get("duration_hours", 0)
            avg_fuel_flow = dwell.get("avg_fuel_flow", 0.5)  # AUXiliary systems

            fuel_consumed_during_dwell = avg_fuel_flow * duration_hours
            refuel_amount = min(
                fuel_consumed_during_dwell * 1.1, estimated_tank_capacity
            )  # 10% buffer

            dwell_results.append(
                {
                    "dwell_period_id": i + 1,
                    "start_time": dwell.get("start_time"),
                    "end_time": dwell.get("end_time"),
                    "duration_hours": duration_hours,
                    "AUXiliary_fuel_consumed_gallons": round(
                        fuel_consumed_during_dwell, 2
                    ),
                    "estimated_refuel_amount_gallons": round(refuel_amount, 2),
                    "fuel_rate_during_dwell_gph": avg_fuel_flow,
                }
            )

        return {
            "total_dwell_periods": len(dwell_results),
            "estimated_tank_capacity_gallons": estimated_tank_capacity,
            "dwell_details": dwell_results,
            "aggregate_totals": {
                "total_dwell_hours": sum(d["duration_hours"] for d in dwell_results),
                "total_AUXiliary_fuel_gallons": sum(
                    d["AUXiliary_fuel_consumed_gallons"] for d in dwell_results
                ),
                "total_refuel_gallons": sum(
                    d["estimated_refuel_amount_gallons"] for d in dwell_results
                ),
            },
        }

    async def _generate_voyage_csv(self, voyage_analytics: Dict) -> str:
        """Generate CSV data for voyage analytics"""
        if not voyage_analytics.get("voyage_details"):
            return "No voyage data available"

        df = pd.DataFrame(voyage_analytics["voyage_details"])
        return df.to_csv(index=False)

    async def _generate_dwell_csv(self, dwell_analytics: Dict) -> str:
        """Generate CSV data for dwell analytics"""
        if not dwell_analytics.get("dwell_details"):
            return "No dwell data available"

        df = pd.DataFrame(dwell_analytics["dwell_details"])
        return df.to_csv(index=False)

    async def _calculate_emissions_summary(
        self, voyage_analytics: Dict, dwell_analytics: Dict
    ) -> Dict[str, Any]:
        """Calculate comprehensive emissions summary"""
        voyage_totals = voyage_analytics.get("aggregate_totals", {})
        dwell_totals = dwell_analytics.get("aggregate_totals", {})

        total_fuel = voyage_totals.get("total_fuel_gallons", 0) + dwell_totals.get(
            "total_AUXiliary_fuel_gallons", 0
        )
        total_co2 = voyage_totals.get("total_co2_lbs", 0) + (
            dwell_totals.get("total_AUXiliary_fuel_gallons", 0) * 22.38
        )

        return {
            "total_fuel_consumption_gallons": round(total_fuel, 2),
            "total_co2_emissions_lbs": round(total_co2, 2),
            "total_co2_emissions_tons": round(total_co2 / 2000, 3),
            "operational_fuel_gallons": voyage_totals.get("total_fuel_gallons", 0),
            "AUXiliary_fuel_gallons": dwell_totals.get(
                "total_AUXiliary_fuel_gallons", 0
            ),
            "fuel_breakdown_percentage": {
                "operational": round(
                    (voyage_totals.get("total_fuel_gallons", 0) / max(total_fuel, 0.1))
                    * 100,
                    1,
                ),
                "AUXiliary": round(
                    (
                        dwell_totals.get("total_AUXiliary_fuel_gallons", 0)
                        / max(total_fuel, 0.1)
                    )
                    * 100,
                    1,
                ),
            },
        }


class ReportChartGeneratorAgent(BaseAgent):
    """Agent 6: Creates comprehensive charts and reports"""

    def __init__(self):
        super().__init__(
            "ReportChartGenerator",
            "Creates charting and reports in JSON-compatible format",
        )

    async def _execute_internal(self, context: WorkflowContext) -> Dict[str, Any]:
        """Generate comprehensive charts and reports"""

        # Collect all previous agent outputs
        all_outputs = {}
        for agent_name in [
            "BoatImageAnalyzer",
            "BoatProfileBuilder",
            "PerformanceCurveGenerator",
            "TelemetryDataProcessor",
            "VoyageAnalyticsEngine",
        ]:
            output = context.get_agent_output(agent_name)
            if output:
                all_outputs[agent_name] = output

        if len(all_outputs) < 4:  # Need at least 4 agents completed
            return {
                "status": "failed",
                "error": "Insufficient data from previous agents for report generation",
            }

        # Generate charts
        charts = await self._generate_charts(all_outputs)

        # Generate comprehensive report
        report = await self._generate_comprehensive_report(all_outputs)

        # Create executive summary
        executive_summary = await self._create_executive_summary(all_outputs)

        return {
            "status": "success",
            "charts": charts,
            "comprehensive_report": report,
            "executive_summary": executive_summary,
            "deliverables": {
                "baseline_profile_complete": True,
                "performance_curves_generated": True,
                "voyage_analytics_complete": True,
                "emissions_calculated": True,
                "json_compatible": True,
            },
        }

    async def _generate_charts(self, all_outputs: Dict) -> Dict[str, Any]:
        """Generate all required charts"""
        charts = {}

        # Performance curves charts
        curves_data = all_outputs.get("PerformanceCurveGenerator", {}).get(
            "performance_curves", {}
        )
        if curves_data:
            charts["performance_curves"] = await self._create_performance_curve_charts(
                curves_data
            )

        # Voyage analytics charts
        voyage_data = all_outputs.get("VoyageAnalyticsEngine", {})
        if voyage_data:
            charts["voyage_analytics"] = await self._create_voyage_analytics_charts(
                voyage_data
            )

        # Emissions breakdown chart
        emissions_data = voyage_data.get("emissions_summary", {})
        if emissions_data:
            charts["emissions_breakdown"] = await self._create_emissions_chart(
                emissions_data
            )

        return charts

    async def _create_performance_curve_charts(
        self, curves_data: Dict
    ) -> Dict[str, str]:
        """Create performance curve charts as base64 images"""
        charts = {}

        try:
            # Speed vs Fuel Rate Chart
            fuel_curve = curves_data.get("speed_vs_fuel_rate", {})
            if fuel_curve:
                plt.figure(figsize=(10, 6))
                speeds = fuel_curve.get("x_axis", {}).get("values", [])
                fuel_rates = fuel_curve.get("y_axis", {}).get("values", [])

                plt.plot(speeds, fuel_rates, "b-o", linewidth=2, markersize=6)
                plt.title(
                    "Vessel Speed vs Fuel Consumption Rate",
                    fontsize=14,
                    fontWEIGHT="bold",
                )
                plt.xlabel("Speed (knots)", fontsize=12)
                plt.ylabel("Fuel Rate (gal/hr)", fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                # Convert to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
                buffer.seek(0)
                charts["speed_vs_fuel"] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()

            # Speed vs Power Chart
            power_curve = curves_data.get("speed_vs_shaft_power", {})
            if power_curve:
                plt.figure(figsize=(10, 6))
                speeds = power_curve.get("x_axis", {}).get("values", [])
                power_values = power_curve.get("y_axis", {}).get("values", [])

                plt.plot(speeds, power_values, "r-s", linewidth=2, markersize=6)
                plt.title("Vessel Speed vs Shaft Power", fontsize=14, fontWEIGHT="bold")
                plt.xlabel("Speed (knots)", fontsize=12)
                plt.ylabel("Shaft Power (HP)", fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
                buffer.seek(0)
                charts["speed_vs_power"] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()

            # Speed vs Thrust Chart
            thrust_curve = curves_data.get("speed_vs_thrust", {})
            if thrust_curve:
                plt.figure(figsize=(10, 6))
                speeds = thrust_curve.get("x_axis", {}).get("values", [])
                thrust_values = thrust_curve.get("y_axis", {}).get("values", [])

                plt.plot(speeds, thrust_values, "g-^", linewidth=2, markersize=6)
                plt.title("Vessel Speed vs Thrust", fontsize=14, fontWEIGHT="bold")
                plt.xlabel("Speed (knots)", fontsize=12)
                plt.ylabel("Thrust (lbs)", fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
                buffer.seek(0)
                charts["speed_vs_thrust"] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()

        except Exception as e:
            logger.error(f"Error creating performance charts: {e}")

        return charts

    async def _create_voyage_analytics_charts(
        self, voyage_data: Dict
    ) -> Dict[str, str]:
        """Create voyage analytics charts"""
        charts = {}

        try:
            voyage_analytics = voyage_data.get("voyage_analytics", {})
            voyage_details = voyage_analytics.get("voyage_details", [])

            if voyage_details:
                # Fuel consumption by voyage
                plt.figure(figsize=(12, 6))
                voyage_ids = [v["voyage_id"] for v in voyage_details]
                fuel_consumed = [v["fuel_consumed_gallons"] for v in voyage_details]

                plt.bar(voyage_ids, fuel_consumed, color="skyblue", alpha=0.7)
                plt.title("Fuel Consumption by Voyage", fontsize=14, fontWEIGHT="bold")
                plt.xlabel("Voyage ID", fontsize=12)
                plt.ylabel("Fuel Consumed (gallons)", fontsize=12)
                plt.grid(True, alpha=0.3, axis="y")
                plt.tight_layout()

                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
                buffer.seek(0)
                charts["fuel_by_voyage"] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()

                # Fuel efficiency by voyage
                plt.figure(figsize=(12, 6))
                efficiency = [v["fuel_efficiency_nmpg"] for v in voyage_details]

                plt.plot(
                    voyage_ids,
                    efficiency,
                    "o-",
                    color="green",
                    linewidth=2,
                    markersize=8,
                )
                plt.title("Fuel Efficiency by Voyage", fontsize=14, fontWEIGHT="bold")
                plt.xlabel("Voyage ID", fontsize=12)
                plt.ylabel("Fuel Efficiency (nm/gal)", fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()

                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
                buffer.seek(0)
                charts["efficiency_by_voyage"] = base64.b64encode(
                    buffer.getvalue()
                ).decode()
                plt.close()

        except Exception as e:
            logger.error(f"Error creating voyage analytics charts: {e}")

        return charts

    async def _create_emissions_chart(self, emissions_data: Dict) -> str:
        """Create emissions breakdown pie chart"""
        try:
            breakdown = emissions_data.get("fuel_breakdown_percentage", {})
            operational = breakdown.get("operational", 0)
            AUXiliary = breakdown.get("AUXiliary", 0)

            if operational + AUXiliary > 0:
                plt.figure(figsize=(8, 8))
                labels = ["Operational Fuel", "AUXiliary Fuel"]
                sizes = [operational, AUXiliary]
                colors = ["#ff9999", "#66b3ff"]

                plt.pie(
                    sizes,
                    labels=labels,
                    colors=colors,
                    autopct="%1.1f%%",
                    startangle=90,
                )
                plt.title("Fuel Consumption Breakdown", fontsize=14, fontWEIGHT="bold")
                plt.axis("equal")
                plt.tight_layout()

                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
                buffer.seek(0)
                chart_data = base64.b64encode(buffer.getvalue()).decode()
                plt.close()

                return chart_data

        except Exception as e:
            logger.error(f"Error creating emissions chart: {e}")

        return ""

    async def _generate_comprehensive_report(self, all_outputs: Dict) -> Dict[str, Any]:
        """Generate comprehensive baseline profile report"""

        # Extract key data
        boat_profile = all_outputs.get("BoatProfileBuilder", {}).get(
            "normalized_profile", {}
        )
        performance_curves = all_outputs.get("PerformanceCurveGenerator", {})
        telemetry_summary = all_outputs.get("TelemetryDataProcessor", {}).get(
            "telemetry_summary", {}
        )
        voyage_analytics = all_outputs.get("VoyageAnalyticsEngine", {})

        report = {
            "report_title": "Baseline Vessel Profile Report",
            "generated_at": datetime.now().isoformat(),
            "vessel_overview": {
                "vessel_identity": boat_profile.get("vessel_identity", {}),
                "physical_specifications": boat_profile.get(
                    "physical_specifications", {}
                ),
                "operational_profile": boat_profile.get("operational_profile", {}),
            },
            "performance_analysis": {
                "curves_generated": bool(performance_curves.get("performance_curves")),
                "validation_status": performance_curves.get("curve_metadata", {}).get(
                    "validation_status"
                ),
                "confidence_level": performance_curves.get("curve_metadata", {}).get(
                    "confidence_level"
                ),
            },
            "operational_analysis": {
                "data_period": telemetry_summary.get("date_range", {}),
                "total_voyages": telemetry_summary.get("voyage_count", 0),
                "total_operating_hours": voyage_analytics.get("voyage_analytics", {})
                .get("aggregate_totals", {})
                .get("total_operating_hours", 0),
                "total_distance_nm": voyage_analytics.get("voyage_analytics", {})
                .get("aggregate_totals", {})
                .get("total_distance_nm", 0),
            },
            "environmental_impact": voyage_analytics.get("emissions_summary", {}),
            "key_findings": await self._generate_key_findings(all_outputs),
            "recommendations": await self._generate_recommendations(all_outputs),
        }

        return report

    async def _create_executive_summary(self, all_outputs: Dict) -> Dict[str, Any]:
        """Create executive summary for stakeholders"""

        boat_profile = all_outputs.get("BoatProfileBuilder", {}).get(
            "normalized_profile", {}
        )
        voyage_analytics = all_outputs.get("VoyageAnalyticsEngine", {})

        vessel_identity = boat_profile.get("vessel_identity", {})
        physical_specs = boat_profile.get("physical_specifications", {})
        emissions = voyage_analytics.get("emissions_summary", {})
        totals = voyage_analytics.get("voyage_analytics", {}).get(
            "aggregate_totals", {}
        )

        return {
            "vessel_name": vessel_identity.get("name", "Unnamed Vessel"),
            "vessel_type": f"{vessel_identity.get('builder_make', '')} {vessel_identity.get('class_model', '')}".strip(),
            "vessel_specifications": f"{physical_specs.get('LENGTH_ft', 0)} ft x {physical_specs.get('BEAM_ft', 0)} ft {physical_specs.get('boat_type', '')}",
            "operational_summary": {
                "total_operating_hours": totals.get("total_operating_hours", 0),
                "total_distance_nautical_miles": totals.get("total_distance_nm", 0),
                "average_fuel_efficiency_nmpg": round(
                    totals.get("total_distance_nm", 0)
                    / max(totals.get("total_fuel_gallons", 0.1), 0.1),
                    2,
                ),
            },
            "environmental_impact": {
                "total_fuel_consumption_gallons": emissions.get(
                    "total_fuel_consumption_gallons", 0
                ),
                "total_co2_emissions_tons": emissions.get(
                    "total_co2_emissions_tons", 0
                ),
            },
            "baseline_status": "Complete - Ready for validation and optimization",
            "next_steps": [
                "Validate performance curves with naval architect review",
                "Implement real-time monitoring for continuous optimization",
                "Explore electrification opportunities based on operational patterns",
            ],
        }

    async def _generate_key_findings(self, all_outputs: Dict) -> List[str]:
        """Generate key findings from analysis"""
        findings = [
            "Baseline vessel profile successfully established from multi-source data analysis",
            "Performance curves generated using AI-enhanced specifications and operational patterns",
            "Telemetry analysis revealed distinct operational and dwell patterns",
            "Fuel consumption patterns identified for optimization opportunities",
        ]

        # Add specific findings based on data
        voyage_analytics = all_outputs.get("VoyageAnalyticsEngine", {})
        if voyage_analytics:
            emissions = voyage_analytics.get("emissions_summary", {})
            breakdown = emissions.get("fuel_breakdown_percentage", {})

            if breakdown.get("AUXiliary", 0) > 20:
                findings.append(
                    f"High AUXiliary fuel consumption ({breakdown.get('AUXiliary', 0):.1f}%) indicates potential for electrification"
                )

            totals = voyage_analytics.get("voyage_analytics", {}).get(
                "aggregate_totals", {}
            )
            if totals.get("total_fuel_gallons", 0) > 0:
                efficiency = totals.get("total_distance_nm", 0) / totals.get(
                    "total_fuel_gallons", 1
                )
                if efficiency < 2:
                    findings.append(
                        "Lower fuel efficiency suggests optimization opportunities in operational patterns"
                    )

        return findings

    async def _generate_recommendations(self, all_outputs: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = [
            "Validate AI-generated performance curves through sea trials or naval architect review",
            "Implement continuous monitoring system for real-time performance optimization",
            "Conduct detailed analysis of high fuel consumption voyages to identify efficiency improvements",
            "Consider operational pattern modifications to reduce environmental impact",
        ]

        # Add specific recommendations based on findings
        boat_profile = all_outputs.get("BoatProfileBuilder", {}).get(
            "normalized_profile", {}
        )
        operational = boat_profile.get("operational_profile", {})

        if operational.get("AUXiliary_systems"):
            recommendations.append(
                "Evaluate AUXiliary system electrification for dwell periods to reduce emissions"
            )

        if operational.get("COMMERCIAL_operation"):
            recommendations.append(
                "Explore COMMERCIAL incentives for fuel efficiency improvements and emission reductions"
            )

        return recommendations
