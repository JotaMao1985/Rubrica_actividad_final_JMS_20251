# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# --- Configuración de la Página ---
st.set_page_config(layout="wide", page_title="Rúbrica")

# --- Datos de la Rúbrica ---
# Claves corregidas para coincidir con los nombres de sección completos
pesos = {
    "Sección 1: Informe LaTeX": 0.20,
    "Sección 2: Jupyter/RMarkdown": 0.20,
    "Sección 3: Diapositivas Beamer": 0.30,
    "Sección 4: Exposición Oral": 0.30
}

# Descripciones de niveles actualizadas
criterios_seccion1 = {
    "1.1 Comprensión del Problema": {
        "Sobresaliente (85-100%)": "Identifica con precisión y profundidad el problema central del artículo, su relevancia y contexto. Demuestra una comprensión matizada de los desafíos.",
        "Notable (75-84%)": "Identifica correctamente el problema principal del artículo y su contexto general. La comprensión es sólida.",
        "Satisfactorio (65-74%)": "Identifica el problema principal, aunque la comprensión del contexto o la relevancia podría ser más superficial.",
        "Necesita Mejorar (50-64%)": "Identifica el problema de forma parcial o con imprecisiones. La comprensión del contexto es limitada.",
        "Insuficiente (0-49%)": "No logra identificar correctamente el problema o demuestra una comprensión muy deficiente del mismo."
    },
    "1.2 Comprensión de Métodos y Planteamientos": {
        "Sobresaliente (85-100%)": "Explica con claridad y detalle exhaustivo los métodos estadísticos y planteamientos del artículo. Demuestra un entendimiento profundo de su base teórica y aplicabilidad.",
        "Notable (75-84%)": "Explica con claridad los métodos y planteamientos. Demuestra un buen entendimiento de su base teórica y aplicabilidad.",
        "Satisfactorio (65-74%)": "Explica los métodos y planteamientos de forma general, pero puede faltar detalle o profundidad en la comprensión teórica o de aplicabilidad.",
        "Necesita Mejorar (50-64%)": "La explicación de los métodos es superficial, confusa o incorrecta en aspectos clave.",
        "Insuficiente (0-49%)": "No explica o demuestra una falta total de comprensión de los métodos y planteamientos."
    },
    "1.3 Comentario y Crítica del Uso y Aplicación de los Métodos": {
        "Sobresaliente (85-100%)": "Realiza una crítica perspicaz y bien fundamentada sobre la idoneidad, supuestos, limitaciones y robustez de los métodos aplicados. Identifica fortalezas y debilidades con argumentos sólidos.",
        "Notable (75-84%)": "Realiza una crítica adecuada sobre la aplicación de los métodos, identificando las principales fortalezas y debilidades con argumentos válidos.",
        "Satisfactorio (65-74%)": "Comenta sobre la aplicación de los métodos, pero la crítica puede ser general, poco profunda o carecer de suficiente argumentación.",
        "Necesita Mejorar (50-64%)": "La crítica es muy limitada, superficial, o se basa en malentendidos de los métodos o su aplicación.",
        "Insuficiente (0-49%)": "No realiza una crítica o esta es irrelevante o incorrecta."
    },
    "1.4 Propuesta de Métodos Alternativos o Mejoras": {
        "Sobresaliente (85-100%)": "Propone alternativas metodológicas (e.g., métodos no paramétricos si aplica, mejoras a los existentes) de forma creativa, justificada y viable, demostrando conocimiento avanzado y pensamiento crítico.",
        "Notable (75-84%)": "Propone alternativas o mejoras metodológicas relevantes y bien justificadas, demostrando buen conocimiento y capacidad de análisis.",
        "Satisfactorio (65-74%)": "Propone alguna alternativa o mejora, pero puede carecer de justificación detallada, originalidad o viabilidad práctica.",
        "Necesita Mejorar (50-64%)": "Las propuestas son vagas, poco realistas, o no están bien justificadas. Demuestra un conocimiento limitado de alternativas.",
        "Insuficiente (0-49%)": "No propone alternativas o mejoras, o las propuestas son completamente inadecuadas."
    },
    "1.5 Calidad del Documento LaTeX": {
        "Sobresaliente (85-100%)": "Documento impecable, profesionalmente formateado en LaTeX. Uso excelente de referencias, citas, figuras, tablas y estructura lógica. Sin errores de compilación o tipográficos.",
        "Notable (75-84%)": "Documento bien formateado en LaTeX, con buena estructura y uso adecuado de referencias y elementos visuales. Mínimos errores.",
        "Satisfactorio (65-74%)": "Documento funcional en LaTeX, pero con algunos problemas de formato, estructura o uso de referencias. Algunos errores menores.",
        "Necesita Mejorar (50-64%)": "Documento con problemas significativos de formato LaTeX, estructura deficiente, o errores que dificultan la lectura.",
        "Insuficiente (0-49%)": "El documento no está en LaTeX o presenta errores graves que impiden su evaluación, o el formato es extremadamente descuidado."
    },
    "1.6 Calidad de la Escritura y Argumentación": {
        "Sobresaliente (85-100%)": "Redacción clara, precisa, concisa y académicamente rigurosa. Argumentos lógicos, bien estructurados y persuasivos. Excelente gramática y ortografía.",
        "Notable (75-84%)": "Redacción clara y coherente. Argumentos bien presentados. Buena gramática y ortografía.",
        "Satisfactorio (65-74%)": "Redacción generalmente clara, pero con algunas áreas que podrían mejorar en precisión o fluidez. Argumentos comprensibles. Algunos errores gramaticales.",
        "Necesita Mejorar (50-64%)": "Redacción confusa en partes, argumentos débiles o mal estructurados. Errores gramaticales u ortográficos frecuentes.",
        "Insuficiente (0-49%)": "Redacción incomprensible, argumentos inexistentes o ilógicos. Numerosos errores gramaticales y ortográficos."
    }
}
criterios_seccion2 = {
    "2.1 Recreación de Procedimientos y Métodos del Artículo": {
        "Sobresaliente (85-100%)": "Recrea fielmente y con precisión los procedimientos y análisis del artículo. El código es eficiente, robusto y demuestra un dominio de las herramientas (Python/R) y librerías.",
        "Notable (75-84%)": "Recrea correctamente la mayoría de los procedimientos y análisis del artículo. El código es funcional y demuestra buena competencia con las herramientas.",
        "Satisfactorio (65-74%)": "Recrea los procedimientos principales, pero puede haber omisiones menores o imprecisiones. El código es funcional pero podría ser más eficiente o claro.",
        "Necesita Mejorar (50-64%)": "Intenta recrear los procedimientos, pero hay errores significativos, omisiones importantes o el código no es robusto.",
        "Insuficiente (0-49%)": "No logra recrear los procedimientos o el código es disfuncional, incompleto o irrelevante para el artículo."
    },
    "2.2 Análisis Exploratorio de Datos (EDA)": {
        "Sobresaliente (85-100%)": "Realiza un EDA exhaustivo, perspicaz y relevante para el problema. Identifica patrones, anomalías y supuestos clave de los datos, justificando las decisiones tomadas. Visualizaciones excelentes.",
        "Notable (75-84%)": "Realiza un EDA completo y adecuado. Identifica aspectos importantes de los datos y justifica las decisiones. Buenas visualizaciones.",
        "Satisfactorio (65-74%)": "Realiza un EDA básico, cubriendo los aspectos esenciales pero sin profundizar. Visualizaciones adecuadas pero podrían mejorar.",
        "Necesita Mejorar (50-64%)": "El EDA es superficial, incompleto o algunas conclusiones no están bien soportadas por los datos. Visualizaciones deficientes o ausentes.",
        "Insuficiente (0-49%)": "No realiza un EDA o este es irrelevante, incorrecto o no utiliza visualizaciones."
    },
    "2.3 Documentación del Código y Conexión con el Informe": {
        "Sobresaliente (85-100%)": "Código excelentemente documentado (comentarios claros, explicaciones concisas). Cada etapa está claramente conectada con las secciones correspondientes del informe LaTeX, facilitando la trazabilidad.",
        "Notable (75-84%)": "Código bien documentado. La conexión con el informe es clara y fácil de seguir en su mayor parte.",
        "Satisfactorio (65-74%)": "Código con documentación básica. La conexión con el informe es funcional pero podría ser más explícita o detallada.",
        "Necesita Mejorar (50-64%)": "Documentación escasa, confusa o ausente en partes significativas. La conexión con el informe es débil o difícil de establecer.",
        "Insuficiente (0-49%)": "Código sin documentación o esta es inútil. No hay conexión evidente con el informe."
    },
    "2.4 Calidad y Reproducibilidad del Código": {
        "Sobresaliente (85-100%)": "El código es limpio, bien estructurado, modular (si aplica) y sigue buenas prácticas de programación. Es fácilmente reproducible (e.g., uso de semillas, rutas relativas, gestión de dependencias).",
        "Notable (75-84%)": "El código es mayormente limpio y bien organizado. Es reproducible con instrucciones claras.",
        "Satisfactorio (65-74%)": "El código es funcional pero podría estar mejor organizado o ser más eficiente. La reproducibilidad puede requerir algunos ajustes menores.",
        "Necesita Mejorar (50-64%)": "El código es desorganizado, difícil de seguir o contiene errores que impiden su fácil ejecución o reproducibilidad.",
        "Insuficiente (0-49%)": "El código no se ejecuta, es caótico, o no es reproducible."
    }
}
criterios_seccion3 = {
    "3.1 Estructura Lógica y Coherencia": {
        "Sobresaliente (85-100%)": "Presentación perfectamente estructurada (introducción, métodos, resultados, discusión, conclusión) con un flujo narrativo claro, lógico y convincente. Todas las secciones están equilibradas.",
        "Notable (75-84%)": "Presentación bien estructurada con un flujo lógico claro. Las secciones son coherentes y están bien conectadas.",
        "Satisfactorio (65-74%)": "Presentación con una estructura adecuada, aunque el flujo o la conexión entre secciones podría mejorar. Alguna sección puede estar desequilibrada.",
        "Necesita Mejorar (50-64%)": "Estructura confusa o ilógica. El flujo de la presentación es difícil de seguir. Faltan secciones clave o están mal ubicadas.",
        "Insuficiente (0-49%)": "Sin estructura discernible o esta es caótica. Imposible seguir un hilo conductor."
    },
    "3.2 Claridad y Accesibilidad del Contenido": {
        "Sobresaliente (85-100%)": "Explicaciones excepcionalmente claras y concisas de métodos y resultados. Foco en los hallazgos más relevantes. Lenguaje accesible sin sacrificar rigor técnico.",
        "Notable (75-84%)": "Explicaciones claras de métodos y resultados. Buen foco en los hallazgos importantes. Lenguaje mayormente accesible.",
        "Satisfactorio (65-74%)": "Explicaciones comprensibles, pero pueden carecer de claridad en algunos puntos o ser demasiado técnicas/simplistas. Foco adecuado en los resultados.",
        "Necesita Mejorar (50-64%)": "Explicaciones confusas, incompletas o incorrectas de métodos o resultados. Dificultad para identificar los hallazgos principales.",
        "Insuficiente (0-49%)": "Contenido incomprensible, irrelevante o ausente."
    },
    "3.3 Visualizaciones": {
        "Sobresaliente (85-100%)": "Visualizaciones (gráficos, tablas) de alta calidad, simples, bien etiquetadas, estéticamente agradables y que apoyan efectivamente los puntos clave. Uso creativo y efectivo de pgfplots u otras herramientas.",
        "Notable (75-84%)": "Visualizaciones claras, bien etiquetadas y que apoyan los puntos clave. Buen uso de herramientas LaTeX.",
        "Satisfactorio (65-74%)": "Visualizaciones adecuadas y funcionales, pero podrían ser más claras, mejor diseñadas o más impactantes.",
        "Necesita Mejorar (50-64%)": "Visualizaciones pobres, mal etiquetadas, confusas, o que no apoyan el contenido. Poco o mal uso de herramientas LaTeX para gráficos.",
        "Insuficiente (0-49%)": "Ausencia de visualizaciones o estas son inintelligibles o irrelevantes."
    },
    "3.4 Diseño y Aspectos Técnicos (Beamer)": {
        "Sobresaliente (85-100%)": "Diseño profesional y consistente (plantilla uniforme, colores contrastantes, fuentes legibles). Texto breve y efectivo. Uso avanzado y apropiado de hyperref, pgfplots, etc. Evita animaciones excesivas.",
        "Notable (75-84%)": "Diseño limpio y consistente. Texto conciso. Buen uso de herramientas LaTeX. Animaciones, si las hay, son sutiles y efectivas.",
        "Satisfactorio (65-74%)": "Diseño funcional pero podría mejorar en consistencia o estética. Texto a veces denso. Uso básico de herramientas LaTeX.",
        "Necesita Mejorar (50-64%)": "Diseño descuidado, inconsistente o poco atractivo. Exceso de texto por diapositiva. Problemas técnicos con Beamer (errores de compilación visibles).",
        "Insuficiente (0-49%)": "Diseño caótico o inexistente. Diapositivas ilegibles o con errores graves de formato."
    },
    "3.5 Comunicación Persuasiva y Ética": {
        "Sobresaliente (85-100%)": "Comunica de manera altamente persuasiva, anticipa preguntas. Transparencia total en datos, métodos y posibles sesgos. Consideraciones éticas bien articuladas.",
        "Notable (75-84%)": "Comunica de forma clara y convincente. Aborda la transparencia y la ética adecuadamente.",
        "Satisfactorio (65-74%)": "Comunicación comprensible. Menciona aspectos de transparencia y ética, aunque de forma general.",
        "Necesita Mejorar (50-64%)": "Comunicación poco convincente o clara. Aspectos éticos o de transparencia omitidos o tratados superficialmente.",
        "Insuficiente (0-49%)": "Comunicación ineficaz. Omisión total de consideraciones éticas o de transparencia."
    },
    "3.6 Accesibilidad": {
        "Sobresaliente (85-100%)": "Considera activamente la accesibilidad (alto contraste, descripciones alternativas implícitas o explícitas para visualizaciones complejas).",
        "Notable (75-84%)": "Buen contraste y legibilidad general.",
        "Satisfactorio (65-74%)": "Contraste y legibilidad aceptables, pero sin consideraciones explícitas de accesibilidad.",
        "Necesita Mejorar (50-64%)": "Problemas de legibilidad (bajo contraste, fuentes pequeñas) que dificultan el acceso a la información.",
        "Insuficiente (0-49%)": "Diapositivas inaccesibles debido a malas elecciones de diseño."
    }
}
criterios_seccion4 = {
    "4.1 Dominio, Comprensión y Apropiación del Tema y Métodos": {
        "Sobresaliente (85-100%)": "Demuestra un dominio excepcional del artículo, los métodos estadísticos (incluyendo sus fundamentos y supuestos) y su aplicación. Se apropia completamente del contenido.",
        "Notable (75-84%)": "Demuestra una sólida comprensión del artículo y los métodos. Evidencia una buena apropiación del tema.",
        "Satisfactorio (65-74%)": "Demuestra una comprensión general del artículo y los métodos, aunque puede haber lagunas en la profundidad o en la conexión entre conceptos.",
        "Necesita Mejorar (50-64%)": "Comprensión superficial o con errores conceptuales significativos del artículo o los métodos. La apropiación del tema es limitada.",
        "Insuficiente (0-49%)": "Falta de comprensión fundamental del artículo o los métodos. No hay evidencia de apropiación del tema."
    },
    "4.2 Análisis Crítico del Artículo (Positivo, Negativo, Mejoras)": {
        "Sobresaliente (85-100%)": "Presenta un análisis crítico profundo, equilibrado y perspicaz del artículo, destacando aspectos positivos, negativos y proponiendo mejoras sustanciales y bien argumentadas.",
        "Notable (75-84%)": "Presenta un análisis crítico claro y bien argumentado, identificando adecuadamente los puntos fuertes, débiles y posibles mejoras.",
        "Satisfactorio (65-74%)": "Presenta un análisis crítico básico, mencionando algunos aspectos positivos y negativos, y quizás alguna mejora, pero con argumentación limitada.",
        "Necesita Mejorar (50-64%)": "Análisis crítico superficial, desequilibrado o con argumentación débil. Dificultad para identificar aspectos clave o proponer mejoras relevantes.",
        "Insuficiente (0-49%)": "No realiza un análisis crítico o este es irrelevante o incorrecto."
    },
    "4.3 Claridad, Elocuencia y Profesionalismo": {
        "Sobresaliente (85-100%)": "Exposición extremadamente clara, fluida y engaging. Lenguaje preciso y profesional. Excelente postura, contacto visual y modulación de la voz.",
        "Notable (75-84%)": "Exposición clara y bien organizada. Lenguaje adecuado y profesional. Buena postura y contacto visual.",
        "Satisfactorio (65-74%)": "Exposición mayormente clara, pero con algunas vacilaciones o falta de fluidez. Lenguaje apropiado. Postura y contacto visual adecuados.",
        "Necesita Mejorar (50-64%)": "Exposición confusa en partes, monótona o con problemas de dicción. Lenguaje informal o impreciso. Postura o contacto visual deficientes.",
        "Insuficiente (0-49%)": "Exposición incomprensible, desorganizada o extremadamente pobre. Falta de profesionalismo."
    },
    "4.4 Manejo del Tiempo (15-20 min)": {
        "Sobresaliente (85-100%)": "Gestiona el tiempo de forma impecable, cubriendo todos los puntos clave de manera equilibrada dentro del rango de 15-20 minutos.",
        "Notable (75-84%)": "Gestiona bien el tiempo, ajustándose al rango de 15-20 minutos y cubriendo los aspectos importantes.",
        "Satisfactorio (65-74%)": "Se ajusta razonablemente al tiempo, aunque puede apresurarse al final o extenderse ligeramente.",
        "Necesita Mejorar (50-64%)": "Dificultad significativa para gestionar el tiempo (demasiado corto o demasiado largo), omitiendo partes importantes o excediéndose considerablemente.",
        "Insuficiente (0-49%)": "Nulo control del tiempo."
    },
    "4.5 Respuesta a Preguntas": {
        "Sobresaliente (85-100%)": "Responde a las preguntas con confianza, precisión y profundidad, demostrando un entendimiento completo y capacidad para reflexionar críticamente.",
        "Notable (75-84%)": "Responde a las preguntas de manera correcta y clara, demostrando buena comprensión.",
        "Satisfactorio (65-74%)": "Responde a las preguntas adecuadamente en su mayoría, aunque algunas respuestas pueden ser superficiales o algo imprecisas.",
        "Necesita Mejorar (50-64%)": "Dificultad para responder preguntas, respuestas evasivas, incorrectas o que demuestran falta de comprensión.",
        "Insuficiente (0-49%)": "Incapaz de responder preguntas o las respuestas son completamente incorrectas."
    }
}

