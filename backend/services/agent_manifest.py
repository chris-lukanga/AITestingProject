AGENTS = [
    {'name': 'Clarification Agent', 'label': 'Scope', 'stage': 'clarification', 'purpose': 'Confirm the application contract and permission to test.'},
    {'name': 'Research Agent', 'label': 'Researcher', 'stage': 'research', 'purpose': 'Find sources, deduplicate evidence and review research quality.'},
    {'name': 'Planning Agent', 'label': 'Planner', 'stage': 'planning', 'purpose': 'Choose testing objectives from the target, research and history.'},
    {'name': 'Test Generation Agent', 'label': 'Generator', 'stage': 'generation', 'purpose': 'Create distinct executable cases with explicit expected behaviour.'},
    {'name': 'Execution Agent', 'label': 'Executor', 'stage': 'execution', 'purpose': 'Send real requests and capture responses, tools and timings.'},
    {'name': 'Evaluation Agent', 'label': 'Evaluator', 'stage': 'evaluation', 'purpose': 'Apply assertions and evidence-based judgments to each case.'},
    {'name': 'Reporting Agent', 'label': 'Reporter', 'stage': 'reporting', 'purpose': 'Aggregate outcomes and preserve downloadable evidence.'},
    {'name': 'Recommendation Agent', 'label': 'Advisor', 'stage': 'recommendation', 'purpose': 'Recommend the next run using failures and coverage gaps.'},
    {'name': 'Review Agent', 'label': 'Quality review', 'stage': 'review', 'purpose': 'Check agent outputs against explicit gates before the next move.'},
]
