# 📊 PronoStats

Pronostics de matchs internationaux à partir de statistiques (Elo + Poisson avec correction Dixon-Coles).

```bash
pip install -r pronostats/requirements.txt
streamlit run pronostats/app.py
```

- `model.py` : calcul des Elo, régression de Poisson, probabilités des scores, prono qui maximise les points au concours, backtest.
- `app.py` : interface Streamlit (pronostic d'un match, classement Elo, fiabilité, méthode).

Données : [martj42/international_results](https://github.com/martj42/international_results), téléchargées au lancement (cache 6 h).