# Mapeos y listas
secciones_map = {
    "Introducción": "intro",
    "Información General": "info_general",
    "Sección 1: Informe LaTeX": "s1",
    "Sección 2: Jupyter/RMarkdown": "s2",
    "Sección 3: Diapositivas Beamer": "s3",
    "Sección 4: Exposición Oral": "s4",
    "Resultados y Comentarios Finales": "resultados"
}
secciones_display_order = list(secciones_map.keys())
criterios_por_seccion_key = {
    "s1": criterios_seccion1, "s2": criterios_seccion2,
    "s3": criterios_seccion3, "s4": criterios_seccion4,
}

# --- Inicialización del Estado de Sesión ---
def inicializar_estado():
    # Navegación
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Introducción"
    
    # Información General y Comentarios Generales
    general_comment_keys = {
        "nombre_estudiante": "", "articulo_analizado": "", "evaluador": "",
        "fecha_evaluacion": datetime.now().date(),
        "fortalezas_generales": "", "mejoras_generales": ""
    }
    for key, default_val in general_comment_keys.items():
        if key not in st.session_state: st.session_state[key] = default_val

    # Estructura de datos central para la evaluación
    if 'datos_evaluacion' not in st.session_state:
        st.session_state.datos_evaluacion = {}

    # Inicializar estructura para cada sección y sus criterios/comentarios
    for seccion_key_short, criterios_dict in criterios_por_seccion_key.items():
        # Asegurar que la entrada de la sección exista
        if seccion_key_short not in st.session_state.datos_evaluacion:
            st.session_state.datos_evaluacion[seccion_key_short] = {"criterios": {}, "comentario_seccion": ""}
        # Asegurar que la entrada de criterios exista
        elif "criterios" not in st.session_state.datos_evaluacion[seccion_key_short]:
             st.session_state.datos_evaluacion[seccion_key_short]["criterios"] = {}
        # Asegurar que la entrada de comentario exista
        elif "comentario_seccion" not in st.session_state.datos_evaluacion[seccion_key_short]:
             st.session_state.datos_evaluacion[seccion_key_short]["comentario_seccion"] = ""

        # Inicializar cada criterio dentro de la sección si no existe
        for idx, _ in enumerate(criterios_dict.keys()):
            if idx not in st.session_state.datos_evaluacion[seccion_key_short]["criterios"]:
                st.session_state.datos_evaluacion[seccion_key_short]["criterios"][idx] = {"score": 60, "na": False}
            else: # Asegurar que score y na existan dentro del criterio
                 if "score" not in st.session_state.datos_evaluacion[seccion_key_short]["criterios"][idx]:
                     st.session_state.datos_evaluacion[seccion_key_short]["criterios"][idx]["score"] = 60
                 if "na" not in st.session_state.datos_evaluacion[seccion_key_short]["criterios"][idx]:
                     st.session_state.datos_evaluacion[seccion_key_short]["criterios"][idx]["na"] = False
                     
        # Inicializar claves temporales para los widgets de comentario de sección (para value=...)
        # Leemos del estado centralizado si ya existe, si no, vacío.
        comment_widget_key = f"com_{seccion_key_short}"
        if comment_widget_key not in st.session_state:
             st.session_state[comment_widget_key] = st.session_state.datos_evaluacion[seccion_key_short].get("comentario_seccion", "")

    # Inicializar diccionario para promedios calculados
    if 'puntuaciones_secciones_bruto' not in st.session_state:
        st.session_state.puntuaciones_secciones_bruto = {
            nombre_largo: 0.0 for nombre_largo in pesos.keys() if nombre_largo in secciones_map # Asegurar que solo secciones válidas estén aquí
        }

