import streamlit as st
import uuid
from datetime import datetime
import time
import anthropic
from db import SupabaseConnection
from prompts import PROMPTS_MAP

# DEBUG - mostrar errores en pantalla
if "error_log" not in st.session_state:
    st.session_state.error_log = []

def log_error(msg):
    st.session_state.error_log.append(msg)
    st.error(f"DEBUG: {msg}")

# Mostrar log de errores acumulados
if "error_log" in st.session_state and st.session_state.error_log:
    st.error("ERRORES ACUMULADOS:")
    for err in st.session_state.error_log[-5:]:  # últimos 5
        st.write(f"• {err}")


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

def log_error(msg):
    if "error_log" not in st.session_state:
        st.session_state.error_log = []
    st.session_state.error_log.append(msg)

def call_claude(user_message: str, system_prompt: str, context: str) -> tuple[str, float]:
    api_key = None
    
    try:
        if "anthropic_api_key" in st.secrets:
            api_key = st.secrets["anthropic_api_key"]
            log_error(f"API key found (len={len(api_key)})")
        else:
            log_error("API key NOT in secrets")
    except Exception as e:
        log_error(f"Error reading secrets: {e}")
        return "", 0.0
    
    if not api_key:
        log_error("API key is empty")
        return "", 0.0
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        log_error("Anthropic client created")
    except Exception as e:
        log_error(f"Error creating client: {e}")
        return "", 0.0
    
    full_system = f"{system_prompt}\n\n---CONTEXTO---\n{context}"
    start_time = time.time()
    
    try:
        log_error("Calling Claude API...")
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=full_system,
            messages=[{"role": "user", "content": user_message}]
        )
        latency = time.time() - start_time
        assistant_message = response.content[0].text
        log_error(f"Response received in {latency:.2f}s")
        return assistant_message, latency
    except Exception as e:
        log_error(f"API Error: {type(e).__name__}: {str(e)[:100]}")
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
