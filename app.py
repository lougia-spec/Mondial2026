import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Mondial 2026",
    page_icon="⚽",
    layout="wide"
)

# 👇 METTRE À JOUR CETTE DATE RÉGULIÈREMENT
DERNIERE_MAJ = "08/12/2025 à 16:00"

# --- CONNEXION GOOGLE SHEETS ---
def connect_to_gsheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        json_info = st.secrets["gcp_service_account"]["json_file"]
        creds_dict = json.loads(json_info)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # Ta clé spécifique
        sheet = client.open_by_key("1TqmQusKk29ii1A1ZRNHDxvJLlv13I1dyXKrhvY-V29Q").sheet1
        return sheet
    except Exception as e:
        return None

# --- LISTE DES MATCHS ---
MATCHS = [
    # --- JEUDI 11 JUIN ---
    {"id": 1, "date": "2026-06-11", "heure": "21h", "groupe": "Groupe A", "eqA": "🇲🇽 Mexique", "eqB": "🇿🇦 Afrique Sud", "scA": 2, "scB": 0},
    
    # --- VENDREDI 12 JUIN ---
    {"id": 2, "date": "2026-06-12", "heure": "04h", "groupe": "Groupe A", "eqA": "🇰🇷 Corée du Sud", "eqB": "🏳️ Barragiste D", "scA": None, "scB": None},
    {"id": 7, "date": "2026-06-12", "heure": "21h", "groupe": "Groupe B", "eqA": "🇨🇦 Canada", "eqB": "🏳️ Barragiste A", "scA": None, "scB": None},

    # --- SAMEDI 13 JUIN ---
    {"id": 19, "date": "2026-06-13", "heure": "03h", "groupe": "Groupe D", "eqA": "🇺🇸 USA", "eqB": "🇵🇾 Paraguay", "scA": None, "scB": None},
    {"id": 20, "date": "2026-06-13", "heure": "06h", "groupe": "Groupe D", "eqA": "🇦🇺 Australie", "eqB": "🏳️ Barragiste C", "scA": None, "scB": None},
    {"id": 8, "date": "2026-06-13", "heure": "21h", "groupe": "Groupe B", "eqA": "🇶🇦 Qatar", "eqB": "🇨🇭 Suisse", "scA": None, "scB": None},

    # --- DIMANCHE 14 JUIN ---
    {"id": 37, "date": "2026-06-14", "heure": "21h", "groupe": "Groupe G", "eqA": "🇧🇪 Belgique", "eqB": "🇪🇬 Égypte", "scA": None, "scB": None},
    {"id": 31, "date": "2026-06-14", "heure": "22h", "groupe": "Groupe F", "eqA": "🇳🇱 Pays-Bas", "eqB": "🇯🇵 Japon", "scA": None, "scB": None},
    {"id": 14, "date": "2026-06-14", "heure": "03h", "groupe": "Groupe C", "eqA": "🇭🇹 Haïti", "eqB": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "scA": None, "scB": None},

    # --- LUNDI 15 JUIN ---
    {"id": 13, "date": "2026-06-15", "heure": "00h", "groupe": "Groupe C", "eqA": "🇧🇷 Brésil", "eqB": "🇲🇦 Maroc", "scA": None, "scB": None},
    {"id": 38, "date": "2026-06-15", "heure": "03h", "groupe": "Groupe G", "eqA": "🇮🇷 Iran", "eqB": "🇳🇿 Nv-Zélande", "scA": None, "scB": None},
    {"id": 25, "date": "2026-06-15", "heure": "19h", "groupe": "Groupe E", "eqA": "🇩🇪 Allemagne", "eqB": "🇨🇼 Curaçao", "scA": None, "scB": None},
    {"id": 26, "date": "2026-06-15", "heure": "01h", "groupe": "Groupe E", "eqA": "🇨🇮 Côte d'Ivoire", "eqB": "🇪🇨 Équateur", "scA": None, "scB": None},

    # --- MARDI 16 JUIN ---
    {"id": 55, "date": "2026-06-16", "heure": "18h", "groupe": "Groupe J", "eqA": "🇦🇷 Argentine", "eqB": "🇩🇿 Algérie", "scA": None, "scB": None},
    {"id": 56, "date": "2026-06-16", "heure": "06h", "groupe": "Groupe J", "eqA": "🇦🇹 Autriche", "eqB": "🇯🇴 Jordanie", "scA": None, "scB": None},
    {"id": 61, "date": "2026-06-16", "heure": "19h", "groupe": "Groupe K", "eqA": "🇵🇹 Portugal", "eqB": "🏳️ Barragiste 1", "scA": None, "scB": None},

    # --- MERCREDI 17 JUIN ---
    {"id": 62, "date": "2026-06-17", "heure": "04h", "groupe": "Groupe K", "eqA": "🇺🇿 Ouzbékistan", "eqB": "🇨🇴 Colombie", "scA": None, "scB": None},
    {"id": 67, "date": "2026-06-17", "heure": "22h", "groupe": "Groupe L", "eqA": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "eqB": "🇭🇷 Croatie", "scA": None, "scB": None},
    {"id": 68, "date": "2026-06-17", "heure": "01h", "groupe": "Groupe L", "eqA": "🇬🇭 Ghana", "eqB": "🇵🇦 Panama", "scA": None, "scB": None},
    {"id": 10, "date": "2026-06-17", "heure": "21h", "groupe": "Groupe B", "eqA": "🏳️ Barragiste A", "eqB": "🇨🇭 Suisse", "scA": None, "scB": None},

    # --- JEUDI 18 JUIN ---
    {"id": 3, "date": "2026-06-18", "heure": "03h", "groupe": "Groupe A", "eqA": "🇲🇽 Mexique", "eqB": "🇰🇷 Corée du Sud", "scA": None, "scB": None},
    {"id": 43, "date": "2026-06-18", "heure": "18h", "groupe": "Groupe H", "eqA": "🇪🇸 Espagne", "eqB": "🇨🇻 Cap-Vert", "scA": None, "scB": None},
    {"id": 44, "date": "2026-06-18", "heure": "00h", "groupe": "Groupe H", "eqA": "🇸🇦 Arabie Saoudite", "eqB": "🇺🇾 Uruguay", "scA": None, "scB": None},

    # --- VENDREDI 19 JUIN ---
    {"id": 4, "date": "2026-06-19", "heure": "06h", "groupe": "Groupe A", "eqA": "🇿🇦 Afrique Sud", "eqB": "🏳️ Barragiste D", "scA": None, "scB": None},
    {"id": 9, "date": "2026-06-19", "heure": "00h", "groupe": "Groupe B", "eqA": "🇨🇦 Canada", "eqB": "🇶🇦 Qatar", "scA": None, "scB": None},
    {"id": 21, "date": "2026-06-19", "heure": "21h", "groupe": "Groupe D", "eqA": "🇺🇸 USA", "eqB": "🇦🇺 Australie", "scA": None, "scB": None},
    {"id": 49, "date": "2026-06-19", "heure": "21h", "groupe": "Groupe I", "eqA": "🇫🇷 France", "eqB": "🇸🇳 Sénégal", "scA": None, "scB": None},
    
    # --- SAMEDI 20 JUIN ---
    {"id": 15, "date": "2026-06-20", "heure": "00h", "groupe": "Groupe C", "eqA": "🇧🇷 Brésil", "eqB": "🇭🇹 Haïti", "scA": None, "scB": None},
    {"id": 16, "date": "2026-06-20", "heure": "00h", "groupe": "Groupe C", "eqA": "🇲🇦 Maroc", "eqB": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "scA": None, "scB": None},
    {"id": 27, "date": "2026-06-20", "heure": "19h", "groupe": "Groupe E", "eqA": "🇩🇪 Allemagne", "eqB": "🇨🇮 Côte d'Ivoire", "scA": None, "scB": None},
    {"id": 39, "date": "2026-06-20", "heure": "21h", "groupe": "Groupe G", "eqA": "🇧🇪 Belgique", "eqB": "🇮🇷 Iran", "scA": None, "scB": None},

    # --- DIMANCHE 21 JUIN ---
    {"id": 28, "date": "2026-06-21", "heure": "02h", "groupe": "Groupe E", "eqA": "🇨🇼 Curaçao", "eqB": "🇪🇨 Équateur", "scA": None, "scB": None},
    {"id": 32, "date": "2026-06-21", "heure": "04h", "groupe": "Groupe F", "eqA": "🏳️ Barragiste B", "eqB": "🇹🇳 Tunisie", "scA": None, "scB": None},
    {"id": 33, "date": "2026-06-21", "heure": "21h", "groupe": "Groupe F", "eqA": "🇳🇱 Pays-Bas", "eqB": "🏳️ Barragiste B", "scA": None, "scB": None},
    {"id": 50, "date": "2026-06-21", "heure": "03h", "groupe": "Groupe I", "eqA": "🏳️ Barragiste 2", "eqB": "🇳🇴 Norvège", "scA": None, "scB": None},

    # --- LUNDI 22 JUIN ---
    {"id": 22, "date": "2026-06-22", "heure": "03h", "groupe": "Groupe D", "eqA": "🇵🇾 Paraguay", "eqB": "🏳️ Barragiste C", "scA": None, "scB": None},
    {"id": 45, "date": "2026-06-22", "heure": "18h", "groupe": "Groupe H", "eqA": "🇪🇸 Espagne", "eqB": "🇸🇦 Arabie Saoudite", "scA": None, "scB": None},
    {"id": 40, "date": "2026-06-22", "heure": "03h", "groupe": "Groupe G", "eqA": "🇪🇬 Égypte", "eqB": "🇳🇿 Nv-Zélande", "scA": None, "scB": None},
    {"id": 57, "date": "2026-06-22", "heure": "18h", "groupe": "Groupe J", "eqA": "🇦🇷 Argentine", "eqB": "🇦🇹 Autriche", "scA": None, "scB": None},

    # --- MARDI 23 JUIN ---
    {"id": 58, "date": "2026-06-23", "heure": "05h", "groupe": "Groupe J", "eqA": "🇩🇿 Algérie", "eqB": "🇯🇴 Jordanie", "scA": None, "scB": None},
    {"id": 63, "date": "2026-06-23", "heure": "19h", "groupe": "Groupe K", "eqA": "🇵🇹 Portugal", "eqB": "🇺🇿 Ouzbékistan", "scA": None, "scB": None},
    {"id": 69, "date": "2026-06-23", "heure": "22h", "groupe": "Groupe L", "eqA": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "eqB": "🇬🇭 Ghana", "scA": None, "scB": None},
    {"id": 52, "date": "2026-06-23", "heure": "23h", "groupe": "Groupe I", "eqA": "🇸🇳 Sénégal", "eqB": "🇳🇴 Norvège", "scA": None, "scB": None},

    # --- MERCREDI 24 JUIN ---
    {"id": 6, "date": "2026-06-24", "heure": "03h", "groupe": "Groupe A", "eqA": "🇿🇦 Afrique Sud", "eqB": "🇰🇷 Corée du Sud", "scA": None, "scB": None},
    {"id": 11, "date": "2026-06-24", "heure": "21h", "groupe": "Groupe B", "eqA": "🇨🇭 Suisse", "eqB": "🇨🇦 Canada", "scA": None, "scB": None},
    {"id": 12, "date": "2026-06-24", "heure": "21h", "groupe": "Groupe B", "eqA": "🏳️ Barragiste A", "eqB": "🇶🇦 Qatar", "scA": None, "scB": None},
    {"id": 64, "date": "2026-06-24", "heure": "04h", "groupe": "Groupe K", "eqA": "🏳️ Barragiste 1", "eqB": "🇨🇴 Colombie", "scA": None, "scB": None},

    # --- JEUDI 25 JUIN ---
    {"id": 73, "date": "2026-06-25", "heure": "03h", "groupe": "Groupe A", "eqA": "🏳️ Barragiste D", "eqB": "🇲🇽 Mexique", "scA": None, "scB": None},
    {"id": 17, "date": "2026-06-25", "heure": "00h", "groupe": "Groupe C", "eqA": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "eqB": "🇧🇷 Brésil", "scA": None, "scB": None},
    {"id": 18, "date": "2026-06-25", "heure": "00h", "groupe": "Groupe C", "eqA": "🇲🇦 Maroc", "eqB": "🇭🇹 Haïti", "scA": None, "scB": None},
    {"id": 23, "date": "2026-06-25", "heure": "21h", "groupe": "Groupe D", "eqA": "🏳️ Barragiste C", "eqB": "🇺🇸 USA", "scA": None, "scB": None},
    {"id": 24, "date": "2026-06-25", "heure": "21h", "groupe": "Groupe D", "eqA": "🇵🇾 Paraguay", "eqB": "🇦🇺 Australie", "scA": None, "scB": None},
    
    # --- VENDREDI 26 JUIN ---
    {"id": 29, "date": "2026-06-26", "heure": "18h", "groupe": "Groupe E", "eqA": "🇪🇨 Équateur", "eqB": "🇩🇪 Allemagne", "scA": None, "scB": None},
    {"id": 30, "date": "2026-06-26", "heure": "18h", "groupe": "Groupe E", "eqA": "🇨🇼 Curaçao", "eqB": "🇨🇮 Côte d'Ivoire", "scA": None, "scB": None},
    {"id": 34, "date": "2026-06-26", "heure": "01h", "groupe": "Groupe F", "eqA": "🇯🇵 Japon", "eqB": "🇹🇳 Tunisie", "scA": None, "scB": None},
    {"id": 35, "date": "2026-06-26", "heure": "01h", "groupe": "Groupe F", "eqA": "🇹🇳 Tunisie", "eqB": "🇳🇱 Pays-Bas", "scA": None, "scB": None},
    {"id": 36, "date": "2026-06-26", "heure": "01h", "groupe": "Groupe F", "eqA": "🇯🇵 Japon", "eqB": "🏳️ Barragiste B", "scA": None, "scB": None},
    
    # --- SAMEDI 27 JUIN ---
    {"id": 41, "date": "2026-06-27", "heure": "05h", "groupe": "Groupe G", "eqA": "🇳🇿 Nv-Zélande", "eqB": "🇧🇪 Belgique", "scA": None, "scB": None},
    {"id": 42, "date": "2026-06-27", "heure": "05h", "groupe": "Groupe G", "eqA": "🇪🇬 Égypte", "eqB": "🇮🇷 Iran", "scA": None, "scB": None},
    {"id": 46, "date": "2026-06-27", "heure": "02h", "groupe": "Groupe H", "eqA": "🇨🇻 Cap-Vert", "eqB": "🇺🇾 Uruguay", "scA": None, "scB": None},
    {"id": 47, "date": "2026-06-27", "heure": "02h", "groupe": "Groupe H", "eqA": "🇺🇾 Uruguay", "eqB": "🇪🇸 Espagne", "scA": None, "scB": None},
    {"id": 51, "date": "2026-06-27", "heure": "21h", "groupe": "Groupe I", "eqA": "🇫🇷 France", "eqB": "🏳️ Barragiste 2", "scA": None, "scB": None},
    {"id": 53, "date": "2026-06-27", "heure": "21h", "groupe": "Groupe I", "eqA": "🇳🇴 Norvège", "eqB": "🇫🇷 France", "scA": None, "scB": None},

    # --- DIMANCHE 28 JUIN ---
    {"id": 59, "date": "2026-06-28", "heure": "04h", "groupe": "Groupe J", "eqA": "🇯🇴 Jordanie", "eqB": "🇦🇷 Argentine", "scA": None, "scB": None},
    {"id": 60, "date": "2026-06-28", "heure": "04h", "groupe": "Groupe J", "eqA": "🇩🇿 Algérie", "eqB": "🇦🇹 Autriche", "scA": None, "scB": None},
    {"id": 65, "date": "2026-06-28", "heure": "01h", "groupe": "Groupe K", "eqA": "🇨🇴 Colombie", "eqB": "🇵🇹 Portugal", "scA": None, "scB": None},
    {"id": 66, "date": "2026-06-28", "heure": "01h", "groupe": "Groupe K", "eqA": "🏳️ Barragiste 1", "eqB": "🇺🇿 Ouzbékistan", "scA": None, "scB": None},
    {"id": 71, "date": "2026-06-28", "heure": "23h", "groupe": "Groupe L", "eqA": "🇵🇦 Panama", "eqB": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "scA": None, "scB": None},
    {"id": 72, "date": "2026-06-28", "heure": "23h", "groupe": "Groupe L", "eqA": "🇭🇷 Croatie", "eqB": "🇬🇭 Ghana", "scA": None, "scB": None},
]

