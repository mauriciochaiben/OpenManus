from enum import Enum

from app.agent.base import BaseAgent
from app.flow.base import BaseFlow
from app.flow.multi_agent import ExecutionMode, MultiAgentFlow
from app.flow.planning import PlanningFlow


class FlowType(str, Enum):
    PLANNING = "planning"
    MULTI_AGENT = "multi_agent"
    SINGLE_AGENT = "single_agent"
    AUTO = "auto"


class FlowFactory:
    """Factory for creating different types of flows with support for multiple agents"""

    @staticmethod
    def create_flow(
        flow_type: FlowType,
        agents: BaseAgent | list[BaseAgent] | dict[str, BaseAgent],
        **kwargs,
    ) -> BaseFlow:
        # Handle different flow types
        if flow_type == FlowType.PLANNING:
            return PlanningFlow(agents, **kwargs)

        if flow_type == FlowType.MULTI_AGENT:
            # Ensure agents is in the right format for MultiAgentFlow
            if isinstance(agents, BaseAgent):
                agents_dict = {"primary": agents, "manus": agents}
            elif isinstance(agents, list):
                agents_dict = {f"agent_{i}": agent for i, agent in enumerate(agents)}
            else:
                agents_dict = agents

            return MultiAgentFlow(
                agents=agents_dict, mode=ExecutionMode.FORCE_MULTI, **kwargs
            )

        if flow_type == FlowType.SINGLE_AGENT:
            # Create a MultiAgentFlow in force single mode
            if isinstance(agents, BaseAgent):
                agents_dict = {"primary": agents}
            elif isinstance(agents, list):
                agents_dict = {"primary": agents[0]}
            else:
                agents_dict = {"primary": list(agents.values())[0]}

            return MultiAgentFlow(
                agents=agents_dict, mode=ExecutionMode.FORCE_SINGLE, **kwargs
            )

        if flow_type == FlowType.AUTO:
            # Create a MultiAgentFlow in auto mode
            if isinstance(agents, BaseAgent):
                agents_dict = {"primary": agents, "manus": agents}
            elif isinstance(agents, list):
                agents_dict = {f"agent_{i}": agent for i, agent in enumerate(agents)}
            else:
                agents_dict = agents

            return MultiAgentFlow(
                agents=agents_dict,
                mode=ExecutionMode.AUTO,
                enable_planning=True,
                enable_coordination=True,
                **kwargs,
            )

        raise ValueError(f"Unknown flow type: {flow_type}")