inicializar_estado()

# --- Funciones de Lógica y Navegación ---
def guardar_datos_seccion_actual(seccion_key_short, criterios_dict):
    """Lee los valores de los widgets (desde st.session_state) y los guarda en datos_evaluacion."""
    if seccion_key_short not in st.session_state.datos_evaluacion:
        st.session_state.datos_evaluacion[seccion_key_short] = {"criterios": {}, "comentario_seccion": ""}
    
    for idx, _ in enumerate(criterios_dict.keys()):
        widget_score_key = f"widget_{seccion_key_short}_crit{idx}_score"
        widget_na_key = f"widget_{seccion_key_short}_crit{idx}_na"
        
        # Inicializar el diccionario para el criterio si no existe
        if idx not in st.session_state.datos_evaluacion[seccion_key_short]["criterios"]:
            st.session_state.datos_evaluacion[seccion_key_short]["criterios"][idx] = {}
            
        # Guardar score y na desde las claves de los widgets
        st.session_state.datos_evaluacion[seccion_key_short]["criterios"][idx]["score"] = st.session_state.get(widget_score_key, 60)
        st.session_state.datos_evaluacion[seccion_key_short]["criterios"][idx]["na"] = st.session_state.get(widget_na_key, False)

    # Guardar comentario de la sección
    widget_comment_key = f"com_{seccion_key_short}"
    st.session_state.datos_evaluacion[seccion_key_short]["comentario_seccion"] = st.session_state.get(widget_comment_key, "")
    
    # Calcular y actualizar el promedio después de guardar
    calcular_promedio_seccion(seccion_key_short, criterios_dict)

