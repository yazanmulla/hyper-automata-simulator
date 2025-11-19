"""
Base class for HyperAutomaton.
"""

from abc import ABC, abstractmethod
from typing import Set, Dict, List, Tuple, Optional


class HyperAutomaton(ABC):
    """
    Base class for hyperautomata.
    
    A hyperautomaton is a finite automaton that processes multiple input words simultaneously.
    """
    
    def __init__(self, states: Set[str], alphabet: Set[str], 
                 initial_state: str, accepting_states: Set[str],
                 transitions: Dict[Tuple[str, str], Set[str]]):
        """
        Initialize a hyperautomaton.
        
        Args:
            states: Set of all states
            alphabet: Set of input symbols
            initial_state: Initial state
            accepting_states: Set of accepting states
            transitions: Dictionary mapping (state, symbol) -> set of next states
        """
        self.states = states
        self.alphabet = alphabet
        self.initial_state = initial_state
        self.accepting_states = accepting_states
        self.transitions = transitions
        
        # Validate inputs
        if initial_state not in states:
            raise ValueError(f"Initial state {initial_state} not in states")
        if not accepting_states.issubset(states):
            raise ValueError("Some accepting states are not in states")
        for (state, symbol), next_states in transitions.items():
            if state not in states:
                raise ValueError(f"State {state} in transition not in states")
            # For synchronous: symbol is a tuple of symbols
            # For asynchronous: symbol is a single symbol
            if isinstance(symbol, tuple):
                # Validate each symbol in the vector
                for sym in symbol:
                    if sym not in alphabet:
                        raise ValueError(f"Symbol {sym} in symbol vector not in alphabet")
            else:
                if symbol not in alphabet:
                    raise ValueError(f"Symbol {symbol} in transition not in alphabet")
            if not next_states.issubset(states):
                raise ValueError(f"Next states {next_states} not subset of states")
    
    @abstractmethod
    def run(self, traces: List[List[str]]) -> Tuple[bool, List[Dict]]:
        """
        Run the hyperautomaton on multiple traces.
        
        Args:
            traces: List of traces (words), where each trace is a list of symbols
            
        Returns:
            Tuple of (accepted, run_history) where:
            - accepted: Boolean indicating if all traces are accepted
            - run_history: List of dictionaries containing the run history
        """
        pass
    
    def get_next_states(self, state: str, symbol: str) -> Set[str]:
        """
        Get the set of next states from a given state and symbol.
        
        Args:
            state: Current state
            symbol: Input symbol
            
        Returns:
            Set of next states
        """
        return self.transitions.get((state, symbol), set())
    
    def is_accepting(self, state: str) -> bool:
        """
        Check if a state is accepting.
        
        Args:
            state: State to check
            
        Returns:
            True if state is accepting, False otherwise
        """
        return state in self.accepting_states
