# --- Imports
import streamlit as st
import google.generativeai as genai
from datetime import datetime
from io import BytesIO
import pandas as pd
from fpdf import FPDF
import plotly.graph_objects as go
from PIL import Image, ImageDraw, ImageFont
import random
import re
import os
import base64
from pathlib import Path
import tempfile

###########################
# --- Configuration Globale
PRIMARY_COLOR = "#C8E546"
SECONDARY_COLOR = "#1013B9"
PREMIUM_FEATURES = True

# --- Configuration des polices locales
def setup_fonts():
    font_dir = Path("fonts")
    font_dir.mkdir(exist_ok=True)
    
    # Créer des polices de base si elles n'existent pas
    dejavu_regular = font_dir / "DejaVuSans.ttf"
    dejavu_bold = font_dir / "DejaVuSans-Bold.ttf"

    if not dejavu_regular.exists() or not dejavu_bold.exists():
        st.warning("Les fichiers de police sont manquants dans le dossier 'fonts'")
        return None, None

    return str(dejavu_regular), str(dejavu_bold)

# --- Configuration Streamlit
st.set_page_config(
    page_title="⚡ Gemini Smart Campaign",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styles CSS
def local_css(file_name):
    if Path(file_name).exists():
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Créer le fichier CSS si inexistant
css_file = "styles.css"
if not Path(css_file).exists():
    css_content = """
    .stApp { background-color: #f9fafb; }
    .sidebar .sidebar-content { background-color: #ffffff; }
    .big-font { font-size: 1.5rem !important; }
    .premium-badge {
        background-color: #F59E0B;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.5rem;
        font-size: 0.8rem;
    }
    .feature-card {
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .celebration {
        animation: celebrate 2s ease-in-out infinite;
        text-align: center;
        padding: 20px;
        margin: 20px 0;
    }
    @keyframes celebrate {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    """
    with open(css_file, "w") as f:
        f.write(css_content)

local_css(css_file)

# --- Fonction pour générer une image de célébration (version améliorée)
def generate_celebration_image(result_quality):
    try:
        width, height = 800, 400
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        # Définir les couleurs de dégradé et l'insigne en fonction de la qualité
        if result_quality == "excellent":
            start_color, end_color = (255, 215, 0), (255, 165, 0) # Or -> Orange
            message, badge = "Analyse Exceptionnelle!", "🏆"
        elif result_quality == "good":
            start_color, end_color = (144, 238, 144), (60, 179, 113) # Vert clair -> Vert moyen
            message, badge = "Résultats Impressionnants!", "⭐"
        else:
            start_color, end_color = (173, 216, 230), (70, 130, 180) # Bleu clair -> Bleu acier
            message, badge = "Analyse Terminée!", "📈"

        # Dessiner le dégradé d'arrière-plan
        for y in range(height):
            r = int(start_color[0] + (end_color[0] - start_color[0]) * (y / height))
            g = int(start_color[1] + (end_color[1] - start_color[1]) * (y / height))
            b = int(start_color[2] + (end_color[2] - start_color[2]) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Charger les polices
        try:
            font_large = ImageFont.truetype("arial.ttf", 48)
            font_medium = ImageFont.truetype("arial.ttf", 28)
            font_badge = ImageFont.truetype("arial.ttf", 80)
        except IOError:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_badge = ImageFont.load_default()

        # Dessiner l'insigne
        badge_bbox = draw.textbbox((0, 0), badge, font=font_badge)
        badge_width = badge_bbox[2] - badge_bbox[0]
        badge_x = (width - badge_width) / 2
        draw.text((badge_x, 50), badge, font=font_badge, fill=(255, 255, 255, 220))

        # Dessiner le message principal avec ombre
        message_bbox = draw.textbbox((0, 0), message, font=font_large)
        text_width = message_bbox[2] - message_bbox[0]
        x = (width - text_width) / 2
        y = 180
        draw.text((x + 2, y + 2), message, font=font_large, fill=(0, 0, 0, 100)) # Ombre
        draw.text((x, y), message, font=font_large, fill=(255, 255, 255)) # Texte

        # Dessiner le message secondaire
        sub_message = "Votre stratégie marketing est prête !"
        sub_message_bbox = draw.textbbox((0, 0), sub_message, font=font_medium)
        sub_text_width = sub_message_bbox[2] - sub_message_bbox[0]
        sub_x = (width - sub_text_width) / 2
        draw.text((sub_x, y + 70), sub_message, font=font_medium, fill=(255, 255, 255, 200))

        # Ajouter des confettis améliorés
        for _ in range(40):
            x_pos, y_pos = random.randint(0, width), random.randint(0, height)
            size = random.randint(5, 15)
            confetti_color = (random.randint(200, 255), random.randint(200, 255), random.randint(150, 255), random.randint(128, 255))
            if random.choice(['ellipse', 'rect']) == 'ellipse':
                draw.ellipse([x_pos, y_pos, x_pos + size, y_pos + size], fill=confetti_color)
            else:
                draw.rectangle([x_pos, y_pos, x_pos + size, y_pos + size], fill=confetti_color)

        # Sauvegarder l'image
        celebration_path = "images/celebration.png"
        img.save(celebration_path, "PNG")
        return celebration_path

    except Exception as e:
        st.warning(f"Impossible de créer l'image de célébration améliorée: {e}")
        return None

# --- Page d'accueil Premium
def display_welcome_page():
    col1, col2 = st.columns([1, 2])
    with col1:
        # Créer le dossier images s'il n'existe pas
        images_dir = Path("images")
        images_dir.mkdir(exist_ok=True)
        
        logo_path = "images/google_ai_gemini_logo.png"
        
        # Vérifier si l'image existe, sinon la créer
        if not Path(logo_path).exists():
            try:
                # Créer une image de remplacement valide
                img = Image.new('RGB', (600, 300), color=(73, 109, 137))
                # Ajouter du texte pour en faire une image valide
                draw = ImageDraw.Draw(img)
                # Utiliser une police par défaut
                try:
                    font = ImageFont.load_default()
                    draw.text((150, 140), "Gemini Marketing", fill=(255, 255, 255), font=font)
                except:
                    draw.text((150, 140), "Gemini Marketing", fill=(255, 255, 255))
                img.save(logo_path, "PNG")
            except Exception as e:
                st.warning(f"Impossible de créer l'image de logo: {e}")
        
        # Charger et afficher l'image
        try:
            st.image(logo_path, width=250)
        except Exception as e:
            st.warning(f"Impossible de charger l'image: {e}")
            # Option de secours: afficher un placeholder
            st.markdown("""
            <div style="width:250px; height:150px; background-color:#4F46E5; 
                        display:flex; align-items:center; justify-content:center; 
                        color:white; font-weight:bold; border-radius:10px;">
                Gemini Marketing
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.title("⚡ Gemini Marketing Pro Plus")
        st.markdown("""
        <div style='font-size:1.1rem; color:#4B5563;'>
        L'outil ultime pour des <span style='color:#4F46E5;font-weight:bold'>stratégies marketing intelligentes</span>
        propulsé par <span style='color:#EA4335;font-weight:bold'>Google Gemini 2.5 Flash</span>
        </div>
        """, unsafe_allow_html=True)

    # Features Grid
    st.markdown("---")
    st.subheader("✨ Fonctionnalités Exclusives")

    features = [
        {"icon": "📊", "title": "Analyse Prédictive", "desc": "Prédictions précises de ROI et CPA"},
        {"icon": "🎯", "title": "Recommandations", "desc": "Stratégies adaptées à votre secteur"},
        {"icon": "📈", "title": "Visualisations", "desc": "Graphiques interactifs professionnels"},
        {"icon": "📄", "title": "Rapports PDF", "desc": "Exportez vos analyses en un clic"},
        {"icon": "🤖", "title": "IA Avancée", "desc": "Gemini 2.5 Flash pour des insights précis"},
        {"icon": "💎", "title": "Mode Premium", "desc": "Fonctionnalités exclusives"}
    ]

    cols = st.columns(3)
    for i, feature in enumerate(features):
        with cols[i%3]:
            with st.container():
                st.markdown(f"""
                <div class='feature-card'>
                    <div style='font-size:2rem;margin-bottom:0.5rem;'>{feature['icon']}</div>
                    <h3>{feature['title']}</h3>
                    <p style='color:#6B7280;'>{feature['desc']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("Pour vous donner une idée visuelle de ce que nous proposons : ")
    st.markdown("Voici un aperçu de l'interface et de ses capacités : ")

# --- Initialisation Gemini
def initialize_gemini(selected_model):
    try:
        # Vérifier si l'API key est disponible
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("Clé API Gemini non trouvée dans les secrets Streamlit")
            return None
            
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name=selected_model,
            generation_config={"temperature": 0.7, "top_p": 1}
        )
        return model
    except Exception as e:
        st.error(f"❌ Erreur Gemini : {str(e)}")
        return None

# --- Fonctions Marketing Avancées
def generate_prediction(model, params, style="Formel", lang="Français", domain="Général"):
    style_prompts = {
        "Formel": "Ton professionnel et technique avec des termes marketing précis.",
        "Dynamique": "Ton énergique avec des verbes d'action et des phrases courtes.",
        "Humour": "Ton décontracté avec des touches d'humour adapté au monde professionnel."
    }

    prompt = f"""
    [ROLE] Vous êtes un expert en marketing digital avec 15 ans d'expérience spécialisé en {domain}.
    [CONTEXTE] Analyse de campagne marketing pour un client.

    [PARAMETRES CLIENT]
    - Budget: {params['budget']} €
    - Audience: {params['audience']}
    - Durée: {params['duration']} jours
    - Objectif: {params['goal']}
    - Domaine: {domain}

    [INSTRUCTIONS]
    1. Analysez les performances attendues (ROI, CPA, etc.)
    2. Proposez 3 stratégies concrètes adaptées
    3. Liste des canaux prioritaires
    4. Estimation des résultats
    5. Conseils d'optimisation

    [FORMAT DE REPONSE]
    ### Analyse Prédictive
    - ROI estimé: X% à Y%
    - CPA moyen: Z €

    ### Stratégies Recommandées
    1. Stratégie 1
    2. Stratégie 2
    3. Stratégie 3

    ### Canaux Prioritaires
    - Canal 1 (X% du budget)
    - Canal 2 (Y% du budget)

    [STYLE] {style_prompts.get(style)}
    [LANGUE] {lang}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erreur génération : {str(e)}")
        return None

def generate_premium_insights(model, params, domain):
    prompt = f"""
    [ROLE] Expert en analyse marketing premium
    [TACHE] Générer des insights exclusifs pour:
    - Budget: {params['budget']} €
    - Audience: {params['audience']}
    - Domaine: {domain}

    [CONTENU EXCLUSIF]
    1. Tendances actuelles du secteur
    2. Opportunités sous-exploitées
    3. Stratégie premium détaillée
    4. Étude de cas similaire
    5. Checklist d'optimisation
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return None

def generate_visual_asset(model, prediction_text, domain):
    """
    Génère un visuel publicitaire avec Gemini 2.5 Flash Image Preview.
    """
    prompt = f"""
    [ROLE] Vous êtes un directeur artistique expert en publicité.
    [CONTEXTE] Créer un visuel publicitaire percutant (bannière ou poster) pour une campagne marketing.
    [INSPIRATION] Le texte suivant est l'analyse stratégique de la campagne :
    ---
    {prediction_text}
    ---
    [INSTRUCTIONS]
    1.  **Analysez** les éléments clés de la stratégie : l'audience, l'objectif, et le domaine ({domain}).
    2.  **Imaginez** un concept visuel fort qui incarne l'esprit de la campagne.
    3.  **Générez** une image publicitaire (format 1200x628 pixels) qui soit moderne, esthétique et professionnelle.
    4.  **Intégrez** un slogan court et percutant directement dans l'image.
    5.  **Assurez-vous** que le style visuel est adapté au secteur d'activité : '{domain}'.

    [EXEMPLE DE STYLE]
    - Si le domaine est 'Technologie', utilisez un style épuré, futuriste, avec des couleurs vives.
    - Si le domaine est 'Mode', optez pour une image élégante, avec une typographie stylisée.
    - Si le domaine est 'Restauration', créez une image appétissante et chaleureuse.

    Générez l'image directement.
    """
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'parts') and len(response.parts) > 0 and response.parts[0].inline_data:
            image_data = response.parts[0].inline_data.data
            image = Image.open(BytesIO(image_data))
            
            asset_path = "images/generated_asset.png"
            image.save(asset_path, "PNG")
            return asset_path
        else:
            st.warning("La réponse du modèle ne contenait pas d'image.")
            return None
            
    except Exception as e:
        st.error(f"Erreur lors de la génération du visuel : {str(e)}")
        return None

def generate_summary_banner(model, prediction_text, domain):
    """
    Génère une bannière résumant les résultats clés de l'analyse en laissant le modèle extraire les données.
    """
    prompt = f"""
    [ROLE] Vous êtes un designer de données (Data Designer) expert, spécialisé dans la création de rapports visuels percutants pour le marketing.

    [CONTEXTE] Votre tâche est de créer une bannière de résumé (format 1200x400 pixels) à partir d'une analyse de campagne marketing. La bannière doit être claire, professionnelle et visuellement attrayante.

    [ANALYSE MARKETING À SYNTHÉTISER]
    ---
    {prediction_text}
    ---

    [INSTRUCTIONS]
    1.  **Analysez le texte ci-dessus** pour identifier les indicateurs de performance clés (KPIs) suivants :
        - Le "ROI estimé" (Retour sur Investissement).
        - Le "CPA moyen" (Coût par Acquisition).
    2.  **Créez une image de bannière** qui présente ces deux KPIs de manière proéminente et claire.
    3.  **Incorporez le titre** "Synthèse des Résultats" dans la bannière.
    4.  **Utilisez le domaine** de la campagne, '{domain}', pour inspirer le style visuel (par exemple, technologie = futuriste, restauration = chaleureux).

    [EXIGENCES DE DESIGN]
    - **Mise en page :** Structurez la bannière en deux grandes sections, une pour le ROI et une pour le CPA. Chaque section doit afficher la valeur du KPI de manière très visible.
    - **Icônes :** Utilisez des icônes simples et modernes pour représenter chaque KPI (par exemple, une fusée ou un graphique en croissance pour le ROI, une cible ou un caddie pour le CPA).
    - **Palette de couleurs :** Employez une palette professionnelle. Utilisez la couleur primaire '#C8E546' (un vert citron vif) pour les accents et les graphiques, et la couleur secondaire '#1013B9' (un bleu foncé) pour le texte principal ou les fonds de section. Le fond général doit rester neutre et clair (blanc ou gris très pâle #f9fafb).
    - **Typographie :** Choisissez une police sans-serif, lisible et moderne. Mettez les valeurs des KPIs en gras et en grande taille.
    - **Slogan (Optionnel) :** Si l'espace le permet, ajoutez un slogan discret comme "La data au service de votre croissance."

    Générez l'image directement. Assurez-vous que les valeurs du ROI et du CPA extraites du texte sont clairely visibles sur l'image finale.
    """
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'parts') and len(response.parts) > 0 and response.parts[0].inline_data:
            image_data = response.parts[0].inline_data.data
            image = Image.open(BytesIO(image_data))
            
            banner_path = "images/summary_banner.png"
            image.save(banner_path, "PNG")
            return banner_path
        else:
            st.warning("La réponse du modèle pour la bannière de synthèse ne contenait pas d'image.")
            return None
            
    except Exception as e:
        st.error(f"Erreur lors de la génération de la bannière de synthèse : {str(e)}")
        return None

# --- Fonction pour déterminer la qualité des résultats
def evaluate_results_quality(prediction_text, budget):
    # Analyse simple pour déterminer la qualité des résultats
    text_lower = prediction_text.lower()
    
    # Vérifier les indicateurs positifs
    positive_indicators = 0
    
    if "roi" in text_lower and any(word in text_lower for word in ["élevé", "fort", "important", "supérieur", "excellent"]):
        positive_indicators += 2
    
    if "cpa" in text_lower and any(word in text_lower for word in ["faible", "bas", "réduit", "optimisé"]):
        positive_indicators += 2
    
    if any(word in text_lower for word in ["exceptionnel", "excellent", "remarquable", "exceptionnelle"]):
        positive_indicators += 3
        
    if any(word in text_lower for word in ["efficace", "performant", "rentable", "optimisé"]):
        positive_indicators += 2
    
    # Budget élevé = attentes plus élevées
    budget_factor = 1.0
    if budget > 20000:
        budget_factor = 1.2
    elif budget < 5000:
        budget_factor = 0.8
    
    adjusted_score = positive_indicators * budget_factor
    
    if adjusted_score >= 5:
        return "excellent"
    elif adjusted_score >= 3:
        return "good"
    else:
        return "normal"

# --- Visualisations
def generate_advanced_graphs(budget, duration, goal, mois_filtre=None):
    # ROI Simulation
    roi_base = random.uniform(5, 15) + budget / 10000
    roi_values = [roi_base * (1 + random.uniform(-0.1, 0.2)) for _ in range(6)]
    # CPA Simulation
    cpa_base = random.uniform(5, 20) - duration / 30
    cpa_values = [cpa_base * (1 + random.uniform(-0.15, 0.15)) for _ in range(6)]
    # Conversions Simulation
    conversions = [int(budget / random.uniform(10, 50) * (1 + i/10)) for i in range(6)]

    # Filtrer les données si un filtre de mois est appliqué
    if mois_filtre:
        start_month, end_month = mois_filtre
        roi_values = roi_values[start_month-1:end_month]
        cpa_values = cpa_values[start_month-1:end_month]
        conversions = conversions[start_month-1:end_month]
        x_axis_labels = [f"Mois {i}" for i in range(start_month, end_month+1)]  # Générer les labels d'axe X
    else:
        x_axis_labels = [f"Mois {i+1}" for i in range(len(roi_values))]

    # ROI Graph
    fig_roi = go.Figure()
    fig_roi.add_trace(go.Scatter(
        x=x_axis_labels,  # Utiliser les labels d'axe X
        y=roi_values,
        mode='lines+markers',
        name='ROI (%)',
        line=dict(color=PRIMARY_COLOR, width=3),
        marker=dict(size=8)
    ))
    fig_roi.update_layout(
        title="ROI Prédictif par Mois",
        xaxis_title="Mois",
        yaxis_title="ROI (%)",
        height=350,
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    # CPA Graph
    fig_cpa = go.Figure()
    fig_cpa.add_trace(go.Bar(
        x=x_axis_labels, # Utiliser les labels d'axe X
        y=cpa_values,
        name='CPA (EUR)',
        marker_color=SECONDARY_COLOR
    ))
    fig_cpa.update_layout(
        title="Coût par Acquisition (CPA)",
        xaxis_title="Mois",
        yaxis_title="CPA (EUR)",
        height=350,
        template="plotly_white"
    )

    # Conversions Graph
    fig_conv = go.Figure()
    fig_conv.add_trace(go.Scatter(
        x=x_axis_labels, # Utiliser les labels d'axe X
        y=conversions,
        mode='lines+markers+text',
        name='Conversions',
        text=conversions,
        textposition="top center",
        line=dict(color="#7C3AED", width=3),
        marker=dict(size=10)
    ))
    fig_conv.update_layout(
        title="Projection de Conversions",
        xaxis_title="Mois",
        yaxis_title="Nombre",
        height=350,
        template="plotly_white"
    )

    return fig_roi, fig_cpa, fig_conv

def create_simple_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    
    # Add logo
    logo_path = "images/google_ai_gemini_logo.png"
    if Path(logo_path).exists():
        try:
            pdf.image(logo_path, x=10, y=8, w=40)
        except Exception as e:
            print(f"Error adding image to PDF: {e}")
            
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(80)
    pdf.cell(30, 10, 'Rapport d\'Analyse Marketing', 0, 0, 'C')
    pdf.ln(20)
    
    pdf.set_font("Arial", '', 12)
    
    # Add analysis content
    # Replace non-breaking space with regular space and handle potential encoding issues
    content = content.replace('\u00a0', ' ').encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, content)
    
    try:
        pdf_bytes = pdf.output()
        return BytesIO(pdf_bytes)
    except Exception as e:
        st.error(f"Erreur création PDF: {str(e)}")
        return None

# --- Interface Utilisateur
def main():
    display_welcome_page()

    # Vérification API Key
    if 'GEMINI_API_KEY' not in st.secrets:
        st.error("""
        🔐 Configuration manquante :
        1. Créez un fichier `.streamlit/secrets.toml`
        2. Ajoutez : `GEMINI_API_KEY = "votre_clé_api"`
        3. Redémarrez l'application
        """)
        return

    # --- Sidebar
    with st.sidebar:
        logo_path = "images/google_ai_gemini_logo.png"
        if Path(logo_path).exists():
            try:
                st.image(logo_path, width=100)
            except:
                st.markdown("""
                <div style="width:100px; height:60px; background-color:#4F46E5; 
                            display:flex; align-items:center; justify-content:center; 
                            color:white; font-weight:bold; border-radius:10px;">
                    Logo
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("## 🎯 Paramètres Campagne")

        # Modification ici pour utiliser le modèle gemini-2.5-flash-image-preview
        selected_model = st.selectbox(
            "Modèle Gemini",
            ["models/gemini-2.5-flash-image-preview", "gemini-pro", "gemini-1.5-pro-latest"],
            index=0,  # Défini par défaut sur gemini-2.5-flash-image-preview
            help="Choisissez le modèle IA à utiliser"
        )

        budget = st.slider("Budget (EUR)", 1000, 50000, 15000, step=500)
        audience = st.selectbox("Audience", ["18-24 ans", "25-34 ans", "35-44 ans", "45+ ans"])
        duration = st.select_slider("Durée (jours)", options=[7, 14, 30, 60, 90])
        goal = st.selectbox("Objectif Principal", ["Acquisition", "Conversion", "Rétention", "Notoriété"])

        st.markdown("---")
        st.markdown("### ✨ Options Avancées")

        col1, col2 = st.columns(2)
        with col1:
            style = st.radio("Style", ["Formel", "Dynamique", "Humour"])
        with col2:
            lang = st.radio("Langue", ["Français", "Anglais"])

        domaine_options = [
            "Général", "E-commerce", "Santé & Bien-être", "Éducation",
            "Immobilier", "Finance", "Technologie", "Mode",
            "Restauration", "Tourisme", "Divertissement", "Autre"
        ]
        domain_selection = st.selectbox("Secteur d'Activité", domaine_options)

        if domain_selection == "Autre":
            domain = st.text_input("Précisez votre secteur :", "")
        else:
            domain = domain_selection

        filename_pdf = st.text_input("Nom du rapport PDF", f"rapport_{domain.lower()}.pdf")

        if PREMIUM_FEATURES:
            st.markdown("---")
            premium = st.checkbox("🔓 Activer les fonctionnalités Premium", True)
            generate_visual = st.checkbox("🎨 Générer un visuel publicitaire", True)
            generate_summary = st.checkbox("📊 Générer une bannière de résumé", True)

        if st.button("🚀 Lancer l'Analyse", use_container_width=True):
            if domain_selection == "Autre" and domain.strip() == "":
                st.warning("Veuillez préciser votre secteur d'activité")
            else:
                with st.spinner("🔎 Analyse en cours avec Gemini 2.5 Flash..."):
                    model = initialize_gemini(selected_model)
                    if model:
                        params = {
                            'budget': budget,
                            'audience': audience,
                            'duration': duration,
                            'goal': goal
                        }

                        prediction = generate_prediction(model, params, style, lang, domain)
                        premium_content = None
                        if PREMIUM_FEATURES and premium:
                            with st.spinner("🔍 Génération des insights premium..."):
                                premium_content = generate_premium_insights(model, params, domain)

                        if prediction:
                            result_quality = evaluate_results_quality(prediction, budget)
                            celebration_path = generate_celebration_image(result_quality)

                            generated_asset_path = None
                            if generate_visual:
                                with st.spinner("🎨 Création du visuel publicitaire..."):
                                    generated_asset_path = generate_visual_asset(model, prediction, domain)
                            
                            summary_banner_path = None
                            if generate_summary:
                                with st.spinner("📊 Création de la bannière de synthèse..."):
                                    summary_banner_path = generate_summary_banner(model, prediction, domain)

                            if 'history' not in st.session_state:
                                st.session_state.history = []

                            st.session_state.history.append({
                                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                "params": params,
                                "domain": domain,
                                "premium": PREMIUM_FEATURES and premium,
                                "quality": result_quality,
                                "visual_asset": generated_asset_path
                            })

                            st.session_state.last_prediction = prediction
                            st.session_state.last_params = params
                            st.session_state.filename_pdf = filename_pdf
                            st.session_state.domain = domain
                            st.session_state.premium_content = premium_content if PREMIUM_FEATURES and premium else None
                            st.session_state.result_quality = result_quality
                            st.session_state.celebration_path = celebration_path
                            st.session_state.generated_asset_path = generated_asset_path
                            st.session_state.summary_banner_path = summary_banner_path
                            st.rerun()

    # --- Affichage Résultats
    if 'last_prediction' in st.session_state:
        # Afficher l'image de célébration
        if st.session_state.celebration_path and Path(st.session_state.celebration_path).exists():
            try:
                st.image(st.session_state.celebration_path, use_container_width=True)
            except:
                # Fallback en cas d'erreur
                quality = st.session_state.result_quality
                if quality == "excellent":
                    st.markdown("""
                    <div class="celebration" style="background:linear-gradient(135deg, #FFD700, #FFA500); padding:30px; border-radius:15px; text-align:center;">
                        <h1 style="color:white; font-size:2.5em;">🎉 Analyse Exceptionnelle!</h1>
                        <p style="color:white; font-size:1.2em;">Vos résultats dépassent toutes les attentes!</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif quality == "good":
                    st.markdown("""
                    <div class="celebration" style="background:linear-gradient(135deg, #90EE90, #32CD32); padding:30px; border-radius:15px; text-align:center;">
                        <h1 style="color:white; font-size:2.5em;">✨ Résultats Impressionnants!</h1>
                        <p style="color:white; font-size:1.2em;">Votre stratégie marketing est très prometteuse!</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="celebration" style="background:linear-gradient(135deg, #ADD8E6, #1E90FF); padding:30px; border-radius:15px; text-align:center;">
                        <h1 style="color:white; font-size:2.5em;">📊 Analyse Terminée avec Succès!</h1>
                        <p style="color:white; font-size:1.2em;">Votre stratégie marketing est prête à être mise en œuvre!</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.header("📊 Résultats de l'Analyse Marketing")

        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Budget", f"{st.session_state.last_params['budget']} €")
            with col2:
                st.metric("Durée", f"{st.session_state.last_params['duration']} jours")
            with col3:
                st.metric("Secteur", st.session_state.domain)

        with st.expander("🔍 Analyse Détailée", expanded=True):
            st.markdown(st.session_state.last_prediction)

        if st.session_state.summary_banner_path and Path(st.session_state.summary_banner_path).exists():
            st.markdown("---")
            st.header("✨ Bannière de Synthèse des Résultats")
            st.image(st.session_state.summary_banner_path, use_container_width=True,
                     caption="Cette bannière de synthèse a été générée par Gemini pour résumer les KPIs.")

        if st.session_state.generated_asset_path and Path(st.session_state.generated_asset_path).exists():
            st.markdown("---")
            st.header("🎨 Visuel Publicitaire Généré")
            st.image(st.session_state.generated_asset_path, use_container_width=True,
                     caption="Ce visuel a été généré par Gemini 2.5 Flash pour illustrer la stratégie.")
        
        st.markdown("Voici une représentation visuelle de l'impact de ces stratégies :")

        st.markdown("### 📈 Visualisations Prédictives")
        # Filtre pour les graphiques
        mois_filtre = st.slider("Mois à afficher", 1, 6, (1, 6))
        fig_roi, fig_cpa, fig_conv = generate_advanced_graphs(
            st.session_state.last_params['budget'],
            st.session_state.last_params['duration'],
            st.session_state.last_params['goal'],
            mois_filtre
        )

        col1, col2, = st.columns(2)
        with col1:
            st.plotly_chart(fig_roi, use_container_width=True)
        with col2:
            st.plotly_chart(fig_cpa, use_container_width=True)
        st.plotly_chart(fig_conv, use_container_width=True)

        if PREMIUM_FEATURES and st.session_state.premium_content:
            st.markdown("---")
            st.header("💎 Insights Premium")
            with st.expander("Afficher les recommandations avancées"):
                st.markdown(st.session_state.premium_content)
            
            st.markdown("Ces insights premium peuvent être illustrés par l'image suivante :")

            st.markdown("### 🛠 Outils Premium")
            tab1, tab2, tab3 = st.tabs(["Checklist", "Calendrier", "Template"])

            with tab1:
                st.markdown("""
                ### Checklist d'Optimisation
                - [ ] Audit des mots-clés
                - [ ] Analyse concurrentielle
                - [ ] Test A/B landing page
                - [ ] Segmentation audience
                - [ ] Automatisation CRM
                """)

            with tab2:
                st.markdown("""
                ### Calendrier Editorial
                | Semaine | Thème Principal | Canaux |
                |---------|------------------|--------|
                | 1 | Lancement produit | FB, IG, Email |
                | 2 | Témoignages clients | LinkedIn, Blog |
                | 3 | Promotion spéciale | Tous canaux |
                """)

            with tab3:
                # Créer le dossier templates s'il n'existe pas
                templates_dir = Path("templates")
                templates_dir.mkdir(exist_ok=True)
                
                template_path = "templates/marketing_template.docx"
                if Path(template_path).exists():
                    with open(template_path, "rb") as f:
                        st.download_button(
                            "📥 Template Stratégie Marketing",
                            data=f,
                            file_name="template_strategie.docx",
                            mime="application/octet-stream"
                        )
                else:
                    st.warning("Template non trouvé dans le dossier 'templates'")

        st.markdown("---")
        st.markdown("### 📤 Exporter le Rapport")

        pdf_buffer = create_simple_pdf(st.session_state.last_prediction)

        if pdf_buffer:
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="💾 Télécharger PDF Complet",
                    data=pdf_buffer,
                    file_name=st.session_state.filename_pdf,
                    mime="application/pdf",
                    use_container_width=True
                )
            with col2:
                if st.button("🔄 Générer une Nouvelle Analyse", use_container_width=True):
                    del st.session_state.last_prediction
                    st.rerun()
        else:
            st.error("Erreur lors de la génération du PDF")

    # --- Section Historique
    if 'history' in st.session_state and st.session_state.history:
        st.sidebar.markdown("---")
        st.sidebar.markdown("## 📚 Historique")

        for i, analysis in enumerate(reversed(st.session_state.history)):
            with st.sidebar.expander(f"Analyse #{len(st.session_state.history)-i}", expanded=False):
                quality_badge = ""
                if analysis.get('quality') == "excellent":
                    quality_badge = " 🏆"
                elif analysis.get('quality') == "good":
                    quality_badge = " ⭐"
                
                st.markdown(f"""
                **Date**: {analysis['date']}
                **Budget**: {analysis['params']['budget']} €
                **Secteur**: {analysis['domain']}
                **Qualité**: {analysis.get('quality', 'normal').capitalize()}{quality_badge}
                """)
                if analysis.get('premium', False):
                    st.markdown("<span class='premium-badge'>Premium</span>", unsafe_allow_html=True)

    # --- Section Contact
    st.markdown("---")
    with st.container():
        st.subheader("📩 Contactez-moi")
        contact_col1, contact_col2 = st.columns(2)

        with contact_col1:
            with st.form("contact_form"):
                st.text_input("Votre nom", key="contact_name")
                st.text_input("Votre email", key="contact_email")
                st.selectbox("Sujet", ["Support technique", "Autre"], key="contact_subject")
                st.text_area("Message", key="contact_message")

                if st.form_submit_button("Envoyer"):
                    if st.session_state.contact_name and st.session_state.contact_email:
                        st.success("Message envoyé! Nous vous répondrons sous 24h.")
                    else:
                        st.warning("Veuillez remplir les champs obligatoires")

        with contact_col2:
            st.markdown("""
            **📞 Support **
            Disponible du Samedi au Jeudi
            9h-18h

            **📧 Email**
            chehbounesofiane@gmail.com

            **🏢 Lieu**
            Algérie
            """)

            # Créer le dossier images s'il n'existe pas
            images_dir = Path("images")
            images_dir.mkdir(exist_ok=True)
            
            # Insérer le QR Code ici en utilisant le chemin du fichier
            qr_image_path = "images/qr-code.png"
            if Path(qr_image_path).exists():
                try:
                    st.image(qr_image_path, caption="Scannez pour nous contacter", width=150)
                except:
                    st.markdown("""
                    <div style="width:150px; height:150px; background-color:#25D366; 
                                display:flex; align-items:center; justify-content:center; 
                                color:white; font-weight:bold; border-radius:10px; margin: auto;">
                        QR Code
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Créer un placeholder pour le QR code
                st.markdown("""
                <div style="width:150px; height:150px; background-color:#25D366; 
                            display:flex; align-items:center; justify-content:center; 
                            color:white; font-weight:bold; border-radius:10px; margin: auto;">
                    QR Code
                </div>
                """, unsafe_allow_html=True)

    # ✅ Bouton WhatsApp bien placé sous le message
    st.markdown(
        """
        <div style="display: flex; justify-content: left; margin-top: 10px;">
            <a href="https://wa.me/213561677957" target="_blank" style="text-decoration: none;">
                <button style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-color: #25D366;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: 0.3s;
                ">
                    📱 Contactez-moi via WhatsApp
                </button>
            </a>
        </div>
        """,
    unsafe_allow_html=True
    )

    # 🎯 Citation inspirante aléatoire
    quotes = [
        """<div style="background-color:#f0f2f6; padding:15px; border-radius:8px; margin:15px 0; border-left:4px solid #6e00ff;">
        <em>🔍✨ "Dans un océan de données, l'analyste est le phare qui révèle les opportunités cachées." 🌊💎</em></div>""",

        """<div style="background-color:#e3f2fd; padding:15px; border-radius:8px; margin:15px 0; border-left:4px solid #2196f3;">
        <em>📈🎯 "Le marketing sans données, c'est comme conduire les yeux fermés..." 👀🚀</em></div>"""
    ]
    st.markdown(random.choice(quotes), unsafe_allow_html=True)

    # --- Footer avec votre photo et lien vers LinkedIn
    with st.sidebar:
        st.markdown("---")
        st.markdown("👉 Développé par : [Sofiane Chehboune](https://www.linkedin.com/in/sofiane-chehboune-5b243766/)")
        
        # Créer le dossier images s'il n'existe pas
        images_dir = Path("images")
        images_dir.mkdir(exist_ok=True)
        
        photo_path = "images/sofiane.jpg"
        if Path(photo_path).exists():
            try:
                st.image(photo_path, width=100)
            except:
                st.markdown("""
                <div style="width:100px; height:100px; background-color:#4F46E5; 
                            border-radius:50%; display:flex; align-items:center; 
                            justify-content:center; color:white; font-weight:bold;">
                    SC
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="width:100px; height:100px; background-color:#4F46E5; 
                        border-radius:50%; display:flex; align-items:center; 
                        justify-content:center; color:white; font-weight:bold;">
                SC
            </div>
            """, unsafe_allow_html=True)

    # --- Footer légal
    st.sidebar.markdown("""
                <div style="margin-top: 20px; border-top: 1px solid #ccc; padding-top: 10px; 
                text-align: center; font-size: 0.8em; color: #777;">
                Cette application utilise l'API Gemini de Google AI Studio.  
                © 2025 - Tous droits réservés.
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
