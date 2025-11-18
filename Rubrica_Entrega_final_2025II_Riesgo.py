import streamlit as st
import pandas as pd
import datetime
import io
import json

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly no está instalado. Las visualizaciones de radar no estarán disponibles. Instale con: `pip install plotly`")

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Evaluación de Artículos - Riesgo Financiero",
    page_icon="📊",
    layout="wide"
)

# --- Paleta de Colores Institucional ---
USTA_PALETTE = {
    "primary": "#0a2f6b",  # Azul institucional
    "secondary": "#1d4f91",  # Azul medio
    "accent": "#f9a602",  # Dorado
    "teal": "#1c9c9c",  # Apoyo complementario
    "neutral_light": "#f5f7fa",
    "neutral_dark": "#17213c",
}

# --- Definición de la Rúbrica ---
RUBRIC_DATA = {
    "A": {
        "name": "COMPONENTE A: INFORME TÉCNICO (HTML + RMARKDOWN)",
        "short_name": "Componente A",
        "weight": 40,
        "criteria": [
            {
                "id": "A1", "name": "Estado del arte y contextualización", "weight": 4,
                "levels": {
                    "insuficiente": "Ausente o irrelevante. No sitúa el tema en un contexto científico.",
                    "basico": "Contextualización débil, escasa conexión con el campo del riesgo financiero.",
                    "satisfactorio": "Presenta una revisión clara del tema, aunque con limitada profundidad crítica o alcance bibliográfico.",
                    "destacado": "Revisa críticamente múltiples fuentes, sitúa el artículo en un debate científico actual y justifica su relevancia con solidez."
                }
            },
            {
                "id": "A2", "name": "Comprensión y análisis exploratorio de datos (AED)", "weight": 6,
                "levels": {
                    "insuficiente": "No se presenta AED o es inaplicable.",
                    "basico": "Análisis incompleto o con errores metodológicos graves.",
                    "satisfactorio": "Realiza un AED básico con gráficos y resúmenes, pero sin profundidad analítica.",
                    "destacado": "Realiza un AED completo: detecta patrones, asimetrías, outliers, relaciones entre variables y justifica transformaciones."
                }
            },
            {
                "id": "A3", "name": "Imputación de datos", "weight": 5,
                "levels": {
                    "insuficiente": "Omite el tratamiento de datos faltantes.",
                    "basico": "Usa imputación inadecuada o sin explicación.",
                    "satisfactorio": "Aplica un método válido (ej. media, KNN), pero sin comparación ni justificación profunda.",
                    "destacado": "Evalúa mecanismos de pérdida (MCAR/MAR), compara métodos y elige el más apropiado con fundamentación."
                }
            },
            {
                "id": "A4", "name": "Ingeniería de características", "weight": 5,
                "levels": {
                    "insuficiente": "No aplica ingeniería de variables.",
                    "basico": "Características poco relevantes o mal construidas.",
                    "satisfactorio": "Genera nuevas variables útiles, aunque con poca originalidad o justificación limitada.",
                    "destacado": "Diseña variables innovadoras bien fundamentadas (índices, ratios) que aportan valor sustancial."
                }
            },
            {
                "id": "A5", "name": "Documentación técnica y reproducibilidad", "weight": 6,
                "levels": {
                    "insuficiente": "No compila o es imposible replicar.",
                    "basico": "Dificultad para seguir el flujo; falta de comentarios o errores.",
                    "satisfactorio": "Código funcional y entendible, aunque con mejoras en estilo o documentación.",
                    "destacado": "Código totalmente reproducible, bien comentado, con buenas prácticas. HTML bien formateado."
                }
            },
            {
                "id": "A6", "name": "Crítica metodológica y argumentación grupal", "weight": 8,
                "levels": {
                    "insuficiente": "Ausente o meramente descriptiva.",
                    "basico": "Crítica superficial o desenfocada.",
                    "satisfactorio": "Identifica algunos aspectos débiles del artículo, pero sin profundidad analítica.",
                    "destacado": "Ofrece una crítica rigurosa basada en evidencia, cuestiona supuestos, limitaciones y sesgos con propuestas alternativas."
                }
            },
            {
                "id": "A7", "name": "Bibliografía y normas académicas", "weight": 6,
                "levels": {
                    "insuficiente": "Sin referencias o plagio.",
                    "basico": "Algunas referencias faltantes o fuentes no académicas.",
                    "satisfactorio": "Citas completas con pequeños errores de formato.",
                    "destacado": "Cumple rigurosamente con las normas, usa fuentes académicas de alto impacto."
                }
            }
        ]
    },
    "B": {
        "name": "COMPONENTE B: DASHBOARD INTERACTIVO",
        "short_name": "Componente B",
        "weight": 30,
        "criteria": [
            {
                "id": "B1", "name": "Claridad del propósito y audiencia", "weight": 5,
                "levels": {
                    "insuficiente": "Sin propósito claro. No es evidente a quién está dirigido.",
                    "basico": "Objetivo ambiguo. Audiencia poco explícita.",
                    "satisfactorio": "Propósito identificado, pero audiencia poco explícita.",
                    "destacado": "Propósito claro, audiencia bien definida y todas las funciones están alineadas con sus necesidades."
                }
            },
            {
                "id": "B2", "name": "Selección y priorización de KPIs", "weight": 6,
                "levels": {
                    "insuficiente": "Ausentes o incorrectos.",
                    "basico": "Indicadores poco representativos.",
                    "satisfactorio": "Incluye KPIs relevantes, pero con redundancia o falta de enfoque.",
                    "destacado": "KPIs altamente pertinentes, jerarquizados y contextualizados."
                }
            },
            {
                "id": "B3", "name": "Calidad técnica y visual de visualizaciones", "weight": 7,
                "levels": {
                    "insuficiente": "Mal diseñados o con errores graves.",
                    "basico": "Errores visuales (ej. 3D innecesario, escalas engañosas).",
                    "satisfactorio": "Gráficos correctos, aunque con detalles mejorables (leyendas, colores).",
                    "destacado": "Visualizaciones precisas, estéticamente pulidas, accesibles y libres de distorsiones."
                }
            },
            {
                "id": "B4", "name": "Interactividad y navegabilidad", "weight": 6,
                "levels": {
                    "insuficiente": "Sin interactividad.",
                    "basico": "Interactividad mínima o con errores.",
                    "satisfactorio": "Funcionalidades básicas implementadas (filtros), pero con limitaciones.",
                    "destacado": "Alta interactividad intuitiva que permite explorar múltiples escenarios."
                }
            },
            {
                "id": "B5", "name": "Insights y accionabilidad", "weight": 6,
                "levels": {
                    "insuficiente": "No aporta insights.",
                    "basico": "Limitado valor práctico.",
                    "satisfactorio": "Presenta información útil, pero requiere interpretación adicional.",
                    "destacado": "Destaca hallazgos clave con alertas, resúmenes dinámicos y sugerencias para la acción."
                }
            }
        ]
    },
    "C": {
        "name": "COMPONENTE C: EXPOSICIÓN ORAL EN VIDEO (10–15 min)",
        "short_name": "Componente C",
        "weight": 30,
        "criteria": [
            {
                "id": "C1", "name": "Dominio conceptual y técnico", "weight": 6,
                "levels": {
                    "insuficiente": "Falta dominio. Inseguridad conceptual evidente.",
                    "basico": "Conocimiento parcial; confunde conceptos.",
                    "satisfactorio": "Demuestra buen conocimiento, aunque con algunas vacilaciones.",
                    "destacado": "Explica con claridad conceptos complejos, responde preguntas implícitas y defiende decisiones."
                }
            },
            {
                "id": "C2", "name": "Uso estratégico del dashboard", "weight": 6,
                "levels": {
                    "insuficiente": "No lo utiliza.",
                    "basico": "Lo menciona brevemente sin demostración.",
                    "satisfactorio": "Muestra el dashboard, pero con poca integración narrativa.",
                    "destacado": "Usa el dashboard como herramienta narrativa, navegando con propósito y destacando insights."
                }
            },
            {
                "id": "C3", "name": "Estructura y claridad comunicativa", "weight": 6,
                "levels": {
                    "insuficiente": "Caótica. Difícil de seguir.",
                    "basico": "Difícil de seguir; sin introducción o cierre.",
                    "satisfactorio": "Estructura clara, aunque con digresiones o ritmo irregular.",
                    "destacado": "Narrativa bien estructurada, lenguaje preciso, transiciones suaves."
                }
            },
            {
                "id": "C4", "name": "Síntesis y manejo del tiempo", "weight": 6,
                "levels": {
                    "insuficiente": "Muy por fuera del tiempo (±3 min).",
                    "basico": "Fuera de tiempo (±2 min) o desbalanceado.",
                    "satisfactorio": "Ligera sobreexposición o omisión de puntos clave.",
                    "destacado": "Tiempo optimizado, contenido conciso y enfocado en lo más relevante."
                }
            },
            {
                "id": "C5", "name": "Argumentación crítica y pensamiento reflexivo", "weight": 6,
                "levels": {
                    "insuficiente": "Reproduce sin cuestionar.",
                    "basico": "Crítica superficial o ausente.",
                    "satisfactorio": "Plantea críticas válidas, aunque con enfoque limitado.",
                    "destacado": "Ofrece una reflexión profunda sobre validez, aplicabilidad y ética del estudio."
                }
            }
        ]
    }
}

