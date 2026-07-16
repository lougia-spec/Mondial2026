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

fond_ecran = """
<style>
.stApp {
    background: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), url("https://images.unsplash.com/photo-1518605368461-1e1c9e1d0092?auto=format&fit=crop&q=80&w=2000");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
.stApp > header {
    background-color: transparent;
}
</style>
"""
st.markdown(fond_ecran, unsafe_allow_html=True)

# --- ZONE D'ADMINISTRATION ---
PRONOS_OUVERTS = True  # Ouvert pour les Demi-finale !
DERNIERE_MAJ = "Automatique via Google Sheets 📱"
LIEN_WHATSAPP = "https://chat.whatsapp.com/LOgrgmIAqgy7m9PBpDsaf9?mode=wwt"
LIEN_CAGNOTTE = "https://paypal.me/mickaelBerault?locale.x=fr_FR&country.x=FR"

# --- CONNEXION GOOGLE SHEETS ---
@st.cache_resource
def get_google_sheet_client():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" not in st.secrets: return None
        creds_dict = json.loads(st.secrets["gcp_service_account"]["json_file"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except: return None

def get_spreadsheet():
    client = get_google_sheet_client()
    if client:
        try: return client.open_by_key("15fDZ_pb8lNnX1TKuTAPNThgRJkF668O8XgkvVUPVldE")
        except: return None
    return None

def connect_to_gsheets():
    ss = get_spreadsheet()
    if ss:
        try: return ss.sheet1
        except: return None
    return None

# --- LA BASE DE DONNÉES DE SECOURS ---
MATCHS_BASE = [
    {"id": 1, "date": "2026-06-11", "heure": "21h", "groupe": "Groupe A", "eqA": "🇲🇽 Mexique", "eqB": "🇿🇦 Afrique Sud", "scA": 2, "scB": 0, "statut": "terminé"},
    {"id": 2, "date": "2026-06-12", "heure": "04h", "groupe": "Groupe A", "eqA": "🇰🇷 Corée du Sud", "eqB": "🇨🇿 Tchéquie", "scA": 2, "scB": 1, "statut": "terminé"},
    {"id": 7, "date": "2026-06-12", "heure": "21h", "groupe": "Groupe B", "eqA": "🇨🇦 Canada", "eqB": "🇧🇦 Bosnie-Herz.", "scA": 1, "scB": 1, "statut": "terminé"},
    {"id": 19, "date": "2026-06-13", "heure": "03h", "groupe": "Groupe D", "eqA": "🇺🇸 USA", "eqB": "🇵🇾 Paraguay", "scA": 4, "scB": 1, "statut": "terminé"},
    {"id": 20, "date": "2026-06-13", "heure": "06h", "groupe": "Groupe D", "eqA": "🇦🇺 Australie", "eqB": "🇹🇷 Turquie", "scA": 2, "scB": 0, "statut": "terminé"},
    {"id": 8, "date": "2026-06-13", "heure": "21h", "groupe": "Groupe B", "eqA": "🇶🇦 Qatar", "eqB": "🇨🇭 Suisse", "scA": 1, "scB": 1, "statut": "terminé"},
    {"id": 31, "date": "2026-06-14", "heure": "22h", "groupe": "Groupe F", "eqA": "🇳🇱 Pays-Bas", "eqB": "🇯🇵 Japon", "scA": 2, "scB": 2, "statut": "terminé"},
    {"id": 14, "date": "2026-06-14", "heure": "03h", "groupe": "Groupe C", "eqA": "🇭🇹 Haïti", "eqB": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "scA": 0, "scB": 1, "statut": "terminé"},
    {"id": 13, "date": "2026-06-15", "heure": "00h", "groupe": "Groupe C", "eqA": "🇧🇷 Brésil", "eqB": "🇲🇦 Maroc", "scA": 1, "scB": 1, "statut": "terminé"},
    {"id": 37, "date": "2026-06-15", "heure": "21h", "groupe": "Groupe G", "eqA": "🇧🇪 Belgique", "eqB": "🇪🇬 Égypte", "scA": None, "scB": None, "statut": ""},
    {"id": 38, "date": "2026-06-15", "heure": "03h", "groupe": "Groupe G", "eqA": "🇮🇷 Iran", "eqB": "🇳🇿 Nv-Zélande", "scA": None, "scB": None, "statut": ""},
    {"id": 25, "date": "2026-06-15", "heure": "19h", "groupe": "Groupe E", "eqA": "🇩🇪 Allemagne", "eqB": "🇨🇼 Curaçao", "scA": 7, "scB": 1, "statut": "terminé"},
    {"id": 26, "date": "2026-06-15", "heure": "01h", "groupe": "Groupe E", "eqA": "🇨🇮 Côte d'Ivoire", "eqB": "🇪🇨 Équateur", "scA": 1, "scB": 0, "statut": "terminé"},
    {"id": 32, "date": "2026-06-15", "heure": "04h", "groupe": "Groupe F", "eqA": "🇸🇪 Suède", "eqB": "🇹🇳 Tunisie", "scA": 5, "scB": 1, "statut": "terminé"},
    {"id": 43, "date": "2026-06-15", "heure": "18h", "groupe": "Groupe H", "eqA": "🇪🇸 Espagne", "eqB": "🇨🇻 Cap-Vert", "scA": 0, "scB": 0, "statut": "terminé"},
    {"id": 55, "date": "2026-06-16", "heure": "18h", "groupe": "Groupe J", "eqA": "🇦🇷 Argentine", "eqB": "🇩🇿 Algérie", "scA": None, "scB": None, "statut": ""},
    {"id": 56, "date": "2026-06-16", "heure": "06h", "groupe": "Groupe J", "eqA": "🇦🇹 Autriche", "eqB": "🇯🇴 Jordanie", "scA": None, "scB": None, "statut": ""},
    {"id": 61, "date": "2026-06-16", "heure": "19h", "groupe": "Groupe K", "eqA": "🇵🇹 Portugal", "eqB": "🇨🇩 RD Congo", "scA": None, "scB": None, "statut": ""},
    {"id": 62, "date": "2026-06-17", "heure": "04h", "groupe": "Groupe K", "eqA": "🇺🇿 Ouzbékistan", "eqB": "🇨🇴 Colombie", "scA": None, "scB": None, "statut": ""},
    {"id": 67, "date": "2026-06-17", "heure": "22h", "groupe": "Groupe L", "eqA": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "eqB": "🇭🇷 Croatie", "scA": None, "scB": None, "statut": ""},
    {"id": 68, "date": "2026-06-17", "heure": "01h", "groupe": "Groupe L", "eqA": "🇬🇭 Ghana", "eqB": "🇵🇦 Panama", "scA": None, "scB": None, "statut": ""},
    {"id": 10, "date": "2026-06-17", "heure": "21h", "groupe": "Groupe B", "eqA": "🇧🇦 Bosnie-Herz.", "eqB": "🇨🇭 Suisse", "scA": None, "scB": None, "statut": ""},
    {"id": 3, "date": "2026-06-18", "heure": "03h", "groupe": "Groupe A", "eqA": "🇲🇽 Mexique", "eqB": "🇰🇷 Corée du Sud", "scA": None, "scB": None, "statut": ""},
    {"id": 44, "date": "2026-06-18", "heure": "00h", "groupe": "Groupe H", "eqA": "🇸🇦 Arabie Saoudite", "eqB": "🇺🇾 Uruguay", "scA": None, "scB": None, "statut": ""},
    {"id": 4, "date": "2026-06-19", "heure": "06h", "groupe": "Groupe A", "eqA": "🇿🇦 Afrique Sud", "eqB": "🇨🇿 Tchéquie", "scA": None, "scB": None, "statut": ""},
    {"id": 9, "date": "2026-06-19", "heure": "00h", "groupe": "Groupe B", "eqA": "🇨🇦 Canada", "eqB": "🇶🇦 Qatar", "scA": None, "scB": None, "statut": ""},
    {"id": 21, "date": "2026-06-19", "heure": "21h", "groupe": "Groupe D", "eqA": "🇺🇸 USA", "eqB": "🇦🇺 Australie", "scA": None, "scB": None, "statut": ""},
    {"id": 49, "date": "2026-06-19", "heure": "21h", "groupe": "Groupe I", "eqA": "🇫🇷 France", "eqB": "🇸🇳 Sénégal", "scA": None, "scB": None, "statut": ""},
    {"id": 15, "date": "2026-06-20", "heure": "00h", "groupe": "Groupe C", "eqA": "🇧🇷 Brésil", "eqB": "🇭🇹 Haïti", "scA": None, "scB": None, "statut": ""},
    {"id": 16, "date": "2026-06-20", "heure": "00h", "groupe": "Groupe C", "eqA": "🇲🇦 Maroc", "eqB": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "scA": None, "scB": None, "statut": ""},
    {"id": 27, "date": "2026-06-20", "heure": "19h", "groupe": "Groupe E", "eqA": "🇩🇪 Allemagne", "eqB": "🇨🇮 Côte d'Ivoire", "scA": None, "scB": None, "statut": ""},
    {"id": 39, "date": "2026-06-20", "heure": "21h", "groupe": "Groupe G", "eqA": "🇧🇪 Belgique", "eqB": "🇮🇷 Iran", "scA": None, "scB": None, "statut": ""},
    {"id": 28, "date": "2026-06-21", "heure": "02h", "groupe": "Groupe E", "eqA": "🇨🇼 Curaçao", "eqB": "🇪🇨 Équateur", "scA": None, "scB": None, "statut": ""},
    {"id": 33, "date": "2026-06-21", "heure": "21h", "groupe": "Groupe F", "eqA": "🇳🇱 Pays-Bas", "eqB": "🇸🇪 Suède", "scA": None, "scB": None, "statut": ""},
    {"id": 34, "date": "2026-06-21", "heure": "01h", "groupe": "Groupe F", "eqA": "🇯🇵 Japon", "eqB": "🇹🇳 Tunisie", "scA": None, "scB": None, "statut": ""},
    {"id": 50, "date": "2026-06-21", "heure": "03h", "groupe": "Groupe I", "eqA": "🇮🇶 Irak", "eqB": "🇳🇴 Norvège", "scA": None, "scB": None, "statut": ""},
    {"id": 22, "date": "2026-06-22", "heure": "03h", "groupe": "Groupe D", "eqA": "🇵🇾 Paraguay", "eqB": "🇹🇷 Turquie", "scA": None, "scB": None, "statut": ""},
    {"id": 45, "date": "2026-06-22", "heure": "18h", "groupe": "Groupe H", "eqA": "🇪🇸 Espagne", "eqB": "🇸🇦 Arabie Saoudite", "scA": None, "scB": None, "statut": ""},
    {"id": 40, "date": "2026-06-22", "heure": "03h", "groupe": "Groupe G", "eqA": "🇪🇬 Égypte", "eqB": "🇳🇿 Nv-Zélande", "scA": None, "scB": None, "statut": ""},
    {"id": 57, "date": "2026-06-22", "heure": "18h", "groupe": "Groupe J", "eqA": "🇦🇷 Argentine", "eqB": "🇦🇹 Autriche", "scA": None, "scB": None, "statut": ""},
    {"id": 46, "date": "2026-06-22", "heure": "02h", "groupe": "Groupe H", "eqA": "🇨🇻 Cap-Vert", "eqB": "🇺🇾 Uruguay", "scA": None, "scB": None, "statut": ""},
    {"id": 51, "date": "2026-06-23", "heure": "21h", "groupe": "Groupe I", "eqA": "🇫🇷 France", "eqB": "🇮🇶 Irak", "scA": None, "scB": None, "statut": ""},
    {"id": 52, "date": "2026-06-23", "heure": "23h", "groupe": "Groupe I", "eqA": "🇸🇳 Sénégal", "eqB": "🇳🇴 Norvège", "scA": None, "scB": None, "statut": ""},
    {"id": 58, "date": "2026-06-23", "heure": "05h", "groupe": "Groupe J", "eqA": "🇩🇿 Algérie", "eqB": "🇯🇴 Jordanie", "scA": None, "scB": None, "statut": ""},
    {"id": 63, "date": "2026-06-23", "heure": "19h", "groupe": "Groupe K", "eqA": "🇵🇹 Portugal", "eqB": "🇺🇿 Ouzbékistan", "scA": None, "scB": None, "statut": ""},
    {"id": 69, "date": "2026-06-23", "heure": "22h", "groupe": "Groupe L", "eqA": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "eqB": "🇬🇭 Ghana", "scA": None, "scB": None, "statut": ""},
    {"id": 6, "date": "2026-06-24", "heure": "03h", "groupe": "Groupe A", "eqA": "🇿🇦 Afrique Sud", "eqB": "🇰🇷 Corée du Sud", "scA": None, "scB": None, "statut": ""},
    {"id": 11, "date": "2026-06-24", "heure": "21h", "groupe": "Groupe B", "eqA": "🇨🇭 Suisse", "eqB": "🇨🇦 Canada", "scA": None, "scB": None, "statut": ""},
    {"id": 12, "date": "2026-06-24", "heure": "21h", "groupe": "Groupe B", "eqA": "🇧🇦 Bosnie-Herz.", "eqB": "🇶🇦 Qatar", "scA": None, "scB": None, "statut": ""},
    {"id": 64, "date": "2026-06-24", "heure": "04h", "groupe": "Groupe K", "eqA": "🇨🇩 RD Congo", "eqB": "🇨🇴 Colombie", "scA": None, "scB": None, "statut": ""},
    {"id": 70, "date": "2026-06-24", "heure": "22h", "groupe": "Groupe L", "eqA": "🇭🇷 Croatie", "eqB": "🇵🇦 Panama", "scA": None, "scB": None, "statut": ""},
    {"id": 5, "date": "2026-06-25", "heure": "03h", "groupe": "Groupe A", "eqA": "🇨🇿 Tchéquie", "eqB": "🇲🇽 Mexique", "scA": None, "scB": None, "statut": ""},
    {"id": 17, "date": "2026-06-25", "heure": "00h", "groupe": "Groupe C", "eqA": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "eqB": "🇧🇷 Brésil", "scA": None, "scB": None, "statut": ""},
    {"id": 18, "date": "2026-06-25", "heure": "00h", "groupe": "Groupe C", "eqA": "🇲🇦 Maroc", "eqB": "🇭🇹 Haïti", "scA": None, "scB": None, "statut": ""},
    {"id": 23, "date": "2026-06-25", "heure": "21h", "groupe": "Groupe D", "eqA": "🇹🇷 Turquie", "eqB": "🇺🇸 USA", "scA": None, "scB": None, "statut": ""},
    {"id": 24, "date": "2026-06-25", "heure": "21h", "groupe": "Groupe D", "eqA": "🇵🇾 Paraguay", "eqB": "🇦🇺 Australie", "scA": None, "scB": None, "statut": ""},
    {"id": 29, "date": "2026-06-26", "heure": "18h", "groupe": "Groupe E", "eqA": "🇪🇨 Équateur", "eqB": "🇩🇪 Allemagne", "scA": None, "scB": None, "statut": ""},
    {"id": 30, "date": "2026-06-26", "heure": "18h", "groupe": "Groupe E", "eqA": "🇨🇼 Curaçao", "eqB": "🇨🇮 Côte d'Ivoire", "scA": None, "scB": None, "statut": ""},
    {"id": 35, "date": "2026-06-26", "heure": "01h", "groupe": "Groupe F", "eqA": "🇹🇳 Tunisie", "eqB": "🇳🇱 Pays-Bas", "scA": None, "scB": None, "statut": ""},
    {"id": 36, "date": "2026-06-26", "heure": "01h", "groupe": "Groupe F", "eqA": "🇯🇵 Japon", "eqB": "🇸🇪 Suède", "scA": None, "scB": None, "statut": ""},
    {"id": 41, "date": "2026-06-27", "heure": "05h", "groupe": "Groupe G", "eqA": "🇳🇿 Nv-Zélande", "eqB": "🇧🇪 Belgique", "scA": None, "scB": None, "statut": ""},
    {"id": 42, "date": "2026-06-27", "heure": "05h", "groupe": "Groupe G", "eqA": "🇪🇬 Égypte", "eqB": "🇮🇷 Iran", "scA": None, "scB": None, "statut": ""},
    {"id": 47, "date": "2026-06-27", "heure": "02h", "groupe": "Groupe H", "eqA": "🇺🇾 Uruguay", "eqB": "🇪🇸 Espagne", "scA": None, "scB": None, "statut": ""},
    {"id": 48, "date": "2026-06-27", "heure": "02h", "groupe": "Groupe H", "eqA": "🇨🇻 Cap-Vert", "eqB": "🇸🇦 Arabie Saoudite", "scA": None, "scB": None, "statut": ""},
    {"id": 53, "date": "2026-06-27", "heure": "21h", "groupe": "Groupe I", "eqA": "🇳🇴 Norvège", "eqB": "🇫🇷 France", "scA": None, "scB": None, "statut": ""},
    {"id": 54, "date": "2026-06-27", "heure": "21h", "groupe": "Groupe I", "eqA": "🇸🇳 Sénégal", "eqB": "🇮🇶 Irak", "scA": None, "scB": None, "statut": ""},
    {"id": 59, "date": "2026-06-28", "heure": "04h", "groupe": "Groupe J", "eqA": "🇯🇴 Jordanie", "eqB": "🇦🇷 Argentine", "scA": None, "scB": None, "statut": ""},
    {"id": 60, "date": "2026-06-28", "heure": "04h", "groupe": "Groupe J", "eqA": "🇩🇿 Algérie", "eqB": "🇦🇹 Autriche", "scA": None, "scB": None, "statut": ""},
    {"id": 65, "date": "2026-06-28", "heure": "01h", "groupe": "Groupe K", "eqA": "🇨🇴 Colombie", "eqB": "🇵🇹 Portugal", "scA": None, "scB": None, "statut": ""},
    {"id": 66, "date": "2026-06-28", "heure": "01h", "groupe": "Groupe K", "eqA": "🇨🇩 RD Congo", "eqB": "🇺🇿 Ouzbékistan", "scA": None, "scB": None, "statut": ""},
    {"id": 71, "date": "2026-06-28", "heure": "23h", "groupe": "Groupe L", "eqA": "🇵🇦 Panama", "eqB": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "scA": None, "scB": None, "statut": ""},
    {"id": 72, "date": "2026-06-28", "heure": "23h", "groupe": "Groupe L", "eqA": "🇭🇷 Croatie", "eqB": "🇬🇭 Ghana", "scA": None, "scB": None, "statut": ""},
]

def formater_date(d_str):
    obj = datetime.strptime(d_str, "%Y-%m-%d")
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois = ["Jan", "Fév", "Mars", "Avril", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
    return f"{jours[obj.weekday()]} {obj.day} {mois[obj.month-1]}"

@st.cache_data(ttl=60)
def charger_calendrier():
    ss = get_spreadsheet()
    if ss is None:
        return MATCHS_BASE
    
    try:
        ws = ss.worksheet("Calendrier")
        records = ws.get_all_records()
        if not records:
            raise Exception("Onglet vide")
            
        matchs_finaux = []
        for r in records:
            m = dict(r)
            m['scA'] = int(m['scA']) if str(m.get('scA', '')).strip() != '' else None
            m['scB'] = int(m['scB']) if str(m.get('scB', '')).strip() != '' else None
            m['statut'] = str(m.get('statut', '')).strip()
            matchs_finaux.append(m)
        return matchs_finaux
        
    except:
        try: ws = ss.add_worksheet(title="Calendrier", rows=100, cols=10)
        except: ws = ss.worksheet("Calendrier")
            
        df_base = pd.DataFrame(MATCHS_BASE).fillna("")
        ws.clear()
        ws.append_rows([df_base.columns.values.tolist()] + df_base.values.tolist())
        return MATCHS_BASE

MATCHS = charger_calendrier()

@st.cache_data(ttl=60)
def charger_donnees():
    try:
        sheet = connect_to_gsheets()
        if sheet is None: return pd.DataFrame(columns=["Nom et Prénom", "Email", "Match_ID", "Prono_A", "Prono_B", "Paiement"])
        data = sheet.get_all_records()
        if not data: return pd.DataFrame(columns=["Nom et Prénom", "Email", "Match_ID", "Prono_A", "Prono_B", "Paiement"])
        
        df = pd.DataFrame(data)
        if "Pseudo" in df.columns and "Nom et Prénom" not in df.columns:
            df.rename(columns={"Pseudo": "Nom et Prénom"}, inplace=True)
        if "Email" not in df.columns: df["Email"] = ""
        if "Paiement" not in df.columns: df["Paiement"] = "⏳ En attente"
        if "Match_ID" in df.columns: df["Match_ID"] = pd.to_numeric(df["Match_ID"], errors='coerce')
        return df
    except Exception as e:
        return pd.DataFrame(columns=["Nom et Prénom", "Email", "Match_ID", "Prono_A", "Prono_B", "Paiement"])

def envoyer_confirmation(destinataire, nom):
    if "email" not in st.secrets: return
    sender_email = st.secrets["email"]["address"]
    sender_password = st.secrets["email"]["password"]
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = destinataire
        msg['Subject'] = "⚽ Mondial 2026 - Pronostics enregistrés !"
        body = f"Bonjour {nom},\n\nTes pronostics pour le Mondial 2026 ont bien été validés !\n\nN'oublie pas de payer ta participation de 5€ via ce lien : {LIEN_CAGNOTTE}\n\nEt rejoins le groupe WhatsApp ici : {LIEN_WHATSAPP}\n\nBonne chance ! 🍀"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, destinataire, msg.as_string())
        server.quit()
    except: pass

def sauvegarder_tout(nom_prenom, email, liste_pronos):
    sheet = connect_to_gsheets()
    if sheet is None: return
    lignes_a_ajouter = []
    for (match_id, pa, pb) in liste_pronos:
        lignes_a_ajouter.append([nom_prenom, email, match_id, pa, pb, "⏳ En attente"])
    sheet.append_rows(lignes_a_ajouter)
    envoyer_confirmation(email, nom_prenom)
    charger_donnees.clear()

def calculer_points(prono_a, prono_b, reel_a, reel_b, eqA="", eqB=""):
    if reel_a is None: return 0 
    try:
        pa, pb = int(prono_a), int(prono_b)
        ra, rb = int(reel_a), int(reel_b)
    except:
        return 0
    points = 0
    res_reel = 1 if ra > rb else (2 if rb > ra else 0)
    res_prono = 1 if pa > pb else (2 if pb > pa else 0)
    if res_reel == res_prono:
        points += 1
        if pa == ra and pb == rb:
            points += 2
            
    if "France" in eqA or "France" in eqB:
        points = points * 2
    return points

def calculer_classement_groupe(nom_groupe):
    matchs_grp = [m for m in MATCHS if m['groupe'] == nom_groupe]
    equipes = set()
    for m in matchs_grp:
        equipes.add(m['eqA'])
        equipes.add(m['eqB'])
    
    stats = {eq: {'Pts': 0, 'J': 0, 'Diff': 0, 'BP': 0} for eq in equipes}
    
    for m in matchs_grp:
        if m['scA'] is not None and m['scB'] is not None:
            sA, sB = m['scA'], m['scB']
            stats[m['eqA']]['J'] += 1
            stats[m['eqB']]['J'] += 1
            stats[m['eqA']]['BP'] += sA
            stats[m['eqB']]['BP'] += sB
            stats[m['eqA']]['Diff'] += (sA - sB)
            stats[m['eqB']]['Diff'] += (sB - sA)
            
            if sA > sB:
                stats[m['eqA']]['Pts'] += 3
            elif sB > sA:
                stats[m['eqB']]['Pts'] += 3
            else:
                stats[m['eqA']]['Pts'] += 1
                stats[m['eqB']]['Pts'] += 1
                
    df = pd.DataFrame.from_dict(stats, orient='index')
    df = df.sort_values(by=['Pts', 'Diff', 'BP'], ascending=False)
    return df

def calculer_tendance(match_id, df_tout):
    if df_tout.empty: return None
    df_m = df_tout[df_tout['Match_ID'] == match_id]
    if df_m.empty: return None
    vic_A = 0
    vic_B = 0
    nul = 0
    total = 0
    for index, row in df_m.iterrows():
        try:
            pa = int(row['Prono_A'])
            pb = int(row['Prono_B'])
            total += 1
            if pa > pb: vic_A += 1
            elif pb > pa: vic_B += 1
            else: nul += 1
        except: pass
    if total == 0: return None
    return {
        "A": round(vic_A / total * 100),
        "B": round(vic_B / total * 100),
        "N": round(nul / total * 100)
    }

# --- INTERFACE ---

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/FIFA_World_Cup_2026_Logo.svg/1024px-FIFA_World_Cup_2026_Logo.svg.png", width=200)
    st.title("⚽ Mondial 2026")
    
    st.markdown("---")
    st.write("### 🏆 Top 10 Actuel")
    
    try:
        df_top = charger_donnees()
        col_nom = "Nom et Prénom" if "Nom et Prénom" in df_top.columns else "Pseudo"
        
        if not df_top.empty and col_nom in df_top.columns:
            scores_live = {}
            joueurs_live = df_top[col_nom].unique()
            for j in joueurs_live:
                pts = 0
                pronos_j = df_top[df_top[col_nom] == j]
                for m in MATCHS:
                    pari = pronos_j[pronos_j.Match_ID == m['id']]
                    if not pari.empty and m['scA'] is not None:
                        try:
                            pts += calculer_points(pari.iloc[0]['Prono_A'], pari.iloc[0]['Prono_B'], m['scA'], m['scB'], m['eqA'], m['eqB'])
                        except: pass
                scores_live[j] = pts
            
            if scores_live:
                df_rank_live = pd.DataFrame(list(scores_live.items()), columns=["Joueur", "Pts"])
                df_rank_live = df_rank_live.sort_values(by="Pts", ascending=False).reset_index(drop=True)
                df_rank_live.index += 1
                st.table(df_rank_live.head(10))
            else:
                st.write("En attente de points...")
        else:
            st.write("Chargement...")
    except:
        st.write("...")

    st.markdown("---")
    st.write(f"🕒 **MàJ :** `{DERNIERE_MAJ}`")
    try:
        nb_joueurs = len(df_top[col_nom].unique()) if not df_top.empty else 0
        st.caption(f"{nb_joueurs} joueurs inscrits")
    except: pass


st.title("🏆 Faites vos Jeux !")

# 👇 NOUVEL ONGLET "TABLEAU FINAL" AJOUTÉ ICI 👇
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📢 Résultats & Calendrier", 
    "📝 Pronostics", 
    "📜 Règlement", 
    "📊 Classement", 
    "🌍 Groupes", 
    "👀 Mes Paris", 
    "🔎 Pronos par Match",
    "🌳 Phase Finale"
])

