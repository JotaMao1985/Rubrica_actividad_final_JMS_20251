# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import base64
from datetime import datetime
import html # Para escapar HTML en el reporte

# --- Configuración de la Página ---
st.set_page_config(layout="wide", page_title="Javier Mauririo Sierra")

# --- Definición de la Rúbrica ---
pesos = {
    "1. SELECCIÓN Y JUSTIFICACIÓN DE BASE DE DATOS": 0.20,
    "2. ANÁLISIS EXPLORATORIO DE DATOS - EDA": 0.25,
    "3. TRATAMIENTO DE DATOS FALTANTES": 0.20,
    "4. INGENIERÍA DE CARACTERÍSTICAS": 0.15,
    "5. PROPUESTA METODOLÓGICA": 0.20
}

rubrica_data_r3 = {
    "1. SELECCIÓN Y JUSTIFICACIÓN DE BASE DE DATOS": {
        "puntos_componente": 20, "max_raw_score": 12, "scaling_factor": 20 / 12, 
        "criterios": {
            "C1.1: Justificación Técnica de la Elección": { "descripcion": "Argumentos sobre relevancia, calidad y potencial analítico de la base. Comprensión de características del dataset.", "niveles": { 4: "Excelente: Presenta argumentos sólidos sobre relevancia, calidad y potencial analítico de la base. Demuestra comprensión profunda de las características del dataset.", 3: "Bueno: Justifica adecuadamente la elección con argumentos válidos sobre relevancia y calidad. Muestra buena comprensión del dataset.", 2: "Satisfactorio: Presenta justificación básica pero suficiente. Comprensión limitada de las características técnicas del dataset.", 1: "Insuficiente: Justificación insuficiente o incorrecta. No demuestra comprensión de las características del dataset seleccionado."}},
            "C1.2: Definición de Objetivos": { "descripcion": "Objetivos específicos, medibles, alcanzables y alineados con el dataset. Jerarquía clara.", "niveles": { 4: "Excelente: Objetivos específicos, medibles, alcanzables y claramente alineados con las capacidades del dataset. Presenta jerarquía clara (general y específicos).", 3: "Bueno: Objetivos bien definidos y realistas, con buena alineación al dataset. Presenta estructura adecuada.", 2: "Satisfactorio: Objetivos básicos pero apropiados. Alineación parcial con las capacidades del dataset.", 1: "Insuficiente: Objetivos vagos, irrealistas o desalineados con el dataset. Falta estructura clara."}},
            "C1.3: Preguntas de Investigación": { "descripcion": "Preguntas pertinentes, específicas, factibles, y que demuestran pensamiento analítico.", "niveles": { 4: "Excelente: Preguntas pertinentes, específicas y factibles de responder con el dataset. Demuestran pensamiento analítico avanzado y originalidad.", 3: "Bueno: Preguntas relevantes y bien formuladas, factibles con el dataset disponible. Muestran buen pensamiento analítico.", 2: "Satisfactorio: Preguntas básicas pero apropiadas. Factibilidad parcialmente evaluada.", 1: "Insuficiente: Preguntas vagas, irrelevantes o no factibles con el dataset seleccionado."}}
        }
    },
    "2. ANÁLISIS EXPLORATORIO DE DATOS - EDA": {
        "puntos_componente": 25, "max_raw_score": 16, "scaling_factor": 25 / 16, 
        "criterios": {
            "C2.1: Profundidad y Sistematización":{ "descripcion": "Cobertura de estructura, distribuciones, correlaciones, patrones. Metodología clara.", "niveles": { 4: "Excelente: Análisis exhaustivo y sistemático que cubre estructura, distribuciones, correlaciones y patrones. Metodología clara y reproducible.", 3: "Bueno: Análisis completo que aborda los aspectos principales de manera organizada. Buena metodología.", 2: "Satisfactorio: Análisis básico pero suficiente. Cubre elementos esenciales con metodología simple.", 1: "Insuficiente: Análisis superficial o desorganizado. Metodología confusa o inexistente."}},
            "C2.2: Calidad de Visualizaciones":{ "descripcion": "Profesionalismo, adecuación y efectividad de gráficos. Claridad narrativa visual.", "niveles": { 4: "Excelente: Visualizaciones profesionales, apropiadas y efectivas. Uso correcto de tipos de gráficos, colores y etiquetas. Narrativa visual clara.", 3: "Bueno: Visualizaciones apropiadas y bien ejecutadas. Buen uso de elementos gráficos con narrativa coherente.", 2: "Satisfactorio: Visualizaciones básicas pero funcionales. Uso aceptable de elementos gráficos.", 1: "Insuficiente: Visualizaciones inadecuadas, poco claras o con errores técnicos significativos."}},
            "C2.3: Estadísticas Descriptivas":{ "descripcion": "Estadísticas completas y apropiadas. Interpretación correcta y contextualizada.", "niveles": { 4: "Excelente: Estadísticas completas y apropiadas para cada tipo de variable. Interpretación técnicamente correcta y contextualizada.", 3: "Bueno: Estadísticas adecuadas con interpretación correcta. Buen contexto analítico.", 2: "Satisfactorio: Estadísticas básicas con interpretación simple pero correcta.", 1: "Insuficiente: Estadísticas limitadas o incorrectas. Interpretación deficiente o errónea."}},
            "C2.4: Interpretación de Hallazgos":{ "descripcion": "Interpretaciones profundas, correctas y relevantes. Identificación de patrones e insights.", "niveles": { 4: "Excelente: Interpretaciones profundas, técnicamente correctas y contextualmente relevantes. Identifica patrones complejos e insights valiosos.", 3: "Bueno: Interpretaciones correctas y relevantes. Identifica patrones importantes con buen contexto.", 2: "Satisfactorio: Interpretaciones básicas pero apropiadas. Identifica algunos patrones relevantes.", 1: "Insuficiente: Interpretaciones superficiales, incorrectas o irrelevantes para los objetivos."}}
        }
    },
    "3. TRATAMIENTO DE DATOS FALTANTES": {
        "puntos_componente": 20, "max_raw_score": 16, "scaling_factor": 20 / 16, 
        "criterios": {
            "C3.1: Identificación y Análisis de Patrones":{ "descripcion": "Análisis del patrón de missingness (MCAR, MAR, MNAR). Diagnóstico y visualización.", "niveles": { 4: "Excelente: Análisis exhaustivo del patrón de missingness (MCAR, MAR, MNAR). Uso de técnicas avanzadas de diagnóstico y visualización.", 3: "Bueno: Buen análisis del patrón de datos faltantes con técnicas apropiadas de diagnóstico.", 2: "Satisfactorio: Análisis básico pero suficiente del patrón de missingness. Uso de técnicas simples.", 1: "Insuficiente: Análisis superficial o incorrecto. No identifica patrones o usa técnicas inadecuadas."}},
            "C3.2: Justificación Teórica del Método":{ "descripcion": "Justificación basada en literatura y dataset. Consideración de alternativas.", "niveles": { 4: "Excelente: Justificación sólida basada en literatura especializada y características específicas del dataset. Considera múltiples alternativas.", 3: "Bueno: Buena justificación con base teórica apropiada. Considera algunas alternativas metodológicas.", 2: "Satisfactorio: Justificación básica pero suficiente. Referencia limitada a fundamentos teóricos.", 1: "Insuficiente: Justificación insuficiente o incorrecta. No considera fundamentos teóricos apropiados."}},
            "C3.3: Implementación Técnica":{ "descripcion": "Implementación correcta, eficiente, documentada y reproducible. Validación.", "niveles": { 4: "Excelente: Implementación técnicamente correcta y eficiente. Código limpio, documentado y reproducible. Validación de resultados.", 3: "Bueno: Implementación correcta con buen código. Documentación adecuada y resultados validados.", 2: "Satisfactorio: Implementación básica pero funcional. Código simple con documentación mínima.", 1: "Insuficiente: Implementación incorrecta o ineficiente. Código confuso o no reproducible."}},
            "C3.4: Evaluación del Impacto":{ "descripcion": "Evaluación del impacto con métricas, análisis de sensibilidad y comparación.", "niveles": { 4: "Excelente: Evaluación rigurosa del impacto usando métricas apropiadas. Análisis de sensibilidad y comparación de métodos.", 3: "Bueno: Buena evaluación del impacto con métricas relevantes. Alguna comparación metodológica.", 2: "Satisfactorio: Evaluación básica del impacto. Uso de métricas simples pero apropiadas.", 1: "Insuficiente: Evaluación insuficiente o incorrecta. No considera el impacto en análisis posteriores."}}
        }
    },
    "4. INGENIERÍA DE CARACTERÍSTICAS": {
        "puntos_componente": 15, "max_raw_score": 12, "scaling_factor": 15 / 12, 
        "criterios": {
            "C4.1: Evaluación de Viabilidad":{ "descripcion": "Evaluación de viabilidad técnica y conceptual. Consideración de limitaciones y recursos.", "niveles": { 4: "Excelente: Evaluación exhaustiva de viabilidad técnica y conceptual. Considera limitaciones y recursos necesarios de manera realista.", 3: "Bueno: Buena evaluación de viabilidad con consideraciones técnicas apropiadas.", 2: "Satisfactorio: Evaluación básica de viabilidad. Considera aspectos principales de manera simple.", 1: "Insuficiente: Evaluación insuficiente o incorrecta de viabilidad. No considera limitaciones importantes."}},
            "C4.2: Creatividad y Relevancia":{ "descripcion": "Propuestas innovadoras y relevantes. Pensamiento analítico avanzado.", "niveles": { 4: "Excelente: Propuestas innovadoras y altamente relevantes para los objetivos. Demuestra pensamiento analítico avanzado y originalidad.", 3: "Bueno: Propuestas creativas y relevantes. Buen pensamiento analítico con algunas ideas originales.", 2: "Satisfactorio: Propuestas básicas pero apropiadas. Relevancia clara aunque limitada creatividad.", 1: "Insuficiente: Propuestas poco creativas o irrelevantes. No demuestra pensamiento analítico apropiado."}},
            "C4.3: Documentación Técnica":{ "descripcion": "Documentación completa, clara y profesional. Justificaciones y metodología.", "niveles": { 4: "Excelente: Documentación completa, clara y profesional. Incluye justificaciones, metodología y ejemplos detallados.", 3: "Bueno: Buena documentación con justificaciones claras y metodología bien explicada.", 2: "Satisfactorio: Documentación básica pero suficiente. Explica aspectos principales de manera simple.", 1: "Insuficiente: Documentación insuficiente, confusa o incompleta. Falta claridad metodológica."}}
        }
    },
    "5. PROPUESTA METODOLÓGICA": {
        "puntos_componente": 20, "max_raw_score": 16, "scaling_factor": 20 / 16, 
        "criterios": {
            "C5.1: Coherencia Objetivos-Metodología":{ "descripcion": "Alineación objetivos y metodología. Comprensión teoría-práctica.", "niveles": { 4: "Excelente: Perfecta alineación entre objetivos planteados y metodología propuesta. Demuestra comprensión profunda de la relación teoría-práctica.", 3: "Bueno: Buena coherencia entre objetivos y metodología. Muestra comprensión sólida de principios analíticos.", 2: "Satisfactorio: Coherencia básica pero suficiente. Comprensión limitada de la relación objetivos-métodos.", 1: "Insuficiente: Falta coherencia o alineación incorrecta. No demuestra comprensión de principios básicos."}},
            "C5.2: Justificación Teórica de Técnicas":{ "descripcion": "Justificación rigurosa basada en literatura. Consideración de supuestos y limitaciones.", "niveles": { 4: "Excelente: Justificación rigurosa basada en literatura especializada. Considera supuestos, limitaciones y alternativas metodológicas.", 3: "Bueno: Buena justificación con base teórica sólida. Considera aspectos técnicos importantes.", 2: "Satisfactorio: Justificación básica pero apropiada. Referencias limitadas a fundamentos teóricos.", 1: "Insuficiente: Justificación insuficiente o incorrecta. No considera fundamentos teóricos apropiados."}},
            "C5.3: Viabilidad de Implementación":{ "descripcion": "Evaluación realista de recursos, tiempo, complejidad. Plan detallado y factible.", "niveles": { 4: "Excelente: Evaluación realista de recursos, tiempo y complejidad. Plan detallado y factible con consideración de riesgos.", 3: "Bueno: Buena evaluación de viabilidad con plan apropiado. Considera aspectos prácticos importantes.", 2: "Satisfactorio: Evaluación básica de viabilidad. Plan simple pero factible.", 1: "Insuficiente: Evaluación poco realista o plan no factible. No considera limitaciones prácticas."}},
            "C5.4: Metodología de Evaluación":{ "descripcion": "Propuesta de métricas y métodos de evaluación rigurosos. Validación y robustez.", "niveles": { 4: "Excelente: Propone métricas y métodos de evaluación rigurosos y apropiados. Considera validación cruzada y análisis de robustez.", 3: "Bueno: Buena propuesta de evaluación con métricas apropiadas. Incluye elementos de validación.", 2: "Satisfactorio: Propuesta básica de evaluación. Métricas simples pero relevantes.", 1: "Insuficiente: Propuesta insuficiente o incorrecta de evaluación. Métricas inapropiadas o ausentes."}}
        }
    }
}
niveles_desempeno_r3 = {4: "Excelente", 3: "Bueno", 2: "Satisfactorio", 1: "Insuficiente", 0: "No Calificado"}
puntos_posibles_por_criterio_r3 = 4
fortalezas_lista_r3 = [ "Selección apropiada del dataset y objetivos claros", "Análisis exploratorio sistemático y visualizaciones efectivas", "Tratamiento técnicamente correcto de datos faltantes", "Propuestas creativas en ingeniería de características", "Metodología bien fundamentada y coherente", "Documentación clara y profesional", "Código limpio y reproducible" ]
areas_mejora_lista_r3 = [ "Profundizar en la justificación teórica de decisiones metodológicas", "Mejorar la calidad y narrativa de visualizaciones", "Fortalecer el análisis de patrones de datos faltantes", "Desarrollar mayor creatividad en ingeniería de características", "Mejorar la coherencia entre objetivos y metodología propuesta", "Ampliar la evaluación de viabilidad e implementación", "Mejorar la documentación técnica y reproducibilidad" ]

