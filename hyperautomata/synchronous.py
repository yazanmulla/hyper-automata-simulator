"""
Synchronous HyperAutomaton implementation.

A synchronous hyperautomaton processes all traces simultaneously.
All traces are always in the same state.
Transitions are defined with vector symbols: δ(q, (a1, a2, ..., ak)) → q'
where (a1, a2, ..., ak) is a vector of symbols, one from each trace.
"""

from typing import List, Dict, Tuple, Set
from .base import HyperAutomaton


class SynchronousHyperAutomaton(HyperAutomaton):
    """
    Synchronous hyperautomaton where all traces advance simultaneously.
    
    In a synchronous hyperautomaton:
    - All traces are always in the SAME state
    - Transitions: δ(q, (a1, a2, ..., ak)) → q'
      where (a1, a2, ..., ak) is a vector of symbols (one from each trace)
    - All traces process symbols at the same position simultaneously
    - All traces transition together to the same next state
    """
    
    def __init__(self, states: Set[str], alphabet: Set[str], 
                 initial_state: str, accepting_states: Set[str],
                 transitions: Dict[Tuple[str, str], Set[str]]):
        """
        Initialize a synchronous hyperautomaton.
        
        Args:
            states: Set of states
            alphabet: Set of input symbols
            initial_state: Initial state (all traces start here)
            accepting_states: Set of accepting states
            transitions: Dictionary mapping (state, symbol_vector) -> set of next states
                         where symbol_vector is a tuple of symbols like (a, b, a)
                         representing the symbols read from each trace simultaneously
        """
        super().__init__(states, alphabet, initial_state, accepting_states, transitions)
        # For synchronous, transitions use vector symbols
        # Format: transitions[(state, (symbol1, symbol2, ..., symbolk))] = {next_state}
    
    def _get_next_state(self, current_state: str, symbol_vector: Tuple[str, ...]) -> Set[str]:
        """
        Get next states from current state and vector of symbols.
        
        Args:
            current_state: Current state (all traces are in this state)
            symbol_vector: Vector of symbols (a1, a2, ..., ak), one from each trace
            
        Returns:
            Set of possible next states
        """
        return self.transitions.get((current_state, symbol_vector), set())
    
    def run(self, traces: List[List[str]]) -> Tuple[bool, List[Dict]]:
        """
        Run the synchronous hyperautomaton on multiple traces.
        
        All traces must have the same length and advance together.
        All traces are always in the same state.
        
        Args:
            traces: List of traces (words), where each trace is a list of symbols
            
        Returns:
            Tuple of (accepted, run_history) where:
            - accepted: Boolean indicating if the run is accepted
            - run_history: List of step-by-step run information
        """
        if not traces:
            # Empty traces: accept if initial state is accepting
            return (self.is_accepting(self.initial_state), [])
        
        num_traces = len(traces)
        
        # Check all traces have the same length
        trace_lengths = [len(trace) for trace in traces]
        if len(set(trace_lengths)) > 1:
            raise ValueError("All traces must have the same length for synchronous hyperautomaton")
        
        max_length = trace_lengths[0]
        
        # Initialize: all traces start in the same initial state
        current_state = self.initial_state
        run_history = []
        
        # Process each position simultaneously
        for step in range(max_length):
            # Get symbol vector: one symbol from each trace at current position
            symbol_vector = tuple(trace[step] for trace in traces)
            
            step_info = {
                'step': step,
                'current_state': current_state,
                'symbol_vector': symbol_vector,
                'next_states': []
            }
            
            # Get next states
            next_states = self._get_next_state(current_state, symbol_vector)
            
            if not next_states:
                # No transition available - reject
                step_info['next_states'] = []
                run_history.append(step_info)
                return (False, run_history)
            
            # For deterministic behavior, take first state
            # For non-deterministic, we'd need to track all possibilities
            current_state = next(iter(next_states))
            step_info['next_states'] = list(next_states)
            step_info['chosen_state'] = current_state
            run_history.append(step_info)
        
        # Check if final state is accepting
        is_accepting = self.is_accepting(current_state)
        
        final_info = {
            'step': max_length,
            'final_state': current_state,
            'accepted': is_accepting
        }
        run_history.append(final_info)
        
        return (is_accepting, run_history)
