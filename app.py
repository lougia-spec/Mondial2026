import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
st.set_page_config(page_title="Mondial 2026", page_icon="⚽", layout="centered")

# --- CONNEXION GOOGLE SHEETS (VERSION FACILE) ---
# --- CONNEXION GOOGLE SHEETS ---
def connect_to_gsheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # On récupère le fichier secret
    json_info = st.secrets["gcp_service_account"]["json_file"]
    creds_dict = json.loads(json_info)
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # MODIFICATION ICI : Remplace la clé ci-dessous par LA TIENNE que tu as copiée
    # Exemple : client.open_by_key("1BxiM-AbcDeFgHiJkLmNoPqRsTvUwXYz").sheet1
    sheet = client.open_by_key("1TqmQusKk29ii1A1ZRNHDxvJLlv13I1dyXKrhvY-V29Q").sheet1
    
    return sheet

# --- LISTE DES MATCHS ---
MATCHS = [
    {"id": 1, "groupe": "Groupe A", "eqA": "🇲🇽 Mexique", "eqB": "🇿🇦 Afrique Sud", "scA": None, "scB": None},
    {"id": 2, "groupe": "Groupe A", "eqA": "🇰🇷 Corée du Sud", "eqB": "🏳️ Barragiste D", "scA": None, "scB": None},
    {"id": 3, "groupe": "Groupe A", "eqA": "🇲🇽 Mexique", "eqB": "🇰🇷 Corée du Sud", "scA": None, "scB": None},
    {"id": 4, "groupe": "Groupe A", "eqA": "🇿🇦 Afrique Sud", "eqB": "🏳️ Barragiste D", "scA": None, "scB": None},
    {"id": 5, "groupe": "Groupe A", "eqA": "🏳️ Barragiste D", "eqB": "🇲🇽 Mexique", "scA": None, "scB": None},
    {"id": 6, "groupe": "Groupe A", "eqA": "🇿🇦 Afrique Sud", "eqB": "🇰🇷 Corée du Sud", "scA": None, "scB": None},
    {"id": 7, "groupe": "Groupe B", "eqA": "🇨🇦 Canada", "eqB": "🏳️ Barragiste A", "scA": None, "scB": None},
    {"id": 8, "groupe": "Groupe B", "eqA": "🇶🇦 Qatar", "eqB": "🇨🇭 Suisse", "scA": None, "scB": None},
    {"id": 9, "groupe": "Groupe B", "eqA": "🇨🇦 Canada", "eqB": "🇶🇦 Qatar", "scA": None, "scB": None},
    {"id": 10, "groupe": "Groupe B", "eqA": "🏳️ Barragiste A", "eqB": "🇨🇭 Suisse", "scA": None, "scB": None},
    {"id": 11, "groupe": "Groupe B", "eqA": "🇨🇭 Suisse", "eqB": "🇨🇦 Canada", "scA": None, "scB": None},
    {"id": 12, "groupe": "Groupe B", "eqA": "🏳️ Barragiste A", "eqB": "🇶🇦 Qatar", "scA": None, "scB": None},
    {"id": 13, "groupe": "Groupe C", "eqA": "🇧🇷 Brésil", "eqB": "🇲🇦 Maroc", "scA": None, "scB": None},
    {"id": 14, "groupe": "Groupe C", "eqA": "🇭🇹 Haïti", "eqB": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "scA": None, "scB": None},
    {"id": 15, "groupe": "Groupe C", "eqA": "🇧🇷 Brésil", "eqB": "🇭🇹 Haïti", "scA": None, "scB": None},
    {"id": 16, "groupe": "Groupe C", "eqA": "🇲🇦 Maroc", "eqB": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "scA": None, "scB": None},
    {"id": 17, "groupe": "Groupe C", "eqA": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Écosse", "eqB": "🇧🇷 Brésil", "scA": None, "scB": None},
    {"id": 18, "groupe": "Groupe C", "eqA": "🇲🇦 Maroc", "eqB": "🇭🇹 Haïti", "scA": None, "scB": None},
    {"id": 19, "groupe": "Groupe D", "eqA": "🇺🇸 USA", "eqB": "🇵🇾 Paraguay", "scA": None, "scB": None},
    {"id": 20, "groupe": "Groupe D", "eqA": "🇦🇺 Australie", "eqB": "🏳️ Barragiste C", "scA": None, "scB": None},
    {"id": 21, "groupe": "Groupe D", "eqA": "🇺🇸 USA", "eqB": "🇦🇺 Australie", "scA": None, "scB": None},
    {"id": 22, "groupe": "Groupe D", "eqA": "🇵🇾 Paraguay", "eqB": "🏳️ Barragiste C", "scA": None, "scB": None},
    {"id": 23, "groupe": "Groupe D", "eqA": "🏳️ Barragiste C", "eqB": "🇺🇸 USA", "scA": None, "scB": None},
    {"id": 24, "groupe": "Groupe D", "eqA": "🇵🇾 Paraguay", "eqB": "🇦🇺 Australie", "scA": None, "scB": None},
    {"id": 25, "groupe": "Groupe E", "eqA": "🇩🇪 Allemagne", "eqB": "🇨🇼 Curaçao", "scA": None, "scB": None},
    {"id": 26, "groupe": "Groupe E", "eqA": "🇨🇮 Côte d'Ivoire", "eqB": "🇪🇨 Équateur", "scA": None, "scB": None},
    {"id": 27, "groupe": "Groupe E", "eqA": "🇩🇪 Allemagne", "eqB": "🇨🇮 Côte d'Ivoire", "scA": None, "scB": None},
    {"id": 28, "groupe": "Groupe E", "eqA": "🇨🇼 Curaçao", "eqB": "🇪🇨 Équateur", "scA": None, "scB": None},
    {"id": 29, "groupe": "Groupe E", "eqA": "🇪🇨 Équateur", "eqB": "🇩🇪 Allemagne", "scA": None, "scB": None},
    {"id": 30, "groupe": "Groupe E", "eqA": "🇨🇼 Curaçao", "eqB": "🇨🇮 Côte d'Ivoire", "scA": None, "scB": None},
    {"id": 31, "groupe": "Groupe F", "eqA": "🇳🇱 Pays-Bas", "eqB": "🇯🇵 Japon", "scA": None, "scB": None},
    {"id": 32, "groupe": "Groupe F", "eqA": "🏳️ Barragiste B", "eqB": "🇹🇳 Tunisie", "scA": None, "scB": None},
    {"id": 33, "groupe": "Groupe F", "eqA": "🇳🇱 Pays-Bas", "eqB": "🏳️ Barragiste B", "scA": None, "scB": None},
    {"id": 34, "groupe": "Groupe F", "eqA": "🇯🇵 Japon", "eqB": "🇹🇳 Tunisie", "scA": None, "scB": None},
    {"id": 35, "groupe": "Groupe F", "eqA": "🇹🇳 Tunisie", "eqB": "🇳🇱 Pays-Bas", "scA": None, "scB": None},
    {"id": 36, "groupe": "Groupe F", "eqA": "🇯🇵 Japon", "eqB": "🏳️ Barragiste B", "scA": None, "scB": None},
    {"id": 37, "groupe": "Groupe G", "eqA": "🇧🇪 Belgique", "eqB": "🇪🇬 Égypte", "scA": None, "scB": None},
    {"id": 38, "groupe": "Groupe G", "eqA": "🇮🇷 Iran", "eqB": "🇳🇿 Nv-Zélande", "scA": None, "scB": None},
    {"id": 39, "groupe": "Groupe G", "eqA": "🇧🇪 Belgique", "eqB": "🇮🇷 Iran", "scA": None, "scB": None},
    {"id": 40, "groupe": "Groupe G", "eqA": "🇪🇬 Égypte", "eqB": "🇳🇿 Nv-Zélande", "scA": None, "scB": None},
    {"id": 41, "groupe": "Groupe G", "eqA": "🇳🇿 Nv-Zélande", "eqB": "🇧🇪 Belgique", "scA": None, "scB": None},
    {"id": 42, "groupe": "Groupe G", "eqA": "🇪🇬 Égypte", "eqB": "🇮🇷 Iran", "scA": None, "scB": None},
    {"id": 43, "groupe": "Groupe H", "eqA": "🇪🇸 Espagne", "eqB": "🇨🇻 Cap-Vert", "scA": None, "scB": None},
    {"id": 44, "groupe": "Groupe H", "eqA": "🇸🇦 Arabie Saoudite", "eqB": "🇺🇾 Uruguay", "scA": None, "scB": None},
    {"id": 45, "groupe": "Groupe H", "eqA": "🇪🇸 Espagne", "eqB": "🇸🇦 Arabie Saoudite", "scA": None, "scB": None},
    {"id": 46, "groupe": "Groupe H", "eqA": "🇨🇻 Cap-Vert", "eqB": "🇺🇾 Uruguay", "scA": None, "scB": None},
    {"id": 47, "groupe": "Groupe H", "eqA": "🇺🇾 Uruguay", "eqB": "🇪🇸 Espagne", "scA": None, "scB": None},
    {"id": 48, "groupe": "Groupe H", "eqA": "🇨🇻 Cap-Vert", "eqB": "🇸🇦 Arabie Saoudite", "scA": None, "scB": None},
    {"id": 49, "groupe": "Groupe I", "eqA": "🇫🇷 France", "eqB": "🇸🇳 Sénégal", "scA": None, "scB": None},
    {"id": 50, "groupe": "Groupe I", "eqA": "🏳️ Barragiste 2", "eqB": "🇳🇴 Norvège", "scA": None, "scB": None},
    {"id": 51, "groupe": "Groupe I", "eqA": "🇫🇷 France", "eqB": "🏳️ Barragiste 2", "scA": None, "scB": None},
    {"id": 52, "groupe": "Groupe I", "eqA": "🇸🇳 Sénégal", "eqB": "🇳🇴 Norvège", "scA": None, "scB": None},
    {"id": 53, "groupe": "Groupe I", "eqA": "🇳🇴 Norvège", "eqB": "🇫🇷 France", "scA": None, "scB": None},
    {"id": 54, "groupe": "Groupe I", "eqA": "🇸🇳 Sénégal", "eqB": "🏳️ Barragiste 2", "scA": None, "scB": None},
    {"id": 55, "groupe": "Groupe J", "eqA": "🇦🇷 Argentine", "eqB": "🇩🇿 Algérie", "scA": None, "scB": None},
    {"id": 56, "groupe": "Groupe J", "eqA": "🇦🇹 Autriche", "eqB": "🇯🇴 Jordanie", "scA": None, "scB": None},
    {"id": 57, "groupe": "Groupe J", "eqA": "🇦🇷 Argentine", "eqB": "🇦🇹 Autriche", "scA": None, "scB": None},
    {"id": 58, "groupe": "Groupe J", "eqA": "🇩🇿 Algérie", "eqB": "🇯🇴 Jordanie", "scA": None, "scB": None},
    {"id": 59, "groupe": "Groupe J", "eqA": "🇯🇴 Jordanie", "eqB": "🇦🇷 Argentine", "scA": None, "scB": None},
    {"id": 60, "groupe": "Groupe J", "eqA": "🇩🇿 Algérie", "eqB": "🇦🇹 Autriche", "scA": None, "scB": None},
    {"id": 61, "groupe": "Groupe K", "eqA": "🇵🇹 Portugal", "eqB": "🏳️ Barragiste 1", "scA": None, "scB": None},
    {"id": 62, "groupe": "Groupe K", "eqA": "🇺🇿 Ouzbékistan", "eqB": "🇨🇴 Colombie", "scA": None, "scB": None},
    {"id": 63, "groupe": "Groupe K", "eqA": "🇵🇹 Portugal", "eqB": "🇺🇿 Ouzbékistan", "scA": None, "scB": None},
    {"id": 64, "groupe": "Groupe K", "eqA": "🏳️ Barragiste 1", "eqB": "🇨🇴 Colombie", "scA": None, "scB": None},
    {"id": 65, "groupe": "Groupe K", "eqA": "🇨🇴 Colombie", "eqB": "🇵🇹 Portugal", "scA": None, "scB": None},
    {"id": 66, "groupe": "Groupe K", "eqA": "🏳️ Barragiste 1", "eqB": "🇺🇿 Ouzbékistan", "scA": None, "scB": None},
    {"id": 67, "groupe": "Groupe L", "eqA": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "eqB": "🇭🇷 Croatie", "scA": None, "scB": None},
    {"id": 68, "groupe": "Groupe L", "eqA": "🇬🇭 Ghana", "eqB": "🇵🇦 Panama", "scA": None, "scB": None},
    {"id": 69, "groupe": "Groupe L", "eqA": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "eqB": "🇬🇭 Ghana", "scA": None, "scB": None},
    {"id": 70, "groupe": "Groupe L", "eqA": "🇭🇷 Croatie", "eqB": "🇵🇦 Panama", "scA": None, "scB": None},
    {"id": 71, "groupe": "Groupe L", "eqA": "🇵🇦 Panama", "eqB": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Angleterre", "scA": None, "scB": None},
    {"id": 72, "groupe": "Groupe L", "eqA": "🇭🇷 Croatie", "eqB": "🇬🇭 Ghana", "scA": None, "scB": None},
]

# --- FONCTIONS ---
def charger_donnees():
    try:
        sheet = connect_to_gsheets()
        data = sheet.get_all_records()
        if not data:
            return pd.DataFrame(columns=["Pseudo", "Match_ID", "Prono_A", "Prono_B"])
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame(columns=["Pseudo", "Match_ID", "Prono_A", "Prono_B"])

def sauvegarder_prono(pseudo, match_id, pa, pb):
    sheet = connect_to_gsheets()
    sheet.append_row([pseudo, match_id, pa, pb])

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

# --- INTERFACE ---
st.title("🏆 Coupe du Monde 2026")
tab1, tab2, tab3 = st.tabs(["📝 Pronostics", "📊 Classement", "🌍 Les Groupes"])

with tab1:
    st.write("### Remplis ta grille")
    try:
        if "google_ok" not in st.session_state:
            connect_to_gsheets()
            st.session_state["google_ok"] = True
    except Exception as e:
        st.error(f"⚠️ Erreur de connexion Google. Vérifie tes 'Secrets' dans Streamlit Cloud. Détail: {e}")
    
    with st.form("grille_pronos"):
        pseudo = st.text_input("Ton Pseudo :")
        saisies = {}
        groupes_liste = sorted(list(set(m['groupe'] for m in MATCHS)))
        for grp in groupes_liste:
            with st.expander(grp, expanded=False): 
                matchs_grp = [m for m in MATCHS if m['groupe'] == grp]
                for m in matchs_grp:
                    st.markdown(f"**{m['eqA']}** vs **{m['eqB']}**")
                    c1, c2 = st.columns(2)
                    pa = c1.number_input(f"Buts {m['eqA']}", 0, 10, key=f"A_{m['id']}")
                    pb = c2.number_input(f"Buts {m['eqB']}", 0, 10, key=f"B_{m['id']}")
                    saisies[m['id']] = (pa, pb)
                    st.divider()
        valider = st.form_submit_button("Valider et Enregistrer")
    
    if valider:
        if not pseudo:
            st.error("⚠️ Il faut un pseudo !")
        else:
            df = charger_donnees()
            pseudos_existants = df['Pseudo'].astype(str).values if not df.empty else []
            
            if pseudo in pseudos_existants:
                st.warning(f"Le pseudo {pseudo} a déjà joué ! Modifie-le ou contacte l'admin.")
            else:
                with st.spinner("Sauvegarde dans le Cloud en cours..."):
                    for mid, (sa, sb) in saisies.items():
                        sauvegarder_prono(pseudo, mid, sa, sb)
                st.success(f"✅ C'est enregistré {pseudo} ! Tes amis peuvent voir ton score.")
                st.balloons()

with tab2:
    st.write("### 🥇 Le Podium")
    df = charger_donnees()
    if df.empty:
        st.info("Personne n'a encore parié.")
    else:
        scores_joueurs = {}
        joueurs = df['Pseudo'].unique()
        for j in joueurs:
            pts = 0
            pronos_j = df[df.Pseudo == j]
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
            st.dataframe(df_rank, use_container_width=True)

with tab3:
    st.header("🌍 Les Équipes par Groupe")
    groupes = sorted(list(set(m['groupe'] for m in MATCHS)))
    for grp in groupes:
        with st.expander(grp, expanded=False):
            equipes_du_groupe = set()
            matchs_du_groupe = [m for m in MATCHS if m['groupe'] == grp]
            for m in matchs_du_groupe:
                equipes_du_groupe.add(m['eqA'])
                equipes_du_groupe.add(m['eqB'])
            for equipe in sorted(list(equipes_du_groupe)):
                st.write(f"🛡️ **{equipe}**")
