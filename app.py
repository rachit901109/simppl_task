import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import networkx as nx
from pyvis.network import Network
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_profile_data():
    return pd.read_csv(r'process_data\insta\profile_data.csv')

profile_data = load_profile_data()

@st.cache_data
def load_raw_data():
    with open(r"raw_data\insta\politician_profile.json", 'r', encoding="utf-8") as f:
        return json.load(f)

network_data = load_raw_data()

@st.cache_data
def load_hashtag_data(hashtag):
    return pd.read_csv(rf"process_data\insta\{hashtag}.csv")

# Group mappings
group_mappings = {
    "bjp4india":1, "bjp4mp":1, "bjp4up":1, "bjp4delhi":1, "bjp4telangana":1,
    "incindia":2, "shivsena":3, "shivsenaofc":3, "aamaadmiparty":4,
    "bsp4india_":5, "narendramodi":1, "amitshahofficial":1, "arvindkejriwal":4,
    "rahulgandhi":2, "mamataofficial":6, "gadkari.nitin":1, "pawarspeaks":6,
    "asadowaisiofficial":6, "mkstalin":6, "zeenews":7, "aajtak":7, "ndtv":7,
    "abpnewstv":7
}

# Color mappings 
color_mappings = {
    1: "#FF9933",  # Orange for BJP
    2: "#0000FF",  # Blue for INC
    3: "#F1C40F",  # Yellow for Shiv Sena
    4: "#27AE60",  # Green for AAP
    5: "#3498DB",  # Light Blue for BSP
    6: "#8E44AD",  # Purple for Others
    7: "#E74C3C",  # Red for News Channels
    8: "#95A5A6"   # Gray for unassigned related profiles
}

hash_counts = {
    "abkibaar400paar": 425955,
    "chunavkaparv": 73077,
    "electioncommission": 101589,
    "indianelection": 7914,
    "loksabhaelection2024": 791188,
    "sharadpawar": 316227
}

st.markdown("""
    <style>
    .card {
        background-color: ##f0f2f6;;
        border: 1px solid #e0e0e0;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 100%;
        box-sizing: border-box;
    }
    .card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 10px 10px 0 0;
        margin-bottom: 10px;
    }
    .card h3 {
        margin: 10px 0;
        font-size: 28px;
        color: #F5761A;
    }
    .card p {
        margin: 5px 0;
        font-size: 14px;
        color: #F8F8FF;
    }
    </style>
""", unsafe_allow_html=True)

# streamlit app
st.sidebar.title("Instagram")
section = st.sidebar.radio("Go to", ["Profiles", "Network Graph", "Hashtags"])

