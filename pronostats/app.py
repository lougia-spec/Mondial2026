"""PronoStats — pronostics de matchs internationaux par statistiques.

Lancer : streamlit run pronostats/app.py
"""
import pandas as pd
import streamlit as st

from model import DATA_URL, EloPoissonModel, backtest, load_results

st.set_page_config(page_title="PronoStats", page_icon="📊", layout="wide")


@st.cache_data(ttl=6 * 3600, show_spinner="Téléchargement de l'historique des matchs…")
def get_results() -> pd.DataFrame:
    return load_results(DATA_URL)


@st.cache_resource(show_spinner="Calcul des classements Elo…")
def get_model(last_date: str) -> EloPoissonModel:
    return EloPoissonModel().fit(get_results())


@st.cache_data(show_spinner="Évaluation du modèle sur les matchs récents…")
def get_backtest(last_date: str, only_wc: bool) -> dict:
    return backtest(get_results(), tournaments={"FIFA World Cup"} if only_wc else None)


def pct(x: float) -> str:
    return f"{x * 100:.0f} %"


def team_form(df: pd.DataFrame, team: str, n: int = 5) -> pd.DataFrame:
    m = df[(df.home_team == team) | (df.away_team == team)].tail(n).iloc[::-1]
    rows = []
    for r in m.itertuples():
        gf, ga = (r.home_score, r.away_score) if r.home_team == team else (r.away_score, r.home_score)
        opp = r.away_team if r.home_team == team else r.home_team
        res = "✅ V" if gf > ga else ("➖ N" if gf == ga else "❌ D")
        rows.append({"Date": r.date.strftime("%d/%m/%Y"), "Adversaire": opp,
                     "Score": f"{gf}-{ga}", "Rés.": res, "Compétition": r.tournament})
    return pd.DataFrame(rows)


def head_to_head(df: pd.DataFrame, a: str, b: str) -> pd.DataFrame:
    m = df[((df.home_team == a) & (df.away_team == b)) | ((df.home_team == b) & (df.away_team == a))]
    return m.iloc[::-1]


df = get_results()
last_date = df["date"].max().strftime("%Y-%m-%d")
model = get_model(last_date)
teams = sorted(model.ranking(active_since="2018-01-01")["Équipe"])

st.title("📊 PronoStats")
st.caption(f"Pronostics statistiques (Elo + Poisson) · {len(df):,} matchs internationaux "
           f"depuis 1872 · dernier match connu : {df['date'].max():%d/%m/%Y}".replace(",", " "))

tab_match, tab_elo, tab_fiab, tab_methode = st.tabs(
    ["🔮 Pronostic d'un match", "📈 Classement Elo", "🧪 Fiabilité", "📚 Méthode"])

# --- Pronostic --------------------------------------------------------------
with tab_match:
    c1, c2, c3 = st.columns([2, 2, 1])
    home = c1.selectbox("Équipe 1", teams, index=teams.index("France") if "France" in teams else 0)
    away = c2.selectbox("Équipe 2", teams, index=teams.index("Brazil") if "Brazil" in teams else 1)
    terrain = c3.radio("Terrain", ["Neutre", "Domicile équipe 1"], index=0)

    if home == away:
        st.warning("Choisis deux équipes différentes.")
    else:
        p = model.predict(home, away, neutral=(terrain == "Neutre"))
        (bi, bj), ev = p.best_contest_pick()

        m1, m2, m3 = st.columns(3)
        m1.metric(f"Victoire {home}", pct(p.p_home))
        m2.metric("Match nul", pct(p.p_draw))
        m3.metric(f"Victoire {away}", pct(p.p_away))

        st.success(f"🎯 **Prono conseillé : {home} {bi} - {bj} {away}** "
                   f"· espérance ≈ {ev:.2f} pt (barème 3 pts score exact / 1 pt bon résultat)")

        left, right = st.columns(2)
        with left:
            st.markdown("##### Scores les plus probables")
            st.dataframe(pd.DataFrame(
                [{"Score": f"{i} - {j}", "Probabilité": pct(pr)} for i, j, pr in p.top_scores(8)]),
                hide_index=True, width="stretch")
            st.caption(f"Buts attendus : {home} {p.lambda_home:.2f} · {away} {p.lambda_away:.2f} · "
                       f"Elo : {model.ratings[home]:.0f} vs {model.ratings[away]:.0f}")
        with right:
            st.markdown("##### Grille des scores (%)")
            grid = pd.DataFrame(p.matrix[:6, :6] * 100,
                                index=[f"{home} {i}" for i in range(6)],
                                columns=[str(j) for j in range(6)]).round(1)
            st.dataframe(grid, width="stretch")
            st.caption(f"Lignes : buts de {home} · colonnes : buts de {away}")

        st.divider()
        f1, f2 = st.columns(2)
        with f1:
            st.markdown(f"##### Forme de {home} (5 derniers)")
            st.dataframe(team_form(df, home), hide_index=True, width="stretch")
        with f2:
            st.markdown(f"##### Forme de {away} (5 derniers)")
            st.dataframe(team_form(df, away), hide_index=True, width="stretch")

        h2h = head_to_head(df, home, away)
        st.markdown(f"##### Confrontations directes ({len(h2h)})")
        if h2h.empty:
            st.info("Ces deux équipes ne se sont jamais affrontées.")
        else:
            wa = ((h2h.home_team == home) & (h2h.home_score > h2h.away_score)).sum() + \
                 ((h2h.away_team == home) & (h2h.away_score > h2h.home_score)).sum()
            wb = ((h2h.home_team == away) & (h2h.home_score > h2h.away_score)).sum() + \
                 ((h2h.away_team == away) & (h2h.away_score > h2h.home_score)).sum()
            st.write(f"{home} **{wa}** victoires · **{len(h2h) - wa - wb}** nuls · {away} **{wb}** victoires")
            show = h2h.head(10).assign(
                Date=lambda d: d.date.dt.strftime("%d/%m/%Y"),
                Match=lambda d: d.home_team + " " + d.home_score.astype(str) + "-" +
                d.away_score.astype(str) + " " + d.away_team,
            )[["Date", "Match", "tournament"]].rename(columns={"tournament": "Compétition"})
            st.dataframe(show, hide_index=True, width="stretch")