with tab1: 
    st.header("📢 Résultats & Calendrier (Phase Finale)")
    
    # 👇 FILTRE : On ne garde que les matchs après les poules (ID > 72) 👇
    matchs_phase_finale = [m for m in MATCHS if int(m.get('id', 0)) > 72]
    
    if not matchs_phase_finale:
        st.info("⏳ Le calendrier de la phase finale est en cours de préparation.")
    else:
        dates_uniques = sorted(list(set(m['date'] for m in matchs_phase_finale)))
        for d in dates_uniques:
            st.markdown(f"##### 🗓️ {formater_date(d)}")
            matchs_du_jour = [m for m in matchs_phase_finale if m['date'] == d]
            cols = st.columns(2)
            for i, m in enumerate(matchs_du_jour):
                with cols[i % 2]:
                    if m['scA'] is not None and m['scB'] is not None:
                        statut = m.get("statut", "terminé")
                        if statut.lower() == "en cours":
                            st.warning(f"### {m['eqA']} **{m['scA']} - {m['scB']}** {m['eqB']}\n🔥 **En cours**")
                        else:
                            st.success(f"### {m['eqA']} **{m['scA']} - {m['scB']}** {m['eqB']}\n✅ **Terminé**")
                    else:
                        with st.container(border=True):
                            st.write(f"**{m['eqA']}** vs **{m['eqB']}**")
                            st.caption(f"🕒 {m['heure']} - {m['groupe']}")

