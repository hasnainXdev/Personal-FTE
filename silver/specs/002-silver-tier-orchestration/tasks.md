# Tasks: Silver Tier Orchestration

**Input**: Design documents from `/specs/002-silver-tier-orchestration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Manual scenario testing per quickstart.md validation checklists. Automated tests are OPTIONAL.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Vault Structure**: `AI_Employee_Vault/` at repository root
- **Skills**: `AI_Employee_Vault/Skills/Silver/` for new Silver skills
- **Scripts**: `scripts/watchers/`, `scripts/scheduler/` at repository root
- **MCP Server**: `mcp_server/` at repository root
- **Logs**: `Logs_Extended/` in vault

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Silver Tier vault directories: Plans/, Proposed_Actions/, Scheduled_Tasks/, Logs_Extended/
- [ ] T002 [P] Create MCP server directory structure: mcp_server/, mcp_server/actions/, mcp_server/logs/
- [ ] T003 [P] Create scripts directory structure: scripts/watchers/, scripts/scheduler/
- [ ] T004 Initialize UV Python environment with dependencies (fastapi, uvicorn, httpx, google-auth, google-auth-oauthlib)
- [ ] T005 [P] Create .env template file with MCP_PORT, GMAIL_OAUTH_TOKEN, SMTP credentials placeholders

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create MCP server base: mcp_server/server.py with HTTP localhost:8765, /health endpoint, /execute endpoint
- [ ] T007 [P] Create MCP logging infrastructure: mcp_server/logs/mcp_actions.md with append-only format
- [ ] T008 [P] Create Dashboard.md extension sections: Watcher Triggers, Plan Creations, Approval Decisions, MCP Actions, Scheduled Tasks
- [ ] T009 Create base watcher utility: scripts/watchers/base_watcher.py with Watcher abstract class (poll, mark_processed, get_last_check, restart)
- [ ] T010 [P] Create duplicate detection persistence: scripts/watchers/duplicate_tracker.py with file-based ID storage, pruning at 1000 IDs
- [ ] T011 Create Bronze routing utility: scripts/watchers/bronze_router.py to route watcher outputs to Inbox/{item_id}.md format
- [ ] T012 Setup cron configuration template: scripts/scheduler/cron_template.sh with example entries for watchers and daily summary

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Multi-Channel Input Processing (Priority: P1) 🎯 MVP

**Goal**: Implement 2+ independent watchers (Gmail, Filesystem) that route to Bronze Inbox without interference

**Independent Test**: Configure both watchers, trigger inputs on both channels within same minute, verify both logged in Dashboard.md and processed through Bronze intake without data loss or duplication

### Implementation for User Story 1

- [ ] T013 [P] [US1] Create Gmail watcher skill definition: AI_Employee_Vault/Skills/Silver/watcher-gmail.md with polling interface, 60s interval, OAuth config
- [ ] T014 [P] [US1] Create Filesystem watcher skill definition: AI_Employee_Vault/Skills/Silver/watcher-filesystem.md with directory polling, 60s interval, file pattern config
- [ ] T015 [P] [US1] Implement Gmail watcher script: scripts/watchers/gmail_watcher.py with OAuth polling, InputItem extraction, duplicate detection
- [ ] T016 [P] [US1] Implement Filesystem watcher script: scripts/watchers/filesystem_watcher.py with directory scan, file content extraction, duplicate detection
- [ ] T017 [US1] Create watcher state persistence: Logs_Extended/watcher_gmail_state.md, Logs_Extended/watcher_filesystem_state.md with last_check_timestamp, processed_ids[]
- [ ] T018 [US1] Implement watcher-to-Inbox routing: scripts/watchers/gmail_watcher.py and filesystem_watcher.py write to Inbox/{MSG_ID}.md with Source, Source_ID, Received metadata
- [ ] T019 [US1] Add watcher logging to Dashboard.md: Each poll logs timestamp, watcher name, items found, status, duration to Watcher Triggers table
- [ ] T020 [US1] Create watcher restart safety: scripts/watchers/gmail_watcher.py and filesystem_watcher.py load state on start, handle missed executions with catch-up poll
- [ ] T021 [US1] Test duplicate detection: Run both watchers, mark items processed, restart watchers, verify no reprocessing of same IDs

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - both watchers operate without interference, duplicate detection works, Bronze Inbox receives inputs

---

## Phase 4: User Story 2 - Structured Plan Generation (Priority: P1)

**Goal**: Automatic Plan.md generation for multi-step tasks, external actions, and high-risk workflows

**Independent Test**: Trigger a task requiring multiple steps, verify Plan.md is created with objective, steps, expected outcome, and risk level before any execution begins

### Implementation for User Story 2

- [ ] T022 [P] [US2] Create Plan.md template: AI_Employee_Vault/Plans/Plan_template.md with Title, Objective, Risk_Level, Approval_Required, Steps[], Expected_Outcome, Rollback_Strategy fields
- [ ] T023 [P] [US2] Create Plan Generator skill definition: AI_Employee_Vault/Skills/Silver/plan-generator.md with trigger conditions (multi-step, external action, high-risk)
- [ ] T024 [US2] Implement Plan Generator service: scripts/services/plan_generator.py with risk assessment heuristics (Low/Medium/High), step extraction, template population
- [ ] T025 [US2] Implement plan storage: scripts/services/plan_generator.py saves Plan_{YYYYMMDD}_{NN}.md to Plans/ directory with sequential numbering
- [ ] T026 [US2] Add plan creation logging: scripts/services/plan_generator.py logs to Dashboard.md Plan Creations section with timestamp, Plan ID, risk level, approval required flag
- [ ] T027 [US2] Integrate with Task Classifier: Bronze task-classifier.md routes complex tasks to Plan Generator skill before execution
- [ ] T028 [US2] Test plan generation triggers: Create multi-step task, verify Plan.md created before execution, verify all required fields populated

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - watchers feed inbox, complex tasks trigger plan generation

---

## Phase 5: User Story 3 - Human Approval Workflow (Priority: P1)

**Goal**: Prevent unsafe auto-execution by requiring human approval for external actions

**Independent Test**: Trigger an action requiring approval (e.g., LinkedIn post), verify Proposed_Action.md is created, wait for manual approval marking, then verify execution only proceeds after "Approved: Yes" is set

### Implementation for User Story 3

- [ ] T029 [P] [US3] Create Proposed_Action.md template: AI_Employee_Vault/Proposed_Actions/Action_template.md with Title, Plan_Reference, Risk_Level, Summary, Approved (PENDING/Yes/No), Created, Reviewed, Result fields
- [ ] T030 [P] [US3] Create Approval Request skill definition: AI_Employee_Vault/Skills/Silver/approval-request.md with trigger conditions (external action, high-risk plan)
- [ ] T031 [US3] Implement Approval Request service: scripts/services/approval_request.py creates Proposed_Actions/Action_{YYYYMMDD}_{NN}.md with action summary, plan reference, risk level
- [ ] T032 [US3] Implement approval polling mechanism: scripts/services/approval_poller.py checks Proposed_Actions/*.md modification time every 60s, reads Approved field
- [ ] T033 [US3] Implement approval decision logging: scripts/services/approval_poller.py logs all decisions to Dashboard.md Approval Decisions section with timestamp, Action ID, decision, decision time
- [ ] T034 [US3] Implement execution halt logic: scripts/services/approval_poller.py does NOT execute action unless "Approved: Yes" is set
- [ ] T035 [US3] Implement rejection handling: scripts/services/approval_poller.py moves rejected actions to Done/Rejected, logs rejection reason
- [ ] T036 [US3] Test approval workflow: Create Proposed_Action.md with "Approved: PENDING", verify no execution, set "Approved: Yes", verify execution proceeds, set "Approved: No", verify rejection logged

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - watchers, planning, and approval workflow all functional

---

## Phase 6: User Story 4 - LinkedIn Content Automation (Priority: P2)

**Goal**: Generate LinkedIn post drafts, route through approval, execute via MCP, store post URL

**Independent Test**: Request LinkedIn post generation, verify draft is saved, approve it, verify post is published via MCP, verify LinkedIn URL is stored in vault

### Implementation for User Story 4

- [ ] T037 [P] [US4] Create LinkedIn Generator skill definition: AI_Employee_Vault/Skills/Silver/linkedin-generator.md with content generation triggers, draft storage
- [ ] T038 [P] [US4] Implement MCP LinkedIn action handler: mcp_server/actions/linkedin.py with post_linkedin action, OAuth integration, URL capture
- [ ] T039 [US4] Implement LinkedIn content generation: scripts/services/linkedin_generator.py generates Draft_LinkedIn_Post.md with post text, saves to Proposed_Actions/
- [ ] T040 [US4] Integrate LinkedIn draft with approval workflow: scripts/services/linkedin_generator.py triggers Approval Request skill after draft creation
- [ ] T041 [US4] Implement MCP execution on approval: scripts/services/approval_poller.py calls POST /execute on mcp_server with action=post_linkedin after "Approved: Yes"
- [ ] T042 [US4] Implement LinkedIn URL storage: mcp_server/actions/linkedin.py captures post_url from LinkedIn API response, stores in vault (e.g., Logs_Extended/linkedin_posts.md)
- [ ] T043 [US4] Add LinkedIn action logging: mcp_server/logs/mcp_actions.md logs full request/response for post_linkedin actions
- [ ] T044 [US4] Test LinkedIn automation: Request post, verify draft saved, approve, verify MCP executes post, verify URL stored in vault

**Checkpoint**: At this point, User Stories 1-4 should all work - full LinkedIn automation chain functional (draft → approval → MCP → URL storage)

---

## Phase 7: User Story 5 - Scheduled Autonomous Workflows (Priority: P2)

**Goal**: Execute routine tasks on schedule (daily summaries, periodic scanning) without user initiation

**Independent Test**: Configure a scheduled task (e.g., daily inbox scan at 9 AM), verify it triggers automatically at the scheduled time and logs execution in Dashboard.md

### Implementation for User Story 5

- [ ] T045 [P] [US5] Create Scheduled Task skill definition: AI_Employee_Vault/Skills/Silver/scheduler.md with cron configuration, task triggers, restart safety
- [ ] T046 [P] [US5] Create scheduled task template: AI_Employee_Vault/Scheduled_Tasks/Task_template.md with Name, Cron, Enabled, Last_Run, Next_Run, Task_Config fields
- [ ] T047 [US5] Implement daily summary scheduler: scripts/scheduler/daily_summary.py generates daily summary at configured time, logs to Dashboard.md
- [ ] T048 [US5] Implement watcher cron integration: scripts/scheduler/cron_runner.py triggers gmail_watcher.py and filesystem_watcher.py hourly via cron
- [ ] T049 [US5] Add scheduled task logging: scripts/scheduler/daily_summary.py and cron_runner.py log to Dashboard.md Scheduled Tasks section with timestamp, task name, next run, status
- [ ] T050 [US5] Implement missed schedule handling: scripts/scheduler/cron_runner.py checks last_run timestamp, executes with "missed_schedule: true" flag if system was off
- [ ] T051 [US5] Test scheduled execution: Configure daily summary at specific time, wait for scheduled time, verify automatic trigger and logging
- [ ] T052 [US5] Test restart consistency: Stop system, wait for scheduled time, restart system, verify missed task executes with proper logging

**Checkpoint**: At this point, User Stories 1-5 should all work - scheduled tasks execute automatically, restart-safe

---

## Phase 8: User Story 6 - External Action Execution via MCP (Priority: P2)

**Goal**: Centralize all external actions through MCP server for logging, safety, and audit boundary

**Independent Test**: Trigger an external action (e.g., send email), verify it routes through MCP server, verify action is logged with full context, verify no direct API calls bypass MCP

### Implementation for User Story 6

- [ ] T053 [P] [US6] Create MCP email action handler: mcp_server/actions/email.py with send_email action, SMTP integration, message_id capture
- [ ] T054 [P] [US6] Create MCP webhook action handler: mcp_server/actions/webhook.py with fetch_url and trigger_webhook actions, HTTP client, response parsing
- [ ] T055 [US6] Implement MCP request validation: mcp_server/server.py validates action type, parameters, timeout before execution
- [ ] T056 [US6] Implement MCP structured response format: mcp_server/server.py returns {success, result, error, error_code, duration_ms, request_id} for all actions
- [ ] T057 [US6] Implement MCP error taxonomy: mcp_server/server.py returns standard error codes (INVALID_REQUEST, ACTION_NOT_FOUND, AUTH_FAILED, TIMEOUT, RATE_LIMITED, INTERNAL_ERROR, SERVICE_UNAVAILABLE)
- [ ] T058 [US6] Add MCP security enforcement: mcp_server/server.py enforces timeouts (default 30s), rate limits, credential storage via environment variables
- [ ] T059 [US6] Test MCP email action: Trigger send_email via POST /execute, verify SMTP sends email, verify response includes message_id, verify log entry created
- [ ] T060 [US6] Test MCP failure handling: Trigger action with invalid credentials, verify error response, verify state not corrupted, verify error logged

**Checkpoint**: At this point, User Stories 1-6 should all work - MCP server handles all external actions (email, LinkedIn, webhook) with full logging

---

## Phase 9: User Story 7 - Skill Chaining and Orchestration (Priority: P3)

**Goal**: Chain multiple skills together in defined sequence (watcher → classifier → planner → executor → logger) for complex workflows

**Independent Test**: Trigger a workflow requiring skill chaining, verify each skill executes in declared order, verify dependencies are respected, verify no implicit chaining occurs

### Implementation for User Story 7

- [ ] T061 [P] [US7] Create Orchestrator skill definition: AI_Employee_Vault/Skills/Silver/orchestrator.md with skill dependency declarations, sequential execution logic
- [ ] T062 [P] [US7] Create skill declaration format: AI_Employee_Vault/Skills/Silver/skill_template.md with Skill_Type, Requires_Plan, Requires_Approval, Side_Effects, Dependencies fields
- [ ] T063 [US7] Implement skill dependency checker: scripts/services/orchestrator.py validates dependencies_satisfied() before each skill execution
- [ ] T064 [US7] Implement sequential chain executor: scripts/services/orchestrator.py executes skills in order: Inbox Intake → Classifier → Plan Generator → Approval Request → MCP Execution → State Mover → Logger
- [ ] T065 [US7] Add skill execution logging: scripts/services/orchestrator.py logs each skill execution to Dashboard.md with skill name, result, duration
- [ ] T066 [US7] Implement failure recovery logic: scripts/services/orchestrator.py halts chain on skill failure, logs error context, does not corrupt state
- [ ] T067 [US7] Prevent circular execution: scripts/services/orchestrator.py detects circular dependencies, raises error, logs to Dashboard.md
- [ ] T068 [US7] Test full chained workflow: Trigger watcher, verify chain executes in order, verify each skill logs execution, verify no implicit chaining
- [ ] T069 [US7] Test interrupted chain recovery: Trigger chain, simulate failure mid-chain, verify state not corrupted, verify error logged, verify recovery possible

**Checkpoint**: At this point, all 7 User Stories should work - full orchestration chain functional with dependency checking and failure recovery

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T070 [P] Create quickstart.md validation checklist: Verify all 7 user stories with independent test scenarios from quickstart.md
- [ ] T071 [P] Create README.md for Silver Tier: Overview, setup instructions, architecture diagram, troubleshooting guide
- [ ] T072 [P] Add environment variable documentation: .env.example with all required variables (GMAIL_OAUTH_TOKEN, SMTP credentials, MCP_PORT, LINKEDIN_ACCESS_TOKEN)
- [ ] T073 [P] Test restart safety: Stop system, restart, verify watchers resume, scheduled tasks continue, duplicate detection persists
- [ ] T074 [P] Test Bronze regression: Verify Bronze Inbox processing, classification, state movement, logging all still functional after Silver changes
- [ ] T075 [P] Run constitution re-check: Verify all 17 constitution principles still PASS after implementation complete
- [ ] T076 [P] Create troubleshooting guide: Common issues (watcher not triggering, MCP unreachable, approval not detected, Bronze regression) with diagnostic commands

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent, may integrate with US1
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Independent, depends on US2 for plan reference
- **User Story 4 (P2)**: Can start after US3 complete - Depends on approval workflow functional
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Independent, uses watchers from US1
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - Independent, MCP server from Phase 2
- **User Story 7 (P3)**: Can start after US1-US6 complete - Depends on all other skills functional

### Within Each User Story

- Models/skill definitions before services
- Services before integration
- Core implementation before testing
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T002, T003, T005 can run in parallel
- **Phase 2 (Foundational)**: T007, T008, T009, T010, T012 can run in parallel
- **Phase 3 (US1)**: T013, T014, T015, T016 can run in parallel (different watchers, different files)
- **Phase 4 (US2)**: T022, T023 can run in parallel
- **Phase 5 (US3)**: T029, T030 can run in parallel
- **Phase 6 (US4)**: T037, T038 can run in parallel
- **Phase 7 (US5)**: T045, T046 can run in parallel
- **Phase 8 (US6)**: T053, T054 can run in parallel
- **Phase 10 (Polish)**: T070, T071, T072, T073, T074, T075, T076 can run in parallel

---

## Parallel Example: User Story 1 (Multi-Channel Input Processing)

```bash
# Launch all watchers in parallel (different files, no dependencies):
Task: "Create Gmail watcher skill definition in AI_Employee_Vault/Skills/Silver/watcher-gmail.md"
Task: "Create Filesystem watcher skill definition in AI_Employee_Vault/Skills/Silver/watcher-filesystem.md"
Task: "Implement Gmail watcher script in scripts/watchers/gmail_watcher.py"
Task: "Implement Filesystem watcher script in scripts/watchers/filesystem_watcher.py"

