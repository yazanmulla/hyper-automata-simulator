# Hyper-Automata Simulator

A comprehensive simulator for hyperautomata that supports both synchronous and asynchronous execution modes. This tool allows you to define hyperautomata, run traces (words) on them, and visualize the execution.

## Features

- **Synchronous Hyperautomata**: All traces advance simultaneously, requiring equal-length inputs
- **Asynchronous Hyperautomata**: Traces can advance independently at their own pace
- **Interactive Input Parser**: Easy-to-use command-line interface for defining automata
- **Visualization**: Beautiful graph visualizations using NetworkX and Matplotlib
- **Detailed Run History**: Step-by-step execution tracking

## Installation

1. Clone this repository
2. Create a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
hyper-automata-simulator/
├── hyperautomata/          # Core automaton classes
│   ├── __init__.py
│   ├── base.py            # Base HyperAutomaton class
│   ├── synchronous.py     # SynchronousHyperAutomaton
│   └── asynchronous.py    # AsynchronousHyperAutomaton
├── visualizer/            # Visualization module
│   ├── __init__.py
│   └── visualizer.py     # Visualization functions
├── simulator.py           # Simulation runner
├── main.py                # Main entry point with parser
└── requirements.txt       # Python dependencies
```

## Usage

### Running the Simulator

```bash
python main.py
```

The program will prompt you for:

1. **Automaton Type**: Choose `synchronous` or `asynchronous`
2. **States**: Number of states and their names
3. **Alphabet**: Number of symbols and the symbols themselves
4. **Initial State**: The starting state
5. **Accepting States**: States that indicate acceptance
6. **Transitions**: State transitions in format `state symbol next_state1 next_state2 ...`
7. **Traces**: The input words to simulate

### Example Input

For synchronous hyperautomaton (3 traces):
```
sync
2
q0 q1
2
a b
q0
1
q1
q0 a b a q1
q1 a a a q0

3
a a
b a
a a
```

This creates a synchronous hyperautomaton with:
- States: q0, q1
- Alphabet: {a, b}
- Initial state: q0 (all traces start here)
- Accepting state: q1
- Transitions: 
  - q0 --(a,b,a)--> q1 (if all 3 traces are in q0 and read a,b,a respectively, they all go to q1)
  - q1 --(a,a,a)--> q0 (if all 3 traces are in q1 and read a,a,a respectively, they all go to q0)
- Three traces: "a a", "b a", "a a"

### Programmatic Usage

You can also use the classes programmatically:

**Synchronous Hyperautomaton:**
```python
from hyperautomata import SynchronousHyperAutomaton
from simulator import simulate_runs

# Create synchronous automaton (for 3 traces)
# Transitions use vector symbols: (symbol1, symbol2, symbol3)
automaton = SynchronousHyperAutomaton(
    states={'q0', 'q1'},
    alphabet={'a', 'b'},
    initial_state='q0',
    accepting_states={'q1'},
    transitions={
        ('q0', ('a', 'b', 'a')): {'q1'},  # Vector symbol: (a, b, a)
        ('q1', ('a', 'a', 'a')): {'q0'},  # Vector symbol: (a, a, a)
    }
)

# Run traces (must have same length)
traces = [['a', 'a'], ['b', 'a'], ['a', 'a']]
result = simulate_runs(automaton, traces)

print(f"Accepted: {result['accepted']}")
```

**Asynchronous Hyperautomaton:**
```python
from hyperautomata import AsynchronousHyperAutomaton
from simulator import simulate_runs

# Create asynchronous automaton
# Transitions use single symbols
automaton = AsynchronousHyperAutomaton(
    states={'q0', 'q1', 'q2'},
    alphabet={'a', 'b'},
    initial_state='q0',
    accepting_states={'q2'},
    transitions={
        ('q0', 'a'): {'q1'},
        ('q1', 'b'): {'q2'},
        ('q2', 'a'): {'q0'},
        ('q2', 'b'): {'q2'}
    }
)

# Run traces (can have different lengths)
traces = [['a', 'b', 'a'], ['a', 'b']]
result = simulate_runs(automaton, traces)

print(f"Accepted: {result['accepted']}")
```

### Visualization

The simulator includes built-in visualization capabilities:

```python
from visualizer import visualize_run, visualize_automaton

# Visualize automaton structure
visualize_automaton(automaton, title="My Hyperautomaton")

# Visualize a run
result = simulate_runs(automaton, traces)
visualize_run(automaton, traces, result)
```

## Key Differences

### Synchronous Hyperautomata
- All traces must have the same length
- **All traces are always in the SAME state** (not vector states)
- Transitions use vector symbols: δ(q, (a₁, a₂, ..., aₖ)) → q'
  - If all k traces are in state q, and trace 1 reads a₁, trace 2 reads a₂, ..., trace k reads aₖ,
    then ALL traces transition together to state q'
- Acceptance: the final state (shared by all traces) must be accepting

### Asynchronous Hyperautomata
- Traces can have different lengths
- Each trace advances independently
- Acceptance requires each trace individually to reach an accepting state

## Dependencies

- `networkx>=3.0`: For graph structure and layout
- `matplotlib>=3.7.0`: For visualization

## License

This project is open source and available for educational and research purposes.
