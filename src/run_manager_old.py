from typing import Dict, Optional
from collections import deque
import time
from .base import NFH

class RunManager:
    def __init__(self, nfh: NFH, assignment, initial_state: Optional[str] = None, timeout: float = 60, enable_timeout: bool = True):
        self.nfh = nfh
        self.timeout = timeout
        self.enable_timeout = enable_timeout
        
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
        self.initial_assignment = None
        if isinstance(assignment, list):
            self.initial_assignment = assignment[:]

    def valid_transitions(self):
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
            
        # Calculate remaining timeout for the branch
        remaining_timeout = self.timeout
        if self.enable_timeout:
            elapsed = time.time() - self.start_time
            remaining_timeout = self.timeout - elapsed

        newRun = RunManager(self.nfh, new_variables, self.current_state, timeout=remaining_timeout, enable_timeout=self.enable_timeout)
        newRun.move(transition)
        return newRun

    def run(self) -> bool:
        self.start_time = time.time()
        try:
            while not self.enable_timeout or (time.time() - self.start_time <= self.timeout):
                if self.acceptingState():
                    return True

                valid_transitions = self.valid_transitions()
                
                if len(valid_transitions) == 1: # Deterministic
                    self.move(valid_transitions[0])
                elif len(valid_transitions) > 1: # Nondeterministic - Branching
                    for trans in valid_transitions:
                        # Check timeout before branching to fail fast
                        if self.enable_timeout and (time.time() - self.start_time > self.timeout):
                            return False

                        branch_run = self.branch(trans)
                        if branch_run.run():
                            self.run_history.extend(branch_run.run_history)
                            return True # Successful run found
                    return False # No successful run found
                else: # No possible transition
                    return False
            return False # Timeout
        except RecursionError:
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
