import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- POP-UP DE CONFIRMATION ---
@st.dialog("⚠️ Changement de langue / Language Change")
def confirm_lang_change(nouvelle_langue):
    st.write("Changer de langue va effacer le planning et la recette actuels. Es-tu sûr ?")
    st.write("*Changing language will erase the current plan and recipe. Are you sure?*")
    
    col1, col2 = st.columns(2)
    if col1.button("Oui / Yes", use_container_width=True):
        st.session_state.langue_actuelle = nouvelle_langue
        st.session_state.planning_genere = None
        st.session_state.recette_generee = None
        st.rerun()
    if col2.button("Non / No", use_container_width=True):
        st.session_state.radio_langue = st.session_state.langue_actuelle
        st.rerun()

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

# --- INITIALISATION DE LA MÉMOIRE GLOBALE ---
if "langue_actuelle" not in st.session_state:
    st.session_state.langue_actuelle = "Français"
if "radio_langue" not in st.session_state:
    st.session_state.radio_langue = "Français"
if "planning_genere" not in st.session_state:
    st.session_state.planning_genere = None
if "recette_generee" not in st.session_state:
    st.session_state.recette_generee = None

# --- GESTION DES LANGUES (INTERCEPTION) ---
langue_selectionnee = st.sidebar.radio(
    "🌐 Langue / Language", 
    ["Français", "English"],
    key="radio_langue"
)

# Si l'utilisateur clique sur une nouvelle langue
if langue_selectionnee != st.session_state.langue_actuelle:
    # On vérifie si du contenu a déjà été généré
    if st.session_state.planning_genere or st.session_state.recette_generee:
        confirm_lang_change(langue_selectionnee) # Ouvre la pop-up
    else:
        st.session_state.langue_actuelle = langue_selectionnee
        st.rerun()

# On verrouille la langue de l'interface sur le choix confirmé
langue = st.session_state.langue_actuelle

if langue == "Français":
    UI = {
        "tab1": "📅 Planification & Courses", "tab2": "📸 Anti-Gaspi (Scan Frigo)",
        "about": "⚙️ À propos", "ready": "L'Intelligence Artificielle est prête et configurée.",
        "conf_title": "Configure ta semaine",
        "budget": "Budget alimentaire mensuel (€)", "budget_info": "💡 Budget alloué pour cette semaine :",
        "sit": "Quelle est ta situation cette semaine ?",
        "sit_opts": ["Période d'examens (repas rapides)", "Prise de masse (sport)", "Fin de mois (ultra économique)", "Mon conjoint/ami est là (repas pour 2)", "Semaine très chargée"],
        "autre": "Autre situation particulière ? (ex: je suis végétarien, pas de porc, etc.)",
        "equip": "Quels équipements as-tu à disposition ?",
        "equip_opts": ["Micro-ondes", "Plaques de cuisson", "Four", "Air fryer", "Poêle", "Casserole", "Mixeur", "Cuiseur à riz"],
        "froids": "Jours sans accès à un micro-ondes le midi (repas froids nécessaires) :",
        "froids_opts": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"],
        "btn_plan": "🚀 Générer mon planning et ma liste de courses", "spin_plan": "L'IA Croqu'Mois analyse tes contraintes et crée ton menu...",
        "delim": "### LISTE DE COURSES", "list_title": "🛒 Ta Liste de Courses",
        "prompt_lang": "Rédige TOUTE ta réponse (planning, descriptions, ingrédients) UNIQUEMENT en Français. Dans le HTML, utilise 'Temps de préparation'.",
        "t2_title": "📸 Fonctionnalité Anti-Gaspillage", "t2_desc": "Prends en photo l'intérieur de ton frigo ou tes placards, et l'IA te trouvera une recette avec ce qu'il te reste !",
        "t2_radio": ["Télécharger une image", "Prendre une photo (Webcam)"],
        "t2_up": "Upload la photo de tes restes", "t2_cam": "Prends une photo de tes ingrédients",
        "t2_cap": "Tes ingrédients",
        "t2_btn": "🪄 Trouver une recette avec ces restes", "t2_spin": "L'IA analyse tes ingrédients...",
        "t2_prompt": "Agis comme un chef anti-gaspillage pour étudiant. Rédige ta réponse UNIQUEMENT en Français.",
        "found": "Recette trouvée !", "err_vis": "Erreur avec l'analyse d'image :",
        "err_api": "Erreur de configuration : Clé API introuvable dans les secrets."
    }
