"""
Asynchronous HyperAutomaton implementation.
"""

from typing import List, Dict, Tuple, Set
from .base import HyperAutomaton


class AsynchronousHyperAutomaton(HyperAutomaton):
    """
    Asynchronous hyperautomaton where traces can advance independently.
    
    In an asynchronous hyperautomaton, each input word can process symbols
    at its own pace. The automaton accepts if all traces can be accepted
    independently (each trace reaches an accepting state).
    """
    
    def run(self, traces: List[List[str]]) -> Tuple[bool, List[Dict]]:
        """
        Run the asynchronous hyperautomaton on multiple traces.
        
        Each trace is processed independently and can have different lengths.
        
        Args:
            traces: List of traces (words), where each trace is a list of symbols
            
        Returns:
            Tuple of (accepted, run_history) where:
            - accepted: Boolean indicating if all traces are accepted
            - run_history: List of step-by-step run information for each trace
        """
        if not traces:
            # Empty traces: accept if initial state is accepting
            return (self.is_accepting(self.initial_state), [])
        
        # Process each trace independently
        all_accepted = True
        run_history = []
        
        for trace_idx, trace in enumerate(traces):
            trace_history = self._run_single_trace(trace, trace_idx)
            run_history.append(trace_history)
            
            if not trace_history['accepted']:
                all_accepted = False
        
        return (all_accepted, run_history)
    
    def _run_single_trace(self, trace: List[str], trace_idx: int) -> Dict:
        """
        Run a single trace through the automaton.
        
        Args:
            trace: Single trace (word) as a list of symbols
            trace_idx: Index of the trace for identification
            
        Returns:
            Dictionary containing the run history and acceptance status
        """
        current_state = self.initial_state
        step_history = []
        
        for step, symbol in enumerate(trace):
            step_info = {
                'step': step,
                'symbol': symbol,
                'current_state': current_state,
                'next_states': []
            }
            
            next_states = self.get_next_states(current_state, symbol)
            
            if not next_states:
                # No transition available - reject
                step_info['next_states'] = []
                step_info['accepted'] = False
                step_history.append(step_info)
                return {
                    'trace_idx': trace_idx,
                    'trace': trace,
                    'accepted': False,
                    'steps': step_history,
                    'final_state': current_state
                }
            
            # For deterministic behavior, take first state
            # For non-deterministic, we'd need to track all possibilities
            current_state = next(iter(next_states))
            step_info['next_states'] = [current_state]
            step_info['new_state'] = current_state
            step_history.append(step_info)
        
        # Check if final state is accepting
        is_accepting = self.is_accepting(current_state)
        
        return {
            'trace_idx': trace_idx,
            'trace': trace,
            'accepted': is_accepting,
            'steps': step_history,
            'final_state': current_state
        }