with tab2:
    if PRONOS_OUVERTS:
        st.write("### 🏆 Pronostics - L'heure de la Finale !")
        try:
            if "google_ok" not in st.session_state:
                connect_to_gsheets()
                st.session_state["google_ok"] = True
        except Exception as e:
            st.error(f"⚠️ Erreur: {e}")
        
        df_stats = charger_donnees()
        
        noms_inscrits = []
        if not df_stats.empty:
            col_nom = "Nom et Prénom" if "Nom et Prénom" in df_stats.columns else "Pseudo"
            if col_nom in df_stats.columns:
                noms_inscrits = sorted(df_stats[col_nom].astype(str).unique().tolist())

        with st.form("grille_pronos_finale"):
            st.info("💡 **Procédure simplifiée :** Sélectionne ton nom dans la liste et confirme ton email pour débloquer ta grille. Remplis les scores pour la petite et la grande finale !")
            
            col_p, col_e = st.columns(2)
            nom_prenom = col_p.selectbox("Ton Nom et Prénom :", ["-- Clique ici pour choisir --"] + noms_inscrits)
            email = col_e.text_input("Ton Email (Sécurité) :")

            saisies = {}
            
            # 👇 LE FILTRE SÉCURISÉ : On cherche exactement "finale" ou on cherche "petite" 👇
            matchs_phase_finale = []
            for m in MATCHS:
                groupe_texte = str(m.get('groupe', '')).lower().strip()
                if groupe_texte == "finale" or "petite" in groupe_texte or "3ème" in groupe_texte or "3eme" in groupe_texte:
                    matchs_phase_finale.append(m)
            
            if not matchs_phase_finale:
                st.warning("⏳ Les matchs finaux n'ont pas encore été ajoutés par l'administrateur.")
            else:
                matchs_tries = sorted(matchs_phase_finale, key=lambda x: x['date'])
                dates_uniques = sorted(list(set(m['date'] for m in matchs_tries)))

                for d in dates_uniques:
                    st.markdown(f"### 🗓️ {formater_date(d)}")
                    matchs_du_jour = [m for m in matchs_tries if m['date'] == d]
                    cols = st.columns(2)
                    for i, m in enumerate(matchs_du_jour):
                        with cols[i % 2]:
                            with st.container(border=True):
                                stats = calculer_tendance(m['id'], df_stats)
                                if stats:
                                    st.caption(f"📊 Tendance : {m['eqA']} {stats['A']}% - Nul {stats['N']}% - {m['eqB']} {stats['B']}%")
                                else:
                                    st.caption(f"🕑 {m['heure']} - {m['groupe']}")
                                
                                st.markdown(f"**{m['eqA']}** vs **{m['eqB']}**")
                                c1, c2 = st.columns(2)
                                pa = c1.number_input(f"{m['eqA']}", 0, 10, key=f"A_{m['id']}")
                                pb = c2.number_input(f"{m['eqB']}", 0, 10, key=f"B_{m['id']}")
                                saisies[m['id']] = (pa, pb)
                    st.divider()
            
            st.write("")
            valider = st.form_submit_button("Valider mes Finales", use_container_width=True)
        
        if valider:
            if nom_prenom == "-- Clique ici pour choisir --" or not email:
                st.error("⚠️ Il faut sélectionner ton Nom/Prénom ET confirmer ton email !")
            else:
                with st.spinner("Enregistrement en cours..."):
                    liste_a_envoyer = []
                    for mid, (sa, sb) in saisies.items():
                        liste_a_envoyer.append((mid, sa, sb))
                    sauvegarder_tout(nom_prenom, email, liste_a_envoyer) 
                
                st.success(f"✅ Tes pronostics pour les Finales ont bien été enregistrés, {nom_prenom} !")
                st.balloons()
    else:
        st.error("⛔️ Les pronostics sont temporairement fermés.")
        st.info("Tu peux toujours consulter ton classement et les résultats dans les autres onglets.")
