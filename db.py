import streamlit as st
from datetime import datetime

try:
    from supabase import create_client, Client
except ImportError:
    st.error("supabase-py no instalado. Ejecuta: pip install supabase")

class SupabaseConnection:
    """Gestor de conexión a Supabase y logging de interacciones"""
    
    def __init__(self):
        """Inicializa conexión a Supabase desde secrets"""
        try:
            supabase_url = st.secrets["supabase"]["url"]
            supabase_key = st.secrets["supabase"]["key"]
            
            self.connection: Client = create_client(supabase_url, supabase_key)
        except KeyError:
            st.warning("Configuración de Supabase no encontrada en secrets. Logging deshabilitado.")
            self.connection = None
        except Exception as e:
            st.warning(f"Error conectando a Supabase: {e}. Logging deshabilitado.")
            self.connection = None
    
    def log_interaction(self, participant_id: str, condition_id: int, condition_label: str,
                       turn_number: int, role: str, message: str, latency_seconds: float) -> bool:
        """
        Registra una interacción en la tabla 'interactions'
        
        Args:
            participant_id: UUID del participante
            condition_id: ID del chatbot (1-8)
            condition_label: Etiqueta descriptiva
            turn_number: Número de turno
            role: "user" o "assistant"
            message: Texto del mensaje
            latency_seconds: Latencia de respuesta (0 para user)
        
        Returns:
            True si éxito, False si fallo
        """
        if self.connection is None:
            return False
        
        try:
            data = {
                "participant_id": participant_id,
                "condition_id": condition_id,
                "condition_label": condition_label,
                "turn_number": turn_number,
                "role": role,
                "message": message,
                "latency_seconds": latency_seconds,
                "timestamp_utc": datetime.utcnow().isoformat() + "Z"
            }
            
            self.connection.table("interactions").insert(data).execute()
            return True
        
        except Exception as e:
            st.warning(f"Error logging a Supabase: {e}")
            return False
    
    def get_participant_interactions(self, participant_id: str) -> list:
        """Recupera todas las interacciones de un participante"""
        if self.connection is None:
            return []
        
        try:
            response = self.connection.table("interactions") \
                .select("*") \
                .eq("participant_id", participant_id) \
                .order("timestamp_utc") \
                .execute()
            return response.data
        except Exception as e:
            st.warning(f"Error recuperando interacciones: {e}")
            return []