def calcular_promedio_seccion(seccion_key_short, criterios_dict):
    """Calcula el promedio basado en st.session_state.datos_evaluacion."""
    suma_puntajes = 0; criterios_evaluados = 0
    seccion_data = st.session_state.datos_evaluacion.get(seccion_key_short, {}).get("criterios", {})
    num_criterios_definidos = len(criterios_dict)

    for idx in range(num_criterios_definidos):
        crit_data = seccion_data.get(idx, {"score": 0, "na": True}) # Obtener datos guardados
        if not crit_data.get("na", False):
            suma_puntajes += crit_data.get("score", 0)
            criterios_evaluados += 1
            
    promedio = suma_puntajes / criterios_evaluados if criterios_evaluados > 0 else 0.0
    
    nombre_largo_seccion_actual = next((k for k, v in secciones_map.items() if v == seccion_key_short), None)
    
    # Asegurar que la clave exista en el diccionario de promedios antes de asignar
    if nombre_largo_seccion_actual and nombre_largo_seccion_actual in pesos: # Solo si la sección tiene peso
        if 'puntuaciones_secciones_bruto' not in st.session_state: # Inicializar si falta
             st.session_state.puntuaciones_secciones_bruto = {nl: 0.0 for nl in pesos.keys()}
        st.session_state.puntuaciones_secciones_bruto[nombre_largo_seccion_actual] = promedio

    return promedio