# --- Inicialización del Estado de Sesión ---
def inicializar_estado_r3():
    if 'current_page_r3' not in st.session_state: st.session_state.current_page_r3 = "Descripción de la Actividad" 
    
    # Estado principal de la aplicación para información general
    app_level_info_keys = { "titulo_proyecto_r3": "", "estudiantes_r3": "", "evaluador_r3": "", "fecha_evaluacion_r3": datetime.now().date() }
    for key, val in app_level_info_keys.items():
        if key not in st.session_state: st.session_state[key] = val
    
    # Claves para los widgets *dentro* del formulario de Información General (para su estado temporal)
    form_widget_info_keys = {
        "form_titulo_proyecto_r3": st.session_state.get("titulo_proyecto_r3", ""), # Inicializa con el valor del estado principal
        "form_estudiantes_r3": st.session_state.get("estudiantes_r3", ""),
        "form_evaluador_r3": st.session_state.get("evaluador_r3", ""),
        "form_fecha_evaluacion_r3": st.session_state.get("fecha_evaluacion_r3", datetime.now().date())
    }
    for key, val_from_main in form_widget_info_keys.items():
        if key not in st.session_state: st.session_state[key] = val_from_main

    if 'calificaciones_r3' not in st.session_state: st.session_state.calificaciones_r3 = {}
    for seccion, detalles_seccion in rubrica_data_r3.items():
        if seccion not in st.session_state.calificaciones_r3: st.session_state.calificaciones_r3[seccion] = {}
        for criterio_key in detalles_seccion["criterios"].keys():
            if criterio_key not in st.session_state.calificaciones_r3[seccion]:
                st.session_state.calificaciones_r3[seccion][criterio_key] = None 
    
    if 'retro_fortalezas_r3' not in st.session_state: st.session_state.retro_fortalezas_r3 = {f: False for f in fortalezas_lista_r3}
    if 'retro_areas_mejora_r3' not in st.session_state: st.session_state.retro_areas_mejora_r3 = {a: False for a in areas_mejora_lista_r3}
    if 'recomendaciones_especificas_r3' not in st.session_state: st.session_state.recomendaciones_especificas_r3 = ""
    if 'observaciones_adicionales_r3' not in st.session_state: st.session_state.observaciones_adicionales_r3 = ""
