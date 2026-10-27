import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Croqu'Mois", page_icon="🍏", layout="wide")

# --- CHARTE GRAPHIQUE (CSS SUPPLÉMENTAIRE) ---
st.markdown("""
    <style>
    /* Fusion parfaite du logo avec le fond de l'application */
    img {
        mix-blend-mode: multiply;
    }
    
    /* Application de l'orange d'accentuation au survol des boutons */
    div.stButton > button {
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #f39c12 !important;
        border-color: #f39c12 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- GESTION DE LA BARRE LATÉRALE (Logo & API) ---
with st.sidebar:# 1. Le logo tout en haut avec une taille réduite (ex: 150 pixels)
    # Utilisation de colonnes pour centrer parfaitement l'image
    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        st.image("assets/logo.png", use_container_width=True)

    st.header("⚙️ À propos")
    st.markdown("**Projet AAA - Advanced AI Algorithms**")
    st.info("L'Intelligence Artificielle est prête et configurée.")
    
# --- CONFIGURATION AUTOMATIQUE DE L'API ---
# Récupération de la clé depuis les secrets Streamlit
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("Erreur de configuration : Clé API introuvable dans les secrets.")
    st.stop() # Arrête l'exécution de l'application si la clé n'est pas trouvée

# --- ONGLETS DE L'APPLICATION ---
tab1, tab2 = st.tabs(["📅 Planification & Courses", "📸 Anti-Gaspi (Scan Frigo)"])

# ==========================================
# ONGLET 1 : PLANIFICATION HEBDOMADAIRE
# ==========================================
with tab1:
    st.header("Configure ta semaine")

    col1, col2 = st.columns(2)

    with col1:
        # Étape 1 : Budget
        budget_mensuel = st.number_input("Budget alimentaire mensuel (€)", min_value=30, max_value=500, value=150, step=10)
        budget_semaine = round(budget_mensuel / 4.33, 2) # Moyenne de semaines dans un mois
        st.info(f"💡 Budget alloué pour cette semaine : **{budget_semaine} €**")

        # Étape 2 : Situation personnelle
        situations = st.multiselect(
            "Quelle est ta situation cette semaine ?",
            ["Période d'examens (repas rapides)", "Prise de masse (sport)", "Fin de mois (ultra économique)", "Mon conjoint/ami est là (repas pour 2)", "Semaine très chargée"],
            default=["Période d'examens (repas rapides)"]
        )
        autre_situation = st.text_input("Autre situation particulière ? (ex: je suis végétarien, pas de porc, etc.)")

    with col2:
        # Étape 3 : Équipements
        equipements = st.multiselect(
            "Quels équipements as-tu à disposition ?",
            ["Micro-ondes", "Plaques de cuisson", "Four", "Air fryer", "Poêle", "Casserole", "Mixeur", "Cuiseur à riz"],
            default=["Micro-ondes", "Plaques de cuisson", "Poêle", "Casserole"]
        )

        repas_exterieur = st.multiselect(
            "Jours sans accès à un micro-ondes le midi (repas froids nécessaires) :",
            ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        )

    # Initialisation de la mémoire (HORS du bouton)
    if "planning_genere" not in st.session_state:
        st.session_state.planning_genere = None

    # Étape 4 & 5 : Génération
    if st.button("🚀 Générer mon planning et ma liste de courses", use_container_width=True):
        with st.spinner("L'IA Croqu'Mois analyse tes contraintes et crée ton menu..."):
            try:
                # Construction du prompt corrigé avec les Emoji Cards
                prompt = f"""
                Tu es un assistant culinaire spécialisé pour les étudiants.
                Voici le profil de l'étudiant pour cette semaine :
    - Budget : {budget_semaine} euros. Tu DOIS le respecter.
    - Situations : {', '.join(situations)} {autre_situation}.
    - Équipements : {', '.join(equipements)}. Ne propose AUCUNE recette nécessitant un équipement non listé.
    - Jours repas froids : {', '.join(repas_exterieur)}.
                    
                    Génère :
    1. Un planning de repas pour 7 jours (midi et soir). Pour CHAQUE repas, utilise STRICTEMENT ce code HTML pour créer une carte de repas avec une icône emoji générée sur mesure :
    
                    <div style="display: flex; align-items: center; margin-bottom: 20px; background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                        <div style="background-color: #f2f9f6; width: 70px; height: 70px; border-radius: 12px; display: flex; justify-content: center; align-items: center; font-size: 35px; margin-right: 20px; flex-shrink: 0; border: 1px solid #e4f0ea;">
                            [INSERER_UN_SEUL_EMOJI_ICI]
                        </div>
                        <div>
                            <h4 style="margin: 0; color: #29a073; font-size: 1.1em; padding-bottom: 3px;">Nom du plat</h4>
                            <i style="color: #666; font-size: 0.9em;">⏱️ Temps de préparation</i><br>
                            <span style="font-size: 0.9em; color: #333;">Brève description des ingrédients utilisés.</span>
                        </div>
                    </div>
    
                    Sépare IMPÉRATIVEMENT le planning et les courses avec ce titre exact : ### LISTE DE COURSES
                    
                    2. Une liste de courses mutualisée et organisée par catégories avec un emoji au début de chaque titre. Inclus l'estimation du prix par ingrédient pour prouver que le total respecte les {budget_semaine} euros.
                    """

                model = genai.GenerativeModel('gemini-3.5-flash-lite')
                response = model.generate_content(prompt)
                st.session_state.planning_genere = response.text

            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la communication avec l'IA : {e}")

    # Affichage interactif (HORS du bouton, pour rester affiché au rechargement)
    if st.session_state.planning_genere:
        texte = st.session_state.planning_genere

        if "### LISTE DE COURSES" in texte:
            planning, courses = texte.split("### LISTE DE COURSES")

            st.markdown(planning, unsafe_allow_html=True)
            st.markdown("---")
            st.header("🛒 Ta Liste de Courses")

            # Génération des cases à cocher dynamiques
            for i, ligne in enumerate(courses.split('\n')):
                ligne_propre = ligne.strip()
                if ligne_propre.startswith('-') or ligne_propre.startswith('*'):
                    texte_checkbox = ligne_propre[1:].strip()
                    # Une clé unique "key" est requise par Streamlit dans une boucle
                    st.checkbox(texte_checkbox, key=f"course_{i}")
                elif ligne_propre:
                    st.markdown(ligne_propre)
        else:
            st.markdown(texte, unsafe_allow_html=True)

# ==========================================
# ONGLET 2 : FONCTIONNALITÉ ANTI-GASPI
# ==========================================
with tab2:
    st.header("📸 Fonctionnalité Anti-Gaspillage")
    st.write("Prends en photo l'intérieur de ton frigo ou tes placards, et l'IA te trouvera une recette avec ce qu'il te reste !")

    # Choix entre upload et caméra
    option_image = st.radio("Comment veux-tu fournir l'image ?", ["Télécharger une image", "Prendre une photo (Webcam)"])

    img_file_buffer = None
    if option_image == "Télécharger une image":
        img_file_buffer = st.file_uploader("Upload la photo de tes restes", type=['png', 'jpg', 'jpeg'])
    else:
        img_file_buffer = st.camera_input("Prends une photo de tes ingrédients")

    if img_file_buffer is not None:
        image = Image.open(img_file_buffer)
        st.image(image, caption="Tes ingrédients", use_container_width=True)

        if st.button("🪄 Trouver une recette avec ces restes", use_container_width=True):
            with st.spinner("L'IA analyse tes ingrédients..."):
                try:
                    prompt_vision = f"""
                    Agis comme un chef anti-gaspillage pour étudiant.
                    Analyse cette image et liste les ingrédients que tu peux identifier.
                    Ensuite, propose UNE seule recette simple, délicieuse et réalisable avec tout ou partie de ces ingrédients.
                    Garde à l'esprit que l'étudiant possède ces équipements : {', '.join(equipements)}.
                    Donne les étapes de préparation étape par étape.
                    """
                    model_vision = genai.GenerativeModel('gemini-3.5-flash-lite')
                    response_vision = model_vision.generate_content([prompt_vision, image])

                    st.success("Recette trouvée !")
                    st.markdown(response_vision.text)
                except Exception as e:
                    st.error(f"Erreur avec l'analyse d'image : {e}")