with tab3:
    st.header("📜 Règlement du Concours")
    st.markdown("""
    ### 🎯 Calcul des Points
    
    * **3 Points** : Score Exact
        * *Exemple : Tu as pronostiqué 2-1 et le match finit 2-1.*
    * **1 Point** : Bon Résultat (mais mauvais score)
        * *Exemple : Tu as pronostiqué 1-0 et le match finit 3-0 (Tu as trouvé le vainqueur).*
        * *Exemple : Tu as pronostiqué 1-1 et le match finit 0-0 (Tu as trouvé le match nul).*
    * **0 Point** : Mauvais Résultat
    
    🔥 **RÈGLE SPÉCIALE :** Tous les matchs de l'**Équipe de France** comptent **DOUBLE** ! Un score exact vaudra **6 points** au lieu de 3, et un bon résultat vaudra **2 points** au lieu d'1.
    
    ---
    ### 🔮 Phase Finale (À partir des 16èmes)
    Une fois la phase de poules officiellement terminée (le 28 juin), la compétition continue ! 
    * Le site sera temporairement réouvert pour vous permettre de pronostiquer la suite du tableau final.
    * **Procédure simplifiée :** Pour valider vos grilles de phase finale, vous n'aurez pas besoin de vous réinscrire. Il vous suffira de **sélectionner votre Nom/Prénom dans un menu déroulant** et, par sécurité contre la triche, de **saisir l'adresse e-mail** utilisée lors de votre inscription initiale.
    
    ---
    ### 🏆 Répartition des Gains
    La somme totale des participations sera redistribuée aux trois meilleurs pronostiqueurs selon la clé de répartition suivante :
    * 🥇 **1ère place** : 60 % de la cagnotte totale.
    * 🥈 **2ème place** : 30 % de la cagnotte totale.
    * 🥉 **3ème place** : 10 % de la cagnotte totale.

    En cas d'égalité, les gains du rang concerné seront partagés équitablement entre les ex-aequo.
    """)

