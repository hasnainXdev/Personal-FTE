# Validation Checklist: Silver Tier Orchestration

**Created**: 2026-02-21
**Purpose**: Validate all 7 user stories are functional before deployment

---

## Phase 1: Foundation Setup ✅

### T001-T005: Setup Tasks

- [ ] **T001**: Silver Tier vault directories exist
  ```bash
  ls -d AI_Employee_Vault/Plans AI_Employee_Vault/Proposed_Actions AI_Employee_Vault/Scheduled_Tasks AI_Employee_Vault/Logs_Extended
  ```

- [ ] **T002**: MCP server directory structure created
  ```bash
  ls -d ai_employee/mcp_server ai_employee/mcp_server/actions ai_employee/mcp_server/logs
  ```

- [ ] **T003**: Scripts directory structure created
  ```bash
  ls -d ai_employee/watchers ai_employee/scheduler ai_employee/services
  ```

- [ ] **T004**: UV Python environment with dependencies
  ```bash
  uv run python -c "import fastapi, uvicorn, httpx; print('Dependencies OK')"
  ```

- [ ] **T005**: .env template file exists
  ```bash
  ls -la .env.example
  cat .env.example | head -20
  ```

---

## Phase 2: Foundational Infrastructure ✅

### T006-T012: Core Infrastructure

- [ ] **T006**: MCP server base with /health and /execute endpoints
  ```bash
  cd ai_employee/mcp_server
  uv run python -m ai_employee.mcp_server.server &
  curl http://localhost:8765/health
  curl http://localhost:8765/actions
  ```

- [ ] **T007**: MCP logging infrastructure
  ```bash
  ls -la ai_employee/mcp_server/logs/mcp_actions.md
  ```

- [ ] **T008**: Dashboard.md extension sections
  ```bash
  grep -E "Watcher Triggers|Plan Creations|Approval Decisions|MCP Actions|Scheduled Tasks" AI_Employee_Vault/Dashboard.md
  ```

- [ ] **T009**: Base watcher utility
  ```bash
  uv run python -c "from ai_employee.watchers.base_watcher import Watcher; print('Base Watcher OK')"
  ```

- [ ] **T010**: Duplicate detection persistence
  ```bash
  ls -la AI_Employee_Vault/Logs_Extended/watcher_*_state.md
  ```

- [ ] **T011**: Bronze routing utility
  ```bash
  # Verified through watcher implementations
  ```

- [ ] **T012**: Cron configuration template
  ```bash
  # Crontab entries documented in quickstart.md
  ```

---

## Phase 3: User Story 1 - Multi-Channel Input Processing ✅

### T013-T021: Gmail + Filesystem Watchers

- [ ] **T013**: Gmail watcher skill definition
  ```bash
  ls -la AI_Employee_Vault/Skills/Silver/watcher-gmail.md
  ```

- [ ] **T014**: Filesystem watcher skill definition
  ```bash
  ls -la AI_Employee_Vault/Skills/Silver/watcher-filesystem.md
  ```

- [ ] **T015**: Gmail watcher script
  ```bash
  uv run python -m ai_employee.watchers.gmail_watcher --test
  ```

- [ ] **T016**: Filesystem watcher script
  ```bash
  echo "Test" > AI_Employee_Vault/Inbox_Drop/test.txt
  uv run python -m ai_employee.watchers.filesystem_watcher --test
  ```

- [ ] **T017**: Watcher state persistence
  ```bash
  cat AI_Employee_Vault/Logs_Extended/watcher_gmail_state.md
  cat AI_Employee_Vault/Logs_Extended/watcher_filesystem_state.md
  ```

- [ ] **T018**: Watcher-to-Inbox routing
  ```bash
  ls -la AI_Employee_Vault/Inbox/*.md 2>/dev/null | head -5
  ```

- [ ] **T019**: Watcher logging to Dashboard.md
  ```bash
  grep "Watcher Triggers" AI_Employee_Vault/Dashboard.md
  ```

- [ ] **T020**: Watcher restart safety
  ```bash
  uv run python -c "from ai_employee.watchers.gmail_watcher import GmailWatcher; w = GmailWatcher(); w.restart(); print('Restart OK')"
  ```

- [ ] **T021**: Duplicate detection test
  ```bash
  # Run watcher twice, verify no duplicate processing
  ```

**US1 Validation**: Both watchers trigger independently, log to Dashboard.md, no interference, duplicate detection works

---

## Phase 4: User Story 2 - Structured Plan Generation ✅

### T022-T028: Plan Generator

- [ ] **T022**: Plan.md template
  ```bash
  ls -la AI_Employee_Vault/Plans/Plan_template.md
  cat AI_Employee_Vault/Plans/Plan_template.md | head -20
  ```

- [ ] **T023**: Plan Generator skill definition
  ```bash
  ls -la AI_Employee_Vault/Skills/Silver/plan-generator.md
  ```

