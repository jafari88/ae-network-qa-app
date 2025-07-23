import streamlit as st
import networkx as nx
import pandas as pd
import json
import os
import re
import base64
import streamlit as st
import base64
import streamlit as st

import base64
import streamlit as st

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

background_image_path = "app_net.png"

try:
    background_image = get_base64_image(background_image_path)
    background_css = f"""
    <style>
        .stApp {{
            position: relative;
        }}
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            background: url('data:image/png;base64,{background_image}') no-repeat center center;
            background-size: contain;
            opacity: 0.18;  /* Adjust for more/less watermark effect */
            pointer-events: none;
        }}
        .stApp > * {{
            position: relative;
            z-index: 1;
        }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Could not load background image: {e}")



def process_single_query(question, G, nodes, edges):
    answer = None
    answer_df = None

    # Node features or metric queries (robust split)
    node_metric_match = re.match(
        r'node\s+(.+?)\s+(degree|degree_centrality|betweenness_centrality|features?)', question, re.IGNORECASE
    )
    if node_metric_match:
        node_name = node_metric_match.group(1).strip()
        metric_match = node_metric_match.group(2).strip().lower()
        # Find exact match (case-insensitive)
        exact_node = None
        for node in G.nodes():
            if node.lower() == node_name.lower():
                exact_node = node
                break
        if exact_node and exact_node in G:
            # Find node features from nodes list
            node_features = None
            for n in nodes:
                if n['AE'].lower() == exact_node.lower():
                    node_features = n
                    break
            if metric_match in ["features", "feature"]:
                if node_features:
                    answer = f"**All features for {exact_node}:**"
                    answer_df = pd.DataFrame([node_features]).T.reset_index()
                    answer_df.columns = ['Feature', 'Value']
                else:
                    answer = f"No features found for node '{exact_node}'."
            elif metric_match == "degree":
                value = G.degree(exact_node)
                answer = f"**Degree for {exact_node}:**\n\n**Value:** {value:.6f}"
                answer_df = pd.DataFrame({
                    'Node': [exact_node],
                    'Metric': ["Degree"],
                    'Value': [f"{value:.6f}"]
                })
            elif metric_match == "degree_centrality":
                value = nx.degree_centrality(G)[exact_node]
                answer = f"**Degree Centrality for {exact_node}:**\n\n**Value:** {value:.6f}"
                answer_df = pd.DataFrame({
                    'Node': [exact_node],
                    'Metric': ["Degree Centrality"],
                    'Value': [f"{value:.6f}"]
                })
            elif metric_match == "betweenness_centrality":
                value = nx.betweenness_centrality(G, weight='weight')[exact_node]
                answer = f"**Betweenness Centrality for {exact_node}:**\n\n**Value:** {value:.6f}"
                answer_df = pd.DataFrame({
                    'Node': [exact_node],
                    'Metric': ["Betweenness Centrality"],
                    'Value': [f"{value:.6f}"]
                })
        else:
            answer = f"Node '{node_name}' not found in network."
        return answer, answer_df

    # Compare nodes by metric
    if "compare" in question and any(metric in question for metric in ["degree", "centrality", "betweenness"]):
        metric_match = None
        if "degree" in question and "centrality" not in question:
            metric_match = "degree"
        elif "degree_centrality" in question or "degree centrality" in question:
            metric_match = "degree_centrality"
        elif "betweenness_centrality" in question or "betweenness centrality" in question:
            metric_match = "betweenness_centrality"
        if metric_match:
            if metric_match == "degree":
                node_metrics = dict(G.degree())
                metric_name = "Degree"
            elif metric_match == "degree_centrality":
                node_metrics = nx.degree_centrality(G)
                metric_name = "Degree Centrality"
            elif metric_match == "betweenness_centrality":
                node_metrics = nx.betweenness_centrality(G, weight='weight')
                metric_name = "Betweenness Centrality"
            sorted_nodes = sorted(node_metrics.items(), key=lambda x: x[1], reverse=True)
            answer = f"**All nodes ranked by {metric_name}:**"
            metric_data = []
            for i, (node, value) in enumerate(sorted_nodes):
                metric_data.append({
                    'Rank': i + 1,
                    'Node': node,
                    metric_name: f"{value:.6f}"
                })
            answer_df = pd.DataFrame(metric_data)
        return answer, answer_df

    # Neighbors with top weights
    if "neighbors" in question and "top" in question and "weight" in question and "of" in question:
        node_match = re.search(r'neighbors of (.+?)(?:\s+top)', question, re.IGNORECASE)
        weight_match = re.search(r'top (\d+) weight', question, re.IGNORECASE)
        if node_match and weight_match:
            node_name = node_match.group(1).strip()
            top_n = int(weight_match.group(1))
            exact_node = None
            for node in G.nodes():
                if node.lower() == node_name.lower():
                    exact_node = node
                    break
            if exact_node and exact_node in G:
                edges_with_node = []
                for u, v, data in G.edges(data=True):
                    if u == exact_node or v == exact_node:
                        weight = data.get('weight', 0)
                        other_node = v if u == exact_node else u
                        edges_with_node.append((exact_node, other_node, weight))
                edges_with_node.sort(key=lambda x: x[2], reverse=True)
                top_edges = edges_with_node[:top_n]
                answer = f"**Top {len(top_edges)} highest weight edges containing {exact_node}:**"
                if top_edges:
                    edge_data = []
                    for i, (ae1, ae2, weight) in enumerate(top_edges):
                        edge_data.append({
                            'Rank': i + 1,
                            'AE1': ae1,
                            'AE2': ae2,
                            'Weight': weight
                        })
                    answer_df = pd.DataFrame(edge_data)
                else:
                    answer += f"No edges found containing {exact_node}"
            else:
                answer = f"Node '{node_name}' not found in network."
        else:
            answer = "Please specify both node name and number (e.g., 'neighbors of DIARRHOEA top 20 weight')"
        return answer, answer_df

    # Regular neighbors query
    if "neighbors" in question and "of" in question:
        node_match = re.search(r'neighbors of (.+?)(?:\s+top|\s*$)', question, re.IGNORECASE)
        if node_match:
            node_name = node_match.group(1).strip()
            exact_node = None
            for node in G.nodes():
                if node.lower() == node_name.lower():
                    exact_node = node
                    break
            if exact_node and exact_node in G:
                neighbors = list(G.neighbors(exact_node))
                total_neighbors = len(neighbors)
                display_neighbors = neighbors[:20]
                answer = f"""
                **Neighbors of {exact_node}:**
                **Top 20 neighbors (out of {total_neighbors} total):**
                {', '.join(display_neighbors)}
                **Total neighbors:** {total_neighbors}
                """
                if neighbors:
                    neighbor_data = []
                    for i, neighbor in enumerate(display_neighbors):
                        neighbor_data.append({
                            'Rank': i + 1,
                            'Neighbor': neighbor
                        })
                    answer_df = pd.DataFrame(neighbor_data)
            else:
                answer = f"Node '{node_name}' not found in network."
        return answer, answer_df

    # Debug nodes
    if "debug nodes" in question:
        answer = f"""
        **Network Debug Info:**
        - **Total nodes:** {len(G.nodes())}
        - **Total edges:** {len(G.edges())}
        - **Sample nodes:** {list(G.nodes())[:10]}
        """
        return answer, answer_df

    # Top weight edges (only if NOT a neighbors query)
    if "top" in question and "weight" in question and "neighbors" not in question:
        weight_match = re.search(r'top (\d+) weight', question, re.IGNORECASE)
        if weight_match:
            n = int(weight_match.group(1))
            edge_weights = [(u, v, G[u][v].get('weight', 0)) for u, v in G.edges()]
            edge_weights.sort(key=lambda x: x[2], reverse=True)
            top_edges = edge_weights[:n]
            answer = f"**Top {n} highest weight edges:**"
            edge_data = []
            for i, (u, v, w) in enumerate(top_edges):
                edge_data.append({
                    'Rank': i + 1,
                    'AE1': u,
                    'AE2': v,
                    'Weight': w
                })
            answer_df = pd.DataFrame(edge_data)
        return answer, answer_df

    # Top degree centrality
    if "top" in question and "centrality" in question:
        centrality_match = re.search(r'top (\d+) centrality', question, re.IGNORECASE)
        if centrality_match:
            n = int(centrality_match.group(1))
            centrality = nx.degree_centrality(G)
            top_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:n]
            answer = f"**Top {n} nodes by degree centrality:**"
            centrality_data = []
            for i, (node, cent) in enumerate(top_centrality):
                centrality_data.append({
                    'Rank': i + 1,
                    'AE': node,
                    'Degree Centrality': f"{cent:.6f}"
                })
            answer_df = pd.DataFrame(centrality_data)
        return answer, answer_df

    # Top degree
    if "top" in question and "degree" in question:
        degree_match = re.search(r'top (\d+) degree', question, re.IGNORECASE)
        if degree_match:
            n = int(degree_match.group(1))
            degrees = dict(G.degree())
            top_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:n]
            answer = f"**Top {n} nodes by degree:**"
            degree_data = []
            for i, (node, deg) in enumerate(top_degrees):
                degree_data.append({
                    'Rank': i + 1,
                    'AE': node,
                    'Degree': deg
                })
            answer_df = pd.DataFrame(degree_data)
        return answer, answer_df

    # List nodes
    if "list nodes" in question:
        all_nodes = list(G.nodes())
        answer = f"**All nodes ({len(all_nodes)} total):**"
        answer_df = pd.DataFrame({'AE': node} for node in all_nodes)
        return answer, answer_df

    # List edges
    if "list edges" in question:
        all_edges = list(G.edges(data=True))
        answer = f"**All edges ({len(all_edges)} total):**"
        edge_data = []
        for u, v, data in all_edges:
            edge_data.append({
                'AE1': u,
                'AE2': v,
                'Weight': data.get('weight', 0)
            })
        answer_df = pd.DataFrame(edge_data)
        return answer, answer_df

    # Network summary
    if "summary" in question:
        answer = f"""
        **Network Summary:**
        - **Nodes:** {len(G.nodes())}
        - **Edges:** {len(G.edges())}
        - **Connected components:** {nx.number_connected_components(G)}
        - **Average degree:** {sum(dict(G.degree()).values()) / len(G.nodes()):.2f}
        """
        return answer, answer_df

    return answer, answer_df

# --- MAIN APP ---
st.title("Adverse Event Network Browser")

st.sidebar.title("🔍 Network Analysis App")

# Add file upload feature
st.sidebar.subheader("📁 Upload Network Files")
uploaded_files = st.sidebar.file_uploader(
    "Upload your network JSON files:",
    type=['json'],
    accept_multiple_files=True,
    help="Upload multiple JSON files (nodes and edges files)"
)

# Process uploaded files
uploaded_networks = {}
uploaded_nodes_data = {}
uploaded_edges_data = {}

if uploaded_files:
    st.sidebar.success(f"✅ Uploaded {len(uploaded_files)} files")
    
    # Group files by snapshot number
    node_files = [f for f in uploaded_files if f.name.endswith('_nodes.json')]
    edge_files = [f for f in uploaded_files if f.name.endswith('_edges.json')]
    
    for node_file in node_files:
        try:
            # Extract snapshot number from filename
            snapshot_num = int(node_file.name.split('_')[2])
            
            # Find corresponding edge file
            edge_file = None
            for ef in edge_files:
                if ef.name == f"network_changepoint_{snapshot_num}_edges.json":
                    edge_file = ef
                    break
            
            if edge_file:
                # Load data
                nodes_data = json.load(node_file)
                edges_data = json.load(edge_file)
                
                # Create network
                G = nx.Graph()
                for node in nodes_data:
                    G.add_node(node['AE'], **{k: v for k, v in node.items() if k != 'AE'})
                for edge in edges_data:
                    G.add_edge(edge['AE1'], edge['AE2'], **{k: v for k, v in edge.items() if k not in ['AE1', 'AE2']})
                
                uploaded_networks[snapshot_num] = G
                uploaded_nodes_data[snapshot_num] = nodes_data
                uploaded_edges_data[snapshot_num] = edges_data
                
        except Exception as e:
            st.sidebar.error(f"Error processing {node_file.name}: {e}")


st.sidebar.header("Network Files")
# --- Directory input in sidebar ---
st.sidebar.header("Network Files")

default_network_dir = r"\network_snapshots"
network_dir = st.sidebar.text_input(
    "Enter directory containing node/edge JSON files:",
    value=default_network_dir,
    help="Browse to the folder where your network_changepoint_X_nodes.json and network_changepoint_X_edges.json files are located."
)

# Determine which data source to use (uploaded files take priority)
if uploaded_networks:
    # Use uploaded files
    all_networks = uploaded_networks
    all_nodes_data = uploaded_nodes_data
    all_edges_data = uploaded_edges_data
    st.sidebar.success(f"✅ Using {len(uploaded_networks)} uploaded snapshots")
    
    # Show snapshot selection for uploaded files
    uploaded_snapshots = sorted(uploaded_networks.keys())
    selected_snapshots = st.sidebar.multiselect(
        "Select snapshots to analyze:",
        uploaded_snapshots,
        default=uploaded_snapshots,
        help="Choose which uploaded snapshots to analyze"
    )
    
    # Filter to selected snapshots
    all_networks = {k: v for k, v in all_networks.items() if k in selected_snapshots}
    all_nodes_data = {k: v for k, v in all_nodes_data.items() if k in selected_snapshots}
    all_edges_data = {k: v for k, v in all_edges_data.items() if k in selected_snapshots}
    
else:
    # Use directory files
    if not os.path.isdir(network_dir):
        st.sidebar.error(f"Directory not found: {network_dir}")
        st.stop()

    if os.path.exists(network_dir):
        files = os.listdir(network_dir)
        node_files = [f for f in files if f.endswith('_nodes.json')]
        edge_files = [f for f in files if f.endswith('_edges.json')]
        snapshot_numbers = []
        for node_file in node_files:
            try:
                snapshot_num = int(node_file.split('_')[2])
                snapshot_numbers.append(snapshot_num)
            except:
                continue
        snapshot_numbers = sorted(snapshot_numbers)
        if snapshot_numbers:
            st.sidebar.subheader("📁 Available Snapshots")
            selected_snapshots = st.sidebar.multiselect(
                "Select snapshots to analyze:",
                snapshot_numbers,
                default=snapshot_numbers,
                help="Choose which snapshots to analyze (select multiple for comparison)"
            )
            all_networks = {}
            all_nodes_data = {}
            all_edges_data = {}
            for snapshot in selected_snapshots:
                node_path = os.path.join(network_dir, f"network_changepoint_{snapshot}_nodes.json")
                edge_path = os.path.join(network_dir, f"network_changepoint_{snapshot}_edges.json")
                if os.path.exists(node_path) and os.path.exists(edge_path):
                    try:
                        with open(node_path, 'r') as f:
                            nodes_data = json.load(f)
                        with open(edge_path, 'r') as f:
                            edges_data = json.load(f)
                        G = nx.Graph()
                        for node in nodes_data:
                            G.add_node(node['AE'], **{k: v for k, v in node.items() if k != 'AE'})
                        for edge in edges_data:
                            G.add_edge(edge['AE1'], edge['AE2'], **{k: v for k, v in edge.items() if k not in ['AE1', 'AE2']})
                        all_networks[snapshot] = G
                        all_nodes_data[snapshot] = nodes_data
                        all_edges_data[snapshot] = edges_data
                    except Exception as e:
                        st.sidebar.error(f"Error loading snapshot {snapshot}: {e}")
        else:
            st.warning("No snapshot files found")
            st.stop()
    else:
        st.info("Please upload files or ensure the network directory exists and contains snapshot files.")
        st.stop()

# Display results if we have networks loaded
if all_networks:
    st.sidebar.success(f"✅ Loaded {len(all_networks)} snapshots")
    st.header("📊 Network Summary (All Snapshots)")
    summary_data = []
    for snapshot, G in all_networks.items():
        summary_data.append({
            'Snapshot': snapshot,
            'Nodes': G.number_of_nodes(),
            'Edges': G.number_of_edges(),
            'Avg Degree': f"{sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}"
        })
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
    st.header("Ask Questions About Your Networks")
    st.markdown("""
    **Example questions:**
    - `node DIARRHOEA features`
    - `node DIARRHOEA degree`
    - `node DIARRHOEA degree_centrality`
    - `node DIARRHOEA betweenness_centrality`
    - `compare degree`
    - `compare degree_centrality`
    - `compare betweenness_centrality`
    - `top 10 weight`
    - `top 5 degree`
    - `top 5 centrality`
    - `neighbors of DIARRHOEA`
    - `neighbors of DIARRHOEA top 20 weight`
    - `list nodes`
    - `list edges`
    - `summary`
    - `debug nodes`
    """)
    question = st.text_input("Enter your question:", placeholder="e.g., node DIARRHOEA features")
    if question:
        for snapshot, G in all_networks.items():
            st.subheader(f" Snapshot {snapshot} Results")
            answer, answer_df = process_single_query(question, G, all_nodes_data[snapshot], all_edges_data[snapshot])
            if answer:
                st.markdown("**Answer:**")
                st.markdown(answer)
            if answer_df is not None:
                st.dataframe(answer_df, use_container_width=True)
            st.markdown("---")
else:
    st.error("No snapshots could be loaded successfully.")