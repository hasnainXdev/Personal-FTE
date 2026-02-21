# Research & Design Decisions: Silver Tier Orchestration

**Feature**: Silver Tier Orchestration
**Created**: 2026-02-20
**Status**: Complete

---

## Decision 1: Watcher Interface Pattern

**Decision**: Polling-based watchers with 60-second intervals

**Rationale**: 
- Polling simpler than webhook setup for Gmail/LinkedIn
- 60s balances responsiveness with API rate limits
- Restart-safe: persist last_check_timestamp and processed_ids[]

**Alternatives Considered**:

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| Push-based webhooks | Real-time | Complex OAuth, firewall issues | Overkill for Silver Tier |
| 30s polling | Faster response | API rate limit risks | 60s sufficient for business use |
| 5min polling | API-friendly | Slow response | 60s better UX |

**Implementation Pattern**:
```python
class Watcher:
    def __init__(self, name, interval_seconds=60):
        self.name = name
        self.last_check = load_timestamp()
        self.processed_ids = load_processed_ids()
    
    def poll(self):
        items = fetch_items_since(self.last_check)
        new_items = [i for i in items if i.id not in self.processed_ids]
        return new_items
    
    def mark_processed(self, item_id):
        self.processed_ids.append(item_id)
        save_processed_ids(self.processed_ids)
```

---

## Decision 2: Duplicate Detection Strategy

**Decision**: Persistent ID tracking with file-based storage

**Rationale**:
- Survives restarts (unlike in-memory sets)
- Simple append-only format
- Vault-compatible (Markdown/JSON)

**Storage Format**: `Watcher/{name}_processed.md`
```markdown
# Processed IDs: Gmail Watcher

- MSG_20260220_001
- MSG_20260220_002
- MSG_20260220_003
```

**Cleanup Strategy**: Remove IDs older than 30 days to prevent unbounded growth

---

## Decision 3: MCP Server Architecture

**Decision**: HTTP localhost server (port 8765)

**Rationale**:
- Simple Python implementation (http.server or FastAPI)
- WSL ↔ Windows interop friendly
- Easy testing with curl/Postman
- Clear network boundary (no direct API calls from skills)

**Alternatives Considered**:

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| stdio pipes | No network overhead | Complex process management | HTTP simpler for WSL |
| Unix sockets | Fast, secure | Windows compatibility issues | WSL needs cross-platform |
| HTTP localhost | Universal, testable | Minimal overhead | ✅ Selected |

**Server Structure**:
```
mcp_server/
├── server.py              # HTTP server on localhost:8765
├── actions/
│   ├── email.py           # send_email action
│   ├── linkedin.py        # post_linkedin action
│   └── webhook.py         # fetch_url action
└── logs/
    └── mcp_actions.md     # Append-only action log
```

**Request/Response Format**:
```json
// POST /execute
{
  "action": "post_linkedin",
  "parameters": {
    "content": "Post text here",
    "draft_url": "Plans/LinkedIn_Draft_20260220.md"
  },
  "timeout_ms": 30000
}

// Response
{
  "success": true,
  "result": {
    "post_url": "https://linkedin.com/posts/..."
  },
  "error": null
}
```

---

## Decision 4: Scheduling Implementation

**Decision**: Native cron (Linux/WSL) with Python wrapper

**Rationale**:
- No external dependencies
- System-level reliability
- Well-documented, debuggable
- WSL cron can trigger Python scripts

**Alternatives Considered**:

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| APScheduler library | Python-native, flexible | Extra dependency | cron sufficient |
| Windows Task Scheduler | Windows-native | WSL interop complex | cron in WSL simpler |
| Custom Python loop | Full control | Restart complexity | cron handles restart |

**Cron Configuration**:
```bash
# Daily summary at 9 AM
0 9 * * * cd /mnt/d/it-course/hackathons/personal-FTE/silver && uv run python scripts/scheduler/daily_summary.py >> Logs_Extended/scheduler.md 2>&1

# Inbox scan every hour
0 * * * * cd /mnt/d/it-course/hackathons/personal-FTE/silver && uv run python scripts/watchers/gmail_watcher.py >> Logs_Extended/watcher.md 2>&1
```

**Missed Execution Handling**: 
- Cron jobs check last_run timestamp
- If missed run detected (system was off), execute on next start with "missed_schedule: true" flag

---

## Decision 5: Plan Generation Triggers

**Decision**: Rule-based trigger conditions

**Trigger Conditions** (any triggers Plan.md generation):

1. **Multi-step execution**: Task requires 3+ skill invocations
2. **External action**: Any MCP server call required
3. **Risk level**: Classifier marks task as "High" risk
4. **Business posting**: LinkedIn or external communication detected

