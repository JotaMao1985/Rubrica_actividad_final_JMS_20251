# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import html # Para escapar HTML en el reporte

# --- Configuración de la Página ---
st.set_page_config(layout="wide", page_title="Rúbrica Visualización Python V7.7")

# --- Definición de la Rúbrica ---
pesos = {
    "Selección de Datos y Narrativa": 0.10,
    "Análisis Exploratorio de Datos (EDA)": 0.15,
    "Limpieza e Imputación de Datos": 0.10,
    "Ingeniería de Características": 0.15,
    "Tablero en Streamlit": 0.20, 
    "Documento PDF (Artículo en LaTeX)": 0.10,
    "Presentación Oral / Demostración": 0.10,
    "Contribución del Equipo": 0.10
}

rubrica_data = {
    "Selección de Datos y Narrativa": {
        "peso": 0.10,
        "criterios": {
            "C1.1: Justificación y Relevancia de Datos DANE, y Narrativa": {
                "descripcion_general": "Justificación de datos DANE y definición de la narrativa del proyecto.",
                "niveles": {
                    4: "Excelente: Base de datos del DANE justificada de manera clara y convincente, demostrando su relevancia para la narrativa. Narrativa original, bien definida y con objetivos claros.",
                    3: "Bueno: Base de datos del DANE justificada adecuadamente. Narrativa definida y con objetivos, aunque podría ser más específica o compelling.",
                    2: "Regular: Base de datos del DANE seleccionada con justificación débil o poco clara. Narrativa vaga, mal definida o con objetivos difusos.",
                    1: "Insuficiente: Base de datos no seleccionada del DANE o sin justificación. Narrativa inexistente o incomprensible.",
                    0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica."
                }
            }
        }
    },
    "Análisis Exploratorio de Datos (EDA)": {
        "peso": 0.15,
        "criterios": {
            "C2.1: Exhaustividad y Calidad del EDA": {
                "descripcion_general": "Identificación de patrones clave, distribuciones, relaciones y anomalías. Uso apropiado y efectivo de visualizaciones y estadísticas descriptivas. Hallazgos integrados con la narrativa.",
                "niveles": {
                    4: "Excelente: EDA exhaustivo que identifica patrones clave, distribuciones, relaciones y anomalías. Uso apropiado y efectivo de visualizaciones y estadísticas descriptivas. Hallazgos integrados con la narrativa.",
                    3: "Bueno: EDA adecuado que explora las principales características de los datos. Uso correcto de visualizaciones y estadísticas básicas. Hallazgos relacionados con la narrativa.",
                    2: "Regular: EDA superficial o incompleto que no identifica patrones importantes. Visualizaciones o estadísticas inapropiadas/limitadas. Hallazgos poco conectados con la narrativa.",
                    1: "Insuficiente: EDA inexistente o incorrecto. No se utilizan visualizaciones ni estadísticas.",
                    0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica."
                }
            }
        }
    },
    "Limpieza e Imputación de Datos": {
        "peso": 0.10,
        "criterios": {
            "C3.1: Manejo Efectivo de Calidad de Datos": {
                "descripcion_general": "Identificación y manejo justificado de datos faltantes, atípicos, inconsistentes; transformaciones lógicas.",
                "niveles": {
                    4: "Excelente: Identificación y manejo (limpieza, imputación) efectivo y justificado de datos faltantes, atípicos o inconsistentes. Transformaciones de datos lógicas y bien aplicadas.",
                    3: "Bueno: Manejo adecuado de los principales problemas de calidad de datos (faltantes, atípicos). Transformaciones de datos correctas en general.",
                    2: "Regular: Manejo incompleto o inapropiado de los problemas de calidad de datos. Transformaciones de datos incorrectas o ausentes.",
                    1: "Insuficiente: No se realizó limpieza ni imputación de datos, o los métodos aplicados son incorrectos.",
                    0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica."
                }
            }
        }
    },
    "Ingeniería de Características": {
        "peso": 0.15,
        "criterios": {
            "C4.1: Creación y Relevancia de Variables Nuevas": {
                "descripcion_general": "Creación de variables nuevas significativas y relevantes alineadas con la narrativa; implementación correcta.",
                "niveles": {
                    4: "Excelente: Creación de variables nuevas significativas y relevantes que enriquecen el análisis y están claramente alineadas con la narrativa. Implementación lógica y correcta.",
                    3: "Bueno: Creación de variables nuevas relevantes en su mayoría, con conexión a la narrativa. Implementación correcta.",
                    2: "Regular: Creación de pocas variables nuevas, irrelevantes o con implementación incorrecta. Conexión débil con la narrativa.",
                    1: "Insuficiente: No se realizó ingeniería de características o las variables creadas no tienen sentido.",
                    0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica."
                }
            }
        }
    },
    "Tablero en Streamlit": { 
        "peso": 0.20,
        "criterios": {
            "C5.0: Evaluación General del Tablero": { "descripcion_general": "Cumplimiento general de los sub-criterios (a-f). Robustez, usabilidad, valor informativo e impacto.", "niveles": { 4: "Excelente: Cumple excelentemente con la mayoría de los sub-criterios (a-f) de esta sección. El tablero es robusto, usable, informativo e impactante.", 3: "Bueno: Cumple bien con la mayoría de los sub-criterios (a-f). El tablero es funcional y presenta la información de forma clara.", 2: "Regular: Cumple parcialmente con los sub-criterios (a-f), presentando deficiencias significativas en varios aspectos. El tablero es funcional pero con limitaciones importantes.", 1: "Insuficiente: No cumple los requisitos mínimos de los sub-criterios (a-f). El tablero no es funcional, está incompleto o es unusable.", 0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica."}},
            "C5.1: Calidad Técnica (Streamlit)": { "descripcion_general": "Organización del código, uso de caching, seguridad, escalabilidad.", "niveles": { 4: "Excelente: Código del tablero organizado, modular y con comentarios claros. Uso efectivo de caching. Consideraciones de seguridad (si aplica) y escalabilidad reflejadas en el diseño.", 3: "Bueno: Código funcional y legible. Uso de caching adecuado en partes clave. Consideraciones básicas de seguridad/escalabilidad.", 2: "Regular: Código desorganizado o difícil de leer. Uso limitado o incorrecto de caching. Falta de atención a seguridad o escalabilidad.", 1: "Insuficiente: Código no funcional, ilegible o ausente. No se usó caching. Problemas graves de seguridad o diseño no escalable.", 0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica." }},
            "C5.2: Experiencia de Usuario (UX) (Streamlit)": { "descripcion_general": "Diseño intuitivo, estética, navegación, responsividad, feedback.", "niveles": { 4: "Excelente: Diseño intuitivo y estéticamente agradable. Navegación clara y lógica. Completamente responsivo en diferentes dispositivos. Feedback amigable (carga, errores, etc.).", 3: "Bueno: Diseño usable y navegación clara. Generalmente responsivo. Feedback básico presente.", 2: "Regular: Diseño confuso o poco atractivo. Navegación poco clara. No responsivo. Falta de feedback al usuario.", 1: "Insuficiente: Diseño unusable, imposible de navegar. No responsivo. Sin feedback.", 0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica." }},
            "C5.3: Funcionalidad (Streamlit)": { "descripcion_general": "Claridad de visualizaciones, interactividad, alineación con objetivos.", "niveles": { 4: "Excelente: Visualizaciones claras, precisas, correctamente etiquetadas y apropiadas para los datos. Interactividad (widgets) fluida y que permite exploración significativa. Alineación completa con los objetivos del proyecto/narrativa.", 3: "Bueno: Visualizaciones claras con etiquetas adecuadas. Widgets funcionales. Alineación general con los objetivos.", 2: "Regular: Visualizaciones confusas, incorrectas o mal etiquetadas. Widgets con errores o poco útiles. Funcionalidad no alinea completamente con los objetivos.", 1: "Insuficiente: Visualizaciones incorrectas o ausentes. Widgets no funcionan o son inútiles. Funcionalidad nula o no relacionada con el proyecto.", 0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica." }},
            "C5.4: Manejo de Datos (en Streamlit)": { "descripcion_general": "Uso de fuentes de datos, preprocesamiento en app, documentación de limitaciones, manejo de errores.", "niveles": { 4: "Excelente: Uso adecuado de las fuentes de datos procesadas. Proceso de preprocesamiento (si ocurre en el app) eficiente. Limitaciones del análisis/datos documentadas (si aplica). Manejo robusto de errores o datos atípicos/faltantes en el app.", 3: "Bueno: Uso correcto de las fuentes de datos. Preprocesamiento manejado. Algún manejo básico de errores.", 2: "Regular: Problemas al cargar/procesar datos en el app. Preprocesamiento inadecuado. Manejo de errores deficiente o ausente.", 1: "Insuficiente: Datos no cargan o procesan correctamente. Errores frecuentes que crashean el app.", 0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica." }},
            "C5.5: Documentación (del Tablero)": { "descripcion_general": "Repositorio, README, licencia, control de versiones.", "niveles": { 4: "Excelente: Repositorio organizado (GitHub/GitLab). README completo con instrucciones claras para despliegue/ejecución. Licencia adecuada incluida. Historial de control de versiones significativo (commits).", 3: "Bueno: Repositorio presente con README básico. Licencia incluida. Uso básico de control de versiones.", 2: "Regular: Repositorio desorganizado o incompleto. README insuficiente o incorrecto. Licencia ausente o inadecuada. Historial de control de versiones pobre o inexistente.", 1: "Insuficiente: No hay repositorio. No hay documentación de despliegue. No hay licencia. No hay control de versiones.", 0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica." }},
            "C5.6: Impacto (del Tablero)": { "descripcion_general": "Valor para usuario final, usabilidad por no expertos, alineación con métricas.", "niveles": { 4: "Excelente: El tablero proporciona un valor claro y tangible para el usuario final (alineado con la narrativa). Potencial de uso por no expertos. Métricas (si aplica) alineadas a objetivos estratégicos.", 3: "Bueno: El tablero proporciona valor, aunque podría ser más claro. Usable por la mayoría de los no expertos.", 2: "Regular: El valor del tablero es poco claro o mínimo. Dificultad de uso para no expertos. Métricas (si aplica) no alineadas.", 1: "Insuficiente: El tablero no proporciona valor alguno. Inusable por el público objetivo.", 0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica." }}
        }
    },
    "Documento PDF (Artículo en LaTeX)": {
        "peso": 0.10,
        "criterios": {
            "C6.1: Calidad y Completitud del Documento LaTeX": { "descripcion_general": "Estructura, claridad, detalle de pasos, figuras/tablas, redacción.", "niveles": { 4: "Excelente: Documento completo y bien estructurado usando LaTeX. Describe detalladamente y con claridad todos los pasos: selección, EDA, limpieza, FE, diseño del tablero, metodologías. Figuras/tablas relevantes incluidas y referenciadas. Redacción profesional y académica.", 3: "Bueno: Documento con la mayoría de las secciones cubiertas. Uso correcto de LaTeX en general. Descripción adecuada de los pasos principales. Figuras/tablas presentes. Redacción clara.", 2: "Regular: Documento incompleto, mal estructurado o con secciones faltantes. Errores significativos en LaTeX. Descripciones vagas o incorrectas de los pasos. Figuras/tablas ausentes o incorrectas.", 1: "Insuficiente: Documento ausente, incompleto o no usa LaTeX. No describe los pasos del proyecto.", 0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica."}}
        }
    },
    "Presentación Oral / Demostración": {
        "peso": 0.10, "opcional": True,
        "criterios": {
            "C7.1: Claridad y Efectividad de la Presentación": { "descripcion_general": "Claridad, concisión, manejo de preguntas.", "niveles": { 4: "Excelente: Presentación clara, concisa y convincente del proyecto, resultados y tablero. Manejo efectivo de preguntas.", 3: "Bueno: Presentación clara de los puntos clave. Manejo adecuado de preguntas.", 2: "Regular: Presentación confusa o incompleta. Dificultad para manejar preguntas.", 1: "Insuficiente: Presentación no realizada o incomprensible. No responde a preguntas.", 0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica."}}
        }
    },
    "Contribución del Equipo": {
        "peso": 0.10, "opcional": True,
        "criterios": {
            "C8.1: Colaboración y Distribución del Trabajo": { "descripcion_general": "Distribución equitativa, colaboración, integración de resultados.", "niveles": { 4: "Excelente: Distribución equitativa del trabajo evidente. Colaboración efectiva y resultados integrados.", 3: "Bueno: Distribución adecuada del trabajo. Buena colaboración.", 2: "Regular: Distribución inequitativa del trabajo o falta de colaboración. Integración de partes difícil.", 1: "Insuficiente: Poca o ninguna evidencia de colaboración. El trabajo no está integrado.", 0: "No Presentado/Irrelevante: El componente no fue presentado o no aplica."}}
        }
    }
}
niveles_desempeno_rubrica = {4: "Excelente", 3: "Bueno", 2: "Regular", 1: "Insuficiente", 0: "No Presentado"}
puntos_posibles_por_criterio = 4

# --- Inicialización del Estado de Sesión ---
def inicializar_estado_nueva_rubrica():
    if 'current_page_nr2' not in st.session_state: st.session_state.current_page_nr2 = "Información General"
    
    # Claves para la información general principal
    app_level_info_keys = {
        "titulo_proyecto_nr2": "", "estudiantes_nr2": "", "evaluador_nr2": "",
        "fecha_evaluacion_nr2": datetime.now().date(),
        "comentarios_adicionales_nr2": ""
    }
    for key, val in app_level_info_keys.items():
        if key not in st.session_state: st.session_state[key] = val

    # Claves para los widgets dentro del formulario de Información General
    form_info_widget_keys = {
        "form_titulo_proyecto_nr2": st.session_state.get("titulo_proyecto_nr2", ""),
        "form_estudiantes_nr2": st.session_state.get("estudiantes_nr2", ""),
        "form_evaluador_nr2": st.session_state.get("evaluador_nr2", ""),
        "form_fecha_evaluacion_nr2": st.session_state.get("fecha_evaluacion_nr2", datetime.now().date())
    }
    for key, val_from_main_state in form_info_widget_keys.items():
        if key not in st.session_state: st.session_state[key] = val_from_main_state
            
    if 'calificaciones_nr2' not in st.session_state: st.session_state.calificaciones_nr2 = {}
    for seccion, detalles_seccion in rubrica_data.items():
        if seccion not in st.session_state.calificaciones_nr2: st.session_state.calificaciones_nr2[seccion] = {}
        for criterio_key in detalles_seccion["criterios"].keys():
            if criterio_key not in st.session_state.calificaciones_nr2[seccion]:
                st.session_state.calificaciones_nr2[seccion][criterio_key] = None
    if 'presentacion_oral_activa_nr2' not in st.session_state: st.session_state.presentacion_oral_activa_nr2 = True
    if 'contribucion_equipo_activa_nr2' not in st.session_state: st.session_state.contribucion_equipo_activa_nr2 = True
inicializar_estado_nueva_rubrica()

# --- Funciones de Lógica y Navegación ---
def set_score_nr2(seccion, criterio, score):
    st.session_state.calificaciones_nr2[seccion][criterio] = score

def render_rubric_table_section(seccion_nombre, detalles_seccion):
    st.header(f"{seccion_nombre} (Peso: {detalles_seccion['peso']*100:.0f}%)")
    mostrar_criterios_para_esta_seccion = True
    if detalles_seccion.get("opcional", False):
        if seccion_nombre == "Presentación Oral / Demostración":
            is_active = st.checkbox("Evaluar esta sección (Presentación Oral)", key="presentacion_oral_activa_nr2", value=st.session_state.get("presentacion_oral_activa_nr2", True)) 
            if not is_active: st.info("Sección opcional no seleccionada para evaluación."); mostrar_criterios_para_esta_seccion = False
        elif seccion_nombre == "Contribución del Equipo":
            is_active = st.checkbox("Evaluar esta sección (Contribución del Equipo)", key="contribucion_equipo_activa_nr2", value=st.session_state.get("contribucion_equipo_activa_nr2", True))
            if not is_active: st.info("Sección opcional no seleccionada para evaluación."); mostrar_criterios_para_esta_seccion = False
    
    if not mostrar_criterios_para_esta_seccion: st.markdown("---"); return
    
    header_cols = st.columns([2.5, 1, 1, 1, 1, 1, 1.5]) 
    header_cols[0].markdown("**Criterio**"); score_idx = 1
    for score_val, score_text in niveles_desempeno_rubrica.items(): header_cols[score_idx].markdown(f"**{score_text} ({score_val})**"); score_idx += 1
    header_cols[score_idx].markdown("**Puntos Obtenidos**"); st.divider()

    for criterio_key, criterio_detalles in detalles_seccion["criterios"].items():
        row_cols = st.columns([2.5, 1, 1, 1, 1, 1, 1.5])
        row_cols[0].markdown(f"**{criterio_key}**<br><small>{criterio_detalles['descripcion_general']}</small>", unsafe_allow_html=True)
        current_score = st.session_state.calificaciones_nr2[seccion_nombre].get(criterio_key)
        score_col_idx = 1
        for score_value, _ in niveles_desempeno_rubrica.items(): 
            btn_text = str(score_value); tooltip_desc = criterio_detalles["niveles"].get(score_value, "")
            button_type = "primary" if current_score == score_value else "secondary"
            if row_cols[score_col_idx].button(btn_text, key=f"btn_{seccion_nombre}_{criterio_key}_{score_value}", type=button_type, help=tooltip_desc, use_container_width=True):
                set_score_nr2(seccion_nombre, criterio_key, score_value); st.rerun()
            score_col_idx +=1
        row_cols[score_col_idx].markdown(f"<div style='text-align:center;font-weight:bold;margin-top:8px;'>{current_score if current_score is not None else '--'}</div>", unsafe_allow_html=True)
        st.divider()

def calcular_resultados_nr2():
    # (Sin cambios funcionales mayores respecto a V7.4, se asume que lee bien de calificaciones_nr2)
    resultados = {"secciones": {}, "total_obtenido": 0, "max_posible_evaluado": 0, "calificacion_final_ponderada": 0}
    peso_total_efectivo = 0
    for seccion, detalles_seccion in rubrica_data.items():
        evaluar_seccion = True
        if detalles_seccion.get("opcional", False):
            if seccion == "Presentación Oral / Demostración" and not st.session_state.get("presentacion_oral_activa_nr2", True): evaluar_seccion = False
            if seccion == "Contribución del Equipo" and not st.session_state.get("contribucion_equipo_activa_nr2", True): evaluar_seccion = False
        if not evaluar_seccion:
            resultados["secciones"][seccion] = {"obtenido": "N/A", "max_posible": "N/A", "rendimiento_0_1": "N/A", "peso_aplicado": 0, "evaluada": False}
            continue
        puntos_obtenidos_seccion = 0; max_puntos_posibles_seccion = 0;
        for criterio_key in detalles_seccion["criterios"].keys():
            score = st.session_state.calificaciones_nr2.get(seccion, {}).get(criterio_key)
            if score is not None:
                puntos_obtenidos_seccion += score; max_puntos_posibles_seccion += puntos_posibles_por_criterio;
        rendimiento_seccion = puntos_obtenidos_seccion / max_puntos_posibles_seccion if max_puntos_posibles_seccion > 0 else 0
        resultados["secciones"][seccion] = {"obtenido": puntos_obtenidos_seccion, "max_posible": max_puntos_posibles_seccion, "rendimiento_0_1": rendimiento_seccion, "peso_aplicado": detalles_seccion["peso"], "evaluada": True}
        if evaluar_seccion: 
            resultados["total_obtenido"] += puntos_obtenidos_seccion
            resultados["max_posible_evaluado"] += max_puntos_posibles_seccion
            resultados["calificacion_final_ponderada"] += rendimiento_seccion * detalles_seccion["peso"]
            peso_total_efectivo += detalles_seccion["peso"]
    if peso_total_efectivo > 0: resultados["calificacion_final_100"] = (resultados["calificacion_final_ponderada"] / peso_total_efectivo) * 100
    else: resultados["calificacion_final_100"] = 0
    if resultados["max_posible_evaluado"] > 0: resultados["puntuacion_total_ratio_100"] = (resultados["total_obtenido"] / resultados["max_posible_evaluado"]) * 100
    else: resultados["puntuacion_total_ratio_100"] = 0
    return resultados

# --- Generador de HTML ---
def generar_html_reporte_nueva_rubrica(resultados_calc):
    # (Adaptado en V7.4 para leer st.session_state.calificaciones_nr2 y la estructura de resultados_calc)
    html_report = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Reporte Evaluación</title>
    <style>body{{font-family:Arial,sans-serif;margin:20px}}h1,h2,h3{{color:#333}}table{{width:100%;border-collapse:collapse;margin-bottom:20px}}th,td{{border:1px solid #ddd;padding:8px;text-align:left}}th{{background-color:#f2f2f2}}.total{{font-weight:bold}}.comentarios-finales{{white-space:pre-wrap;background-color:#f9f9f9;padding:10px;border:1px dashed #ccc}}</style>
    </head><body><h1>Reporte: {html.escape(st.session_state.get('titulo_proyecto_nr2','N/A'))}</h1>
    <p><strong>Estudiante(s):</strong> {html.escape(st.session_state.get('estudiantes_nr2','N/A'))}</p>
    <p><strong>Evaluador:</strong> {html.escape(st.session_state.get('evaluador_nr2','N/A'))}</p>
    <p><strong>Fecha:</strong> {st.session_state.get('fecha_evaluacion_nr2',datetime.now().date()).strftime('%Y-%m-%d')}</p><hr>
    <h2>Resultados</h2><p><strong>Puntos Totales:</strong> {resultados_calc['total_obtenido']}/{resultados_calc['max_posible_evaluado']}</p>
    <p class="total"><strong>Calificación Ponderada: {resultados_calc['calificacion_final_100']:.2f}/100</strong></p><hr>
    <h2>Desglose por Sección y Criterios Evaluados</h2>"""
    for seccion, data in resultados_calc["secciones"].items():
        if not data["evaluada"]: continue
        html_report += f"<h3>{html.escape(seccion)} (Peso:{data['peso_aplicado']*100:.0f}%)</h3><p>Puntaje Sección:{data['obtenido']}/{data['max_posible']} (Rend.:{data['rendimiento_0_1']*100:.1f}%)</p><table><tr><th>Criterio</th><th>Puntaje</th><th>Nivel</th></tr>"
        for crit, _ in rubrica_data[seccion]["criterios"].items(): # Iterar por definición para orden
            score = st.session_state.calificaciones_nr2[seccion].get(crit)
            if score is not None: html_report += f"<tr><td>{html.escape(crit)}</td><td>{score}</td><td>{html.escape(niveles_desempeno_rubrica.get(score,'N/A'))}</td></tr>"
            else: html_report += f"<tr><td>{html.escape(crit)}</td><td>No evaluado</td><td>N/A</td></tr>" # Si no fue evaluado
        html_report += "</table>"
    
    # Sección de Referencia de Criterios (Nueva adición)
    html_report += "<hr><h2>Referencia Completa de Criterios de Evaluación</h2>"
    html_report += "<table border='1' style='border-collapse: collapse; width: 100%;font-size:0.9em;'>"
    html_report += """
    <thead>
        <tr style='background-color: #f2f2f2;'>
            <th style='width:25%;'>Criterio</th>
            <th>4: Excelente</th>
            <th>3: Bueno</th>
            <th>2: Regular</th>
            <th>1: Insuficiente</th>
            <th>0: No Presentado/Irrelevante</th>
        </tr>
    </thead>
    <tbody>
    """
    for section_name_ref, section_details_ref in rubrica_data.items():
        html_report += f"<tr><td colspan='6' style='background-color: #e0e0e0; font-weight:bold;'>{html.escape(section_name_ref)}</td></tr>"
        for criterion_key_ref, criterion_content_ref in section_details_ref["criterios"].items():
            # Usar descripcion_general para la primera columna si es más corta, o el nombre del criterio
            nombre_criterio_display = criterion_key_ref # O criterion_content_ref['descripcion_general']
            html_report += f"<tr><td><strong>{html.escape(nombre_criterio_display)}</strong><br><small>{html.escape(criterion_content_ref['descripcion_general'])}</small></td>"
            html_report += f"<td>{html.escape(criterion_content_ref['niveles'].get(4, ''))}</td>"
            html_report += f"<td>{html.escape(criterion_content_ref['niveles'].get(3, ''))}</td>"
            html_report += f"<td>{html.escape(criterion_content_ref['niveles'].get(2, ''))}</td>"
            html_report += f"<td>{html.escape(criterion_content_ref['niveles'].get(1, ''))}</td>"
            html_report += f"<td>{html.escape(criterion_content_ref['niveles'].get(0, ''))}</td>"
            html_report += "</tr>"
    html_report += "</tbody></table>"

    # Comentarios finales
    com_final = html.escape(st.session_state.get('comentarios_adicionales_nr2','Sin comentarios.'))
    html_report += f"<hr><h2>Comentarios Adicionales</h2><div class='comentarios-finales'>{com_final}</div><hr><p style='font-size:0.8em;text-align:center;'>Generado:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p></body></html>"
    return html_report

def get_html_download_link(html_content, filename="reporte.html"):
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}" style="text-decoration:none;display:inline-block;margin:15px 0;padding:12px 25px;background-color:#28a745;color:white;border-radius:5px;font-weight:bold;text-align:center;">⬇️ Descargar Reporte HTML</a>'

# --- Interfaz de Usuario ---
st.title("Rúbrica de Evaluación: Visualización y Manejo de Datos con Python")

# Sidebar
st.sidebar.title("Navegación Rúbrica")
lista_paginas_display_sidebar = ["Información General"] + list(rubrica_data.keys()) + ["Resultados", "Resumen de Criterios (Rúbrica)"]
for nombre_pagina_sidebar in lista_paginas_display_sidebar:
    sidebar_btn_key = f"sidebar_nav_btn_nr2_{nombre_pagina_sidebar.replace(' ', '_').replace('/', '').replace('(', '').replace(')', '')}"
    is_active = (st.session_state.current_page_nr2 == nombre_pagina_sidebar)
    button_label = f"➡️ {nombre_pagina_sidebar}" if is_active else nombre_pagina_sidebar
    if st.sidebar.button(button_label, key=sidebar_btn_key, use_container_width=True):
        st.session_state.current_page_nr2 = nombre_pagina_sidebar; st.rerun()
st.sidebar.markdown("---"); st.sidebar.info(f"Nueva Rúbrica V2.5 - {datetime.now().strftime('%Y%m%d')}")

# Contenido Principal
current_page_display_nr = st.session_state.current_page_nr2

if current_page_display_nr == "Información General":
    st.header("Información del Proyecto")
    with st.form(key="info_general_form_nr2"): # Envolver en un formulario
        st.text_input("Título del Proyecto:", value=st.session_state.get("form_titulo_proyecto_nr2", st.session_state.get("titulo_proyecto_nr2","")), key="form_titulo_proyecto_nr2")
        st.text_input("Estudiante(s):", value=st.session_state.get("form_estudiantes_nr2", st.session_state.get("estudiantes_nr2","")), key="form_estudiantes_nr2")
        st.text_input("Evaluador:", value=st.session_state.get("form_evaluador_nr2", st.session_state.get("evaluador_nr2","")), key="form_evaluador_nr2")
        st.date_input("Fecha de Evaluación:", value=st.session_state.get("form_fecha_evaluacion_nr2", st.session_state.get("fecha_evaluacion_nr2",datetime.now().date())), key="form_fecha_evaluacion_nr2")
        
        submitted_info = st.form_submit_button("Guardar Información y Continuar a Sección 1 ➡️", type="primary", use_container_width=True)
        if submitted_info:
            # Guardar explícitamente desde las claves del formulario al estado principal de la app
            st.session_state.titulo_proyecto_nr2 = st.session_state.form_titulo_proyecto_nr2
            st.session_state.estudiantes_nr2 = st.session_state.form_estudiantes_nr2
            st.session_state.evaluador_nr2 = st.session_state.form_evaluador_nr2
            st.session_state.fecha_evaluacion_nr2 = st.session_state.form_fecha_evaluacion_nr2
            
            st.session_state.current_page_nr2 = list(rubrica_data.keys())[0]; st.rerun()
    st.markdown("---")

elif current_page_display_nr in rubrica_data:
    render_rubric_table_section(current_page_display_nr, rubrica_data[current_page_display_nr])
    idx_pagina_actual = list(rubrica_data.keys()).index(current_page_display_nr)
    cols_nav_rubric = st.columns(2)
    if idx_pagina_actual > 0:
        if cols_nav_rubric[0].button(f"⬅️ Anterior: {list(rubrica_data.keys())[idx_pagina_actual - 1]}", use_container_width=True, key=f"prev_nr2_{current_page_display_nr}"):
            st.session_state.current_page_nr2 = list(rubrica_data.keys())[idx_pagina_actual - 1]; st.rerun()
    else:
        if cols_nav_rubric[0].button("⬅️ Anterior: Información General", use_container_width=True, key=f"prev_to_info_nr2_{current_page_display_nr}"):
            st.session_state.current_page_nr2 = "Información General"; st.rerun()
    if idx_pagina_actual < len(rubrica_data) - 1:
        if cols_nav_rubric[1].button(f"Siguiente: {list(rubrica_data.keys())[idx_pagina_actual + 1]} ➡️", type="primary", use_container_width=True, key=f"next_nr2_{current_page_display_nr}"):
            st.session_state.current_page_nr2 = list(rubrica_data.keys())[idx_pagina_actual + 1]; st.rerun()
    else:
        if cols_nav_rubric[1].button("Ver Resultados Finales 🏁", type="primary", use_container_width=True, key=f"to_results_nr2_{current_page_display_nr}"):
            st.session_state.current_page_nr2 = "Resultados"; st.rerun()

elif current_page_display_nr == "Resultados":
    st.header("📊 Resultados de la Evaluación"); resultados = calcular_resultados_nr2()
    st.subheader("Resumen General"); col1_res, col2_res, col3_res = st.columns(3)
    col1_res.metric("Puntos Totales", f"{resultados['total_obtenido']}/{resultados['max_posible_evaluado']}", help=f"Sobre secciones evaluadas.")
    col2_res.metric("Rendimiento Bruto", f"{resultados['puntuacion_total_ratio_100']:.1f}%", help="Porcentaje de puntos obtenidos.")
    col3_res.metric("Calificación Ponderada", f"{resultados['calificacion_final_100']:.2f}/100")
    if resultados['max_posible_evaluado'] > 0 : st.progress(min(1.0, resultados['calificacion_final_100'] / 100))
    st.subheader("Desglose por Sección"); seccion_data_list = []
    for seccion, data in resultados["secciones"].items():
        if data["evaluada"]: seccion_data_list.append({ "Sección": seccion, "Puntos": data["obtenido"], "Máx.": data["max_posible"], "Rend. (%)": f"{data['rendimiento_0_1']*100:.1f}%", "Peso (%)": f"{data['peso_aplicado']*100:.0f}%", "Aporte Final": f"{data['rendimiento_0_1']*data['peso_aplicado']*100:.1f}"})
    if seccion_data_list: st.dataframe(pd.DataFrame(seccion_data_list), hide_index=True, use_container_width=True)
    else: st.info("No hay secciones evaluadas.")
    st.subheader("Comentarios Adicionales"); 
    st.text_area("Escribe aquí tus comentarios finales:", value=st.session_state.get("comentarios_adicionales_nr2",""), key="widget_comentarios_adicionales_nr2", height=200)
    if st.button("Guardar Comentarios Finales", key="save_final_comments_nr2"): # Botón para guardar comentarios finales
        st.session_state.comentarios_adicionales_nr2 = st.session_state.widget_comentarios_adicionales_nr2
        st.toast("Comentarios finales guardados.", icon="📝")
        st.rerun()

    if st.button("Generar Reporte HTML 📄", key="btn_generar_reporte_nr2", type="primary", use_container_width=True):
        html_content_nr2 = generar_html_reporte_nueva_rubrica(resultados)
        b64_html_nr2 = base64.b64encode(html_content_nr2.encode()).decode()
        file_name_html_nr2 = f"Reporte_{html.escape(st.session_state.get('titulo_proyecto_nr2', 'Proyecto').replace(' ', '_'))}.html"
        st.markdown(get_html_download_link(html_content_nr2, file_name_html_nr2), unsafe_allow_html=True)
    if resultados['calificacion_final_100'] > 70: st.balloons()
    if st.button("⬅️ Volver a la última sección", use_container_width=True, key="back_to_last_section_nr2"):
        st.session_state.current_page_nr2 = list(rubrica_data.keys())[-1] if rubrica_data else "Información General"; st.rerun()

elif current_page_display_nr == "Resumen de Criterios (Rúbrica)":
    st.header("Resumen de Criterios de Evaluación (Rúbrica Completa)")
    st.markdown("Esta sección muestra la tabla completa de la rúbrica como referencia. La calificación interactiva se realiza en las páginas de cada sección individual.")
    # El Markdown para la tabla de referencia completa
    tabla_markdown_rubrica_completa = """
| Criterio                                                      | Puntos Posibles | 4: Excelente                                                                                                                                                                     | 3: Bueno                                                                                                                                                                       | 2: Regular                                                                                                                                                                     | 1: Insuficiente                                                                                                                                                                  |
| :------------------------------------------------------------ | :-------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Selección de Datos y Narrativa** | [4 por crit.]   | Base de datos del DANE justificada de manera clara y convincente, demostrando su relevancia para la narrativa. Narrativa original, bien definida y con objetivos claros.                 | Base de datos del DANE justificada adecuadamente. Narrativa definida y con objetivos, aunque podría ser más específica o compelling.                                           | Base de datos del DANE seleccionada con justificación débil o poco clara. Narrativa vaga, mal definida o con objetivos difusos.                                                | Base de datos no seleccionada del DANE o sin justificación. Narrativa inexistente o incomprensible.                                                                              |
| **2. Análisis Exploratorio de Datos (EDA)** | [4 por crit.]   | EDA exhaustivo que identifica patrones clave, distribuciones, relaciones y anomalías. Uso apropiado y efectivo de visualizaciones y estadísticas descriptivas. Hallazgos integrados con la narrativa. | EDA adecuado que explora las principales características de los datos. Uso correcto de visualizaciones y estadísticas básicas. Hallazgos relacionados con la narrativa.       | EDA superficial o incompleto que no identifica patrones importantes. Visualizaciones o estadísticas inapropiadas/limitadas. Hallazgos poco conectados con la narrativa.    | EDA inexistente o incorrecto. No se utilizan visualizaciones ni estadísticas.                                                                                                  |
| **3. Limpieza e Imputación de Datos** | [4 por crit.]   | Identificación y manejo (limpieza, imputación) efectivo y justificado de datos faltantes, atípicos o inconsistentes. Transformaciones de datos lógicas y bien aplicadas.              | Manejo adecuado de los principales problemas de calidad de datos (faltantes, atípicos). Transformaciones de datos correctas en general.                                      | Manejo incompleto o inapropiado de los problemas de calidad de datos. Transformaciones de datos incorrectas o ausentes.                                                       | No se realizó limpieza ni imputación de datos, o los métodos aplicados son incorrectos.                                                                                          |
| **4. Ingeniería de Características** | [4 por crit.]   | Creación de variables nuevas significativas y relevantes que enriquecen el análisis y están claramente alineadas con la narrativa. Implementación lógica y correcta.                   | Creación de variables nuevas relevantes en su mayoría, con conexión a la narrativa. Implementación correcta.                                                                 | Creación de pocas variables nuevas, irrelevantes o con implementación incorrecta. Conexión débil con la narrativa.                                                              | No se realizó ingeniería de características o las variables creadas no tienen sentido.                                                                                           |
| **5. Tablero en Streamlit (Evaluación General)** | [4 por crit.]   | Cumple excelentemente con la mayoría de los sub-criterios (a-f) de esta sección. El tablero es robusto, usable, informativo e impactante.                                         | Cumple bien con la mayoría de los sub-criterios (a-f). El tablero es funcional y presenta la información de forma clara.                                                        | Cumple parcialmente con los sub-criterios (a-f), presentando deficiencias significativas en varios aspectos. El tablero es funcional pero con limitaciones importantes.        | No cumple los requisitos mínimos de los sub-criterios (a-f). El tablero no es funcional, está incompleto o es unusable.                                                         |
| **5.a. Calidad Técnica (Streamlit)** | [4 por crit.]   | Código del tablero organizado, modular y con comentarios claros. Uso efectivo de caching. Consideraciones de seguridad (si aplica) y escalabilidad reflejadas en el diseño.         | Código funcional y legible. Uso de caching adecuado en partes clave. Consideraciones básicas de seguridad/escalabilidad.                                                    | Código desorganizado o difícil de leer. Uso limitado o incorrecto de caching. Falta de atención a seguridad o escalabilidad.                                                  | Código no funcional, ilegible o ausente. No se usó caching. Problemas graves de seguridad o diseño no escalable.                                                                 |
| **5.b. Experiencia de Usuario (UX) (Streamlit)** | [4 por crit.]   | Diseño intuitivo y estéticamente agradable. Navegación clara y lógica. Completamente responsivo en diferentes dispositivos. Feedback amigable (carga, errores, etc.).                   | Diseño usable y navegación clara. Generalmente responsivo. Feedback básico presente.                                                                                           | Diseño confuso o poco atractivo. Navegación poco clara. No responsivo. Falta de feedback al usuario.                                                                         | Diseño unusable, imposible de navegar. No responsivo. Sin feedback.                                                                                                             |
| **5.c. Funcionalidad (Streamlit)** | [4 por crit.]   | Visualizaciones claras, precisas, correctamente etiquetadas y apropiadas para los datos. Interactividad (widgets) fluida y que permite exploración significativa. Alineación completa con los objetivos del proyecto/narrativa. | Visualizaciones claras con etiquetas adecuadas. Widgets funcionales. Alineación general con los objetivos.                                                                     | Visualizaciones confusas, incorrectas o mal etiquetadas. Widgets con errores o poco útiles. Funcionalidad no alinea completamente con los objetivos.                            | Visualizaciones incorrectas o ausentes. Widgets no funcionan o son inútiles. Funcionalidad nula o no relacionada con el proyecto.                                                |
| **5.d. Manejo de Datos (en Streamlit)** | [4 por crit.]   | Uso adecuado de las fuentes de datos procesadas. Proceso de preprocesamiento (si ocurre en el app) eficiente. Limitaciones del análisis/datos documentadas (si aplica). Manejo robusto de errores o datos atípicos/faltantes en el app. | Uso correcto de las fuentes de datos. Preprocesamiento manejado. Algún manejo básico de errores.                                                                              | Problemas al cargar/procesar datos en el app. Preprocesamiento inadecuado. Manejo de errores deficiente o ausente.                                                              | Datos no cargan o procesan correctamente. Errores frecuentes que crashean el app.                                                                                                |
| **5.e. Documentación (del Tablero)** | [4 por crit.]   | Repositorio organizado (GitHub/GitLab). README completo con instrucciones claras para despliegue/ejecución. Licencia adecuada incluida. Historial de control de versiones significativo (commits). | Repositorio presente con README básico. Licencia incluida. Uso básico de control de versiones.                                                                              | Repositorio desorganizado o incompleto. README insuficiente o incorrecto. Licencia ausente o inadecuada. Historial de control de versiones pobre o inexistente.                   | No hay repositorio. No hay documentación de despliegue. No hay licencia. No hay control de versiones.                                                                            |
| **5.f. Impacto (del Tablero)** | [4 por crit.]   | El tablero proporciona un valor claro y tangible para el usuario final (alineado con la narrativa). Potencial de uso por no expertos. Métricas (si aplica) alineadas a objetivos estratégicos. | El tablero proporciona valor, aunque podría ser más claro. Usable por la mayoría de los no expertos.                                                                          | El valor del tablero es poco claro o mínimo. Dificultad de uso para no expertos. Métricas (si aplica) no alineadas.                                                               | El tablero no proporciona valor alguno. Inusable por el público objetivo.                                                                                                       |
| **6. Documento PDF (Artículo en LaTeX)** | [4 por crit.]   | Documento completo y bien estructurado usando LaTeX. Describe detalladamente y con claridad todos los pasos: selección, EDA, limpieza, FE, diseño del tablero, metodologías. Figuras/tablas relevantes incluidas y referenciadas. Redacción profesional y académica. | Documento con la mayoría de las secciones cubiertas. Uso correcto de LaTeX en general. Descripción adecuada de los pasos principales. Figuras/tablas presentes. Redacción clara. | Documento incompleto, mal estructurado o con secciones faltantes. Errores significativos en LaTeX. Descripciones vagas o incorrectas de los pasos. Figuras/tablas ausentes o incorrectas. | Documento ausente, incompleto o no usa LaTeX. No describe los pasos del proyecto.                                                                                                 |
| **Presentación Oral / Demostración (Opcional)** | [4 por crit.]   | Presentación clara, concisa y convincente del proyecto, resultados y tablero. Manejo efectivo de preguntas.                                                                   | Presentación clara de los puntos clave. Manejo adecuado de preguntas.                                                                                                          | Presentación confusa o incompleta. Dificultad para manejar preguntas.                                                                                                          | Presentación no realizada o incomprensible. No responde a preguntas.                                                                                                             |
| **Contribución del Equipo (Si es en Grupo)** | [4 por crit.]   | Distribución equitativa del trabajo evidente. Colaboración efectiva y resultados integrados.                                                                                     | Distribución adecuada del trabajo. Buena colaboración.                                                                                                                      | Distribución inequitativa del trabajo o falta de colaboración. Integración de partes difícil.                                                                                    | Poca o ninguna evidencia de colaboración. El trabajo no está integrado.                                                                                                       |
    """
    st.markdown(tabla_markdown_rubrica_completa, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("⬅️ Volver a Resultados", key="back_to_results_from_summary_nr2"):
        st.session_state.current_page_nr2 = "Resultados"; st.rerun()