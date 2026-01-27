from typing import Set, Tuple, List, Dict
from src.base import NFH

def parse_nfh_from_text(text: str) -> NFH:
    lines = text.strip().split('\n')
    data = {}
    current_section = None
    delta_lines = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if ':' in line and not current_section == 'delta':
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key == 'delta':
                current_section = 'delta'
                continue # Transitions follow on next lines
            
            data[key] = value
        elif current_section == 'delta':
            delta_lines.append(line)

    # Required fields
    required = ['k', 'alpha', 'states', 'initial', 'accepting', 'alphabet']
    for req in required:
        if req not in data:
            # aliases check
            if req == 'initial' and 'initial states' in data: data['initial'] = data['initial states']
            elif req == 'accepting' and 'accepting states' in data: data['accepting'] = data['accepting states']
            elif req == 'alpha' and 'quantifiers' in data: data['alpha'] = data['quantifiers']
            else:
                raise ValueError(f"Missing required field: {req}")

    k = int(data['k'])
    alpha = data['alpha'].replace(',', ' ').split()
    states = set(data['states'].replace(',', ' ').split())
    initial = set(data['initial'].replace(',', ' ').split())
    accepting = set(data['accepting'].replace(',', ' ').split())
    alphabet = set(data['alphabet'].replace(',', ' ').split())

    delta_set = set()
    for dline in delta_lines:
        parts = dline.replace(',', ' ').split()
        if len(parts) != k + 2:
            raise ValueError(f"Invalid transition format: '{dline}'. Expected {k+2} parts.")
        
        state = parts[0]
        symbols = tuple(parts[1:-1])
        next_state = parts[-1]
        
        delta_set.add((state, symbols, next_state))

    return NFH(states, initial, accepting, k, delta_set, alpha, alphabet)
