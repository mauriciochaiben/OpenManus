import asyncio

from app.agent.manus import Manus
from app.core.settings import settings
from app.flow.flow_factory import FlowFactory, FlowType
from app.flow.multi_agent import ExecutionMode
from app.logger import logger


def analyze_task_complexity(prompt: str) -> dict:
    """Análise simples de complexidade da tarefa"""
    complexity_indicators = {
        "length": len(prompt.split()) > 20,
        "keywords": any(
            keyword in prompt.lower()
            for keyword in [
                "plan",
                "multi",
                "analyze",
                "research",
                "develop",
                "create",
                "implement",
                "coordinate",
                "collaborate",
                "complex",
            ]
        ),
        "multiple_domains": len(
            [
                domain
                for domain in ["code", "research", "analysis", "web", "system"]
                if domain in prompt.lower()
            ]
        )
        > 1,
        "time_consuming": any(
            word in prompt.lower()
            for word in ["detailed", "comprehensive", "thorough", "complete"]
        ),
    }

    complexity_score = sum(complexity_indicators.values())
    return {
        "score": complexity_score,
        "indicators": complexity_indicators,
        "is_complex": complexity_score >= 2,
    }


async def main():
    # Configuration is now automatically loaded from settings

    try:
        prompt = input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        logger.warning("Processing your request...")

        # Análise de complexidade
        task_analysis = analyze_task_complexity(prompt)
        logger.info(f"Task complexity analysis: {task_analysis}")

        # Criar agente principal
        manus_agent = await Manus.create()

        if task_analysis["is_complex"]:
            logger.info("Detected complex task. Using multi-agent flow.")

            # Criar flow multi-agente
            agents = {
                "manus": manus_agent,
                "primary": manus_agent,  # Usar Manus como agente primário
            }

            flow = FlowFactory.create_flow(
                flow_type=FlowType.MULTI_AGENT,
                agents=agents,
                mode=ExecutionMode.AUTO,  # Decisão automática
                enable_planning=True,
                enable_coordination=True,
            )

            # Inicializar o flow
            await flow.initialize()

            # Executar
            result = await flow.execute(prompt)

            # Mostrar status final
            status = await flow.get_status()
            logger.info(f"Multi-agent execution status: {status}")

        else:
            logger.info("Detected simple task. Using single agent.")
            result = await manus_agent.run(prompt)

        logger.info("Request processing completed.")
        print("\n" + "=" * 50)
        print("RESULT:")
        print("=" * 50)
        print(result)
        print("=" * 50)

    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        print(f"Error: {str(e)}")
    finally:
        # Cleanup de recursos
        try:
            if "manus_agent" in locals():
                await manus_agent.cleanup()
            if "flow" in locals() and hasattr(flow, "cleanup"):
                await flow.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
