"""
Simulator for running traces on hyperautomata.
"""

from typing import List, Tuple, Dict
from hyperautomata import HyperAutomaton


def simulate_runs(automaton: HyperAutomaton, traces: List[List[str]]) -> Dict:
    """
    Simulate hyperautomaton runs on multiple traces.
    
    Args:
        automaton: The hyperautomaton to run
        traces: List of traces (words), where each trace is a list of symbols
        
    Returns:
        Dictionary containing:
        - accepted: Boolean indicating if all traces are accepted
        - run_history: Detailed run history
        - summary: Summary of the run
    """
    accepted, run_history = automaton.run(traces)
    
    summary = {
        'total_traces': len(traces),
        'accepted': accepted,
        'trace_lengths': [len(trace) for trace in traces] if traces else []
    }
    
    return {
        'accepted': accepted,
        'run_history': run_history,
        'summary': summary
    }

