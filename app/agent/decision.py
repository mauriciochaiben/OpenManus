"""
Sistema de decisão inteligente para escolha entre single agent e multi-agent
"""

from dataclasses import dataclass
from enum import Enum
import re

from app.logger import logger


class TaskComplexity(Enum):
    """Níveis de complexidade da tarefa"""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class AgentApproach(Enum):
    """Abordagens de execução"""

    SINGLE_AGENT = "single_agent"
    MULTI_AGENT_SEQUENTIAL = "multi_agent_sequential"
    MULTI_AGENT_PARALLEL = "multi_agent_parallel"
    MULTI_AGENT_COLLABORATIVE = "multi_agent_collaborative"


@dataclass
class TaskAnalysis:
    """Resultado da análise de uma tarefa"""

    complexity: TaskComplexity
    domains: set[str]
    estimated_steps: int
    requires_specialization: bool
    parallel_potential: bool
    collaboration_needed: bool
    tools_needed: list[str]


class AgentDecisionSystem:
    """
    Sistema que decide entre single agent ou multi-agent baseado na complexidade.

    Baseado na complexidade da tarefa.
    """

    def __init__(self):
        # Padrões que indicam diferentes domínios
        self.domain_patterns = {
            "development": [
                r"\b(code|program|develop|implement|build|create.*app|software|debug|fix.*bug)\b",
                r"\b(python|javascript|java|html|css|api|database|sql)\b",
                r"\b(git|github|commit|repository|branch|merge)\b",
            ],
            "research": [
                r"\b(research|investigate|analyze|study|find.*information|gather.*data)\b",
                r"\b(search|google|browse|web|internet|online)\b",
                r"\b(paper|article|document|report|publication)\b",
            ],
            "data_analysis": [
                r"\b(analyze.*data|statistics|chart|graph|visualization|plot)\b",
                r"\b(excel|csv|dataframe|pandas|numpy|matplotlib)\b",
                r"\b(correlation|trend|pattern|insight|metric)\b",
            ],
            "system_admin": [
                r"\b(install|configure|setup|deploy|server|system)\b",
                r"\b(file.*system|directory|folder|permission|backup)\b",
                r"\b(terminal|command.*line|bash|shell|script)\b",
            ],
            "browser_automation": [
                r"\b(browser|website|web.*page|click|navigate|scrape)\b",
                r"\b(form|submit|download|upload|screenshot)\b",
                r"\b(selenium|playwright|automation)\b",
            ],
            "document_processing": [
                r"\b(document|pdf|word|text|read|parse|extract)\b",
                r"\b(summary|summarize|content|format|convert)\b",
            ],
        }

        # Padrões que indicam complexidade
        self.complexity_indicators = {
            "high": [
                r"\b(multiple|several|many|various|different)\b",
                r"\b(integrate|combine|coordinate|orchestrate)\b",
                r"\b(workflow|pipeline|process|sequence)\b",
                r"\b(complex|complicated|sophisticated|advanced)\b",
            ],
            "parallel": [
                r"\b(parallel|simultaneously|at.*same.*time|concurrently)\b",
                r"\b(independent|separate|isolated)\b",
            ],
            "collaborative": [
                r"\b(collaborate|coordinate|work.*together|communicate)\b",
                r"\b(share|exchange|combine.*results)\b",
            ],
        }

        # Mapeamento de ferramentas para domínios
        self.tool_domain_map = {
            "bash": ["system_admin", "development"],
            "browser": ["browser_automation", "research"],
            "editor": ["development", "document_processing"],
            "python": ["development", "data_analysis"],
            "search": ["research"],
            "document_reader": ["document_processing", "research"],
            "planning": ["all"],
        }

    def analyze_task_complexity(self, task: str) -> TaskAnalysis:
        """Analisa a complexidade de uma tarefa"""
        logger.info(f"Analyzing task complexity: {task[:100]}...")

        # Detectar domínios envolvidos
        domains = self._detect_domains(task)

        # Detectar ferramentas necessárias
        tools_needed = self._detect_tools_needed(task, domains)

        # Calcular complexidade
        complexity = self._calculate_complexity(task, domains, tools_needed)

        # Detectar potencial para execução paralela
        parallel_potential = self._detect_parallel_potential(task)

        # Detectar necessidade de colaboração
        collaboration_needed = self._detect_collaboration_need(task)

        # Estimar número de passos
        estimated_steps = self._estimate_steps(task, complexity)

        # Verificar se requer especialização
        requires_specialization = len(domains) > 1 or complexity in [
            TaskComplexity.COMPLEX,
            TaskComplexity.VERY_COMPLEX,
        ]

        analysis = TaskAnalysis(
            complexity=complexity,
            domains=domains,
            estimated_steps=estimated_steps,
            requires_specialization=requires_specialization,
            parallel_potential=parallel_potential,
            collaboration_needed=collaboration_needed,
            tools_needed=tools_needed,
        )

        logger.info(f"Task analysis result: {analysis}")
        return analysis

    def recommend_approach(self, analysis: TaskAnalysis) -> AgentApproach:
        """Recomenda a abordagem baseada na análise da tarefa"""
        # Single agent para tarefas simples ou com um único domínio
        if (
            analysis.complexity == TaskComplexity.SIMPLE
            and len(analysis.domains) <= 1
            and not analysis.requires_specialization
        ):
            return AgentApproach.SINGLE_AGENT

        # Multi-agent paralelo se há potencial e não precisa de colaboração
        if analysis.parallel_potential and not analysis.collaboration_needed and len(analysis.domains) > 1:
            return AgentApproach.MULTI_AGENT_PARALLEL

        # Multi-agent colaborativo se precisa de colaboração
        if analysis.collaboration_needed:
            return AgentApproach.MULTI_AGENT_COLLABORATIVE

        # Multi-agent sequencial para outras tarefas complexas
        if analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX] or len(analysis.domains) > 1:
            return AgentApproach.MULTI_AGENT_SEQUENTIAL

        # Padrão: single agent
        return AgentApproach.SINGLE_AGENT

    def _detect_domains(self, task: str) -> set[str]:
        """Detecta os domínios envolvidos na tarefa"""
        domains = set()
        task_lower = task.lower()

        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                if re.search(pattern, task_lower, re.IGNORECASE):
                    domains.add(domain)
                    break

        return domains

    def _detect_tools_needed(self, task: str, domains: set[str]) -> list[str]:
        """Detecta as ferramentas necessárias baseado na tarefa e domínios"""
        tools = set()
        task_lower = task.lower()

        # Detecção direta por palavras-chave
        tool_keywords = {
            "bash": ["terminal", "command", "shell", "bash", "script"],
            "browser": ["browser", "website", "web", "navigate", "click"],
            "editor": ["edit", "file", "code", "text", "write"],
            "python": ["python", "script", "execute", "run"],
            "search": ["search", "find", "look", "google"],
            "document_reader": ["document", "pdf", "read", "parse"],
            "planning": ["plan", "steps", "organize", "sequence"],
        }

        for tool, keywords in tool_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                tools.add(tool)

        # Adicionar ferramentas baseado nos domínios
        for tool, tool_domains in self.tool_domain_map.items():
            if tool_domains == ["all"] or any(domain in domains for domain in tool_domains):
                tools.add(tool)

        return list(tools)

    def _calculate_complexity(self, task: str, domains: set[str], tools_needed: list[str]) -> TaskComplexity:
        """Calcula a complexidade da tarefa"""
        complexity_score = 0
        task_lower = task.lower()

        # Pontuação baseada no número de domínios
        complexity_score += len(domains) * 2

        # Pontuação baseada no número de ferramentas
        complexity_score += len(tools_needed)

        # Pontuação baseada no tamanho da descrição
        word_count = len(task.split())
        if word_count > 50:
            complexity_score += 3
        elif word_count > 20:
            complexity_score += 2
        elif word_count > 10:
            complexity_score += 1

        # Pontuação baseada em indicadores de complexidade
        for pattern in self.complexity_indicators["high"]:
            if re.search(pattern, task_lower, re.IGNORECASE):
                complexity_score += 2

        # Determinar nível de complexidade
        if complexity_score <= 3:
            return TaskComplexity.SIMPLE
        if complexity_score <= 7:
            return TaskComplexity.MODERATE
        if complexity_score <= 12:
            return TaskComplexity.COMPLEX
        return TaskComplexity.VERY_COMPLEX

    def _detect_parallel_potential(self, task: str) -> bool:
        """Detecta se a tarefa tem potencial para execução paralela"""
        task_lower = task.lower()

        for pattern in self.complexity_indicators["parallel"]:
            if re.search(pattern, task_lower, re.IGNORECASE):
                return True

        # Verificar se há múltiplas tarefas independentes mencionadas
        independence_indicators = ["separate", "independent", "different", "various"]
        return any(indicator in task_lower for indicator in independence_indicators)

    def _detect_collaboration_need(self, task: str) -> bool:
        """Detecta se a tarefa precisa de colaboração entre agentes"""
        task_lower = task.lower()

        for pattern in self.complexity_indicators["collaborative"]:
            if re.search(pattern, task_lower, re.IGNORECASE):
                return True

        return False

    def _estimate_steps(self, task: str, complexity: TaskComplexity) -> int:
        """Estima o número de passos necessários"""
        base_steps = {
            TaskComplexity.SIMPLE: 2,
            TaskComplexity.MODERATE: 4,
            TaskComplexity.COMPLEX: 7,
            TaskComplexity.VERY_COMPLEX: 12,
        }

        # Ajustar baseado em palavras-chave que indicam múltiplos passos
        step_indicators = [
            "step",
            "phase",
            "stage",
            "first",
            "second",
            "then",
            "after",
            "next",
        ]
        additional_steps = sum(1 for indicator in step_indicators if indicator in task.lower())

        return base_steps[complexity] + additional_steps


