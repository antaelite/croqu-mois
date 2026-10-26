import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="CampusCook AI", page_icon="🍲", layout="wide")

# --- TITRE ET INTRODUCTION ---
st.title("🎓 CampusCook AI : Ton assistant alimentaire étudiant")
st.markdown("Mange mieux, respecte ton budget et ne gaspille plus rien !")

# --- GESTION DE LA CLÉ API ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Entre ta clé API Gemini :", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("Clé API validée !")
    else:
        st.warning("Veuillez entrer une clé API pour faire fonctionner l'IA.")
        st.markdown("[Obtenir une clé API gratuite](https://aistudio.google.com/)")

    st.markdown("---")
    st.markdown("**Projet AAA - Advanced AI Algorithms**")

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

    # Étape 4 & 5 : Génération
    if st.button("🚀 Générer mon planning et ma liste de courses", use_container_width=True):
        if not api_key:
            st.error("Veuillez d'abord configurer votre clé API dans la barre latérale.")
        else:
            with st.spinner("L'IA CampusCook analyse tes contraintes et crée ton menu..."):
                try:
                    # Construction du prompt
                    prompt = f"""
                    Tu es un assistant culinaire spécialisé pour les étudiants.
                    Voici le profil de l'étudiant pour cette semaine :
                    - Budget pour la semaine : {budget_semaine} euros. Tu DOIS respecter ce budget.
                    - Situations particulières : {', '.join(situations)} {autre_situation}.
                    - Équipements disponibles : {', '.join(equipements)}. Ne propose AUCUNE recette nécessitant un équipement non listé (ex: pas de cuisson au four si 'Four' n'est pas coché).
                    - Jours nécessitant un repas froid le midi (facile à transporter) : {', '.join(repas_exterieur)}.

                    Génère :
                    1. Un planning de repas pour 7 jours (midi et soir). Sois varié mais réaliste financièrement. Précise le temps de préparation.
                    2. Une liste de courses mutualisée (optimisée pour éviter le gaspillage) avec l'estimation du prix par ingrédient pour montrer que ça rentre dans les {budget_semaine} euros.

                    Structure ta réponse en Markdown de façon claire (Titres, puces).
                    """

                    # Appel à l'API Gemini
                    model = genai.GenerativeModel('gemini-3.5-flash-lite')
                    response = model.generate_content(prompt)

                    st.success("Planning généré avec succès !")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"Une erreur s'est produite lors de la communication avec l'IA : {e}")

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
            if not api_key:
                st.error("Veuillez d'abord configurer votre clé API dans la barre latérale.")
            else:
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