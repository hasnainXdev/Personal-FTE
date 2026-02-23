---
Skill: Orchestrator
Type: Coordinator
Requires_Plan: No
Requires_Approval: No
Side_Effects: Executes skill chains, logs all executions
Dependencies:
  - All skills in chain
---

# Skill: Orchestrator

**Purpose**: Chain multiple skills together in defined sequence with dependency checking

**Source**: `ai_employee/services/orchestrator.py`

## Configuration

```yaml
default_chain:
  - Inbox Intake
  - Task Classifier
  - Plan Generator
  - Approval Request
  - MCP Execution
  - Task State Mover
  - Dashboard Logger
dependency_checking: strict
failure_recovery: halt_and_log
```

## Skill Declaration Format

Each skill declares its properties:

```markdown
---
Skill: Skill Name
Type: Input | Processor | Executor | Logger
Requires_Plan: Yes|No
Requires_Approval: Yes|No
Side_Effects: [list of side effects]
Dependencies: [list of skill names that must complete first]
---
```

## Execution Logic

1. **Dependency Validation**: Before each skill execution, verify all dependencies completed successfully
2. **Sequential Execution**: Execute skills in declared order
3. **Failure Recovery**: Halt chain on skill failure, log error context, do not corrupt state
4. **Circular Detection**: Detect and prevent circular dependencies

## Default Chain

```
Inbox Intake → Task Classifier → Plan Generator → Approval Request → MCP Execution → Task State Mover → Dashboard Logger
```

## Error Handling

- **Dependency Not Satisfied**: Skip skill, log error, halt chain
- **Skill Execution Failure**: Log error, halt chain, preserve state
- **Circular Dependency**: Detect before execution, raise error, log to Dashboard.md

## Logging

Logs each skill execution to Dashboard.md:
- Skill name
- Result (Success/Failed)
- Duration (ms)
- Error context (if failed)

## Example Usage

```python
from ai_employee.services import Orchestrator
from ai_employee.services.orchestrator import SkillDeclaration, create_default_chain

orchestrator = Orchestrator()

# Register skills
orchestrator.register_skill(SkillDeclaration(
    name="Inbox Intake",
    skill_type="Input",
    dependencies=[]
))

orchestrator.register_skill(SkillDeclaration(
    name="Task Classifier",
    skill_type="Processor",
    dependencies=["Inbox Intake"]
))

# Execute chain
results = orchestrator.execute_chain(
    chain=create_default_chain(),
    context={"task_id": "123"},
    skill_executors={...}
)
```

## Related Skills

- All Silver skills (coordinates execution)
- Plan Generator (may be in chain)
- Approval Request (may be in chain)
