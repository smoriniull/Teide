# Sistema de 8 Chatbots con Claude Haiku + Streamlit Cloud + Supabase

## Estructura

- **app.py** — Aplicación principal Streamlit
- **prompts.py** — 4 prompts (combinaciones de var1 × var2)
- **db.py** — Conexión y logging a Supabase
- **context_A.txt, context_B.txt** — Contextos cerrados (knowledge base)
- **requirements.txt** — Dependencias Python
- **secrets_example.toml** — Plantilla de secrets

## Pasos de Setup

### 1. Preparar Supabase

1. Crear tabla en Supabase:
```sql
CREATE TABLE interactions (
  id BIGSERIAL PRIMARY KEY,
  participant_id TEXT NOT NULL,
  condition_id INT,
  condition_label TEXT,
  turn_number INT,
  role TEXT,
  message TEXT,
  latency_seconds NUMERIC,
  timestamp_utc TIMESTAMPTZ NOT NULL
);
```

2. Obtener:
   - `supabase_url` (Settings → API → Project URL)
   - `supabase_key` (Settings → API → anon public key)

### 2. Preparar GitHub

1. Crear repositorio público en GitHub
2. Subir estos archivos:
   - app.py
   - prompts.py
   - db.py
   - requirements.txt
   - context_A.txt
   - context_B.txt
   - .gitignore

**NO subir:** `secrets_example.toml` (renombrarlo a `.gitignore`)

### 3. Streamlit Cloud Deployment

1. Ir a https://share.streamlit.io/
2. Conectar tu repo de GitHub
3. Seleccionar:
   - Repository: tu-usuario/tu-repo
   - Branch: main
   - Main file path: app.py

4. Ir a **Settings → Secrets** y pegar (desde `secrets_example.toml`):
```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"
```

5. Deploy — ¡Listo!

## URLs para Participantes

Cada encuestado accede con su chatbot asignado:

```
https://tu-usuario-streamlit.streamlit.app/?chatbot_id=1
https://tu-usuario-streamlit.streamlit.app/?chatbot_id=2
... hasta ?chatbot_id=8
```

## Mapeo Interno (8 Chatbots)

| ID | Context | Var1 | Var2 |
|:--:|:-------:|:----:|:----:|
| 1  | A       | A    | A    |
| 2  | A       | A    | B    |
| 3  | A       | B    | A    |
| 4  | A       | B    | B    |
| 5  | B       | A    | A    |
| 6  | B       | A    | B    |
| 7  | B       | B    | A    |
| 8  | B       | B    | B    |

## Personalización

### Contextos
- Editar `context_A.txt` y `context_B.txt` con tu knowledge base
- Los cambios se reflejan inmediatamente al recargar en Streamlit Cloud

### Prompts
- Editar `prompts.py` con tus instrucciones de sistema
- Cambios en Streamlit Cloud tras `git push`

## Datos Registrados

Cada interacción guarda:
- `participant_id` — UUID único
- `condition_id` — ID del chatbot (1-8)
- `condition_label` — Etiqueta descriptiva
- `turn_number` — Número del turno
- `role` — "user" o "assistant"
- `message` — Texto
- `latency_seconds` — Tiempo de respuesta (solo para assistant)
- `timestamp_utc` — Marca temporal

## Acceso a Datos

Consultar Supabase → Table Editor → `interactions`

## Troubleshooting

**"No context file found"**
→ Verificar que `context_A.txt` y `context_B.txt` están en el repo

**"Supabase connection failed"**
→ Verificar URL y key en Streamlit Cloud → Settings → Secrets

**"Invalid chatbot_id"**
→ URL debe tener `?chatbot_id=1` a `?chatbot_id=8`
