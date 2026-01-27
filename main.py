
import sys
import argparse
import json
from typing import Set, Tuple, List, Dict, Optional
from src.base import NFH, Hyperword
from src.simulator import checkMembership
from src.parser import parse_nfh_from_text
from src.visualizer.visualizer import visualize_run

def get_input(prompt: str) -> str:
    print(prompt)
    return input().strip()

def get_multiline_input(prompt: str) -> str:
    print(prompt)
    print("(Enter 'END' on a new line to finish, or Ctrl+D)")
    lines = []
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            if line.strip() == 'END':
                break
            lines.append(line)
        except EOFError:
            break
    return "".join(lines)

def parse_nfh() -> NFH:
    print("\n--- Define NFH ---")
    print("Format example:")
    print("k: 1")
    print("alpha: E")
    print("states: q0 q1")
    print("initial: q0")
    print("accepting: q1")
    print("alphabet: a b")
    print("delta:")
    print("q0 a q1")
    print("-------------------")
    
    data = get_multiline_input("Enter your NFH definition:")
    return parse_nfh_from_text(data)

def parse_hyperword() -> Hyperword:
    print("\n--- Define Hyperword (Set of Words) ---")
    print("Enter words (one per line). Enter empty line to finish.")
    
    words = set()
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        words.add(line)
        
    return Hyperword(words)

def load_nfh_from_json(path: str) -> NFH:
    with open(path, 'r') as f:
        data = json.load(f)
    
    # Extract fields
    k = data['k']
    alpha = data['alpha']
    states = set(data['states'])
    initial = set(data.get('initial', data.get('initial_states')))
    accepting = set(data.get('accepting', data.get('accepting_states')))
    alphabet = set(data['alphabet'])
    
    # Delta
    delta = set()
    for trans in data['delta']:
        # Format: [state, [syms], next_state]
        state = trans[0]
        symbols = tuple(trans[1])
        next_state = trans[2]
        delta.add((state, symbols, next_state))
        
    return NFH(states, initial, accepting, k, delta, alpha, alphabet)

def load_hyperword_from_json(path: str) -> Hyperword:
    with open(path, 'r') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        words = set(data)
    elif isinstance(data, dict) and 'words' in data:
        words = set(data['words'])
    else:
        raise ValueError("Invalid Hyperword JSON format. Expected list or object with 'words' key.")
        
    return Hyperword(words)

def main():
    parser = argparse.ArgumentParser(description="NFH Simulator")
    parser.add_argument("-nfh", help="Path to NFH JSON file")
    parser.add_argument("-hyperword", help="Path to Hyperword JSON file")
    args = parser.parse_args()

    try:
        if args.nfh:
            print(f"Loading NFH from {args.nfh}...")
            nfh = load_nfh_from_json(args.nfh)
            print("NFH Loaded Successfully.")
        else:
            nfh = parse_nfh()
            print("\nNFH Created Successfully.")
        
        if args.hyperword:
            print(f"Loading Hyperword from {args.hyperword}...")
            hyperword = load_hyperword_from_json(args.hyperword)
        else:
            hyperword = parse_hyperword()
        
        print(f"\nHyperword: {hyperword}")
        
        print("\nChecking Membership...")
        is_accepted, managers = checkMembership(nfh, hyperword)
        
        print("\n" + "="*30)
        if is_accepted and managers:
            print("RESULT: ACCEPTED (True)")
            print(f"Succeeded on {len(managers)} branch(es).")
            
            for i, mgr in enumerate(managers):
                print(f"\nRun #{i+1} (Assignment: {mgr.initial_assignment}):")
                print(mgr.run_history)
            
            while True:
                prompt_msg = "\nVisualize a run? Enter number (1-{}) or 'n' to finish:".format(len(managers))
                if len(managers) == 1:
                     prompt_msg = "\nVisualize this run? (y/n):"
                
                vis_choice = get_input(prompt_msg).lower()
                
                if vis_choice == 'n':
                    break
                
                # Handle single run 'y' shortcut
                if len(managers) == 1 and vis_choice == 'y':
                    vis_choice = '1'

                if vis_choice.isdigit():
                    idx = int(vis_choice) - 1
                    if 0 <= idx < len(managers):
                        print(f"Launching visualizer for Run #{idx+1}...")
                        mgr = managers[idx]
                        visualize_run(nfh, mgr.run_history, 
                                    initial_assignment=mgr.initial_assignment, 
                                    interactive=True)
                    else:
                        print("Invalid number.")
                else:
                    print("Invalid input.")
        else:
            print("RESULT: REJECTED (False)")
        print("="*30)
        
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    main()