with tab4:
    st.write("### 📊 Classement Général Complet")
    df = charger_donnees()
    if df.empty:
        st.info("Personne n'a encore parié.")
    else:
        scores_joueurs = {}
        col_nom = "Nom et Prénom" if "Nom et Prénom" in df.columns else "Pseudo"
        if col_nom in df.columns:
            joueurs = df[col_nom].unique()
            
            for j in joueurs:
                pts = 0
                pronos_j = df[df[col_nom] == j]
                for m in MATCHS:
                    pari = pronos_j[pronos_j.Match_ID == m['id']]
                    if not pari.empty and m['scA'] is not None:
                        try:
                            pts += calculer_points(pari.iloc[0]['Prono_A'], pari.iloc[0]['Prono_B'], m['scA'], m['scB'], m['eqA'], m['eqB'])
                        except: pass
                scores_joueurs[j] = pts
            
            if scores_joueurs:
                df_rank = pd.DataFrame(list(scores_joueurs.items()), columns=["Joueur", "Points"])
                df_rank = df_rank.sort_values(by="Points", ascending=False).reset_index(drop=True)
                df_rank.index += 1
                st.dataframe(df_rank, use_container_width=True, height=600)
                
                st.markdown("---")
                st.write("### 📈 La Course aux Points (Évolution)")
                
                matchs_joues = [m for m in MATCHS if m['scA'] is not None and m['scB'] is not None]
                matchs_joues.sort(key=lambda x: x['date']) 
                dates_jouees = sorted(list(set(m['date'] for m in matchs_joues)))
                
                if dates_jouees:
                    historique = {j: [0] for j in joueurs} 
                    labels_x = ["00 - Départ"]
                    cumul = {j: 0 for j in joueurs}
                    
                    for index, d in enumerate(dates_jouees):
                        jour_num = str(index + 1).zfill(2) 
                        labels_x.append(f"{jour_num} - {formater_date(d)}")
                        
                        matchs_jour = [m for m in matchs_joues if m['date'] == d]
                        for j in joueurs:
                            pronos_j = df[df[col_nom] == j]
                            pts_jour = 0
                            for m in matchs_jour:
                                pari = pronos_j[pronos_j.Match_ID == m['id']]
                                if not pari.empty:
                                    try:
                                        pts_jour += calculer_points(pari.iloc[0]['Prono_A'], pari.iloc[0]['Prono_B'], m['scA'], m['scB'], m['eqA'], m['eqB'])
                                    except: pass
                            cumul[j] += pts_jour 
                            historique[j].append(cumul[j])
                            
                    df_chart = pd.DataFrame(historique, index=labels_x)
                    st.line_chart(df_chart, height=450)
                else:
                    st.info("Le graphique s'affichera dès que le premier match sera terminé !")