inicializar_estado_r3()

# --- Funciones de Lógica y Navegación ---
def set_score_r3(seccion, criterio, score):
    if st.session_state.calificaciones_r3[seccion].get(criterio) == score: st.session_state.calificaciones_r3[seccion][criterio] = None
    else: st.session_state.calificaciones_r3[seccion][criterio] = score

def render_rubric_section_r3(seccion_nombre, detalles_seccion):
    st.header(f"{seccion_nombre} (Total: {detalles_seccion['puntos_componente']} puntos)")
    header_cols = st.columns([2.5, 0.8, 0.8, 0.8, 0.8, 0.8, 1.5]) 
    header_cols[0].markdown("**Criterio**"); col_idx = 1
    for score_val in sorted(niveles_desempeno_r3.keys(), reverse=True): header_cols[col_idx].markdown(f"<div style='text-align:center'><strong>{niveles_desempeno_r3[score_val]}<br>({score_val})</strong></div>", unsafe_allow_html=True); col_idx += 1
    header_cols[col_idx].markdown("<div style='text-align:center'><strong>Puntos</strong></div>", unsafe_allow_html=True); st.divider()

    for criterio_key, criterio_detalles in detalles_seccion["criterios"].items():
        row_cols = st.columns([2.5, 0.8, 0.8, 0.8, 0.8, 0.8, 1.5])
        row_cols[0].markdown(f"**{criterio_key}**<br><small>{criterio_detalles['descripcion']}</small>", unsafe_allow_html=True)
        current_score = st.session_state.calificaciones_r3[seccion_nombre].get(criterio_key)
        col_idx = 1
        for score_value in sorted(niveles_desempeno_r3.keys(), reverse=True): 
            btn_text = str(score_value); tooltip_desc = criterio_detalles["niveles"].get(score_value, "")
            button_type = "primary" if current_score == score_value else "secondary"
            if row_cols[col_idx].button(btn_text, key=f"btn_{seccion_nombre}_{criterio_key}_{score_value}_r3", type=button_type, help=tooltip_desc, use_container_width=True, on_click=set_score_r3, args=(seccion_nombre, criterio_key, score_value)): pass
            col_idx +=1
        display_score = current_score if current_score is not None else "--"
        row_cols[col_idx].markdown(f"<div style='text-align:center;font-weight:bold;margin-top:8px;'>{display_score}</div>", unsafe_allow_html=True)
        st.divider()