**Risk Assessment Heuristics**:

| Condition | Risk Level | Approval Required |
|-----------|------------|-------------------|
| Internal state change only | Low | No |
| Single external read (fetch) | Low | No |
| Single external write (post/email) | Medium | Yes |
| Multi-step external workflow | High | Yes |
| Irreversible action (delete) | High | Yes |

---

## Decision 6: Approval Workflow Pattern

**Decision**: File-based approval with modification-time polling

**Rationale**:
- Obsidian-compatible (edit Proposed_Action.md in vault)
- No separate approval UI needed
- Polling simple (check file mtime)
- Audit trail automatic (file history)

**Approval Flow**:

```
1. AI creates: Proposed_Actions/Action_20260220_001.md
   ---
   Title: Post LinkedIn update
   Plan Reference: Plans/Plan_20260220_001.md
   Risk Level: Medium
   Approved: [PENDING]
   Created: 2026-02-20T10:30:00Z
   ---

2. Human reviews in Obsidian, edits:
   Approved: Yes
   (file mtime updates)

3. Polling detects mtime change, reads Approved field

4. If "Yes" → execute via MCP
   If "No" → log rejection, move to Done/Rejected
```

**Polling Implementation**:
```python
def check_approvals():
    for action_file in glob("Proposed_Actions/*.md"):
        mtime = get_mtime(action_file)
        if mtime > last_poll_time:
            content = read_file(action_file)
            if "Approved: Yes" in content:
                execute_action(action_file)
```

---

## Decision 7: Skill Chaining Orchestration

**Decision**: Declarative dependency graph with sequential executor

**Rationale**:
- Explicit dependencies prevent implicit coupling
- Sequential execution simplifies debugging
- Failure recovery straightforward

**Skill Declaration Format**:
```markdown
---
Skill: Plan Generator
Type: Internal
Requires_Plan: No
Requires_Approval: No
Side_Effects: Creates Plan.md in vault
Dependencies:
  - Inbox Intake (must complete first)
  - Task Classifier (must complete first)
---
```

**Orchestration Logic**:
```python
def execute_chain(trigger_event):
    chain = [
        "Inbox Intake",
        "Task Classifier", 
        "Plan Generator",      # if multi-step
        "Approval Request",    # if external action
        "MCP Execution",       # if approved
        "Task State Mover",
        "Dashboard Logger"
    ]
    
    for skill_name in chain:
        skill = load_skill(skill_name)
        if not skill.dependencies_satisfied():
            raise Error(f"Dependencies not met for {skill_name}")
        
        result = skill.execute(trigger_event)
        log_skill_execution(skill_name, result)
```

---

## Decision 8: Logging Extension Strategy

**Decision**: Dashboard.md extension with structured sections

**Rationale**:
- Single source of truth for all activity
- Obsidian-compatible
- Append-only prevents overwrites

**Dashboard.md Structure**:
```markdown
# Dashboard

## Bronze Logs
[Existing Bronze logging format - UNCHANGED]

## Silver Logs

### Watcher Triggers
| Timestamp | Watcher | Items Found | Status |
|-----------|---------|-------------|--------|
| 2026-02-20T10:00:00Z | Gmail | 3 | Processed |

### Plan Creations
| Timestamp | Plan ID | Risk Level | Approval Required |
|-----------|---------|------------|-------------------|
| 2026-02-20T10:05:00Z | Plan_001 | Medium | Yes |

### Approval Decisions
| Timestamp | Action ID | Decision | Decision Time |
|-----------|-----------|----------|---------------|
| 2026-02-20T10:10:00Z | Action_001 | Yes | 5 min |

### MCP Actions
| Timestamp | Action | Result | Duration |
|-----------|--------|--------|----------|
| 2026-02-20T10:11:00Z | post_linkedin | Success (URL) | 2.3s |

### Scheduled Tasks
| Timestamp | Task | Next Run | Status |
|-----------|------|----------|--------|
| 2026-02-20T09:00:00Z | Daily Summary | 2026-02-21T09:00:00Z | Completed |
```

---

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Watcher polling interval? | 60 seconds |
| MCP transport protocol? | HTTP localhost:8765 |
| Scheduling library? | Native cron (no dependencies) |
| Approval UI? | File-based (Obsidian edit) |
| Plan storage format? | Markdown (vault-compatible) |
| Duplicate detection storage? | File-based ID tracking |

---

## Next Steps

1. ✅ Research complete - all NEEDS CLARIFICATION resolved
2. Proceed to data-model.md (entity definitions)
3. Generate contracts/ (MCP interface, watcher contract)
4. Create quickstart.md (setup guide)
5. Run update-agent-context.sh