with tab5:
    st.header("🌍 Classement des Groupes")
    groupes = sorted(list(set(m['groupe'] for m in MATCHS if "groupe" in m['groupe'].lower())))
    cols = st.columns(2)
    for i, grp in enumerate(groupes):
        with cols[i % 2]: 
            with st.container(border=True):
                st.subheader(grp)
                df_classement = calculer_classement_groupe(grp)
                st.dataframe(df_classement, use_container_width=True)
                st.divider()
                st.caption(f"Matchs du {grp}")
                matchs_grp = [m for m in MATCHS if m['groupe'] == grp]
                for m in matchs_grp:
                    if m['scA'] is not None:
                        statut = m.get("statut", "terminé")
                        if statut.lower() == "en cours":
                            st.warning(f"🔥 {m['eqA']} **{m['scA']}-{m['scB']}** {m['eqB']}")
                        else:
                            st.success(f"{m['eqA']} **{m['scA']}-{m['scB']}** {m['eqB']}")
                    else:
                        st.write(f"⏳ {m['eqA']} vs {m['eqB']}")

with tab6:
    st.header("🔍 Retrouver mes pronostics")
    st.markdown("Tape simplement ton prénom pour retrouver ta grille.")
    nom_search = st.text_input("Recherche :")
    
    if nom_search:
        df = charger_donnees()
        col_nom = "Nom et Prénom" if "Nom et Prénom" in df.columns else "Pseudo"
        
        if not df.empty and col_nom in df.columns:
            df_temp = df.copy()
            df_temp[col_nom] = df_temp[col_nom].astype(str).str.lower().str.strip()
            search_clean = nom_search.lower().strip()
            
            mes_pronos = df[df_temp[col_nom].str.contains(search_clean, na=False)].copy()
            
            if not mes_pronos.empty:
                vrai_nom = mes_pronos.iloc[0][col_nom]
                mes_pronos = df[df[col_nom] == vrai_nom]
                
                st.success(f"✅ Pronostics trouvés pour : **{vrai_nom}**")
                
                data_affichage = []
                for m in MATCHS:
                    ligne_prono = mes_pronos[mes_pronos['Match_ID'] == m['id']]
                    if not ligne_prono.empty:
                        pa = ligne_prono.iloc[0]['Prono_A']
                        pb = ligne_prono.iloc[0]['Prono_B']
                        data_affichage.append({
                            "Date": m['date'],
                            "Match": f"{m['eqA']} vs {m['eqB']}",
                            "Mon Prono": f"{pa} - {pb}"
                        })
                if data_affichage:
                    st.table(pd.DataFrame(data_affichage))
            else:
                st.info("Nom introuvable. Vérifie l'orthographe.")

