import streamlit as st
import pandas as pd
import datetime
import json
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly no está instalado. Las visualizaciones de radar no estarán disponibles. Instale con: `pip install plotly`")

# --- Datos de la Rúbrica ---
RUBRIC_DATA = {
    "c1": {
        "title": "1. Dominio conceptual y manejo del notebook (10%)",
        "weight": 0.10,
        "levels": {
            5: "Excelente (5): El notebook demuestra dominio técnico y estadístico avanzado: código limpio, comentarios claros, uso eficiente de funciones y estructuras. Se aplican conceptos estadísticos y de programación con precisión.",
            4: "Satisfactorio (4): El notebook es funcional y claro; se usan adecuadamente las herramientas, aunque con algunos detalles mejorables en organización o estilo de código. Los conceptos se aplican correctamente.",
            3: "Parcialmente satisfactorio (3): El notebook contiene errores menores o falta de documentación parcial. Algunos procedimientos no están bien explicados. El dominio conceptual es básico.",
            2: "Insuficiente (2): El notebook presenta problemas técnicos (errores de ejecución, código poco claro) o omisiones significativas. Falta comprensión de conceptos clave.",
            1: "Deficiente (1): El notebook es incomprensible, no ejecutable o copiado sin entendimiento. Ausencia de dominio conceptual."
        }
    },
    "c2": {
        "title": "2. Estructura y claridad comunicativa (10%)",
        "weight": 0.10,
        "levels": {
            5: "Excelente (5): La presentación y el notebook tienen una estructura lógica impecable: introducción, desarrollo, resultados y conclusiones están bien definidos. Uso efectivo de gráficos, títulos y transiciones. Lenguaje claro y profesional.",
            4: "Satisfactorio (4): La estructura es clara y coherente, aunque con pequeñas falencias en fluidez o diseño visual. La información se entiende sin dificultad.",
            3: "Parcialmente satisfactorio (3): La estructura existe pero es inconsistente; algunos apartados carecen de conexión. La comunicación es comprensible, pero con esfuerzo.",
            2: "Insuficiente (2): La organización es deficiente: secuencia confusa, gráficos mal etiquetados, ausencia de narrativa clara.",
            1: "Deficiente (1): No hay estructura discernible. La comunicación es caótica o ininteligible."
        }
    },
    "c3": {
        "title": "3. Justificación de aplicación de procedimientos (10%)",
        "weight": 0.10,
        "levels": {
            5: "Excelente (5): Todos los pasos (imputación, ingeniería de variables, selección de modelos) están sólidamente justificados con base en supuestos estadísticos, características de los datos o literatura.",
            4: "Satisfactorio (4): La mayoría de decisiones metodológicas están justificadas. Se mencionan criterios razonables para cada elección.",
            3: "Parcialmente satisfactorio (3): Algunas justificaciones son débiles o incompletas. Se aplican métodos sin explicar completamente por qué.",
            2: "Insuficiente (2): Justificaciones mínimas o poco pertinentes. Decisiones metodológicas parecen arbitrarias.",
            1: "Deficiente (1): No se justifica ningún procedimiento. Uso mecánico de técnicas sin razonamiento."
        }
    },
    "c4": {
        "title": "4. Capacidad de síntesis (máx. 15 min) (10%)",
        "weight": 0.10,
        "levels": {
            5: "Excelente (5): La exposición cubre todos los aspectos clave con precisión y elegancia, ajustándose perfectamente al tiempo. Prioriza lo más relevante sin sacrificar rigor.",
            4: "Satisfactorio (4): La exposición es clara y completa, termina a tiempo o con ligera sobrecarga (<2 min). Buena selección de contenidos.",
            3: "Parcialmente satisfactorio (3): La exposición supera el tiempo entre 2 y 4 minutos o deja fuera elementos importantes por apresuramiento.",
            2: "Insuficiente (2): Excede el tiempo entre 4 y 6 minutos o omite secciones clave por mala planificación.",
            1: "Deficiente (1): Excede ampliamente el tiempo (>6 min) o no logra transmitir el núcleo del trabajo."
        }
    },
    "c5": {
        "title": "5. Argumentación crítica y respuesta a preguntas (10%)",
        "weight": 0.10,
        "levels": {
            5: "Excelente (5): Respuestas precisas, reflexivas y basadas en evidencia. Demuestran profunda comprensión del análisis y conciencia de limitaciones. Capacidad de debate académico.",
            4: "Satisfactorio (4): Respuestas correctas y razonadas. Reconocen aspectos clave del modelo y datos. Alguna limitación identificada.",
            3: "Parcialmente satisfactorio (3): Respuestas parciales o con dudas menores. Algunas preguntas se responden de forma incompleta.",
            2: "Insuficiente (2): Dificultad para responder preguntas técnicas. Confusión sobre decisiones metodológicas.",
            1: "Deficiente (1): No responde o da respuestas incorrectas. Muestra desconocimiento del trabajo presentado."
        }
    },
    "c6": {
        "title": "6. Análisis exploratorio de datos (AED) (15%)",
        "weight": 0.15,
        "levels": {
            5: "Excelente (5): AED exhaustivo: estadísticos descriptivos relevantes, múltiples gráficos bien interpretados, detección de patrones, outliers y relaciones. Uso avanzado de visualización.",
            4: "Satisfactorio (4): AED completo con estadísticos y gráficos adecuados. Interpretaciones correctas, aunque con menor profundidad.",
            3: "Parcialmente satisfactorio (3): AED básico: se presentan medidas y gráficos, pero con interpretaciones superficiales o limitadas.",
            2: "Insuficiente (2): AED incompleto: falta análisis de variables clave o gráficos inadecuados.",
            1: "Deficiente (1): Ausencia de análisis exploratorio significativo."
        }
    },
    "c7": {
        "title": "7. Manejo de datos: imputación e ingeniería (10%)",
        "weight": 0.10,
        "levels": {
            5: "Excelente (5): Imputación realizada con método apropiado (ej. múltiple, KNN) y justificado. Ingeniería de variables creativa y útil, mejora sustancial el modelo.",
            4: "Satisfactorio (4): Imputación adecuada (ej. media, mediana) con justificación. Se crean nuevas variables relevantes.",
            3: "Parcialmente satisfactorio (3): Imputación aplicada, pero método cuestionable o mal justificado. Poca o nula ingeniería de características.",
            2: "Insuficiente (2): Intento fallido de imputación o ingeniería. Sin justificación.",
            1: "Deficiente (1): No se aborda el problema de datos faltantes ni se transforman variables."
        }
    },
    "c8": {
        "title": "8. Aplicación de métodos de machine learning (15%)",
        "weight": 0.15,
        "levels": {
            5: "Excelente (5): Aplica al menos dos métodos distintos, compara su desempeño, valida modelos (cross-validation), y selecciona el mejor con criterios claros (RMSE, accuracy, etc.).",
            4: "Satisfactorio (4): Aplica uno o dos métodos correctamente, con métricas de evaluación. Validación básica.",
            3: "Parcialmente satisfactorio (3): Aplica un método, pero sin validación adecuada o comparación. Métricas incompletas.",
            2: "Insuficiente (2): Implementación técnica presente, pero con errores o sin métricas.",
            1: "Deficiente (1): No aplica métodos de machine learning o entrega resultados sin sentido."
        }
    },
    "c9": {
        "title": "9. Calidad del objetivo y enfoque analítico (10%)",
        "weight": 0.10,
        "levels": {
            5: "Excelente (5): Objetivo claro, relevante y viable. Enfoque analítico coherente desde el inicio hasta el final. Todo el trabajo gira en torno a responder una pregunta bien formulada.",
            4: "Satisfactorio (4): Objetivo claro y adecuado. El análisis sigue una línea lógica, aunque con algún desvío menor.",
            3: "Parcialmente satisfactorio (3): Objetivo definido, pero poco ambicioso o con enfoque difuso. Análisis algo disperso.",
            2: "Insuficiente (2): Objetivo vago o mal definido. Falta coherencia entre objetivos y métodos.",
            1: "Deficiente (1): Objetivo ausente o irrelevante. Trabajo sin dirección analítica."
        }
    }
}

