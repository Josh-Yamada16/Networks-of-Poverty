import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.animation import FuncAnimation
import networkx as nx
from .visualizer import Visualization as viz
import parameters as P

class InteractivePlot:
    def __init__(self, states, layout):
        self.states = states  # list of (graph, layout, title, node_colors)
        self.current_index = 0
        self.layout = dict(layout)
        self._auto_running = False
        self.cbar = None
        self.ani = None

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        plt.subplots_adjust(bottom=0.2)

        # Button setup
        self.toggle_ax = plt.axes([0.36, 0.05, 0.1, 0.075])
        self.toggle_button = Button(self.toggle_ax, 'End')

        self.prev_ax = self.fig.add_axes([0.47, 0.05, 0.1, 0.075])
        self.next_ax = self.fig.add_axes([0.58, 0.05, 0.1, 0.075])
        self.loop_ax = plt.axes([0.69, 0.05, 0.1, 0.075])

        self.next_button = Button(self.next_ax, 'Next')
        self.prev_button = Button(self.prev_ax, 'Prev')
        self.loop_button = Button(self.loop_ax, 'Loop')

        self.toggle_button.on_clicked(self.toggle_begin_end)
        self.prev_button.on_clicked(self.prev)
        self.next_button.on_clicked(self.next)
        self.loop_button.on_clicked(self.toggle_loop)

    def _layout_for_graph(self, g):
        missing_nodes = [node for node in g.nodes() if node not in self.layout]
        if missing_nodes:
            fixed_nodes = [node for node in g.nodes() if node in self.layout]
            # Keep existing node positions stable and only place newly added nodes.
            self.layout = nx.spring_layout(g, pos=self.layout, fixed=fixed_nodes, seed=42)
        return self.layout

    def draw_current(self):
        self.ax.clear()
        g, node_colors = self.states[self.current_index]
        render_layout = self._layout_for_graph(g)
        nx.draw(g, pos=render_layout, ax=self.ax, node_color=node_colors, with_labels=P.SHOW_NODE_LABELS,
                edge_color='lightgray', width=2, node_size=500, font_color='white', font_size=10)
        if self.current_index == 0:
            self.ax.set_title("Initial State")
        else:
            self.ax.set_title(f"Iteration {self.current_index}")

        self.fig.canvas.draw_idle()

    def toggle_begin_end(self, event):
        if self.current_index == len(self.states) - 1:
            self.current_index = 0
        else:
            self.current_index = len(self.states) - 1
        self.draw_current()
        self.update_toggle_button_label()

    def next(self, event):
        if self.current_index < len(self.states) - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        self.draw_current()
        self.update_toggle_button_label()

    def prev(self, event):
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.states) - 1
        self.draw_current()
        self.update_toggle_button_label()

    def toggle_loop(self, event):
        if self._auto_running:
            self._auto_running = False
            self.loop_button.label.set_text('Loop')
        else:
            self._auto_running = True
            self.loop_button.label.set_text('Stop')
            self.ani = FuncAnimation(self.fig, self._update_animation_frame, interval=100, cache_frame_data=False)
            self.next(None)

    def _update_animation_frame(self, frame):
        if not self._auto_running:
            if self.ani:
                self.ani.event_source.stop()
            return
        self.current_index = (self.current_index + 1) % len(self.states)
        self.draw_current()
        self.update_toggle_button_label()

    def update_toggle_button_label(self):
        if self.current_index == len(self.states) - 1:
            self.toggle_button.label.set_text('Beginning')
        else:
            self.toggle_button.label.set_text('End')
