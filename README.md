# 🚀 Gemini Marketing App

![Gemini Marketing](https://raw.githubusercontent.com/gemini-marketing-app/gemini-marketing-app/main/images/google_ai_gemini_logo.png)

**Gemini Marketing App** — Une application Streamlit qui utilise Google Gemini pour générer du contenu marketing, analyser des campagnes et produire des visuels/rapports. Ce README est **un seul fichier** prêt à copier-coller.

---

## 🧭 Résumé

Application interactive pour la génération de contenu marketing (posts, slogans, rapports), visualisations prédictives et export PDF. Pensée pour être déployée localement ou sur Streamlit Cloud. Les clés secrètes (ex: GEMINI_API_KEY) sont stockées localement dans `.streamlit/secrets.toml` et **ne doivent jamais** être poussées sur GitHub.

---

## ✨ Fonctionnalités principales

- Génération de contenu marketing via Google Gemini
- Création automatique de visuels (bannières / assets)
- Analyse prédictive (ROI, CPA) et graphiques interactifs (Plotly)
- Export PDF avec polices locales
- Historique des analyses et options premium
- Interface simple avec Streamlit

---

## Prérequis

- Python 3.10+ (ou 3.11+ recommandé)
- Git
- Streamlit (`pip install streamlit`)
- Clé API Gemini valide

---

## Structure recommandée du projet

gemini_marketing_app/
│── app.py
│── requirements.txt
│── README.md ← (ce fichier)
│── styles.css
│── fonts/
│── images/
│── templates/
└── .streamlit/
    └── secrets.toml ← NE PAS COMMITTER

---

## ⚙️ Configuration des secrets (NE PAS pousser)

Créer le dossier `.streamlit` si non présent et ajouter `secrets.toml` :

`.streamlit/secrets.toml`
GEMINI_API_KEY = "VOTRE_CLE_GEMINI_ICI"

Vérifier que `.gitignore` contient bien la ligne suivante :
.streamlit/secrets.toml

Pour confirmer que Git ignore bien le fichier :
git check-ignore -v .streamlit/secrets.toml
## Retour attendu: .gitignore:16:.streamlit/secrets.toml   .streamlit/secrets.toml

---

## 📦 Installation & Démarrage

Cloner le dépôt
git clone <votre-repo-url>
cd gemini_marketing_app

Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
### ou
venv\Scripts\activate     # Windows

Installer les dépendances
pip install -r requirements.txt

Configurer les secrets
mkdir -p .streamlit
echo 'GEMINI_API_KEY = "votre_cle_api_ici"' > .streamlit/secrets.toml

Lancer l'application
streamlit run app.py

---

## 🎯 Utilisation

1. Saisir votre clé API Gemini (si non configurée dans `secrets.toml`)
2. Choisir le type de contenu à générer (post, slogan, rapport)
3. Paramétrer votre campagne (budget, cible, durée)
4. Générer le contenu et visualiser les résultats
5. Exporter en PDF si nécessaire

---

## 📊 Fonctionnalités Avancées

- **Analyse prédictive** : Estimation du ROI, CPA et autres métriques clés
- **Graphiques interactifs** : Visualisations Plotly des performances
- **Génération d'images** : Création de visuels marketing automatisés
- **Historique** : Sauvegarde des analyses précédentes
- **Mode premium** : Options avancées pour utilisateurs professionnels

---

## 🚀 Déploiement

### Déploiement sur Streamlit Cloud
1. Poussez votre code sur GitHub
2. Connectez-vous à Streamlit Cloud
3. Configurez vos secrets dans l'interface Streamlit Cloud
4. Déployez automatiquement depuis GitHub

### Déploiement local avancé
# Avec Gunicorn (optionnel)
pip install gunicorn
gunicorn app:app -b 0.0.0.0:8501

---

## 🔧 Dépannage

### Problèmes courants
- **Clé API non reconnue** : Vérifiez le format dans `secrets.toml`
- **Erreurs de dépendances** : Réinstallez `requirements.txt`
- **Problèmes de PDF** : Vérifiez l'installation de ReportLab

### Commandes utiles
# Vérifier l'installation
python -c "import streamlit; print('Streamlit OK')"

# Nettoyer le cache
rm -rf __pycache__/ .streamlit/cache/

---

## 📝 Structure du Code

L'application est structurée autour des modules suivants :
- `app.py` : Point d'entrée principal
- `gemini_client.py` : Client pour l'API Gemini
- `pdf_generator.py` : Générateur de rapports PDF
- `utils.py` : Fonctions utilitaires et helpers

---

## 🤝 Contribution

1. Forkez le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commitez vos changes (`git commit -m 'Add AmazingFeature'`)
4. Pushez la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🆘 Support

Pour toute question ou problème :
- Consultez les [issues GitHub](<votre-repo-url>/issues)
- Contactez-nous via email

---

**Note importante** : Cette application utilise l'API Google Gemini. Assurez-vous de respecter les conditions d'utilisation de Google et les limites d'API.

Dernière mise à jour : 2025