# --- Textos de Instrucciones y Diseño ---
INSTRUCTIONS_MD = """
**Introducción:**

Esta actividad tiene como objetivo que los estudiantes desarrollen competencias prácticas y críticas en el análisis estadístico y metodológico de bases de datos reales, provenientes de fuentes oficiales como Microdatos DANE o Datos Abiertos. Cada grupo, conformado por máximo tres personas, deberá seleccionar una base de datos publicada en los últimos dos años, explorarla en profundidad, aplicar técnicas de ciencia de datos y machine learning con un propósito claro de estimación, y presentar sus hallazgos de manera clara y rigurosa. La entrega incluirá un notebook bien documentado en Google Colab y una exposición oral de 15 minutos. Esta experiencia integrará conocimientos teóricos con habilidades técnicas y comunicativas, promoviendo el pensamiento analítico y la argumentación basada en evidencia.
"""

DESIGN_MD = """
### **Explicación de las decisiones de diseño instruccional**

1. **Enfoque integral y progresivo**:  
   La rúbrica está diseñada para evaluar tanto habilidades técnicas (manejo de datos, modelación) como competencias comunicativas y críticas. Esto refleja una visión moderna de la formación en estadística y ciencia de datos, donde el análisis no basta si no va acompañado de una buena interpretación y comunicación.

2. **Distribución ponderada equilibrada**:  
   - Los aspectos **técnicos centrales** (AED, machine learning, manejo de datos) suman el **40%**, reconociendo su importancia fundamental.  
   - Las **habilidades comunicativas y argumentativas** (estructura, síntesis, respuestas) suman otro **40%**, porque en la práctica profesional, explicar bien los resultados es tan importante como obtenerlos.  
   - El **dominio conceptual y la calidad del objetivo** (20%) aseguran que el trabajo tenga fundamento teórico y propósito claro.

3. **Énfasis en la justificación metodológica**:  
   Es crucial que los estudiantes no solo apliquen técnicas, sino que entiendan *por qué*. Por eso se incluye un criterio específico para evaluar la justificación de decisiones como imputación o selección de modelos, promoviendo el pensamiento crítico.

4. **Promoción de buenas prácticas de reproducibilidad**:  
   El notebook en Google Colab no solo facilita la revisión, sino que fomenta la documentación clara y el código reproducible. La rúbrica premia la limpieza, comentarios y organización del código.

5. **Tiempo limitado como recurso formativo**:  
   Limitar la exposición a 15 minutos obliga a los estudiantes a sintetizar, priorizar y comunicar eficientemente —una competencia clave en entornos académicos y laborales.

6. **Criterios observables y evitación de subjetividad**:  
   Cada nivel de la rúbrica describe conductas específicas y evidenciables (ej. “código limpio”, “justifica el método de imputación”), lo que garantiza una evaluación más objetiva y transparente.

7. **Adaptabilidad a contextos reales**:  
   Al usar bases de datos recientes del DANE o datos abiertos, los estudiantes trabajan con información actual y relevante para Colombia, fortaleciendo la conexión entre academia y realidad social.
"""

