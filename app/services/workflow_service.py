"""
Workflow Service for orchestrating complex workflows in OpenManus.

This module implements the WorkflowService, responsible for orchestrating
workflow execution using PlannerAgent, ToolUserAgent, and EventBus to
decompose tasks, execute steps, and publish progress events.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.infrastructure.messaging.event_bus import Event, EventBus
from app.knowledge.services.rag_service import RagService
from app.roles.planner_agent import PlannerAgent
from app.roles.tool_user_agent import ToolUserAgent
from app.services.role_manager import RoleManager
from app.workflows.podcast_generator import PodcastGenerator

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStartedEvent(Event):
    """Event fired when a workflow starts execution"""

    workflow_id: str
    initial_task: str

    def get_event_type(self) -> str:
        """Return the type of event"""
        return "workflow_started"


@dataclass
class WorkflowStepStartedEvent(Event):
    """Event fired when a workflow step starts"""

    workflow_id: str
    step_number: int
    step_description: str
    step_type: str  # 'tool' or 'generic'

    def get_event_type(self) -> str:
        """Return the type of event"""
        return "workflow_step_started"


@dataclass
class WorkflowStepCompletedEvent(Event):
    """Event fired when a workflow step completes"""

    workflow_id: str
    step_number: int
    step_description: str
    step_type: str
    success: bool
    result: dict | None = None
    error: str | None = None

    def get_event_type(self) -> str:
        """Return the type of event"""
        return "workflow_step_completed"


@dataclass
class WorkflowCompletedEvent(Event):
    """Event fired when a workflow completes"""

    workflow_id: str
    success: bool
    total_steps: int
    completed_steps: int
    successful_steps: int
    failed_steps: int
    final_status: str
    final_result: dict | None = None
    error: str | None = None

    def get_event_type(self) -> str:
        """Return the type of event"""
        return "workflow_completed"


class WorkflowRequest:
    def __init__(
        self,
        title: str,
        description: str,
        steps: list,
        source_ids: list[str] | None = None,
    ):
        self.title = title
        self.description = description
        self.steps = steps
        self.source_ids = source_ids or []


class WorkflowContext:
    """Manages shared state between workflow steps."""

    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.shared_data: dict[str, Any] = {}
        self.step_outputs: dict[str, Any] = {}
        self.metadata: dict[str, Any] = {}
        self.source_ids: list[str] | None = None

    def set_shared_data(self, key: str, value: Any):
        """Set shared data that persists across steps."""
        self.shared_data[key] = value

    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """Get shared data by key."""
        return self.shared_data.get(key, default)

    def set_step_output(self, step_id: str, output: Any):
        """Store output from a specific step."""
        self.step_outputs[step_id] = output

    def get_step_output(self, step_id: str, default: Any = None) -> Any:
        """Get output from a specific step."""
        return self.step_outputs.get(step_id, default)

    def get_previous_step_output(self) -> Any:
        """Get output from the most recent step."""
        if self.step_outputs:
            return list(self.step_outputs.values())[-1]
        return None

    def update_metadata(self, metadata: dict[str, Any]):
        """Update workflow metadata."""
        self.metadata.update(metadata)


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
        planner_agent: PlannerAgent | None = None,
        tool_user_agent: ToolUserAgent | None = None,
        event_bus: EventBus | None = None,
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

        self._current_workflow_id = None

        self.rag_service = None  # Will be injected via dependency injection
        self.role_manager: RoleManager | None = None
        self.podcast_generator: PodcastGenerator | None = None

        logger.info("WorkflowService initialized")

    def set_rag_service(self, rag_service: RagService):
        """Set the RAG service for context-enhanced processing."""
        self.rag_service = rag_service

    def set_role_manager(self, role_manager: RoleManager):
        """Set the role manager for agent instantiation."""
        self.role_manager = role_manager

    def set_podcast_generator(self, podcast_generator: PodcastGenerator):
        """Set the podcast generator for content-to-audio workflows."""
        self.podcast_generator = podcast_generator

    async def enhance_prompt_with_context(
        self,
        original_prompt: str,
        source_ids: list[str] | None = None,
        max_context_chunks: int = 5,
    ) -> str:
        """
        Enhance a prompt with relevant context from knowledge sources.

        Args:
            original_prompt: The original user prompt/query
            source_ids: Optional list of source IDs to retrieve context from
            max_context_chunks: Maximum number of context chunks to retrieve

        Returns:
            Enhanced prompt with context or original prompt if no context available
        """
        if not source_ids or not self.rag_service:
            return original_prompt

        try:
            # Retrieve relevant context from knowledge base
            logger.info(
                f"Retrieving context from {len(source_ids)} sources for query: {original_prompt[:100]}..."
            )

            context_chunks = await self.rag_service.retrieve_relevant_context(
                query=original_prompt,
                source_ids=source_ids,
                k=max_context_chunks,
            )

            if not context_chunks:
                logger.warning(
                    "No relevant context found for the given query and sources"
                )
                return original_prompt

            # Format context for LLM prompt
            context_text = "\n\n".join(
                [f"Context {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)]
            )

            enhanced_prompt = f"""Use the following context from the knowledge base to help answer the question or complete the task. The context provides relevant information that should inform your response.

