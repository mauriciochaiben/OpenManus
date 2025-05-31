"""
Classe abstrata base para agentes do OpenManus.

Este módulo define a interface base que todos os agentes devem implementar,
seguindo os padrões de Clean Architecture e convenções do projeto OpenManus.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class BaseAgent(ABC):
    """Classe abstrata base para todos os agentes do OpenManus.

    Define a interface comum que todos os agentes devem implementar,
    garantindo consistência na arquitetura multi-agente do sistema.

    Esta classe segue os princípios de Clean Architecture e fornece
    a base para implementação de agentes especializados.
    """

    @abstractmethod
    def __init__(self, config: Optional[Dict] = None) -> None:
        """Inicializa o agente com configurações opcionais.

        Args:
            config: Dicionário opcional contendo configurações específicas
                   do agente (ex: URLs, credenciais, parâmetros de execução).

        Note:
            Subclasses devem implementar este método para configurar
            suas dependências e estado inicial específicos.
        """
        pass

    @abstractmethod
    async def run(self, task_details: Dict) -> Dict:
        """Executa uma tarefa específica de forma assíncrona.

        Args:
            task_details: Dicionário contendo os detalhes da tarefa a ser executada.
                         Pode incluir campos como:
                         - description: Descrição da tarefa
                         - parameters: Parâmetros específicos
                         - context: Contexto adicional necessário
                         - priority: Prioridade da execução

        Returns:
            Dict: Resultado da execução contendo:
                 - success: Boolean indicando sucesso/falha
                 - result: Dados resultantes da execução
                 - message: Mensagem descritiva do resultado
                 - metadata: Metadados adicionais (tempo, recursos usados, etc.)

        Raises:
            Exception: Quando ocorre erro durante a execução da tarefa.

        Note:
            Este método é o ponto principal de execução do agente.
            Implementações devem ser thread-safe e handle exceptions apropriadamente.
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Retorna uma lista das capacidades do agente.

        Returns:
            List[str]: Lista de strings descrevendo as capacidades específicas
                      do agente. Exemplos:
                      - "web_browsing": Navegação web
                      - "code_execution": Execução de código
                      - "file_manipulation": Manipulação de arquivos
                      - "data_analysis": Análise de dados
                      - "api_integration": Integração com APIs

        Note:
            Esta informação é usada pelo sistema de roteamento de tarefas
            para determinar qual agente é mais adequado para cada tarefa.

            As capacidades devem ser descritas de forma consistente
            para facilitar a descoberta e seleção automática de agentes.
        """
        pass
