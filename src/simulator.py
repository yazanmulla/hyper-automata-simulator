from typing import List, Dict, Optional
from src.base import NFH, Hyperword
from src.run_manager import RunManager


def checkMembership(A: NFH, S: Hyperword) -> bool:
    quantifiers = list(zip(A.alpha, range(1, A.k + 1)))
    return check_models(A, S, quantifiers, {})


def check_models(A: NFH, S: Hyperword, quantifiers: List[tuple], assignment: Dict[int, str]) -> bool:
    if not quantifiers:
        final_assignment = [assignment[i] for i in range(1, A.k + 1)]
        manager = RunManager(A, final_assignment)
        return manager.run()

    (q_type, var_idx) = quantifiers[0]
    remaining_quantifiers = quantifiers[1:]
    
    if q_type == 'E': # Exists
        if len(S) == 0:
            return False
            
        for word in S:
            new_assignment = assignment.copy()
            new_assignment[var_idx] = word
            if check_models(A, S, remaining_quantifiers, new_assignment):
                return True
        return False
        
    elif q_type == 'A': # For All
        if len(S) == 0:
            return True
            
        for word in S:
            new_assignment = assignment.copy()
            new_assignment[var_idx] = word
            if not check_models(A, S, remaining_quantifiers, new_assignment):
                return False
        return True