# After watchers implemented, test in parallel:
Task: "Test Gmail watcher polling and duplicate detection"
Task: "Test Filesystem watcher polling and duplicate detection"
Task: "Test both watchers simultaneously, verify no interference"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T012) - CRITICAL: Blocks all stories
3. Complete Phase 3: User Story 1 (T013-T021)
4. **STOP and VALIDATE**: Run quickstart.md Phase 1 validation checklist
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Multi-Channel Watchers) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Plan Generation) → Test independently → Deploy/Demo
4. Add User Story 3 (Approval Workflow) → Test independently → Deploy/Demo
5. Add User Story 4 (LinkedIn Automation) → Test independently → Deploy/Demo
6. Add User Story 5 (Scheduling) → Test independently → Deploy/Demo
7. Add User Story 6 (MCP Centralization) → Test independently → Deploy/Demo
8. Add User Story 7 (Orchestration) → Test independently → Deploy/Demo
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Watchers)
   - Developer B: User Story 2 (Planning) + User Story 3 (Approval)
   - Developer C: User Story 6 (MCP Server)
3. After US1, US2, US3, US6 complete:
   - Developer A: User Story 4 (LinkedIn)
   - Developer B: User Story 5 (Scheduling)
   - Developer C: User Story 7 (Orchestration)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **CRITICAL**: After each phase, run validation gate before proceeding to next phase
- **CRITICAL**: If Bronze regression detected at any point, STOP immediately and fix before continuing
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

| Phase | User Story | Priority | Task Count | Task IDs |
|-------|-----------|----------|------------|----------|
| 1 | Setup | N/A | 5 | T001-T005 |
| 2 | Foundational | N/A | 7 | T006-T012 |
| 3 | US1: Multi-Channel Input | P1 | 9 | T013-T021 |
| 4 | US2: Plan Generation | P1 | 7 | T022-T028 |
| 5 | US3: Approval Workflow | P1 | 8 | T029-T036 |
| 6 | US4: LinkedIn Automation | P2 | 8 | T037-T044 |
| 7 | US5: Scheduling | P2 | 8 | T045-T052 |
| 8 | US6: MCP Execution | P2 | 8 | T053-T060 |
| 9 | US7: Orchestration | P3 | 9 | T061-T069 |
| 10 | Polish | N/A | 7 | T070-T076 |
| **Total** | | | **76** | |