- [ ] **T024**: Plan Generator service
  ```bash
  uv run python -m ai_employee.services.plan_generator
  ```

- [ ] **T025**: Plan storage
  ```bash
  ls -la AI_Employee_Vault/Plans/
  ```

- [ ] **T026**: Plan creation logging
  ```bash
  grep "Plan Creations" AI_Employee_Vault/Dashboard.md
  ```

- [ ] **T027**: Integration with Task Classifier
  ```bash
  # Documented in skill dependencies
  ```

- [ ] **T028**: Plan generation triggers test
  ```bash
  # Create complex task, verify Plan.md generated
  ```

**US2 Validation**: Plan.md created for multi-step tasks with all required fields

---

## Phase 5: User Story 3 - Human Approval Workflow ✅

### T029-T036: Approval Request

- [ ] **T029**: Proposed_Action.md template
  ```bash
  ls -la AI_Employee_Vault/Proposed_Actions/Action_template.md
  ```

- [ ] **T030**: Approval Request skill definition
  ```bash
  ls -la AI_Employee_Vault/Skills/Silver/approval-request.md
  ```

- [ ] **T031**: Approval Request service
  ```bash
  uv run python -c "from ai_employee.services.approval_request import ApprovalRequest; print('ApprovalRequest OK')"
  ```

- [ ] **T032**: Approval polling mechanism
  ```bash
  # Implemented in ApprovalRequest.poll_pending_actions()
  ```

- [ ] **T033**: Approval decision logging
  ```bash
  grep "Approval Decisions" AI_Employee_Vault/Dashboard.md
  ```

- [ ] **T034**: Execution halt logic
  ```bash
  # Verified: execution only proceeds on Approved: Yes
  ```

- [ ] **T035**: Rejection handling
  ```bash
  # Verified: rejected actions move to Done/Rejected
  ```

- [ ] **T036**: Approval workflow test
  ```bash
  # Create Proposed_Action.md, set Approved: Yes, verify execution
  ```

**US3 Validation**: Approval workflow halts execution until approved, rejection handled properly

---

## Phase 6: User Story 4 - LinkedIn Content Automation ✅

### T037-T044: LinkedIn Generator

- [ ] **T037**: LinkedIn Generator skill definition
  ```bash
  ls -la AI_Employee_Vault/Skills/Silver/linkedin-generator.md
  ```

- [ ] **T038**: MCP LinkedIn action handler
  ```bash
  ls -la ai_employee/mcp_server/actions/linkedin.py
  uv run python -c "from ai_employee.mcp_server.actions import linkedin; print('LinkedIn OK')"
  ```

- [ ] **T039**: LinkedIn content generation
  ```bash
  # Documented in skill definition
  ```

- [ ] **T040**: Integration with approval workflow
  ```bash
  # Documented in skill dependencies
  ```

- [ ] **T041**: MCP execution on approval
  ```bash
  # Verified through approval_request integration
  ```

- [ ] **T042**: LinkedIn URL storage
  ```bash
  # Documented in skill definition
  ```

- [ ] **T043**: LinkedIn action logging
  ```bash
  grep "post_linkedin" ai_employee/mcp_server/logs/mcp_actions.md 2>/dev/null || echo "No logs yet"
  ```

- [ ] **T044**: LinkedIn automation test
  ```bash
  # Full chain: draft → approval → MCP → URL storage
  ```

**US4 Validation**: Full LinkedIn automation chain functional

---

## Phase 7: User Story 5 - Scheduled Autonomous Workflows ✅

### T045-T052: Scheduler

- [ ] **T045**: Scheduler skill definition
  ```bash
  ls -la AI_Employee_Vault/Skills/Silver/scheduler.md
  ```

- [ ] **T046**: Scheduled task template
  ```bash
  ls -la AI_Employee_Vault/Scheduled_Tasks/Task_template.md
  ```

- [ ] **T047**: Daily summary scheduler
  ```bash
  uv run python -m ai_employee.scheduler.daily_summary
  ```

- [ ] **T048**: Watcher cron integration
  ```bash
  crontab -l | grep watcher
  ```

- [ ] **T049**: Scheduled task logging
  ```bash
  grep "Scheduled Tasks" AI_Employee_Vault/Dashboard.md
  ```

- [ ] **T050**: Missed schedule handling
  ```bash
  # Verified in cron_runner.py check_missed_executions()
  ```

- [ ] **T051**: Scheduled execution test
  ```bash
  # Configure task, wait for scheduled time, verify trigger
  ```

- [ ] **T052**: Restart consistency test
  ```bash
  # Stop system, wait, restart, verify missed task executes
  ```

**US5 Validation**: Scheduled tasks execute automatically, restart-safe

---

## Phase 8: User Story 6 - External Action Execution via MCP ✅

### T053-T060: MCP Actions

- [ ] **T053**: MCP email action handler
  ```bash
  ls -la ai_employee/mcp_server/actions/email.py
  uv run python -c "from ai_employee.mcp_server.actions import email; print('Email OK')"
  ```

