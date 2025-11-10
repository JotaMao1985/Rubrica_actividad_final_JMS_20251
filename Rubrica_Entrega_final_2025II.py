import streamlit as st
import pandas as pd
import datetime
import io

try:
    import xlsxwriter  # noqa: F401
    EXCEL_WRITER_ENGINE = "xlsxwriter"
except ModuleNotFoundError:
    try:
        import openpyxl  # noqa: F401
        EXCEL_WRITER_ENGINE = "openpyxl"
    except ModuleNotFoundError:
        EXCEL_WRITER_ENGINE = None


USTA_PALETTE = {
    "primary": "#0a2f6b",  # Azul institucional
    "secondary": "#1d4f91",  # Azul medio
    "accent": "#f9a602",  # Dorado
    "teal": "#1c9c9c",  # Apoyo complementario
    "neutral_light": "#f5f7fa",
    "neutral_dark": "#17213c",
}

# --- DATOS DE LA RÚBRICA ---
# Se definen los datos de la rúbrica en una estructura de diccionario.
# Corregí el peso de A4 a 10% para que el Componente A sume 50%,
# basándome en el total de 50% indicado para el componente.
RUBRIC_DATA = {
    "A": {
        "name": "COMPONENTE A: INFORME ACADÉMICO",
        "short_name": "Componente A",
        "weight": 50,
        "criteria": [
            {
                "id": "A1", "name": "Base de Datos y Objetivos (Comprensión, documentación, objetivos y EDA)", "weight": 10,
                "levels": {
                    "insuficiente": "Omite o describe incorrectamente las variables. No define objetivos claros. El análisis exploratorio (EDA) es ausente o irrelevante.",
                    "basico": "Describe las variables superficialmente (p.ej., solo tipo de dato). Los objetivos son vagos. El EDA es una ejecución mecánica de gráficos sin interpretación.",
                    "satisfactorio": "Documenta adecuadamente el diccionario de datos, su origen y limpieza. Los objetivos son claros y medibles. El EDA es relevante y genera hipótesis iniciales.",
                    "destacado": "Provee una documentación exhaustiva (incluyendo sesgos y limitaciones de los datos). Los objetivos son específicos, medibles y relevantes (SMART). El EDA es profundo y guía directamente la modelación."
                }
            },
            {
                "id": "A2", "name": "Análisis Metodológico Aplicado (Aplicación y justificación de métodos)", "weight": 15,
                "levels": {
                    "insuficiente": "Aplica métodos estadísticos de forma incorrecta o inapropiada para el tipo de datos u objetivos. No se validan supuestos clave.",
                    "basico": "Aplica métodos de forma técnicamente correcta, pero sin justificar su idoneidad. La interpretación de resultados es literal y no se conecta con los objetivos.",
                    "satisfactorio": "Justifica la elección de los métodos en función de los objetivos y los datos. La aplicación es robusta, valida supuestos y la interpretación es correcta.",
                    "destacado": "Demuestra maestría al seleccionar y aplicar métodos, comparándolos con alternativas. La aplicación es elegante, robusta (p.ej., validación cruzada) y la interpretación es matizada."
                }
            },
            {
                "id": "A3", "name": "Pensamiento Crítico Metodológico (Limitaciones y métodos propuestos)", "weight": 15,
                "levels": {
                    "insuficiente": "No identifica limitaciones. Asume los resultados como verdades absolutas. No hay propuesta de análisis futuros.",
                    "basico": "Menciona limitaciones obvias (p.ej., 'se necesita más data'), pero sin analizar su impacto real en las conclusiones. La propuesta futura es vaga.",
                    "satisfactorio": "Discute críticamente las limitaciones de los métodos elegidos y su impacto en la validez de las inferencias. Propone análisis futuros pertinentes.",
                    "destacado": "Realiza una reflexión profunda sobre los sesgos, supuestos y el alcance real de las inferencias. Propone métodos futuros innovadores que abordan dichas limitaciones."
                }
            },
            {
                "id": "A4", "name": "Contextualización (Estado del Arte) (Revisión de literatura)", "weight": 10, # Peso ajustado de 5 a 10 para sumar 50%
                "levels": {
                    "insuficiente": "No incluye referencias o estas son irrelevantes (p.ej., blogs, Wikipedia). No hay conexión con el problema.",
                    "basico": "Incluye algunas referencias, pero sin una síntesis clara. Se limita a definir conceptos básicos.",
                    "satisfactorio": "Sitúa el problema en un contexto académico o de industria relevante, usando fuentes apropiadas (papers, reportes).",
                    "destacado": "Integra la literatura de forma crítica para justificar la elección del problema y los métodos, identificando un vacío que su análisis intenta llenar."
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
                "id": "B1", "name": "Propósito y Audiencia (Claridad y enfoque)", "weight": 5,
                "levels": {
                    "insuficiente": "El dashboard carece de un propósito claro. No es evidente a quién está dirigido ni qué problema resuelve.",
                    "basico": "El propósito es genérico ('mostrar los datos'). La audiencia no está definida, resultando en un dashboard poco enfocado.",
                    "satisfactorio": "El dashboard tiene un propósito claro y una audiencia objetivo definida. Los elementos visuales son pertinentes para esa audiencia.",
                    "destacado": "El propósito es estratégico y está alineado con una necesidad específica de la audiencia. Cada componente del dashboard contribuye directamente a ese propósito."
                }
            },
            {
                "id": "B2", "name": "KPIs y Priorización (Selección de métricas)", "weight": 7,
                "levels": {
                    "insuficiente": "No se definen KPIs. Se limita a mostrar datos brutos o métricas irrelevantes.",
                    "basico": "Los KPIs seleccionados son superficiales (p.ej., promedios simples) y no están priorizados.",
                    "satisfactorio": "Selecciona KPIs relevantes que responden a los objetivos del análisis. Hay una jerarquía visual clara.",
                    "destacado": "Selecciona y diseña KPIs estratégicos (p.ej., tasas de conversión, métricas de riesgo) que sintetizan la información compleja de forma inteligente."
                }
            },
            {
                "id": "B3", "name": "Calidad Técnica y Visual (Diseño y visualización)", "weight": 5,
                "levels": {
                    "insuficiente": "El dashboard es técnicamente inestable (lento, errores) o visualmente confuso (colores inadecuados, gráficos 3D, chartjunk).",
                    "basico": "El dashboard es funcional, pero el diseño es básico. La elección de gráficos es apropiada, pero la ejecución es mejorable (p.ej., etiquetas poco claras).",
                    "satisfactorio": "Diseño limpio, profesional y coherente. Las visualizaciones son técnicamente correctas y estéticamente agradables. Buena aplicación de principios de diseño (CRAP).",
                    "destacado": "Diseño excepcional que facilita la comprensión instantánea. Uso avanzado de la gramática de gráficos. El rendimiento es óptimo."
                }
            },
            {
                "id": "B4", "name": "Interactividad y Exploración (Filtros y Drill-down)", "weight": 6,
                "levels": {
                    "insuficiente": "No hay interactividad, o los filtros no funcionan / no tienen sentido. Es un informe estático.",
                    "basico": "La interactividad es básica (p.ej., un solo filtro general). No permite una exploración profunda de los datos.",
                    "satisfactorio": "Ofrece interactividad funcional (filtros, tooltips, drill-down) que permite al usuario explorar y responder preguntas secundarias.",
                    "destacado": "La interactividad es intuitiva y potente. Permite al usuario realizar análisis de escenarios o explorar relaciones complejas que no son evidentes a simple vista."
                }
            },
            {
                "id": "B5", "name": "Accionabilidad e Insights (Generación de valor)", "weight": 7,
                "levels": {
                    "insuficiente": "El dashboard es puramente descriptivo. No se extraen conclusiones claras ni se sugiere ninguna acción.",
                    "basico": "Los insights son obvios o simplemente repiten lo que muestra el gráfico ('las ventas subieron').",
                    "satisfactorio": "El dashboard revela patrones o insights relevantes. Se proponen recomendaciones lógicas basadas en los hallazgos.",
                    "destacado": "Genera insights no triviales y estratégicos. Las recomendaciones son accionables, priorizadas y tienen un impacto claro en la toma de decisiones de la audiencia."
                }
            }
        ]
    },
    "C": {
        "name": "COMPONENTE C: EXPOSICIÓN ORAL",
        "short_name": "Componente C",
        "weight": 20,
        "criteria": [
            {
                "id": "C1", "name": "Dominio Conceptual y Técnico (Manejo del tema y del dashboard)", "weight": 7,
                "levels": {
                    "insuficiente": "Muestra inseguridad conceptual evidente. Lee las diapositivas. Tiene dificultades técnicas para operar su propio dashboard.",
                    "basico": "Demuestra un manejo conceptual básico, pero se limita a lo memorizado. Utiliza el dashboard de forma mecánica, sin fluidez.",
                    "satisfactorio": "Demuestra un dominio sólido de los conceptos estadísticos y del contexto del problema. Navega el dashboard con fluidez para ilustrar sus puntos.",
                    "destacado": "Demuestra un dominio excepcional. Explica conceptos complejos con analogías simples y usa el dashboard como una herramienta dinámica de pensamiento."
                }
            },
            {
                "id": "C2", "name": "Estructura y Claridad (Flujo narrativo)", "weight": 4,
                "levels": {
                    "insuficiente": "Presentación desorganizada. Es difícil seguir el hilo conductor. El lenguaje es excesivamente técnico o demasiado simple.",
                    "basico": "La estructura es predecible (Introducción, Método, Resultado). La conexión entre secciones es débil.",
                    "satisfactorio": "Presenta una narrativa clara y lógica ('storytelling'). Adapta el lenguaje a la audiencia. Conecta el problema, el método y la solución de forma coherente.",
                    "destacado": "Presenta una narrativa cautivadora. Sintetiza magistralmente la información, enfocándose en el 'por qué' y el 'para qué', no solo en el 'qué'."
                }
            },
            {
                "id": "C3", "name": "Capacidad de Síntesis (Manejo del tiempo)", "weight": 3,
                "levels": {
                    "insuficiente": "Excede significativamente el tiempo límite, o termina muy pronto por falta de contenido. Se pierde en detalles irrelevantes.",
                    "basico": "Cubre los puntos principales, pero con un manejo del tiempo ajustado. Tiende a acelerar al final o a detenerse demasiado en el inicio.",
                    "satisfactorio": "Gestiona el tiempo de forma eficaz, asignando el énfasis adecuado a cada componente (problema, insights y recomendaciones).",
                    "destacado": "Realiza una presentación concisa y de alto impacto dentro del tiempo. Demuestra una gran capacidad para priorizar la información esencial."
                }
            },
            {
                "id": "C4", "name": "Argumentación y Q&A (Respuesta a preguntas)", "weight": 6,
                "levels": {
                    "insuficiente": "No puede responder a preguntas o las respuestas son evasivas/incorrectas. Se muestra a la defensiva.",
                    "basico": "Responde a preguntas fácticas, but titubea ante preguntas críticas, de profundización o sobre las limitaciones del análisis.",
                    "satisfactorio": "Responde con confianza y precisión a la mayoría de las preguntas. Puede defender sus elecciones metodológicas con argumentos sólidos.",
                    "destacado": "Responde con agilidad, profundidad y espíritu crítico. Utiliza las preguntas para expandir el análisis y demostrar un dominio que excede lo expuesto."
                }
            }
        ]
    }
}

# --- FUNCIONES HELPERS ---

def initialize_session_state(rubric):
    """
    Inicializa el st.session_state para cada criterio de la rúbrica.
    Esto evita que los valores se reseteen con cada interacción.
    """
    for comp_data in rubric.values():
        for criterion in comp_data["criteria"]:
            score_key = f"{criterion['id']}_score"
            feedback_key = f"{criterion['id']}_feedback"
            
            if score_key not in st.session_state:
                # Iniciar con un puntaje por defecto (ej. 3.0)
                st.session_state[score_key] = 3.0
            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = ""

def reset_rubric_state(rubric):
    """Reinicia los valores de puntuaciones, comentarios y datos del proyecto."""
    for comp_data in rubric.values():
        for criterion in comp_data["criteria"]:
            st.session_state[f"{criterion['id']}_score"] = 3.0
            st.session_state[f"{criterion['id']}_feedback"] = ""

    # Restablecer información del proyecto
    st.session_state["project_name_input"] = ""
    st.session_state["eval_date_input"] = datetime.date.today()
    st.session_state["num_members_input"] = 1
    st.session_state["course_selection"] = "Estadística exploratoría"

    # Limpiar nombres de integrantes que excedan el nuevo tamaño
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

            /* Fondo y encabezados */
            .stApp {{
                background: linear-gradient(180deg, rgba(10,47,107,0.05) 0%, rgba(28,156,156,0.03) 100%);
            }}

            .st-emotion-cache-1vxn2o5, .st-emotion-cache-1avcm0n {{
                color: var(--neutral-dark);
            }}

            h1, h2, h3, h4 {{
                color: var(--primary-color) !important;
            }}

            /* Componentes laterales */
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

            /* Slider y métricas */
            div[data-baseweb="slider"] > div > div {{
                background: var(--secondary-color);
            }}

            div[data-baseweb="slider"] > div > div > div {{
                background: var(--accent-color);
            }}

            .stProgress > div > div > div > div {{
                background-color: var(--accent-color);
            }}

            /* Contenedores */
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

def get_auto_feedback(score, levels):
    """
    Genera retroalimentación automática basada en el puntaje.
    """
    if score <= 2.9:
        return {"level": "Insuficiente", "desc": levels['insuficiente']}
    elif score <= 3.5:
        return {"level": "Básico", "desc": levels['basico']}
    elif score <= 4.2:
        return {"level": "Satisfactorio", "desc": levels['satisfactorio']}
    else:
        return {"level": "Destacado", "desc": levels['destacado']}

def display_project_info_sidebar():
    """
    Muestra los campos de entrada para la información del proyecto en la barra lateral.
    """
    st.sidebar.title("Información del Proyecto")
    if "project_name_input" not in st.session_state:
        st.session_state["project_name_input"] = ""
    project_name = st.sidebar.text_input(
        "Nombre del Proyecto/Artículo",
        key="project_name_input"
    ).strip()

    if "eval_date_input" not in st.session_state:
        st.session_state["eval_date_input"] = datetime.date.today()
    eval_date = st.sidebar.date_input(
        "Fecha de Evaluación",
        key="eval_date_input"
    )

    if "course_selection" not in st.session_state:
        st.session_state["course_selection"] = "Estadística exploratoría"
    course = st.sidebar.selectbox(
        "Asignatura",
        options=[
            "Estadística exploratoría",
            "Estadística no paramétrica",
            "Diseño de experimentos",
            "Teoría del riesgo",
        ],
        key="course_selection"
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

    # Eliminar integrantes que ya no están visibles
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

    # Validación simple
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
        "course": course,
        "validated": validated
    }

def display_component_criteria(component_data):
    """
    Muestra la interfaz de calificación (sliders, expanders) para un componente.
    """
    st.header(f"{component_data['name']} ({component_data['weight']}%)")
    
    for criterion in component_data["criteria"]:
        st.markdown(f"### {criterion['id']}. {criterion['name']} `({criterion['weight']}%)`")
        score_key = f"{criterion['id']}_score"
        feedback_key = f"{criterion['id']}_feedback"
        
        # Layout en columnas para slider y feedback automático
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Slider para la calificación
            st.slider(
                "Puntaje (0.0 - 5.0)",
                min_value=0.0,
                max_value=5.0,
                step=0.1,
                value=float(st.session_state[score_key]),
                key=score_key,
                help="Arrastre para seleccionar el puntaje."
            )
            # Área de texto para retroalimentación manual
            st.text_area(
                "Comentarios Específicos", 
                key=feedback_key,
                height=100
            )

        with col2:
            # Feedback automático basado en el puntaje del slider
            current_score = st.session_state[score_key]
            feedback = get_auto_feedback(current_score, criterion['levels'])
            
            st.info(f"**Nivel: {feedback['level']} ({current_score:.1f})**\n\n{feedback['desc']}")

        # Expander para mostrar los detalles de la rúbrica
        with st.expander("Ver descripción completa de niveles"):
            levels = criterion['levels']
            cols = st.columns(4)
            cols[0].markdown(f"**Insuficiente (0.0-2.9)**\n\n{levels['insuficiente']}")
            cols[1].markdown(f"**Básico (3.0-3.5)**\n\n{levels['basico']}")
            cols[2].markdown(f"**Satisfactorio (3.6-4.2)**\n\n{levels['satisfactorio']}")
            cols[3].markdown(f"**Destacado (4.3-5.0)**\n\n{levels['destacado']}")
        
        st.divider()

def calculate_results(rubric):
    """
    Calcula la calificación final ponderada y prepara los datos para el DF.
    """
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
            
            # Contribución ponderada de este criterio al 100% total
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

    # La calificación final es el total de puntos (sobre 100) re-escalado a 5.0
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

def display_results_sidebar(results, project_info, placeholder, rubric):
    """
    Muestra los resultados (calificación, barra, desglose) en la barra lateral.
    """
    with placeholder.container():
        st.sidebar.divider()
        st.sidebar.header("Resultados de la Evaluación")
        st.sidebar.button(
            "🔄 Reiniciar evaluación",
            type="secondary",
            use_container_width=True,
            on_click=reset_rubric_state,
            args=(rubric,)
        )
        
        final_grade = results["final_grade"]
        
        # Métrica de Calificación Final
        st.sidebar.metric(
            label="Calificación Final (sobre 5.0)", 
            value=f"{final_grade:.2f}"
        )
        
        # Barra de progreso
        progress_value = min(max(final_grade / 5.0, 0.0), 1.0)
        st.sidebar.progress(progress_value)
        
        st.sidebar.subheader("Desglose por Componente")
        
        # Mostrar desglose
        for comp_id, comp_res in results["component_scores"].items():
            name = comp_res["short_name"]
            score = comp_res["score_pct"]
            weight = comp_res["weight"]
            component_grade = comp_res["normalized_score"] * 5
            st.sidebar.write(
                f"{name}: **{score:.2f} / {weight:.0f} pts** · {component_grade:.2f} / 5.0"
            )

        # --- Funcionalidad de Exportación ---
        if project_info["validated"]:
            if EXCEL_WRITER_ENGINE is None:
                st.sidebar.error(
                    "No se encontró un motor para exportar a Excel. Instale 'xlsxwriter' o 'openpyxl'."
                )
                return

            df = results["details_df"]
            component_summary_df = results["component_summary_df"]
            
            # Añadir info del proyecto al DF
            df_header = pd.DataFrame({
                "Project": [project_info["project_name"]],
                "Date": [project_info["eval_date"]],
                "Members": [project_info["members"]],
                "Course": [project_info.get("course", "")],
                "Final_Grade_5.0": [final_grade]
            })
            
            # Usar io.BytesIO para crear el CSV en memoria
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine=EXCEL_WRITER_ENGINE) as writer:
                # Escribir hojas separadas
                df_header.to_excel(writer, sheet_name='Resumen', index=False)
                component_summary_df.to_excel(writer, sheet_name='Componentes', index=False)
                df.to_excel(writer, sheet_name='Detalle_Criterios', index=False)

            output.seek(0)
            processed_data = output.getvalue()

            st.sidebar.download_button(
                label="📥 Exportar Resultados (Excel)",
                data=processed_data,
                file_name=f"Calificacion_{project_info['project_name']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.sidebar.info("Complete la información del proyecto para habilitar la exportación.")

        st.sidebar.caption(
            "Creado con ❤️ por Javier Mauricio Sierra - USTA"
        )


def _format_dataframe_for_html(df: pd.DataFrame, formats: dict) -> str:
    """Devuelve el DataFrame formateado como tabla HTML aplicando formatos por columna."""
    formatted_df = df.copy()
    for column, fmt in formats.items():
        if column in formatted_df.columns:
            formatted_df[column] = formatted_df[column].map(
                lambda value: fmt.format(value) if pd.notnull(value) else ""
            )
    return formatted_df.to_html(index=False, escape=False, justify="left")


def build_html_report(results: dict, project_info: dict) -> bytes:
    """Construye un reporte HTML completo con la información del proyecto y la evaluación."""
    project_name = project_info.get("project_name") or "Proyecto sin nombre"
    eval_date = project_info.get("eval_date")
    if isinstance(eval_date, datetime.date):
        eval_date_str = eval_date.strftime("%Y-%m-%d")
    else:
        eval_date_str = str(eval_date) if eval_date else ""
    members = project_info.get("members") or "No registrado"
    course = project_info.get("course") or "Sin asignatura"

    final_grade = results.get("final_grade", 0)
    total_score_pct = results.get("total_score_pct", 0)
    component_summary_df = results.get("component_summary_df", pd.DataFrame())
    details_df = results.get("details_df", pd.DataFrame())

    component_summary_html = "<p>No hay información disponible.</p>"
    if not component_summary_df.empty:
        component_summary_html = _format_dataframe_for_html(
            component_summary_df,
            {
                "Peso (%)": "{:,.0f}%",
                "Puntaje obtenido (pts)": "{:,.2f}",
                "Avance (%)": "{:,.1f}%",
                "Calificación (0-5)": "{:,.2f}",
            },
        )

    details_html = "<p>No hay información disponible.</p>"
    if not details_df.empty:
        details_html = _format_dataframe_for_html(
            details_df,
            {
                "Puntaje (sobre 5.0)": "{:,.1f}",
                "Peso (%)": "{:,.0f}%",
                "Puntaje_Ponderado (sobre 100)": "{:,.2f}",
            },
        )

    html_content = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
    <meta charset=\"UTF-8\" />
    <title>Reporte de Calificación - {project_name}</title>
    <style>
        :root {{
            --primary: {USTA_PALETTE['primary']};
            --secondary: {USTA_PALETTE['secondary']};
            --accent: {USTA_PALETTE['accent']};
            --teal: {USTA_PALETTE['teal']};
            --neutral-light: {USTA_PALETTE['neutral_light']};
            --neutral-dark: {USTA_PALETTE['neutral_dark']};
        }}

        body {{
            font-family: 'Segoe UI', Arial, Helvetica, sans-serif;
            margin: 2rem;
            color: var(--neutral-dark);
            background: linear-gradient(180deg, rgba(10,47,107,0.05) 0%, rgba(28,156,156,0.02) 100%);
        }}
        h1, h2, h3 {{ color: var(--primary); }}
        .badge {{
            display: inline-block;
            padding: 0.35rem 0.9rem;
            background: linear-gradient(135deg, var(--accent), #ffd166);
            color: var(--neutral-dark);
            border-radius: 999px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
        th, td {{
            border: 1px solid rgba(10,47,107,0.18);
            padding: 0.65rem;
            font-size: 0.95rem;
            vertical-align: top;
        }}
        th {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: #ffffff;
            text-align: left;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}
        tr:nth-child(even) {{ background-color: rgba(10,47,107,0.05); }}
        tr:nth-child(odd) {{ background-color: rgba(255,255,255,0.9); }}
        footer {{ margin-top: 3rem; font-size: 0.85rem; color: rgba(23,33,60,0.7); }}
        .meta {{
            margin-bottom: 1.8rem;
            padding: 1rem 1.2rem;
            background: rgba(255,255,255,0.85);
            border-left: 4px solid var(--teal);
            box-shadow: 0 6px 18px rgba(15,33,58,0.08);
            border-radius: 10px;
        }}
        .meta p {{ margin: 0.35rem 0; }}
        section {{ margin-bottom: 2.2rem; }}
        section h2 {{
            border-bottom: 3px solid var(--accent);
            display: inline-block;
            padding-bottom: 0.25rem;
        }}
    </style>
</head>
<body>
    <h1>Reporte de Calificación</h1>
    <div class=\"meta\">
        <p><strong>Proyecto:</strong> {project_name}</p>
        <p><strong>Fecha de evaluación:</strong> {eval_date_str}</p>
    <p><strong>Integrantes:</strong> {members}</p>
    <p><strong>Asignatura:</strong> {course}</p>
    </div>
    <section>
        <h2>Resultado general</h2>
        <p><span class=\"badge\">Calificación final: {final_grade:.2f} / 5.0</span></p>
        <p>Puntaje ponderado total: {total_score_pct:.2f} / 100</p>
    </section>
    <section>
        <h2>Resumen por componente</h2>
        {component_summary_html}
    </section>
    <section>
        <h2>Detalle por criterio</h2>
        {details_html}
    </section>
    <footer>
        <p>Reporte generado automáticamente por la herramienta de calificación.</p>
    </footer>
</body>
</html>"""

    return html_content.encode("utf-8")


def display_html_report_tab(results: dict, project_info: dict) -> None:
    """Renderiza la pestaña de descarga del reporte HTML."""
    st.subheader("Reporte HTML del proyecto")

    if not project_info.get("validated"):
        st.info("Complete la información del proyecto y asigne calificaciones para habilitar la descarga.")
        return

    html_bytes = build_html_report(results, project_info)
    project_name = project_info.get("project_name") or "proyecto"
    safe_project_name = "_".join(project_name.split()) or "proyecto"

    st.download_button(
        label="📄 Descargar reporte HTML",
        data=html_bytes,
        file_name=f"Reporte_{safe_project_name}.html",
        mime="text/html"
    )
    st.caption("El reporte incluye el resumen por componente y el detalle por criterio con los comentarios registrados.")


# --- APLICACIÓN PRINCIPAL ---

def main():
    """
    Función principal que ejecuta la aplicación Streamlit.
    """
    # Configuración de la página
    st.set_page_config(
        page_title="Herramienta de Calificación",
        page_icon="✅",
        layout="wide"
    )

    inject_brand_theme()

    st.title("✅ Herramienta de Calificación Automatizada")
    st.markdown("Use la barra lateral para ingresar la información del proyecto y las pestañas a continuación para calificar cada componente.")

    # 1. Inicializar el estado de la sesión
    initialize_session_state(RUBRIC_DATA)

    # 2. Mostrar inputs del proyecto en la barra lateral
    project_info = display_project_info_sidebar()

    # 3. Crear un placeholder para los resultados en la barra lateral
    #    Esto permite que los resultados se actualicen en tiempo real
    results_placeholder = st.sidebar.empty()

    # 4. Crear pestañas para la interfaz de calificación
    tab_titles = [data["name"] for data in RUBRIC_DATA.values()] + ["Reporte HTML"]
    tabs = st.tabs(tab_titles)

    component_tabs = tabs[:len(RUBRIC_DATA)]
    report_tab = tabs[-1]

    for (comp_id, comp_data), tab in zip(RUBRIC_DATA.items(), component_tabs):
        with tab:
            display_component_criteria(comp_data)

    # 5. Calcular y mostrar los resultados (se re-calcula en cada interacción)
    #    Esto es el núcleo de la reactividad de Streamlit
    results = calculate_results(RUBRIC_DATA)
    display_results_sidebar(results, project_info, results_placeholder, RUBRIC_DATA)

    with report_tab:
        display_html_report_tab(results, project_info)

    # Mostrar los detalles en el cuerpo principal
    st.divider()
    st.subheader("Resumen por componente")
    component_summary_df = results["component_summary_df"]
    if not component_summary_df.empty:
        st.dataframe(
            component_summary_df.style.format({
                "Peso (%)": "{:.0f}",
                "Puntaje obtenido (pts)": "{:.2f}",
                "Avance (%)": "{:.1f}%",
                "Calificación (0-5)": "{:.2f}"
            }),
            use_container_width=True
        )

    st.subheader("Detalle por criterio")
    details_df = results["details_df"]
    if not details_df.empty:
        st.dataframe(
            details_df.style.format({
                "Puntaje (sobre 5.0)": "{:.1f}",
                "Peso (%)": "{:.0f}",
                "Puntaje_Ponderado (sobre 100)": "{:.2f}"
            }),
            use_container_width=True
        )


if __name__ == "__main__":
    main()