"""Mock LLM implementation for testing when external APIs are unavailable"""

import asyncio
import random

from openai.types.chat import ChatCompletionMessage

from app.schema import Message


class MockLLM:
    """Mock LLM that provides realistic responses for testing progress broadcasting"""

    def __init__(self):
        self.model = "mock-gpt-4o-mini"
        self.api_type = "mock"
        self.request_count = 0

        # Sample responses for different types of requests
        self.responses = {
            "greeting": [
                "Olá! Como posso ajudá-lo hoje?",
                "Oi! Em que posso ser útil?",
                "Olá! Estou aqui para ajudar.",
            ],
            "task": [
                "Entendi sua solicitação. Vou processar isso para você.",
                "Perfeito! Vou trabalhar nisso agora.",
                "Compreendi. Deixe-me resolver isso.",
            ],
            "analysis": [
                "Analisando os dados fornecidos...",
                "Processando as informações...",
                "Examinando os detalhes...",
            ],
            "default": [
                "Processando sua solicitação...",
                "Trabalhando na resposta...",
                "Analisando o conteúdo...",
            ],
        }

    def _get_response_type(self, content: str) -> str:
        """Determine response type based on content"""
        content_lower = content.lower()

        if any(word in content_lower for word in ["olá", "oi", "hello", "hi"]):
            return "greeting"
        if any(word in content_lower for word in ["criar", "fazer", "analisar", "pesquisar"]):
            return "task"
        if any(word in content_lower for word in ["dados", "informação", "análise"]):
            return "analysis"
        return "default"

    async def ask(
        self,
        messages: list[dict | Message],
        system_msgs: list[dict | Message] | None = None,  # noqa: ARG002
        stream: bool = True,  # noqa: ARG002
        temperature: float | None = None,  # noqa: ARG002
    ) -> str:
        """Mock ask method that provides realistic responses"""

        # Simulate processing delay
        await asyncio.sleep(random.uniform(0.5, 2.0))

        self.request_count += 1

        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if isinstance(msg, dict):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            elif hasattr(msg, "role") and msg.role == "user":
                user_message = msg.content
                break

        # Determine response type and get appropriate response
        response_type = self._get_response_type(user_message)
        responses = self.responses.get(response_type, self.responses["default"])
        base_response = random.choice(responses)

        # Add some context based on the request
        if len(user_message) > 50:
            detailed_response = (
                f"{base_response}\n\n"
                f"**Sua solicitação:** {user_message[:100]}...\n\n"
                f"**Resposta detalhada:** Com base na sua solicitação, "
                f"vou processar as informações e fornecer uma resposta "
                f"adequada. Este é um sistema de demonstração que mostra "
                f"como as mensagens de progresso funcionam durante a "
                f"execução de tarefas."
            )
            response = detailed_response
        else:
            response = (
                f"{base_response}\n\n**Resposta:** {user_message}\n\n**Status:** Processamento concluído com sucesso."
            )

        return response

    async def ask_tool(
        self,
        messages: list[dict | Message],
        system_msgs: list[dict | Message] | None = None,
        timeout: int = 300,  # noqa: ARG002
        tools: list[dict] | None = None,  # noqa: ARG002
        tool_choice=None,  # noqa: ARG002
        temperature: float | None = None,
        **kwargs,  # noqa: ARG002
    ) -> ChatCompletionMessage:
        """Mock ask_tool method"""

        # Simulate processing delay
        await asyncio.sleep(random.uniform(1.0, 3.0))

        response_content = await self.ask(messages, system_msgs, False, temperature)

        # Create a mock ChatCompletionMessage
        class MockChatCompletionMessage:
            def __init__(self, content: str):
                self.content = content
                self.role = "assistant"
                self.tool_calls = None
                self.function_call = None

        return MockChatCompletionMessage(response_content)

    async def cleanup(self):
        """Mock cleanup method"""
        pass

    async def ask_internal(self, *args, **kwargs):
        """Compatibility method for internal calls"""
        return await self.ask(*args, **kwargs)

    async def ask_tool_internal(self, *args, **kwargs):
        """Compatibility method for internal tool calls"""
        return await self.ask_tool(*args, **kwargs)


# Create singleton instance
mock_llm = MockLLM()
