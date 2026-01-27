
"""
Visualizer for hyperautomata runs using matplotlib (Word View).
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
from typing import List, Tuple, Optional
from src.base import NFH


def visualize_automaton(automaton: NFH, title: str = "NFH"):
    """
    Deprecated: Graph visualization is removed.
    Printing a warning or effectively doing nothing if called, 
    but for now we can just print structure text to stdout or ignore.
    """
    print(f"Visualizing Automaton '{title}': (Graph view disabled)")
    print(f"States: {automaton.states}")
    print(f"Initial: {automaton.initial_states}")
    print(f"Accepting: {automaton.accepting_states}")


def visualize_run(automaton: NFH, run_history: List[Tuple], 
                  save_path: str = None, interactive: bool = False,
                  initial_assignment: List[str] = None):
    if interactive:
        _visualize_run_interactive(automaton, run_history, initial_assignment)
    else:
        print("Static visualization disabled in Word View mode.")


def _visualize_run_interactive(automaton: NFH, run_history: List[Tuple], initial_assignment: List[str] = None):
    
    if not run_history:
        print("No run history to visualize.")
        return
    
    if not initial_assignment:
        print("Initial assignment is required for Word View visualization.")
        return

    # 1. Pre-calculate cursor positions per step
    # ----------------------------------------
    k = len(initial_assignment)
    
    states_data = [] # List of state names
    if run_history:
        states_data.append(run_history[0][0]) # Initial state
    
    cursor_history = []
    current_cursors = [0] * k
    cursor_history.append(list(current_cursors))
    
    transitions_data = [] # List of tuples containing (prev_state, syms_vector, next_state)
    
    for index, transition_tuple in enumerate(run_history):
        q_curr, syms_vector, q_next = transition_tuple
        
        transitions_data.append((q_curr, syms_vector, q_next))
        states_data.append(q_next)
        
        for i, sym in enumerate(syms_vector):
            if sym != '#':
                current_cursors[i] += 1
        
        cursor_history.append(list(current_cursors))

    # 2. Setup Figure
    # ---------------
    fig = plt.figure(figsize=(14, 8)) # Slightly wider for controls
    
    # Main area for Words
    ax_words = plt.axes([0.1, 0.3, 0.8, 0.6])
    ax_words.axis('off')
    
    # Info/Status area
    ax_info = plt.axes([0.1, 0.15, 0.8, 0.1])
    ax_info.axis('off')
    
    # Controls Layout
    btn_bottom = 0.05
    btn_height = 0.05
    
    # Navigation Buttons (Left)
    ax_prev = plt.axes([0.1, btn_bottom, 0.1, btn_height])
    ax_next = plt.axes([0.21, btn_bottom, 0.1, btn_height])
    ax_reset = plt.axes([0.32, btn_bottom, 0.1, btn_height])
    
    # Animation Controls (Right)
    ax_anim = plt.axes([0.55, btn_bottom, 0.12, btn_height])
    
    # Interval Input (Far Right)
    # Label is handled by TextBox, but we need space for it
    ax_interval = plt.axes([0.80, btn_bottom, 0.1, btn_height])
    
    current_step = [0]
    
    # Animation State
    anim_state = {
        'running': False,
        'timer': None,
        'interval': 400 # ms
    }
    
    def render_text_fixed_grid(ax, x, y, text_str, highlight_idx):
        fs = 18
        char_interval = 0.022 
        MAX_VISIBLE = 35 
        
        # Determine Window
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
        ax_words.clear()
        ax_words.axis('off')
        
        ax_info.clear()
        ax_info.axis('off')
        
        step = current_step[0]
        max_step = len(states_data) - 1
        
        # FAILSAFE
        if step >= len(states_data):
            step = len(states_data) - 1
            current_step[0] = step
        if step >= len(cursor_history):
             step = len(cursor_history) - 1
             current_step[0] = step

        # Auto-stop animation if end reached
        if step == max_step and anim_state['running']:
             stop_animation()

        # 1. Info
        curr_state = states_data[step]
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
        
        # 2. Words
        if step < len(cursor_history):
            cursors = cursor_history[step]
            y_start = 0.8
            y_step = 0.15
            for i, word in enumerate(initial_assignment):
                c_idx = cursors[i]
                y_pos = y_start - (i * y_step)
                ax_words.text(0.05, y_pos, f"x{i+1}: ", fontsize=18, color='blue', transform=ax_words.transAxes)
                render_text_fixed_grid(ax_words, 0.15, y_pos, word, c_idx)
        else:
            ax_words.text(0.5, 0.5, "Data Error", ha='center')
            
        plt.draw()

    # --- Callbacks ---

    def on_prev(event):
        if current_step[0] > 0:
            current_step[0] -= 1
            update_visualization()
            
    def on_next(event=None): # Optional event arg for timer call
        if current_step[0] < len(states_data) - 1:
            current_step[0] += 1
            update_visualization()
            
    def on_reset(event):
        stop_animation()
        current_step[0] = 0
        update_visualization()

    # --- Animation Logic ---

    def timer_callback():
        on_next()
    
    def start_animation():
        if not anim_state['running']:
            anim_state['running'] = True
            btn_anim.label.set_text("Stop")
            
            # Create/Start Timer
            if anim_state['timer']:
                anim_state['timer'].stop()
            
            # Interval in ms
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
            # If at end, reset to start? Or just don't start?
            # User might want to restart manually. 
            # If at end, let's wrap to 0? Or just do nothing.
            # Let's wrap to 0 if at end for convenience.
            if current_step[0] >= len(states_data) - 1:
                current_step[0] = 0
                update_visualization()
            
            start_animation()

    def submit_interval(text):
        try:
            val = float(text)
            if val < 0.01: val = 0.01 # Min limit
            ms = int(val * 1000)
            anim_state['interval'] = ms
            
            # Restart timer if running
            if anim_state['running']:
                stop_animation()
                start_animation()
        except ValueError:
            pass # Ignore invalid

    # --- Controls ---

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