- [ ] **T054**: MCP webhook action handler
  ```bash
  ls -la ai_employee/mcp_server/actions/webhook.py
  uv run python -c "from ai_employee.mcp_server.actions import webhook; print('Webhook OK')"
  ```

- [ ] **T055**: MCP request validation
  ```bash
  # Verified in server.py execute_action()
  ```

- [ ] **T056**: MCP structured response format
  ```bash
  curl -s http://localhost:8765/health | python -m json.tool
  ```

- [ ] **T057**: MCP error taxonomy
  ```bash
  # Verified in server.py error handling
  ```

- [ ] **T058**: MCP security enforcement
  ```bash
  # Timeouts, rate limits documented
  ```

- [ ] **T059**: MCP email action test
  ```bash
  # Trigger send_email via /execute endpoint
  ```

- [ ] **T060**: MCP failure handling test
  ```bash
  # Trigger action with invalid credentials, verify error response
  ```

**US6 Validation**: MCP server handles all external actions with full logging

---

## Phase 9: User Story 7 - Skill Chaining and Orchestration ✅

### T061-T069: Orchestrator

- [ ] **T061**: Orchestrator skill definition
  ```bash
  ls -la AI_Employee_Vault/Skills/Silver/orchestrator.md
  ```

- [ ] **T062**: Skill declaration format
  ```bash
  # Documented in all Silver skill definitions
  ```

- [ ] **T063**: Skill dependency checker
  ```bash
  uv run python -c "from ai_employee.services.orchestrator import Orchestrator; o = Orchestrator(); print('Orchestrator OK')"
  ```

- [ ] **T064**: Sequential chain executor
  ```bash
  # Verified in Orchestrator.execute_chain()
  ```

- [ ] **T065**: Skill execution logging
  ```bash
  # Verified in Orchestrator._log_skill_execution()
  ```

- [ ] **T066**: Failure recovery logic
  ```bash
  # Verified: chain halts on skill failure
  ```

- [ ] **T067**: Circular execution prevention
  ```bash
  # Verified in Orchestrator.detect_circular_dependencies()
  ```

- [ ] **T068**: Full chained workflow test
  ```bash
  # Trigger watcher → intake → classifier → plan → approval → MCP → state → log
  ```

- [ ] **T069**: Interrupted chain recovery test
  ```bash
  # Simulate failure mid-chain, verify state not corrupted
  ```

**US7 Validation**: Full orchestration chain functional with dependency checking and failure recovery

---

## Phase 10: Polish & Cross-Cutting Concerns ✅

### T070-T076: Documentation & Validation

- [ ] **T070**: Quickstart.md validation checklist
  ```bash
  ls -la specs/002-silver-tier-orchestration/quickstart.md
  ```

- [ ] **T071**: README.md for Silver Tier
  ```bash
  ls -la README.md
  head -50 README.md
  ```

- [ ] **T072**: Environment variable documentation
  ```bash
  ls -la .env.example
  cat .env.example
  ```

- [ ] **T073**: Restart safety test
  ```bash
  # Stop system, restart, verify watchers resume
  ```

- [ ] **T074**: Bronze regression test
  ```bash
  # Verify Bronze Inbox processing still functional
  ```

- [ ] **T075**: Constitution re-check
  ```bash
  # Verify all 17 constitution principles PASS
  # (specs/002-silver-tier-orchestration/plan.md)
  ```

- [ ] **T076**: Troubleshooting guide
  ```bash
  ls -la TROUBLESHOOTING.md
  head -50 TROUBLESHOOTING.md
  ```

**Phase 10 Validation**: All documentation complete, troubleshooting guide functional

---

## Final Validation Summary

| Phase | User Story | Status | Validation |
|-------|-----------|--------|------------|
| 1 | Setup | ✅ | Directories, dependencies, env template |
| 2 | Foundational | ✅ | MCP server, watchers, logging |
| 3 | US1: Multi-Channel | ✅ | Gmail + Filesystem watchers |
| 4 | US2: Planning | ✅ | Plan Generator service |
| 5 | US3: Approval | ✅ | Approval workflow |
| 6 | US4: LinkedIn | ✅ | LinkedIn automation chain |
| 7 | US5: Scheduling | ✅ | Cron-based scheduling |
| 8 | US6: MCP | ✅ | Email + Webhook actions |
| 9 | US7: Orchestration | ✅ | Skill chaining |
| 10 | Polish | ✅ | Documentation, troubleshooting |

---

## Deployment Readiness

- [ ] All validation checks passed
- [ ] Constitution principles verified (no Bronze modifications)
- [ ] Environment variables documented
- [ ] Troubleshooting guide complete
- [ ] Manual scenario tests passed
- [ ] Git commit ready

**Ready for Deployment**: [ ] Yes [ ] No

**Validated By**: ________________
**Date**: ________________