with tab7:
    st.header("🔎 Tous les pronostics par match")
    df = charger_donnees()
    
    if df.empty:
        st.info("Personne n'a encore parié. Reviens plus tard ! 😊")
    else:
        # 👇 FILTRE : On ne garde que les matchs non joués OU les matchs en cours 👇
        matchs_filtrés = [m for m in MATCHS if m['scA'] is None or str(m.get('statut', '')).lower() == "en cours"]
        
        if not matchs_filtrés:
            st.success("🎉 Tous les matchs du tournoi ont été joués et saisis !")
        else:
            options_matchs = []
            for m in matchs_filtrés:
                date_belle = formater_date(m['date'])
                # On ajoute un petit indicateur visuel si le match est en cours de jeu
                prefixe = "🔥 [EN COURS] " if str(m.get('statut', '')).lower() == "en cours" else ""
                options_matchs.append(f"{prefixe}{m['eqA']} vs {m['eqB']} ({date_belle})")
            
            choix = st.selectbox("Sélectionne un match pour voir les paris :", options_matchs)
            
            index_choix = options_matchs.index(choix)
            match_select = matchs_filtrés[index_choix] # On utilise bien la liste filtrée ici
            
            df_filtre = df[df['Match_ID'] == match_select['id']]
            
            if df_filtre.empty:
                st.warning("Aucun joueur n'a encore pronostiqué ce match.")
            else:
                col_nom = "Nom et Prénom" if "Nom et Prénom" in df.columns else "Pseudo"
                
                stats = calculer_tendance(match_select['id'], df)
                if stats:
                    st.info(f"📊 **Tendance de la communauté :** Victoire {match_select['eqA']} **{stats['A']}%** | Nul **{stats['N']}%** | Victoire {match_select['eqB']} **{stats['B']}%**")
                
                df_affichage = df_filtre[[col_nom, 'Prono_A', 'Prono_B']].copy()
                df_affichage = df_affichage.rename(columns={
                    col_nom: "Joueur", 
                    "Prono_A": f"Score {match_select['eqA']}", 
                    "Prono_B": f"Score {match_select['eqB']}"
                })
                
                df_affichage = df_affichage.sort_values(by="Joueur").reset_index(drop=True)
                st.dataframe(df_affichage, use_container_width=True)
