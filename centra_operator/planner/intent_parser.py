"""
Intent Parser and Goal Disambiguation Engine:
Grounds vague user requests in corporate memory, standard operating procedures, and entity contexts.
"""

from typing import Any, Dict, Tuple
from centra_operator.memory.store import GLOBAL_MEMORY
from centra_operator.memory.default_knowledge import CompanySOP
from centra_operator.llm.provider import GLOBAL_LLM

class IntentParser:
    def __init__(self):
        self.memory = GLOBAL_MEMORY
        self.llm = GLOBAL_LLM

    def parse_intent(self, user_goal: str) -> Tuple[str, CompanySOP, Dict[str, Any]]:
        """
        Resolves ambiguous goal into:
        1. Disambiguated Objective statement
        2. Relevant Standard Operating Procedure (SOP)
        3. Extracted entity parameters
        """
        # Step A: Search Org Memory for matching SOP
        matched_sop = self.memory.find_relevant_sop(user_goal)
        
        # Step B: LLM / Semantic Reasoner grounding
        sops_summary = f"{matched_sop.id}: {matched_sop.title} - {matched_sop.description}"
        understanding = self.llm.understand_goal(user_goal, sops_summary)
        
        disambiguated_intent = understanding.get(
            "disambiguated_intent",
            f"Execute {matched_sop.title} according to organizational guidelines."
        )
        entities = understanding.get("entities", {})

        return disambiguated_intent, matched_sop, entities

GLOBAL_INTENT_PARSER = IntentParser()
