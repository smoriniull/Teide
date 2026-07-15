import streamlit as st
import uuid
from datetime import datetime
import time
import anthropic
from db import SupabaseConnection
from prompts import PROMPTS_MAP

# Configuración de página
st.set_page_config(page_title="Chatbot", layout="centered", initial_sidebar_state="collapsed")

# Mapeo de chatbot_id a (contexto, variables de prompt)
# 4 contextos × 2 variables de prompt = 8 chatbots
CHATBOT_CONFIG = {
    1: {"context": "A", "var1": "A", "var2": "A", "label": "Context A - Prompt Var1_A Var2_A"},
    2: {"context": "A", "var1": "A", "var2": "B", "label": "Context A - Prompt Var1_A Var2_B"},
    3: {"context": "B", "var1": "A", "var2": "A", "label": "Context B - Prompt Var1_A Var2_A"},
    4: {"context": "B", "var1": "A", "var2": "B", "label": "Context B - Prompt Var1_A Var2_B"},
    5: {"context": "C", "var1": "A", "var2": "A", "label": "Context C - Prompt Var1_A Var2_A"},
    6: {"context": "C", "var1": "A", "var2": "B", "label": "Context C - Prompt Var1_A Var2_B"},
    7: {"context": "D", "var1": "A", "var2": "A", "label": "Context D - Prompt Var1_A Var2_A"},
    8: {"context": "D", "var1": "A", "var2": "B", "label": "Context D - Prompt Var1_A Var2_B"},
}

def load_context(context_id: str) -> str:
    """Carga contexto desde fichero .txt"""
    try:
        with open(f"context_{context_id}.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Contexto no encontrado: context_{context_id}.txt")
        return ""

def get_chatbot_id():
    """Extrae chatbot_id de parámetros URL"""
    query_params = st.query_params
    chatbot_id = query_params.get("chatbot_id", None)
    
    if not chatbot_id:
        st.error("Parámetro 'chatbot_id' requerido en URL. Ej: ?chatbot_id=1")
        st.stop()
    
    try:
        chatbot_id = int(chatbot_id)
        if chatbot_id not in CHATBOT_CONFIG:
            st.error(f"chatbot_id debe estar entre 1 y 8. Recibido: {chatbot_id}")
            st.stop()
        return chatbot_id
    except ValueError:
        st.error("chatbot_id debe ser un número entero")
        st.stop()

def initialize_session(chatbot_id: int):
    """Inicializa variables de sesión"""
    if "participant_id" not in st.session_state:
        st.session_state.participant_id = str(uuid.uuid4())
    
    if "chatbot_id" not in st.session_state:
        st.session_state.chatbot_id = chatbot_id
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "turn_number" not in st.session_state:
        st.session_state.turn_number = 0
    
    if "db" not in st.session_state:
        st.session_state.db = SupabaseConnection()

def call_claude(user_message: str, system_prompt: str, context: str) -> tuple[str, float]:
    """
    Llama a Claude Haiku con contexto cerrado.
    Retorna: (respuesta, latencia_segundos)
    """
    try:
        api_key = st.secrets.get("anthropic_api_key", None)
        if not api_key:
            return "Error: API key de Anthropic no configurada. Contacta al administrador.", 0.0
    except:
        return "Error: No se puede acceder a configuración de Anthropic. Contacta al administrador.", 0.0
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Construir mensaje del sistema con contexto
    full_system = f"{system_prompt}\n\n---CONTEXTO---\n{context}"
    
    start_time = time.time()
    
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=full_system,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        latency = time.time() - start_time
        assistant_message = response.content[0].text
        
        return assistant_message, latency
    
    except Exception as e:
        st.error(f"Error al llamar a Claude: {e}")
        return "", 0.0

def log_interaction(participant_id: str, chatbot_id: int, turn_number: int, 
                   role: str, message: str, latency: float, condition_label: str):
    """Registra interacción en Supabase"""
    if st.session_state.db.connection is None:
        return
    
    st.session_state.db.log_interaction(
        participant_id=participant_id,
        condition_id=chatbot_id,
        condition_label=condition_label,
        turn_number=turn_number,
        role=role,
        message=message,
        latency_seconds=latency
    )

# Main
chatbot_id = get_chatbot_id()
initialize_session(chatbot_id)

config = CHATBOT_CONFIG[chatbot_id]
context = load_context(config["context"])
system_prompt = PROMPTS_MAP.get((config["var1"], config["var2"]), "")

if not system_prompt:
    st.error(f"Prompt no encontrado para var1={config['var1']}, var2={config['var2']}")
    st.stop()

# UI
st.title(f"Chatbot #{chatbot_id}")
st.caption(f"Session: {st.session_state.participant_id[:8]}...")

# Historial de mensajes
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input del usuario
user_input = st.chat_input("Tu mensaje...")

if user_input:
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.write(user_input)
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.turn_number += 1
    
    # Llamar a Claude
    with st.spinner("Pensando..."):
        assistant_response, latency = call_claude(user_input, system_prompt, context)
    
    # Mostrar respuesta
    with st.chat_message("assistant"):
        st.write(assistant_response)
    
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    
    # Registrar en Supabase
    log_interaction(
        participant_id=st.session_state.participant_id,
        chatbot_id=chatbot_id,
        turn_number=st.session_state.turn_number,
        role="user",
        message=user_input,
        latency=0.0,
        condition_label=config["label"]
    )
    
    log_interaction(
        participant_id=st.session_state.participant_id,
        chatbot_id=chatbot_id,
        turn_number=st.session_state.turn_number,
        role="assistant",
        message=assistant_response,
        latency=latency,
        condition_label=config["label"]
    )
    
    st.rerun()
