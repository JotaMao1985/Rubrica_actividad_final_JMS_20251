import streamlit as st
import pandas as pd
import datetime
import base64

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Calificador Automático de Rúbrica",
    page_icon="✍️",
    layout="wide"
)

# --- Datos de la Rúbrica ---
# (La estructura de datos de la rúbrica es la misma que la versión anterior, la omito aquí por brevedad)
# ... (Pega aquí la variable 'rubric_data' del código anterior) ...
rubric_data = {
    'Informe': {
        'ponderacion_total': 0.60,
        'criterios': {
            '1.1 Comprensión del Problema': {
                'ponderacion': 0.10,
                'descripciones': {
                    'Insuficiente (0.0 - 1.5)': 'No identifica o describe erróneamente el problema de investigación y su relevancia.',
                    'Básico (1.6 - 2.9)': 'Describe el problema de forma superficial, sin profundizar en su contexto o importancia.',
                    'Satisfactorio (3.0 - 4.4)': 'Describe con claridad y precisión el problema de investigación, su contexto y su justificación.',
                    'Destacado (4.5 - 5.0)': 'Analiza el problema a profundidad, conectándolo con un marco teórico más amplio y destacando sus implicaciones de manera excepcional.'
                }
            },
            '1.2 Métodos y Planteamientos': {
                'ponderacion': 0.05,
                'descripciones': {
                    'Insuficiente (0.0 - 1.5)': 'Omite la mayoría de los métodos o los describe incorrectamente.',
                    'Básico (1.6 - 2.9)': 'Lista algunos métodos, pero sin detalle o con imprecisiones. No diferencia entre planteamientos teóricos y técnicas aplicadas.',
                    'Satisfactorio (3.0 - 4.4)': 'Identifica y describe correctamente los principales métodos y planteamientos estadísticos y/o metodológicos usados en el artículo.',
                    'Destacado (4.5 - 5.0)': 'Identifica todos los métodos, explica su pertinencia para el problema y los categoriza de forma clara (e.g., modelos, pruebas, diseño).'
                }
            },
            '1.3 Comentario Crítico': {
                'ponderacion': 0.15,
                'descripciones': {
                    'Insuficiente (0.0 - 1.5)': 'No ofrece un comentario crítico o este se limita a una opinión subjetiva sin fundamento técnico.',
                    'Básico (1.6 - 2.9)': 'El comentario es vago, repite las conclusiones del autor sin análisis propio o se enfoca en aspectos triviales.',
                    'Satisfactorio (3.0 - 4.4)': 'Evalúa de forma argumentada la pertinencia y las limitaciones de los métodos aplicados, basándose en conceptos teóricos.',
                    'Destacado (4.5 - 5.0)': 'Realiza una crítica profunda y original, proponiendo alternativas metodológicas justificadas o identificando supuestos clave no discutidos por los autores.'
                }
            },
            '1.4 Estado del Arte': {
                'ponderacion': 0.10,
                'descripciones': {
                    'Insuficiente (0.0 - 1.5)': 'No presenta un estado del arte o las fuentes son irrelevantes.',
                    'Básico (1.6 - 2.9)': 'Presenta un listado de trabajos relacionados sin integrarlos en una narrativa coherente. Las fuentes son escasas o de baja calidad.',
                    'Satisfactorio (3.0 - 4.4)': 'Sintetiza un estado del arte relevante, mostrando cómo el artículo se inserta en la conversación académica existente. Usa fuentes apropiadas.',
                    'Destacado (4.5 - 5.0)': 'Construye un estado del arte exhaustivo y bien estructurado que demuestra una comprensión sofisticada del campo. Integra las fuentes de manera fluida y crítica.'
                }
            },
            '1.5 Objetivos Personales': {
                'ponderacion': 0.05,
                'descripciones': {
                    'Insuficiente (0.0 - 1.5)': 'No define objetivos o estos son confusos y no se relacionan con el artículo.',
                    'Básico (1.6 - 2.9)': 'Plantea objetivos muy generales (e.g., "entender el artículo") sin especificar un propósito de aprendizaje o aplicación.',
                    'Satisfactorio (3.0 - 4.4)': 'Define objetivos claros y alcanzables que demuestran una intención de aprendizaje o aplicación concreta a partir del artículo.',
                    'Destacado (4.5 - 5.0)': 'Propone objetivos innovadores y personales que conectan el artículo con sus propios intereses de investigación o profesionales de manera reflexiva.'
                }
            },
            '1.6 Análisis Exploratorio de Datos (AED)': {
                'ponderacion': 0.10,
                'descripciones': {
                    'Insuficiente (0.0 - 1.5)': 'No realiza un AED o los resultados son incorrectos y no se presentan visualizaciones.',
                    'Básico (1.6 - 2.9)': 'Realiza un AED muy simple, con visualizaciones poco informativas o mal elaboradas. El análisis no genera conclusiones relevantes.',
                    'Satisfactorio (3.0 - 4.4)': 'Ejecuta un AED pertinente utilizando los datos (del artículo o propios), con visualizaciones claras y una interpretación correcta de los hallazgos iniciales.',
                    'Destacado (4.5 - 5.0)': 'Diseña y ejecuta un AED completo y perspicaz que revela patrones no evidentes. Las visualizaciones son de alta calidad y la narrativa es convincente.'
                }
            },
            '1.7 Estructura y Formato LaTeX': {
                'ponderacion': 0.05,
                'descripciones': {
                    'Insuficiente (0.0 - 1.5)': 'El documento no compila, tiene errores graves de sintaxis o no sigue la estructura de un artículo académico.',
                    'Básico (1.6 - 2.9)': 'El documento tiene una estructura básica pero desorganizada. El uso de LaTeX es rudimentario (e.g., mal manejo de referencias, figuras o tablas).',
                    'Satisfactorio (3.0 - 4.4)': 'El documento está bien estructurado, compila sin errores y utiliza adecuadamente las funcionalidades de LaTeX (bibliografía, etiquetas, secciones).',
                    'Destacado (4.5 - 5.0)': 'El código LaTeX es limpio y eficiente. El diseño tipográfico es excelente, demostrando un dominio avanzado de la herramienta para la comunicación académica.'
                }
            }
        }
    },
    'Presentacion': {
        'ponderacion_total': 0.20,
        'criterios': {
            '2.1 Estructura y Claridad Visual': {
                'ponderacion': 0.10,
                'descripciones': {
                    'Insuficiente (0.0 - 1.5)': 'Diapositivas desorganizadas, sobrecargadas de texto y visualmente confusas. Difícil de seguir.',
                    'Básico (1.6 - 2.9)': 'La estructura es lógica pero las diapositivas son monótonas o tienen problemas de diseño (e.g., bajo contraste, fuentes pequeñas).',
                    'Satisfactorio (3.0 - 4.4)': 'Diapositivas bien organizadas, con un diseño limpio y profesional. Se hace un buen uso de elementos visuales (gráficos, tablas) para apoyar el contenido.',
                    'Destacado (4.5 - 5.0)': 'El diseño de las diapositivas es excepcional, creativo y altamente efectivo para comunicar las ideas. La jerarquía visual es impecable.'
                }
            },
            '2.2 Síntesis y Relevancia': {
                'ponderacion': 0.10,
                'descripciones': {
                    'Insuficiente (0.0 - 1.5)': 'El contenido es un volcado de texto del informe. No hay esfuerzo de síntesis. Los puntos clave no son evidentes.',
                    'Básico (1.6 - 2.9)': 'Sintetiza la información de manera parcial, omitiendo puntos importantes o incluyendo detalles irrelevantes para una presentación oral.',
                    'Satisfactorio (3.0 - 4.4)': 'Resume eficazmente los puntos más importantes del informe, enfocándose en los hallazgos y el análisis crítico. El contenido es coherente y conciso.',
                    'Destacado (4.5 - 5.0)': 'Realiza una síntesis magistral que no solo resume, sino que crea una narrativa convincente y memorable, guiando a la audiencia a través de los argumentos clave.'
                }
            }
        }
    },
    'Exposicion': {
        'ponderacion_total': 0.20,
        'criterios': {
            '3.1 Dominio y Claridad': {
                'ponderacion': 0.15,
                'descripciones': {
                    'Insuficiente (0.0 - 1.5)': 'Lee directamente de las diapositivas. Muestra inseguridad y no logra explicar los conceptos con sus propias palabras.',
                    'Básico (1.6 - 2.9)': 'Explica los temas con algunas dudas o imprecisiones. La exposición es monótona y poco atractiva. Responde preguntas de forma vacilante.',
                    'Satisfactorio (3.0 - 4.4)': 'Demuestra un buen dominio del tema, explicando los conceptos con claridad y confianza. Mantiene el contacto visual y responde a las preguntas de forma adecuada.',
                    'Destacado (4.5 - 5.0)': 'Expone con total fluidez, pasión y autoridad. Demuestra una comprensión profunda que va más allá del material presentado. Responde a preguntas de forma precisa y reflexiva.'
                }
            },
            '3.2 Gestión del Tiempo y Recursos': {
                'ponderacion': 0.05,
                'descripciones': {
                    'Insuficiente (0.0 - 1.5)': 'Excede significativamente el tiempo límite o termina de forma muy prematura. No utiliza las diapositivas como apoyo.',
                    'Básico (1.6 - 2.9)': 'Se ajusta al tiempo con dificultad, apresurando el final o dejando temas sin cubrir. El uso de las diapositivas es mecánico.',
                    'Satisfactorio (3.0 - 4.4)': 'Gestiona el tiempo de manera efectiva, cubriendo todos los puntos clave dentro de los 10 minutos. Utiliza las diapositivas como un soporte visual bien integrado.',
                    'Destacado (4.5 - 5.0)': 'Realiza una presentación con un ritmo perfecto, utilizando el tiempo para enfatizar los puntos más importantes. Las diapositivas y el discurso están perfectamente sincronizados.'
                }
            }
        }
    }
}
# --- Inicialización del Estado de la Sesión para el Reset ---
if 'form_id' not in st.session_state:
    st.session_state.form_id = 0