else:
    UI = {
        "tab1": "📅 Planning & Groceries", "tab2": "📸 Anti-Waste (Fridge Scan)",
        "about": "⚙️ About", "ready": "Artificial Intelligence is ready and configured.",
        "conf_title": "Configure your week",
        "budget": "Monthly food budget (€)", "budget_info": "💡 Budget allocated for this week:",
        "sit": "What is your situation this week?",
        "sit_opts": ["Exam period (quick meals)", "Bulking (sports)", "End of month (ultra economical)", "My partner/friend is here (meals for 2)", "Very busy week"],
        "autre": "Any other specific situation? (e.g., I'm vegetarian, no pork, etc.)",
        "equip": "What equipment do you have available?",
        "equip_opts": ["Microwave", "Stove", "Oven", "Air fryer", "Frying pan", "Pot", "Blender", "Rice cooker"],
        "froids": "Days without access to a microwave at noon (cold meals needed):",
        "froids_opts": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "btn_plan": "🚀 Generate my plan and grocery list", "spin_plan": "Croqu'Mois AI is analyzing your constraints and creating your menu...",
        "delim": "### GROCERY LIST", "list_title": "🛒 Your Grocery List",
        "prompt_lang": "Write your ENTIRE response (plan, descriptions, ingredients) ONLY in English. In the HTML, use 'Prep time'.",
        "t2_title": "📸 Anti-Waste Feature", "t2_desc": "Take a picture of the inside of your fridge or cupboards, and the AI will find you a recipe with what you have left!",
        "t2_radio": ["Upload an image", "Take a photo (Webcam)"],
        "t2_up": "Upload the photo of your leftovers", "t2_cam": "Take a photo of your ingredients",
        "t2_cap": "Your ingredients",
        "t2_btn": "🪄 Find a recipe with these leftovers", "t2_spin": "The AI is analyzing your ingredients...",
        "t2_prompt": "Act as an anti-waste chef for students. Write your response ONLY in English.",
        "found": "Recipe found!", "err_vis": "Error with image analysis:",
        "err_api": "Configuration error: API Key not found in secrets."
    }

# --- GESTION DE LA BARRE LATÉRALE (Logo & API) ---
with st.sidebar:# 1. Le logo tout en haut avec une taille réduite (ex: 150 pixels)
    # Utilisation de colonnes pour centrer parfaitement l'image
    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        st.image("assets/logo.png", use_container_width=True)

    st.header(UI["about"])
    st.markdown("**Projet AAA - Advanced AI Algorithms**")
    st.info(UI["ready"])
    
# --- CONFIGURATION AUTOMATIQUE DE L'API ---
# Récupération de la clé depuis les secrets Streamlit
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error(UI["err_api"])
    st.stop() # Arrête l'exécution de l'application si la clé n'est pas trouvée

# --- ONGLETS DE L'APPLICATION ---
tab1, tab2 = st.tabs([UI["tab1"], UI["tab2"]])