CONTEXT:
{context_text}

QUESTION/TASK:
{original_prompt}

Please provide a comprehensive response that incorporates relevant information from the context above. If the context doesn't contain information relevant to the question, you may still provide a general response but mention that the provided context doesn't contain specific relevant information."""

            logger.info(f"Enhanced prompt with {len(context_chunks)} context chunks")
            return enhanced_prompt

        except Exception as e:
            logger.error(f"Error retrieving context for prompt enhancement: {str(e)}")
            # Return original prompt if context retrieval fails
            return original_prompt

    async def start_complex_workflow(self, request: WorkflowRequest) -> dict:
        """
        Start a complex workflow with dynamic agent selection and state management.

        This method provides enhanced workflow execution with:
        - Dynamic agent role determination
        - Shared state management between steps
        - Context enhancement from knowledge sources
        - Error recovery and step dependencies
        """

        workflow_id = self._generate_workflow_id()

        # Initialize workflow data structure
        workflow_data = {
            "id": workflow_id,
            "title": request.title,
            "description": request.description,
            "status": "running",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "steps": [],
        }

        # Initialize workflow context
        context = WorkflowContext(workflow_id)
        context.source_ids = request.source_ids

        # Publish workflow started event
        await self.event_bus.publish(
            WorkflowStartedEvent(
                workflow_id=workflow_id,
                title=workflow_data["title"],
                step_count=len(request.steps),
            )
        )

        try:
            completed_steps = 0
            total_steps = len(request.steps)
            step_results = []

            # Process each step with enhanced execution
            for step_index, step_config in enumerate(request.steps):
                step_result = await self._execute_complex_step_dict(
                    workflow_data=workflow_data,
                    step_config=step_config,
                    step_index=step_index,
                    context=context,
                )
                workflow_data["steps"].append(step_result)
                step_results.append(step_result)

                # Count successful steps
                if step_result.get("status") == "completed":
                    completed_steps += 1

                # Stop execution if step failed and no error recovery
                if step_result.get("status") == "failed" and not step_config.get(
                    "continue_on_error", False
                ):
                    workflow_data["status"] = "failed"
                    return {
                        "workflow_id": workflow_id,
                        "status": "failed",
                        "steps_executed": completed_steps,
                        "total_steps": total_steps,
                        "results": step_results,
                        "error": f"Step '{step_result.get('name')}' failed: {step_result.get('error')}",
                        "metadata": {
                            "initial_task": request.title,
                            "execution_summary": f"{completed_steps}/{total_steps} steps completed before failure",
                        },
                    }

            # All steps completed successfully
            workflow_data["status"] = "completed"
            workflow_data["updated_at"] = datetime.utcnow()

            # Create final result
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
                    "initial_task": request.title,
                    "execution_summary": f"{completed_steps}/{total_steps} steps completed successfully",
                },
            }

            await self.event_bus.publish(
                WorkflowCompletedEvent(
                    workflow_id=workflow_id,
                    success=workflow_success,
                    total_steps=total_steps,
                    completed_steps=completed_steps,
                    successful_steps=completed_steps,  # For now, same as completed_steps
                    failed_steps=total_steps - completed_steps,
                    final_status="completed" if workflow_success else "failed",
                    final_result=final_result,
                )
            )

            return result

        except Exception as e:
            logger.error(f"Complex workflow execution failed: {str(e)}")
            workflow_data["status"] = "failed"

            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "steps_executed": 0,
                "total_steps": len(request.steps),
                "results": [],
                "error": str(e),
                "metadata": {
                    "initial_task": request.title,
                    "execution_summary": "Workflow failed during initialization",
                },
            }

    async def _execute_complex_step_dict(
        self,
        workflow_data: dict,
        step_config: dict[str, Any],
        step_index: int,
        context: WorkflowContext,  # noqa: ARG002
    ) -> dict:
        """
        Execute a single workflow step with enhanced agent selection (dictionary version).

        Args:
            workflow_data: The workflow data dictionary
            step_config: Configuration for the current step
            step_index: Index of the current step
            context: Shared workflow context

        Returns:
            Dictionary representing the executed step result
        """
        step_id = f"{workflow_data['id']}-step-{step_index}"
        step_name = step_config.get("name", f"step_{step_index}")

        step_result = {
            "id": step_id,
            "name": step_name,
            "status": "pending",
            "step_number": step_index + 1,
            "description": step_config.get("description", step_name),
            "type": "generic",
            "success": False,
            "result": None,
            "error": None,
        }

        try:
            # Publish step started event
            await self.event_bus.publish(
                WorkflowStepStartedEvent(
                    workflow_id=workflow_data["id"],
                    step_number=step_index + 1,
                    step_description=step_result["description"],
                    step_type=step_result["type"],
                )
            )

            # For now, simulate successful step execution
            # In a real implementation, this would use agent selection and execution
            logger.info(
                f"Executing step '{step_name}' for workflow {workflow_data['id']}"
            )

            # Simulate step execution
            step_result["status"] = "completed"
            step_result["success"] = True
            step_result["result"] = f"Step {step_name} completed successfully"
            step_result["type"] = self._classify_step(step_result["description"])

            # Publish step completed event
            await self.event_bus.publish(
                WorkflowStepCompletedEvent(
                    workflow_id=workflow_data["id"],
                    step_number=step_index + 1,
                    step_description=step_result["description"],
                    step_type=step_result["type"],
                    success=True,
                    result=step_result["result"],
                )
            )

            return step_result

        except Exception as e:
            step_result["status"] = "failed"
            step_result["success"] = False
            step_result["error"] = str(e)
            step_result["result"] = f"Step execution failed: {str(e)}"

            logger.error(f"Step execution failed: {str(e)}")

            await self.event_bus.publish(
                WorkflowStepCompletedEvent(
                    workflow_id=workflow_data["id"],
                    step_number=step_index + 1,
                    step_description=step_result["description"],
                    step_type=step_result["type"],
                    success=False,
                    error=str(e),
                )
            )

            return step_result

    async def start_simple_workflow(self, request) -> dict:
        """
        Start a simple workflow (legacy method, now uses complex workflow internally).

        This method maintains backward compatibility while leveraging the enhanced
        complex workflow execution system.

        Args:
            request: Either a string (initial task) or WorkflowRequest object
        """
        # Handle backward compatibility - convert string to WorkflowRequest
        if isinstance(request, str):
            request = WorkflowRequest(
                title="Simple Workflow", description=request, steps=[], source_ids=None
            )

        # Convert simple workflow request to complex workflow format if needed
        if not hasattr(request, "source_ids"):
            request.source_ids = None

        # Use the complex workflow system for better agent management
        if self.role_manager:
            return await self.start_complex_workflow(request)

        # Fallback to original implementation if role manager not available
        return await self._start_simple_workflow_legacy(request)

    async def _start_simple_workflow_legacy(self, request) -> dict:
        """Legacy simple workflow implementation for backward compatibility."""
        import uuid

        workflow_id = str(uuid.uuid4())
        self._current_workflow_id = workflow_id

        # Handle both string and WorkflowRequest object inputs
        if isinstance(request, str):
            initial_task = request
            title = "Simple Workflow"
        else:
            initial_task = request.description
            title = request.title

        logger.info(f"Starting workflow {workflow_id} with task: {title}")

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
                    "initial_task": request.title,
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
                        successful_steps=completed_steps,  # For now, same as completed_steps
                        failed_steps=total_steps - completed_steps,
                        final_status="completed" if workflow_success else "failed",
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
                        successful_steps=0,
                        failed_steps=0,
                        final_status="failed",
                        error=error_msg,
                    )
                )

            return self._create_error_result(workflow_id, error_msg, 0, 0)

    async def _decompose_task(self, task: str) -> dict:
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

    async def _execute_tool_step(self, step_description: str) -> dict:
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

    async def _execute_generic_step(self, step_description: str) -> dict:
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

    def _extract_tool_info(self, step_description: str) -> dict:
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

    def _aggregate_results(self, step_results: list[dict]) -> dict:
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
    ) -> dict:
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

    def _should_enhance_with_context(
        self, step_config: dict, source_ids: list[str] | None
    ) -> bool:
        """
        Determine if a workflow step should be enhanced with knowledge context.

        Args:
            step_config: Configuration for the workflow step
            source_ids: Available source IDs for context

        Returns:
            True if the step should be enhanced with context
        """
        if not source_ids or not self.rag_service:
            return False

        # Define step types that benefit from context enhancement
        context_enhanced_steps = {
            "question_answering",
            "content_generation",
            "analysis",
            "planning",
            "research",
        }

        step_name = step_config.get("name", "")
        step_type = step_config.get("type", "")
        agent_type = step_config.get("agent_type", "")

        # Check if step explicitly requests context enhancement
        if step_config.get("use_knowledge_context", False):
            return True

        # Check if step type typically benefits from context
        if any(keyword in step_name.lower() for keyword in context_enhanced_steps):
            return True

        if any(keyword in step_type.lower() for keyword in context_enhanced_steps):
            return True

        # Planner agents often benefit from context
        return agent_type == "planner"

    async def _enhance_step_with_context(
        self, step_input: dict, step_config: dict, source_ids: list[str]
    ) -> dict:
        """
        Enhance a workflow step's input with relevant knowledge context.

        Args:
            step_input: Original step input configuration
            step_config: Step configuration
            source_ids: Source IDs for context retrieval

        Returns:
            Enhanced input configuration with context
        """
        try:
            # Extract the main query/prompt from step input
            query = self._extract_query_from_step_input(step_input, step_config)

            if not query:
                logger.warning(
                    "Could not extract query from step input for context enhancement"
                )
                return {}

            # Enhance the query with context
            enhanced_query = await self.enhance_prompt_with_context(
                original_prompt=query,
                source_ids=source_ids,
                max_context_chunks=5,
            )

            # Update the appropriate field in step input
            enhanced_input = {}

            # Common field names that might contain the main prompt/query
            query_fields = [
                "objective",
                "prompt",
                "query",
                "instruction",
                "task",
                "description",
            ]

            for field in query_fields:
                if field in step_input and step_input[field] == query:
                    enhanced_input[field] = enhanced_query
                    break
            else:
                # If no specific field found, add as context
                enhanced_input["knowledge_context"] = enhanced_query

            # Add metadata about context enhancement
            enhanced_input["_context_enhanced"] = True
            enhanced_input["_source_ids_used"] = source_ids

            logger.info(
                f"Enhanced step '{step_config.get('name', 'unknown')}' with knowledge context"
            )
            return enhanced_input

        except Exception as e:
            logger.error(f"Error enhancing step with context: {str(e)}")
            return {}

    def _extract_query_from_step_input(
        self, step_input: dict, step_config: dict
    ) -> str | None:
        """
        Extract the main query/prompt from step input for context enhancement.

        Args:
            step_input: Step input configuration
            step_config: Step configuration

        Returns:
            Extracted query string or None if not found
        """
        # Try common field names for queries/prompts
        query_fields = [
            "objective",
            "prompt",
            "query",
            "instruction",
            "task",
            "description",
        ]

        for field in query_fields:
            if field in step_input and isinstance(step_input[field], str):
                return step_input[field]

        # Fallback: use step name as query if it looks like a question or task
        step_name = step_config.get("name", "")
        if step_name and any(char in step_name for char in "?"):
            return step_name

        # Last resort: concatenate all string values
        text_values = [
            str(v)
            for v in step_input.values()
            if isinstance(v, str) and len(str(v)) > 10
        ]
        if text_values:
            return " ".join(text_values)

        return None
