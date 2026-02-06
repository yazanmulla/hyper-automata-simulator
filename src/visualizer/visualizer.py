
"""
Visualizer for hyperautomata runs using matplotlib (Word View + Graph View).
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
import networkx as nx
from typing import List, Tuple, Optional
from src.base import NFH


def visualize_automaton(automaton: NFH, title: str = "NFH"):
    """
    Visualize structure only (static).
    """
    G = build_automaton_graph(automaton)
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=2000, font_weight='bold', arrows=True)
    plt.title(f"Automaton: {title}")
    plt.show()

def build_automaton_graph(automaton: NFH) -> nx.DiGraph:
    """Builds a NetworkX graph from the NFH."""
    G = nx.DiGraph()
    
    # Add nodes
    for state in automaton.states:
        # Color accepting states differently in base attributes
        color = 'lightgreen' if state in automaton.accepting_states else 'lightblue'
        if state in automaton.initial_states:
             color = 'gold'
        G.add_node(state, color=color, label=str(state))
        
    # Add edges
    # delta structure: list of (q, syms, next_q)
    # We aggregate edges to avoid clutter? Or just multigraph? 
    # For simplicitly, DiGraph with labeling.
    
    edge_labels = {}
    
    for q, syms, next_q in automaton.delta:
        # syms is a tuple ('a', 'b') etc.
        # Check if edge exists
        if G.has_edge(q, next_q):
            # Append label
            current_label = edge_labels.get((q, next_q), "")
            new_label = f"{syms}"
            # Avoid too long labels?
            if len(current_label) < 20: 
                 edge_labels[(q, next_q)] = current_label + "\n" + new_label
        else:
            G.add_edge(q, next_q)
            edge_labels[(q, next_q)] = f"{syms}"
            
    # Store labels in graph for access later? or return them?
    # Easier to just attach to edge data if possible, but nx drawing needs distinct dict for labels.
    G.graph['edge_labels'] = edge_labels
    return G

def visualize_run(automaton: NFH, run_history: List[Tuple], 
                  save_path: str = None, interactive: bool = False,
                  initial_assignment: List[str] = None):
    if interactive:
        _visualize_run_interactive(automaton, run_history, initial_assignment)
    else:
        print("Static visualization disabled.")


def _visualize_run_interactive(automaton: NFH, run_history: List[Tuple], initial_assignment: List[str] = None):
    
    if not run_history:
        print("No run history to visualize.")
        return
    
    if not initial_assignment:
        print("Initial assignment is required for visualization.")
        return

    # --- Data Prep ---
    k = len(initial_assignment)
    states_data = [] 
    if run_history:
        states_data.append(run_history[0][0]) 
    
    cursor_history = []
    current_cursors = [0] * k
    cursor_history.append(list(current_cursors))
    
    transitions_data = [] 
    
    for index, transition_tuple in enumerate(run_history):
        q_curr, syms_vector, q_next = transition_tuple
        transitions_data.append((q_curr, syms_vector, q_next))
        states_data.append(q_next)
        
        for i, sym in enumerate(syms_vector):
            if sym != '#':
                current_cursors[i] += 1
        cursor_history.append(list(current_cursors))

    # --- Graph Prep ---
    G = build_automaton_graph(automaton)
    # Use spring layout but fix it
    pos = nx.spring_layout(G, seed=42, k=0.9) 
    base_edge_labels = G.graph.get('edge_labels', {})

    # --- Figure ---
    fig = plt.figure(figsize=(14, 12)) 
    
    # Layout Breakdown
    # Top: Graph (0.55 to 0.95 -> Height 0.4)
    ax_graph = plt.axes([0.05, 0.55, 0.9, 0.4])
    ax_graph.axis('off')
    
    # Middle: Words (0.20 to 0.50 -> Height 0.3)
    ax_words = plt.axes([0.05, 0.20, 0.9, 0.3])
    ax_words.axis('off')
    
    # Bottom: Info (0.08 to 0.18 -> Height 0.1)
    ax_info = plt.axes([0.05, 0.08, 0.9, 0.1])
    ax_info.axis('off')
    
    # Controls (Bottom strip)
    btn_bottom = 0.02
    btn_height = 0.04
    
    ax_prev = plt.axes([0.1, btn_bottom, 0.1, btn_height])
    ax_next = plt.axes([0.22, btn_bottom, 0.1, btn_height])
    ax_reset = plt.axes([0.34, btn_bottom, 0.1, btn_height])
    ax_anim = plt.axes([0.55, btn_bottom, 0.12, btn_height])
    ax_interval = plt.axes([0.80, btn_bottom, 0.1, btn_height])
    
    current_step = [0]
    anim_state = {'running': False, 'timer': None, 'interval': 400}
    
    # --- Helpers ---
    
    def render_text_fixed_grid(ax, x, y, text_str, highlight_idx):
        fs = 16 # Slightly smaller to fit bounds
        char_interval = 0.022 
        MAX_VISIBLE = 35 
        
        if len(text_str) <= MAX_VISIBLE:
            visible_str = text_str
            start_offset = 0
            show_left_ell = False
            show_right_ell = False
        else:
            half_win = MAX_VISIBLE // 2
            win_start = highlight_idx - half_win
            if win_start < 0: win_start = 0
            win_end = win_start + MAX_VISIBLE
            if win_end > len(text_str):
                win_end = len(text_str)
                win_start = max(0, win_end - MAX_VISIBLE)
            visible_str = text_str[win_start:win_end]
            start_offset = win_start
            show_left_ell = (win_start > 0)
            show_right_ell = (win_end < len(text_str))

        if show_left_ell:
             ax.text(x - 0.03, y, "<", color='gray', fontsize=fs, fontfamily='monospace', transform=ax.transAxes)

        for i, ch in enumerate(visible_str):
            true_idx = start_offset + i
            color = 'red' if true_idx == highlight_idx else 'black'
            weight = 'bold' if true_idx == highlight_idx else 'normal'
            x_pos = x + (i * char_interval)
            ax.text(x_pos, y, ch, color=color, fontsize=fs, fontfamily='monospace', fontweight=weight, transform=ax.transAxes, ha='left')
                    
        if show_right_ell:
             x_end = x + (len(visible_str) * char_interval)
             ax.text(x_end, y, ">", color='gray', fontsize=fs, fontfamily='monospace', transform=ax.transAxes)

    def format_sym_vector(syms):
        if len(syms) == 1:
            return f"({syms[0]})"
        return str(syms)

    def update_visualization():
        # Clear Axes
        ax_graph.clear()
        ax_graph.axis('off')
        
        ax_words.clear()
        ax_words.axis('off')
        
        ax_info.clear()
        ax_info.axis('off')
        
        # Get Step
        step = current_step[0]
        max_step = len(states_data) - 1
        
        if step >= len(states_data): step = len(states_data) - 1; current_step[0] = step
        if step >= len(cursor_history): step = len(cursor_history) - 1; current_step[0] = step
        if step == max_step and anim_state['running']: stop_animation()

        curr_state = states_data[step]
        
        # --- 1. Draw Graph ---
        node_colors = []
        for node in G.nodes():
            if node == curr_state:
                node_colors.append('#ff7f0e') # Matplotlib Orange
            else:
                node_colors.append(G.nodes[node].get('color', 'lightblue'))
        
        edge_colors = ['gray'] * len(G.edges())
        edge_widths = [1] * len(G.edges())
        
        # Highlight previous transition edge if possible
        # This is tricky with multigraphs or labels, but simple check:
        if step > 0 and (step - 1) < len(transitions_data):
            q_prev, _, q_curr_trans = transitions_data[step-1]
            # Try to find edge (q_prev, q_curr_trans) index
            try:
                edges_list = list(G.edges())
                if (q_prev, q_curr_trans) in edges_list:
                    idx = edges_list.index((q_prev, q_curr_trans))
                    edge_colors[idx] = 'red'
                    edge_widths[idx] = 2.5
            except ValueError:
                pass

        nx.draw_networkx_nodes(G, pos, ax=ax_graph, node_color=node_colors, node_size=1500)
        nx.draw_networkx_labels(G, pos, ax=ax_graph, font_weight='bold')
        nx.draw_networkx_edges(G, pos, ax=ax_graph, edge_color=edge_colors, width=edge_widths, arrowsize=20)
        nx.draw_networkx_edge_labels(G, pos, ax=ax_graph, edge_labels=base_edge_labels, font_size=8)
        ax_graph.set_title("Automaton State", fontsize=14, loc='left')

        # --- 2. Update Info ---
        is_acc = curr_state in automaton.accepting_states
        state_display = f"{curr_state} (Accepting)" if is_acc else f"{curr_state}"
        
        if step == 0:
            status_text = f"Start\nCurrent State: {state_display}"
        else:
            if (step - 1) < len(transitions_data):
                q_prev, syms, q_curr = transitions_data[step-1]
                trans_str = f"{q_prev}-{format_sym_vector(syms)}->{q_curr}"
                last_trans = f"Last Transition: {trans_str}"
            else:
                last_trans = "End"
            status_text = f"Step: {step} / {max_step}\nCurrent State: {state_display}\n{last_trans}"
        
        ax_info.text(0.5, 0.5, status_text, fontsize=14, ha='center', va='center', transform=ax_info.transAxes)
        
        # --- 3. Update Words ---
        if step < len(cursor_history):
            cursors = cursor_history[step]
            y_start = 0.8
            y_step = 0.15
            for i, word in enumerate(initial_assignment):
                c_idx = cursors[i]
                y_pos = y_start - (i * y_step)
                ax_words.text(0.05, y_pos, f"x{i+1}: ", fontsize=16, color='blue', transform=ax_words.transAxes)
                render_text_fixed_grid(ax_words, 0.15, y_pos, word, c_idx)
        else:
             ax_words.text(0.5, 0.5, "Error", ha='center')
            
        plt.draw()

    # --- Interaction ---

    def on_prev(event):
        if current_step[0] > 0:
            current_step[0] -= 1
            update_visualization()
            
    def on_next(event=None): 
        if current_step[0] < len(states_data) - 1:
            current_step[0] += 1
            update_visualization()
            
    def on_reset(event):
        stop_animation()
        current_step[0] = 0
        update_visualization()

    def timer_callback():
        on_next()
    
    def start_animation():
        if not anim_state['running']:
            anim_state['running'] = True
            btn_anim.label.set_text("Pause")
            if anim_state['timer']: anim_state['timer'].stop()
            timer = fig.canvas.new_timer(interval=anim_state['interval'])
            timer.add_callback(timer_callback)
            timer.start()
            anim_state['timer'] = timer
            plt.draw()

    def stop_animation():
        if anim_state['running']:
            anim_state['running'] = False
            btn_anim.label.set_text("Animate")
            if anim_state['timer']:
                anim_state['timer'].stop()
                anim_state['timer'] = None
            plt.draw()

    def toggle_animation(event):
        if anim_state['running']:
            stop_animation()
        else:
            if current_step[0] >= len(states_data) - 1:
                current_step[0] = 0
                update_visualization()
            start_animation()

    def submit_interval(text):
        try:
            val = float(text)
            if val < 0.01: val = 0.01
            anim_state['interval'] = int(val * 1000)
            if anim_state['running']:
                stop_animation(); start_animation()
        except ValueError: pass

    btn_prev = Button(ax_prev, 'Previous')
    btn_next = Button(ax_next, 'Next')
    btn_reset = Button(ax_reset, 'Reset')
    btn_anim = Button(ax_anim, 'Animate')
    text_interval = TextBox(ax_interval, 'Interval (s): ', initial="0.4")
    
    btn_prev.on_clicked(on_prev)
    btn_next.on_clicked(on_next)
    btn_reset.on_clicked(on_reset)
    btn_anim.on_clicked(toggle_animation)
    text_interval.on_submit(submit_interval)
    
    update_visualization()
    plt.show()
