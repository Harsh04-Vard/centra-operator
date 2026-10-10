"""
Base Tool Interface and Execution Result Contracts.
Every enterprise tool extends BaseTool to guarantee deterministic schema, error logging, and auditability.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
from centra_operator.engine.state import RiskLevel

class ToolResult(BaseModel):
    success: bool
    output: Any
    evidence: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    artifacts: List[str] = Field(default_factory=list)
    telemetry: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)

class BaseTool(ABC):
    name: str
    description: str
    risk_level: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False

    @abstractmethod
    def execute(self, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Execute the tool action with given parameters and contextual state."""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Return tool parameter schema description."""
        return {
            "name": self.name,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "requires_confirmation": self.requires_confirmation
        }