# --- FONCTIONS ---
def charger_donnees():
    try:
        sheet = connect_to_gsheets()
        if sheet is None: return pd.DataFrame(columns=["Nom et Prénom", "Email", "Match_ID", "Prono_A", "Prono_B"])
        data = sheet.get_all_records()
        if not data:
            return pd.DataFrame(columns=["Nom et Prénom", "Email", "Match_ID", "Prono_A", "Prono_B"])
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame(columns=["Nom et Prénom", "Email", "Match_ID", "Prono_A", "Prono_B"])

def sauvegarder_tout(nom_prenom, email, liste_pronos):
    sheet = connect_to_gsheets()
    if sheet is None: return
    lignes_a_ajouter = []
    for (match_id, pa, pb) in liste_pronos:
        lignes_a_ajouter.append([nom_prenom, email, match_id, pa, pb])
    sheet.append_rows(lignes_a_ajouter)

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

# --- INTERFACE ---

# 1. Bannière
st.image("https://images.unsplash.com/photo-1522778119026-d647f0565c6a?q=80&w=2070&auto=format&fit=crop", use_container_width=True)

# 2. Barre Latérale
with st.sidebar:
    st.title("⚽ Mondial 2026")
    st.info("Bienvenue sur l'app de pronostics !")
    
    st.markdown("---")
    st.write("### 📜 Les Règles")
    st.success("✅ **1 Point** : Bon vainqueur")
    st.success("🎯 **3 Points** : Score Exact")
    
    st.markdown("---")
    st.write(f"🕒 **Dernière mise à jour :**\n\n`{DERNIERE_MAJ}`")

    st.markdown("---")
    try:
        df_count = charger_donnees()
        nb_joueurs = len(df_count['Nom et Prénom'].unique()) if not df_count.empty else 0
        st.metric("Joueurs inscrits", nb_joueurs)
    except:
        pass