# Convenience function for external use
def analyze_task_complexity(task: str) -> dict:
    """
    Standalone function for analyzing task complexity.

    Returns a simplified dictionary format for compatibility with existing tests
    """
    try:
        decision_system = AgentDecisionSystem()
        analysis = decision_system.analyze_task_complexity(task)

        return {
            "is_complex": analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX],
            "complexity": analysis.complexity.value,
            "domains": list(analysis.domains),
            "estimated_steps": analysis.estimated_steps,
            "requires_specialization": analysis.requires_specialization,
            "parallel_potential": analysis.parallel_potential,
            "collaboration_needed": analysis.collaboration_needed,
            "tools_needed": analysis.tools_needed,
            "recommended_approach": _get_recommended_approach(analysis).value,
        }
    except Exception as e:
        logger.error(f"Error analyzing task complexity: {e}")
        return {
            "is_complex": False,
            "complexity": "simple",
            "domains": [],
            "estimated_steps": 1,
            "requires_specialization": False,
            "parallel_potential": False,
            "collaboration_needed": False,
            "tools_needed": [],
            "recommended_approach": "single_agent",
        }


def _get_recommended_approach(analysis: TaskAnalysis) -> AgentApproach:
    """Determine the recommended approach based on task analysis"""
    if analysis.complexity == TaskComplexity.SIMPLE:
        return AgentApproach.SINGLE_AGENT

    if analysis.collaboration_needed:
        return AgentApproach.MULTI_AGENT_COLLABORATIVE
    if analysis.parallel_potential:
        return AgentApproach.MULTI_AGENT_PARALLEL
    if analysis.requires_specialization or len(analysis.domains) > 1:
        return AgentApproach.MULTI_AGENT_SEQUENTIAL
    return AgentApproach.SINGLE_AGENT
