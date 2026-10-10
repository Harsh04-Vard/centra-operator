"""
Configuration module for CentrAlign Autonomous Company Operator.
Manages system environments, model providers, execution limits, and safety boundaries.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional

class OperatorConfig(BaseModel):
    app_name: str = "CentrAlign Company Operator"
    version: str = "1.0.0"
    environment: str = Field(default_factory=lambda: os.getenv("OPERATOR_ENV", "development"))
    
    # Base sandbox directory for file tools, evidence storage, and audit logs
    base_dir: Path = Field(default_factory=lambda: Path(os.getcwd()))
    sandbox_dir: Path = Field(default_factory=lambda: Path(os.getcwd()) / "workspace_sandbox")
    evidence_dir: Path = Field(default_factory=lambda: Path(os.getcwd()) / "workspace_sandbox" / "evidence")
    
    # LLM Settings
    llm_provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "smart_deterministic"))
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    model_name: str = Field(default_factory=lambda: os.getenv("MODEL_NAME", "gemini-2.0-flash"))
    
    # Execution & Safety Guardrail Limits
    max_replan_retries: int = 3
    max_tool_execution_timeout_sec: int = 30
    require_hitl_for_high_risk: bool = True
    financial_approval_threshold_usd: float = 50.0  # Actions with financial impact > $50 require HITL
    
    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True

    class Config:
        arbitrary_types_allowed = True

CONFIG = OperatorConfig()
CONFIG.sandbox_dir.mkdir(parents=True, exist_ok=True)
CONFIG.evidence_dir.mkdir(parents=True, exist_ok=True)