def initialize_session_state(rubric):
    """Inicializa el session_state para cada criterio de la rúbrica."""
    for comp_data in rubric.values():
        for criterion in comp_data["criteria"]:
            score_key = f"{criterion['id']}_score"
            feedback_key = f"{criterion['id']}_feedback"
            
            if score_key not in st.session_state:
                st.session_state[score_key] = 3.0
            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = ""

def reset_rubric_state(rubric):
    """Reinicia los valores de puntuaciones, comentarios y datos del proyecto."""
    for comp_data in rubric.values():
        for criterion in comp_data["criteria"]:
            st.session_state[f"{criterion['id']}_score"] = 3.0
            st.session_state[f"{criterion['id']}_feedback"] = ""

    st.session_state["project_name_input"] = ""
    st.session_state["eval_date_input"] = datetime.date.today()
    st.session_state["num_members_input"] = 1

    member_keys = [key for key in st.session_state.keys() if key.startswith("member_")]
    for key in member_keys:
        del st.session_state[key]

def inject_brand_theme():
    """Aplica estilos personalizados alineados con la paleta de colores institucional."""
    st.markdown(
        f"""
        <style>
            :root {{
                --primary-color: {USTA_PALETTE['primary']};
                --secondary-color: {USTA_PALETTE['secondary']};
                --accent-color: {USTA_PALETTE['accent']};
                --teal-color: {USTA_PALETTE['teal']};
                --neutral-light: {USTA_PALETTE['neutral_light']};
                --neutral-dark: {USTA_PALETTE['neutral_dark']};
            }}

            .stApp {{
                background: linear-gradient(180deg, rgba(10,47,107,0.05) 0%, rgba(28,156,156,0.03) 100%);
            }}

            .st-emotion-cache-1vxn2o5, .st-emotion-cache-1avcm0n {{
                color: var(--neutral-dark);
            }}

            h1, h2, h3, h4 {{
                color: var(--primary-color) !important;
            }}

            section[data-testid="stSidebar"] {{
                background: var(--neutral-light);
                color: var(--neutral-dark);
                border-right: 1px solid rgba(10,47,107,0.15);
            }}

            section[data-testid="stSidebar"] * {{
                color: var(--neutral-dark) !important;
            }}

            section[data-testid="stSidebar"] label {{
                font-weight: 600;
            }}

            section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {{
                background: #ffffff;
                border: 1px solid rgba(10,47,107,0.25);
                border-radius: 8px;
            }}

            section[data-testid="stSidebar"] .stNumberInput input,
            section[data-testid="stSidebar"] .stTextInput input {{
                background: #ffffff;
                border: 1px solid rgba(10,47,107,0.25);
                border-radius: 8px;
                color: var(--neutral-dark) !important;
            }}

            section[data-testid="stSidebar"] .stDownloadButton button {{
                background-color: var(--accent-color);
                color: var(--neutral-dark) !important;
                font-weight: 600;
            }}

            section[data-testid="stSidebar"] button[kind="secondary"] {{
                background-color: rgba(10,47,107,0.08);
                border: 1px solid rgba(10,47,107,0.25);
                color: var(--neutral-dark) !important;
            }}

            div[data-baseweb="slider"] > div > div {{
                background: var(--secondary-color);
            }}

            div[data-baseweb="slider"] > div > div > div {{
                background: var(--accent-color);
            }}

            .stProgress > div > div > div > div {{
                background-color: var(--accent-color);
            }}

            .st-expander {{
                border: 1px solid rgba(10,47,107,0.2);
                box-shadow: 0 3px 12px rgba(10,47,107,0.08);
            }}

            .st-info {{
                background-color: rgba(28,156,156,0.08);
                border-left: 4px solid var(--teal-color);
            }}

            .stDataFrame {{
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 3px 14px rgba(15,33,58,0.08);
            }}

            .stDataFrame thead tr {{
                background-color: var(--primary-color) !important;
                color: white !important;
            }}

            .stDataFrame tbody tr:nth-child(even) {{
                background-color: rgba(10,47,107,0.05);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

@st.cache_data
def get_auto_feedback(score, levels_tuple):
    """Genera retroalimentación automática basada en el puntaje."""
    levels = dict(levels_tuple)
    if score <= 2.9:
        return {"level": "Insuficiente", "desc": levels['insuficiente'], "color": "#ff4444"}
    elif score <= 3.5:
        return {"level": "Básico", "desc": levels['basico'], "color": "#ffa726"}
    elif score <= 4.2:
        return {"level": "Satisfactorio", "desc": levels['satisfactorio'], "color": "#66bb6a"}
    else:
        return {"level": "Destacado", "desc": levels['destacado'], "color": "#1c9c9c"}

def display_project_info_sidebar():
    """Muestra los campos de entrada para la información del proyecto en la barra lateral."""
    st.sidebar.title("Información del Proyecto")
    
    if "project_name_input" not in st.session_state:
        st.session_state["project_name_input"] = ""
    project_name = st.sidebar.text_input(
        "Nombre del Artículo/Proyecto",
        key="project_name_input"
    ).strip()

    if "eval_date_input" not in st.session_state:
        st.session_state["eval_date_input"] = datetime.date.today()
    eval_date = st.sidebar.date_input(
        "Fecha de Evaluación",
        key="eval_date_input"
    )

    st.sidebar.subheader("Integrantes del equipo")

    if "num_members_input" not in st.session_state:
        st.session_state["num_members_input"] = 1
    num_members = int(
        st.sidebar.number_input(
            "Número de Integrantes",
            min_value=1,
            max_value=10,
            step=1,
            format="%d",
            key="num_members_input"
        )
    )

    member_key_prefix = "member_"
    stale_member_keys = [
        key for key in st.session_state.keys()
        if key.startswith(member_key_prefix) and int(key.split("_")[1]) >= num_members
    ]
    for key in stale_member_keys:
        del st.session_state[key]

    members = []
    for i in range(num_members):
        member_key = f"{member_key_prefix}{i}"
        if member_key not in st.session_state:
            st.session_state[member_key] = ""
        member_name = st.sidebar.text_input(
            f"Nombre Integrante {i+1}",
            key=member_key
        ).strip()
        members.append(member_name)

    validated = bool(project_name and all(members))
    if validated:
        st.sidebar.success("Datos del proyecto completos.")
    else:
        st.sidebar.warning("Por favor, complete toda la información del proyecto.")

    members_display = ", ".join(filter(None, members))
    
    return {
        "project_name": project_name,
        "eval_date": eval_date,
        "members": members_display,
        "validated": validated
    }

def display_component_criteria(component_data):
    """Muestra la interfaz de calificación (sliders, expanders) para un componente."""
    st.header(f"{component_data['name']} ({component_data['weight']}%)")
    
    for criterion in component_data["criteria"]:
        st.markdown(f"### {criterion['id']}. {criterion['name']} `({criterion['weight']}%)`")
        score_key = f"{criterion['id']}_score"
        feedback_key = f"{criterion['id']}_feedback"
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.slider(
                "Puntaje (0.0 - 5.0)",
                min_value=0.0,
                max_value=5.0,
                step=0.1,
                value=float(st.session_state[score_key]),
                key=score_key,
                help="📊 Escalas: Insuficiente (0-2.9) | Básico (3.0-3.5) | Satisfactorio (3.6-4.2) | Destacado (4.3-5.0)"
            )
            st.text_area(
                "Comentarios Específicos", 
                key=feedback_key,
                height=100
            )

        with col2:
            current_score = st.session_state[score_key]
            levels_tuple = tuple(criterion['levels'].items())
            feedback = get_auto_feedback(current_score, levels_tuple)
            
            st.markdown(f"""<div style='padding: 1rem; background-color: {feedback['color']}15; 
                        border-left: 4px solid {feedback['color']}; border-radius: 8px;'>
                        <strong style='color: {feedback['color']};'>Nivel: {feedback['level']} ({current_score:.1f})</strong><br><br>
                        {feedback['desc']}</div>""", unsafe_allow_html=True)

        with st.expander("Ver descripción completa de niveles"):
            levels = criterion['levels']
            cols = st.columns(4)
            cols[0].markdown(f"**Insuficiente (0.0-2.9)**\n\n{levels['insuficiente']}")
            cols[1].markdown(f"**Básico (3.0-3.5)**\n\n{levels['basico']}")
            cols[2].markdown(f"**Satisfactorio (3.6-4.2)**\n\n{levels['satisfactorio']}")
            cols[3].markdown(f"**Destacado (4.3-5.0)**\n\n{levels['destacado']}")
        
        st.divider()

def create_radar_chart(component_scores):
    """Crea un gráfico de radar para visualizar el desempeño por componente."""
    if not PLOTLY_AVAILABLE:
        return None
    
    categories = [comp['short_name'] for comp in component_scores.values()]
    values = [comp['normalized_score'] * 100 for comp in component_scores.values()]
    
    # Cerrar el polígono
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(28, 156, 156, 0.3)',
        line=dict(color=USTA_PALETTE['teal'], width=2),
        marker=dict(size=8, color=USTA_PALETTE['accent']),
        name='Desempeño'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%',
                showline=True,
                linecolor='rgba(10,47,107,0.2)',
                gridcolor='rgba(10,47,107,0.1)'
            ),
            angularaxis=dict(
                linecolor='rgba(10,47,107,0.2)',
                gridcolor='rgba(10,47,107,0.1)'
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=80, r=80, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def calculate_results(rubric):
    """Calcula la calificación final ponderada y prepara los datos para el DF."""
    total_score_pct = 0
    component_scores = {}
    criteria_details = []
    component_summary_rows = []

    for comp_id, comp_data in rubric.items():
        comp_score_pct = 0
        short_name = comp_data.get("short_name", comp_data["name"])
        for criterion in comp_data["criteria"]:
            score = st.session_state[f"{criterion['id']}_score"]
            feedback = st.session_state[f"{criterion['id']}_feedback"]
            weight_pct = criterion['weight']
            
            criterion_weighted_points = (score / 5.0) * weight_pct
            comp_score_pct += criterion_weighted_points
            
            criteria_details.append({
                "Componente": short_name,
                "Criterio_ID": criterion['id'],
                "Criterio_Nombre": criterion['name'],
                "Puntaje (sobre 5.0)": score,
                "Peso (%)": weight_pct,
                "Puntaje_Ponderado (sobre 100)": criterion_weighted_points,
                "Feedback": feedback
            })
            
        normalized_component_score = (comp_score_pct / comp_data['weight']) if comp_data['weight'] else 0
        component_scores[comp_id] = {
            "name": comp_data['name'],
            "short_name": short_name,
            "score_pct": comp_score_pct,
            "weight": comp_data['weight'],
            "normalized_score": normalized_component_score
        }
        total_score_pct += comp_score_pct
        component_summary_rows.append({
            "Componente": short_name,
            "Peso (%)": comp_data['weight'],
            "Puntaje obtenido (pts)": comp_score_pct,
            "Avance (%)": normalized_component_score * 100,
            "Calificación (0-5)": normalized_component_score * 5
        })

    final_grade_5_0_scale = (total_score_pct / 100.0) * 5.0
    
    results_df = pd.DataFrame(criteria_details)
    component_summary_df = pd.DataFrame(component_summary_rows)
    
    return {
        "final_grade": final_grade_5_0_scale,
        "total_score_pct": total_score_pct,
        "component_scores": component_scores,
        "details_df": results_df,
        "component_summary_df": component_summary_df
    }

def save_evaluation_to_json(rubric, project_info):
    """Guarda la evaluación actual en formato JSON."""
    evaluation_data = {
        "project_info": {
            "project_name": project_info.get("project_name", ""),
            "eval_date": str(project_info.get("eval_date", "")),
            "members": project_info.get("members", "")
        },
        "scores": {},
        "feedbacks": {}
    }
    
    for comp_data in rubric.values():
        for criterion in comp_data["criteria"]:
            crit_id = criterion['id']
            evaluation_data["scores"][crit_id] = st.session_state.get(f"{crit_id}_score", 3.0)
            evaluation_data["feedbacks"][crit_id] = st.session_state.get(f"{crit_id}_feedback", "")
    
    return json.dumps(evaluation_data, indent=2, ensure_ascii=False).encode('utf-8')

def load_evaluation_from_json(json_data, rubric):
    """Carga una evaluación desde un archivo JSON."""
    try:
        evaluation_data = json.loads(json_data.decode('utf-8'))
        
        project_info = evaluation_data.get("project_info", {})
        st.session_state["project_name_input"] = project_info.get("project_name", "")
        st.session_state["eval_date_input"] = datetime.datetime.strptime(
            project_info.get("eval_date", str(datetime.date.today())), "%Y-%m-%d"
        ).date()
        
        # Cargar integrantes
        members_str = project_info.get("members", "")
        members_list = members_str.split(", ")
        st.session_state["num_members_input"] = len(members_list)
        for i, member in enumerate(members_list):
            st.session_state[f"member_{i}"] = member
        
        scores = evaluation_data.get("scores", {})
        feedbacks = evaluation_data.get("feedbacks", {})
        
        for comp_data in rubric.values():
            for criterion in comp_data["criteria"]:
                crit_id = criterion['id']
                if crit_id in scores:
                    st.session_state[f"{crit_id}_score"] = scores[crit_id]
                if crit_id in feedbacks:
                    st.session_state[f"{crit_id}_feedback"] = feedbacks[crit_id]
        
        return True, "Evaluación cargada exitosamente"
    except Exception as e:
        return False, f"Error al cargar la evaluación: {str(e)}"

def display_results_sidebar(results, project_info, placeholder, rubric):
    """Muestra los resultados (calificación, barra, desglose) en la barra lateral."""
    with placeholder.container():
        st.sidebar.divider()
        st.sidebar.header("Resultados de la Evaluación")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.button(
                "🔄 Reiniciar",
                type="secondary",
                use_container_width=True,
                on_click=reset_rubric_state,
                args=(rubric,)
            )
        with col2:
            if project_info["validated"]:
                json_data = save_evaluation_to_json(rubric, project_info)
                safe_filename = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in project_info['project_name'])
                st.download_button(
                    label="💾 Guardar",
                    data=json_data,
                    file_name=f"eval_{safe_filename}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        uploaded_file = st.sidebar.file_uploader(
            "📂 Cargar evaluación guardada",
            type=['json'],
            help="Cargue un archivo JSON de evaluación previamente guardado"
        )
        
        if uploaded_file is not None:
            success, message = load_evaluation_from_json(uploaded_file.getvalue(), rubric)
            if success:
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.error(message)

        st.sidebar.divider()
        
        # Mostrar calificación final
        final_grade = results["final_grade"]
        total_pct = results["total_score_pct"]
        
        st.sidebar.metric(
            "Calificación Final",
            f"{final_grade:.2f} / 5.0",
            f"{total_pct:.1f} pts"
        )
        
        st.sidebar.progress(total_pct / 100.0)
        
        # Clasificación de desempeño
        if final_grade >= 4.3:
            st.sidebar.success("✨ Destacado")
        elif final_grade >= 3.6:
            st.sidebar.info("✅ Satisfactorio")
        elif final_grade >= 3.0:
            st.sidebar.warning("⚠️ Básico")
        else:
            st.sidebar.error("❌ Insuficiente")
        
        st.sidebar.divider()
        
        # Desglose por componente
        st.sidebar.subheader("Desglose por Componente")
        for comp_id, comp_info in results["component_scores"].items():
            percentage = comp_info["normalized_score"] * 100
            st.sidebar.metric(
                label=comp_info["short_name"],
                value=f"{comp_info['score_pct']:.1f} / {comp_info['weight']}",
                delta=f"{percentage:.1f}%"
            )

# --- MAIN APP ---
def main():
    inject_brand_theme()
    initialize_session_state(RUBRIC_DATA)
    
    st.title("📊 Evaluación de Artículos - Riesgo Financiero")
    st.markdown("**Sistema de Evaluación por Rúbrica** | Análisis Crítico de Artículos Científicos")
    
    # Sidebar para información del proyecto
    project_info = display_project_info_sidebar()
    
    # Placeholder para resultados en sidebar
    sidebar_placeholder = st.sidebar.empty()
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs([
        "📋 Componente A: Informe Técnico",
        "📊 Componente B: Dashboard",
        "🎤 Componente C: Exposición Oral"
    ])
    
    with tab1:
        display_component_criteria(RUBRIC_DATA["A"])
    
    with tab2:
        display_component_criteria(RUBRIC_DATA["B"])
    
    with tab3:
        display_component_criteria(RUBRIC_DATA["C"])
    
    # Calcular resultados
    results = calculate_results(RUBRIC_DATA)
    
    # Mostrar resultados en sidebar
    display_results_sidebar(results, project_info, sidebar_placeholder, RUBRIC_DATA)
    
    # Sección de visualización y exportación al final
    st.divider()
    st.header("📊 Visualización del Desempeño")
    
    if PLOTLY_AVAILABLE:
        radar_chart = create_radar_chart(results["component_scores"])
        if radar_chart:
            col_chart, col_stats = st.columns([2, 1])
            with col_chart:
                st.plotly_chart(radar_chart, use_container_width=True, key="radar_main")
            with col_stats:
                st.markdown("#### Estadísticas por Componente")
                st.dataframe(
                    results["component_summary_df"],
                    hide_index=True,
                    use_container_width=True
                )
    
    st.divider()
    st.header("📥 Exportar Resultados")
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        # Exportar CSV
        csv_buffer = io.StringIO()
        results["details_df"].to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_data = csv_buffer.getvalue().encode('utf-8-sig')
        
        safe_filename = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in project_info['project_name'])
        
        st.download_button(
            label="📄 Descargar CSV",
            data=csv_data,
            file_name=f"evaluacion_{safe_filename}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_exp2:
        # Guardar JSON
        if project_info["validated"]:
            json_data = save_evaluation_to_json(RUBRIC_DATA, project_info)
            safe_filename = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in project_info['project_name'])
            st.download_button(
                label="💾 Guardar JSON",
                data=json_data,
                file_name=f"eval_{safe_filename}.json",
                mime="application/json",
                use_container_width=True,
                help="Descargue este archivo para continuar la evaluación más tarde"
            )
    
    with col_exp3:
        # Ver reporte HTML
        if st.button("📑 Ver Reporte HTML", use_container_width=True):
            st.session_state.show_html_report = True
    
    # Botón adicional para descargar HTML
    if st.session_state.get("show_html_report", False):
        # Generar HTML completo para descarga
        fecha_str = project_info["eval_date"].strftime('%Y-%m-%d')
        
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Evaluación - {project_info['project_name']}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #17213c;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(180deg, rgba(10,47,107,0.05) 0%, rgba(28,156,156,0.03) 100%);
        }}
        h1 {{ color: #0a2f6b; border-bottom: 3px solid #f9a602; padding-bottom: 10px; }}
        h2 {{ color: #1d4f91; margin-top: 30px; }}
        h3 {{ color: #0a2f6b; }}
        .metric-box {{
            background: white;
            border-left: 4px solid #1c9c9c;
            padding: 15px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        .component {{
            background: #f5f7fa;
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
            border: 1px solid rgba(10,47,107,0.1);
        }}
        .criterion {{
            background: white;
            padding: 12px;
            margin: 10px 0;
            border-radius: 6px;
            border-left: 3px solid #f9a602;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        th {{
            background: #0a2f6b;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:nth-child(even) {{
            background: rgba(10,47,107,0.05);
        }}
        .chart-container {{
            width: 100%;
            max-width: 600px;
            margin: 30px auto;
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }}
        @media print {{
            body {{ background: white; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <h1>📊 Reporte de Evaluación - Riesgo Financiero</h1>
    
    <div class="metric-box">
        <p><strong>Artículo/Proyecto:</strong> {project_info['project_name']}</p>
        <p><strong>Fecha de Evaluación:</strong> {fecha_str}</p>
        <p><strong>Integrantes:</strong> {project_info['members']}</p>
    </div>
    
    <h2>📊 Calificación Final</h2>
    <div class="metric-box">
        <h3>Puntaje Total: {results['total_score_pct']:.1f} / 100.0</h3>
        <h3>Calificación: {results['final_grade']:.2f} / 5.0</h3>
    </div>
    
    <h2>📋 Desglose por Componentes</h2>
"""
        
        for comp_id, comp_info in results["component_scores"].items():
            percentage = comp_info["normalized_score"] * 100
            calificacion = comp_info["normalized_score"] * 5
            html_content += f"""
    <div class="component">
        <h3>{comp_info['name']}</h3>
        <ul>
            <li><strong>Puntaje:</strong> {comp_info['score_pct']:.1f} / {comp_info['weight']} puntos</li>
            <li><strong>Porcentaje:</strong> {percentage:.1f}%</li>
            <li><strong>Calificación:</strong> {calificacion:.2f} / 5.0</li>
        </ul>
    </div>
"""
        
        # Agregar gráfico de radar
        categories = [comp['short_name'] for comp in results["component_scores"].values()]
        values = [comp['normalized_score'] * 100 for comp in results["component_scores"].values()]
        categories_js = json.dumps(categories)
        values_js = json.dumps(values)
        
        html_content += f"""
    <h2>📊 Visualización del Desempeño</h2>
    <div class="chart-container">
        <canvas id="radarChart"></canvas>
    </div>
    
    <script>
        const ctx = document.getElementById('radarChart');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: {categories_js},
                datasets: [{{
                    label: 'Desempeño (%)',
                    data: {values_js},
                    fill: true,
                    backgroundColor: 'rgba(28, 156, 156, 0.2)',
                    borderColor: 'rgb(28, 156, 156)',
                    pointBackgroundColor: 'rgb(249, 166, 2)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(28, 156, 156)'
                }}]
            }},
            options: {{
                scales: {{
                    r: {{
                        angleLines: {{ display: true }},
                        suggestedMin: 0,
                        suggestedMax: 100,
                        ticks: {{
                            callback: function(value) {{ return value + '%'; }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: true }}
                }}
            }}
        }});
    </script>
    
    <h2>📊 Tabla de Estadísticas</h2>
    <table>
        <thead>
            <tr>
                <th>Componente</th>
                <th>Peso (%)</th>
                <th>Puntaje obtenido (pts)</th>
                <th>Avance (%)</th>
                <th>Calificación (0-5)</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for _, row in results["component_summary_df"].iterrows():
            html_content += f"""
            <tr>
                <td>{row['Componente']}</td>
                <td>{row['Peso (%)']}</td>
                <td>{row['Puntaje obtenido (pts)']:.2f}</td>
                <td>{row['Avance (%)']:.1f}%</td>
                <td>{row['Calificación (0-5)']:.2f}</td>
            </tr>
"""
        
        html_content += """
        </tbody>
    </table>
    
    <h2>📝 Detalle de Criterios</h2>
"""
        
        for comp_id, comp_data in RUBRIC_DATA.items():
            html_content += f"<h3>{comp_data['name']}</h3>\n"
            for criterion in comp_data["criteria"]:
                score = st.session_state[f"{criterion['id']}_score"]
                feedback = st.session_state[f"{criterion['id']}_feedback"]
                weighted_score = (score / 5.0) * criterion['weight']
                
                html_content += f"""
    <div class="criterion">
        <h4>{criterion['id']}. {criterion['name']} ({criterion['weight']}%)</h4>
        <ul>
            <li><strong>Puntaje:</strong> {score:.1f} / 5.0</li>
            <li><strong>Ponderado:</strong> {weighted_score:.2f} pts</li>
            <li><strong>Retroalimentación:</strong> {feedback if feedback else "<em>Sin comentarios</em>"}</li>
        </ul>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        safe_filename = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in project_info['project_name'])
        
        st.download_button(
            label="⬇️ Descargar Reporte HTML",
            data=html_content.encode('utf-8'),
            file_name=f"reporte_{safe_filename}.html",
            mime="text/html",
            use_container_width=False
        )
    
    # Mostrar reporte HTML
    if st.session_state.get("show_html_report", False):
        with st.expander("📄 Reporte HTML Completo", expanded=True):
            fecha_str = project_info["eval_date"].strftime('%Y-%m-%d')
            
            report_md = f"""
# Reporte de Evaluación - Riesgo Financiero

**Artículo/Proyecto:** {project_info['project_name']}  
**Fecha de Evaluación:** {fecha_str}  
**Integrantes:** {project_info['members']}

---

## 📊 Calificación Final

**Puntaje Total:** {results['total_score_pct']:.1f} / 100.0  
**Calificación:** {results['final_grade']:.2f} / 5.0  

---

## 📋 Desglose por Componentes

"""
            
            for comp_id, comp_info in results["component_scores"].items():
                percentage = comp_info["normalized_score"] * 100
                calificacion = comp_info["normalized_score"] * 5
                report_md += f"""
### {comp_info['name']}

- **Puntaje:** {comp_info['score_pct']:.1f} / {comp_info['weight']} puntos
- **Porcentaje:** {percentage:.1f}%
- **Calificación:** {calificacion:.2f} / 5.0

"""
            
            
            report_md += "\n---\n\n## 📊 Visualización del Desempeño\n\n"
            
            # Mostrar el gráfico de radar si Plotly está disponible
            if PLOTLY_AVAILABLE:
                radar_chart = create_radar_chart(results["component_scores"])
                if radar_chart:
                    st.plotly_chart(radar_chart, use_container_width=True, key="radar_report")
            
            # Tabla de resumen
            st.dataframe(
                results["component_summary_df"],
                hide_index=True,
                use_container_width=True
            )
            
            report_md += "\n---\n\n## 📝 Detalle de Criterios\n\n"
            
            for comp_id, comp_data in RUBRIC_DATA.items():
                report_md += f"### {comp_data['name']}\n\n"
                for criterion in comp_data["criteria"]:
                    score = st.session_state[f"{criterion['id']}_score"]
                    feedback = st.session_state[f"{criterion['id']}_feedback"]
                    weighted_score = (score / 5.0) * criterion['weight']
                    
                    report_md += f"""
**{criterion['id']}. {criterion['name']}** ({criterion['weight']}%)

- Puntaje: {score:.1f} / 5.0
- Ponderado: {weighted_score:.2f} pts
- Retroalimentación: {feedback if feedback else "_Sin comentarios_"}

"""
            
            st.markdown(report_md, unsafe_allow_html=True)
            st.info("💡 **Consejo:** Para guardar como PDF, use Ctrl+P (o Cmd+P) y seleccione 'Guardar como PDF'")

if __name__ == "__main__":
    main()
