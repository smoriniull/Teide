import streamlit as st
from datetime import datetime
import json

class SupabaseConnection:
    """Gestor de conexión a Supabase y logging de interacciones"""
    
    def __init__(self):
        """Inicializa conexión a Supabase desde secrets"""
        self.connection = None
        self.use_supabase = False
    
        try:
            supabase_url = st.secrets.get("supabase", {}).get("url")
            supabase_key = st.secrets.get("supabase", {}).get("key")
        
            if not supabase_url or not supabase_key:
                print(f"[DB] Supabase no configurado - URL: {bool(supabase_url)}, KEY: {bool(supabase_key)}")
                return
        
            from supabase import create_client
            self.connection = create_client(supabase_url, supabase_key)
            self.use_supabase = True
            print(f"[DB] Supabase conectado exitosamente")
        except Exception as e:
            print(f"[DB] Error conectando Supabase: {e}")
            self.use_supabase = False
    
    def log_interaction(self, participant_id: str, condition_id: int, condition_label: str,
                   turn_number: int, role: str, message: str, latency_seconds: float) -> bool:
    print(f"[DB] Intentando guardar - use_supabase={self.use_supabase}, connection={bool(self.connection)}")
    
    
        """
        Registra una interacción en Supabase (si disponible) o localmente
        
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
        
        if self.use_supabase and self.connection:
            try:
                self.connection.table("interactions").insert(data).execute()
                return True
            except Exception as e:
                print(f"Error logging a Supabase: {e} (falling back to local logging)")
                return False
        else:
            # Logging local (opcional: guardar en sesión)
            if "interaction_log" not in st.session_state:
                st.session_state.interaction_log = []
            st.session_state.interaction_log.append(data)
            return True
    
    def get_participant_interactions(self, participant_id: str) -> list:
        """Recupera todas las interacciones de un participante"""
        if self.use_supabase and self.connection:
            try:
                response = self.connection.table("interactions") \
                    .select("*") \
                    .eq("participant_id", participant_id) \
                    .order("timestamp_utc") \
                    .execute()
                return response.data
            except Exception as e:
                print(f"Error recuperando interacciones: {e}")
                return []
        else:
            # Retorna log local si está disponible
            if "interaction_log" in st.session_state:
                return [log for log in st.session_state.interaction_log 
                       if log.get("participant_id") == participant_id]
            return []
