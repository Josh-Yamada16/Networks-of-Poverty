import networkx as nx
import matplotlib.pyplot as plt

class Visualization:
    spring_lay = lambda x: nx.spring_layout(x, seed=42)
    circ_lay = lambda x: nx.circular_layout(x)
    
    @staticmethod
    def visualize_network(G, title="Network Visualization"):
        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_size=700, node_color='lightblue', font_size=10, font_color='black', edge_color='gray')
        plt.title(title)
        plt.show()
    
    @staticmethod
    def draw_node_labels(g, pos, ax):
        for node, (x, y) in pos.items():
            label = f"${g.nodes[node]['money']:.2f}"  # Format money however you want
            ax.text(
                x, y - 0.03,                  # Adjust Y-position to move below node
                label,
                fontsize=8,
                fontweight='bold',
                ha='center', va='top',
                color='black',               # Match node font color if needed
                bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.1')
            )

    @staticmethod
    def draw_graph_initial(g: nx.Graph, layout, title, node_colors):
        fig, ax = plt.subplots()
        nx.draw(g, pos=layout, with_labels=True, node_color=node_colors, node_size=500,\
                 font_color="white", font_size=15, font_weight='bold', width=3,\
                      edge_color='lightgray', cmap="viridis", ax=ax)
        # Visualization.draw_node_labels(g, layout, ax)
        ax.set_title(title)
        plt.show(block=False)
        plt.waitforbuttonpress()
        return ax

    @staticmethod
    def redraw(g: nx.Graph, layout, title, node_colors, ax):
        ax.cla()
        nx.draw_networkx_edges(g, layout, ax=ax, edge_color='lightgray', width=2)
        nx.draw_networkx_nodes(g, layout, node_color=node_colors, cmap="viridis", ax=ax)
        Visualization.draw_node_labels(g, layout, ax)
        ax.set_title(title)
        plt.waitforbuttonpress()
