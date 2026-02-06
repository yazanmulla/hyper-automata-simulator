from typing import List, Dict, Optional
from src.base import NFH, Hyperword
from src.run_manager import RunManager


def checkMembership(A: NFH, S: Hyperword) -> Tuple[bool, List[RunManager]]:
    # Singleton Hyperword: assignment = (w, ..., w)
    if len(S) == 1: 
        w = next(iter(S))
        assignment = [w] * A.k
        manager = RunManager(A, assignment)
        if manager.run():
            return True, [manager]
        return False, []
    
    quantifiers = list(zip(A.alpha, range(1, A.k + 1)))
    return check_models(A, S, quantifiers, {})


def check_models(A: NFH, S: Hyperword, quantifiers: List[tuple], assignment: Dict[int, str]) -> Tuple[bool, List[RunManager]]:
    if not quantifiers:
        final_assignment = [assignment[i] for i in range(1, A.k + 1)]
        manager = RunManager(A, final_assignment)
        if manager.run():
            return True, [manager]
        return False, []

    (q_type, var_idx) = quantifiers[0]
    remaining_quantifiers = quantifiers[1:]
    
    if q_type == 'E': # Exists
        if len(S) == 0:
            return False, []
            
        for word in S:
            new_assignment = assignment.copy()
            new_assignment[var_idx] = word
            # Debug/Progress Info for searches
            success, managers = check_models(A, S, remaining_quantifiers, new_assignment)
            if success:
                return True, managers
        return False, []
        
    elif q_type == 'A': # For All
        if len(S) == 0:
            return True, []
            
        all_managers = []
        for word in S:
            new_assignment = assignment.copy()
            new_assignment[var_idx] = word
            success, managers = check_models(A, S, remaining_quantifiers, new_assignment)
            if not success:
                return False, []
            all_managers.extend(managers)
        return True, all_managers
