# Mapeo de (var1, var2) a prompt del sistema
# Personaliza cada prompt según tus necesidades

PROMPTS_MAP = {
    # Variable 1 = A, Variable 2 = A
    ("A", "A"): """Eres un asistente útil y conciso. 
Responde de manera breve y directa.
Mantén un tono profesional.""",
    
    # Variable 1 = A, Variable 2 = B
    ("A", "B"): """Eres un asistente amable y conversacional.
Responde con un tono cálido y accesible.
Incluye ejemplos cuando sea apropiado.""",
    
    # Variable 1 = B, Variable 2 = A
    ("B", "A"): """Eres un asistente especialista en tu dominio.
Responde con profundidad y rigurosidad.
Cita fuentes cuando sea posible.""",
    
    # Variable 1 = B, Variable 2 = B
    ("B", "B"): """Eres un asistente creativo y explorador.
Ofrece perspectivas nuevas e interesantes.
Haz preguntas que inviten a reflexionar.""",
}

# Etiquetas legibles para logging (opcional)
CONDITION_LABELS = {
    1: "Context_A_Var1_A_Var2_A",
    2: "Context_A_Var1_A_Var2_B",
    3: "Context_A_Var1_B_Var2_A",
    4: "Context_A_Var1_B_Var2_B",
    5: "Context_B_Var1_A_Var2_A",
    6: "Context_B_Var1_A_Var2_B",
    7: "Context_B_Var1_B_Var2_A",
    8: "Context_B_Var1_B_Var2_B",
}
