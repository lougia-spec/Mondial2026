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
DERNIERE_MAJ = "17/05/2026 à 13:00"
LIEN_WHATSAPP = "https://chat.whatsapp.com/LOgrgmIAqgy7m9PBpDsaf9?mode=wwt"
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
            return client.open_by_key("4cU79Zf5vxuEgjRdkPRuAXkbyorHtMNIQTU2ZYFUTy8").sheet1
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
@st.cache_data(ttl=60)
def charger_donnees():
    try:
        sheet = connect_to_gsheets()
        if sheet is None: 
            return pd.DataFrame(columns=["Nom et Prénom", "Email", "Match_ID", "Prono_A", "Prono_B"])
        data = sheet.get_all_records()
        if not data:
            return pd.DataFrame(columns=["Nom et Prénom", "Email", "Match_ID", "Prono_A", "Prono_B"])
        df = pd.DataFrame(data)
        if "Pseudo" in df.columns and "Nom et Prénom" not in df.columns:
            df.rename(columns={"Pseudo": "Nom et Prénom"}, inplace=True)
        if "Email" not in df.columns:
            df["Email"] = ""
        return df
    except Exception as e:
        return pd.DataFrame(columns=["Nom et Prénom", "Email", "Match_ID", "Prono_A", "Prono_B"])

def envoyer_confirmation(destinataire, nom):
    if "email" not in st.secrets: return
    sender_email = st.secrets["email"]["address"]
    sender_password = st.secrets["email"]["password"]
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = destinataire
        msg['Subject'] = "⚽ Mondial 2026 - Pronostics enregistrés !"
        body = f"Bonjour {nom},\n\nTes pronostics pour le Mondial 2026 ont bien été validés !\n\nN'oublie pas de rejoindre le groupe WhatsApp pour suivre la compétition : {LIEN_WHATSAPP}\n\nBonne chance ! 🍀"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, destinataire, msg.as_string())
        server.quit()
    except Exception as e:
        st.error(f"Erreur d'envoi d'email : {e}")

def sauvegarder_tout(nom_prenom, email, liste_pronos):
    sheet = connect_to_gsheets()
    if sheet is None: return
    lignes_a_ajouter = []
    for (match_id, pa, pb) in liste_pronos:
        lignes_a_ajouter.append([nom_prenom, email, match_id, pa, pb])
    sheet.append_rows(lignes_a_ajouter)
    envoyer_confirmation(email, nom_prenom)
    charger_donnees.clear()

def calculer_points(prono_a, prono_b, reel_a, reel_b):
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
                            pts += calculer_points(pari.iloc[0]['Prono_A'], pari.iloc[0]['Prono_B'], m['scA'], m['scB'])
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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📝 Pronostics", "📢 Résultats & Calendrier", "📜 Règlement", "📊 Classement", "🌍 Groupes", "👀 Mes Paris"])

