import streamlit as st
import pandas as pd
import gspread
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Mondial 2026",
    page_icon="⚽",
    layout="wide"
)

# 👇 NOUVEAU : LE FOND D'ÉCRAN 👇
fond_ecran = """
<style>
.stApp {
    /* Image de stade avec un voile blanc transparent à 88% pour garantir la lisibilité du texte */
    background: linear-gradient(rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.88)), url("https://images.unsplash.com/photo-1518605368461-1e1c9e1d0092?auto=format&fit=crop&q=80&w=2000");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
/* Rendre l'entête transparente pour voir le fond */
.stApp > header {
    background-color: transparent;
}
</style>
"""
st.markdown(fond_ecran, unsafe_allow_html=True)
# 👆 ---------------------- 👆

# 👇 --- ZONE D'ADMINISTRATION --- 👇
PRONOS_OUVERTS = True  
DERNIERE_MAJ = "17/05/2026 à 18:30"
LIEN_WHATSAPP = "https://chat.whatsapp.com/LOgrgmIAqgy7m9PBpDsaf9?mode=wwt"
LIEN_CAGNOTTE = "https://paypal.me/mickaelBerault?locale.x=fr_FR&country.x=FR"
# 👆 ---------------------------- 👆

# --- CONNEXION GOOGLE SHEETS ---
@st.cache_resource
def get_google_sheet_client():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" not in st.secrets:
            return None
        json_info = st.secrets["gcp_service_account"]["json_file"]
        creds_dict = json.loads(json_info)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        return None

def connect_to_gsheets():
    client = get_google_sheet_client()
    if client:
        try:
            return client.open_by_key("15fDZ_pb8lNnX1TKuTAPNThgRJkF668O8XgkvVUPVldE").sheet1
        except:
            return None
    return None

# --- LISTE DES 72 MATCHS ---
MATCHS = [
    {"id": 1, "date": "2026-06-11", "heure": "21h", "groupe": "Groupe A", "eqA": "🇲🇽 Mexique", "eqB": "🇿🇦 Afrique Sud", "scA": None, "scB": None},
    {"id": 2, "date": "2026-06-12", "heure": "04h", "groupe": "Groupe A", "eqA": "🇰🇷 Corée du Sud", "eqB": "🇨🇿 Tchéquie", "scA": None, "scB": None},
    {"id": 7, "date": "2026-06-12", "heure": "21h", "groupe": "Groupe B", "eqA": "🇨🇦 Canada", "eqB": "🇧🇦 Bosnie-Herz.", "scA": None, "scB": None},
    {"id": 19, "date": "2026-06-13", "heure": "03h", "groupe": "Groupe D", "eqA": "🇺🇸 USA", "eqB": "🇵🇾 Paraguay", "scA": None, "scB": None},
    {"id": 20, "date": "2026-06-13", "heure": "06h", "groupe": "Groupe D", "eqA": "🇦🇺 Australie", "eqB": "🇹🇷 Turquie", "scA": None, "scB": None},
    {"id": 8, "date": "2026-06-13", "heure": "21h", "groupe": "Groupe B", "eqA": "🇶🇦 Qatar", "eqB": "🇨🇭 Suisse", "scA": None, "scB": None},
    {"id": 37, "date": "2026-06-14", "heure": "21h", "groupe": "Groupe G", "eqA": "🇧🇪 Belgique", "eqB": "🇪🇬 Égypte", "scA": None, "scB": None},
    {"id": 31, "date": "2026-06-14", "heure": "22h", "groupe": "Groupe F", "eqA": "🇳🇱 Pays-Bas", "eqB": "🇯🇵 Japon", "scA": None, "scB": None},
    {"id": 14, "date": "2026-06-14", "heure": "03h", "groupe": "Groupe C", "eqA": "🇭🇹 Haïti", "eqB": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "scA": None, "scB": None},
    {"id": 13, "date": "2026-06-15", "heure": "00h", "groupe": "Groupe C", "eqA": "🇧🇷 Brésil", "eqB": "🇲🇦 Maroc", "scA": None, "scB": None},
    {"id": 38, "date": "2026-06-15", "heure": "03h", "groupe": "Groupe G", "eqA": "🇮🇷 Iran", "eqB": "🇳🇿 Nv-Zélande", "scA": None, "scB": None},
    {"id": 25, "date": "2026-06-15", "heure": "19h", "groupe": "Groupe E", "eqA": "🇩🇪 Allemagne", "eqB": "🇨🇼 Curaçao", "scA": None, "scB": None},
    {"id": 26, "date": "2026-06-15", "heure": "01h", "groupe": "Groupe E", "eqA": "🇨🇮 Côte d'Ivoire", "eqB": "🇪🇨 Équateur", "scA": None, "scB": None},
    {"id": 55, "date": "2026-06-16", "heure": "18h", "groupe": "Groupe J", "eqA": "🇦🇷 Argentine", "eqB": "🇩🇿 Algérie", "scA": None, "scB": None},
    {"id": 56, "date": "2026-06-16", "heure": "06h", "groupe": "Groupe J", "eqA": "🇦🇹 Autriche", "eqB": "🇯🇴 Jordanie", "scA": None, "scB": None},
    {"id": 61, "date": "2026-06-16", "heure": "19h", "groupe": "Groupe K", "eqA": "🇵🇹 Portugal", "eqB": "🇨🇩 RD Congo", "scA": None, "scB": None},
    {"id": 62, "date": "2026-06-17", "heure": "04h
