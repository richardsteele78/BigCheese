import networkx as nx
from pyvis.network import Network
import base64

# Convert the image to a Base64 string
with open("assets/cheese.png", "rb") as img_file:
    cheese_icon_base64 = base64.b64encode(img_file.read()).decode()
# Use the Base64 string as the image source
cheese_icon_path = f"data:image/png;base64,{cheese_icon_base64}"

def create_custom_graph(df):
    # Define colors
    director_color = "rgb(247,122,64)"  # Orange for directors
    non_director_color = "rgb(51,96,101)"  # Teal for companies
    vertical_spacing = 100  # Spacing between teal nodes in the vertical line
    horizontal_offset = 200  # Horizontal offset for orange nodes
#    cheese_icon_path = "assets/cheese.png"  # Path to the cheese icon

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges based on the DataFrame
    for idx, row in df.iterrows():
        # Determine the color of Entity1 and Entity2 based on their roles
        entity1_color = director_color if row['Role'] == 'Director' else non_director_color
        entity2_color = non_director_color  # Entity2 is always a company (teal)

        # Add Entity1 as a node if it doesn't already exist
        if row['Entity1'] not in G.nodes:
            G.add_node(row['Entity1'], color=entity1_color, label=row['Entity1'])
        # Add Entity2 as a node if it doesn't already exist
        if row['Entity2'] not in G.nodes:
            G.add_node(row['Entity2'], color=entity2_color, label=row['Entity2'])

        # Add an edge between Entity1 and Entity2 with the role as the label
        G.add_edge(row['Entity1'], row['Entity2'], label=row['Role'])

    # Identify the last Entity2 in the DataFrame
    last_entity2 = df.iloc[-1]['Entity2']

    # Create a PyVis network visualization
    net = Network(notebook=True, cdn_resources='remote')

    # Define positions for teal nodes (companies) in a strict vertical line
    pos = {}
    teal_nodes = [node for node, data in G.nodes(data=True) if data['color'] == non_director_color]
    for i, node in enumerate(reversed(teal_nodes)):  # Reverse to start from the bottom
        pos[node] = (0, i * vertical_spacing)  # Place teal nodes in a vertical line

    # Apply positions and add nodes to the PyVis network
    for node, (x, y) in pos.items():
        net.add_node(node, x=x, y=y, color=G.nodes[node]['color'], label=node, fixed={"x": True, "y": True})

    # Add remaining nodes (directors) and edges
    for node, data in G.nodes(data=True):
        if node not in pos:  # Add nodes not already positioned
            # Position directors to the side of the vertical line
            x = horizontal_offset if data['color'] == director_color else 0
            y = pos.get(node, (0, 0))[1]  # Keep y-coordinate consistent if already defined

            # Check if the node is a director of the last Entity2
            if data['color'] == director_color and any(
                (row['Entity1'] == node and row['Entity2'] == last_entity2) for _, row in df.iterrows()
            ):
                # Use the cheese icon for directors of the last Entity2
                net.add_node(node, x=x, y=y, shape="image", image=cheese_icon_path, label=data['label'],size=15)
            else:
                net.add_node(node, x=x, y=y, color=data['color'], label=data['label'])
    # Add edges
    for source, target, data in G.edges(data=True):
        net.add_edge(source, target, label=data['label'])
    return net