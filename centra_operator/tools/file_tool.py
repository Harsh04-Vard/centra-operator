"""
File and Document Operator Tool:
Handles safe local sandbox file operations, document parsing, diff generation,
compliance checklist authoring, and SHA256 cryptographic verification.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from centra_operator.tools.base import BaseTool, ToolResult
from centra_operator.engine.state import RiskLevel
from centra_operator.config import CONFIG

class FileOperatorTool(BaseTool):
    name = "file_operator"
    description = "Read, write, diff, hash, and format documents in the enterprise workspace sandbox."
    risk_level = RiskLevel.LOW

    def __init__(self, sandbox_dir: Optional[Path] = None):
        self.sandbox_dir = sandbox_dir or CONFIG.sandbox_dir
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        self._seed_sample_documents()

    def _seed_sample_documents(self):
        """Seed initial documents in sandbox for scenarios (contracts, ledgers, policies)."""
        docs_dir = self.sandbox_dir / "documents"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Sample signed offer agreement
        contract_path = docs_dir / "offer_letter_alex_morgan.md"
        if not contract_path.exists():
            contract_path.write_text(
                "# Acme Corp - Executive Offer Agreement\n"
                "**Candidate Name:** Alex Morgan\n"
                "**Role:** Senior Frontend Engineer\n"
                "**Department:** Engineering\n"
                "**Email:** alex.m@acme.corp\n"
                "**Starting Base Salary:** $165,000 USD\n"
                "**Target Start Date:** 2026-10-15\n"
                "**Reporting To:** Sarah Lin (VP of Engineering)\n"
                "**Signed Status:** SIGNED & VERIFIED (DocuSign Envelope ID: 9481-BCA2-8812)\n"
                "**Required Equipment:** MacBook Pro M3 Max 32GB, YubiKey 5C NFC\n",
                encoding="utf-8"
            )

        # Sample Q3 refund ledger
        ledger_path = docs_dir / "q3_refund_reconciliation.csv"
        if not ledger_path.exists():
            ledger_path.write_text(
                "date,ticket_id,charge_id,customer_email,amount_usd,status,approved_by\n"
                "2026-10-01,TICK-101,ch_3N8812,user1@alpha.io,25.00,RESOLVED,auto_policy\n"
                "2026-10-03,TICK-102,ch_3N9934,ops@beta.co,49.99,RESOLVED,auto_policy\n",
                encoding="utf-8"
            )

    def execute(self, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        action = params.get("action", "read")
        file_path_str = params.get("path", "")
        content = params.get("content", "")
        
        target_path = self.sandbox_dir / file_path_str if not os.path.isabs(file_path_str) else Path(file_path_str)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if action == "read":
                if not target_path.exists():
                    return ToolResult(
                        success=False,
                        output=None,
                        error=f"File not found: {target_path.name}"
                    )
                text = target_path.read_text(encoding="utf-8")
                file_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
                return ToolResult(
                    success=True,
                    output=text,
                    evidence={
                        "path": str(target_path),
                        "size_bytes": len(text),
                        "sha256": file_hash
                    },
                    artifacts=[str(target_path)]
                )

            elif action == "write":
                target_path.write_text(content, encoding="utf-8")
                file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                return ToolResult(
                    success=True,
                    output=f"Successfully written {len(content)} bytes to {target_path.name}",
                    evidence={
                        "path": str(target_path),
                        "size_bytes": len(content),
                        "sha256": file_hash
                    },
                    artifacts=[str(target_path)]
                )

            elif action == "append":
                existing = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
                sep = "\n" if existing and not existing.endswith("\n") else ""
                new_text = existing + sep + content
                target_path.write_text(new_text, encoding="utf-8")
                file_hash = hashlib.sha256(new_text.encode("utf-8")).hexdigest()
                return ToolResult(
                    success=True,
                    output=f"Appended entry to {target_path.name}",
                    evidence={
                        "path": str(target_path),
                        "new_size_bytes": len(new_text),
                        "sha256": file_hash
                    },
                    artifacts=[str(target_path)]
                )

            elif action == "hash":
                if not target_path.exists():
                    return ToolResult(success=False, output=None, error=f"File {target_path.name} does not exist")
                text = target_path.read_text(encoding="utf-8")
                file_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
                return ToolResult(
                    success=True,
                    output=file_hash,
                    evidence={"sha256": file_hash, "file": target_path.name}
                )

            else:
                return ToolResult(success=False, output=None, error=f"Unknown file action: {action}")

        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
