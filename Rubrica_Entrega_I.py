import streamlit as st
import pandas as pd
import datetime

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Calificador Automático de Rúbrica",
    page_icon="📊",
    layout="wide"
)

# --- ESTRUCTURA DE DATOS DE LA RÚBRICA ---
rubric_data = {
    'Informe': {
        'title': 'Informe en R Markdown',
        'ponderacion_total': 0.60,
        'criterios': {
            '1.1 Comprensión de la Base de Datos': {
                'ponderacion': 0.10,
                'descripciones': {
                    'Insuficiente (0.0 - 2.9)': 'No describe o describe incorrectamente la base de datos. Omite variables, estructura o propósito.',
                    'Básico (3.0 - 3.9)': 'Describe la base de datos de forma superficial, mencionando su origen y algunas variables sin profundizar en su estructura o limitaciones.',
                    'Satisfactorio (4.0 - 4.5)': 'Describe con detalle la base de datos, incluyendo su propósito, estructura, tipos de variables y dimensiones. Identifica correctamente las unidades de análisis.',
                    'Destacado (4.6 - 5.0)': 'Realiza una descripción exhaustiva y crítica de la base de datos, discutiendo sus fortalezas, debilidades, posibles sesgos y la pertinencia de las variables para el estudio.'
                }
            },
            '1.2 Métodos y Planteamientos': {
                'ponderacion': 0.10,
                'descripciones': {
                    'Insuficiente (0.0 - 2.9)': 'No identifica o lista incorrectamente los métodos estadísticos del artículo.',
                    'Básico (3.0 - 3.9)': 'Lista algunos métodos utilizados, pero sin describir su función en el estudio.',
                    'Satisfactorio (4.0 - 4.5)': 'Identifica y describe correctamente los principales métodos del artículo, explicando su propósito general en la investigación.',
                    'Destacado (4.6 - 5.0)': 'Identifica y describe con precisión todos los métodos, explicando su fundamentación teórica y su rol específico para responder a las preguntas de investigación.'
                }
            },
            '1.3 Comentario Crítico': {
                'ponderacion': 0.15,
                'descripciones': {
                    'Insuficiente (0.0 - 2.9)': 'El comentario es una opinión superficial, no fundamentada, o simplemente un resumen.',
                    'Básico (3.0 - 3.9)': 'Realiza un comentario general, mencionando fortalezas o debilidades obvias sin una argumentación sólida.',
                    'Satisfactorio (4.0 - 4.5)': 'Ofrece un comentario bien argumentado sobre la aplicación de los métodos, evaluando su pertinencia y señalando limitaciones.',
                    'Destacado (4.6 - 5.0)': 'Desarrolla un análisis crítico profundo, proponiendo alternativas metodológicas justificadas y discutiendo las implicaciones de las decisiones del autor.'
                }
            },
            '1.4 Estado del Arte': {
                'ponderacion': 0.05,
                'descripciones': {
                    'Insuficiente (0.0 - 2.9)': 'No presenta un estado del arte o cita fuentes irrelevantes.',
                    'Básico (3.0 - 3.9)': 'Presenta una lista de trabajos relacionados sin integrarlos en una narrativa coherente.',
                    'Satisfactorio (4.0 - 4.5)': 'Sintetiza literatura relevante que contextualiza el problema y justifica la pertinencia de su propuesta.',
                    'Destacado (4.6 - 5.0)': 'Construye un estado del arte robusto y actualizado que posiciona su propuesta como una contribución clara y necesaria al campo.'
                }
            },
            '1.5 Objetivos Personales/Grupales': {
                'ponderacion': 0.05,
                'descripciones': {
                    'Insuficiente (0.0 - 2.9)': 'No define objetivos o estos son vagos o inalcanzables.',
                    'Básico (3.0 - 3.9)': 'Plantea objetivos generales y poco específicos.',
                    'Satisfactorio (4.0 - 4.5)': 'Define objetivos claros, específicos y alcanzables para el análisis, derivados lógicamente del estudio previo.',
                    'Destacado (4.6 - 5.0)': 'Formula objetivos de investigación (general y específicos) de manera precisa, coherente y metodológicamente abordable.'
                }
            },
            '1.6 Análisis Exploratorio (EDA)': {
                'ponderacion': 0.15,
                'descripciones': {
                    'Insuficiente (0.0 - 2.9)': 'No realiza un EDA o presenta visualizaciones sin interpretación. El código en R Markdown no es reproducible o contiene errores graves.',
                    'Básico (3.0 - 3.9)': 'Realiza un EDA básico con algunas gráficas y estadísticas, pero la interpretación es limitada o desconectada de los objetivos.',
                    'Satisfactorio (4.0 - 4.5)': 'Ejecuta un EDA relevante para los objetivos, utilizando las herramientas adecuadas e interpretando los resultados para generar hipótesis. El código es claro y funcional.',
                    'Destacado (4.6 - 5.0)': 'Conduce un EDA exhaustivo y creativo, descubriendo patrones no evidentes. Las visualizaciones son de alta calidad y la interpretación es profunda. El código es eficiente y está bien documentado.'
                }
            }
        }
    },
    'Presentacion': {
        'title': 'Presentación en Beamer',
        'ponderacion_total': 0.20,
        'criterios': {
            '2.1 Síntesis y Organización': {
                'ponderacion': 0.10,
                'descripciones': {
                    'Insuficiente (0.0 - 2.9)': 'La presentación es una copia del informe, desorganizada y sin estructura lógica.',
                    'Básico (3.0 - 3.9)': 'Resume algunos puntos, pero la estructura es confusa y no fluye lógicamente.',
                    'Satisfactorio (4.0 - 4.5)': 'Sintetiza eficazmente los puntos clave del informe en una estructura lógica y coherente (introducción, métodos, crítica, propuesta).',
                    'Destacado (4.6 - 5.0)': 'La presentación es una narrativa visual convincente que destila la esencia del trabajo, guiando a la audiencia de forma natural y persuasiva.'
                }
            },
            '2.2 Claridad y Diseño Visual': {
                'ponderacion': 0.10,
                'descripciones': {
                    'Insuficiente (0.0 - 2.9)': 'Diapositivas sobrecargadas de texto, con mala calidad de imagen o diseño que dificulta la lectura.',
                    'Básico (3.0 - 3.9)': 'Diseño básico, legible, pero con demasiado texto o visualizaciones de baja calidad.',
                    'Satisfactorio (4.0 - 4.5)': 'Diseño limpio y profesional. Usa elementos visuales de forma efectiva para complementar la exposición, con texto conciso.',
                    'Destacado (4.6 - 5.0)': 'El diseño es excepcional, comunicando ideas complejas de forma simple e intuitiva. Cada elemento en la diapositiva tiene un propósito claro.'
                }
            }
        }
    },
    'Exposicion': {
        'title': 'Exposición Oral',
        'ponderacion_total': 0.20,
        'criterios': {
            '3.1 Dominio y Claridad Conceptual': {
                'ponderacion': 0.10,
                'descripciones': {
                    'Insuficiente (0.0 - 2.9)': 'Lee directamente de las diapositivas. Muestra inseguridad y comete errores conceptuales. No puede responder preguntas.',
                    'Básico (3.0 - 3.9)': 'Explica los conceptos de forma superficial. Duda al explicar partes complejas y responde a preguntas de manera vaga.',
                    'Satisfactorio (4.0 - 4.5)': 'Demuestra buen dominio del tema, explicando con sus propias palabras. Responde a las preguntas de forma correcta y coherente.',
                    'Destacado (4.6 - 5.0)': 'Expone con total fluidez y autoridad, demostrando una comprensión profunda. Responde a las preguntas con solvencia, precisión y capacidad de reflexión.'
                }
            },
            '3.2 Efectividad Comunicativa y Tiempo': {
                'ponderacion': 0.10,
                'descripciones': {
                    'Insuficiente (0.0 - 2.9)': 'Comunicación monótona, poco clara. No logra captar la atención. Excede o le falta mucho tiempo del límite establecido.',
                    'Básico (3.0 - 3.9)': 'Comunicación mayormente clara, pero con ritmo irregular. Se ajusta de manera aproximada al tiempo.',
                    'Satisfactorio (4.0 - 4.5)': 'Se comunica de manera efectiva, manteniendo el interés. Gestiona el tiempo de forma excelente.',
                    'Destacado (4.6 - 5.0)': 'Exposición dinámica, persuasiva y entusiasta. Utiliza el tiempo de forma estratégica para enfatizar los puntos más importantes.'
                }
            }
        }
    }
}

