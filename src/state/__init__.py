"""
State management module for the multi-agent math problem solving system.
Provides both legacy and new state definitions for backward compatibility.
"""

from .state import (
    # Legacy state definitions
    ProblemType,
    ExecutionStatus,
    ComprehensionState,
    PlanningState,
    ExecutionState,
    VerificationState,
    MathProblemState,
    MathInputState,
    ComprehensionAnalysis,
    override_reducer,
    dict_merge_reducer,
    SolveMathProblem,
    VerifySolution,
    PlanSolutionStrategy
)

from .state_v2 import (
    # New state definitions (prompt-driven design)
    MathProblemStateV2,
    ComprehensionState as ComprehensionStateV2,
    PlanningState as PlanningStateV2,
    ExecutionState as ExecutionStateV2,
    VerificationState as VerificationStateV2,
    CoordinatorState,
    
    # Enumerations
    ProblemType as ProblemTypeV2,
    ExecutionStatus as ExecutionStatusV2,
    ToolType,
    VerificationVerdict,
    
    # Structured models
    LaTeXNormalization,
    ProblemSurfaceDeconstruction,
    CorePrinciplesTracing,
    StrategicPathBuilding,
    ExecutionTask,
    ExecutionPlan,
    ToolExecution,
    VerificationCheck,
    VerificationReport,
    
    # Reducer functions
    override_reducer as override_reducer_v2,
    dict_merge_reducer as dict_merge_reducer_v2,
    list_append_reducer,
    
    # Utility functions
    create_initial_state,
    get_current_phase,
    should_retry_phase,
    mark_phase_completed
)

# Export both versions for compatibility
__all__ = [
    # Legacy exports
    'ProblemType',
    'ExecutionStatus',
    'ComprehensionState',
    'PlanningState',
    'ExecutionState',
    'VerificationState',
    'MathProblemState',
    'MathInputState',
    'ComprehensionAnalysis',
    'override_reducer',
    'dict_merge_reducer',
    'SolveMathProblem',
    'VerifySolution',
    'PlanSolutionStrategy',
    
    # New exports
    'MathProblemStateV2',
    'ComprehensionStateV2',
    'PlanningStateV2',
    'ExecutionStateV2',
    'VerificationStateV2',
    'CoordinatorState',
    'ProblemTypeV2',
    'ExecutionStatusV2',
    'ToolType',
    'VerificationVerdict',
    'LaTeXNormalization',
    'ProblemSurfaceDeconstruction',
    'CorePrinciplesTracing',
    'StrategicPathBuilding',
    'ExecutionTask',
    'ExecutionPlan',
    'ToolExecution',
    'VerificationCheck',
    'VerificationReport',
    'override_reducer_v2',
    'dict_merge_reducer_v2',
    'list_append_reducer',
    'create_initial_state',
    'get_current_phase',
    'should_retry_phase',
    'mark_phase_completed'
]