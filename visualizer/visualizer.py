"""
Visualizer for hyperautomata runs using networkx and matplotlib.
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import networkx as nx
from typing import List, Dict
from hyperautomata import NFH


def visualize_automaton(automaton: NFH, title: str = "NFH"):
    G = nx.DiGraph()
    
    # Add nodes (states)
    for state in automaton.states:
        node_color = 'lightgreen' if state in automaton.accepting_states else 'lightblue'
        if state == automaton.initial_state:
            node_color = 'lightyellow'
        G.add_node(state, color=node_color)
    
    # Add edges (transitions)
    edge_labels = {}
    for (state, symbol), next_states in automaton.transitions.items():
        for next_state in next_states:
            if G.has_edge(state, next_state):
                # Multiple transitions between same states - append label
                edge_labels[(state, next_state)] += f", {symbol}"
            else:
                G.add_edge(state, next_state)
                edge_labels[(state, next_state)] = symbol
    
    # Create layout
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Draw the graph
    plt.figure(figsize=(12, 8))
    
    # Draw nodes
    node_colors = [G.nodes[node].get('color', 'lightgray') for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=2000, alpha=0.9)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', 
                          arrows=True, arrowsize=20, alpha=0.6)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # Draw edge labels
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='lightyellow', label='Initial State'),
        Patch(facecolor='lightgreen', label='Accepting State'),
        Patch(facecolor='lightblue', label='Regular State')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def visualize_run(automaton: NFH, traces: List[List[str]], 
                  result: Dict, save_path: str = None, interactive: bool = False):
    if interactive:
        _visualize_run_interactive(automaton, traces, result)
    else:
        _visualize_run_static(automaton, traces, result, save_path)


def _visualize_run_static(automaton: NFH, traces: List[List[str]],
                               result: Dict, save_path: str = None):
    run_history = result['run_history']
    
    if not run_history:
        print("No run history to visualize.")
        return
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot 1: State transitions over time (all traces in same state)
    ax1 = axes[0]
    steps = []
    states = []
    
    for step_info in run_history:
        if 'step' in step_info and 'current_state' in step_info:
            steps.append(step_info['step'])
            states.append(step_info['current_state'])
        elif 'final_state' in step_info:
            # Add final state
            steps.append(len(steps))
            states.append(step_info['final_state'])
    
    if steps and states:
        # Create a mapping from states to y-positions
        all_states = sorted(automaton.states)
        state_to_y = {state: i for i, state in enumerate(all_states)}
        
        # All traces are in the same state, so plot one line
        y_positions = [state_to_y.get(state, 0) for state in states]
        ax1.plot(steps, y_positions, marker='o', linewidth=3, 
                markersize=10, label='All traces (same state)', color='blue')
        
        ax1.set_xlabel('Step', fontsize=12)
        ax1.set_ylabel('State', fontsize=12)
        ax1.set_title('Synchronous Run: All Traces in Same State', 
                     fontsize=14, fontweight='bold')
        ax1.set_yticks(range(len(all_states)))
        ax1.set_yticklabels(all_states)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
    
    # Plot 2: Automaton structure with highlighted path
    ax2 = axes[1]
    G = nx.DiGraph()
    
    # Add nodes
    for state in automaton.states:
        node_color = 'lightgreen' if state in automaton.accepting_states else 'lightblue'
        if state == automaton.initial_state:
            node_color = 'lightyellow'
        G.add_node(state, color=node_color)
    
    # Add edges with vector symbol labels
    edge_labels = {}
    for (state, symbol_vector), next_states in automaton.transitions.items():
        # symbol_vector is a tuple for sync, single symbol for async
        if isinstance(symbol_vector, tuple):
            label = ','.join(symbol_vector)  # Show vector as comma-separated
        else:
            label = symbol_vector
        
        for next_state in next_states:
            edge = (state, next_state)
            if edge in edge_labels:
                edge_labels[edge] += f", ({label})"
            else:
                edge_labels[edge] = f"({label})"
            if not G.has_edge(state, next_state):
                G.add_edge(state, next_state)
    
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Highlight path taken
    edge_colors = []
    edge_widths = []
    used_edges = set()
    
    for step_info in run_history:
        if 'current_state' in step_info and 'chosen_state' in step_info:
            curr = step_info['current_state']
            next_state = step_info['chosen_state']
            used_edges.add((curr, next_state))
    
    for edge in G.edges():
        used = edge in used_edges
        
        if used:
            edge_colors.append('red')
            edge_widths.append(3)
        else:
            edge_colors.append('gray')
            edge_widths.append(1)
    
    node_colors = [G.nodes[node].get('color', 'lightgray') for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=2000, alpha=0.9, ax=ax2)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, 
                          width=edge_widths, arrows=True, 
                          arrowsize=20, alpha=0.6, ax=ax2)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=ax2)
    
    ax2.set_title('Automaton Structure (Red edges = used, labels show symbol vectors)', 
                 fontsize=14, fontweight='bold')
    ax2.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {save_path}")
    else:
        plt.show()




def _visualize_run_interactive(automaton: NFH, traces: List[List[str]],
                                          result: Dict):        
    run_history = result['run_history']
    
    if not run_history:
        print("No run history to visualize.")
        return
    
    # Prepare data
    steps_data = []
    states_data = []
    symbol_vectors = []
    
    for step_info in run_history:
        if 'step' in step_info and 'current_state' in step_info:
            steps_data.append(step_info['step'])
            states_data.append(step_info['current_state'])
            symbol_vectors.append(step_info.get('symbol_vector', ()))
        elif 'final_state' in step_info:
            steps_data.append(len(steps_data))
            states_data.append(step_info['final_state'])
            symbol_vectors.append(())
    
    if not steps_data:
        print("No valid steps to visualize.")
        return
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 10))
    
    # Create axes for plots
    ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=3, rowspan=2)
    ax2 = plt.subplot2grid((3, 3), (2, 0), colspan=3)
    
    # Button area
    ax_prev = plt.axes([0.1, 0.02, 0.1, 0.04])
    ax_next = plt.axes([0.25, 0.02, 0.1, 0.04])
    ax_reset = plt.axes([0.4, 0.02, 0.1, 0.04])
    ax_info = plt.axes([0.55, 0.02, 0.4, 0.04])
    ax_info.axis('off')
    
    # Current step tracker
    current_step = [0]  # Use list to allow modification in nested functions
    
    # Build automaton graph (static)
    G = nx.DiGraph()
    for state in automaton.states:
        node_color = 'lightgreen' if state in automaton.accepting_states else 'lightblue'
        if state == automaton.initial_state:
            node_color = 'lightyellow'
        G.add_node(state, color=node_color)
    
    edge_labels = {}
    for (state, symbol_vector), next_states in automaton.transitions.items():
        if isinstance(symbol_vector, tuple):
            label = ','.join(symbol_vector)
        else:
            label = symbol_vector
        
        for next_state in next_states:
            edge = (state, next_state)
            if edge in edge_labels:
                edge_labels[edge] += f", ({label})"
            else:
                edge_labels[edge] = f"({label})"
            if not G.has_edge(state, next_state):
                G.add_edge(state, next_state)
    
    pos = nx.spring_layout(G, k=2, iterations=50)
    all_states = sorted(automaton.states)
    state_to_y = {state: i for i, state in enumerate(all_states)}
    
    def update_visualization():
        ax1.clear()
        ax2.clear()
        
        step_idx = current_step[0]
        max_step = len(steps_data) - 1
        
        # Plot 1: State transitions up to current step
        if step_idx >= 0:
            steps_to_show = steps_data[:step_idx + 1]
            states_to_show = states_data[:step_idx + 1]
            
            y_positions = [state_to_y.get(state, 0) for state in states_to_show]
            ax1.plot(steps_to_show, y_positions, marker='o', linewidth=3, 
                    markersize=12, label='All traces (same state)', color='blue', zorder=3)
            
            # Highlight current position
            if step_idx < len(steps_data):
                ax1.scatter([steps_data[step_idx]], [state_to_y.get(states_data[step_idx], 0)], 
                           s=200, color='red', zorder=4, edgecolors='black', linewidths=2)
        
        ax1.set_xlabel('Step', fontsize=12)
        ax1.set_ylabel('State', fontsize=12)
        ax1.set_title(f'Synchronous Run: Step {step_idx}/{max_step}', 
                     fontsize=14, fontweight='bold')
        ax1.set_yticks(range(len(all_states)))
        ax1.set_yticklabels(all_states)
        ax1.set_xlim(-0.5, max(len(steps_data) - 1, 0) + 0.5)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot 2: Automaton structure with highlighted path up to current step
        edge_colors = []
        edge_widths = []
        used_edges = set()
        
        # Mark edges used up to current step
        for i in range(min(step_idx + 1, len(run_history) - 1)):
            step_info = run_history[i]
            if 'current_state' in step_info and 'chosen_state' in step_info:
                curr = step_info['current_state']
                next_state = step_info['chosen_state']
                used_edges.add((curr, next_state))
        
        for edge in G.edges():
            used = edge in used_edges
            if used:
                edge_colors.append('red')
                edge_widths.append(3)
            else:
                edge_colors.append('gray')
                edge_widths.append(1)
        
        # Highlight current state node
        node_colors = []
        for node in G.nodes():
            base_color = G.nodes[node].get('color', 'lightgray')
            if node == states_data[min(step_idx, len(states_data) - 1)]:
                node_colors.append('orange')  # Highlight current state
            else:
                node_colors.append(base_color)
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=2000, alpha=0.9, ax=ax2)
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, 
                              width=edge_widths, arrows=True, 
                              arrowsize=20, alpha=0.6, ax=ax2)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax2)
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=ax2)
        
        ax2.set_title('Automaton Structure', fontsize=14, fontweight='bold')
        ax2.axis('off')
        
        # Update info text
        if step_idx < len(states_data):
            state = states_data[step_idx]
            symbol_vec = symbol_vectors[step_idx] if step_idx < len(symbol_vectors) else ()
            info_text = f"Step {step_idx}: State={state}"
            if symbol_vec:
                info_text += f", Symbols={symbol_vec}"
            if step_idx < len(run_history) - 1:
                next_info = run_history[step_idx]
                if 'chosen_state' in next_info:
                    info_text += f" → {next_info['chosen_state']}"
            ax_info.text(0.05, 0.5, info_text, fontsize=11, 
                        verticalalignment='center', fontweight='bold')
        
        plt.draw()
    
    def on_prev(event):
        if current_step[0] > 0:
            current_step[0] -= 1
            update_visualization()
    
    def on_next(event):
        if current_step[0] < len(steps_data) - 1:
            current_step[0] += 1
            update_visualization()
    
    def on_reset(event):
        current_step[0] = 0
        update_visualization()
    
    # Create buttons
    btn_prev = Button(ax_prev, 'Previous')
    btn_next = Button(ax_next, 'Next')
    btn_reset = Button(ax_reset, 'Reset')
    
    btn_prev.on_clicked(on_prev)
    btn_next.on_clicked(on_next)
    btn_reset.on_clicked(on_reset)
    
    # Initial visualization
    update_visualization()
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)
    plt.show()