# --- Función para generar el reporte HTML ---
def generar_html(project_name, group_members, evaluation_date, subject, desglose_df, summary_df, calificacion_final, observaciones):
    integrantes_html = group_members.replace('\n', '<br>')
    observaciones_html = observaciones.replace('\n', '<br>')
    desglose_html = desglose_df.to_html(index=False, justify='center', classes='styled-table')
    summary_html = summary_df.to_html(index=False, justify='center', classes='styled-table')
    
    if calificacion_final >= 4.0:
        color_nota = "#009879" # Verde
    elif calificacion_final >= 3.0:
        color_nota = "#f39c12" # Naranja
    else:
        color_nota = "#c0392b" # Rojo

    html_template = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Reporte de Calificación</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            .container {{ max-width: 800px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1, h2 {{ color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 5px;}}
            .info-section p {{ line-height: 1.6; }}
            .styled-table {{ border-collapse: collapse; margin: 25px 0; font-size: 0.9em; min-width: 400px; border-radius: 5px 5px 0 0; overflow: hidden; box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);}}
            .styled-table thead tr {{ background-color: #0056b3; color: #ffffff; text-align: left; }}
            .styled-table th, .styled-table td {{ padding: 12px 15px; }}
            .styled-table tbody tr {{ border-bottom: 1px solid #dddddd; }}
            .styled-table tbody tr:nth-of-type(even) {{ background-color: #f3f3f3; }}
            .styled-table tbody tr:last-of-type {{ border-bottom: 2px solid #0056b3; }}
            .final-score {{ text-align: center; font-size: 1.5em; padding: 20px; border-radius: 8px; margin-top: 20px;}}
            .final-score h2 {{ color: white; background-color: {color_nota}; padding: 10px; border-radius: 5px; }}
            .observaciones {{ background-color: #f9f9f9; border-left: 5px solid #0056b3; padding: 15px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Reporte de Calificación</h1>
            <div class="info-section">
                <h2>Información General</h2>
                <p><strong>Nombre del Proyecto:</strong> {project_name}</p>
                <p><strong>Integrantes:</strong><br>{integrantes_html}</p>
                <p><strong>Fecha de Evaluación:</strong> {evaluation_date}</p>
                <p><strong>Asignatura:</strong> {subject}</p>
            </div>
            <h2>Resumen de Ponderados</h2>
            {summary_html}
            <div class="final-score">
                <h2 style="background-color: {color_nota};">Calificación Final: {calificacion_final:.3f}</h2>
            </div>
            <h2>Desglose de Calificaciones</h2>
            {desglose_html}
            <h2>Observaciones Generales</h2>
            <div class="observaciones">
                <p>{observaciones_html}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

# --- Inicialización del Estado de la Sesión para el Reset ---
if 'form_id' not in st.session_state:
    st.session_state.form_id = 0

# --- INICIO DE LA APLICACIÓN VISUAL ---
st.title("📊 Calificador Automático para Análisis Científico")
st.markdown("Javier Mauricio Sierra.")
st.markdown("---")

# --- Encabezado con Información del Grupo ---
st.header("1. Información General del Proyecto")
form_key = f"form_{st.session_state.form_id}"

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Nombre del Proyecto (Artículo)", "Ej: Propuesta de Análisis sobre...", key=f"project_{form_key}")
        group_members = st.text_area("Integrantes del Grupo", "Nombre Apellido 1\nNombre Apellido 2", key=f"members_{form_key}")
    with col2:
        evaluation_date = st.date_input("Fecha de Evaluación", datetime.date.today(), key=f"date_{form_key}")
        subject = st.selectbox(
            "Asignatura",
            ("Estadística exploratoría","Diseño de experimentos", "Estadística no paramétrica", "Teoría del riesgo"),
            key=f"subject_{form_key}"
        )

st.markdown("---")

# --- Cuerpo del Calificador ---
st.header("2. Calificación por Criterios")
calificaciones = {}
calificaciones_ponderadas = {}

def render_section(section_data, form_key):
    st.subheader(f"Parte: {section_data['title']} (Ponderación Total: {section_data['ponderacion_total']:.0%})")
    total_ponderado_seccion = 0
    
    with st.container(border=True):
        for criterio, detalles in section_data['criterios'].items():
            st.markdown(f"**Criterio:** {criterio} (Ponderación: {detalles['ponderacion']:.0%})")
            with st.expander("Ver detalles de la rúbrica para este criterio"):
                for nivel, descripcion in detalles['descripciones'].items():
                    st.markdown(f"***{nivel}:*** *{descripcion}*")
            
            calificacion_actual = st.slider(
                f"Calificación para '{criterio}'", 
                min_value=0.0, max_value=5.0, value=4.0, step=0.1, 
                key=f"{criterio}_{form_key}"
            )
            
            calificaciones[criterio] = calificacion_actual
            calificacion_ponderada = calificacion_actual * detalles['ponderacion']
            calificaciones_ponderadas[criterio] = calificacion_ponderada
            total_ponderado_seccion += calificacion_ponderada
            
            st.info(f"Calificación Ponderada del Criterio: **{calificacion_ponderada:.3f}**")
            # Evita poner una línea extra al final de la sección
            if criterio != list(section_data['criterios'].keys())[-1]:
                 st.markdown("---")
            
    return total_ponderado_seccion

# --- Renderizar cada sección ---
total_informe = render_section(rubric_data['Informe'], form_key)
total_presentacion = render_section(rubric_data['Presentacion'], form_key)
total_exposicion = render_section(rubric_data['Exposicion'], form_key)

# --- Resumen y Calificación Final ---
st.header("3. Resultados y Acciones")
calificacion_final = total_informe + total_presentacion + total_exposicion

with st.container(border=True):
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### Resumen de Ponderados")
        summary_data = {
            "Componente": ["Total Informe (60%)", "Total Presentación (20%)", "Total Exposición (20%)"],
            "Calificación Ponderada": [f"{total_informe:.3f}", f"{total_presentacion:.3f}", f"{total_exposicion:.3f}"]
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, hide_index=True)
        
        st.markdown("### CALIFICACIÓN FINAL")
        st.metric(label="Nota Definitiva", value=f"{calificacion_final:.3f}")
        
        if calificacion_final >= 4.6:
            st.success("¡Trabajo Destacado! 🚀")
        elif calificacion_final >= 4.0:
            st.success("Trabajo Satisfactorio. 👍")
        elif calificacion_final >= 3.0:
            st.warning("Trabajo Básico. Se requieren mejoras. 🤔")
        else:
            st.error("Rendimiento Insuficiente. 📉")

    with col2:
        st.markdown("### Desglose de Calificaciones")
        desglose_data = {
            "Criterio": list(calificaciones.keys()),
            "Calificación (0-5)": [f"{v:.1f}" for v in calificaciones.values()],
            "Calificación Ponderada": [f"{v:.3f}" for v in calificaciones_ponderadas.values()]
        }
        desglose_df = pd.DataFrame(desglose_data)
        st.dataframe(desglose_df, hide_index=True, use_container_width=True)

    st.markdown("---")
    observaciones = st.text_area("Observaciones Generales", "El análisis crítico de los métodos fue el punto más fuerte. Se sugiere profundizar más en la propuesta de análisis futuro.", height=150, key=f"obs_{form_key}")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🔄 Reiniciar Calificación", use_container_width=True):
            st.session_state.form_id += 1
            st.rerun()
            
    with btn_col2:
        html_report = generar_html(project_name, group_members, evaluation_date, subject, desglose_df, summary_df, calificacion_final, observaciones)
        st.download_button(
            label="📄 Descargar Reporte en HTML",
            data=html_report,
            file_name=f"calificacion_{project_name.replace(' ', '_')}.html",
            mime='text/html',
            use_container_width=True
        )