# ==========================================
# ONGLET 1 : PLANIFICATION HEBDOMADAIRE
# ==========================================
with tab1:
    st.header(UI["conf_title"])

    col1, col2 = st.columns(2)

    with col1:
        # Étape 1 : Budget
        budget_mensuel = st.number_input(UI["budget"], min_value=30, max_value=500, value=150, step=10)
        budget_semaine = round(budget_mensuel / 4.33, 2) # Moyenne de semaines dans un mois
        st.info(f"{UI['budget_info']} **{budget_semaine} €**")

        # Étape 2 : Situation personnelle
        situations = st.multiselect(
            UI["sit"],
            UI["sit_opts"],
            default=[UI["sit_opts"][0]]
        )
        autre_situation = st.text_input(UI["autre"])

    with col2:
        # Étape 3 : Équipements
        equipements = st.multiselect(
            UI["equip"],
            UI["equip_opts"],
            default=[UI["equip_opts"][0], UI["equip_opts"][1], UI["equip_opts"][4], UI["equip_opts"][5]]
        )

        repas_exterieur = st.multiselect(
            UI["froids"],
            UI["froids_opts"]
        )

    # Initialisation de la mémoire (HORS du bouton)
    if "planning_genere" not in st.session_state:
        st.session_state.planning_genere = None

    # Étape 4 & 5 : Génération
    if st.button(UI["btn_plan"], use_container_width=True):
        with st.spinner(UI["spin_plan"]):
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
    
                    Sépare IMPÉRATIVEMENT le planning et les courses avec ce titre exact : {UI['delim']}
                    
                    2. Une liste de courses mutualisée et organisée par catégories avec un emoji au début de chaque titre. Inclus l'estimation du prix par ingrédient pour prouver que le total respecte les {budget_semaine} euros.
                    
                    INSTRUCTION DE LANGUE OBLIGATOIRE : {UI['prompt_lang']}
                    """

                model = genai.GenerativeModel('gemini-3.5-flash-lite')
                response = model.generate_content(prompt)
                
                if response.parts:
                    st.session_state.planning_genere = response.text
                else:
                    st.error("L'IA n'a pas pu générer le texte. Veuillez réessayer. / The AI could not generate text. Please try again.")

            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la communication avec l'IA : {e}")

    # Affichage interactif (HORS du bouton, pour rester affiché au rechargement)
    if st.session_state.planning_genere:
        texte = st.session_state.planning_genere

        if UI["delim"] in texte:
            planning, courses = texte.split(UI["delim"])

            st.markdown(planning, unsafe_allow_html=True)
            st.markdown("---")
            st.header(UI["list_title"])

            # Génération des cases à cocher dynamiques
            for i, ligne in enumerate(courses.split('\n')):
                ligne_propre = ligne.strip()
                if ligne_propre.startswith('-') or ligne_propre.startswith('*'):
                    texte_checkbox = ligne_propre[1:].strip()
                    # Une clé unique "key" est requise par Streamlit dans une boucle
                    st.checkbox(texte_checkbox, key=f"course_{langue}_{i}")
                elif ligne_propre:
                    st.markdown(ligne_propre)
        else:
            st.markdown(texte, unsafe_allow_html=True)

# ==========================================
# ONGLET 2 : FONCTIONNALITÉ ANTI-GASPI
# ==========================================
with tab2:
    st.header(UI["t2_title"])
    st.write(UI["t2_desc"])

    # Choix entre upload et caméra
    option_image = st.radio("", UI["t2_radio"])

    img_file_buffer = None
    if option_image == UI["t2_radio"][0]:
        img_file_buffer = st.file_uploader(UI["t2_up"], type=['png', 'jpg', 'jpeg'])
    else:
        img_file_buffer = st.camera_input(UI["t2_cam"])

    if img_file_buffer is not None:
        image = Image.open(img_file_buffer)
        st.image(image, caption=UI["t2_cap"], use_container_width=True)

        if st.button(UI["t2_btn"], use_container_width=True):
            with st.spinner(UI["t2_spin"]):
                try:
                    prompt_vision = f"""
                    {UI['t2_prompt']}
                    Analyse cette image et liste les ingrédients que tu peux identifier.
                    Ensuite, propose UNE seule recette simple, délicieuse et réalisable avec tout ou partie de ces ingrédients.
                    Garde à l'esprit que l'étudiant possède ces équipements : {', '.join(equipements)}.
                    Donne les étapes de préparation étape par étape.
                    """
                    model_vision = genai.GenerativeModel('gemini-3.5-flash-lite')
                    response_vision = model_vision.generate_content([prompt_vision, image])

                    st.session_state.recette_generee = response_vision.text
                    
                except Exception as e:
                    st.error(f"{UI['err_vis']} {e}")

        if st.session_state.recette_generee:
            st.success(UI["found"])
            st.markdown(st.session_state.recette_generee)