import streamlit as st
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv
import os
import plotly.express as px

# Chargement des variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")

# Connexion MongoDB
client = MongoClient(MONGO_URI)
db = client["twitchtracker"]
collection = db["viewership_fr"]
profiles_collection = db["profiles"]

# Configuration Streamlit
st.set_page_config(
    page_title="🎮 Twitch FR Analytics",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 2px 10px rgba(139, 92, 246, 0.3);
    }
    .streamer-card {
        background: #E5E7EB;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #6B7280;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .top-streamer {
        background: linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%);
        color: white;
        border: 2px solid #8B5CF6;
    }
    .profile-card {
        background: linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎮 TWITCH FRANCE ANALYTICS</h1>
    <p style="font-size: 1.2rem;">📊 Classement des Streamers Francophones</p>
</div>
""", unsafe_allow_html=True)

# Onglets
tab1, tab2 = st.tabs(["📊 Classement & Stats", "👤 Profils Détaillés"])


# ---------- TAB 1 ----------
with tab1:

    def safe_eval(x):
        try:
            return float(eval(x))
        except:
            return None

    @st.cache_data
    def load_data():
        data = list(collection.find({}, {"_id": 0}))
        df = pd.DataFrame(data)

        for col in ["avg_viewers", "total_followers", "hours_streamed", "followers_gain"]:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "")
                .str.replace("K", "*1e3")
                .str.replace("M", "*1e6")
                .apply(safe_eval)
            )

        df["rank"] = df["rank"].astype(int)
        df = df.sort_values(by="rank")
        return df

    df = load_data()

    with st.sidebar:
        st.subheader("🎯 Navigation")
        st.metric("Total Streamers", len(df))
        st.metric("Top Viewers", f"{int(df['avg_viewers'].max()):,}")
        st.metric("Total Followers", f"{int(df['total_followers'].sum()/1e6):.1f}M")
        st.metric("Heures Streamées", f"{int(df['hours_streamed'].sum()):,}h")
        st.markdown("---")

        # Pagination
        per_page = st.selectbox("Résultats par page", [10, 25, 50, 100], index=2)
        total_pages = (len(df) - 1) // per_page + 1
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
        st.markdown("---")

        # Filtres
        st.subheader("🔍 Filtres")
        min_viewers = st.slider("Viewers minimum", 0, int(df['avg_viewers'].max()), 0)
        min_followers = st.slider("Followers minimum (K)", 0, int(df['total_followers'].max()/1000), 0)

    # Filtres & pagination
    filtered_df = df[
        (df["avg_viewers"] >= min_viewers) &
        (df["total_followers"] >= min_followers * 1000)
    ]

    start = (page - 1) * per_page
    end = start + per_page
    paginated_df = filtered_df.iloc[start:end]

    # Graphiques
    col1, col2 = st.columns(2)
    top10 = df.head(10)

    with col1:
        fig = px.bar(
            top10,
            x="avg_viewers", y="name",
            orientation="h", color="avg_viewers",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            top10,
            x="total_followers", y="name",
            orientation="h", color="total_followers",
            color_continuous_scale="Plasma"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Affichage des cartes
    st.markdown(f"### 🎯 Page {page}/{total_pages} — {len(filtered_df)} streamers filtrés")

    for _, row in paginated_df.iterrows():
        card_class = "streamer-card top-streamer" if row["rank"] <= 3 else "streamer-card"
        rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(row["rank"], "🎮")

        st.markdown(f"""
        <div class="{card_class}">
            <h3>{rank_emoji} #{row['rank']} <a href="{row['profile_url']}" target="_blank">{row['name']}</a></h3>
            <ul>
                <li>👁️ Viewers moyens : {int(row['avg_viewers']):,}</li>
                <li>👥 Followers : {int(row['total_followers']):,}</li>
                <li>🕒 Heures streamées : {int(row['hours_streamed']):,}</li>
                <li>📈 Gain followers : {int(row['followers_gain']):,}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ---------- TAB 2 ----------
with tab2:
    st.markdown("### 👤 Profils Détaillés")

    @st.cache_data
    def load_profiles():
        data = list(profiles_collection.find({}, {"_id": 0}))
        return pd.DataFrame(data)

    profiles_df = load_profiles()

    if not profiles_df.empty:
        st.success(f"{len(profiles_df)} profils détaillés disponibles")
        selected = st.selectbox("🎯 Choisir un streamer", sorted(profiles_df['name'].tolist()))

        if selected:
            profile = profiles_df[profiles_df['name'] == selected].iloc[0]
            st.markdown(f"""
                <div class="profile-card">
                    <h2>🎮 {profile.get('name')}</h2>
                    <p><strong>🔗 Profil:</strong> <a href="{profile.get('profile_url')}" target="_blank">Voir sur TwitchTracker</a></p>
                    <p><strong>🏆 Rang:</strong> #{profile.get('rank', 'N/A')}</p>
                    <p><strong>📅 Scrapé le:</strong> {profile.get('scraped_at', '')[:10]}</p>
                </div>
            """, unsafe_allow_html=True)

            # Bio
            st.subheader("📝 Biographie")
            st.markdown(f"*{profile.get('bio', 'Aucune biographie disponible')}*")

            # Stats
            st.subheader("📊 Statistiques")
            for key, val in profile.get("additional_stats", {}).items():
                st.metric(key.replace("_", " ").title(), val)

            # Infos channel
            st.subheader("📺 Infos du Channel")
            for key, val in profile.get("channel_info", {}).items():
                st.write(f"**{key.replace('_', ' ').title()}:** {val}")

            # Top jeux
            st.subheader("🎮 Top Jeux")
            for i, game in enumerate(profile.get("top_games", []), 1):
                st.markdown(f"**{i}.** {game.get('game')} – {game.get('hours')}")

            # Streams récents
            st.subheader("📺 Streams Récents")
            for stream in profile.get("recent_streams", []):
                st.markdown(f"- {stream.get('date')} – {stream.get('game')} ({stream.get('duration')})")
    else:
        st.warning("⚠️ Aucun profil trouvé. Lancez `main_profiles.py` pour les scraper.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 2rem;">
    <p>📊 Données récupérées depuis TwitchTracker · 🧠 Projet Streamlit</p>
</div>
""", unsafe_allow_html=True)
