from typing import Set, Dict, List, Tuple, Optional
from collections import deque

class NFH:
    def __init__(self, states: Set[str], 
                 initial_states: Set[str], accepting_states: Set[str],
                 k: int, delta: Set[Tuple[str, Tuple[str, ...], str]],
                 alpha: List[str], alphabet: Set[str] = {'0', '1'}):
        self.states = states
        self.alphabet = alphabet
        self.initial_states = initial_states
        self.accepting_states = accepting_states
        self.delta = delta
        self.k = k
        self.alpha = alpha if alpha else []
        
        # validate inputs (for both sync and async)
        assert len(states) > 0, "Must have at least one state"
        assert initial_states.issubset(states), "Initial states must be valid states"
        assert len(initial_states) > 0, "Must have at least one initial state"
        assert accepting_states.issubset(states), "Accepting states must be valid states"
        assert len(accepting_states) > 0, "Must have at least one accepting state"
        assert all(t[0] in states and t[2] in states for t in delta), "All states in transitions must be valid states"
        assert all(all(symbol in alphabet or symbol == '#' for symbol in t[1]) for t in delta), "All symbols in transitions must be from the alphabet or be '#'"
        assert all(len(t[1]) == k for t in delta), "All symbol vectors in transitions must have length k"
        assert all(q in {'E', 'A'} for q in alpha), "All quantifiers must be 'E' or 'A'"
        assert len(alpha) == k, "alpha must have k quantifiers"

        self.transition_map = {state: [] for state in states}
        for t in delta:
            self.transition_map[t[0]].append(t)

        '''
        Example for an NFH structure:
            states = {'q0', 'q1', 'q2'}
            alphabet = {'a', 'b'}
            initial_states = {'q0'}
            accepting_states = {'q1'}
            delta = {
                ('q0', ('a', 'b')): {'q1'},
                ('q0', ('b', 'a')): {'q2'},
                ('q1', ('a', 'b')): {'q1'},
                ('q2', ('b', 'a')): {'q2'},
            }
            k = 2
            alpha = ['A', 'E']
        '''

class Hyperword: # Finite set of words
    def __init__(self, words: Set[str]):
        self.words = words

    def __len__(self):
        return len(self.words)
    
    def __iter__(self):
        return iter(self.words)
    
    def __contains__(self, item):
        return item in self.words
    
    def __str__(self):
        return "{ " + ", ".join(self.words) + " }"