def navegar_a(nombre_pagina_display):
    st.session_state.current_page = nombre_pagina_display

def accion_navegacion(seccion_key_short_actual, criterios_dict_actual, proxima_pagina_display):
    """Callback para botones de formulario: guarda y navega."""
    guardar_datos_seccion_actual(seccion_key_short_actual, criterios_dict_actual)
    navegar_a(proxima_pagina_display)
    # st.rerun() es implícito al salir del callback de form_submit_button

# --- Generador de HTML (Leerá datos actualizados de st.session_state.datos_evaluacion) ---
def generar_html_reporte_v7():
    # Asegurar que los promedios estén actualizados antes de generar el reporte
    for skey_html, crit_dict_html in criterios_por_seccion_key.items():
        calcular_promedio_seccion(skey_html, crit_dict_html)

    total_ponderado_html = 0
    # Calcular puntaje total basado en los promedios almacenados
    for nombre_largo_html, promedio_bruto_html in st.session_state.puntuaciones_secciones_bruto.items():
         if nombre_largo_html in pesos: # Solo considerar secciones con peso
              total_ponderado_html += promedio_bruto_html * pesos[nombre_largo_html]

    # Inicio del HTML (estilos y encabezado)
    html_text = f"""
    <!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Reporte de Evaluación</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        h1, h2, h3 {{ color: #333; }} table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }} th {{ background-color: #f2f2f2; font-weight: bold; }}
        .criterio-nombre {{ font-weight: bold; }} .comentarios {{ white-space: pre-wrap; background-color: #f9f9f9; padding: 10px; border: 1px dashed #ccc; margin-top:5px;}}
        .total-score {{ font-size: 1.2em; font-weight: bold; color: #4CAF50; }} .na-text {{color: #777; font-style: italic;}}
        tfoot td {{font-weight: bold; background-color: #f0f2f6;}}
    </style></head><body>
    <h1>Reporte de Evaluación del Proyecto</h1> <h2>Información General</h2>
    <p><strong>Estudiante/Grupo:</strong> {st.session_state.get('nombre_estudiante', 'N/A')}</p>
    <p><strong>Artículo Científico Analizado:</strong> {st.session_state.get('articulo_analizado', 'N/A')}</p>
    <p><strong>Fecha de Evaluación:</strong> {st.session_state.get('fecha_evaluacion', datetime.now().date()).strftime('%Y-%m-%d')}</p>
    <p><strong>Evaluador:</strong> {st.session_state.get('evaluador', 'N/A')}</p><hr>
    """

    # Iterar por secciones y criterios guardados en datos_evaluacion
    for seccion_key_short_html, seccion_criterios_html in criterios_por_seccion_key.items():
        nombre_largo_seccion_html = next((k for k,v in secciones_map.items() if v == seccion_key_short_html), "Sección Desconocida")
        promedio_seccion_html = st.session_state.puntuaciones_secciones_bruto.get(nombre_largo_seccion_html, 0.0)
        peso_seccion_html = pesos.get(nombre_largo_seccion_html, 0) # Usar get para seguridad

        html_text += f"<h2>Sección: {nombre_largo_seccion_html} (Peso: {peso_seccion_html*100:.0f}%)</h2>"
        html_text += f"<p><strong>Promedio Sección: {promedio_seccion_html:.2f} / 100</strong></p>"
        html_text += "<table><thead><tr><th>Criterio</th><th>Puntuación</th></tr></thead><tbody>"
        
        criterios_data_html = st.session_state.datos_evaluacion.get(seccion_key_short_html, {}).get("criterios", {})
        for idx_html, nombre_criterio_html in enumerate(seccion_criterios_html.keys()): # Usar definición para asegurar orden
            crit_data_html = criterios_data_html.get(idx_html, {"score": 0, "na": True}) # Obtener datos guardados por índice
            puntaje_str_html = "<span class='na-text'>No Aplica</span>" if crit_data_html.get("na") else str(crit_data_html.get("score"))
            html_text += f"<tr><td class='criterio-nombre'>{nombre_criterio_html}</td><td>{puntaje_str_html}</td></tr>"
        html_text += "</tbody></table>"
        
        comentario_seccion_html = st.session_state.datos_evaluacion.get(seccion_key_short_html, {}).get("comentario_seccion", "")
        if comentario_seccion_html:
            # Escapar HTML en comentarios para seguridad
            import html
            comentario_escaped = html.escape(comentario_seccion_html)
            html_text += f"<h3>Comentarios para {nombre_largo_seccion_html}:</h3><div class='comentarios'>{comentario_escaped}</div>"
        html_text += "<hr>"

    # Resumen final
    html_text += f"""
        <h2>Puntuación Final y Comentarios Generales</h2>
        <p class='total-score'>Puntuación Total Ponderada: {total_ponderado_html:.2f} / 100</p>
        <h3>Desglose de Puntajes por Sección:</h3>
        <table><thead><tr><th>Sección</th><th>Promedio Sección</th><th>Peso</th><th>Aporte al Total</th></tr></thead><tbody>"""
    for nombre_largo_df_html, promedio_bruto_df_html in st.session_state.puntuaciones_secciones_bruto.items():
        if nombre_largo_df_html in pesos:
            peso_df_html = pesos[nombre_largo_df_html]
            aporte_total_df_html = promedio_bruto_df_html * peso_df_html
            html_text += f"<tr><td>{nombre_largo_df_html}</td><td>{promedio_bruto_df_html:.2f}</td><td>{peso_df_html*100:.0f}%</td><td>{aporte_total_df_html:.2f}</td></tr>"
    html_text += "</tbody></table>"

    fortalezas_g_html = st.session_state.get("fortalezas_generales", "")
    if fortalezas_g_html: html_text += f"<h3>Fortalezas Principales:</h3><div class='comentarios'>{html.escape(fortalezas_g_html)}</div>" # Escapar
    mejoras_g_html = st.session_state.get("mejoras_generales", "")
    if mejoras_g_html: html_text += f"<h3>Áreas de Mejora:</h3><div class='comentarios'>{html.escape(mejoras_g_html)}</div>" # Escapar
    html_text += "<hr><p style='text-align: center; font-size: 0.8em; color: #777;'>Reporte generado el " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "</p></body></html>"
    return html_text

