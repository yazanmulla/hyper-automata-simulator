# Hyper-Automata Simulator

A simulator for Nondeterministic Finite-Word Hyperautomata (NFH) as defined in the paper. This tool allows you to define NFHs, check if a set of words (a Hyperword) is accepted by the automaton, and visualize the logical constraints.

## Features

- **NFH Model**: Implementation of the formal NFH definition, supporting $k$-tuple transitions.
- **Run Manager**: Handles nondeterministic execution branching and history tracking.
- **Membership Checking**: Verifies if a Hyperword satisfies the NFH's quantifier prefix (e.g., $\exists x \forall y \dots$).
- **Support for Synchronous NFHs**: handles padding (`#`) for input streams of different lengths.
- **Support for Asynchronous NFHs**: handles padding (`#`) for asynchronous transitions between states.

## Project Structure

```
hyper-automata-simulator/
├── hyperautomata/          # Core package
│   ├── base.py             # NFH, Hyperword, and RunManager classes
│   └── __init__.py
├── visualizer/             # (WIP) Visualization module
│   ├── __init__.py
│   └── visualizer.py
├── simulator.py            # Membership checking logic (checkMembership relation between NFH and Hyperword)
├── main.py                 # (WIP) Main entry point with parser
├── tests/                  # Unit tests
│   ├── test_run_manager.py
│   ├── test_simulator.py
│   └── test_complex.py
├── run_tests.sh            # Script to run all tests
└── requirements.txt        # Python dependencies
└── Research/               # (External) Research papers and LaTeX sources
```

*Note: The `Research` folder contains external reference materials and is irrelevant to the simulator project itself.*


## Installation

1. Clone this repository.
3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

## Usage

### Programmatic Usage

The core usage involves defining an `NFH` and checking if a `Hyperword` is a member of its language.

```python
from hyperautomata.base import NFH, Hyperword
from simulator import checkMembership

# 1. Define NFH components
states = {'q0', 'q1'}
initial_states = {'q0'}
accepting_states = {'q1'}
alphabet = {'a', 'b'}
k = 2  # Number of variables/tracks

# Transition: q0 --(a,b)--> q1
delta = {
    ('q0', ('a', 'b'), 'q1')
}

quantifiers = ['E', 'E'] # Exists x, Exists y

# 2. Create NFH instance
nfh = NFH(states, initial_states, accepting_states, k, delta, quantifiers, alphabet)

# 3. Define a Hyperword (set of strings)
S = Hyperword({'a', 'b'})

# 4. Check membership
result = checkMembership(nfh, S)
print(f"Accepted: {result}")
```

## Testing

The project uses `pytest` for testing. You can run the comprehensive test suite using the provided script:

```bash
./run_tests.sh
```

Or manually:
```bash
 pytest tests
```

### Running Specific Tests

To run a specific test file:
```bash
pytest tests/test_run_manager.py
```

To run a specific test class:
```bash
pytest tests/test_run_manager.py::TestRunManager
```

To run a specific test case:
```bash
pytest tests/test_run_manager.py::TestRunManager::test_run_manager_steps
```

To run with verbose output (showing each passing test):
```bash
pytest -v tests
```

Tests cover:
- Basic deterministic and nondeterministic runs.
- Synchronous and asynchronous (padded) transitions.
- Complex quantifier alternations ($\forall \exists$ etc.).
- Deep recursion and edge cases.
