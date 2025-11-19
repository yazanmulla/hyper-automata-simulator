"""
Main entry point for hyperautomata simulator.
Parses input and creates hyperautomata instances.
"""

import sys
from typing import Set, Dict, Tuple
from hyperautomata import HyperAutomaton, SynchronousHyperAutomaton, AsynchronousHyperAutomaton


def parse_automaton_input() -> Dict:
    """
    Parse hyperautomaton definition from input.
    
    Expected format:
    - First line: "sync" or "async" (or "synchronous"/"asynchronous")
    - Second line: number of states
    - Third line: space-separated state names
    - Fourth line: number of symbols in alphabet
    - Fifth line: space-separated alphabet symbols
    - Sixth line: initial state
    - Seventh line: number of accepting states
    - Eighth line: space-separated accepting states
    - Following lines: transitions in format "state symbol next_state1 next_state2 ..."
    - Empty line or EOF to end transitions
    
    Returns:
        Dictionary containing parsed automaton definition
    """
    print("Enter hyperautomaton definition:")
    print("Type 'sync' or 'async':")
    mode_input = input().strip().lower()
    
    # Normalize input: accept both short and long forms
    if mode_input in ['sync', 'synchronous']:
        mode = 'synchronous'
    elif mode_input in ['async', 'asynchronous']:
        mode = 'asynchronous'
    else:
        raise ValueError(f"Invalid mode: {mode_input}. Must be 'sync' or 'async'")
    
    print("Enter number of states:")
    num_states = int(input().strip())
    
    print("Enter state names (space-separated):")
    states = set(input().strip().split())
    
    if len(states) != num_states:
        raise ValueError(f"Number of states doesn't match: expected {num_states}, got {len(states)}")
    
    print("Enter number of alphabet symbols:")
    num_symbols = int(input().strip())
    
    print("Enter alphabet symbols (space-separated):")
    alphabet = set(input().strip().split())
    
    if len(alphabet) != num_symbols:
        raise ValueError(f"Number of symbols doesn't match: expected {num_symbols}, got {len(alphabet)}")
    
    print("Enter initial state:")
    initial_state = input().strip()
    
    print("Enter number of accepting states:")
    num_accepting = int(input().strip())
    
    print("Enter accepting states (space-separated):")
    accepting_states = set(input().strip().split())
    
    if len(accepting_states) != num_accepting:
        raise ValueError(f"Number of accepting states doesn't match: expected {num_accepting}, got {len(accepting_states)}")
    
    if mode == 'synchronous':
        print("Enter transitions (format: 'state symbol1 symbol2 ... symbolN next_state'):")
        print("  For sync: use vector of symbols (one per trace), e.g., 'q0 a b a q1'")
        print("  (Enter empty line to finish)")
    else:
        print("Enter transitions (format: 'state symbol next_state1 next_state2 ...'):")
        print("(Enter empty line to finish)")
    transitions = {}
    
    while True:
        line = input().strip()
        if not line:
            break
        
        parts = line.split()
        if len(parts) < 3:
            print(f"Invalid transition format: {line}. Skipping.")
            continue
        
        state = parts[0]
        
        if mode == 'synchronous':
            # For sync: state symbol1 symbol2 ... symbolN next_state
            # The number of symbols should match the number of traces (we'll validate later)
            # Last part is the next state
            if len(parts) < 3:
                print(f"Invalid transition format: {line}. Need at least state, symbols, and next_state. Skipping.")
                continue
            
            # All parts except first and last are symbols
            symbol_vector = tuple(parts[1:-1])
            next_state = parts[-1]
            next_states = {next_state}
            
            key = (state, symbol_vector)
            if key in transitions:
                transitions[key].update(next_states)
            else:
                transitions[key] = next_states
        else:
            # For async: state symbol next_state1 next_state2 ...
            symbol = parts[1]
            next_states = set(parts[2:])
            
            key = (state, symbol)
            if key in transitions:
                transitions[key].update(next_states)
            else:
                transitions[key] = next_states
    
    return {
        'mode': mode,
        'states': states,
        'alphabet': alphabet,
        'initial_state': initial_state,
        'accepting_states': accepting_states,
        'transitions': transitions
    }


