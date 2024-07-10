import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

@st.cache_data
def load_data():
    return pd.read_csv(r'process_data\insta\profile_data.csv')

data = load_data()

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
section = st.sidebar.radio("Go to", ["Profiles", "Hashtags"])

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
    for i in range(0, len(data), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(data):
                profile = data.iloc[i + j]
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
    st.title("Hashtags (Coming Soon)")
    st.write("Hashtag analysis will be implemented in the next version.")