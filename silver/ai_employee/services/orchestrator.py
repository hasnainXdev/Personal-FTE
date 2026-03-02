"""
Orchestrator Service - Skill chaining and workflow orchestration

Chains multiple skills together in defined sequence with
dependency checking and failure recovery.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class SkillDeclaration:
    """Declares a skill's properties and dependencies"""
    name: str
    skill_type: str  # Input | Processor | Executor | Logger
    requires_plan: bool = False
    requires_approval: bool = False
    side_effects: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)  # Skill names that must complete first


@dataclass
class SkillResult:
    """Result of skill execution"""
    skill_name: str
    success: bool
    result: Any = None
    error: str | None = None
    duration_ms: int = 0


class Orchestrator:
    """
    Orchestrate skill execution chains with dependency checking.
    
    Executes skills in sequential order, validating dependencies
    before each skill execution.
    """
    
    def __init__(
        self,
        dashboard_path: Path | None = None,
    ):
        """
        Initialize orchestrator.
        
        Args:
            dashboard_path: Path to Dashboard.md for logging
        """
        project_root = Path(__file__).parent.parent.parent
        self.dashboard_path = dashboard_path or (project_root / "AI_Employee_Vault" / "Dashboard.md")
        
        # Registered skills
        self.skills: dict[str, SkillDeclaration] = {}
        
        # Execution state
        self.executed_skills: set[str] = set()
        self.execution_results: dict[str, SkillResult] = {}
        
        logger.info("Orchestrator initialized")
    
    def register_skill(self, declaration: SkillDeclaration):
        """Register a skill declaration"""
        self.skills[declaration.name] = declaration
        logger.info(f"Registered skill: {declaration.name}")
    
    def dependencies_satisfied(self, skill_name: str) -> bool:
        """
        Check if all dependencies for a skill are satisfied.
        
        Args:
            skill_name: Name of skill to check
        
        Returns:
            True if all dependencies executed successfully
        """
        if skill_name not in self.skills:
            logger.error(f"Unknown skill: {skill_name}")
            return False
        
        skill = self.skills[skill_name]
        
        for dep_name in skill.dependencies:
            if dep_name not in self.executed_skills:
                logger.debug(f"Dependency not executed: {dep_name}")
                return False
            
            # Check if dependency succeeded
            if dep_name in self.execution_results:
                result = self.execution_results[dep_name]
                if not result.success:
                    logger.debug(f"Dependency failed: {dep_name}")
                    return False
        
        return True
    
    def detect_circular_dependencies(self) -> bool:
        """
        Detect circular dependencies in skill graph.
        
        Returns:
            True if circular dependency detected
        """
        visited = set()
        rec_stack = set()
        
        def has_cycle(skill_name: str) -> bool:
            visited.add(skill_name)
            rec_stack.add(skill_name)
            
            if skill_name in self.skills:
                for dep in self.skills[skill_name].dependencies:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True
            
            rec_stack.remove(skill_name)
            return False
        
        for skill_name in self.skills:
            if skill_name not in visited:
                if has_cycle(skill_name):
                    return True
        
        return False
    
    def execute_skill(
        self,
        skill_name: str,
        execute_func: Callable,
        context: dict,
    ) -> SkillResult:
        """
        Execute a single skill.
        
        Args:
            skill_name: Name of skill to execute
            execute_func: Function to execute (receives context)
            context: Execution context
        
        Returns:
            SkillResult
        """
        import time
        start_time = time.time()
        
        logger.info(f"Executing skill: {skill_name}")
        
        try:
            # Check dependencies
            if not self.dependencies_satisfied(skill_name):
                return SkillResult(
                    skill_name=skill_name,
                    success=False,
                    error=f"Dependencies not satisfied for {skill_name}"
                )
            
            # Execute skill
            result = execute_func(context)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            skill_result = SkillResult(
                skill_name=skill_name,
                success=True,
                result=result,
                duration_ms=duration_ms
            )
            
            # Update state
            self.executed_skills.add(skill_name)
            self.execution_results[skill_name] = skill_result
            
            # Log to dashboard
            self._log_skill_execution(skill_name, "Success", duration_ms)
            
            logger.info(f"Skill {skill_name} completed in {duration_ms}ms")
            
            return skill_result
        
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            logger.error(f"Skill {skill_name} failed: {e}", exc_info=True)
            
            skill_result = SkillResult(
                skill_name=skill_name,
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )
            
            self.execution_results[skill_name] = skill_result
            self._log_skill_execution(skill_name, f"Failed: {e}", duration_ms)
            
            return skill_result
    
    def execute_chain(
        self,
        chain: list[str],
        context: dict,
        skill_executors: dict[str, Callable],
    ) -> dict[str, SkillResult]:
        """
        Execute a chain of skills in order.
        
        Args:
            chain: List of skill names in execution order
            context: Execution context (shared across skills)
            skill_executors: Map of skill_name -> execute_func
        
        Returns:
            Map of skill_name -> SkillResult
        """
        logger.info(f"Executing chain: {chain}")
        
        # Check for circular dependencies first
        if self.detect_circular_dependencies():
            logger.error("Circular dependency detected in skill chain")
            self._log_skill_execution("ORCHESTRATOR", "Failed: Circular dependency", 0)
            return {}
        
        results = {}
        
        for skill_name in chain:
            if skill_name not in skill_executors:
                logger.error(f"Skill executor not found: {skill_name}")
                results[skill_name] = SkillResult(
                    skill_name=skill_name,
                    success=False,
                    error=f"Executor not found: {skill_name}"
                )
                continue
            
            # Execute skill
            result = self.execute_skill(
                skill_name=skill_name,
                execute_func=skill_executors[skill_name],
                context=context
            )
            
            results[skill_name] = result
            
            # Halt on failure
            if not result.success:
                logger.warning(f"Chain halted at skill: {skill_name}")
                break
        
        return results
    
    def _log_skill_execution(self, skill_name: str, result: str, duration_ms: int):
        """Log skill execution to Dashboard.md"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # For now, just log - could add to Dashboard.md table
        logger.debug(f"Dashboard log: {skill_name} - {result} ({duration_ms}ms)")
    
    def reset(self):
        """Reset execution state for new chain"""
        self.executed_skills.clear()
        self.execution_results.clear()
        logger.info("Orchestrator state reset")


def create_default_chain() -> list[str]:
    """
    Create default skill execution chain.
    
    Returns:
        List of skill names in order
    """
    return [
        "Inbox Intake",
        "Task Classifier",
        "Plan Generator",      # If multi-step
        "Approval Request",    # If external action
        "MCP Execution",       # If approved
        "Task State Mover",
        "Dashboard Logger"
    ]


if __name__ == "__main__":
    # Test orchestrator
    orchestrator = Orchestrator()
    
    # Register test skills
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
    
    orchestrator.register_skill(SkillDeclaration(
        name="Plan Generator",
        skill_type="Processor",
        requires_plan=False,
        dependencies=["Task Classifier"]
    ))
    
    # Test chain execution
    def mock_executor(ctx):
        return {"status": "ok"}
    
    skill_executors = {
        "Inbox Intake": mock_executor,
        "Task Classifier": mock_executor,
        "Plan Generator": mock_executor,
    }
    
    results = orchestrator.execute_chain(
        chain=["Inbox Intake", "Task Classifier", "Plan Generator"],
        context={"test": True},
        skill_executors=skill_executors
    )
    
    print("Chain execution results:")
    for name, result in results.items():
        print(f"  {name}: {'Success' if result.success else 'Failed'}")
