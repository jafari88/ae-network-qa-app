# AE Network QA App - Streamlit App

A comprehensive Streamlit application for querying and analyzing Adverse Event (AE) network data using natural language questions.

## Features

- **Natural Language Queries**: Ask questions about your network data in plain English
- **Network Analysis**: Explore nodes, edges, centrality measures, and network properties
- **Multi-Snapshot Support**: Analyze multiple network snapshots simultaneously
- **Interactive Interface**: User-friendly interface with real-time results
- **Background Watermark**: Custom background image support
- **Comprehensive Metrics**: Degree, centrality, betweenness, and more

## Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
cd <your-repo-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app locally:
```bash
streamlit run ae_network_qa_app.py
```

## Deployment to Streamlit Community Cloud

### Step 1: Prepare Your Repository

1. Ensure your main Streamlit app file is named `ae_network_qa_app.py`
2. Make sure `requirements.txt` is in the root directory
3. Add your network data files to the repository
4. Commit and push all changes to GitHub

### Step 2: Deploy to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set the main file path to `ae_network_qa_app.py`
6. Click "Deploy!"

### Step 3: Configure App Settings (Optional)

Create a `.streamlit/config.toml` file for custom settings:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

## Project Structure

```
├── ae_network_qa_app.py     # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── .gitignore              # Git ignore file
├── .streamlit/             # Streamlit configuration
│   └── config.toml
├── app_net.png             # Background image (optional)
└── network_snapshots/      # Network data files
    ├── network_changepoint_1_nodes.json
    ├── network_changepoint_1_edges.json
    └── ...
```

## Usage

1. **Load Network Data**: Point the app to your network snapshot directory
2. **Select Snapshots**: Choose which network snapshots to analyze
3. **Ask Questions**: Use natural language to query your networks
4. **View Results**: Get instant answers with detailed data tables

## Example Queries

- `node DIARRHOEA features` - Get all features for a specific node
- `node DIARRHOEA degree` - Get degree for a specific node
- `node DIARRHOEA degree_centrality` - Get degree centrality for a node
- `node DIARRHOEA betweenness_centrality` - Get betweenness centrality
- `compare degree` - Compare all nodes by degree
- `compare degree_centrality` - Compare all nodes by degree centrality
- `compare betweenness_centrality` - Compare all nodes by betweenness centrality
- `top 10 weight` - Show top 10 highest weight edges
- `top 5 degree` - Show top 5 nodes by degree
- `top 5 centrality` - Show top 5 nodes by degree centrality
- `neighbors of DIARRHOEA` - Show neighbors of a specific node
- `neighbors of DIARRHOEA top 20 weight` - Show top 20 weight neighbors
- `list nodes` - List all nodes in the network
- `list edges` - List all edges in the network
- `summary` - Get network summary statistics
- `debug nodes` - Debug network information

## Data Format

Your network data should be in JSON format:

**Nodes file** (`network_changepoint_X_nodes.json`):
```json
[
  {
    "AE": "DIARRHOEA",
    "degree": 5,
    "degree_centrality": 0.1,
    "betweenness_centrality": 0.05
  }
]
```

**Edges file** (`network_changepoint_X_edges.json`):
```json
[
  {
    "AE1": "DIARRHOEA",
    "AE2": "NAUSEA",
    "weight": 10.5
  }
]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License. 