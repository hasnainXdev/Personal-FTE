# Tasks: AI Employee Vault — Bronze Tier

**Input**: Design documents from `/specs/001-ai-employee-vault/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks following TDD principles. Tests should be written FIRST, verified to FAIL, then implementation makes them PASS.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `ai_employee/src/`, `ai_employee/tests/`
- Paths shown below assume single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create ai_employee project directory at repository root
- [X] T002 [P] Initialize UV project with `uv init ai_employee` in ai_employee/
- [X] T003 [P] Add dependencies to pyproject.toml: watchdog, pydantic, rich, typer, markdown
- [X] T004 [P] Add dev dependencies: pytest, pytest-asyncio
- [X] T005 Create src/ai_employee package structure with __init__.py files
- [X] T006 [P] Configure pytest in pyproject.toml (testpaths, async mode)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 [P] Create VaultState enum (inbox, needs_action, done) in src/ai_employee/models/vault.py
- [X] T008 [P] Create Source enum (gmail, filesystem) in src/ai_employee/models/vault.py
- [X] T009 Create VaultItem Pydantic model with all fields in src/ai_employee/models/vault.py
- [X] T010 [P] Create VaultService class skeleton in src/ai_employee/services/vault.py
- [X] T011 Implement create_vault_structure() method in VaultService
- [X] T012 Implement atomic file write with locking in VaultService.write_item()
- [X] T013 Implement file move with state validation in VaultService.move_item()
- [X] T014 [P] Create IdempotencyRegistry class in src/ai_employee/services/registry.py
- [X] T015 Implement is_processed() and mark_processed() methods using SHA256 hashing
- [X] T016 [P] Create DashboardLogger class in src/ai_employee/services/logger.py
- [X] T017 Implement log_entry() method appending to Dashboard.md table
- [X] T018 [P] Create error taxonomy module in src/ai_employee/errors.py
- [X] T019 Define all error classes (VaultCreationError, FileLockTimeout, etc.) with error codes

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Establish Local AI Employee System (Priority: P1) 🎯 MVP

**Goal**: Set up a local AI employee that operates autonomously within an Obsidian vault, creating required vault structure and processing inputs

**Independent Test**: Verify AI employee can read/write to Obsidian vault, monitor inputs, and execute basic tasks without cloud services or manual intervention

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T020 [P] [US1] Create test_vault_service.py in tests/unit/
- [X] T021 [P] [US1] Test create_vault_structure() creates Inbox/, Needs_Action/, Done/ in tests/unit/test_vault_service.py
- [X] T022 [P] [US1] Test write_item() creates valid markdown file in tests/unit/test_vault_service.py
- [X] T023 [P] [US1] Test move_item() transitions states correctly in tests/unit/test_vault_service.py
- [X] T024 [US1] Create integration test for vault initialization in tests/integration/test_vault_operations.py
- [X] T025 [US1] Verify vault structure exists after service init in tests/integration/test_vault_operations.py

### Implementation for User Story 1

- [X] T026 [P] [US1] Create CLI entry point with typer in src/ai_employee/main.py
- [X] T027 [P] [US1] Implement `ai-employee start` command in src/ai_employee/main.py
- [X] T028 [P] [US1] Implement `ai-employee status` command in src/ai_employee/main.py
- [X] T029 [P] [US1] Implement `ai-employee process <path>` command in src/ai_employee/main.py
- [X] T030 [US1] Integrate VaultService with CLI start command
- [X] T031 [US1] Add Qwen CLI validation via `qwen --version` check in main.py
- [X] T032 [US1] Create Company_Handbook.md template in AI_Employee_Vault/
- [X] T033 [US1] Create Agent_Skills.md template with ProcessFile skill definition
- [X] T034 [US1] Initialize Dashboard.md with header and empty table
- [X] T035 [US1] Add logging for all US1 operations to Dashboard.md

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Monitor Input Sources (Priority: P1)

**Goal**: AI employee monitors Gmail inbox OR filesystem location, detecting and processing new information automatically

**Independent Test**: Place sample inputs in monitored source and verify AI employee detects and processes them appropriately

### Tests for User Story 2 ⚠️

- [X] T036 [P] [US2] Create test_watcher.py in tests/unit/
- [X] T037 [P] [US2] Test FilesystemWatcher detects new .md files in tests/unit/test_watcher.py
- [X] T038 [P] [US2] Test watcher respects poll interval (30s default) in tests/unit/test_watcher.py
- [X] T039 [US2] Create integration test for watcher in tests/integration/test_watcher_integration.py
- [X] T040 [US2] Verify input detection triggers processing within 30s (SC-003) in tests/integration/

### Implementation for User Story 2

- [X] T041 [P] [US2] Create WatcherConfig Pydantic model in src/ai_employee/models/config.py
- [X] T042 [P] [US2] Create FilesystemConfig schema model in src/ai_employee/models/config.py
- [X] T043 [P] [US2] Create GmailConfig schema model in src/ai_employee/models/config.py
- [X] T044 [US2] Create WatcherService abstract base class in src/ai_employee/services/watcher.py
- [X] T045 [US2] Implement FilesystemWatcher using watchdog in src/ai_employee/services/watcher.py
- [X] T046 [US2] Implement on_created event handler with debounce (500ms)
- [X] T047 [US2] Implement start() and stop() methods for watcher lifecycle
- [X] T048 [US2] Create config loader for .ai_employee/config.json
- [X] T049 [US2] Implement health_check() for watcher connectivity
- [X] T050 [US2] Add error handling: WatcherConnectionError, WatcherTimeout
- [X] T051 [US2] Integrate watcher with VaultService for input processing trigger
- [X] T052 [US2] Log watcher events to Dashboard.md

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Organize Information into Task States (Priority: P2)

**Goal**: AI employee organizes information into structured task states (Inbox → Needs_Action → Done) for easy tracking

**Independent Test**: Provide inputs and verify they are correctly placed in appropriate vault folders based on state

### Tests for User Story 3 ⚠️

- [X] T053 [P] [US3] Create test_state_transitions.py in tests/unit/
- [X] T054 [P] [US3] Test inbox→needs_action transition in tests/unit/test_state_transitions.py
- [X] T055 [P] [US3] Test needs_action→done transition in tests/unit/test_state_transitions.py
- [X] T056 [P] [US3] Test inbox→done direct transition (no action needed) in tests/unit/test_state_transitions.py
- [X] T057 [US3] Create integration test for 100 file transitions in tests/integration/test_vault_operations.py (SC-005)

### Implementation for User Story 3

- [X] T058 [P] [US3] Create state transition validator in src/ai_employee/services/vault.py
- [X] T059 [US3] Implement transition rules: inbox→needs_action, needs_action→done, inbox→done
- [X] T060 [US3] Add InvalidTransitionError for invalid state changes
- [X] T061 [US3] Implement atomic file move with rollback on failure
- [X] T062 [US3] Create state query methods: list_items(state), get_item_state(id)
- [X] T063 [US3] Add state transition logging to Dashboard.md
- [X] T064 [US3] Implement file locking during transitions (fcntl)
- [X] T065 [US3] Add retry mechanism for transient lock failures (3 attempts, exponential backoff)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Execute Defined Agent Skills (Priority: P2)

**Goal**: AI employee executes predefined agent skills as documented in Agent_Skills.md with proper input/output handling

**Independent Test**: Invoke specific agent skills and verify they execute correctly with appropriate input/output formats

### Tests for User Story 4 ⚠️

- [X] T066 [P] [US4] Create test_skill_executor.py in tests/unit/
- [X] T067 [P] [US4] Test skill loading from Agent_Skills.md in tests/unit/test_skill_executor.py
- [X] T068 [P] [US4] Test input validation against skill schema in tests/unit/test_skill_executor.py
- [X] T069 [P] [US4] Test output validation against skill schema in tests/unit/test_skill_executor.py
- [X] T070 [US4] Create contract test for ProcessFile skill in tests/contract/test_skill_contracts.py
- [X] T071 [US4] Test failure handling: skill error logged to Dashboard in tests/unit/test_skill_executor.py
- [X] T072 [US4] Verify skill execution meets SC-004 in tests/integration/

### Implementation for User Story 4

- [X] T073 [P] [US4] Create AgentSkill Pydantic model in src/ai_employee/models/skill.py
- [X] T074 [P] [US4] Create SkillResult model in src/ai_employee/models/skill.py
- [X] T075 [US4] Create SkillExecutor class in src/ai_employee/services/executor.py
- [X] T076 [US4] Implement load_skills() parsing Agent_Skills.md
- [X] T077 [US4] Implement validate_input() using JSON Schema or markdown template
- [X] T078 [US4] Implement validate_output() for skill output validation
- [X] T079 [US4] Implement execute_skill() with error handling
- [X] T080 [US4] Create ProcessFile skill in src/ai_employee/skills/process_file.py
- [X] T081 [US4] Implement ProcessFile input/output format handling
- [X] T082 [US4] Add skill execution logging to Dashboard.md
- [X] T083 [US4] Implement failure handling: log error, move to Needs_Action for review
- [X] T084 [US4] Add execution count and last_executed tracking
- [X] T085 [US4] Create ProcessEmail skill skeleton in src/ai_employee/skills/process_email.py (Gmail support)

**Checkpoint**: User Stories 1-4 should all work independently with at least one working skill (ProcessFile)

---

## Phase 7: User Story 5 - Maintain Operational Log (Priority: P3)

**Goal**: AI employee maintains operational log in Dashboard.md for monitoring activities and troubleshooting

**Independent Test**: Perform various operations and verify they are correctly logged in Dashboard.md with complete information

### Tests for User Story 5 ⚠️

- [X] T086 [P] [US5] Create test_dashboard_logger.py in tests/unit/
- [X] T087 [P] [US5] Test log_entry() appends correct markdown row in tests/unit/test_dashboard_logger.py
- [X] T088 [P] [US5] Test get_recent_logs() returns entries in tests/unit/test_dashboard_logger.py
- [X] T089 [US5] Verify 100% logging coverage in tests/integration/ (SC-006)
- [X] T090 [US5] Test log archive functionality in tests/unit/test_dashboard_logger.py

### Implementation for User Story 5

- [X] T091 [P] [US5] Create LogEntry Pydantic model in src/ai_employee/models/logger.py
- [X] T092 [P] [US5] Create LogOutcome enum (success, failure, skipped) in src/ai_employee/models/logger.py
- [X] T093 [US5] Implement to_markdown_row() method for LogEntry
- [X] T094 [US5] Implement get_recent_logs(limit) in DashboardLogger
- [X] T095 [US5] Implement archive_old_logs(cutoff_date) creating Archive/YYYY-MM.md
- [X] T096 [US5] Add log rotation when entries exceed 1000
- [X] T097 [US5] Ensure all services log to Dashboard.md after operations
- [X] T098 [US5] Add duration_ms tracking for all logged operations
- [X] T099 [US5] Implement structured logging format with timestamps

**Checkpoint**: All 5 user stories complete with comprehensive operational logging

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T100 [P] Create quickstart.md validation script to verify setup steps
- [X] T101 [P] Add comprehensive docstrings to all public methods
- [X] T102 [P] Create README.md for ai_employee package
- [X] T103 Code cleanup: remove unused imports, fix type hints
- [X] T104 [P] Add unit tests for models in tests/unit/test_models.py
- [X] T105 [P] Add unit tests for executor in tests/unit/test_executor.py
- [X] T106 [P] Add unit tests for registry in tests/unit/test_registry.py
- [X] T107 Security: validate file paths to prevent directory traversal
- [X] T108 Performance: add caching for frequently accessed vault items
- [X] T109 [P] Create .env.example with GMAIL_APP_PASSWORD placeholder
- [X] T110 [P] Add environment variable loading for sensitive config
- [X] T111 Run full test suite and fix any failures
- [X] T112 Verify all success criteria (SC-001 through SC-008) with integration tests
- [X] T113 Create CHANGELOG.md with version history
- [X] T114 [P] Add CI configuration (GitHub Actions) for automated testing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent, can run in parallel with US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on VaultService from foundation
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Depends on VaultService, benefits from US3
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Independent but integrates with all stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Models before services
- Services before integration
- Core implementation before cross-cutting concerns
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003, T004, T006 can all run in parallel (different files)

**Phase 2 (Foundational)**:
- T007, T008, T010, T014, T016, T018 can run in parallel
- T009 depends on T007, T008
- T011, T012, T013 depend on T010
- T015 depends on T014
- T017 depends on T016

**Phase 3+ (User Stories)**:
- Once Phase 2 completes, all user story phases can start in parallel
- Within each story, tests (marked [P]) can run in parallel
- Models within a story (marked [P]) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "T020 [P] [US1] Create test_vault_service.py in tests/unit/"
Task: "T021 [P] [US1] Test create_vault_structure() in tests/unit/test_vault_service.py"
Task: "T022 [P] [US1] Test write_item() in tests/unit/test_vault_service.py"
Task: "T023 [P] [US1] Test move_item() in tests/unit/test_vault_service.py"

# Launch all CLI commands for User Story 1 together:
Task: "T026 [P] [US1] Create CLI entry point in src/ai_employee/main.py"
Task: "T027 [P] [US1] Implement `ai-employee start` command"
Task: "T028 [P] [US1] Implement `ai-employee status` command"
Task: "T029 [P] [US1] Implement `ai-employee process <path>` command"
```

