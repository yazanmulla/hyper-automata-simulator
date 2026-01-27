from typing import Dict, Optional, Tuple, Set
from collections import deque
import time
from .base import NFH

class RunManager:
    def __init__(self, nfh: NFH, assignment, initial_state: Optional[str] = None, timeout: float = 60, enable_timeout: bool = True):
        self.nfh = nfh
        self.timeout = timeout
        self.enable_timeout = enable_timeout
        
        if initial_state is None:
            initial_state = list(nfh.initial_states)[0]
        
        assert initial_state in self.nfh.states, "Initial state must be a valid state"
        assert len(assignment) == self.nfh.k, "Assignment must have k = {} words".format(self.nfh.k)

        self.initial_state = initial_state
        
        # Store assignment as immutable strings for indexing
        if isinstance(assignment, list):
            self.assignment = tuple(assignment)
        elif isinstance(assignment, dict):
            # Sort by keys to ensure order 1..k
            sorted_keys = sorted(assignment.keys(), key=lambda x: int(x))
            self.assignment = tuple(deque(assignment[k]) if isinstance(assignment[k], str) else "".join(assignment[k]) for k in sorted_keys)
        else:
            raise ValueError("Assignment must be a list of strings")

        self.initial_assignment = list(self.assignment)
        
        # Run state
        self.run_history = [] 
        self.current_state = initial_state
        
        # Pointers for current position in each string (0-indexed)
        self.ptrs = tuple([0] * self.nfh.k)
        
        # Memoization: (state, ptrs) -> bool
        self.memo: Dict[Tuple[str, Tuple[int, ...]], bool] = {}
        
        # Path reconstruction: (state, ptrs) -> transition that led to success
        self.path_map: Dict[Tuple[str, Tuple[int, ...]], tuple] = {}

    def _get_char(self, tape_idx, ptr):
        if ptr < len(self.assignment[tape_idx]):
            return self.assignment[tape_idx][ptr]
        return '#'

    def _solve(self, state: str, ptrs: Tuple[int, ...]) -> bool:
        if self.enable_timeout and (time.time() - self.start_time > self.timeout):
            return False

        state_key = (state, ptrs)
        if state_key in self.memo:
            return self.memo[state_key]

        # Check Acceptance (Base Case)
        # Accepted if in accepting state AND all tapes consumed
        if state in self.nfh.accepting_states:
            all_consumed = True
            for i, ptr in enumerate(ptrs):
                if ptr < len(self.assignment[i]):
                    all_consumed = False
                    break
            if all_consumed:
                self.memo[state_key] = True
                return True

        # Recursion
        possible_transitions = self.nfh.transition_map.get(state, [])
        for transition in possible_transitions:
            (_, symbols, next_state) = transition
            
            valid = True
            next_ptrs_list = list(ptrs)
            
            for i, sym in enumerate(symbols):
                # i corresponds to tape i (0-indexed)
                curr_char = self._get_char(i, ptrs[i])
                
                if sym == '#':
                    pass
                else:
                    if sym == curr_char:
                        next_ptrs_list[i] += 1
                    else:
                        valid = False
                        break
            
            if valid:
                next_ptrs = tuple(next_ptrs_list)
                if self._solve(next_state, next_ptrs):
                    self.memo[state_key] = True
                    self.path_map[state_key] = transition
                    return True

        self.memo[state_key] = False
        return False

    def reconstruct_path(self):
        curr_state = self.initial_state
        curr_ptrs = tuple([0] * self.nfh.k)
        
        self.run_history = []
        
        while True:
            key = (curr_state, curr_ptrs)
            if key in self.path_map:
                trans = self.path_map[key]
                self.run_history.append(trans)
                
                # Update state and ptrs
                (_, symbols, next_state) = trans
                curr_state = next_state
                
                next_ptrs_list = list(curr_ptrs)
                for i, sym in enumerate(symbols):
                    if sym != '#':
                        next_ptrs_list[i] += 1
                curr_ptrs = tuple(next_ptrs_list)
            else:
                break
                
        self.variables = {}
        for i, w in enumerate(self.assignment):
            self.variables[str(i+1)] = deque() # All consumed

    def run(self) -> bool:
        self.start_time = time.time()
        self.memo = {}
        self.path_map = {}

        success = self._solve(self.initial_state, self.ptrs)
        if success:
            self.reconstruct_path()
            if self.run_history:
                self.current_state = self.run_history[-1][2]
        return success