with tab1:
    if PRONOS_OUVERTS:
        st.write("### 📅 Le Calendrier")
        try:
            if "google_ok" not in st.session_state:
                connect_to_gsheets()
                st.session_state["google_ok"] = True
        except Exception as e:
            st.error(f"⚠️ Erreur: {e}")
        
        df_stats = charger_donnees()

        with st.form("grille_pronos"):
            col_p, col_e = st.columns(2)
            nom_prenom = col_p.text_input("Ton Nom et Prénom (Obligatoire) :")
            email = col_e.text_input("Ton Email (Pour les résultats) :")

            saisies = {}
            MATCHS.sort(key=lambda x: x['date'])
            dates_uniques = sorted(list(set(m['date'] for m in MATCHS)))
            
            def formater_date(d_str):
                obj = datetime.strptime(d_str, "%Y-%m-%d")
                jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
                mois = ["Jan", "Fév", "Mars", "Avril", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
                return f"{jours[obj.weekday()]} {obj.day} {mois[obj.month-1]}"

            for d in dates_uniques:
                st.markdown(f"### 🗓️ {formater_date(d)}")
                matchs_du_jour = [m for m in MATCHS if m['date'] == d]
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
            valider = st.form_submit_button("Valider et Enregistrer", use_container_width=True)
        
        if valider:
            if not nom_prenom or not email:
                st.error("⚠️ Il faut ton Nom/Prénom ET un email !")
            else:
                df = charger_donnees()
                col_nom = "Nom et Prénom" if "Nom et Prénom" in df.columns else "Pseudo"
                noms_existants = []
                if not df.empty and col_nom in df.columns:
                    noms_existants = df[col_nom].astype(str).values 
                
                if nom_prenom in noms_existants:
                    st.warning(f"Attention, {nom_prenom} a déjà joué ! Modifie le nom si c'est un homonyme.")
                else:
                    with st.spinner("Envoi..."):
                        liste_a_envoyer = []
                        for mid, (sa, sb) in saisies.items():
                            liste_a_envoyer.append((mid, sa, sb))
                        sauvegarder_tout(nom_prenom, email, liste_a_envoyer) 
                    st.success(f"✅ C'est enregistré {nom_prenom} !")
                    st.markdown("---")
                    st.success("📲 **REJOINS LE GROUPE WHATSAPP MAINTENANT !**")
                    st.markdown("Clique ci-dessous pour être au courant de tout :")
                    st.link_button("Rejoindre le groupe WhatsApp ⚽", LIEN_WHATSAPP)
                    st.balloons()
    else:
        st.error("⛔️ Les pronostics sont fermés ! La compétition a commencé.")
        st.info("Tu peux toujours consulter ton classement et les résultats dans les autres onglets.")

with tab2:
    st.header("📢 Résultats & Calendrier")
    dates_uniques = sorted(list(set(m['date'] for m in MATCHS)))
    for d in dates_uniques:
        st.markdown(f"##### 🗓️ {formater_date(d)}")
        matchs_du_jour = [m for m in MATCHS if m['date'] == d]
        cols = st.columns(2)
        for i, m in enumerate(matchs_du_jour):
            with cols[i % 2]:
                with st.container(border=True):
                    if m['scA'] is not None and m['scB'] is not None:
                        st.markdown(f"### {m['eqA']} **{m['scA']} - {m['scB']}** {m['eqB']}")
                        st.caption("✅ Terminé")
                    else:
                        st.write(f"**{m['eqA']}** vs **{m['eqB']}**")
                        st.caption(f"🕒 {m['heure']} - {m['groupe']}")

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
    
    ---
    ### 🏆 Répartition des Gains
    La somme totale des participations sera redistribuée aux trois meilleurs pronostiqueurs selon la clé de répartition suivante :
    * 🥇 **1ère place** : 60 % de la cagnotte totale.
    * 🥈 **2ème place** : 30 % de la cagnotte totale.
    * 🥉 **3ème place** : 10 % de la cagnotte totale.

    En cas d'égalité, les gains du rang concerné seront partagés équitablement entre les ex-aequo.
    
    ---
    ### ⚠️ Autres règles
    * **IMPORTANT :** La totalité de la grille (tous les matchs) doit être remplie et validée **impérativement avant le coup d'envoi du premier match** de la Coupe du Monde. Toute grille incomplète ou en retard ne sera pas prise en compte.
    * En cas d'égalité de points à la fin, le nombre de "Scores Exacts" départagera les joueurs.
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
                            pts += calculer_points(pari.iloc[0]['Prono_A'], pari.iloc[0]['Prono_B'], m['scA'], m['scB'])
                        except: pass
                scores_joueurs[j] = pts
            
            if scores_joueurs:
                df_rank = pd.DataFrame(list(scores_joueurs.items()), columns=["Joueur", "Points"])
                df_rank = df_rank.sort_values(by="Points", ascending=False).reset_index(drop=True)
                df_rank.index += 1
                st.dataframe(df_rank, use_container_width=True, height=600)

with tab5:
    st.header("🌍 Classement des Groupes")
    groupes = sorted(list(set(m['groupe'] for m in MATCHS)))
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
                        st.write(f"{m['eqA']} **{m['scA']}-{m['scB']}** {m['eqB']}")
                    else:
                        st.write(f"{m['eqA']} vs {m['eqB']}")

with tab6:
    st.header("🔍 Retrouver mes pronostics")
    nom_search = st.text_input("Entre ton Nom exact :")
    if nom_search:
        df = charger_donnees()
        col_nom = "Nom et Prénom" if "Nom et Prénom" in df.columns else "Pseudo"
        if not df.empty and col_nom in df.columns and nom_search in df[col_nom].values:
            mes_pronos = df[df[col_nom] == nom_search]
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
                st.warning("Rien trouvé.")
        else:
            st.info("Nom inconnu.")
