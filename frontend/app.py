import streamlit as st
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")

# Connexion MongoDB
client = MongoClient(MONGO_URI)
db = client["twitchtracker"]
collection = db["viewership_fr"]

# Config Streamlit
st.set_page_config(page_title="📊 Twitch FR Viewership", layout="wide")
st.title("🇫🇷 Classement des Streamers Francophones (Pagination par 50)")

# Chargement des données
data = list(collection.find({}, {"_id": 0}))
df = pd.DataFrame(data)

# Nettoyage
def clean_number(col):
    return (
        df[col]
        .astype(str)
        .str.replace(",", "")
        .str.replace("K", "*1e3")
        .str.replace("M", "*1e6")
        .apply(lambda x: eval(x) if x.replace('.', '', 1).replace('-', '', 1).isdigit() or 'e' in x else None)
    )

for col in ["avg_viewers", "total_followers", "hours_streamed", "followers_gain"]:
    df[col] = clean_number(col)

df["rank"] = df["rank"].astype(int)
df = df.sort_values(by="rank")

# Pagination réelle par 50
per_page = 50
total_pages = (len(df) - 1) // per_page + 1

st.sidebar.header("📄 Pagination")
page = st.sidebar.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

start_idx = (page - 1) * per_page
end_idx = start_idx + per_page
paginated_df = df.iloc[start_idx:end_idx]

# Affichage
st.markdown(f"### Page {page}/{total_pages} — Résultats {start_idx+1} à {min(end_idx, len(df))}")

for _, row in paginated_df.iterrows():
    st.markdown(f"""
    <div style="display:flex;align-items:center;margin-bottom:1.5rem;padding:1rem;border:1px solid #eee;border-radius:10px;box-shadow:0 2px 4px rgba(0,0,0,0.05);">
        <img src="{row['avatar_url']}" width="60" height="60" style="border-radius:50%;margin-right:1rem;">
        <div>
            <b>#{row['rank']} <a href="{row['profile_url']}" target="_blank">{row['name']}</a></b><br>
            👁️ <b>{int(row['avg_viewers']):,}</b> viewers moyens • 🕒 <b>{row['hours_streamed']}</b> h streamées<br>
            👥 <b>{int(row['total_followers']):,}</b> followers • 📈 Gain : <b>{int(row['followers_gain']):,}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