# --- Funciones ---
def create_radar_chart(scores_dict):
    """Crea un gráfico de radar con las puntuaciones obtenidas."""
    if not PLOTLY_AVAILABLE:
        return None

    categories = []
    values = []

    for key, item in RUBRIC_DATA.items():
        title_short = item["title"].split("(")[0].strip()
        if len(title_short) > 30:
            title_short = title_short[:27] + "..."
        categories.append(title_short)
        values.append((scores_dict[key] / 5) * 100)

    # Cerrar el gráfico duplicando el primer punto
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(245, 130, 32, 0.3)',
        line=dict(color='#f58220', width=2),
        marker=dict(size=8, color='#f58220'),
        name='Desempeño'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%',
                showline=True,
                linecolor='rgba(34,34,34,0.2)',
                gridcolor='rgba(34,34,34,0.1)'
            ),
            angularaxis=dict(
                linecolor='rgba(34,34,34,0.2)',
                gridcolor='rgba(34,34,34,0.1)'
            )
        ),
        showlegend=False,
        height=500,
        margin=dict(l=100, r=100, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def save_evaluation_to_json(project_name, eval_date, members, scores, feedbacks):
    """Guarda la evaluación en formato JSON."""
    evaluation_data = {
        "project_info": {
            "project_name": project_name,
            "eval_date": str(eval_date),
            "members": [m for m in members if m] # Filtrar miembros vacíos
        },
        "scores": scores,
        "feedbacks": feedbacks
    }
    return json.dumps(evaluation_data, indent=2, ensure_ascii=False).encode('utf-8')

def load_evaluation_from_json(json_data):
    """Carga una evaluación desde JSON."""
    try:
        evaluation_data = json.loads(json_data.decode('utf-8'))
        return evaluation_data, None
    except Exception as e:
        return None, f"Error al cargar el archivo: {str(e)}"

def generate_html_report(project_name, eval_date, members, scores, feedbacks, total_score_pct, weighted_scores):
    """Genera un reporte HTML completo de la evaluación."""
    members_list = [m for m in members if m]
    members_html = "<br>".join([f"{i+1}. {m}" for i, m in enumerate(members_list)])
    
    criteria_rows = ""
    for key, item in RUBRIC_DATA.items():
        score = scores[key]
        feedback = feedbacks[key] if feedbacks[key] else "Sin comentarios"
        weight = item['weight'] * 100
        weighted_score = weighted_scores[key]
        
        color = '#d4edda' if score >= 4 else '#fff3cd' if score >= 3 else '#f8d7da'
        
        criteria_rows += f"""
        <tr>
            <td>{item['title']}</td>
            <td style='background-color: {color}; text-align: center; font-weight: bold;'>{score}</td>
            <td style='text-align: center;'>{weight:.0f}%</td>
            <td style='text-align: center;'>{weighted_score:.2f}</td>
            <td>{feedback}</td>
        </tr>
        """
    
    # Generar datos para el gráfico de radar y calcular estadísticas
    radar_labels = []
    radar_values = []
    fortalezas_html = ""
    areas_mejora_html = ""
    
    for key, item in RUBRIC_DATA.items():
        score = scores[key]
        title_short = item["title"].split("(")[0].strip()
        
        # Preparar datos del radar
        if len(title_short) > 30:
            title_short = title_short[:27] + "..."
        radar_labels.append(title_short)
        radar_values.append((score / 5) * 100)
        
        # Identificar fortalezas y áreas de mejora
        if score >= 4:
            fortalezas_html += f"<li>✓ {RUBRIC_DATA[key]['title'].split('(')[0].strip()}</li>"
        elif score <= 2:
            areas_mejora_html += f"<li>✗ {RUBRIC_DATA[key]['title'].split('(')[0].strip()}</li>"
    
    if not fortalezas_html:
        fortalezas_html = "<li>No se identificaron fortalezas destacadas</li>"
    if not areas_mejora_html:
        areas_mejora_html = "<li>No se identificaron áreas críticas de mejora</li>"
    
    # Calcular estadísticas
    scores_list = list(scores.values())
    avg_score = sum(scores_list) / len(scores_list)
    max_score = max(scores_list)
    min_score = min(scores_list)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reporte de Evaluación - {project_name}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
            
            body {{
                font-family: 'Montserrat', sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 4px solid #f58220;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #222;
                margin: 0 0 10px 0;
            }}
            .header .subtitle {{
                color: #666;
                font-size: 1.1rem;
            }}
            .info-box {{
                background: #f9f9f9;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                border-left: 5px solid #f58220;
            }}
            .info-box h2 {{
                margin-top: 0;
                color: #222;
            }}
            .info-row {{
                margin: 10px 0;
            }}
            .info-label {{
                font-weight: 600;
                color: #555;
            }}
            .score-box {{
                background: linear-gradient(135deg, #f58220 0%, #d9701a 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                margin: 30px 0;
                box-shadow: 0 5px 15px rgba(245, 130, 32, 0.3);
            }}
            .score-box h2 {{
                margin: 0;
                font-size: 1.2rem;
                font-weight: 600;
            }}
            .score-box .score {{
                font-size: 3.5rem;
                font-weight: 700;
                margin: 10px 0;
            }}
            .visualization-section {{
                margin: 40px 0;
                padding: 30px;
                background: #f9f9f9;
                border-radius: 15px;
            }}
            .visualization-section h2 {{
                color: #222;
                margin-top: 0;
            }}
            .chart-container {{
                display: flex;
                gap: 30px;
                align-items: flex-start;
                flex-wrap: wrap;
            }}
            .radar-chart {{
                flex: 2;
                min-width: 300px;
            }}
            .stats-box {{
                flex: 1;
                min-width: 250px;
            }}
            .stat-item {{
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
                border-left: 4px solid #f58220;
            }}
            .stat-label {{
                font-size: 0.9rem;
                color: #666;
                margin-bottom: 5px;
            }}
            .stat-value {{
                font-size: 1.5rem;
                font-weight: 700;
                color: #f58220;
            }}
            .strength-list, .improvement-list {{
                background: white;
                padding: 15px;
                margin: 15px 0;
                border-radius: 10px;
            }}
            .strength-list {{
                border-left: 4px solid #28a745;
            }}
            .improvement-list {{
                border-left: 4px solid #dc3545;
            }}
            .strength-list h4 {{
                color: #28a745;
                margin-top: 0;
            }}
            .improvement-list h4 {{
                color: #dc3545;
                margin-top: 0;
            }}
            .strength-list ul, .improvement-list ul {{
                margin: 10px 0;
                padding-left: 20px;
            }}
            .strength-list li {{
                color: #155724;
                margin: 5px 0;
            }}
            .improvement-list li {{
                color: #721c24;
                margin: 5px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border: 1px solid #ddd;
            }}
            th {{
                background: #f58220;
                color: white;
                font-weight: 600;
            }}
            tr:nth-child(even) {{
                background: #f9f9f9;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #eee;
                color: #666;
                font-size: 0.9rem;
            }}
            @media print {{
                body {{
                    background: white;
                }}
                .container {{
                    box-shadow: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 Reporte de Evaluación de Proyecto</h1>
                <div class="subtitle">Análisis Exploratorio y Modelación con Machine Learning</div>
            </div>
            
            <div class="info-box">
                <h2>Información del Proyecto</h2>
                <div class="info-row"><span class="info-label">Proyecto:</span> {project_name}</div>
                <div class="info-row"><span class="info-label">Fecha:</span> {eval_date}</div>
                <div class="info-row"><span class="info-label">Integrantes:</span><br>{members_html}</div>
            </div>
            
            <div class="score-box">
                <h2>Calificación Final</h2>
                <div class="score">{total_score_pct:.2f} / 100</div>
                <div>Equivalente a {(total_score_pct/20):.2f} / 5.0</div>
            </div>
            
            <div class="visualization-section">
                <h2>📊 Visualización del Desempeño</h2>
                <div class="chart-container">
                    <div class="radar-chart">
                        <canvas id="radarChart"></canvas>
                    </div>
                    <div class="stats-box">
                        <h3>Estadísticas Rápidas</h3>
                        <div class="stat-item">
                            <div class="stat-label">Promedio de Puntuaciones</div>
                            <div class="stat-value">{avg_score:.2f} / 5.0</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Puntuación Más Alta</div>
                            <div class="stat-value">{max_score} / 5.0</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Puntuación Más Baja</div>
                            <div class="stat-value">{min_score} / 5.0</div>
                        </div>
                        
                        <div class="strength-list">
                            <h4>💪 Fortalezas</h4>
                            <ul>
                                {fortalezas_html}
                            </ul>
                        </div>
                        
                        <div class="improvement-list">
                            <h4>📉 Áreas de Mejora</h4>
                            <ul>
                                {areas_mejora_html}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <h2>Desglose por Criterios</h2>
            <table>
                <thead>
                    <tr>
                        <th>Criterio</th>
                        <th style="text-align: center;">Puntaje (1-5)</th>
                        <th style="text-align: center;">Peso</th>
                        <th style="text-align: center;">Aporte</th>
                        <th>Retroalimentación</th>
                    </tr>
                </thead>
                <tbody>
                    {criteria_rows}
                </tbody>
            </table>
            
            <div class="footer">
                <p>Generado el {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")} - Universidad Compensar</p>
            </div>
        </div>
        
        <script>
            // Datos del gráfico de radar
            const radarLabels = {json.dumps(radar_labels, ensure_ascii=False)};
            const radarValues = {json.dumps(radar_values)};
            
            // Crear el gráfico de radar
            const ctx = document.getElementById('radarChart').getContext('2d');
            new Chart(ctx, {{
                type: 'radar',
                data: {{
                    labels: radarLabels,
                    datasets: [{{
                        label: 'Desempeño',
                        data: radarValues,
                        fill: true,
                        backgroundColor: 'rgba(245, 130, 32, 0.2)',
                        borderColor: '#f58220',
                        pointBackgroundColor: '#f58220',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: '#f58220',
                        borderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {{
                        r: {{
                            angleLines: {{
                                color: 'rgba(0, 0, 0, 0.1)'
                            }},
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.1)'
                            }},
                            pointLabels: {{
                                font: {{
                                    size: 12,
                                    family: 'Montserrat'
                                }},
                                color: '#222'
                            }},
                            ticks: {{
                                beginAtZero: true,
                                max: 100,
                                stepSize: 20,
                                callback: function(value) {{
                                    return value + '%';
                                }},
                                backdropColor: 'transparent'
                            }},
                            suggestedMin: 0,
                            suggestedMax: 100
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return 'Desempeño: ' + context.parsed.r.toFixed(1) + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html_content.encode('utf-8')

def load_custom_css():
    """Carga estilos CSS para imitar la paleta de UCompensar."""
    st.markdown("""
        <style>
            /* Importar Google Font */
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

            /* --- Variables de Color (Paleta UCompensar) --- */
            :root {
                --primary-color: #f58220; /* Naranja UCompensar */
                --dark-text: #222222;
                --light-gray-bg: #f9f9f9;
                --font-family: 'Montserrat', sans-serif;
            }

            /* --- Fuente General --- */
            html, body, [class*="st-"] {
                font-family: var(--font-family);
            }
            .main .block-container {
                padding-top: 2rem;
            }

            /* --- Tipografía (Títulos) --- */
            h1, h2 {
                font-family: var(--font-family);
                font-weight: 700 !important;
                color: var(--dark-text) !important;
            }
            h3 {
                font-family: var(--font-family);
                font-weight: 600 !important;
                color: var(--primary-color) !important;
            }

            /* --- Barra Lateral --- */
            [data-testid="stSidebar"] {
                background-color: var(--light-gray-bg);
            }
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
                color: var(--dark-text) !important;
            }

            /* --- Botones Principales (Enviar, Descargar) --- */
            [data-testid="stFormSubmitButton"] button, [data-testid="stDownloadButton"] button {
                background-color: var(--primary-color) !important;
                color: white !important;
                border-radius: 30px !important;
                border: none !important;
                padding: 0.5rem 1.5rem !important;
                font-weight: 600 !important;
                transition: all 0.3s ease;
            }
            [data-testid="stFormSubmitButton"] button:hover, [data-testid="stDownloadButton"] button:hover {
                background-color: #d9701a !important; /* Naranja más oscuro */
                transform: scale(1.02);
            }

            /* --- Pestañas (Tabs) --- */
            [data-testid="stTabs"] button[role="tab"] {
                border-radius: 20px 20px 0 0 !important;
                font-weight: 600 !important;
                color: var(--dark-text) !important;
            }
            [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
                background-color: var(--light-gray-bg) !important;
                color: var(--primary-color) !important;
                border-bottom: 3px solid var(--primary-color) !important;
            }

            /* --- Expanders (Criterios de Rúbrica) --- */
            [data-testid="stExpander"] summary {
                background-color: var(--light-gray-bg) !important;
                border: 1px solid #ddd !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
                color: var(--dark-text);
                transition: all 0.2s ease;
            }
            [data-testid="stExpander"] summary:hover {
                background-color: #eee !important;
            }
            
            /* Ocultar completamente el texto de Material Icons que aparece como texto */
            [data-testid="stExpander"] summary span {
                font-size: 0 !important;
            }
            [data-testid="stExpander"] summary span::before,
            [data-testid="stExpander"] summary span::after {
                font-size: 0 !important;
            }
            
            /* Forzar que solo el contenido del título sea visible */
            [data-testid="stExpander"] summary > div {
                font-size: 1rem !important;
            }
            
            /* Ocultar específicamente spans con clases de Material Icons */
            [data-testid="stExpander"] summary span[class*="material-icons"],
            [data-testid="stExpander"] summary span[class*="keyboard"] {
                display: none !important;
                visibility: hidden !important;
                width: 0 !important;
                height: 0 !important;
                font-size: 0 !important;
                line-height: 0 !important;
            }

            /* --- Radio Buttons (Puntuación) --- */
            [data-testid="stRadio"] label {
                padding: 0.5rem;
                border-radius: 10px;
                transition: all 0.2s ease;
            }
            [data-testid="stRadio"] label:hover {
                background-color: #fef0e4; /* Naranja muy claro */
            }

            /* --- Métrica (Resultado Final) --- */
            [data-testid="stMetric"] {
                background-color: var(--light-gray-bg);
                border-left: 5px solid var(--primary-color);
                padding: 1rem;
                border-radius: 10px;
            }
            [data-testid="stMetric"] [data-testid="stMetricValue"] {
                color: var(--primary-color) !important;
                font-size: 2.5rem !important;
                font-weight: 700 !important;
            }
            
            /* --- Barra de Progreso --- */
            [data-testid="stProgressBar"] > div > div {
                background-color: var(--primary-color) !important;
            }
        </style>
        """, unsafe_allow_html=True)

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Herramienta de Calificación UCompensar",
    page_icon="🎓",
    layout="wide"
)

load_custom_css()

# --- Barra Lateral ---
with st.sidebar:
    st.header("Detalles del Proyecto")

    project_name = st.text_input("Nombre del Proyecto/Artículo", placeholder="Ej: Análisis de Deserción Estudiantil")
    eval_date = st.date_input("Fecha de Evaluación", datetime.date.today())

    st.markdown("---")

    st.subheader("📂 Cargar Evaluación")
    uploaded_file = st.file_uploader(
        "Cargar evaluación guardada (JSON)",
        type=['json'],
        help="Cargue un archivo JSON previamente guardado"
    )

    if uploaded_file is not None:
        loaded_data, error = load_evaluation_from_json(uploaded_file.getvalue())
        if error:
            st.error(error)
        else:
            st.success("✅ Evaluación cargada exitosamente")
            # Opcional: Guardar en session_state para uso futuro
            st.session_state.loaded_evaluation = loaded_data
            st.info("📋 Vaya a la pestaña 'Calificar Proyecto' para ver los datos cargados")

    st.markdown("---")

    num_members = st.number_input(
        "Número de Integrantes (Máx. 3)",
        min_value=1,
        max_value=3,
        value=1,
        step=1,
        format="%d"
    )
    members = []
    for i in range(num_members):
        members.append(st.text_input(f"Nombre Integrante {i+1}", key=f"member_{i}"))
    
    st.markdown("---")
    
    st.subheader("🔄 Reiniciar")
    if st.button("🗑️ Nueva Evaluación", type="secondary", use_container_width=True):
        # Limpiar todos los estados relevantes del formulario
        keys_to_clear = [key for key in st.session_state.keys() if key.startswith(('score_', 'feedback_', 'open_expander'))]
        for key in keys_to_clear:
            del st.session_state[key]
        st.rerun()


# --- Títulos Principales ---
st.title("🎓 Herramienta de Evaluación de Proyectos")
st.subheader("Análisis Exploratorio y Modelación con Machine Learning")

# --- Pestañas ---
tab_intro, tab_rubric, tab_design = st.tabs([
    "ℹ️ Introducción",
    "📝 Calificar Proyecto",
    "📐 Diseño de la Rúbrica"
])

with tab_intro:
    st.header("Introducción a la Actividad")
    st.markdown(INSTRUCTIONS_MD)

with tab_design:
    st.header("Diseño Instruccional de la Rúbrica")
    st.markdown(DESIGN_MD)

with tab_rubric:
    st.header("Formulario de Calificación")

    st.info("💡 **Instrucción:** Evalúe cada criterio seleccionando el nivel de desempeño y agregando comentarios específicos.")
    st.warning("⚠️ Complete todos los campos. Los resultados se actualizarán automáticamente.")

    # Inicializar session_state para controlar qué expander está abierto
    if 'open_expander' not in st.session_state:
        st.session_state.open_expander = None

    # Layout con columnas: Formulario a la izquierda, Resultados a la derecha
    col_form, col_results = st.columns([3, 2])

    with col_form:
        with st.form(key="rubric_form"):
            scores = {}
            feedbacks = {}

            for key, item in RUBRIC_DATA.items():
                # Determinar si este expander debe estar abierto
                is_expanded = (st.session_state.open_expander == key)
                
                with st.expander(item["title"], expanded=is_expanded):
                    options = [item["levels"][i] for i in sorted(item["levels"].keys(), reverse=True)]

                    selected_option = st.radio(
                        "Seleccione la puntuación:",
                        options,
                        key=f"score_{key}",
                        horizontal=False
                    )
                    scores[key] = int(selected_option.split("(")[1].split(")")[0])

                    st.markdown("---")
                    feedbacks[key] = st.text_area(
                        "Retroalimentación específica para este criterio:",
                        key=f"feedback_{key}",
                        height=100
                    )

            submitted = st.form_submit_button("✅ Calcular Calificación Final", use_container_width=True)

    with col_results:
        st.markdown("### 📊 Resultados en Tiempo Real")
        
        if not submitted:
            st.info("👈 Complete el formulario y presione 'Calcular Calificación Final' para ver los resultados aquí.")
            
            if project_name:
                st.markdown(f"**Proyecto:** {project_name}")
            if any(members):
                st.markdown(f"**Integrantes:** {', '.join(filter(None, members))}")
        
    # --- Lógica Post-Formulario ---
    if submitted:
        is_valid = True
        if not project_name:
            st.error("❌ Error: Por favor, ingrese el 'Nombre del Proyecto' en la barra lateral.")
            is_valid = False

        if not all(members):
            st.warning("⚠️ Advertencia: No se han ingresado los nombres de todos los integrantes. Los campos vacíos no se incluirán en el reporte.")

        if is_valid:
            # --- Cálculo de la Puntuación ---
            total_score_pct = 0
            weighted_scores = {}

            for key, item in RUBRIC_DATA.items():
                score = scores[key]
                weight = item["weight"]
                item_score_pct = (score / 5) * (weight * 100)
                weighted_scores[key] = round(item_score_pct, 2)
                total_score_pct += item_score_pct

            total_score_pct = round(total_score_pct, 2)

            # --- Mostrar Resultados en Panel Derecho ---
            with col_results:
                st.success("✅ ¡Calificación calculada!")
                st.markdown(f"**Proyecto:** {project_name}")
                st.markdown(f"**Integrantes:** {', '.join(filter(None, members))}")

                st.markdown("---")
                st.metric("Calificación Final", f"{total_score_pct} / 100")
                st.progress(total_score_pct / 100)

                st.markdown("#### 🎯 Retroalimentación")
                if total_score_pct >= 95:
                    st.success("🌟 **¡Excelente!** Dominio excepcional.")
                elif total_score_pct >= 85:
                    st.success("✅ **¡Muy bien!** Proyecto sólido.")
                elif total_score_pct >= 70:
                    st.info("👍 **Bien.** Satisfactorio.")
                elif total_score_pct >= 60:
                    st.warning("⚠️ **Suficiente.** Mejorar.")
                else:
                    st.error("❌ **Insuficiente.**")

                st.markdown("#### 📥 Exportar")
                
                # Botón CSV
                export_data = []
                export_data.append(["Proyecto", project_name])
                export_data.append(["Fecha", str(eval_date)])
                for i, member in enumerate(filter(None, members)):
                    export_data.append([f"Integrante {i+1}", member])
                export_data.append(["", ""])
                export_data.append(["CALIFICACIÓN FINAL", total_score_pct, "Sobre 100"])
                export_data.append(["", ""])
                export_data.append(["Criterio", "Puntaje (1-5)", "Retroalimentación Específica"])
                
                for key, item in RUBRIC_DATA.items():
                    export_data.append([
                        item["title"],
                        scores[key],
                        feedbacks[key].replace("\n", " ") if feedbacks[key] else ""
                    ])
                
                df_export = pd.DataFrame(export_data)
                csv_file = df_export.to_csv(index=False, header=False, encoding='utf-8-sig').encode('utf-8-sig')
                safe_filename = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in project_name.lower())
                
                st.download_button(
                    label="📄 CSV",
                    data=csv_file,
                    file_name=f"calificacion_{safe_filename}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                # Botón JSON
                json_file = save_evaluation_to_json(project_name, eval_date, members, scores, feedbacks)
                st.download_button(
                    label="💾 JSON",
                    data=json_file,
                    file_name=f"evaluacion_{safe_filename}.json",
                    mime="application/json",
                    use_container_width=True
                )
                
                # Botón HTML
                html_file = generate_html_report(project_name, eval_date, members, scores, feedbacks, total_score_pct, weighted_scores)
                st.download_button(
                    label="📑 HTML",
                    data=html_file,
                    file_name=f"reporte_{safe_filename}.html",
                    mime="text/html",
                    use_container_width=True
                )

            # --- Detalles Completos Abajo ---
            st.markdown("---")
            st.header(f"📋 Detalles Completos - {project_name}")

            if PLOTLY_AVAILABLE:
                st.subheader("📊 Visualización del Desempeño")
                radar_chart = create_radar_chart(scores)
                if radar_chart:
                    col_chart, col_stats = st.columns([3, 2])
                    with col_chart:
                        st.plotly_chart(radar_chart, use_container_width=True)
                    with col_stats:
                        st.markdown("#### Estadísticas Rápidas")
                        scores_list = list(scores.values())
                        st.metric("Promedio de Puntuaciones", f"{sum(scores_list)/len(scores_list):.2f} / 5.0")
                        st.metric("Puntuación Más Alta", f"{max(scores_list)} / 5.0")
                        st.metric("Puntuación Más Baja", f"{min(scores_list)} / 5.0")

                        st.markdown("#### 💪 Fortalezas y 📉 Áreas de Mejora")
                        for key, score in scores.items():
                            if score >= 4:
                                st.success(f"✓ {RUBRIC_DATA[key]['title'].split('(')[0].strip()[:40]}...")
                        for key, score in scores.items():
                            if score <= 2:
                                st.error(f"✗ {RUBRIC_DATA[key]['title'].split('(')[0].strip()[:40]}...")

                st.markdown("---")

            st.subheader("Desglose de Calificación y Retroalimentación")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("#### Desglose de Puntuación")
                results_data = []
                for key, item in RUBRIC_DATA.items():
                    results_data.append({
                        "Criterio": item["title"].split("(")[0].strip(),
                        "Puntaje (1-5)": scores[key],
                        "Peso": f"{item['weight']*100:.0f}%",
                        "Aporte a la Nota": weighted_scores[key]
                    })

                df_results = pd.DataFrame(results_data)

                def color_score(val):
                    if isinstance(val, (int, float)):
                        if val >= 4:
                            color = 'background-color: #d4edda; color: #155724;'
                        elif val >= 3:
                            color = 'background-color: #fff3cd; color: #856404;'
                        else:
                            color = 'background-color: #f8d7da; color: #721c24;'
                        return color
                    return ''

                styled_df = df_results.style.applymap(color_score, subset=['Puntaje (1-5)'])
                st.dataframe(styled_df, use_container_width=True)

            with col2:
                st.markdown("#### Retroalimentación Específica")
                for key, feedback in feedbacks.items():
                    if feedback.strip():
                        st.markdown(f"**{RUBRIC_DATA[key]['title'].split('(')[0].strip()}**")
                        st.info(feedback)

