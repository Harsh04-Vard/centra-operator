"""
Corporate Knowledge and Memory Store:
Provides semantic and keyword indexing, SOP retrieval, and organizational context lookup.
"""

import re
from typing import List, Optional, Dict, Any, Tuple
from centra_operator.memory.org_graph import OrgMemoryGraph
from centra_operator.memory.default_knowledge import CompanySOP, get_default_sops

class CorporateMemoryStore:
    def __init__(self, org_graph: Optional[OrgMemoryGraph] = None):
        self.org_graph = org_graph or OrgMemoryGraph.create_default()
        self.sops: Dict[str, CompanySOP] = {sop.id: sop for sop in get_default_sops()}
        self.past_execution_learnings: List[Dict[str, Any]] = []

    def find_relevant_sop(self, user_goal: str) -> Optional[CompanySOP]:
        goal_lower = user_goal.lower()
        scored_sops: List[Tuple[float, CompanySOP]] = []
        
        for sop in self.sops.values():
            score = 0.0
            # Keyword matching
            for kw in sop.trigger_keywords:
                if kw.lower() in goal_lower:
                    score += 3.0
            # Department matching
            if sop.department.lower() in goal_lower:
                score += 1.5
            # Token overlap
            tokens = set(re.findall(r'\w+', goal_lower))
            sop_tokens = set(re.findall(r'\w+', sop.description.lower()))
            overlap = len(tokens.intersection(sop_tokens))
            score += overlap * 0.5
            
            if score > 0:
                scored_sops.append((score, sop))
                
        if not scored_sops:
            return next(iter(self.sops.values()))
            
        scored_sops.sort(key=lambda x: x[0], reverse=True)
        return scored_sops[0][1]

    def get_employee_context(self, query: str) -> Optional[Dict[str, Any]]:
        query_lower = query.lower()
        for email, emp in self.org_graph.employees.items():
            if emp.name.lower() in query_lower or email.lower() in query_lower or emp.id.lower() in query_lower:
                return emp.dict()
        return None

    def record_learning(self, session_id: str, goal: str, outcome: str, notes: str):
        self.past_execution_learnings.append({
            "session_id": session_id,
            "goal": goal,
            "outcome": outcome,
            "notes": notes
        })

GLOBAL_MEMORY = CorporateMemoryStore()
