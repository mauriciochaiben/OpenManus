"""
Workflow Service for orchestrating complex workflows in OpenManus.

This module implements the WorkflowService, responsible for orchestrating
workflow execution using PlannerAgent, ToolUserAgent, and EventBus to
decompose tasks, execute steps, and publish progress events.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.infrastructure.messaging.event_bus import Event, EventBus
from app.roles.planner_agent import PlannerAgent
from app.roles.tool_user_agent import ToolUserAgent

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStartedEvent(Event):
    """Event fired when a workflow starts execution"""

    workflow_id: str
    initial_task: str


@dataclass
class WorkflowStepStartedEvent(Event):
    """Event fired when a workflow step starts"""

    workflow_id: str
    step_number: int
    step_description: str
    step_type: str  # 'tool' or 'generic'


@dataclass
class WorkflowStepCompletedEvent(Event):
    """Event fired when a workflow step completes"""

    workflow_id: str
    step_number: int
    step_description: str
    step_type: str
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None


@dataclass
class WorkflowCompletedEvent(Event):
    """Event fired when a workflow completes"""

    workflow_id: str
    success: bool
    total_steps: int
    completed_steps: int
    final_result: Optional[Dict] = None
    error: Optional[str] = None


class WorkflowService:
    """Service for orchestrating workflow execution.

    The WorkflowService coordinates the execution of complex workflows by:
    1. Using PlannerAgent to decompose tasks into steps
    2. Classifying steps as tool-based or generic tasks
    3. Executing tool-based steps using ToolUserAgent
    4. Publishing workflow progress events via EventBus
    5. Returning comprehensive workflow results
    """

    # Keywords that indicate a step requires tool execution
    TOOL_KEYWORDS = {
        "search",
        "web_search",
        "google",
        "lookup",
        "find",
        "query",
        "scrape",
        "crawl",
        "fetch",
        "download",
        "retrieve",
        "api",
        "call",
        "request",
        "http",
        "post",
        "get",
        "file",
        "read",
        "write",
        "save",
        "load",
        "database",
        "sql",
        "query",
        "insert",
        "update",
        "delete",
        "email",
        "send",
        "notify",
        "alert",
        "message",
        "calculate",
        "compute",
        "process",
        "convert",
        "transform",
    }

    def __init__(
        self,
        planner_agent: Optional[PlannerAgent] = None,
        tool_user_agent: Optional[ToolUserAgent] = None,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        """Initialize the WorkflowService with required dependencies.

        Args:
            planner_agent: PlannerAgent instance for task decomposition
            tool_user_agent: ToolUserAgent instance for tool execution
            event_bus: EventBus instance for publishing workflow events
        """
        self.planner_agent = planner_agent or PlannerAgent()
        self.tool_user_agent = tool_user_agent or ToolUserAgent()
        self.event_bus = event_bus

        # Generate unique workflow ID
        import uuid

        self._current_workflow_id = None

        logger.info("WorkflowService initialized")

    async def start_simple_workflow(self, initial_task: str) -> Dict:
        """Start a simple workflow execution.

        Args:
            initial_task: The initial task description to decompose and execute

        Returns:
            Dict: Workflow execution results containing:
                 - workflow_id: Unique identifier for the workflow
                 - status: "success" or "error"
                 - steps_executed: Number of steps successfully executed
                 - total_steps: Total number of planned steps
                 - results: List of step execution results
                 - final_result: Aggregated final workflow result
                 - error: Error message if workflow failed
        """
        import uuid

        workflow_id = str(uuid.uuid4())
        self._current_workflow_id = workflow_id

        logger.info(f"Starting workflow {workflow_id} with task: {initial_task}")

        try:
            # Publish workflow started event
            if self.event_bus:
                await self.event_bus.publish(
                    WorkflowStartedEvent(
                        workflow_id=workflow_id, initial_task=initial_task
                    )
                )

            # Step 1: Use PlannerAgent to decompose the task
            decomposition_result = await self._decompose_task(initial_task)
            if decomposition_result["status"] != "success":
                return self._create_error_result(
                    workflow_id,
                    f"Task decomposition failed: {decomposition_result.get('message', 'Unknown error')}",
                    0,
                    0,
                )

            steps = decomposition_result["steps"]
            total_steps = len(steps)

            logger.info(f"Workflow {workflow_id} decomposed into {total_steps} steps")

            # Step 2: Execute each step
            step_results = []
            completed_steps = 0

            for step_number, step_description in enumerate(steps, 1):
                try:
                    # Classify step type
                    step_type = self._classify_step(step_description)

                    # Publish step started event
                    if self.event_bus:
                        await self.event_bus.publish(
                            WorkflowStepStartedEvent(
                                workflow_id=workflow_id,
                                step_number=step_number,
                                step_description=step_description,
                                step_type=step_type,
                            )
                        )

                    # Execute step based on type
                    if step_type == "tool":
                        step_result = await self._execute_tool_step(step_description)
                    else:
                        step_result = await self._execute_generic_step(step_description)

                    step_results.append(
                        {
                            "step_number": step_number,
                            "description": step_description,
                            "type": step_type,
                            "success": step_result.get("success", False),
                            "result": step_result.get("result"),
                            "message": step_result.get("message", ""),
                        }
                    )

                    # Publish step completed event
                    if self.event_bus:
                        await self.event_bus.publish(
                            WorkflowStepCompletedEvent(
                                workflow_id=workflow_id,
                                step_number=step_number,
                                step_description=step_description,
                                step_type=step_type,
                                success=step_result.get("success", False),
                                result=step_result.get("result"),
                                error=(
                                    step_result.get("message")
                                    if not step_result.get("success")
                                    else None
                                ),
                            )
                        )

                    if step_result.get("success"):
                        completed_steps += 1
                    else:
                        logger.warning(
                            f"Step {step_number} failed in workflow {workflow_id}: "
                            f"{step_result.get('message', 'Unknown error')}"
                        )

                except Exception as e:
                    error_msg = f"Error executing step {step_number}: {str(e)}"
                    logger.error(error_msg)

                    step_results.append(
                        {
                            "step_number": step_number,
                            "description": step_description,
                            "type": "unknown",
                            "success": False,
                            "result": None,
                            "message": error_msg,
                        }
                    )

                    # Publish step failed event
                    if self.event_bus:
                        await self.event_bus.publish(
                            WorkflowStepCompletedEvent(
                                workflow_id=workflow_id,
                                step_number=step_number,
                                step_description=step_description,
                                step_type="unknown",
                                success=False,
                                error=error_msg,
                            )
                        )

            # Step 3: Create final result
            final_result = self._aggregate_results(step_results)
            workflow_success = completed_steps == total_steps

            result = {
                "workflow_id": workflow_id,
                "status": "success" if workflow_success else "partial_success",
                "steps_executed": completed_steps,
                "total_steps": total_steps,
                "results": step_results,
                "final_result": final_result,
                "metadata": {
                    "initial_task": initial_task,
                    "execution_summary": f"{completed_steps}/{total_steps} steps completed successfully",
                },
            }

            # Publish workflow completed event
            if self.event_bus:
                await self.event_bus.publish(
                    WorkflowCompletedEvent(
                        workflow_id=workflow_id,
                        success=workflow_success,
                        total_steps=total_steps,
                        completed_steps=completed_steps,
                        final_result=final_result,
                    )
                )

            logger.info(
                f"Workflow {workflow_id} completed: {completed_steps}/{total_steps} steps successful"
            )

            return result

        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(f"Workflow {workflow_id} failed: {error_msg}")

            # Publish workflow failed event
            if self.event_bus:
                await self.event_bus.publish(
                    WorkflowCompletedEvent(
                        workflow_id=workflow_id,
                        success=False,
                        total_steps=0,
                        completed_steps=0,
                        error=error_msg,
                    )
                )

            return self._create_error_result(workflow_id, error_msg, 0, 0)

    async def _decompose_task(self, task: str) -> Dict:
        """Decompose a task using the PlannerAgent.

        Args:
            task: The task description to decompose

        Returns:
            Dict: Decomposition result from PlannerAgent
        """
        try:
            return await self.planner_agent.run(
                {
                    "input": task,
                    "context": "Simple workflow execution",
                    "complexity": "medium",
                }
            )
        except Exception as e:
            logger.error(f"Task decomposition failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Task decomposition failed: {str(e)}",
                "steps": [],
            }

    def _classify_step(self, step_description: str) -> str:
        """Classify a step as requiring tools or being a generic task.

        Args:
            step_description: The description of the step to classify

        Returns:
            str: "tool" if step requires tool execution, "generic" otherwise
        """
        step_lower = step_description.lower()

        # Check if any tool keywords are present in the step description
        for keyword in self.TOOL_KEYWORDS:
            if keyword in step_lower:
                return "tool"

        return "generic"

    async def _execute_tool_step(self, step_description: str) -> Dict:
        """Execute a tool-based step using ToolUserAgent.

        Args:
            step_description: Description of the step to execute

        Returns:
            Dict: Execution result
        """
        try:
            # Extract potential tool name and arguments from step description
            tool_info = self._extract_tool_info(step_description)

            # Execute using ToolUserAgent
            return await self.tool_user_agent.run(tool_info)

        except Exception as e:
            error_msg = f"Tool step execution failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "result": None, "message": error_msg}

    async def _execute_generic_step(self, step_description: str) -> Dict:
        """Execute a generic step that doesn't require specific tools.

        Args:
            step_description: Description of the step to execute

        Returns:
            Dict: Execution result (simulated for generic steps)
        """
        try:
            # Simulate generic step execution
            await asyncio.sleep(0.1)  # Simulate processing time

            return {
                "success": True,
                "result": {
                    "step_type": "generic",
                    "description": step_description,
                    "status": "completed",
                    "output": f"Generic step completed: {step_description}",
                },
                "message": "Generic step executed successfully",
            }

        except Exception as e:
            error_msg = f"Generic step execution failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "result": None, "message": error_msg}

    def _extract_tool_info(self, step_description: str) -> Dict:
        """Extract tool name and arguments from step description.

        Args:
            step_description: The step description to parse

        Returns:
            Dict: Tool execution details for ToolUserAgent
        """
        # Simple extraction logic - can be enhanced with NLP
        step_lower = step_description.lower()

        # Default tool configuration
        tool_info = {
            "tool_name": "generic_tool",
            "arguments": {"description": step_description, "action": "execute"},
            "timeout": 30,
            "context": {"workflow_id": self._current_workflow_id, "step_type": "tool"},
        }

        # Try to identify specific tools based on keywords
        if any(
            keyword in step_lower
            for keyword in ["search", "web_search", "google", "lookup"]
        ):
            tool_info.update(
                {
                    "tool_name": "web_search",
                    "arguments": {
                        "query": step_description.replace("search for", "")
                        .replace("lookup", "")
                        .strip(),
                        "max_results": 5,
                    },
                }
            )
        elif any(keyword in step_lower for keyword in ["file", "read", "write"]):
            tool_info.update(
                {
                    "tool_name": "file_handler",
                    "arguments": {
                        "operation": "read" if "read" in step_lower else "write",
                        "description": step_description,
                    },
                }
            )

        return tool_info

    def _aggregate_results(self, step_results: List[Dict]) -> Dict:
        """Aggregate step results into a final workflow result.

        Args:
            step_results: List of individual step execution results

        Returns:
            Dict: Aggregated final result
        """
        successful_steps = [r for r in step_results if r.get("success")]
        failed_steps = [r for r in step_results if not r.get("success")]

        return {
            "workflow_summary": {
                "total_steps": len(step_results),
                "successful_steps": len(successful_steps),
                "failed_steps": len(failed_steps),
                "success_rate": (
                    len(successful_steps) / len(step_results) if step_results else 0
                ),
            },
            "successful_results": [
                r["result"] for r in successful_steps if r.get("result")
            ],
            "failed_results": [r["message"] for r in failed_steps],
            "overall_status": "success" if not failed_steps else "partial_success",
        }

    def _create_error_result(
        self,
        workflow_id: str,
        error_message: str,
        completed_steps: int,
        total_steps: int,
    ) -> Dict:
        """Create a standardized error result.

        Args:
            workflow_id: The workflow identifier
            error_message: Description of the error
            completed_steps: Number of successfully completed steps
            total_steps: Total number of planned steps

        Returns:
            Dict: Standardized error result
        """
        return {
            "workflow_id": workflow_id,
            "status": "error",
            "steps_executed": completed_steps,
            "total_steps": total_steps,
            "results": [],
            "final_result": None,
            "error": error_message,
            "metadata": {"error_occurred": True, "error_message": error_message},
        }
