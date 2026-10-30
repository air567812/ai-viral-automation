import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(agent_name)

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the autonomous agent's primary task."""
        pass
