#!/usr/bin/env python3
"""
Silver Tier Sandbox Tester - 100% Safe Testing

Runs complete Silver Tier workflow tests WITHOUT any external API calls.
All actions are mocked/simulated. Safe for CI/CD and local development.

Usage:
    python test_sandbox.py              # Run all tests
    python test_sandbox.py --component mcp      # Test MCP only
    python test_sandbox.py --component watcher  # Test watchers only
    python test_sandbox.py --verbose            # Show detailed output
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
VAULT_DIR = PROJECT_ROOT / "AI_Employee_Vault"


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


class SandboxTester:
    """
    Safe sandbox tester for Silver Tier components.
    
    All tests run locally with NO external API calls.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "tests": []
        }
        
        # Ensure vault directories exist
        (VAULT_DIR / "Inbox_Drop").mkdir(parents=True, exist_ok=True)
        (VAULT_DIR / "Inbox").mkdir(parents=True, exist_ok=True)
        (VAULT_DIR / "Plans").mkdir(parents=True, exist_ok=True)
        (VAULT_DIR / "Proposed_Actions").mkdir(parents=True, exist_ok=True)
        (VAULT_DIR / "Done").mkdir(parents=True, exist_ok=True)
        (VAULT_DIR / "Logs_Extended").mkdir(parents=True, exist_ok=True)

    def run_test(self, name: str, test_func, expected_success: bool = True):
        """Run a single test and record result"""
        print(f"  Testing: {name}...", end=" ", flush=True)
        
        start_time = time.time()
        try:
            result = test_func()
            duration = time.time() - start_time
            
            if expected_success:
                print_success(f"Passed ({duration:.2f}s)")
                self.test_results["passed"] += 1
                self.test_results["tests"].append({
                    "name": name,
                    "status": "PASSED",
                    "duration": duration
                })
            else:
                print_error(f"Expected failure but passed")
                self.test_results["failed"] += 1
                self.test_results["tests"].append({
                    "name": name,
                    "status": "UNEXPECTED_PASS",
                    "duration": duration
                })
                
        except Exception as e:
            duration = time.time() - start_time
            
            if not expected_success:
                print_success(f"Expected failure ({duration:.2f}s)")
                self.test_results["passed"] += 1
                self.test_results["tests"].append({
                    "name": name,
                    "status": "EXPECTED_FAILURE",
                    "duration": duration,
                    "error": str(e)
                })
            else:
                print_error(f"Failed: {e} ({duration:.2f}s)")
                self.test_results["failed"] += 1
                self.test_results["tests"].append({
                    "name": name,
                    "status": "FAILED",
                    "duration": duration,
                    "error": str(e)
                })

    def test_mcp_health(self):
        """Test MCP Server health endpoint"""
        import httpx
        
        response = httpx.get("http://localhost:8765/health", timeout=5.0)
        response.raise_for_status()
        
        data = response.json()
        assert data.get("status") == "healthy", "MCP not healthy"
        assert "uptime_seconds" in data, "Missing uptime"
        assert "version" in data, "Missing version"
        
        if self.verbose:
            print(f"\n    MCP Health: {json.dumps(data, indent=2)}")

    def test_mcp_actions_list(self):
        """Test MCP actions listing"""
        import httpx
        
        response = httpx.get("http://localhost:8765/actions", timeout=5.0)
        response.raise_for_status()
        
        data = response.json()
        actions = data.get("actions", [])
        
        assert len(actions) >= 4, f"Expected 4+ actions, got {len(actions)}"
        assert "send_email" in actions, "Missing send_email action"
        assert "post_linkedin" in actions, "Missing post_linkedin action"
        
        if self.verbose:
            print(f"\n    Available Actions: {actions}")

    def test_filesystem_watcher(self):
        """Test Filesystem Watcher"""
        import subprocess
        
        # Create test file
        test_file = VAULT_DIR / "Inbox_Drop" / f"sandbox_test_{int(time.time())}.txt"
        test_file.write_text(f"Sandbox test content\nTimestamp: {datetime.now(timezone.utc).isoformat()}")
        
        # Run watcher
        result = subprocess.run(
            [sys.executable, "-m", "ai_employee.watchers.filesystem_watcher", "--test"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}
        )
        
        assert result.returncode == 0, f"Watcher failed: {result.stderr}"
        assert "Processed" in result.stdout, "No processing detected"
        
        if self.verbose:
            print(f"\n    Watcher Output: {result.stdout}")

    def test_plan_generator(self):
        """Test Plan Generator Service"""
        from ai_employee.services.plan_generator import PlanGenerator
        
        generator = PlanGenerator(
            plans_dir=VAULT_DIR / "Plans",
            dashboard_path=VAULT_DIR / "Dashboard.md"
        )
        
        plan, plan_id = generator.create_plan(
            title="Sandbox Test Plan",
            objective="Test plan generation in sandbox mode",
            steps=[
                {"skill_name": "Test Skill", "description": "Test step", "dependencies": []}
            ],
            requires_mcp=False
        )
        
        assert plan_id.startswith("Plan_"), "Invalid plan ID format"
        assert plan.risk_level in ["Low", "Medium", "High"], "Invalid risk level"
        
        if self.verbose:
            print(f"\n    Plan ID: {plan_id}")
            print(f"    Risk Level: {plan.risk_level}")
            print(f"    Approval Required: {plan.approval_required}")

    def test_approval_request(self):
        """Test Approval Request Service"""
        from ai_employee.services.approval_request import ApprovalRequest
        
        service = ApprovalRequest(
            actions_dir=VAULT_DIR / "Proposed_Actions",
            dashboard_path=VAULT_DIR / "Dashboard.md"
        )
        
        action, action_id = service.create_approval_request(
            title="Sandbox Test Action",
            plan_reference="Plans/Sandbox_Test_Plan.md",
            summary="Test approval workflow in sandbox",
            risk_level="Low"
        )
        
        assert action_id.startswith("Action_"), "Invalid action ID format"
        assert action.approved == "PENDING", "Action should be pending"
        
        if self.verbose:
            print(f"\n    Action ID: {action_id}")
            print(f"    Status: {action.approved}")

    def test_linkedin_mock(self):
        """Test LinkedIn Mock Poster"""
        from ai_employee.mcp_server.actions.linkedin_mock_test import LinkedInMockPoster
        
        poster = LinkedInMockPoster()
        
        # Generate draft
        draft_content = "🚀 Sandbox test post\n\n#Testing #Automation"
        draft_path = poster.generate_post_draft(draft_content, "Sandbox Test")
        
        assert Path(draft_path).exists(), "Draft file not created"
        assert "Sandbox test post" in Path(draft_path).read_text(), "Content mismatch"
        
        if self.verbose:
            print(f"\n    Draft Path: {draft_path}")

    def test_cron_runner(self):
        """Test Cron Runner"""
        from ai_employee.scheduler.cron_runner import CronRunner
        
        runner = CronRunner(
            scheduled_tasks_dir=VAULT_DIR / "Scheduled_Tasks",
            dashboard_path=VAULT_DIR / "Dashboard.md"
        )
        
        # Check for missed executions (should not raise)
        runner.check_missed_executions()
        
        # Verify tasks loaded
        if self.verbose:
            print(f"\n    Loaded Tasks: {len(runner.tasks)}")
            for name, task in runner.tasks.items():
                print(f"      - {name}: enabled={task.enabled}")

    def test_vault_structure(self):
        """Test Obsidian Vault Structure"""
        required_dirs = [
            "Inbox_Drop",
            "Inbox",
            "Plans",
            "Proposed_Actions",
            "Done",
            "Logs_Extended",
            "Scheduled_Tasks"
        ]
        
        for dir_name in required_dirs:
            dir_path = VAULT_DIR / dir_name
            assert dir_path.exists(), f"Missing directory: {dir_name}"
            assert dir_path.is_dir(), f"Not a directory: {dir_name}"
        
        # Check Dashboard.md exists
        dashboard = VAULT_DIR / "Dashboard.md"
        assert dashboard.exists(), "Dashboard.md missing"
        
        if self.verbose:
            print(f"\n    Vault Directories:")
            for dir_name in required_dirs:
                file_count = len(list((VAULT_DIR / dir_name).glob("*")))
                print(f"      {dir_name}: {file_count} files")

    def run_all_tests(self, component: str = None):
        """Run all sandbox tests"""
        print_header("🛡️ Silver Tier Sandbox Tester")
        print_info("All tests run locally - NO external API calls")
        print_info(f"Vault: {VAULT_DIR}\n")
        
        # Define test suites
        test_suites = {
            "mcp": [
                ("MCP Server Health", self.test_mcp_health),
                ("MCP Actions List", self.test_mcp_actions_list),
            ],
            "watcher": [
                ("Filesystem Watcher", self.test_filesystem_watcher),
            ],
            "services": [
                ("Plan Generator", self.test_plan_generator),
                ("Approval Request", self.test_approval_request),
                ("LinkedIn Mock", self.test_linkedin_mock),
            ],
            "scheduler": [
                ("Cron Runner", self.test_cron_runner),
            ],
            "vault": [
                ("Vault Structure", self.test_vault_structure),
            ]
        }
        
        # Determine which suites to run
        if component:
            suites_to_run = {component: test_suites[component]} if component in test_suites else {}
            if not suites_to_run:
                print_warning(f"Unknown component: {component}")
                print_info(f"Valid components: {', '.join(test_suites.keys())}")
                return
        else:
            suites_to_run = test_suites
        
        # Run tests
        for suite_name, tests in suites_to_run.items():
            print_header(f"📦 {suite_name.upper()} Tests")
            for test_name, test_func in tests:
                self.run_test(test_name, test_func)
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print_header("📊 Test Summary")
        
        total = self.test_results["passed"] + self.test_results["failed"]
        
        print(f"  Total Tests:  {total}")
        print(f"  {Colors.GREEN}Passed:  {self.test_results['passed']}{Colors.RESET}")
        print(f"  {Colors.RED}Failed:  {self.test_results['failed']}{Colors.RESET}")
        
        if self.test_results["failed"] > 0:
            print(f"\n{Colors.YELLOW}Failed Tests:{Colors.RESET}")
            for test in self.test_results["tests"]:
                if test["status"] == "FAILED":
                    print(f"  - {test['name']}: {test.get('error', 'Unknown error')}")
        
        print(f"\n  Success Rate: {self.test_results['passed']/total*100:.1f}%" if total > 0 else "  No tests run")
        
        if self.test_results["failed"] == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All tests passed! Safe to use.{Colors.RESET}\n")
        else:
            print(f"\n{Colors.YELLOW}⚠ Some tests failed. Review output above.{Colors.RESET}\n")


def main():
    import os
    
    parser = argparse.ArgumentParser(description="Silver Tier Sandbox Tester")
    parser.add_argument(
        "--component",
        type=str,
        choices=["mcp", "watcher", "services", "scheduler", "vault"],
        help="Test specific component only"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    try:
        tester = SandboxTester(verbose=args.verbose)
        tester.run_all_tests(component=args.component)
        
        if args.json:
            print(json.dumps(tester.test_results, indent=2, default=str))
        
        # Exit with error code if tests failed
        sys.exit(0 if tester.test_results["failed"] == 0 else 1)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.RESET}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
