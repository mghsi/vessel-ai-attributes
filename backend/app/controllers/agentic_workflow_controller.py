"""
Agentic Workflow Controller

Handles API endpoints for the multi-agent boat profiling workflow system.
"""

import logging
import asyncio
from functools import wraps
from flask import request, jsonify, current_app, Response
from app.services.agentic_workflow import WorkflowOrchestrator

logger = logging.getLogger(__name__)


def async_route(f):
    """Decorator to handle async functions in Flask routes"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()

    return wrapper


class AgenticWorkflowController:
    """Controller for agentic workflow operations"""

    @staticmethod
    @async_route
    async def start_workflow():
        """Start a new agentic workflow session"""
        try:
            # Validate request
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided", "code": "REQ001"}), 400

            # Extract workflow input
            workflow_input = {}

            # Handle image upload path
            if "image_data" in data:
                workflow_input["image_data"] = data["image_data"]
                workflow_input["brand"] = data.get("brand", "")
                workflow_input["model"] = data.get("model", "")

            # Handle manual input path
            elif "manual_data" in data:
                manual_data = data["manual_data"]
                required_fields = ["builder_make", "class_model"]

                # Validate required fields
                missing_fields = [
                    field for field in required_fields if not manual_data.get(field)
                ]
                if missing_fields:
                    return (
                        jsonify(
                            {
                                "error": f'Missing required fields: {", ".join(missing_fields)}',
                                "code": "VAL001",
                                "required_fields": required_fields,
                            }
                        ),
                        400,
                    )

                workflow_input["manual_data"] = manual_data

            else:
                return (
                    jsonify(
                        {
                            "error": "Either image_data or manual_data must be provided",
                            "code": "REQ002",
                        }
                    ),
                    400,
                )

            # Initialize workflow orchestrator
            orchestrator = WorkflowOrchestrator(
                github_pat=current_app.config["GITHUB_PAT"],
                api_url=current_app.config["GITHUB_API_URL"],
                model=current_app.config["DEFAULT_MODEL"],
            )

            # Start workflow
            session_id = await orchestrator.start_workflow(workflow_input)

            return (
                jsonify(
                    {
                        "status": "success",
                        "session_id": session_id,
                        "message": "Agentic workflow started successfully",
                        "next_action": "execute_step",
                        "total_steps": 6,
                    }
                ),
                200,
            )

        except Exception as e:
            logger.error(f"Error starting workflow: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Failed to start workflow",
                        "code": "SYS001",
                        "details": str(e),
                    }
                ),
                500,
            )

    @staticmethod
    @async_route
    async def execute_workflow_step():
        """Execute the next step in an active workflow"""
        try:
            data = request.get_json()
            if not data or "session_id" not in data:
                return jsonify({"error": "Session ID required", "code": "REQ003"}), 400

            session_id = data["session_id"]

            # Initialize orchestrator
            orchestrator = WorkflowOrchestrator(
                github_pat=current_app.config["GITHUB_PAT"],
                api_url=current_app.config["GITHUB_API_URL"],
                model=current_app.config["DEFAULT_MODEL"],
            )

            # Execute next step
            result = await orchestrator.execute_next_step(session_id)

            if "error" in result:
                return jsonify(result), 400

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error executing workflow step: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Failed to execute workflow step",
                        "code": "SYS002",
                        "details": str(e),
                    }
                ),
                500,
            )

    @staticmethod
    def get_workflow_status():
        """Get the current status of a workflow session"""
        try:
            session_id = request.args.get("session_id")
            if not session_id:
                return jsonify({"error": "Session ID required", "code": "REQ004"}), 400

            # Initialize orchestrator
            orchestrator = WorkflowOrchestrator(
                github_pat=current_app.config["GITHUB_PAT"],
                api_url=current_app.config["GITHUB_API_URL"],
                model=current_app.config["DEFAULT_MODEL"],
            )

            # Get status
            status = orchestrator.get_workflow_status(session_id)

            if "error" in status:
                return jsonify(status), 404

            return jsonify(status), 200

        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Failed to get workflow status",
                        "code": "SYS003",
                        "details": str(e),
                    }
                ),
                500,
            )

    @staticmethod
    @async_route
    async def execute_full_workflow():
        """Execute the complete workflow from start to finish"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided", "code": "REQ005"}), 400

            # Start workflow
            orchestrator = WorkflowOrchestrator(
                github_pat=current_app.config["GITHUB_PAT"],
                api_url=current_app.config["GITHUB_API_URL"],
                model=current_app.config["DEFAULT_MODEL"],
            )

            # Extract workflow input (same as start_workflow)
            workflow_input = {}

            if "image_data" in data:
                workflow_input["image_data"] = data["image_data"]
                workflow_input["brand"] = data.get("brand", "")
                workflow_input["model"] = data.get("model", "")
            elif "manual_data" in data:
                workflow_input["manual_data"] = data["manual_data"]
            else:
                return (
                    jsonify(
                        {
                            "error": "Either image_data or manual_data must be provided",
                            "code": "REQ006",
                        }
                    ),
                    400,
                )

            # Start workflow
            session_id = await orchestrator.start_workflow(workflow_input)

            # Execute all steps
            results = []
            step_count = 0
            max_steps = 6

            while step_count < max_steps:
                step_result = await orchestrator.execute_next_step(session_id)

                if "error" in step_result:
                    return (
                        jsonify(
                            {
                                "error": f"Workflow failed at step {step_count + 1}",
                                "step_result": step_result,
                                "completed_steps": results,
                            }
                        ),
                        500,
                    )

                results.append(
                    {
                        "step": step_count + 1,
                        "agent_name": step_result.get("agent_name"),
                        "result": step_result.get("agent_result"),
                        "status": step_result.get("status"),
                    }
                )

                step_count += 1

                if step_result.get("status") == "completed":
                    break

            # Get final workflow status
            final_status = orchestrator.get_workflow_status(session_id)

            return (
                jsonify(
                    {
                        "status": "success",
                        "session_id": session_id,
                        "message": "Complete workflow executed successfully",
                        "step_results": results,
                        "final_status": final_status,
                        "total_steps_completed": len(results),
                    }
                ),
                200,
            )

        except Exception as e:
            logger.error(f"Error executing full workflow: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Failed to execute full workflow",
                        "code": "SYS004",
                        "details": str(e),
                    }
                ),
                500,
            )

    @staticmethod
    @async_route
    async def download_performance_csv():
        """Download performance curves as CSV file"""
        try:
            session_id = request.args.get("session_id")
            format_type = request.args.get("format", "holtrop-mennen")

            if not session_id:
                return (
                    jsonify({"error": "Session ID is required", "code": "REQ001"}),
                    400,
                )

            # Get GitHub settings
            github_pat = current_app.config.get("GITHUB_PAT")
            api_url = current_app.config.get("GITHUB_MODELS_API_URL")
            model = current_app.config.get("GITHUB_MODELS_MODEL")

            orchestrator = WorkflowOrchestrator(github_pat, api_url, model)

            # Get workflow status and check if PerformanceCurveGenerator completed
            workflow_status = orchestrator.get_workflow_status(session_id)

            if not workflow_status or workflow_status.get("status") == "not_found":
                return (
                    jsonify({"error": "Workflow session not found", "code": "SESS001"}),
                    404,
                )

            # Check if performance curves are available
            agent_results = workflow_status.get("agent_results", {})
            perf_agent_result = agent_results.get("PerformanceCurveGenerator", {})

            if not perf_agent_result or perf_agent_result.get("status") != "success":
                return (
                    jsonify(
                        {
                            "error": "Performance curves not available. Run workflow first.",
                            "code": "WORK001",
                        }
                    ),
                    400,
                )

            # Get CSV data
            csv_data = perf_agent_result.get("csv_data")

            if not csv_data:
                return (
                    jsonify({"error": "CSV data not available", "code": "DATA001"}),
                    404,
                )

            # Create response with proper headers for CSV download
            filename = f"vessel_performance_curves_{session_id[:8]}.csv"

            response = Response(
                csv_data,
                mimetype="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "text/csv; charset=utf-8",
                },
            )

            return response

        except Exception as e:
            logger.error(f"Error downloading performance CSV: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Failed to download performance curves",
                        "code": "SYS005",
                        "details": str(e),
                    }
                ),
                500,
            )


# Controller methods are already decorated with @async_route
