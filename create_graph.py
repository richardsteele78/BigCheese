import networkx as nx
from pyvis.network import Network

def create_CHgraph(my_df):
    image_path = r"assets/cheese.png"
    G = nx.DiGraph()  # Use a directed graph to represent roles as edges

    # Add nodes and edges based on the DataFrame
    for idx, row in my_df.iterrows():
        # Add Entity1 and Entity2 as nodes
        G.add_node(row['Entity1'], color='blue' if row['Role'] == 'pwsc' else 'orange', label=row['Entity1'])
        G.add_node(row['Entity2'], color='blue' if row['Role'] == 'pwsc' else 'orange', label=row['Entity2'])
        # Add an edge between Entity1 and Entity2 with the role as the label
        G.add_edge(row['Entity1'], row['Entity2'], label=row['Role'])

    # Create a PyVis network visualization
    net = Network(notebook=True, cdn_resources='remote')

    # Define positions for blue nodes in a strict vertical line
    pos = {}
    blue_nodes = [node for node, data in G.nodes(data=True) if data['color'] == 'blue']
    orange_nodes = [node for node, data in G.nodes(data=True) if data['color'] == 'orange']
    for i, node in enumerate(reversed(blue_nodes)):  # Reverse to place the first entry at the bottom
        pos[node] = (0, i * 100)  # Place blue nodes in a straight vertical line with spacing

    # Apply positions and add nodes to the PyVis network
    for node, (x, y) in pos.items():
        if node == blue_nodes[-1]:  # Use the image for the last blue node
            net.add_node(node, x=x, y=y, shape="image", image=image_path, label=node)
        else:
            net.add_node(node, x=x, y=y, color=G.nodes[node]['color'], label=node)
    
    # Add remaining nodes and edges
    for node, data in G.nodes(data=True):
        if node not in pos:  # Add nodes not already positioned
            net.add_node(node, color=data['color'], label=data['label'])
    for source, target, data in G.edges(data=True):
        net.add_edge(source, target, label=data['label'])
    # Generate and save the graph
    net.show(f'temp_html/test_graph.html')        
    return net