def calcular_resultados_r3():
    resultados = {"secciones": {}, "total_puntos_obtenidos_final": 0 }
    for seccion, detalles_seccion in rubrica_data_r3.items():
        puntos_raw_seccion = 0;
        for criterio_key in detalles_seccion["criterios"].keys():
            score = st.session_state.calificaciones_r3.get(seccion, {}).get(criterio_key)
            if score is not None: puntos_raw_seccion += score
        max_raw_seccion = detalles_seccion["max_raw_score"]
        puntos_escalados_seccion = (puntos_raw_seccion / max_raw_seccion) * detalles_seccion["puntos_componente"] if max_raw_seccion > 0 else 0
        resultados["secciones"][seccion] = { "obtenido_raw": puntos_raw_seccion, "max_raw": max_raw_seccion, "obtenido_escalado": puntos_escalados_seccion, "max_escalado": detalles_seccion["puntos_componente"], "evaluada": True } # 'evaluada' es True porque todas las secciones de rubrica_data_r3 se procesan
        resultados["total_puntos_obtenidos_final"] += puntos_escalados_seccion
    return resultados

def get_qualitative_grade_r3(score_100):
    if score_100 >= 90: return "Excelente"
    if score_100 >= 80: return "Bueno"
    if score_100 >= 70: return "Satisfactorio"
    return "Insuficiente"

