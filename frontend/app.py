import streamlit as st
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv
import os
import plotly.express as px
import plotly.graph_objects as go

# Chargement des variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")

# Connexion MongoDB
client = MongoClient(MONGO_URI)
db = client["twitchtracker"]
collection = db["viewership_fr"]
profiles_collection = db["streamers_profiles_fr"]

# Config Streamlit avec thème personnalisé
st.set_page_config(
    page_title="🎮 Twitch FR Analytics", 
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design moderne
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
        transition: transform 0.2s ease;
    }
    
    .streamer-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #D1D5DB;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .top-streamer {
        background: linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%);
        border-left-color: #8B5CF6;
        border: 2px solid #8B5CF6;
        color: white;
        font-weight: bold;
    }
    
    .top-streamer h3 {
        color: white !important;
    }
    
    .top-streamer a {
        color: #E0E7FF !important;
    }
    
    .profile-card {
        background: linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        color: #374151;
        font-weight: bold;
    }
    
    .metric-label {
        color: #6B7280;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Header principal avec design moderne
st.markdown("""
<div class="main-header">
    <h1>🎮 TWITCH FRANCE ANALYTICS</h1>
    <p style="font-size: 1.2rem; margin: 0;">📊 Classement des Streamers Francophones</p>
</div>
""", unsafe_allow_html=True)

# Navigation par onglets
tab1, tab2 = st.tabs(["📊 Classement & Stats", "👤 Profils Détaillés"])

with tab1:
    # Chargement des données principales
    @st.cache_data
    def load_data():
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
        return df

    df = load_data()

    # Sidebar avec design amélioré
    with st.sidebar:
        st.markdown('<div class="sidebar-header"><h2>🎯 Navigation</h2></div>', unsafe_allow_html=True)
        
        # Métriques globales
        st.markdown("### 📈 Statistiques Globales")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Streamers", len(df))
            st.metric("Top Viewers", f"{int(df['avg_viewers'].max()):,}")
        
        with col2:
            st.metric("Total Followers", f"{int(df['total_followers'].sum()/1000000):.1f}M")
            st.metric("Heures Streamées", f"{int(df['hours_streamed'].sum()):,}h")
        
        st.markdown("---")
        
        # Pagination
        st.markdown("### 📄 Pagination")
        per_page = st.selectbox("Résultats par page", [10, 25, 50, 100], index=2)
        total_pages = (len(df) - 1) // per_page + 1
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
        
        st.markdown("---")
        
        # Filtres
        st.markdown("### 🔍 Filtres")
        min_viewers = st.slider("Viewers minimum", 0, int(df['avg_viewers'].max()), 0)
        min_followers = st.slider("Followers minimum (K)", 0, int(df['total_followers'].max()/1000), 0)

    # Application des filtres
    filtered_df = df[
        (df['avg_viewers'] >= min_viewers) & 
        (df['total_followers'] >= min_followers * 1000)
    ]

    # Pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_df = filtered_df.iloc[start_idx:end_idx]

    # Graphiques analytiques
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Top 10 - Viewers Moyens")
        top_10 = df.head(10)
        fig = px.bar(
            top_10, 
            x='avg_viewers', 
            y='name',
            orientation='h',
            color='avg_viewers',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 👥 Top 10 - Followers")
        fig2 = px.bar(
            top_10, 
            x='total_followers', 
            y='name',
            orientation='h',
            color='total_followers',
            color_continuous_scale='Plasma'
        )
        fig2.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Affichage des résultats avec design amélioré
    st.markdown(f"### 🎯 Page {page}/{total_pages} — Résultats {start_idx+1} à {min(end_idx, len(filtered_df))} sur {len(filtered_df)} streamers")

    for idx, (_, row) in enumerate(paginated_df.iterrows()):
        # Style spécial pour le top 3
        card_class = "streamer-card top-streamer" if row['rank'] <= 3 else "streamer-card"
        rank_emoji = "🥇" if row['rank'] == 1 else "🥈" if row['rank'] == 2 else "🥉" if row['rank'] == 3 else "🎮"
        
        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <img src="{row['avatar_url']}" width="80" height="80" style="border-radius: 50%; border: 2px solid #5E81AC;">
                <div style="flex: 1;">
                    <h3 style="margin: 0; color: #2E3440;">
                        {rank_emoji} #{row['rank']} 
                        <a href="{row['profile_url']}" target="_blank" style="text-decoration: none; color: #5E81AC;">
                            {row['name']}
                        </a>
                    </h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
                        <div class="metric-container">
                            <div class="metric-value" style="font-size: 1.5rem;">
                                👁️ {int(row['avg_viewers']):,}
                            </div>
                            <div class="metric-label">Viewers moyens</div>
                        </div>
                        <div class="metric-container">
                            <div class="metric-value" style="font-size: 1.5rem;">
                                👥 {int(row['total_followers']):,}
                            </div>
                            <div class="metric-label">Followers</div>
                        </div>
                        <div class="metric-container">
                            <div class="metric-value" style="font-size: 1.5rem;">
                                🕒 {int(row['hours_streamed']):,}h
                            </div>
                            <div class="metric-label">Heures streamées</div>
                        </div>
                        <div class="metric-container">
                            <div class="metric-value" style="font-size: 1.5rem;">
                                📈 {int(row['followers_gain']):,}
                            </div>
                            <div class="metric-label">Gain followers</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 👤 Profils Détaillés des Streamers")
    
    # Chargement des profils détaillés
    @st.cache_data
    def load_profiles():
        profiles_data = list(profiles_collection.find({}, {"_id": 0}))
        return pd.DataFrame(profiles_data)
    
    profiles_df = load_profiles()
    
    if len(profiles_df) > 0:
        st.markdown(f"**📊 {len(profiles_df)} profils détaillés disponibles**")
        
        # Sélecteur de streamer
        streamer_names = sorted(profiles_df['name'].tolist())
        selected_streamer = st.selectbox("🎯 Choisir un streamer", streamer_names)
        
        if selected_streamer:
            profile = profiles_df[profiles_df['name'] == selected_streamer].iloc[0]
            
            # Affichage du profil détaillé
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class="profile-card">
                    <h2>🎮 {profile['name']}</h2>
                    <p><strong>🔗 Profil:</strong> <a href="{profile['profile_url']}" target="_blank" style="color: #FFD700;">Voir sur TwitchTracker</a></p>
                    <p><strong>🏆 Rang:</strong> #{profile.get('rank', 'N/A')}</p>
                    <p><strong>📅 Dernière mise à jour:</strong> {profile['scraped_at'][:10]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Bio
                bio = profile.get('bio')
                if bio:
                    st.markdown("### 📝 Biographie")
                    st.markdown(f"*{bio}*")
                else:
                    st.markdown("### 📝 Biographie")
                    st.markdown("*Aucune biographie disponible*")
            
            with col2:
                # Statistiques additionnelles
                additional_stats = profile.get('additional_stats', {})
                if additional_stats:
                    st.markdown("### 📊 Statistiques")
                    for key, value in additional_stats.items():
                        st.metric(key.replace('_', ' ').title(), value)
                
                # Infos du channel
                channel_info = profile.get('channel_info', {})
                if channel_info:
                    st.markdown("### 📺 Infos Channel")
                    for key, value in channel_info.items():
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            
            # Top jeux et streams récents
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("### 🎮 Top Jeux")
                top_games = profile.get('top_games', [])
                if top_games:
                    for i, game in enumerate(top_games[:5], 1):
                        st.markdown(f"**{i}.** {game.get('game', 'N/A')} - {game.get('hours', 'N/A')}")
                else:
                    st.markdown("*Aucun jeu trouvé*")
            
            with col4:
                st.markdown("### 📺 Streams Récents")
                recent_streams = profile.get('recent_streams', [])
                if recent_streams:
                    for stream in recent_streams[:5]:
                        st.markdown(f"**{stream.get('date', 'N/A')}** - {stream.get('game', 'N/A')} ({stream.get('duration', 'N/A')})")
                else:
                    st.markdown("*Aucun stream récent trouvé*")
    
    else:
        st.warning("⚠️ Aucun profil détaillé trouvé. Lancez d'abord le scraping des profils avec `python main_profiles.py`")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>📊 Données mises à jour en temps réel depuis TwitchTracker</p>
    <p>🚀 Développé avec Streamlit & Python</p>
</div>
""", unsafe_allow_html=True)