def get_html_download_link(html_content, filename="reporte_evaluacion.html"):
    """Genera un enlace de descarga para contenido HTML."""
    b64 = base64.b64encode(html_content.encode()).decode()
    # Estilo mejorado para el botón de descarga
    link_style = """
    text-decoration: none; display:inline-block; margin-top: 15px; margin-bottom: 15px;
    padding: 12px 25px; background-color: #28a745; color: white; 
    border-radius: 5px; font-weight: bold; text-align:center;
    border: none; cursor: pointer; transition: background-color 0.3s ease;
    """
    hover_style = "background-color: #218838;" # Estilo al pasar el mouse
    # Nota: El estilo hover directo no funciona bien en markdown, pero el estilo base sí.
    return f'<a href="data:text/html;base64,{b64}" download="{filename}" style="{link_style}">⬇️ Descargar Reporte HTML</a>'

# --- Interfaz de Usuario ---

# Sidebar (Sin cambios funcionales)
st.markdown("""<style> div[data-testid="stSidebar"] button { width: 100% !important; border-radius: 5px; margin-bottom: 3px; } </style>""", unsafe_allow_html=True)
st.sidebar.title("Navegación Rápida 🧭")
st.sidebar.warning("Usar esta navegación **NO GUARDA** los cambios de la sección actual. Use los botones 'Anterior/Siguiente' en el formulario principal.")
for nombre_display in secciones_display_order:
    sidebar_btn_key = f"sidebar_nav_btn_{secciones_map[nombre_display]}"
    is_active = (st.session_state.current_page == nombre_display)
    button_label = f"➡️ {nombre_display}" if is_active else nombre_display
    if st.sidebar.button(button_label, key=sidebar_btn_key, use_container_width=True):
        navegar_a(nombre_display)
        st.rerun()
