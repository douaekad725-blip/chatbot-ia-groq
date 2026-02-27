import streamlit as st
import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Configuration
st.set_page_config(page_title="🤖 Mon Chatbot IA", page_icon="🤖", layout="centered", initial_sidebar_state="collapsed")
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

# CSS personnalisé
st.markdown("""
<style>
    .chat-message { padding: 1rem; border-radius: 10px; margin: 10px 0; }
    .user-message { background-color: #e3f2fd; border-left: 5px solid #2196F3; }
    .bot-message { background-color: #f1f8e9; border-left: 5px solid #4CAF50; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Personas
PERSONAS = {
    "🤖 Assistant Standard": "Tu es un assistant intelligent et utile. Si tu ne connais pas une réponse, dis-le honnêtement.",
    "👨‍🏫 Professeur Patient": "Tu es un professeur patient qui explique clairement. Si tu ne sais pas, admets-le.",
    "🎯 Expert Professionnel": "Tu es un expert précis. Tu ne donnes que des informations vérifiées. Tu dis 'Je ne sais pas' si nécessaire.",
    "😄 Ami Sympathique": "Tu es un ami chaleureux et honnête. Tu ne inventes pas d'informations.",
    "🔧 Développeur Senior": "Tu es un développeur senior. Tu donnes du code correct et tu admets tes limites."
}

# Fonctions utilitaires
def save_conversation(conversation, filename=None):
    if filename is None:
        filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    os.makedirs("conversations", exist_ok=True)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"💬 CONVERSATION - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n{'='*60}\n\n")
            for msg in conversation:
                if msg["role"] == "system": continue
                emoji = "👤" if msg["role"] == "user" else "🤖"
                f.write(f"{emoji} {msg['role'].upper()}: {msg['content']}\n\n")
            f.write(f"{'='*60}\n✅ Fin\n")
        return filename
    except Exception as e:
        st.error(f"❌ Erreur sauvegarde: {e}")
        return None

def display_message(content, role):
    css_class = "user-message" if role == "user" else "bot-message"
    label = "👤 <b>Toi:</b>" if role == "user" else "🤖 <b>Bot:</b>"
    st.markdown(f'<div class="chat-message {css_class}">{label}<br>{content}</div>', unsafe_allow_html=True)

# Initialisation session state
for key, default in {"messages": [], "persona_choice": "🤖 Assistant Standard", "conversation_started": False}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Sidebar
with st.sidebar:
    st.title("⚙️ Options")
    st.markdown("---")
    persona_choice = st.selectbox("🎭 Style du bot:", list(PERSONAS.keys()), index=list(PERSONAS.keys()).index(st.session_state.persona_choice))
    st.session_state.persona_choice = persona_choice
    if st.button("🗑️ Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_started = False
        st.rerun()
    st.markdown("---")
    if st.button("💾 Sauvegarder", use_container_width=True) and st.session_state.messages:
        file = save_conversation(st.session_state.messages)
        if file: st.success(f"✅ {file}")
    if not API_KEY:
        st.error("❌ Clé API manquante dans .env")

# Interface principale
st.title("🤖 Mon Chatbot IA")
st.markdown("---")

# Affichage historique
for message in st.session_state.messages:
    if message["role"] != "system":
        display_message(message["content"], message["role"])

st.markdown("---")
user_input = st.chat_input("Posez votre question...")

# Traitement
if user_input:
    if not API_KEY:
        st.error("❌ Clé API non configurée! Vérifie ton fichier .env")
        st.stop()
    
    display_message(user_input, "user")
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    if user_input.lower() == "exit":
        st.markdown("### 👋 Au revoir!")
        st.stop()
    
    system_prompt = PERSONAS.get(st.session_state.persona_choice, PERSONAS["🤖 Assistant Standard"])
    api_messages = [{"role": "system", "content": system_prompt}] + [m for m in st.session_state.messages if m["role"] != "system"]
    
    with st.spinner("🤖 Réflexion..."):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": api_messages, "temperature": 0.3},
                timeout=30
            )
            response.raise_for_status()
            bot_reply = response.json()["choices"][0]["message"]["content"]
            display_message(bot_reply, "assistant")
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            
            if not st.session_state.conversation_started:
                st.session_state.conversation_started = True
                st.info("💡 Astuce: Pense à sauvegarder ta conversation dans le menu!")
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout: Réessaie!")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