with tab8:
    st.header("🌳 Phase Finale")
    st.markdown("Suivez l'évolution des éliminations directes !")

    matchs_finale = [m for m in MATCHS if int(m.get('id', 0)) > 72]

    if not matchs_finale:
        st.info("⏳ Les affiches de la phase finale n'ont pas encore été définies. Le tableau apparaîtra ici une fois complété par l'administrateur.")
    else:
        ordre_phases = ["16ème", "8ème", "Quart", "Demi", "Finale"]
        
        for phase in ordre_phases:
            matchs_phase = [m for m in matchs_finale if phase.lower() in str(m.get('groupe', '')).lower()]
            
            if matchs_phase:
                st.markdown(f"### 🏆 {phase}s de finale" if phase != "Finale" else f"### 🏆 {phase}")
                cols = st.columns(2)
                for i, m in enumerate(matchs_phase):
                    with cols[i % 2]:
                        if m['scA'] is not None and m['scB'] is not None:
                            statut = m.get("statut", "terminé")
                            if statut.lower() == "en cours":
                                st.warning(f"🔥 {m['eqA']} **{m['scA']} - {m['scB']}** {m['eqB']}")
                            else:
                                st.success(f"✅ {m['eqA']} **{m['scA']} - {m['scB']}** {m['eqB']}")
                        else:
                            with st.container(border=True):
                                st.write(f"**{m['eqA']}** vs **{m['eqB']}**")
                                st.caption(f"🗓️ {formater_date(m['date'])} - 🕒 {m['heure']}")
                st.divider()
