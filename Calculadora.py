import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Sistema de Costeo de Concursos - ESAP",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# PALETA DE COLORES ESAP Y ESTILOS CSS
# ==============================================================================
ESAP_PALETTE = {
    "primary": "#003366",      # Azul institucional ESAP
    "secondary": "#004080",   # Azul secundario
    "accent": "#FF8C00",      # Naranja ESAP
    "orange": "#FFA500",      # Naranja claro
    "neutral_light": "#f8f9fa",
    "neutral_mid": "#6c757d",
    "neutral_dark": "#333333",
}

st.markdown(
    f"""
    <style>
        :root {{
            --esap-primary: {ESAP_PALETTE['primary']};
            --esap-secondary: {ESAP_PALETTE['secondary']};
            --esap-accent: {ESAP_PALETTE['accent']};
            --esap-orange: {ESAP_PALETTE['orange']};
        }}
        
        .stApp {{
            background: linear-gradient(180deg, rgba(0,51,102,0.05) 0%, rgba(255,140,0,0.02) 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #003366 0%, #004080 50%, #003366 100%);
            border-right: 3px solid var(--esap-accent);
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }}
        
        section[data-testid="stSidebar"] * {{
            color: #ffffff !important;
        }}
        
        section[data-testid="stSidebar"] .stRadio label {{
            font-weight: 600;
            font-size: 0.95rem;
        }}
        
        section[data-testid="stSidebar"] .stRadio > div {{
            background: rgba(255,255,255,0.1);
            padding: 0.5rem;
            border-radius: 8px;
        }}
        
        /* Métricas */
        .stMetric {{
            background: rgba(255,255,255,0.95);
            padding: 1.2rem;
            border-radius: 12px;
            border-left: 4px solid var(--esap-accent);
            box-shadow: 0 4px 12px rgba(0,51,102,0.1);
            transition: transform 0.2s ease;
        }}
        
        .stMetric:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,51,102,0.15);
        }}
        
        div[data-testid="stMetricValue"] {{
            color: var(--esap-primary) !important;
            font-weight: 700;
            font-size: 2rem;
        }}
        
        div[data-testid="stMetricLabel"] {{
            color: var(--esap-neutral-mid) !important;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
        }}
        
        /* Botones */
        .stButton button {{
            background: linear-gradient(135deg, var(--esap-accent), var(--esap-orange));
            color: #ffffff !important;
            font-weight: 700;
            border-radius: 8px;
            border: none;
            padding: 0.7rem 2rem;
            box-shadow: 0 4px 8px rgba(255,140,0,0.3);
            transition: all 0.3s ease;
        }}
        
        .stButton button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(255,140,0,0.4);
        }}
        
        /* Títulos */
        h1 {{
            color: #000000 !important;
            font-weight: 700;
            border-bottom: 3px solid var(--esap-accent);
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }}
        
        h2 {{
            color: #000000 !important;
            font-weight: 600;
        }}
        
        h3 {{
            color: #000000 !important;
            font-weight: 600;
        }}
        
        /* DataFrames y Tablas */
        .stDataFrame {{
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,51,102,0.08);
            border: 1px solid rgba(0,51,102,0.1);
        }}
        
        /* Columnas */
        div[data-testid="column"] {{
            background: rgba(255,255,255,0.5);
            padding: 1rem;
            border-radius: 8px;
        }}
        
        /* Notificaciones */
        div[data-testid="stNotification"] {{
            border-left: 4px solid var(--esap-accent);
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background: rgba(0,51,102,0.05);
            border-left: 3px solid var(--esap-accent);
            font-weight: 600;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 1. LÓGICA DEL NEGOCIO (FUNCIONES DEL MODELO PARAMÉTRICO)
# ==============================================================================

def obtener_tarifa_transporte(ciudad, n_aspirantes):
    """
    Calcula el costo de transporte basado en RANGOS DE VOLUMEN (Lotes de seguridad),
    aproximando la realidad del archivo CSV donde los costos son por 'Cuadernillo/Lote'
    y no por 'Sitio'.
    
    Retorna: Costo Total del Transporte, Tarifa Promedio Aplicada
    """
    # Normalización de nombre
    ciudad_key = ciudad.title()
    
    # BASE DE DATOS DE TARIFAS POR LOTES (Aproximación Opción B)
    # Estructura: (Rango_Min, Rango_Max, Precio_Total_del_Lote)
    # Estos precios incluyen: Recolección + Transporte Seguro + Custodia + Retorno
    
    tarifarios = {
        # ZONA A: Ciudades Principales (Logística terrestre estándar)
        'Bogotá': [
            (0, 200, 450000),       # Costo mínimo de operación
            (201, 1000, 1200000),   # Camión mediano
            (1001, 5000, 3500000),  # Logística mayor
            (5001, 999999, 8000000)
        ],
        'Medellín': [
            (0, 200, 600000),
            (201, 1000, 1800000),
            (1001, 5000, 5500000),
            (5001, 999999, 12000000)
        ],
        'Cali': [
            (0, 200, 600000),
            (201, 1000, 1800000),
            (1001, 5000, 5500000),
            (5001, 999999, 12000000)
        ],
        
        # ZONA B: Ciudades Intermedias (Requiere logística dedicada)
        'Ibagué': [(0, 500, 900000), (501, 999999, 4000000)],
        'Tunja': [(0, 500, 900000), (501, 999999, 4000000)],
        'Villavicencio': [(0, 500, 1000000), (501, 999999, 4500000)],
        'Pereira': [(0, 500, 1100000), (501, 999999, 4800000)],
        
        # ZONA C: Costa y Norte (Logística terrestre larga distancia o aérea mixta)
        'Barranquilla': [(0, 500, 1500000), (501, 2000, 4500000), (2001, 999999, 9000000)],
        'Cartagena': [(0, 500, 1500000), (501, 2000, 4500000), (2001, 999999, 9000000)],
        'Santa Marta': [(0, 500, 1600000), (501, 2000, 4800000), (2001, 999999, 9500000)],
        'Riohacha': [(0, 500, 2000000), (501, 999999, 6000000)],
        'Valledupar': [(0, 500, 1800000), (501, 999999, 5500000)],
        
        # ZONA D: Zonas Especiales / Difícil Acceso (Aéreo Obligatorio / Fluvial)
        # Basado en tus datos de San Andrés, Chocó, Arauca, etc.
        'San Andrés': [
            (0, 100, 2500000),      # Costo de entrada muy alto (Avión valores)
            (101, 500, 4500000),
            (501, 2000, 9000000),
            (2001, 999999, 15000000)
        ],
        'Quibdó': [(0, 200, 2200000), (201, 999999, 6000000)],
        'Arauca': [(0, 200, 2000000), (201, 999999, 5500000)],
        'Pasto': [(0, 200, 1800000), (201, 999999, 5000000)],
        'Cúcuta': [(0, 200, 1500000), (201, 999999, 4500000)],
        'Popayán': [(0, 200, 1200000), (201, 999999, 3500000)]
    }
    
    # 1. Seleccionar Tabla (Fallback a promedio nacional si no existe la ciudad)
    tabla_tarifas = tarifarios.get(ciudad_key, tarifarios.get('Ibagué', [(0, 999999, n_aspirantes * 3000)]))

    # 2. Buscar el precio en el rango
    costo_total = 0
    for r_min, r_max, precio in tabla_tarifas:
        if r_min <= n_aspirantes <= r_max:
            costo_total = precio
            break
    
    # Si se sale del rango máximo, usamos el precio más alto + variable por aspirante extra
    if costo_total == 0:
        ultimo_rango = tabla_tarifas[-1]
        costo_base = ultimo_rango[2]
        extra_aspirantes = n_aspirantes - ultimo_rango[1]
        costo_total = costo_base + (extra_aspirantes * 2000)

    return costo_total

def calcular_modelo_parametrico(n_aspirantes, ciudad, tipo_prueba):
    # --- A. MOTOR LÓGICO (Cantidades Físicas - Deterministas) ---
    n_sitios = math.ceil(n_aspirantes / 500)
    n_salones = math.ceil(n_aspirantes / 25)
    
    # Personal Logístico
    n_delegados = n_sitios
    n_coord_sitio = n_sitios
    n_coord_aula = math.ceil(n_salones / 6)
    n_jefes_salon = n_salones * (1 if tipo_prueba == "Escrita" else 2)
    n_dactilo = math.ceil(n_salones / 4)
    n_aseo = math.ceil(n_salones / 6)
    n_seguridad = n_sitios * 2
    
    # --- B. MOTOR FINANCIERO (Con Variabilidad) ---
    
    # 1. Transporte (El rubro más volátil)
    costo_transporte_base = obtener_tarifa_transporte(ciudad, n_aspirantes)
    
    # RIESGO: Aplicamos un rango del -5% al +20% para transporte
    transporte_min = costo_transporte_base * 0.95
    transporte_max = costo_transporte_base * 1.20
    
    # 2. Nómina
    precios_nomina = {
        'Delegado de Sitio': 300000, 'Coordinador de Sitio': 283333,
        'Coordinador de Aulas': 283333, 'Jefe de Salón': 200000,
        'Dactiloscopista': 200000, 'Auxiliar de Aseo': 200000,
        'Seguridad': 200000
    }
    
    detalle_nomina = [
        {'Cargo': 'Delegado de Sitio', 'Cantidad': n_delegados, 'Tarifa': precios_nomina['Delegado de Sitio']},
        {'Cargo': 'Coordinador de Sitio', 'Cantidad': n_coord_sitio, 'Tarifa': precios_nomina['Coordinador de Sitio']},
        {'Cargo': 'Coordinador de Aulas', 'Cantidad': n_coord_aula, 'Tarifa': precios_nomina['Coordinador de Aulas']},
        {'Cargo': 'Jefe de Salón', 'Cantidad': n_jefes_salon, 'Tarifa': precios_nomina['Jefe de Salón']},
        {'Cargo': 'Dactiloscopista', 'Cantidad': n_dactilo, 'Tarifa': precios_nomina['Dactiloscopista']},
        {'Cargo': 'Auxiliar de Aseo', 'Cantidad': n_aseo, 'Tarifa': precios_nomina['Auxiliar de Aseo']},
        {'Cargo': 'Seguridad', 'Cantidad': n_seguridad, 'Tarifa': precios_nomina['Seguridad']}
    ]
    
    total_nomina = 0
    for item in detalle_nomina:
        item['Subtotal'] = item['Cantidad'] * item['Tarifa']
        total_nomina += item['Subtotal']

    # 3. Impresión y Kits
    if n_aspirantes <= 1000:
        precio_imp = 5705
    elif n_aspirantes <= 1500:
        precio_imp = 4909
    else:
        precio_imp = 4744
    
    costo_impresion = n_aspirantes * precio_imp
    costo_kits = (n_salones * 18183) + (n_dactilo * 40669) + (n_aseo * 95000)
    
    otros_base = costo_impresion + costo_kits + total_nomina
    otros_min = otros_base
    otros_max = otros_base * 1.05

    # Consolidación de escenarios
    total_base = costo_transporte_base + otros_base
    total_min = transporte_min + otros_min
    total_max = transporte_max + otros_max
    
    return {
        'logistica': {'Sitios': n_sitios, 'Salones': n_salones},
        'detalle_nomina': detalle_nomina,
        'financiero': {
            'Transporte': costo_transporte_base,
            'Nómina': total_nomina,
            'Impresión': costo_impresion,
            'Insumos': costo_kits,
            'TOTAL_BASE': total_base
        },
        'intervalo': {
            'min': total_min,
            'max': total_max,
            'gap': total_max - total_min
        },
        'unitario': total_base / n_aspirantes,
        'unitario_max': total_max / n_aspirantes,
        'precio_impresion_aplicado': precio_imp
    }

# ==============================================================================
# INTERFAZ DE USUARIO (SIDEBAR)
# ==============================================================================
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 1rem; margin-bottom: 1.5rem;">
        <h2 style="color: #FF8C00; margin: 0; font-size: 1.5rem; border: none;"> ESAP</h2>
        <p style="color: #ffffff; font-size: 0.85rem; margin: 0.5rem 0 0 0;">
            Sistema de Costeo de Concursos
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("Navegación")
opcion = st.sidebar.radio(
    "Seleccione una vista:",
    ["1. Contexto y EDA", "2. Evaluación Modelos ML", "3. Calculadora de Costos", "4. Cotización Multi-Ciudad"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Estado del Proyecto:**
    ✅ Análisis Exploratorio
    ✅ Evaluación de Modelos ML
    ✅ Implementación Paramétrica
    """
)