---

## Parallel Example: User Story 2

```bash
# Launch all models for User Story 2 together:
Task: "T041 [P] [US2] Create WatcherConfig model in src/ai_employee/models/config.py"
Task: "T042 [P] [US2] Create FilesystemConfig model in src/ai_employee/models/config.py"
Task: "T043 [P] [US2] Create GmailConfig model in src/ai_employee/models/config.py"

# Launch all tests for User Story 2 together:
Task: "T036 [P] [US2] Create test_watcher.py in tests/unit/"
Task: "T037 [P] [US2] Test FilesystemWatcher detects new files"
Task: "T038 [P] [US2] Test watcher respects poll interval"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T019)
3. Complete Phase 3: User Story 1 (T020-T035)
4. **STOP and VALIDATE**: 
   - Run `uv run pytest tests/unit/test_vault_service.py`
   - Run `uv run pytest tests/integration/test_vault_operations.py`
   - Verify `ai-employee start` creates vault structure
   - Verify `ai-employee status` shows system state
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T020-T035)
   - Developer B: User Story 2 (T036-T052)
   - Developer C: User Story 3 (T053-T065)
3. After US1-3 complete:
   - Developer A: User Story 4 (T066-T085)
   - Developer B: User Story 5 (T086-T099)
4. Team completes Polish phase together

---

## Task Summary

| Phase | Task Count | Description |
|-------|------------|-------------|
| Phase 1: Setup | 6 | Project initialization |
| Phase 2: Foundational | 13 | Core infrastructure |
| Phase 3: US1 | 16 | Establish local AI employee system |
| Phase 4: US2 | 17 | Monitor input sources |
| Phase 5: US3 | 13 | Organize into task states |
| Phase 6: US4 | 20 | Execute agent skills |
| Phase 7: US5 | 14 | Maintain operational log |
| Phase 8: Polish | 15 | Cross-cutting concerns |
| **Total** | **114** | Complete implementation |

### Task Count per User Story

- **US1**: 16 tasks (T020-T035)
- **US2**: 17 tasks (T036-T052)
- **US3**: 13 tasks (T053-T065)
- **US4**: 20 tasks (T066-T085)
- **US5**: 14 tasks (T086-T099)

### MVP Scope (User Story 1 Only)

Minimum viable product includes:
- Vault structure creation (Inbox/, Needs_Action/, Done/)
- CLI commands: start, status, process
- Basic file read/write operations
- Company_Handbook.md and Agent_Skills.md templates
- Dashboard.md initialization
- Qwen CLI validation

**MVP Tasks**: T001-T035 (35 tasks total)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Success Criteria Validation

After completing all phases, verify:

- [ ] SC-001: Vault structure exists within 5 minutes of initialization
- [ ] SC-002: Qwen CLI reads/writes markdown with 95% reliability (100 test ops)
- [ ] SC-003: Watcher triggers within 30 seconds of input detection
- [ ] SC-004: At least one working Agent Skill (ProcessFile)
- [ ] SC-005: File transitions correct with 98% accuracy (100 test cases)
- [ ] SC-006: Dashboard.md logs 100% of operations with complete info
- [ ] SC-007: System operates without manual intervention
- [ ] SC-008: System runs entirely locally (no Docker/Kubernetes)
