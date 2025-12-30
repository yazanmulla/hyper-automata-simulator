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

class RunManager:
    '''
    Current thoughts on RunManager:
    1)
    This class is designed to simulate a specific run of an NFH on a given assignment for the NFH's variables.
    Since NFH is non-deterministic, this class is supposed to recursively define its branches and simulate them
    to check for at least one passing run. If such run exists, append its history to the main run and return it.
    If no such run exists, return False.
    The problem with this is that for asynchronous NFHs, there could be paths of infinite length, meaning
    branches which do not stop eventually. This would cause infinite recursion and stack overflow.
    To prevent this, we need to implement a timeout or a maximum depth for the recursion. (Also thinking of clever ways to prevent loops, WIP)
    Currently ignoring this problem. (assuming infinite resources or no infinite loops in the given NFH)


    1.1) Possible ways to fix problem in (1):
        Limit of branch run to a maximum depth. (which is defined by NFH values such as maximum variable length)
        Timeout per branch run.
        Limiting the number of times transitions of type (q1, (#, #, ..., #), q2) allowed.
        Controlled execution (runs indefinitely, maybe prompt the user to continue or stop)


    2)
    For now, the run_history saved in this manager will be the history of the successful run, if such run exists.
    Otherwise, it will have the history of the run up to the first branching point.
    (WIP: think of a way to save history of all failed runs, if needed TODO: check with Sarai and Hadar)
    '''

    def __init__(self, nfh: NFH, assignment, initial_state: Optional[str] = None):
        self.nfh = nfh
        
        if initial_state is None:
            initial_state = list(nfh.initial_states)[0] # Just pick one for default behavior
        
        assert initial_state in self.nfh.states, "Initial state must be a valid state"
        assert len(assignment) == self.nfh.k, "Assignment must have k = {} words".format(self.nfh.k)

        self.current_state = initial_state
        
        # Deep copy the assignment queues so this run has its own independent buffers
        # Internal storage: keys are indices as strings '1'...'k'
        self.variables: Dict[str, deque] = {}
        if isinstance(assignment, list):
            for i, w in enumerate(assignment):
                self.variables[str(i+1)] = deque(w)
        elif isinstance(assignment, dict): # internal usage
            self.variables = assignment
        else:
            raise ValueError("Assignment must be a list of strings")

        self.run_history = [] # List of transitions

    def valid_transitions(self):
        '''
        Note: This function works for both sync and async models.
        If we want explicit sync transitions, Then we should override this function to accept '#' as a symbol
        only if the corresponding buffer is empty
        '''
        valid_transitions = []

        possible_transitions = self.nfh.transition_map[self.current_state]
        for transition in possible_transitions:
            valid = True
            (_, symbols, _) = transition
            for i, symbol in enumerate(symbols):
                buffer = self.variables[str(i+1)]
                current_char = buffer[0] if buffer else '#'
                if symbol != '#' and symbol != current_char:
                    valid = False
                    break
            if valid:
                valid_transitions.append(transition)
        return valid_transitions

    def move(self, transition):
        assert transition in self.nfh.delta, "INTERNAL: Transition must be a valid transition"
        (q0, symbols, q1) = transition
        assert q0 == self.current_state, "INTERNAL: Transition must start from the current state"
        
        self.current_state = q1
        self.run_history.append(transition)
        for sym, buffer in zip(symbols, self.variables.values()):
            if sym != '#':
                buffer.popleft()

    def branch(self, transition):
        assert transition in self.nfh.delta, "INTERNAL: Transition must be a valid transition"

        # Copy variables for the child
        new_variables = {}
        for k, v in self.variables.items():
            new_variables[k] = deque(v)
            
        newRun = RunManager(self.nfh, new_variables, self.current_state)
        newRun.move(transition)
        return newRun

    def run(self) -> bool:
        while True:
            if self.acceptingState():
                return True

            valid_transitions = self.valid_transitions()
            
            if len(valid_transitions) == 1: # Deterministic
                self.move(valid_transitions[0])
            elif len(valid_transitions) > 1: # Nondeterministic - Branching
                for trans in valid_transitions:
                    branch_run = self.branch(trans)
                    if branch_run.run():
                        self.run_history.extend(branch_run.run_history)
                        return True # Successful run found
                return False # No successful run found
            else: # No possible transition
                return False

    def print_run_history(self):
        print(f"Run History (Start: {self.run_history[0][0] if self.run_history else self.current_state}):")
        for i, step in enumerate(self.run_history):
            print(f"Step {i+1}: State {step[0]} --({step[1]})--> State {step[2]}")
        
        last_state = self.run_history[-1][2] if self.run_history else self.current_state
        print(f"Final State: {last_state}")
        print(f"Result: {'ACCEPTED' if last_state in self.nfh.accepting_states else 'REJECTED'}")


    def acceptingState(self):
        return self.current_state in self.nfh.accepting_states and all(len(d) == 0 for d in self.variables.values())