def generar_html_reporte_r3(resultados_calc):
    info_gen = { "titulo": html.escape(st.session_state.get('titulo_proyecto_r3', 'N/A')), "estudiantes": html.escape(st.session_state.get('estudiantes_r3', 'N/A')), "evaluador": html.escape(st.session_state.get('evaluador_r3', 'N/A')), "fecha": st.session_state.get('fecha_evaluacion_r3', datetime.now().date()).strftime('%Y-%m-%d')}
    html_report = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Reporte Rúbrica DANE</title><style>body{{font-family:Arial,sans-serif;margin:20px;line-height:1.4;font-size:10pt}}h1,h2,h3{{color:#004080;border-bottom:1px solid #ccc;padding-bottom:5px}}table{{width:100%;border-collapse:collapse;margin:15px 0}}th,td{{border:1px solid #ddd;padding:6px;text-align:left;vertical-align:top}}th{{background-color:#e9f2f9}}tr:nth-child(even){{background-color:#f8f8f8}}.total-final{{font-size:1.2em;font-weight:bold;color:#004080;margin-top:20px;padding:10px;background-color:#e9f2f9;border:1px solid #ccc;text-align:center}}.retro-section{{margin-top:20px;padding:10px;border:1px solid #eee;border-radius:5px}}ul{{padding-left:20px}}</style></head><body><h1>Reporte de Evaluación: {info_gen['titulo']}</h1><p><strong>Estudiante(s):</strong> {info_gen['estudiantes']}</p><p><strong>Evaluador:</strong> {info_gen['evaluador']}</p><p><strong>Fecha de Evaluación:</strong> {info_gen['fecha']}</p><hr>"""
    html_report += "<h2>Resumen de Puntuación por Componente</h2><table><thead><tr><th>Componente</th><th>Puntuación Obtenida (Escalada)</th><th>Puntos Máximos del Componente</th></tr></thead><tbody>"
    for seccion, data in resultados_calc["secciones"].items(): html_report += f"<tr><td>{html.escape(seccion)}</td><td>{data['obtenido_escalado']:.2f}</td><td>{data['max_escalado']}</td></tr>"
    html_report += f"<tr style='font-weight:bold;background-color:#e9f2f9;'><td>PUNTUACIÓN FINAL</td><td>{resultados_calc['total_puntos_obtenidos_final']:.2f}</td><td>100</td></tr></tbody></table>"
    qual_grade = get_qualitative_grade_r3(resultados_calc['total_puntos_obtenidos_final'])
    html_report += f"<div class='total-final'>PUNTUACIÓN FINAL: {resultados_calc['total_puntos_obtenidos_final']:.2f} / 100 ({html.escape(qual_grade)})</div><hr>"
    html_report += "<h2>Detalle de Calificaciones por Criterio</h2>"
    for seccion, detalles_seccion in rubrica_data_r3.items():
        html_report += f"<h3>{html.escape(seccion)}</h3><table><thead><tr><th style='width:40%;'>Criterio</th><th>Puntaje (0-4)</th><th>Nivel Alcanzado</th><th>Descripción del Nivel Logrado</th></tr></thead><tbody>"
        for criterio_key, criterio_vals in detalles_seccion["criterios"].items():
            score = st.session_state.calificaciones_r3.get(seccion, {}).get(criterio_key)
            nivel_desc_logrado = "No calificado"; score_display = "N/A"; nivel_display = "N/A"
            if score is not None: nivel_desc_logrado = criterio_vals["niveles"].get(score, "Desc. no disponible"); score_display = str(score); nivel_display = niveles_desempeno_r3.get(score, "N/A")
            html_report += f"<tr><td><strong>{html.escape(criterio_key)}</strong><br><small>{html.escape(criterio_vals['descripcion'])}</small></td><td>{score_display}</td><td>{html.escape(nivel_display)}</td><td>{html.escape(nivel_desc_logrado)}</td></tr>"
        html_report += "</tbody></table>"
    html_report += "<hr><h2>Retroalimentación Constructiva</h2><div class='retro-section'><h3>Fortalezas Identificadas:</h3><ul>"
    for f, checked in st.session_state.retro_fortalezas_r3.items():
        if checked: html_report += f"<li>{html.escape(f)}</li>"
    if not any(st.session_state.retro_fortalezas_r3.values()): html_report += "<li>No se marcaron fortalezas específicas.</li>"
    html_report += "</ul></div><div class='retro-section'><h3>Áreas de Mejora:</h3><ul>"
    for a, checked in st.session_state.retro_areas_mejora_r3.items():
        if checked: html_report += f"<li>{html.escape(a)}</li>"
    if not any(st.session_state.retro_areas_mejora_r3.values()): html_report += "<li>No se marcaron áreas de mejora específicas.</li>"
    html_report += "</ul></div>"
    html_report += f"<div class='retro-section'><h3>Recomendaciones Específicas para el equipo:</h3><p>{html.escape(st.session_state.get('recomendaciones_especificas_r3', 'N/A'))}</p></div>"
    html_report += f"<div class='retro-section'><h3>Observaciones Adicionales del Evaluador:</h3><p>{html.escape(st.session_state.get('observaciones_adicionales_r3', 'N/A'))}</p></div>"
    
    # Incluir la tabla de referencia completa de criterios de evaluación
    html_report += "<hr><h2>Criterios de Evaluación Completos (Referencia)</h2>"
    html_report += "<table border='1' style='border-collapse: collapse; width: 100%;font-size:0.8em;'>"
    html_report += """<thead><tr style='background-color: #f0f2f0;'><th style='width:30%;'>Criterio</th><th>4: Excelente</th><th>3: Bueno</th><th>2: Satisfactorio</th><th>1: Insuficiente</th></tr></thead><tbody>"""
    secciones_a_incluir_en_referencia_html = ["1. SELECCIÓN Y JUSTIFICACIÓN DE BASE DE DATOS", "2. ANÁLISIS EXPLORATORIO DE DATOS - EDA", "3. TRATAMIENTO DE DATOS FALTANTES", "4. INGENIERÍA DE CARACTERÍSTICAS", "5. PROPUESTA METODOLÓGICA"]
    for section_name_ref in secciones_a_incluir_en_referencia_html:
        if section_name_ref in rubrica_data_r3:
            section_details_ref = rubrica_data_r3[section_name_ref]
            html_report += f"<tr><td colspan='5' style='background-color:#e0e0e0;font-weight:bold;'>{html.escape(section_name_ref)} (Componente de {section_details_ref['puntos_componente']} pts)</td></tr>"
            for criterion_key_ref, criterion_content_ref in section_details_ref["criterios"].items():
                html_report += f"<tr><td><strong>{html.escape(criterion_key_ref)}</strong><br><small>{html.escape(criterion_content_ref['descripcion'])}</small></td>"
                html_report += f"<td>{html.escape(criterion_content_ref['niveles'].get(4, ''))}</td>"
                html_report += f"<td>{html.escape(criterion_content_ref['niveles'].get(3, ''))}</td>"
                html_report += f"<td>{html.escape(criterion_content_ref['niveles'].get(2, ''))}</td>"
                html_report += f"<td>{html.escape(criterion_content_ref['niveles'].get(1, ''))}</td></tr>"
    html_report += "</tbody></table>"
    html_report += f"<hr><p style='font-size:0.8em;text-align:center;'>Generado:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p></body></html>"
    return html_report

def get_html_download_link(html_content, filename="reporte.html"):
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}" style="text-decoration:none;display:inline-block;margin:15px 0;padding:12px 25px;background-color:#004080;color:white;border-radius:5px;font-weight:bold;text-align:center;">⬇️ Descargar Reporte HTML</a>'

# --- Interfaz de Usuario ---
st.title("Rúbrica: Proyecto Ciencia de Datos, Visualización de datos masivos")

# Sidebar
st.sidebar.title("Navegación")
lista_paginas_display_sidebar_r3 = ["Descripción de la Actividad", "Información General"] + list(rubrica_data_r3.keys()) + ["Resultados y Retroalimentación", "Criterios de Evaluación (Referencia)"]
for nombre_pagina_sidebar in lista_paginas_display_sidebar_r3:
    sidebar_btn_key = f"sidebar_nav_btn_r3_{nombre_pagina_sidebar.replace(' ', '_').replace('/', '').replace('(', '').replace(')', '')}"
    is_active = (st.session_state.current_page_r3 == nombre_pagina_sidebar)
    button_label = f"➡️ {nombre_pagina_sidebar}" if is_active else nombre_pagina_sidebar
    if st.sidebar.button(button_label, key=sidebar_btn_key, use_container_width=True):
        st.session_state.current_page_r3 = nombre_pagina_sidebar; st.rerun()
st.sidebar.markdown("---"); st.sidebar.info(f"AEIDM: Javier Mauricio Sierra")

# Contenido Principal
current_page_display_r3 = st.session_state.current_page_r3

if current_page_display_r3 == "Descripción de la Actividad":
    st.header("DESCRIPCIÓN Y JUSTIFICACIÓN DE LA ACTIVIDAD")
    st.subheader("Descripción del Proyecto")
    st.markdown("""El proyecto consiste en que equipos de máximo 4 estudiantes desarrollen un análisis integral de ciencia de datos utilizando bases de datos reales del DANE (https://microdatos.dane.gov.co/index.php/catalog/central/about). Los estudiantes deben completar un ciclo completo de análisis que incluye: selección y justificación del dataset, análisis exploratorio profundo, tratamiento sistemático de datos faltantes, ingeniería de características innovadora, y propuesta metodológica fundamentada para análisis posteriores.""")
    st.subheader("Justificación Pedagógica")
    st.markdown("""1.  **Aprendizaje Basado en Proyectos Reales**\n    * Utiliza datos gubernamentales oficiales, exponiendo a los estudiantes a la complejidad y riquezas de datasets del mundo real.\n    * Desarrolla competencias para trabajar con información de calidad variable, típica en contextos profesionales.\n2.  **Integración de Competencias Técnicas**\n    * Pensamiento analítico: Selección crítica de datos y formulación de preguntas de investigación.\n    * Competencias estadísticas: EDA sistemático y tratamiento riguroso de missingness.\n    * Habilidades de programación: Implementación técnica y documentación reproducible.\n    * Creatividad aplicada: Ingeniería de características y propuestas metodológicas innovadoras.\n3.  **Desarrollo de Habilidades Profesionales**\n    * Trabajo colaborativo: Equipos multidisciplinarios que reflejan la práctica profesional.\n    * Comunicación técnica: Documentación clara y justificación de decisiones metodológicas.\n    * Pensamiento crítico: Evaluación de viabilidad y consideración de limitaciones.\n4.  **Relevancia Contextual**\n    * Conecta el aprendizaje académico con problemáticas socioeconómicas colombianas.\n    * Fomenta el uso responsable de datos públicos para generar conocimiento social.\n    * Desarrolla consciencia sobre la calidad y limitaciones de datos gubernamentales.\n5.  **Evaluación Auténtica**\n    * La rúbrica refleja estándares profesionales reales de la industria.\n    * Evalúa tanto competencias técnicas como capacidades de razonamiento y justificación.\n    * Proporciona retroalimentación específica para crecimiento profesional continuo.\n\nEsta actividad prepara a los estudiantes para enfrentar desafíos reales en ciencia de datos, desarrollando tanto competencias técnicas como habilidades de pensamiento crítico esenciales para el ejercicio profesional exitoso.""")
    st.markdown("---")
    if st.button("Continuar a Información General ➡️", type="primary", use_container_width=True, key="btn_to_info_gen_r3"):
        st.session_state.current_page_r3 = "Información General"; st.rerun()

elif current_page_display_r3 == "Información General":
    st.header("1. Información del Proyecto y Evaluador")
    # Usar st.form para asegurar el guardado explícito
    with st.form(key="info_general_form_r3_explicit"):
        st.text_input("Título del Proyecto:", value=st.session_state.get("titulo_proyecto_r3", ""), key="form_titulo_proyecto_r3")
        st.text_input("Estudiante(s) (Nombres, separados por coma):", value=st.session_state.get("estudiantes_r3", ""), key="form_estudiantes_r3")
        st.text_input("Evaluador:", value=st.session_state.get("evaluador_r3", ""), key="form_evaluador_r3")
        st.date_input("Fecha de Evaluación:", value=st.session_state.get("fecha_evaluacion_r3", datetime.now().date()), key="form_fecha_evaluacion_r3")
        
        submitted_info = st.form_submit_button("Guardar Información y Continuar a Evaluación ➡️", type="primary", use_container_width=True)
        if submitted_info:
            # Guardar explícitamente desde las claves del formulario al estado principal de la app
            st.session_state.titulo_proyecto_r3 = st.session_state.form_titulo_proyecto_r3
            st.session_state.estudiantes_r3 = st.session_state.form_estudiantes_r3
            st.session_state.evaluador_r3 = st.session_state.form_evaluador_r3
            st.session_state.fecha_evaluacion_r3 = st.session_state.form_fecha_evaluacion_r3
            
            st.toast("Información general guardada.", icon="📝")
            st.session_state.current_page_r3 = list(rubrica_data_r3.keys())[0] # Primera sección de la rúbrica
            st.rerun() 
    st.markdown("---")
    if st.button("⬅️ Anterior: Descripción de la Actividad", use_container_width=True, key="btn_back_to_desc_r3"):
        st.session_state.current_page_r3 = "Descripción de la Actividad"; st.rerun()

elif current_page_display_r3 in rubrica_data_r3:
    render_rubric_section_r3(current_page_display_r3, rubrica_data_r3[current_page_display_r3])
    idx_pagina_actual = list(rubrica_data_r3.keys()).index(current_page_display_r3)
    cols_nav_rubric = st.columns(2)
    if idx_pagina_actual > 0: # No es la primera sección de la rúbrica
        if cols_nav_rubric[0].button(f"⬅️ Anterior: {list(rubrica_data_r3.keys())[idx_pagina_actual - 1]}", use_container_width=True, key=f"prev_r3_{current_page_display_r3}"):
            st.session_state.current_page_r3 = list(rubrica_data_r3.keys())[idx_pagina_actual - 1]; st.rerun()
    else: # Es la primera sección de la rúbrica
        if cols_nav_rubric[0].button("⬅️ Anterior: Información General", use_container_width=True, key=f"prev_to_info_r3_{current_page_display_r3}"):
            st.session_state.current_page_r3 = "Información General"; st.rerun()

    if idx_pagina_actual < len(rubrica_data_r3) - 1: # No es la última sección de la rúbrica
        if cols_nav_rubric[1].button(f"Siguiente: {list(rubrica_data_r3.keys())[idx_pagina_actual + 1]} ➡️", type="primary", use_container_width=True, key=f"next_r3_{current_page_display_r3}"):
            st.session_state.current_page_r3 = list(rubrica_data_r3.keys())[idx_pagina_actual + 1]; st.rerun()
    else: # Es la última sección de la rúbrica
        if cols_nav_rubric[1].button("Ver Resultados y Retroalimentación 🏁", type="primary", use_container_width=True, key=f"to_results_r3_{current_page_display_r3}"):
            st.session_state.current_page_r3 = "Resultados y Retroalimentación"; st.rerun()

elif current_page_display_r3 == "Resultados y Retroalimentación":
    st.header("📊 Resultados Finales y Retroalimentación")
    resultados_r3 = calcular_resultados_r3()
    st.subheader("Puntuación Final del Proyecto")
    final_score = resultados_r3['total_puntos_obtenidos_final']
    qualitative_grade = get_qualitative_grade_r3(final_score)
    st.metric("PUNTUACIÓN FINAL", f"{final_score:.2f} / 100", delta=qualitative_grade, delta_color="off")
    if final_score >=0 : st.progress(min(1.0, final_score / 100))
    st.subheader("Desglose de Puntuación por Componente")
    component_data_list = []
    for seccion, data in resultados_r3["secciones"].items(): 
        if data["evaluada"]: component_data_list.append({ "Componente": seccion, "Puntos Obtenidos (Raw)": data["obtenido_raw"], "Máx. Raw": data["max_raw"], "Puntaje Escalado": f"{data['obtenido_escalado']:.2f} / {data['max_escalado']}"})
    if component_data_list: st.dataframe(pd.DataFrame(component_data_list), hide_index=True, use_container_width=True)
    else: st.info("No hay componentes evaluados para mostrar desglose.")
    
    st.subheader("Retroalimentación Constructiva")
    col_f, col_a = st.columns(2)
    with col_f:
        st.markdown("**Fortalezas Identificadas:**")
        for fortaleza_item in fortalezas_lista_r3:
            cb_key_f = f"cb_fort_{fortaleza_item.replace(' ', '_').replace('/','_')}_r3"
            current_val_f = st.session_state.retro_fortalezas_r3.get(fortaleza_item, False)
            # Usar una función lambda para on_change para actualizar el diccionario anidado directamente
            if st.checkbox(fortaleza_item, key=cb_key_f, value=current_val_f, 
                           on_change=lambda item_name, current_st_val: st.session_state.retro_fortalezas_r3.update({item_name: not current_st_val}), 
                           args=(fortaleza_item, current_val_f)): # Pasar el valor actual para el toggle
                pass # La lógica está en on_change
    with col_a:
        st.markdown("**Áreas de Mejora:**")
        for area_item in areas_mejora_lista_r3:
             cb_key_a = f"cb_area_{area_item.replace(' ', '_').replace('/','_')}_r3"
             current_val_a = st.session_state.retro_areas_mejora_r3.get(area_item, False)
             if st.checkbox(area_item, key=cb_key_a, value=current_val_a,
                            on_change=lambda item_name, current_st_val: st.session_state.retro_areas_mejora_r3.update({item_name: not current_st_val}),
                            args=(area_item, current_val_a)):
                 pass

    st.text_area("Recomendaciones Específicas para el equipo:", value=st.session_state.get("recomendaciones_especificas_r3",""), key="recomendaciones_especificas_r3", height=100)
    st.text_area("OBSERVACIONES ADICIONALES del evaluador:", value=st.session_state.get("observaciones_adicionales_r3",""), key="observaciones_adicionales_r3", height=150)

    if st.button("Generar Reporte HTML 📄", key="btn_generar_reporte_r3", type="primary", use_container_width=True):
        html_content_r3 = generar_html_reporte_r3(resultados_r3)
        b64_html_r3 = base64.b64encode(html_content_r3.encode()).decode()
        file_name_html_r3 = f"Reporte_DANE_{html.escape(st.session_state.get('titulo_proyecto_r3', 'Proyecto').replace(' ', '_'))}.html"
        st.markdown(get_html_download_link(html_content_r3, file_name_html_r3), unsafe_allow_html=True)
    if final_score > 70: st.balloons()

elif current_page_display_r3 == "Criterios de Evaluación (Referencia)":
    st.header("Criterios de Evaluación Completos (Referencia)")
    st.markdown("Esta sección muestra los detalles de los criterios de evaluación como referencia. La calificación interactiva se realiza en las páginas de cada componente.")
    secciones_para_referencia = ["1. SELECCIÓN Y JUSTIFICACIÓN DE BASE DE DATOS", "2. ANÁLISIS EXPLORATORIO DE DATOS - EDA", "3. TRATAMIENTO DE DATOS FALTANTES", "4. INGENIERÍA DE CARACTERÍSTICAS", "5. PROPUESTA METODOLÓGICA"]
    for seccion_nombre_ref in secciones_para_referencia:
        if seccion_nombre_ref in rubrica_data_r3:
            detalles_seccion_ref = rubrica_data_r3[seccion_nombre_ref]
            st.subheader(f"{seccion_nombre_ref} (Total: {detalles_seccion_ref['puntos_componente']} puntos)")
            for crit_key_ref, crit_details_ref in detalles_seccion_ref["criterios"].items():
                st.markdown(f"**{crit_key_ref}**")
                st.markdown(f"<small><i>{html.escape(crit_details_ref['descripcion'])}</i></small>", unsafe_allow_html=True)
                with st.expander("Ver descriptores de nivel detallados"):
                    for score_val_ref, desc_nivel_ref in sorted(crit_details_ref["niveles"].items(), reverse=True):
                        st.markdown(f"**{niveles_desempeno_r3.get(score_val_ref, str(score_val_ref))} ({score_val_ref} pts):** {html.escape(desc_nivel_ref)}")
                st.markdown("---")
        else: st.warning(f"Detalles para la sección '{html.escape(seccion_nombre_ref)}' no encontrados.")
    if st.button("⬅️ Volver a Resultados", key="back_to_results_from_ref_r3"):
        st.session_state.current_page_r3 = "Resultados y Retroalimentación"; st.rerun()