st.title("🏆 Faites vos Jeux !")

tab1, tab2, tab3 = st.tabs(["📝 Pronostics", "📊 Classement", "🌍 Classement des Groupes"])

with tab1:
    st.write("### 📅 Le Calendrier")
    try:
        if "google_ok" not in st.session_state:
            connect_to_gsheets()
            st.session_state["google_ok"] = True
    except Exception as e:
        st.error(f"⚠️ Erreur de connexion Google. Vérifie tes 'Secrets'. Détail: {e}")
    
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
            # On vérifie si ce nom existe déjà
            noms_existants = df['Nom et Prénom'].astype(str).values if not df.empty else []
            if nom_prenom in noms_existants:
                st.warning(f"Attention, {nom_prenom} a déjà joué ! Modifie le nom si c'est un homonyme.")
            else:
                with st.spinner("Envoi de tes pronostics..."):
                    liste_a_envoyer = []
                    for mid, (sa, sb) in saisies.items():
                        liste_a_envoyer.append((mid, sa, sb))
                    sauvegarder_tout(nom_prenom, email, liste_a_envoyer)
                    
                st.success(f"✅ C'est enregistré {nom_prenom} ! On t'enverra les résultats sur {email}.")
                st.balloons()

with tab2:
    st.write("### 🥇 Le Podium")
    df = charger_donnees()
    if df.empty:
        st.info("Personne n'a encore parié.")
    else:
        scores_joueurs = {}
        joueurs = df['Nom et Prénom'].unique()
        for j in joueurs:
            pts = 0
            pronos_j = df[df['Nom et Prénom'] == j]
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
            st.dataframe(df_rank, use_container_width=True, height=500)

with tab3:
    st.header("🌍 Classement des Groupes")
    st.info("Ce classement est calculé automatiquement selon les résultats réels.")
    
    groupes = sorted(list(set(m['groupe'] for m in MATCHS)))
    cols = st.columns(2)
    
    for i, grp in enumerate(groupes):
        with cols[i % 2]: 
            with st.container(border=True):
                st.subheader(grp)
                df_classement = calculer_classement_groupe(grp)
                st.dataframe(df_classement, use_container_width=True)