def get_image(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return Image.new('RGB', (200, 200), color = (211, 211, 211))

# Profiles Section
if section == "Profiles":
    st.title("Political Instagram Profiles")
    
    # Create rows of 3 cards each
    for i in range(0, len(profile_data), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(profile_data):
                profile = profile_data.iloc[i + j]
                with cols[j]:
                    img = get_image(profile['profilePicUrl'])
                    st.image(img, use_column_width=True)
                    st.markdown(f"""
                        <div class="card">
                            <h3>{profile['username']}</h3>
                            <p><strong>Followers:</strong> {profile['followersCount']:,}</p>
                            <p><strong>Following:</strong> {profile['followsCount']:,}</p>
                            <p><strong>Posts:</strong> {profile['postsCount']:,}</p>
                            <p><strong>IGTV Videos:</strong> {profile['igtvVideoCount']}</p>
                            <p><strong>Verified:</strong> {"✅" if profile['verified'] else "❌"}</p>
                            <p><strong>Business Account:</strong> {"✅" if profile['isBusinessAccount'] else "❌"}</p>
                        </div>
                    """, unsafe_allow_html=True)


# Hashtags Section
if section == "Hashtags":
    st.title("Hashtag Analysis")

    hashtags = ["abkibaar400paar", "chunavkaparv", "electioncommission", "indianelection", "loksabhaelection2024", "sharadpawar"]
    selected_hashtag = st.selectbox("Select a hashtag", hashtags)
    st.title("#"+selected_hashtag+" -Total post: "+str(hash_counts[selected_hashtag]))

    df = load_hashtag_data(selected_hashtag)
    # type of post: image, video or sidecar
    st.subheader(f"Distribution of Post Types for {selected_hashtag}")
    fig, ax = plt.subplots()
    df['type'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')  # Remove y-label
    st.pyplot(fig)

    df['upload_date'] = pd.to_datetime(df['upload_date'])

    # scatter plot of likes and comments over time
    st.subheader(f"Likes and Comments Over Time for {selected_hashtag}")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.scatterplot(x='upload_date', y='likes_count', data=df, label='Likes', ax=ax)
    sns.scatterplot(x='upload_date', y='comments_count', data=df, label='Comments', ax=ax)
    ax.set_xlabel('Upload Date')
    ax.set_ylabel('Count')
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Summary statistics
    st.subheader("Summary Statistics")
    st.write(f"Average likes per post: {df['likes_count'].mean():.2f}")
    st.write(f"Average comments per post: {df['comments_count'].mean():.2f}")
    st.write(f"Most common post type: {df['type'].mode().values[0]}")

    # Top 10 most liked posts
    st.subheader("Top 10 Most Liked Posts")
    top_liked = df.nlargest(10, 'likes_count')[['type', 'likes_count', 'comments_count', 'upload_date']]
    st.dataframe(top_liked)


# Network Graph Section
if section == "Network Graph":
    st.title("Network Graph of related profiles")
    G = nx.Graph()
    connection_counts = defaultdict(int)

    # Add nodes and edges
    for profile in network_data:
        group = group_mappings.get(profile['username'], 8) 
        G.add_node(profile['username'], title=profile['username'], group=group)
        connection_counts[profile['username']] = len(profile['relatedProfiles'])
        for related in profile['relatedProfiles']:
            related_group = group_mappings.get(related['username'], 8)
            G.add_node(related['username'], title=related['username'], group=related_group)
            G.add_edge(profile['username'], related['username'])

    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")

    for node in G.nodes():
        group = G.nodes[node]['group']
        color = color_mappings[group]
        net.add_node(node, label=node, title=node, color=color)

    for edge in G.edges():
        net.add_edge(edge[0], edge[1])

    net.save_graph("network_graph.html")

    # Display the graph in Streamlit
    st.components.v1.html(open("network_graph.html", 'r').read(), height=700)

    # Legend
    st.markdown("""
    <style>
    .graph-container {
        border: 2px solid #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="graph-container">
        <h3>Graph Legend</h3>
        <p><span style="color: #FF9933;">●</span> BJP</p>
        <p><span style="color: #0000FF;">●</span> INC</p>
        <p><span style="color: #F1C40F;">●</span> Shiv Sena</p>
        <p><span style="color: #27AE60;">●</span> AAP</p>
        <p><span style="color: #3498DB;">●</span> BSP</p>
        <p><span style="color: #8E44AD;">●</span> Other Political</p>
        <p><span style="color: #E74C3C;">●</span> News Channels</p>
        <p><span style="color: #95A5A6;">●</span> Unassigned Related Profiles</p>
    </div>
    """, unsafe_allow_html=True)

    # Network Statistics
    st.subheader("Network Statistics")
    st.write(f"Total number of profiles: {G.number_of_nodes()}")
    st.write(f"Number of connections: {G.number_of_edges()}")

    selected_profile = st.selectbox("Highlight a profile", ["None"] + list(group_mappings))
    if selected_profile != "None":
        highlighted_net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
        for node in G.nodes():
            group = G.nodes[node]['group']
            if node == selected_profile:
                color = "#000000"
            else:
                color = color_mappings[group]
            highlighted_net.add_node(node, label=node, title=node, color=color)
        
        for edge in G.edges():
            highlighted_net.add_edge(edge[0], edge[1])
        
        highlighted_net.save_graph("highlighted_network_graph.html")
        st.components.v1.html(open("highlighted_network_graph.html", 'r').read(), height=700)