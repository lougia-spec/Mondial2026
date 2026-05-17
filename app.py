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

# 👇 --- ZONE D'ADMINISTRATION --- 👇
PRONOS_OUVERTS = True  
DERNIERE_MAJ = "17/05/2026 à 18:15"
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
    {"id": 62, "date": "2026-06-17", "heure": "04h", "groupe": "Groupe K", "eqA": "🇺🇿 Ouzbékistan", "eqB": "🇨🇴 Colombie", "scA": None, "scB": None},
    {"id": 67, "date": "2026-06-17", "heure": "22h", "groupe": "Groupe L", "eqA": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "eqB": "🇭🇷 Croatie", "scA": None, "scB": None},
    {"id": 68, "date": "2026-06-17", "heure": "01h", "groupe": "Groupe L", "eqA": "🇬🇭 Ghana", "eqB": "🇵🇦 Panama", "scA": None, "scB": None},
    {"id": 10, "date": "2026-06-17", "heure": "21h", "groupe": "Groupe B", "eqA": "🇧🇦 Bosnie-Herz.", "eqB": "🇨🇭 Suisse", "scA": None, "scB": None},
    {"id": 3, "date": "2026-06-18", "heure": "03h", "groupe": "Groupe A", "eqA": "🇲🇽 Mexique", "eqB": "🇰🇷 Corée du Sud", "scA": None, "scB": None},
    {"id": 43, "date": "2026-06-18", "heure": "18h", "groupe": "Groupe H", "eqA": "🇪🇸 Espagne", "eqB": "🇨🇻 Cap-Vert", "scA": None, "scB": None},
    {"id": 44, "date": "2026-06-18", "heure": "00h", "groupe": "Groupe H", "eqA": "🇸🇦 Arabie Saoudite", "eqB": "🇺🇾 Uruguay", "scA": None, "scB": None},
    {"id": 4, "date": "2026-06-19", "heure": "06h", "groupe": "Groupe A", "eqA": "🇿🇦 Afrique Sud", "eqB": "🇨🇿 Tchéquie", "scA": None, "scB": None},
    {"id": 9, "date": "2026-06-19", "heure": "00h", "groupe": "Groupe B", "eqA": "🇨🇦 Canada", "eqB": "🇶🇦 Qatar", "scA": None, "scB": None},
    {"id": 21, "date": "2026-06-19", "heure": "21h", "groupe": "Groupe D", "eqA": "🇺🇸 USA", "eqB": "🇦🇺 Australie", "scA": None, "scB": None},
    {"id": 49, "date": "2026-06-19", "heure": "21h", "groupe": "Groupe I", "eqA": "🇫🇷 France", "eqB": "🇸🇳 Sénégal", "scA": None, "scB": None},
    {"id": 15, "date": "2026-06-20", "heure": "00h", "groupe": "Groupe C", "eqA": "🇧🇷 Brésil", "eqB": "🇭🇹 Haïti", "scA": None, "scB": None},
    {"id": 16, "date": "2026-06-20", "heure": "00h", "groupe": "Groupe C", "eqA": "🇲🇦 Maroc", "eqB": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "scA": None, "scB": None},
    {"id": 27, "date": "2026-06-20", "heure": "19h", "groupe": "Groupe E", "eqA": "🇩🇪 Allemagne", "eqB": "🇨🇮 Côte d'Ivoire", "scA": None, "scB": None},
    {"id": 39, "date": "2026-06-20", "heure": "21h", "groupe": "Groupe G", "eqA": "🇧🇪 Belgique", "eqB": "🇮🇷 Iran", "scA": None, "scB": None},
    {"id": 28, "date": "2026-06-21", "heure": "02h", "groupe": "Groupe E", "eqA": "🇨🇼 Curaçao", "eqB": "🇪🇨 Équateur", "scA": None, "scB": None},
    {"id": 32, "date": "2026-06-21", "heure": "04h", "groupe": "Groupe F", "eqA": "🇸🇪 Suède", "eqB": "🇹🇳 Tunisie", "scA": None, "scB": None},
    {"id": 33, "date": "2026-06-21", "heure": "21h", "groupe": "Groupe F", "eqA": "🇳🇱 Pays-Bas", "eqB": "🇸🇪 Suède", "scA": None, "scB": None},
    {"id": 50, "date": "2026-06-21", "heure": "03h", "groupe": "Groupe I", "eqA": "🇮🇶 Irak", "eqB": "🇳🇴 Norvège", "scA": None, "scB": None},
    {"id": 22, "date": "2026-06-22", "heure": "03h", "groupe": "Groupe D", "eqA": "🇵🇾 Paraguay", "eqB": "🇹🇷 Turquie", "scA": None, "scB": None},
    {"id": 45, "date": "2026-06-22", "heure": "18h", "groupe": "Groupe H", "eqA": "🇪🇸 Espagne", "eqB": "🇸🇦 Arabie Saoudite", "scA": None, "scB": None},
    {"id": 40, "date": "2026-06-22", "heure": "03h", "groupe": "Groupe G", "eqA": "🇪🇬 Égypte", "eqB": "🇳🇿 Nv-Zélande", "scA": None, "scB": None},
    {"id": 57, "date": "2026-06-22", "heure": "18h", "groupe": "Groupe J", "eqA": "🇦🇷 Argentine", "eqB": "🇦🇹 Autriche", "scA": None, "scB": None},
    {"id": 58, "date": "2026-06-23", "heure": "05h", "groupe": "Groupe J", "eqA": "🇩🇿 Algérie", "eqB": "🇯🇴 Jordanie", "scA": None, "scB": None},
    {"id": 63, "date": "2026-06-23", "heure": "19h", "groupe": "Groupe K", "eqA": "🇵🇹 Portugal", "eqB": "🇺🇿 Ouzbékistan", "scA": None, "scB": None},
    {"id": 69, "date": "2026-06-23", "heure": "22h", "groupe": "Groupe L", "eqA": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "eqB": "🇬🇭 Ghana", "scA": None, "scB": None},
    {"id": 52, "date": "2026-06-23", "heure": "23h", "groupe": "Groupe I", "eqA": "🇸🇳 Sénégal", "eqB": "🇳🇴 Norvège", "scA": None, "scB": None},
    {"id": 54, "date": "2026-06-23", "heure": "18h", "groupe": "Groupe I", "eqA": "🇸🇳 Sénégal", "eqB": "🇮🇶 Irak", "scA": None, "scB": None},
    {"id": 6, "date": "2026-06-24", "heure": "03h", "groupe": "Groupe A", "eqA": "🇿🇦 Afrique Sud", "eqB": "🇰🇷 Corée du Sud", "scA": None, "scB": None},
    {"id": 11, "date": "2026-06-24", "heure": "21h", "groupe": "Groupe B", "eqA": "🇨🇭 Suisse", "eqB": "🇨🇦 Canada", "scA": None, "scB": None},
    {"id": 12, "date": "2026-06-24", "heure": "21h", "groupe": "Groupe B", "eqA": "🇧🇦 Bosnie-Herz.", "eqB": "🇶🇦 Qatar", "scA": None, "scB": None},
    {"id": 64, "date": "2026-06-24", "heure": "04h", "groupe": "Groupe K", "eqA": "🇨🇩 RD Congo", "eqB": "🇨🇴 Colombie", "scA": None, "scB": None},
    {"id": 70, "date": "2026-06-24", "heure": "22h", "groupe": "Groupe L", "eqA": "🇭🇷 Croatie", "eqB": "🇵🇦 Panama", "scA": None, "scB": None},
    {"id": 73, "date": "2026-06-25", "heure": "03h", "groupe": "Groupe A", "eqA": "🇨🇿 Tchéquie", "eqB": "🇲🇽 Mexique", "scA": None, "scB": None},
    {"id": 17, "date": "2026-06-25", "heure": "00h", "groupe": "Groupe C", "eqA": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "eqB": "🇧🇷 Brésil", "scA": None, "scB": None},
    {"id": 18, "date": "2026-06-25", "heure": "00h", "groupe": "Groupe C", "eqA": "🇲🇦 Maroc", "eqB": "🇭🇹 Haïti", "scA": None, "scB": None},
    {"id": 23, "date": "2026-06-25", "heure": "21h", "groupe": "Groupe D", "eqA": "🇹🇷 Turquie", "eqB": "🇺🇸 USA", "scA": None, "scB": None},
    {"id": 24, "date": "2026-06-25", "heure": "21h", "groupe": "Groupe D", "eqA": "🇵🇾 Paraguay", "eqB": "🇦🇺 Australie", "scA": None, "scB": None},
    {"id": 29, "date": "2026-06-26", "heure": "18h", "groupe": "Groupe E", "eqA": "🇪🇨 Équateur", "eqB": "🇩🇪 Allemagne", "scA": None, "scB": None},
    {"id": 30, "date": "2026-06-26", "heure": "18h", "groupe": "Groupe E", "eqA": "🇨🇼 Curaçao", "eqB": "🇨🇮 Côte d'Ivoire", "scA": None, "scB": None},
    {"id": 34, "date": "2026-06-26", "heure": "01h", "groupe": "Groupe F", "eqA": "🇯🇵 Japon", "eqB": "🇹🇳 Tunisie", "scA": None, "scB": None},
    {"id": 35, "date": "2026-06-26", "heure": "01h", "groupe": "Groupe F", "eqA": "🇹🇳 Tunisie", "eqB": "🇳🇱 Pays-Bas", "scA": None, "scB": None},
    {"id": 36, "date": "2026-06-26", "heure": "01h", "groupe": "Groupe F", "eqA": "🇯🇵 Japon", "eqB": "🇸🇪 Suède", "scA": None, "scB": None},
    {"id": 41, "date": "2026-06-27", "heure": "05h", "groupe": "Groupe G", "eqA": "🇳🇿 Nv-Zélande", "eqB": "🇧🇪 Belgique", "scA": None, "scB": None},
    {"id": 42, "date": "2026-06-27", "heure": "05h", "groupe": "Groupe G", "eqA": "🇪🇬 Égypte", "eqB": "🇮🇷 Iran", "scA": None, "scB": None},
    {"id": 46, "date": "2026-06-27", "heure": "02h", "groupe": "Groupe H", "eqA": "🇨🇻 Cap-Vert", "eqB": "🇺🇾 Uruguay", "scA": None, "scB": None},
    {"id": 47, "date": "2026-06-27", "heure": "02h", "groupe": "Groupe H", "eqA": "🇺🇾 Uruguay", "eqB": "🇪🇸 Espagne", "scA": None, "scB": None},
    {"id": 48, "date": "2026-06-27", "heure": "02h", "groupe": "Groupe H", "eqA": "🇨🇻 Cap-Vert", "eqB": "🇸🇦 Arabie Saoudite", "scA": None, "scB": None},
    {"id": 51, "date": "2026-06-27", "heure": "21h", "groupe": "Groupe I", "eqA": "🇫🇷 France", "eqB": "🇮🇶 Irak", "scA": None, "scB": None},
    {"id": 53, "date": "2026-06-27", "heure": "21h", "groupe": "Groupe I", "eqA": "🇳🇴 Norvège", "eqB": "🇫🇷 France", "scA": None, "scB": None},
    {"id": 59, "date": "2026-06-28", "heure": "04h", "groupe": "Groupe J", "eqA": "🇯🇴 Jordanie", "eqB": "🇦🇷 Argentine", "scA": None, "scB": None},
    {"id": 60, "date": "2026-06-28", "heure": "04h", "groupe": "Groupe J", "eqA": "🇩🇿 Algérie", "eqB": "🇦🇹 Autriche", "scA": None, "scB": None},
    {"id": 65, "date": "2026-06-28", "heure": "01h", "groupe": "Groupe K", "eqA": "🇨🇴 Colombie", "eqB": "🇵🇹 Portugal", "scA": None, "scB": None},
    {"id": 66, "date": "2026-06-28", "heure": "01h", "groupe": "Groupe K", "eqA": "🇨🇩 RD Congo", "eqB": "🇺🇿 Ouzbékistan", "scA": None, "scB": None},
    {"id": 71, "date": "2026-06-28", "heure": "23h", "groupe": "Groupe L", "eqA": "🇵🇦 Panama", "eqB": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "scA": None, "scB": None},
    {"id": 72, "date": "2026-06-28", "heure": "23h", "groupe": "Groupe L", "eqA": "🇭🇷 Croatie", "eqB": "🇬🇭 Ghana", "scA": None, "scB": None},
]

# --- FONCTIONS ROBUSTES AVEC CACHE ---

def formater_date
