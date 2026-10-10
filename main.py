"""
CentrAlign Autonomous Company Operator - Main Entrypoint
Run with `--web` to launch the Interactive Web Dashboard,
or `--cli` for terminal mission control.
"""

import sys
import argparse
import uvicorn
from centra_operator.config import CONFIG

def main():
    parser = argparse.ArgumentParser(description="CentrAlign Autonomous Company Operator")
    parser.add_argument("--web", action="store_true", default=True, help="Launch Mission Control Web Dashboard (Default)")
    parser.add_argument("--cli", action="store_true", help="Run interactive CLI interface")
    parser.add_argument("--goal", type="str", help="Goal to execute in CLI mode")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve HITL gates in CLI mode")
    parser.add_argument("--port", type=int, default=CONFIG.port, help="Port to bind web server")
    args = parser.parse_args()

    if args.cli or args.goal:
        from cli import run_cli_goal
        goal = args.goal or "Onboard Alex Morgan as Senior Frontend Engineer starting Monday"
        run_cli_goal(goal, auto_approve=args.auto_approve)
    else:
        divider = "=" * 70
        print(divider)
        print(" ? CentrAlign Autonomous Company Operator - Mission Control Server ? ")
        print(f" Access Web Dashboard at: http://localhost:{args.port}")
        print(divider)
        uvicorn.run("centra_operator.web.app:app", host="127.0.0.1", port=args.port, reload=False)

if __name__ == "__main__":
    main()