# --- Classement Elo ---------------------------------------------------------
with tab_elo:
    st.markdown("Classement des sélections ayant joué depuis 2022.")
    rank = model.ranking()
    c1, c2 = st.columns([1, 2])
    with c1:
        st.dataframe(rank, width="stretch", height=600)
    with c2:
        choix = st.multiselect("Évolution de l'Elo", teams,
                               default=[t for t in ["France", "Spain", "Argentina", "England"] if t in teams])
        since = st.slider("Depuis l'année", 1950, int(last_date[:4]), 2010)
        if choix:
            h = model.history[model.history["date"].dt.year >= since]
            series = {}
            for t in choix:
                rows = pd.concat([
                    h.loc[h.home_team == t, ["date", "elo_home"]].rename(columns={"elo_home": "elo"}),
                    h.loc[h.away_team == t, ["date", "elo_away"]].rename(columns={"elo_away": "elo"}),
                ]).sort_values("date").drop_duplicates("date", keep="last")
                series[t] = rows.set_index("date")["elo"]
            st.line_chart(pd.DataFrame(series).ffill(), height=500)

# --- Fiabilité --------------------------------------------------------------
with tab_fiab:
    st.markdown("Le modèle est entraîné sur les matchs **2000–2021**, puis testé sur tous les matchs "
                "**depuis 2022** qu'il n'a jamais vus (les Elo utilisés sont ceux d'avant chaque match).")
    only_wc = st.toggle("Uniquement les matchs de Coupe du monde (2022 + 2026)", value=False)
    bt = get_backtest(last_date, only_wc)
    if bt["n"] == 0:
        st.info("Aucun match à évaluer.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Matchs testés", f"{bt['n']:,}".replace(",", " "))
        c2.metric("Bon résultat (V/N/D)", pct(bt["accuracy"]))
        c3.metric("Score exact", pct(bt["exact"]))
        c4.metric("Points / match au concours", f"{bt['pts_per_match']:.2f}",
                  delta=f"{bt['pts_per_match'] - bt['pts_per_match_fav']:+.2f} vs « favori 1-0 »")
        st.caption(f"Log-loss : {bt['logloss']:.3f} (référence sans info sur les équipes : "
                   f"{bt['logloss_base']:.3f}, plus bas = mieux) · Brier : {bt['brier']:.3f}")

# --- Méthode ----------------------------------------------------------------
with tab_methode:
    st.markdown(f"""
### Comment ça marche ?

1. **Classement Elo** — chaque sélection part de 1500 points. Après chaque match, le gagnant
   prend des points au perdant, d'autant plus que la victoire était inattendue.
   L'importance du match compte (Coupe du monde ×60, phases finales continentales ×50,
   qualifications et Ligue des nations ×40, amicaux ×20) ainsi que l'écart de buts.
   L'équipe à domicile reçoit un bonus de 100 points.
2. **Buts attendus** — une régression de Poisson apprend, sur les matchs depuis 2000,
   comment un écart d'Elo se traduit en buts : `buts attendus = exp(a + b × écart/400)`
   (a = {model.beta[0]:.3f}, b = {model.beta[1]:.3f}).
3. **Probabilités des scores** — loi de Poisson pour chaque équipe, avec la correction
   Dixon-Coles (ρ = {model.rho:.3f}) qui ajuste les petits scores (0-0, 1-0, 0-1, 1-1).
4. **Prono conseillé** — le score qui maximise les points espérés avec le barème du concours
   (3 pts score exact, 1 pt bon résultat). Ce n'est pas toujours le score le plus probable !

Données : [martj42/international_results]({DATA_URL.replace('raw.githubusercontent.com', 'github.com').replace('/master/', '/blob/master/')}),
mises à jour automatiquement toutes les 6 heures.
""")