st.sidebar.markdown("---")
#st.sidebar.info(f"Versión: {datetime.now().strftime('%Y%m%d.%H%M')}")

# --- Contenido Principal ---
current_page_display = st.session_state.current_page

# Página de Introducción
if current_page_display == "Introducción":
    st.title("📊 Tablero de Rúbrica Automatizada")
    st.markdown("---")
    st.header("Introducción y Objetivos del Proyecto")
    st.markdown("""
    El presente proyecto está diseñado para sumergir a los estudiantes en el análisis crítico y la aplicación práctica de la estadística, tomando como base la literatura científica actual relevante para los temas de la asignatura.
    A través de la disección de un artículo científico, se busca que los estudiantes no solo comprendan a cabalidad el problema abordado y las metodologías estadísticas empleadas, sino que también desarrollen un juicio crítico sobre su idoneidad y aplicación.

    **Los objetivos fundamentales de esta actividad son:**
    - **Fomentar la comprensión profunda:** Asegurar que los estudiantes puedan interpretar y explicar con claridad tanto el problema de investigación como los planteamientos y métodos estadísticos presentados en un contexto real.
    - **Desarrollar el pensamiento crítico y analítico:** Capacitar a los estudiantes para evaluar rigurosamente la aplicación de métodos estadísticos, identificando sus fortalezas, debilidades, y la validez de sus supuestos.
    - **Estimular la innovación y la propuesta de valor:** Incentivar a los estudiantes a proponer mejoras o métodos alternativos (incluyendo, cuando sea pertinente, enfoques no paramétricos) de manera justificada y coherente con el problema estudiado.
    - **Consolidar habilidades técnicas y de reproducibilidad:** Fortalecer la competencia en el uso de herramientas como LaTeX para la documentación científica y Jupyter Notebook/RMarkdown para el análisis exploratorio de datos, la recreación de procedimientos y la documentación exhaustiva del código.
    - **Perfeccionar la comunicación científica:** Desarrollar la capacidad de comunicar hallazgos, procedimientos y análisis críticos de forma estructurada, clara y persuasiva, tanto de manera escrita (informe) como visual (diapositivas Beamer) como oral (exposición).
    - **Promover la apropiación del conocimiento:** Lograr que los estudiantes integren y se apropien del conocimiento estadístico, demostrando dominio y soltura al discutir los temas y métodos abordados.

    Este proyecto, por lo tanto, integra la teoría con la práctica, la crítica con la propuesta, y la técnica con la comunicación, preparando a los estudiantes para enfrentar desafíos analíticos complejos en su futuro profesional.
    """)

# Página de Información General
elif current_page_display == "Información General":
    st.header("📝 Información de la Evaluación")
    # Claves de widget únicas para este formulario
    with st.form(key="info_general_form"):
        st.text_input("Nombre del Estudiante/Grupo:", value=st.session_state.get("nombre_estudiante", ""), key="widget_nombre_estudiante")
        st.text_input("Artículo Científico Analizado:", value=st.session_state.get("articulo_analizado", ""), key="widget_articulo_analizado")
        st.date_input("Fecha de Evaluación:", value=st.session_state.get("fecha_evaluacion", datetime.now().date()), key="widget_fecha_evaluacion")
        st.text_input("Evaluador:", value=st.session_state.get("evaluador", ""), key="widget_evaluador")
        
        submitted_info = st.form_submit_button("Guardar Información y Continuar a Sección 1 ➡️")
        if submitted_info:
            # Guardar en el estado principal al enviar
            st.session_state.nombre_estudiante = st.session_state.widget_nombre_estudiante
            st.session_state.articulo_analizado = st.session_state.widget_articulo_analizado
            st.session_state.fecha_evaluacion = st.session_state.widget_fecha_evaluacion
            st.session_state.evaluador = st.session_state.widget_evaluador
            navegar_a("Sección 1: Informe LaTeX")
            st.rerun() # Asegurar cambio de página inmediato
    st.markdown("---")

