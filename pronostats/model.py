"""Modèle statistique de pronostics : Elo + Poisson (avec correction Dixon-Coles).

1. Elo : chaque sélection a une note mise à jour après chaque match
   (méthode World Football Elo : K selon la compétition, bonus selon l'écart
   de buts, +100 pour l'équipe à domicile).
2. Poisson : on apprend comment l'écart d'Elo se traduit en buts attendus
   (régression de Poisson log(lambda) = a + b * écart_elo / 400).
3. Dixon-Coles : petite correction des scores 0-0, 1-0, 0-1, 1-1
   (la loi de Poisson indépendante sous-estime les nuls).

Les données viennent du jeu public martj42/international_results.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"

ELO_INIT = 1500.0
HOME_ADV = 100.0
MAX_GOALS = 10

GRANDES_FINALES = {
    "UEFA Euro", "Copa América", "African Cup of Nations", "AFC Asian Cup",
    "Gold Cup", "CONCACAF Championship", "Confederations Cup", "OFC Nations Cup",
}


def k_factor(tournament: str) -> float:
    t = str(tournament)
    if t == "FIFA World Cup":
        return 60
    if t in GRANDES_FINALES:
        return 50
    if "qualification" in t or "Nations League" in t:
        return 40
    if t == "Friendly":
        return 20
    return 30


def goal_multiplier(diff: int) -> float:
    n = abs(diff)
    if n <= 1:
        return 1.0
    if n == 2:
        return 1.5
    return (11 + n) / 8


def load_results(source: str = DATA_URL) -> pd.DataFrame:
    df = pd.read_csv(source)
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["home_score", "away_score"]).copy()
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    df["neutral"] = df["neutral"].astype(str).str.upper().eq("TRUE")
    return df.sort_values("date", kind="stable").reset_index(drop=True)


def compute_elo(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    """Ajoute les Elo *avant* match (elo_home, elo_away) et renvoie les Elo actuels."""
    ratings: dict[str, float] = {}
    pre_h = np.empty(len(df))
    pre_a = np.empty(len(df))
    for i, (h, a, hs, as_, neutral, tour) in enumerate(zip(
        df["home_team"], df["away_team"], df["home_score"], df["away_score"],
        df["neutral"], df["tournament"],
    )):
        rh = ratings.get(h, ELO_INIT)
        ra = ratings.get(a, ELO_INIT)
        pre_h[i], pre_a[i] = rh, ra
        dr = rh - ra + (0 if neutral else HOME_ADV)
        expected = 1 / (10 ** (-dr / 400) + 1)
        result = 1.0 if hs > as_ else (0.5 if hs == as_ else 0.0)
        delta = k_factor(tour) * goal_multiplier(hs - as_) * (result - expected)
        ratings[h] = rh + delta
        ratings[a] = ra - delta
    out = df.copy()
    out["elo_home"] = pre_h
    out["elo_away"] = pre_a
    out["elo_diff"] = pre_h - pre_a + np.where(out["neutral"], 0, HOME_ADV)
    return out, ratings


# --- Poisson ---------------------------------------------------------------

def _fit_poisson(x: np.ndarray, y: np.ndarray, iters: int = 50) -> np.ndarray:
    """Régression de Poisson log(mu) = b0 + b1*x par IRLS (sans dépendance scipy)."""
    X = np.column_stack([np.ones_like(x), x])
    beta = np.array([np.log(y.mean()), 0.0])
    for _ in range(iters):
        mu = np.exp(X @ beta)
        z = X @ beta + (y - mu) / mu
        W = mu
        new = np.linalg.solve(X.T @ (W[:, None] * X), X.T @ (W * z))
        if np.max(np.abs(new - beta)) < 1e-9:
            beta = new
            break
        beta = new
    return beta


def _poisson_pmf(lam: float, n: int = MAX_GOALS) -> np.ndarray:
    k = np.arange(n + 1)
    log_fact = np.cumsum(np.log(np.maximum(k, 1)))
    return np.exp(k * np.log(lam) - lam - log_fact)


def _dc_tau(lh: float, la: float, rho: float) -> np.ndarray:
    tau = np.ones((MAX_GOALS + 1, MAX_GOALS + 1))
    tau[0, 0] = 1 - lh * la * rho
    tau[0, 1] = 1 + lh * rho
    tau[1, 0] = 1 + la * rho
    tau[1, 1] = 1 - rho
    return tau


@dataclass
class Prediction:
    home: str
    away: str
    lambda_home: float
    lambda_away: float
    matrix: np.ndarray  # matrix[i, j] = P(home marque i, away marque j)
    p_home: float = field(init=False)
    p_draw: float = field(init=False)
    p_away: float = field(init=False)

    def __post_init__(self):
        self.p_home = float(np.tril(self.matrix, -1).sum())
        self.p_draw = float(np.trace(self.matrix))
        self.p_away = float(np.triu(self.matrix, 1).sum())

    def top_scores(self, n: int = 5) -> list[tuple[int, int, float]]:
        flat = np.argsort(self.matrix, axis=None)[::-1][:n]
        return [(int(i), int(j), float(self.matrix[i, j]))
                for i, j in zip(*np.unravel_index(flat, self.matrix.shape))]

    def best_contest_pick(self, pts_result: float = 1, pts_exact_bonus: float = 2):
        """Score qui maximise l'espérance de points au concours
        (1 pt bon résultat, +2 pts si score exact => 3 pts)."""
        best, best_ev = (0, 0), -1.0
        size = self.matrix.shape[0]
        for i in range(size):
            for j in range(size):
                p_res = self.p_home if i > j else (self.p_draw if i == j else self.p_away)
                ev = pts_result * p_res + pts_exact_bonus * self.matrix[i, j]
                if ev > best_ev:
                    best, best_ev = (i, j), ev
        return best, best_ev


class EloPoissonModel:
    def __init__(self, train_from: str = "2000-01-01"):
        self.train_from = pd.Timestamp(train_from)
        self.beta = np.array([0.0, 0.0])
        self.rho = 0.0
        self.ratings: dict[str, float] = {}
        self.history: pd.DataFrame | None = None

    # -- entraînement -------------------------------------------------------
    def fit(self, df: pd.DataFrame, until: str | pd.Timestamp | None = None) -> "EloPoissonModel":
        hist, ratings = compute_elo(df)
        self.history, self.ratings = hist, ratings
        train = hist[hist["date"] >= self.train_from]
        if until is not None:
            train = train[train["date"] < pd.Timestamp(until)]
        x = np.concatenate([train["elo_diff"].to_numpy(), -train["elo_diff"].to_numpy()]) / 400
        y = np.concatenate([train["home_score"].to_numpy(), train["away_score"].to_numpy()]).astype(float)
        self.beta = _fit_poisson(x, y)
        self.rho = self._fit_rho(train)
        return self

    def _lambdas(self, elo_diff):
        d = np.asarray(elo_diff, dtype=float) / 400
        return np.exp(self.beta[0] + self.beta[1] * d), np.exp(self.beta[0] - self.beta[1] * d)

    def _fit_rho(self, train: pd.DataFrame) -> float:
        lh, la = self._lambdas(train["elo_diff"].to_numpy())
        hs, as_ = train["home_score"].to_numpy(), train["away_score"].to_numpy()
        best_rho, best_ll = 0.0, -np.inf
        for rho in np.linspace(-0.2, 0.2, 81):
            tau = np.ones_like(lh)
            m00, m01 = (hs == 0) & (as_ == 0), (hs == 0) & (as_ == 1)
            m10, m11 = (hs == 1) & (as_ == 0), (hs == 1) & (as_ == 1)
            tau[m00] = 1 - lh[m00] * la[m00] * rho
            tau[m01] = 1 + lh[m01] * rho
            tau[m10] = 1 + la[m10] * rho
            tau[m11] = 1 - rho
            if np.any(tau <= 0):
                continue
            ll = np.log(tau).sum()
            if ll > best_ll:
                best_rho, best_ll = rho, ll
        return float(best_rho)

    # -- prédiction ---------------------------------------------------------
    def predict_from_diff(self, elo_diff: float, home: str = "A", away: str = "B") -> Prediction:
        lh, la = self._lambdas(elo_diff)
        lh, la = float(lh), float(la)
        m = np.outer(_poisson_pmf(lh), _poisson_pmf(la)) * _dc_tau(lh, la, self.rho)
        m /= m.sum()
        return Prediction(home, away, lh, la, m)

    def predict(self, home: str, away: str, neutral: bool = True) -> Prediction:
        rh = self.ratings.get(home, ELO_INIT)
        ra = self.ratings.get(away, ELO_INIT)
        return self.predict_from_diff(rh - ra + (0 if neutral else HOME_ADV), home, away)

    def ranking(self, active_since: str = "2022-01-01") -> pd.DataFrame:
        recent = self.history[self.history["date"] >= pd.Timestamp(active_since)]
        actives = set(recent["home_team"]) | set(recent["away_team"])
        df = pd.DataFrame(
            [(t, r) for t, r in self.ratings.items() if t in actives], columns=["Équipe", "Elo"]
        ).sort_values("Elo", ascending=False).reset_index(drop=True)
        df.index += 1
        df["Elo"] = df["Elo"].round(0).astype(int)
        return df


# --- Évaluation ------------------------------------------------------------

def backtest(df: pd.DataFrame, split: str = "2022-01-01",
             tournaments: set[str] | None = None) -> dict:
    """Entraîne la partie Poisson avant `split`, évalue sur les matchs suivants.
    Les Elo utilisés sont toujours ceux d'avant chaque match (pas de triche)."""
    model = EloPoissonModel().fit(df, until=split)
    test = model.history[model.history["date"] >= pd.Timestamp(split)]
    if tournaments:
        test = test[test["tournament"].isin(tournaments)]
    if test.empty:
        return {"n": 0}

    n = len(test)
    correct = exact = pts = pts_fav = 0
    logloss = brier = 0.0
    for d, hs, as_ in zip(test["elo_diff"], test["home_score"], test["away_score"]):
        p = model.predict_from_diff(d)
        probs = np.array([p.p_home, p.p_draw, p.p_away])
        outcome = 0 if hs > as_ else (1 if hs == as_ else 2)
        onehot = np.eye(3)[outcome]
        logloss -= np.log(max(probs[outcome], 1e-12))
        brier += ((probs - onehot) ** 2).sum()
        correct += int(np.argmax(probs) == outcome)
        (bi, bj), _ = p.best_contest_pick()
        pick_out = 0 if bi > bj else (1 if bi == bj else 2)
        if pick_out == outcome:
            pts += 1 + (2 if (bi, bj) == (hs, as_) else 0)
        exact += int((bi, bj) == (hs, as_))
        # Référence naïve : toujours "favori Elo gagne 1-0" (nul 1-1 si égalité)
        if d > 0:
            fav = (1, 0)
        elif d < 0:
            fav = (0, 1)
        else:
            fav = (1, 1)
        fav_out = 0 if fav[0] > fav[1] else (1 if fav[0] == fav[1] else 2)
        if fav_out == outcome:
            pts_fav += 1 + (2 if fav == (hs, as_) else 0)

    # Référence : fréquences historiques V/N/D (sans info sur les équipes)
    train = model.history[(model.history["date"] >= model.train_from) &
                          (model.history["date"] < pd.Timestamp(split))]
    base = np.array([
        (train["home_score"] > train["away_score"]).mean(),
        (train["home_score"] == train["away_score"]).mean(),
        (train["home_score"] < train["away_score"]).mean(),
    ])
    outs = np.where(test["home_score"] > test["away_score"], 0,
                    np.where(test["home_score"] == test["away_score"], 1, 2))
    base_ll = -np.log(base[outs]).mean()

    return {
        "n": n,
        "accuracy": correct / n,
        "exact": exact / n,
        "logloss": logloss / n,
        "logloss_base": float(base_ll),
        "brier": brier / n,
        "pts_per_match": pts / n,
        "pts_per_match_fav": pts_fav / n,
        "beta": model.beta.tolist(),
        "rho": model.rho,
    }
