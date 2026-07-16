import streamlit as st
from datetime import datetime

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
        """Registra una interacción en Supabase"""
        print(f"[DB] Intentando guardar - use_supabase={self.use_supabase}, connection={bool(self.connection)}")
        
        if not self.use_supabase or not self.connection:
            print("[DB] Supabase deshabilitado, logging local solo")
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
            
            print(f"[DB] Insertando: {participant_id[:8]}... turno {turn_number}")
            self.connection.table("interactions").insert(data).execute()
            print("[DB] Insertado exitosamente")
            return True
        
        except Exception as e:
            print(f"[DB] Error insertando: {e}")
            return False
    
    def get_participant_interactions(self, participant_id: str) -> list:
        """Recupera todas las interacciones de un participante"""
        if not self.use_supabase or not self.connection:
            return []
        
        try:
            response = self.connection.table("interactions") \
                .select("*") \
                .eq("participant_id", participant_id) \
                .order("timestamp_utc") \
                .execute()
            return response.data
        except Exception as e:
            print(f"[DB] Error recuperando: {e}")
            return []