# --- Función para generar el reporte HTML (CORREGIDA) ---
def generar_html(project_name, group_members, evaluation_date, subject, desglose_df, summary_df, calificacion_final, observaciones):
    # Formatear la lista de integrantes y observaciones para HTML ANTES del f-string
    integrantes_html = group_members.replace('\n', '<br>')
    observaciones_html = observaciones.replace('\n', '<br>')
    
    # Generar la tabla de desglose en HTML
    desglose_html = desglose_df.to_html(index=False, justify='center', classes='styled-table')
    summary_html = summary_df.to_html(index=False, justify='center', classes='styled-table')
    
    # Definir el color del texto de la calificación final
    if calificacion_final >= 3.0:
        color_nota = "green"
    elif calificacion_final >= 1.6:
        color_nota = "orange"
    else:
        color_nota = "red"

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
            .styled-table thead tr {{ background-color: #009879; color: #ffffff; text-align: left; }}
            .styled-table th, .styled-table td {{ padding: 12px 15px; }}
            .styled-table tbody tr {{ border-bottom: 1px solid #dddddd; }}
            .styled-table tbody tr:nth-of-type(even) {{ background-color: #f3f3f3; }}
            .styled-table tbody tr:last-of-type {{ border-bottom: 2px solid #009879; }}
            .final-score {{ text-align: center; font-size: 1.5em; padding: 20px; border-radius: 8px; margin-top: 20px;}}
            .final-score h2 {{ color: white; background-color: {color_nota}; padding: 10px; border-radius: 5px; }}
            .observaciones {{ background-color: #f9f9f9; border-left: 5px solid #0056b3; padding: 15px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✍️ Reporte de Calificación</h1>
            
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

# --- Inicialización de la App ---
st.title("✍️ Calificador Automático para Análisis de Artículo Científico")
st.markdown("Herramienta para evaluar de forma interactiva y ponderada informes, presentaciones y exposiciones.")
st.markdown("---")

# --- Encabezado con Información del Grupo ---
st.header("1. Información General del Proyecto")
# Se usa una 'key' que depende del form_id para forzar el reinicio
form_key = f"form_{st.session_state.form_id}"

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Nombre del Proyecto (Artículo)", "Ej: Análisis de Modelos de Riesgo Crediticio", key=f"project_{form_key}")
        group_members = st.text_area("Integrantes del Grupo", "Juan Pérez\nMaría Rodríguez", key=f"members_{form_key}")

    with col2:
        evaluation_date = st.date_input("Fecha de Evaluación", datetime.date.today(), key=f"date_{form_key}")
        subject = st.selectbox(
            "Asignatura",
            ("Teoría del riesgo", "Diseño de experimentos", "Estadística no paramétrica"),
            key=f"subject_{form_key}"
        )

st.markdown("---")

# --- Cuerpo del Calificador ---
st.header("2. Calificación por Criterios")

calificaciones = {}
calificaciones_ponderadas = {}

def render_section(section_title, section_data, form_key):
    st.subheader(f"Parte: {section_title} (Ponderación Total: {section_data['ponderacion_total']:.0%})")
    total_ponderado_seccion = 0
    
    with st.container(border=True):
        for criterio, detalles in section_data['criterios'].items():
            st.markdown(f"**Criterio:** {criterio} (Ponderación: {detalles['ponderacion']:.0%})")

            with st.expander("Ver detalles de la rúbrica para este criterio"):
                for nivel, descripcion in detalles['descripciones'].items():
                    st.markdown(f"***{nivel}:*** *{descripcion}*")
            
            calificacion_actual = st.slider(
                f"Calificación para '{criterio}'", 
                min_value=0.0, max_value=5.0, value=3.0, step=0.1, 
                key=f"{criterio}_{form_key}" # Llave única para cada slider
            )
            
            calificaciones[criterio] = calificacion_actual
            calificacion_ponderada = calificacion_actual * detalles['ponderacion']
            calificaciones_ponderadas[criterio] = calificacion_ponderada
            total_ponderado_seccion += calificacion_ponderada
            
            st.info(f"Calificación Ponderada del Criterio: **{calificacion_ponderada:.3f}**")
            st.markdown("---")
            
    return total_ponderado_seccion

total_informe = render_section("Informe Escrito en LaTeX", rubric_data['Informe'], form_key)
total_presentacion = render_section("Presentación en Beamer", rubric_data['Presentacion'], form_key)
total_exposicion = render_section("Exposición Oral", rubric_data['Exposicion'], form_key)

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
        
        if calificacion_final >= 4.5:
            st.success("¡Excelente trabajo! 🚀")
        elif calificacion_final >= 3.0:
            st.success("Trabajo satisfactorio. 👍")
        elif calificacion_final >= 1.6:
            st.warning("Se requieren mejoras. 🤔")
        else:
            st.error("Rendimiento insuficiente. 📉")

    with col2:
        st.markdown("### Desglose de Calificaciones")
        desglose_data = {
            "Criterio": list(calificaciones.keys()),
            "Calificación (0-5)": [f"{v:.1f}" for v in calificaciones.values()],
            "Calificación Ponderada": [f"{v:.3f}" for v in calificaciones_ponderadas.values()]
        }
        desglose_df = pd.DataFrame(desglose_data)
        st.dataframe(desglose_df, hide_index=True, use_container_width=True)

    # --- Sección de Observaciones y Botones ---
    st.markdown("---")
    observaciones = st.text_area("Observaciones Generales", "El grupo demostró un buen dominio del tema, pero se recomienda mejorar el análisis exploratorio de datos...", height=150, key=f"obs_{form_key}")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        # Botón para Reiniciar
        if st.button("🔄 Reiniciar Calificación", use_container_width=True):
            st.session_state.form_id += 1
            st.rerun()

    with btn_col2:
        # Botón para Descargar HTML
        html_report = generar_html(project_name, group_members, evaluation_date, subject, desglose_df, summary_df, calificacion_final, observaciones)
        
        st.download_button(
            label="📄 Descargar Reporte en HTML",
            data=html_report,
            file_name=f"calificacion_{project_name.replace(' ', '_')}.html",
            mime='text/html',
            use_container_width=True
        )