# Lógica para Secciones de Evaluación (Informe LaTeX, Jupyter, Beamer, Exposición Oral)
elif current_page_display in secciones_display_order[2:-1]: 
    page_display_name = current_page_display
    
    # Validaciones robustas para evitar errores
    if page_display_name not in secciones_map: st.error("Error interno: Nombre de página inválido."); st.stop()
    seccion_key_short_actual = secciones_map[page_display_name]
    if seccion_key_short_actual not in criterios_por_seccion_key: st.error(f"Error interno: No hay criterios para '{seccion_key_short_actual}'."); st.stop()
    criterios_dict_actual = criterios_por_seccion_key[seccion_key_short_actual]
    nombre_largo_seccion_actual = page_display_name
    peso_actual = pesos.get(nombre_largo_seccion_actual) 
    if peso_actual is None: st.error(f"Error interno: No se encontró peso para '{nombre_largo_seccion_actual}'. Verifica diccionario 'pesos'."); st.stop()
    
    # Renderizado de la sección
    st.header(f"{page_display_name} (Peso: {peso_actual*100:.0f}%)")
    form_key = f"form_{seccion_key_short_actual}"
    
    with st.form(key=form_key):
        # Renderizar criterios
        for idx, (nombre_criterio, desc_niveles) in enumerate(criterios_dict_actual.items()):
            widget_score_key = f"widget_{seccion_key_short_actual}_crit{idx}_score"
            widget_na_key = f"widget_{seccion_key_short_actual}_crit{idx}_na"
            
            # Leer valor inicial desde la estructura central de datos
            crit_data = st.session_state.datos_evaluacion.get(seccion_key_short_actual, {}).get("criterios", {}).get(idx, {"score": 60, "na": False})
            initial_score = crit_data.get("score", 60)
            initial_na = crit_data.get("na", False)

            st.subheader(nombre_criterio)
            col1_form, col2_form = st.columns([3,1])
            with col2_form: st.checkbox("No Aplica", key=widget_na_key, value=initial_na)
            with col1_form: st.slider("Puntuación:", 0, 100, value=initial_score, step=10, key=widget_score_key, disabled=st.session_state.get(widget_na_key, initial_na), format="%d")
            with st.expander("Ver descripciones de niveles"): st.markdown("".join([f"**{lvl}:** {desc}<br>" for lvl, desc in desc_niveles.items()]), unsafe_allow_html=True)
            st.markdown("---")
            
        # Comentario para la sección actual
        widget_comment_key = f"com_{seccion_key_short_actual}"
        initial_comment = st.session_state.datos_evaluacion.get(seccion_key_short_actual, {}).get("comentario_seccion", "")
        st.text_area(f"Comentarios para {page_display_name}:", value=initial_comment, key=widget_comment_key, height=100)
        st.markdown("---")

        # Botones de navegación del formulario
        idx_pagina_actual_en_orden = secciones_display_order.index(page_display_name)
        cols_nav = st.columns(3 if idx_pagina_actual_en_orden > 1 else 2) 
        
        if idx_pagina_actual_en_orden > 1: # Mostrar 'Anterior' si no es la primera página de evaluación ("Información General" es índice 1)
            pagina_anterior_display = secciones_display_order[idx_pagina_actual_en_orden - 1]
            cols_nav[0].form_submit_button("⬅️ Anterior", on_click=accion_navegacion, args=(seccion_key_short_actual, criterios_dict_actual, pagina_anterior_display), use_container_width=True)
            offset = 1
        else: offset = 0 

        if idx_pagina_actual_en_orden < len(secciones_display_order) - 2: # Si no es la última sección de evaluación
            pagina_siguiente_display = secciones_display_order[idx_pagina_actual_en_orden + 1]
            cols_nav[offset].form_submit_button("Siguiente ➡️", type="primary", on_click=accion_navegacion, args=(seccion_key_short_actual, criterios_dict_actual, pagina_siguiente_display), use_container_width=True)
        else: # Última sección de evaluación
             cols_nav[offset].form_submit_button("Ver Resultados y Comentarios Finales 🏁", type="primary", on_click=accion_navegacion, args=(seccion_key_short_actual, criterios_dict_actual, "Resultados y Comentarios Finales"), use_container_width=True)
             
    # Mostrar promedio DESPUÉS del form para reflejar el estado guardado si se hizo submit
    promedio_actual = calcular_promedio_seccion(seccion_key_short_actual, criterios_dict_actual) 
    st.subheader(f"Promedio {page_display_name}: {promedio_actual:.2f} / 100")

# Página de Resultados Finales
elif current_page_display == "Resultados y Comentarios Finales":
    st.header("📊 Puntuación Final y Comentarios Generales")
    for skey_res, crit_dict_res in criterios_por_seccion_key.items(): calcular_promedio_seccion(skey_res, crit_dict_res) # Asegurar promedios actualizados
    
    puntaje_total_ponderado = 0
    for nombre_largo_res, promedio_bruto_res in st.session_state.puntuaciones_secciones_bruto.items():
        if nombre_largo_res in pesos: puntaje_total_ponderado += promedio_bruto_res * pesos[nombre_largo_res]

    st.subheader(f"Puntuación Total Ponderada: {puntaje_total_ponderado:.2f} / 100")
    st.progress(min(max(0, int(puntaje_total_ponderado)), 100)) # Asegurar entre 0 y 100

    st.markdown("#### Desglose de Puntajes por Sección:")
    data_desglose = []
    for nombre_largo_df, promedio_bruto_df in st.session_state.puntuaciones_secciones_bruto.items():
        if nombre_largo_df in pesos:
            peso_df = pesos[nombre_largo_df]; aporte_total_df = promedio_bruto_df * peso_df
            data_desglose.append({ "Sección": nombre_largo_df, "Promedio Sección (0-100)": f"{promedio_bruto_df:.2f}", "Peso": f"{peso_df*100:.0f}%", "Aporte al Total": f"{aporte_total_df:.2f}" })
    if data_desglose: st.table(pd.DataFrame(data_desglose))
    else: st.info("No hay datos de secciones evaluadas para mostrar desglose.")

    st.text_area("Fortalezas Principales del Proyecto:", value=st.session_state.get("fortalezas_generales", ""), key="widget_fortalezas_generales", height=150)
    st.text_area("Áreas Principales de Mejora:", value=st.session_state.get("mejoras_generales", ""), key="widget_mejoras_generales", height=150)
    if st.button("Guardar Comentarios Generales", key="save_general_comments"):
        st.session_state.fortalezas_generales = st.session_state.widget_fortalezas_generales
        st.session_state.mejoras_generales = st.session_state.widget_mejoras_generales
        st.toast("Comentarios generales guardados.", icon="📝"); st.rerun()
        
    st.markdown("---")
    nombre_archivo_html = f"Reporte_{st.session_state.get('nombre_estudiante', 'Estudiante').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.html"
    html_reporte_str_v7 = generar_html_reporte_v7()
    st.markdown(get_html_download_link(html_reporte_str_v7, nombre_archivo_html), unsafe_allow_html=True)
    if puntaje_total_ponderado > 70: st.balloons()