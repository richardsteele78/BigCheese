import networkx as nx
from pyvis.network import Network

image_path = r"assets/cheese.png"

def create_custom_graph(df):
    # Define colors
    director_color = "rgb(247,122,64)"
    non_director_color = "rgb(51,96,101)"  # Teal color for non-directors
    vertical_spacing = 100  # Spacing between blue nodes in the vertical line
    horizontal_offset = 200  # Horizontal offset for orange nodes

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges based on the DataFrame
    for idx, row in df.iterrows():
        # Add Entity1 and Entity2 as nodes
        G.add_node(row['Entity1'], color=director_color if row['Role'] == 'Director' else non_director_color, label=row['Entity1'])
        G.add_node(row['Entity2'], color=director_color if row['Role'] == 'Director' else non_director_color, label=row['Entity2'])
        # Add an edge between Entity1 and Entity2 with the role as the label
        G.add_edge(row['Entity1'], row['Entity2'], label=row['Role'])

    # Create a PyVis network visualization
    net = Network(notebook=True, cdn_resources='remote')

    # Define positions for blue nodes (non-directors) in a strict vertical line
    pos = {}
    blue_nodes = [node for node, data in G.nodes(data=True) if data['color'] == non_director_color]
    for i, node in enumerate(reversed(blue_nodes)):  # Reverse to start from the bottom
        pos[node] = (0, i * vertical_spacing)  # Place blue nodes in a vertical line

    # Apply positions and add nodes to the PyVis network
    for node, (x, y) in pos.items():
        net.add_node(node, x=x, y=y, color=G.nodes[node]['color'], label=node, fixed={"x": True, "y": True})

    # Add remaining nodes (directors) and edges
    for node, data in G.nodes(data=True):
        if node not in pos:  # Add nodes not already positioned
            # Position directors to the side of the vertical line
            x = horizontal_offset if data['color'] == director_color else 0
            y = pos.get(node, (0, 0))[1]  # Keep y-coordinate consistent if already defined
            net.add_node(node, x=x, y=y, color=data['color'], label=data['label'])
    for source, target, data in G.edges(data=True):
        net.add_edge(source, target, label=data['label'])

    # Generate and save the graph
    net.show("temp_html/custom_graph.html")
    return net