def create_automaton(definition: Dict) -> HyperAutomaton:
    """
    Create a hyperautomaton instance from definition.
    
    Args:
        definition: Dictionary containing automaton definition
        
    Returns:
        HyperAutomaton instance (Synchronous or Asynchronous)
    """
    if definition['mode'] == 'synchronous':
        return SynchronousHyperAutomaton(
            states=definition['states'],
            alphabet=definition['alphabet'],
            initial_state=definition['initial_state'],
            accepting_states=definition['accepting_states'],
            transitions=definition['transitions']
        )
    else:
        return AsynchronousHyperAutomaton(
            states=definition['states'],
            alphabet=definition['alphabet'],
            initial_state=definition['initial_state'],
            accepting_states=definition['accepting_states'],
            transitions=definition['transitions']
        )


def parse_traces() -> list:
    """
    Parse traces (words) from input.
    
    Expected format:
    - First line: number of traces
    - Following lines: each trace as space-separated symbols
    
    Returns:
        List of traces, where each trace is a list of symbols
    """
    print("\nEnter traces to simulate:")
    print("Enter number of traces:")
    num_traces = int(input().strip())
    
    traces = []
    for i in range(num_traces):
        print(f"Enter trace {i+1} (space-separated symbols):")
        trace = input().strip().split()
        traces.append(trace)
    
    return traces


def main():
    """Main function to run the hyperautomata simulator."""
    try:
        # Parse automaton definition
        definition = parse_automaton_input()
        
        # Create automaton
        automaton = create_automaton(definition)
        print(f"\n✓ Created {definition['mode']} hyperautomaton")
        
        # Parse and run traces
        traces = parse_traces()
        
        # Import simulator
        from simulator import simulate_runs
        
        # Run simulation
        result = simulate_runs(automaton, traces)
        
        # Print results
        print("\n" + "="*50)
        print("SIMULATION RESULTS")
        print("="*50)
        print(f"Total traces: {result['summary']['total_traces']}")
        print(f"All traces accepted: {result['accepted']}")
        print(f"Trace lengths: {result['summary']['trace_lengths']}")
        
        # Print detailed history
        print("\nDetailed run history:")
        if isinstance(automaton, SynchronousHyperAutomaton):
            print("  (Synchronous: all traces are in the same state)")
            for step_info in result['run_history']:
                if 'step' in step_info and step_info['step'] < len(result['run_history']) - 1:
                    print(f"  Step {step_info['step']}:")
                    print(f"    Current state: {step_info['current_state']} (all traces)")
                    print(f"    Symbol vector: {step_info['symbol_vector']} (one from each trace)")
                    if 'chosen_state' in step_info:
                        print(f"    Next state: {step_info['chosen_state']} (all traces transition together)")
                    if len(step_info.get('next_states', [])) > 1:
                        print(f"    (Other possible states: {step_info['next_states']})")
            if result['run_history']:
                final = result['run_history'][-1]
                if 'final_state' in final:
                    print(f"  Final state: {final['final_state']} (all traces)")
                    print(f"  Accepted: {final['accepted']}")
        else:  # Asynchronous
            for trace_result in result['run_history']:
                print(f"\n  Trace {trace_result['trace_idx']}: {trace_result['trace']}")
                print(f"    Accepted: {trace_result['accepted']}")
                print(f"    Final state: {trace_result['final_state']}")
                for step in trace_result['steps']:
                    print(f"      Step {step['step']}: {step['current_state']} --{step['symbol']}--> {step['new_state']}")
        
        # Option to visualize
        print("\nWould you like to visualize the run? (y/n):")
        visualize_choice = input().strip().lower()
        if visualize_choice == 'y':
            from visualizer import visualize_run
            print("Choose visualization mode:")
            print("  1. Full run (shows entire run at once)")
            print("  2. Step-by-step (interactive with buttons)")
            mode_choice = input("Enter 1 or 2: ").strip()
            interactive = (mode_choice == '2')
            visualize_run(automaton, traces, result, interactive=interactive)
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

