"""
CentrAlign Operator - Interactive CLI Runner
Provides headless and interactive terminal interfaces for running enterprise workflows,
observing live telemetry, and responding to Human-in-the-Loop prompts.
"""

import sys
import argparse
from centra_operator.engine.runtime import GLOBAL_RUNTIME
from centra_operator.engine.state import TaskStatus
from centra_operator.memory.store import GLOBAL_MEMORY

def run_cli_goal(goal: str, auto_approve: bool = False):
    divider = "=" * 70
    alert_div = "!" * 70
    print("\n" + divider)
    print(" ? CentrAlign Autonomous Company Operator - Mission Control ? ")
    print(divider)
    print(f"[*] High-Level User Request: {goal}\n")

    state = GLOBAL_RUNTIME.initialize_session(goal)
    print(f"[+] Grounded SOP: {state.matched_sop_id}")
    print(f"[+] Disambiguated Intent: {state.disambiguated_intent}")
    print(f"[+] Compiled Task DAG: {len(state.tasks)} discrete verifiable steps\n")

    while state.status in (TaskStatus.RUNNING, TaskStatus.PLANNING, TaskStatus.AWAITING_APPROVAL):
        if state.status == TaskStatus.AWAITING_APPROVAL and state.pending_approvals:
            approval = state.pending_approvals[0]
            print("\n" + alert_div)
            print(f" [!] HUMAN APPROVAL REQUIRED (Risk: {approval.risk_level.value})")
            print(f" [!] Reason: {approval.reason}")
            print(f" [!] Blast Radius: {approval.blast_radius}")
            print(f" [!] Tool: {approval.tool_name} | Params: {approval.tool_params}")
            print(alert_div)

            if auto_approve:
                print(" -> Auto-approving (test flag enabled)...")
                GLOBAL_RUNTIME.hitl_manager.submit_decision(state, approval.id, "APPROVED", feedback="Auto-approved via CLI flag")
            else:
                choice = input("\n[?] Enter Decision [A]pprove / [R]eject / [M]odify params: ").strip().upper()
                if choice == "R":
                    reason = input("Enter rejection reason: ").strip()
                    GLOBAL_RUNTIME.hitl_manager.submit_decision(state, approval.id, "REJECTED", feedback=reason)
                elif choice == "M":
                    new_val = input("Enter modified value: ").strip()
                    GLOBAL_RUNTIME.hitl_manager.submit_decision(state, approval.id, "MODIFIED", feedback="Modified via CLI", modified_params={"custom_override": new_val})
                else:
                    note = input("Enter optional signoff note: ").strip()
                    GLOBAL_RUNTIME.hitl_manager.submit_decision(state, approval.id, "APPROVED", feedback=note or "Approved via CLI")

        GLOBAL_RUNTIME.step(state, auto_approve_hitl=auto_approve)

    print("\n" + divider)
    if state.status == TaskStatus.COMPLETED:
        print(" [?] GOAL COMPLETED & INVARIANT VERIFIED SUCCESSFULLY!")
    else:
        print(f" [?] EXECUTION FINISHED WITH STATUS: {state.status.value}")
    print(divider)

    if state.evidence_summary:
        print(f"[*] Audit Report (Markdown): {state.evidence_summary.get('report_path_md')}")
        print(f"[*] Audit Bundle (JSON):     {state.evidence_summary.get('report_path_json')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CentrAlign Operator CLI")
    parser.add_argument("goal", nargs="?", default="Onboard Alex Morgan as Senior Frontend Engineer starting Monday", help="Enterprise goal to execute")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve HITL gates")
    args = parser.parse_args()

    run_cli_goal(args.goal, auto_approve=args.auto_approve)