# ==============================================================================
# VISTA 1: CONTEXTO Y EDA
# ==============================================================================
if opcion == "1. Contexto y EDA":
    # Header principal con estilo ESAP
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #003366 0%, #004080 100%); 
                    padding: 2rem; 
                    border-radius: 12px; 
                    margin-bottom: 2rem;
                    box-shadow: 0 4px 12px rgba(0,51,102,0.2);
                    border-left: 6px solid #FF8C00;">
            <h1 style="color: #ffffff; 
                       margin: 0; 
                       font-size: 2rem; 
                       font-weight: 700;
                       text-align: center;
                       text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                       border: none;">
                🔍 Análisis Exploratorio y Diagnóstico
            </h1>
            <p style="color: #FFA500; 
                      text-align: center; 
                      margin: 0.5rem 0 0 0; 
                      font-size: 1rem;">
                Escuela Superior de Administración Pública
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("""
    Este módulo explica **por qué fallaron los modelos tradicionales** (Regresión Lineal, XGBoost) y justifica el cambio hacia un modelo paramétrico.
    
    El hallazgo clave fue identificar que los costos no son lineales, sino que funcionan por **Tarifas Escalonadas (Step Functions)**.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("El Comportamiento Real (Escalonado)")
        # Simulación de datos para el gráfico
        x_sim = np.arange(1, 2500)
        y_sim = [5705 if x <= 1000 else (4909 if x <= 1500 else 4744) for x in x_sim]
        
        df_sim = pd.DataFrame({'Aspirantes': x_sim, 'Costo Unitario': y_sim})
        
        fig = px.line(df_sim, x='Aspirantes', y='Costo Unitario', 
                      title="Estructura de Tarifas (Cuadernillos)",
                      color_discrete_sequence=[ESAP_PALETTE['primary']])
        fig.update_layout(
            yaxis_title="Precio Unitario ($)",
            font=dict(family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"),
            plot_bgcolor='#ffffff',
            paper_bgcolor=ESAP_PALETTE['neutral_light']
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Nota cómo el precio cae abruptamente en 1000 y 1500. Esto confunde a las regresiones lineales.")

    with col2:
        st.subheader("Distribución Geográfica")
        st.markdown("Los costos logísticos varían drásticamente según la ciudad. Un modelo que solo vea 'Aspirantes' ignorará la complejidad del terreno.")
        ciudades_ejemplo = pd.DataFrame({
            'Ciudad': ['Bogotá', 'Medellín', 'San Andrés', 'Quibdó'],
            'Costo Logístico Base': [45000, 85000, 250000, 180000]
        })
        fig2 = px.bar(ciudades_ejemplo, x='Ciudad', y='Costo Logístico Base', 
                      color='Costo Logístico Base',
                      title="Variabilidad de Costos Logísticos",
                      color_continuous_scale=[[0, ESAP_PALETTE['primary']], 
                                             [0.5, ESAP_PALETTE['secondary']], 
                                             [1, ESAP_PALETTE['accent']]])
        fig2.update_layout(
            font=dict(family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"),
            plot_bgcolor='#ffffff',
            paper_bgcolor=ESAP_PALETTE['neutral_light']
        )
        st.plotly_chart(fig2, use_container_width=True)

# ==============================================================================
# VISTA 2: EVALUACIÓN DE MODELOS ML (MEJORADA CON GRÁFICAS)
# ==============================================================================
elif opcion == "2. Evaluación Modelos ML":
    # Header principal con estilo ESAP
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #003366 0%, #004080 100%); 
                    padding: 2rem; 
                    border-radius: 12px; 
                    margin-bottom: 2rem;
                    box-shadow: 0 4px 12px rgba(0,51,102,0.2);
                    border-left: 6px solid #FF8C00;">
            <h1 style="color: #ffffff; 
                       margin: 0; 
                       font-size: 2rem; 
                       font-weight: 700;
                       text-align: center;
                       text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                       border: none;">
                🧪 Evaluación Visual de la Dificultad
            </h1>
            <p style="color: #FFA500; 
                      text-align: center; 
                      margin: 0.5rem 0 0 0; 
                      font-size: 1rem;">
                Escuela Superior de Administración Pública
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("""
    Aquí visualizamos **por qué** el Machine Learning tradicional no es la herramienta adecuada para este problema específico.
    """)

    # --- GRÁFICA 1: EL ABISMO DEL OVERFITTING ---
    st.subheader("1. El 'Espejismo' del Entrenamiento")
    st.markdown("Mira la diferencia entre lo que el modelo 'cree' que sabe (Azul) y cómo le va en la realidad (Rojo).")

    # Datos preparados
    data_perf = pd.DataFrame({
        'Modelo': ['Gradient Boosting', 'XGBoost (Default)', 'Random Forest', 'Regresión Lineal'],
        'R2_Train': [0.99, 0.99, 0.80, 0.40],   # Entrenamiento (Casi perfecto en árboles)
        'R2_Test':  [-1.01, -0.94, -0.01, -1.50] # Realidad (Desastroso, peor que el promedio)
    })

    # Transformar para gráfica de barras agrupadas
    df_melt = data_perf.melt(id_vars=['Modelo'], var_name='Fase', value_name='Score R2')
    
    fig_overfit = px.bar(df_melt, x='Modelo', y='Score R2', color='Fase', barmode='group',
                         color_discrete_map={'R2_Train': ESAP_PALETTE['accent'], 
                                           'R2_Test': ESAP_PALETTE['primary']},
                         title="Comparativa: Ilusión (Train) vs. Realidad (Test)")
    
    fig_overfit.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Límite de Utilidad")
    fig_overfit.update_layout(
        font=dict(family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"),
        plot_bgcolor='#ffffff',
        paper_bgcolor=ESAP_PALETTE['neutral_light']
    )
    st.plotly_chart(fig_overfit, use_container_width=True)
    
    st.error("""
    **Interpretación:** Las barras verdes (Entrenamiento) muestran modelos que "memorizaron" los datos. 
    Las barras rojas (Test) cayendo por debajo de 0 indican que los modelos fallaron estructuralmente al ver datos nuevos.
    """)

    st.markdown("---")

    # --- GRÁFICA 2: POR QUÉ FALLA LA REGRESIÓN (SIMULACIÓN) ---
    st.subheader("2. Anatomía del Error: Lineal vs. Escalonado")
    st.markdown("Esta gráfica simula por qué una línea recta (Regresión) no puede capturar el tarifario.")

    # Generar datos simulados de la curva real vs predicción lineal
    x_demo = np.linspace(0, 2000, 100)
    y_real = [5705 * x if x <= 1000 else (5705 * 1000 + 4909 * (x - 1000)) for x in x_demo]
    y_lineal = [5100 * x for x in x_demo] 

    df_demo = pd.DataFrame({
        'Aspirantes': x_demo,
        'Costo Real (Escalonado)': y_real,
        'Predicción Lineal (Errónea)': y_lineal
    })
    
    fig_error = px.line(df_demo, x='Aspirantes', y=['Costo Real (Escalonado)', 'Predicción Lineal (Errónea)'],
                        title="Simulación: Realidad vs. Modelo Lineal",
                        color_discrete_map={'Costo Real (Escalonado)': ESAP_PALETTE['primary'], 
                                          'Predicción Lineal (Errónea)': ESAP_PALETTE['accent']})
    fig_error.update_layout(
        font=dict(family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"),
        plot_bgcolor='#ffffff',
        paper_bgcolor=ESAP_PALETTE['neutral_light']
    )
    st.plotly_chart(fig_error, use_container_width=True)
    
    st.info("""
    **El problema visual:** La línea roja (Predicción) ignora los cambios de tarifa. 
    * En 800 aspirantes, subestima el costo.
    * En 1200 aspirantes, lo sobreestima.
    **Solución:** Usar el modelo paramétrico (Calculadora) que sigue la línea azul exactamente.
    """)

# ==============================================================================
# VISTA 3: CALCULADORA DE COSTOS (ACTUALIZADA CON DESGLOSE DE PERSONAL)
# ==============================================================================
elif opcion == "3. Calculadora de Costos":
    # Header principal con estilo ESAP
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #003366 0%, #004080 100%); 
                    padding: 2rem; 
                    border-radius: 12px; 
                    margin-bottom: 2rem;
                    box-shadow: 0 4px 12px rgba(0,51,102,0.2);
                    border-left: 6px solid #FF8C00;">
            <h1 style="color: #ffffff; 
                       margin: 0; 
                       font-size: 2rem; 
                       font-weight: 700;
                       text-align: center;
                       text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                       border: none;">
                🧮 Calculadora Paramétrica de Costos
            </h1>
            <p style="color: #FFA500; 
                      text-align: center; 
                      margin: 0.5rem 0 0 0; 
                      font-size: 1rem;">
                Escuela Superior de Administración Pública
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("Herramienta de precisión basada en **Reglas de Negocio** y **Tarifario Maestro**.")
    
    # --- FORMULARIO DE INGRESO ---
    with st.form("input_form"):
        st.subheader("Parámetros del Concurso")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            aspirantes = st.number_input("Número de Aspirantes", min_value=1, value=500, step=10)
        with col2:
            ciudades = ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'San Andrés', 'Quibdó', 
                        'Ibagué', 'Tunja', 'Villavicencio', 'Pereira', 'Manizales', 'Cartagena', 
                        'Santa Marta', 'Riohacha', 'Arauca', 'Cúcuta', 'Pasto', 'Popayán']
            ciudad = st.selectbox("Ciudad de Aplicación", sorted(ciudades))
        with col3:
            prueba = st.radio("Modalidad", ["Escrita", "Virtual"])
            
        submitted = st.form_submit_button("Calcular Cotización 🚀", type="primary")
    
    if submitted:
        # Ejecutar lógica
        res = calcular_modelo_parametrico(aspirantes, ciudad, prueba)
        st.divider()
        
        st.subheader("🎯 Resultado de la Cotización")
        
        # --- VISUALIZACIÓN DEL INTERVALO (NUEVO) ---
        col_rango_1, col_rango_2, col_rango_3 = st.columns([1, 2, 1])
        
        with col_rango_1:
            st.metric(
                label="Escenario Optimista (Mínimo)",
                value=f"${res['intervalo']['min']:,.0f}",
                help="Asume transporte sin contratiempos y cero desperdicio."
            )
            
        with col_rango_2:
            # Valor Central Grande
            st.markdown(f"""
            <div style="text-align: center;">
                <span style="font-size: 1.2em; color: gray;">Estimación Central</span><br>
                <span style="font-size: 2.5em; font-weight: bold; color: #2E86C1;">${res['financiero']['TOTAL_BASE']:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Barra de progreso visual del rango
            rango_pct = 100 * (res['financiero']['TOTAL_BASE'] - res['intervalo']['min']) / res['intervalo']['gap']
            st.progress(int(rango_pct))
            st.caption(f"Rango de Riesgo: +/- ${res['intervalo']['gap']/2:,.0f} (Debido a volatilidad logística)")

        with col_rango_3:
            st.metric(
                label="Escenario Conservador (Máximo)",
                value=f"${res['intervalo']['max']:,.0f}",
                delta=f"Reserve hasta: ${res['unitario_max']:,.0f}/asp",
                delta_color="inverse",
                help="Incluye +20% en transporte y +5% en imprevistos generales."
            )

        st.divider()
        
        # --- KPIS LOGÍSTICOS ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sitios", res['logistica']['Sitios'])
        c2.metric("Salones", res['logistica']['Salones'])
        total_personas = sum([item['Cantidad'] for item in res['detalle_nomina']])
        c3.metric("Total Staff", total_personas)
        c4.metric("Tarifa Impresión", f"${res['precio_impresion_aplicado']:,.0f}/u")
        
        # --- PESTAÑAS PARA EL DETALLE ---
        tab1, tab2 = st.tabs(["👥 Nómina Detallada", "📊 Análisis de Costos"])
        
        with tab1:
            df_personal = pd.DataFrame(res['detalle_nomina'])
            st.dataframe(
                df_personal.style.format({'Tarifa': '${:,.0f}', 'Subtotal': '${:,.0f}'}),
                use_container_width=True, hide_index=True
            )
            
        with tab2:
            # Gráfico de Torta
            df_pie = pd.DataFrame({
                'Rubro': ['Transporte (Base)', 'Nómina', 'Impresión', 'Insumos'],
                'Costo': [res['financiero']['Transporte'], res['financiero']['Nómina'], 
                          res['financiero']['Impresión'], res['financiero']['Insumos']]
            })
            fig_pie = px.pie(df_pie, values='Costo', names='Rubro', hole=0.4, 
                           title="Distribución del Presupuesto Base",
                           color_discrete_sequence=[ESAP_PALETTE['primary'], 
                                                   ESAP_PALETTE['secondary'],
                                                   ESAP_PALETTE['accent'], 
                                                   ESAP_PALETTE['orange']])
            fig_pie.update_layout(
                font=dict(family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"),
                paper_bgcolor=ESAP_PALETTE['neutral_light']
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Alerta sobre transporte
            if res['financiero']['Transporte'] > res['financiero']['TOTAL_BASE'] * 0.3:
                st.warning(f"⚠️ **Atención:** El transporte representa una parte muy alta del presupuesto. La variabilidad en el precio de la gasolina o fletes en {ciudad} podría afectar significativamente el margen.")

# ==============================================================================
# VISTA 4: COTIZACIÓN MULTI-CIUDAD
# ==============================================================================
elif opcion == "4. Cotización Multi-Ciudad":
    # Header principal con estilo ESAP
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #003366 0%, #004080 100%); 
                    padding: 2rem; 
                    border-radius: 12px; 
                    margin-bottom: 2rem;
                    box-shadow: 0 4px 12px rgba(0,51,102,0.2);
                    border-left: 6px solid #FF8C00;">
            <h1 style="color: #ffffff; 
                       margin: 0; 
                       font-size: 2rem; 
                       font-weight: 700;
                       text-align: center;
                       text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                       border: none;">
                🌎 Cotizador Nacional Multi-Ciudad
            </h1>
            <p style="color: #FFA500; 
                      text-align: center; 
                      margin: 0.5rem 0 0 0; 
                      font-size: 1rem;">
                Escuela Superior de Administración Pública
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("Configure un operativo nacional seleccionando múltiples ciudades y asignando aspirantes a cada una.")
    
    # 1. Selección de Ciudades
    ciudades_disponibles = sorted(['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'San Andrés', 'Quibdó', 
                'Ibagué', 'Tunja', 'Villavicencio', 'Pereira', 'Manizales', 'Cartagena', 
                'Santa Marta', 'Riohacha', 'Arauca', 'Cúcuta', 'Pasto', 'Popayán'])
    
    ciudades_sel = st.multiselect("Seleccione las Ciudades del Operativo:", ciudades_disponibles, default=["Bogotá", "Medellín"])
    
    if ciudades_sel:
        # 2. Configuración de Aspirantes (Data Editor)
        st.subheader("📋 Asignación de Aspirantes por Ciudad")
        
        # Crear DF inicial
        df_input = pd.DataFrame({
            'Ciudad': ciudades_sel,
            'Aspirantes': [500] * len(ciudades_sel), # Valor por defecto
            'Modalidad': ["Escrita"] * len(ciudades_sel)
        })
        
        # Editor
        edited_df = st.data_editor(
            df_input,
            column_config={
                "Aspirantes": st.column_config.NumberColumn(
                    "N° Aspirantes",
                    min_value=1,
                    max_value=100000,
                    step=10,
                ),
                "Modalidad": st.column_config.SelectboxColumn(
                    "Modalidad",
                    options=["Escrita", "Virtual"],
                    required=True,
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("Calcular Cotización Global 🚀", type="primary"):
            
            resultados_lista = []
            total_global = 0
            total_min_global = 0
            total_max_global = 0
            total_aspirantes = 0
            
            # Barra de progreso
            progress_text = "Calculando costos por ciudad..."
            my_bar = st.progress(0, text=progress_text)
            
            for idx, row in enumerate(edited_df.itertuples()):
                ciudad_iter = row.Ciudad
                asp_iter = row.Aspirantes
                mod_iter = row.Modalidad
                
                # Calcular usando la función existente
                res = calcular_modelo_parametrico(asp_iter, ciudad_iter, mod_iter)
                
                # Acumular
                costo_base = res['financiero']['TOTAL_BASE']
                total_global += costo_base
                total_min_global += res['intervalo']['min']
                total_max_global += res['intervalo']['max']
                total_aspirantes += asp_iter
                
                resultados_lista.append({
                    'Ciudad': ciudad_iter,
                    'Aspirantes': asp_iter,
                    'Modalidad': mod_iter,
                    'Costo Total': costo_base,
                    'Costo Unitario': res['unitario'],
                    'Sitios': res['logistica']['Sitios'],
                    'Salones': res['logistica']['Salones'],
                    'Staff': sum(x['Cantidad'] for x in res['detalle_nomina'])
                })
                
                # Actualizar barra
                my_bar.progress((idx + 1) / len(edited_df), text=progress_text)
                
            my_bar.empty()
            
            st.divider()
            
            # --- RESULTADOS GLOBALES ---
            st.subheader("💰 Resumen Financiero Nacional")
            
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.metric("Costo Total Operativo", f"${total_global:,.0f}")
            with c2:
                st.metric("Total Aspirantes", f"{total_aspirantes:,.0f}")
            with c3:
                if total_aspirantes > 0:
                    promedio_unitario = total_global / total_aspirantes
                    st.metric("Costo Promedio / Aspirante", f"${promedio_unitario:,.0f}")
            
            # --- INTERVALO DE CONFIANZA ---
            st.info(f"**Rango de Presupuesto Sugerido:** Entre **${total_min_global:,.0f}** (Optimista) y **${total_max_global:,.0f}** (Conservador)")
            
            # --- DETALLE POR CIUDAD ---
            st.subheader("📍 Desglose por Ciudad")
            df_res = pd.DataFrame(resultados_lista)
            
            # Formato condicional para resaltar costos altos
            st.dataframe(
                df_res.style.format({
                    'Costo Total': '${:,.0f}',
                    'Costo Unitario': '${:,.0f}',
                    'Aspirantes': '{:,.0f}'
                }).background_gradient(subset=['Costo Total'], cmap='Blues'),
                use_container_width=True,
                hide_index=True
            )
            
            # --- DESCARGA ---
            # Convertir a CSV para descargar
            csv = df_res.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Detalle (CSV)",
                data=csv,
                file_name='cotizacion_nacional_esap.csv',
                mime='text/csv',
            )

            st.divider()

            # --- PESTAÑAS PARA EL DETALLE GLOBAL ---
            tab_glob_1, tab_glob_2 = st.tabs(["👥 Nómina Detallada Global", "📊 Análisis de Costos Global"])

            with tab_glob_1:
                # Agrupar nómina global
                nomina_global = {}
                for item in resultados_lista:
                    # Reconstruir detalle de nómina desde los resultados si es necesario, 
                    # pero como no guardamos el detalle crudo en resultados_lista, 
                    # lo mejor es recalcular o acumular en el loop principal.
                    # ESTRATEGIA: Acumular en el loop principal hubiera sido mejor, 
                    # pero para no romper el flujo, recalculamos rápido o extraemos.
                    # Dado que 'Staff' es un entero, necesitamos el desglose.
                    
                    # RE-CALCULO para obtener detalle preciso (rápido)
                    res_temp = calcular_modelo_parametrico(item['Aspirantes'], item['Ciudad'], item['Modalidad'])
                    for cargo in res_temp['detalle_nomina']:
                        nombre_cargo = cargo['Cargo']
                        if nombre_cargo not in nomina_global:
                            nomina_global[nombre_cargo] = {'Cantidad': 0, 'Subtotal': 0, 'Tarifa': cargo['Tarifa']}
                        
                        nomina_global[nombre_cargo]['Cantidad'] += cargo['Cantidad']
                        nomina_global[nombre_cargo]['Subtotal'] += cargo['Subtotal']
                
                # Convertir a DF
                df_nomina_global = pd.DataFrame([
                    {'Cargo': k, 'Cantidad': v['Cantidad'], 'Tarifa': v['Tarifa'], 'Subtotal': v['Subtotal']}
                    for k, v in nomina_global.items()
                ])
                
                st.dataframe(
                    df_nomina_global.style.format({'Tarifa': '${:,.0f}', 'Subtotal': '${:,.0f}'}),
                    use_container_width=True, hide_index=True
                )

            with tab_glob_2:
                # Agrupar costos globales
                costos_globales = {'Transporte': 0, 'Nómina': 0, 'Impresión': 0, 'Insumos': 0}
                
                for item in resultados_lista:
                    # Mismo approach de re-calculo para precisión de componentes
                    res_temp = calcular_modelo_parametrico(item['Aspirantes'], item['Ciudad'], item['Modalidad'])
                    costos_globales['Transporte'] += res_temp['financiero']['Transporte']
                    costos_globales['Nómina'] += res_temp['financiero']['Nómina']
                    costos_globales['Impresión'] += res_temp['financiero']['Impresión']
                    costos_globales['Insumos'] += res_temp['financiero']['Insumos']
                
                # Gráfico de Torta
                df_pie_global = pd.DataFrame({
                    'Rubro': ['Transporte (Base)', 'Nómina', 'Impresión', 'Insumos'],
                    'Costo': [costos_globales['Transporte'], costos_globales['Nómina'], 
                              costos_globales['Impresión'], costos_globales['Insumos']]
                })
                
                fig_pie_global = px.pie(df_pie_global, values='Costo', names='Rubro', hole=0.4, 
                               title="Distribución del Presupuesto Nacional",
                               color_discrete_sequence=[ESAP_PALETTE['primary'], 
                                                       ESAP_PALETTE['secondary'],
                                                       ESAP_PALETTE['accent'], 
                                                       ESAP_PALETTE['orange']])
                fig_pie_global.update_layout(
                    font=dict(family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"),
                    paper_bgcolor=ESAP_PALETTE['neutral_light']
                )
                st.plotly_chart(fig_pie_global, use_container_width=True)
                
                # Alerta Global
                if costos_globales['Transporte'] > total_global * 0.3:
                    st.warning(f"⚠️ **Atención:** A nivel nacional, el transporte representa el {costos_globales['Transporte']/total_global:.1%} del presupuesto. Considere optimizar las ciudades con logística compleja.")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Creado con ❤️ por el equipo de analítica de la ESAP")
