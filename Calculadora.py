import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Estimación de Costos - ESAP",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# PALETA DE COLORES ESAP
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

# Aplicar estilos CSS personalizados
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
        
        h1 {{
            color: #000000 !important;
            font-weight: 700;
            border-bottom: 3px solid var(--esap-accent);
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }}
        
        h2, h3 {{
            color: #000000 !important;
            font-weight: 600;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255,255,255,0.8);
            border-radius: 8px 8px 0 0;
            color: var(--esap-primary);
            font-weight: 600;
            padding: 1rem 2rem;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, var(--esap-primary), var(--esap-secondary));
            color: white !important;
            border-bottom: 3px solid var(--esap-accent);
        }}
        
        .stDataFrame {{
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,51,102,0.08);
            border: 1px solid rgba(0,51,102,0.1);
        }}
        
        div[data-testid="stNotification"] {{
            border-left: 4px solid var(--esap-accent);
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# LÓGICA DEL MODELO PARAMÉTRICO (Backend)
# ==============================================================================
def calcular_costo_parametrico(n_aspirantes, ciudad, tipo_prueba):
    """
    Motor de cálculo basado en reglas de negocio y tarifarios definidos.
    """
    # 1. REGLAS DE NEGOCIO (Logística)
    # ---------------------------------------------------------
    n_sitios = math.ceil(n_aspirantes / 500)
    
    factor_salon = 25 # Personas por salón
    n_salones = math.ceil(n_aspirantes / factor_salon)
    
    # Personal
    n_delegados_sitio = n_sitios
    n_jefes_salon = n_salones * (2 if tipo_prueba == "Virtual" else 1)
    n_dactiloscopistas = math.ceil(n_salones / 4)
    n_coord_aulas = math.ceil(n_salones / 6)
    n_aseo = math.ceil(n_salones / 6)
    n_seguridad = n_sitios * 2
    
    total_staff = n_delegados_sitio + n_jefes_salon + n_dactiloscopistas + n_coord_aulas + n_aseo + n_seguridad

    # Materiales (Kits)
    n_kits_salon = n_salones
    n_kits_dactilo = n_dactiloscopistas
    n_kits_aseo = n_aseo

    # 2. TARIFARIO (Financiero) - Precios base aproximados
    # ---------------------------------------------------------
    precios = {
        'Delegado': 300000, 'Jefe Salón': 200000, 'Dactiloscopista': 214298,
        'Coord. Aulas': 250000, 'Aseo': 207420, 'Seguridad': 207420,
        'Kit Salón': 18183, 'Kit Dactilo': 40669, 'Kit Aseo': 95000
    }
    
    # Lógica de rangos para impresión (Economía de escala)
    if n_aspirantes <= 1000:
        precio_impresion = 5705
    elif n_aspirantes <= 1500:
        precio_impresion = 4909
    else:
        precio_impresion = 4500
    
    # Lógica de transporte (Geográfica simplificada)
    factor_ciudad = 1.0 if ciudad == "Bogotá" else 1.8
    costo_transporte_base = 50000 * n_sitios * factor_ciudad

    # 3. CÁLCULO DE COSTOS
    # ---------------------------------------------------------
    costo_impresion = n_aspirantes * precio_impresion
    
    costo_staff = (n_delegados_sitio * precios['Delegado']) + \
                  (n_jefes_salon * precios['Jefe Salón']) + \
                  (n_dactiloscopistas * precios['Dactiloscopista']) + \
                  (n_coord_aulas * precios['Coord. Aulas']) + \
                  (n_aseo * precios['Aseo']) + \
                  (n_seguridad * precios['Seguridad'])
                  
    costo_insumos = (n_kits_salon * precios['Kit Salón']) + \
                    (n_kits_dactilo * precios['Kit Dactilo']) + \
                    (n_kits_aseo * precios['Kit Aseo'])
    
    total = costo_impresion + costo_staff + costo_insumos + costo_transporte_base
    
    return {
        "logistica": {
            "Sitios": n_sitios, "Salones": n_salones, "Staff Total": total_staff,
            "Jefes de Salón": n_jefes_salon, "Dactiloscopistas": n_dactiloscopistas
        },
        "financiero": {
            "Impresión": costo_impresion, "Personal": costo_staff,
            "Insumos": costo_insumos, "Logística": costo_transporte_base,
            "Total": total
        }
    }

# ==============================================================================
# INTERFAZ DE USUARIO (Frontend)
# ==============================================================================

# Header institucional ESAP
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
                   font-size: 2.5rem; 
                   font-weight: 700;
                   text-align: center;
                   text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                   border: none;">
            📊 Sistema de Estimación de Costos - Concursos ESAP
        </h1>
        <p style="color: #FFA500; 
                  text-align: center; 
                  margin: 0.5rem 0 0 0; 
                  font-size: 1.1rem;
                  font-weight: 500;">
            Escuela Superior de Administración Pública
        </p>
        <p style="color: #ffffff; 
                  text-align: center; 
                  margin: 0.5rem 0 0 0; 
                  font-size: 0.95rem;">
            Herramienta integrada de análisis histórico y modelo paramétrico para cotización de concursos
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Crear Pestañas para organizar la historia
tab1, tab2, tab3 = st.tabs(["1. Análisis Exploratorio (EDA)", "2. Evaluación Modelos AI", "3. Calculadora Final"])

# ------------------------------------------------------------------------------
# TAB 1: ANÁLISIS EXPLORATORIO (SIMULADO)
# ------------------------------------------------------------------------------
with tab1:
    st.header("Comportamiento Histórico de Costos")
    st.markdown("Simulación de la estructura de datos basada en el análisis de *Recopilado_Perso.xlsx*.")
    
    # Generar datos simulados para visualizar el "Escalón"
    df_sim = pd.DataFrame({'Aspirantes': range(100, 5000, 50)})
    # Aplicamos una lógica simplificada para generar el costo y graficarlo
    df_sim['Costo_Total'] = df_sim['Aspirantes'].apply(lambda x: calcular_costo_parametrico(x, "Bogotá", "Escrita")['financiero']['Total'])
    # Añadimos un poco de ruido aleatorio para simular datos reales imperfectos
    df_sim['Costo_Real_Simulado'] = df_sim['Costo_Total'] * np.random.uniform(0.95, 1.05, len(df_sim))

    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_scatter = px.scatter(df_sim, x='Aspirantes', y='Costo_Real_Simulado', 
                                 title="Correlación Aspirantes vs. Costo Total",
                                 labels={'Costo_Real_Simulado': 'Costo Total (COP)'},
                                 trendline="ols",
                                 color_discrete_sequence=[ESAP_PALETTE['primary']])
        fig_scatter.update_layout(
            font=dict(family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", color=ESAP_PALETTE['neutral_dark']),
            title=dict(font=dict(color=ESAP_PALETTE['primary'], size=18)),
            plot_bgcolor='#ffffff',
            paper_bgcolor=ESAP_PALETTE['neutral_light']
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col2:
        st.info("""
        **Hallazgos del EDA:**
        1. **Linealidad por Tramos:** Existe una relación directa fuerte, pero los precios unitarios cambian por volumen.
        2. **Efecto Escalonado:** Los saltos en el costo ocurren cuando se abre un nuevo sitio (cada 500 pax) o se cambia de rango de impresión.
        3. **Outliers:** Los puntos dispersos representan costos logísticos variables (zonas apartadas).
        """)
        st.dataframe(df_sim.head(10), hide_index=True)

# ------------------------------------------------------------------------------
# TAB 2: EVALUACIÓN DE MODELOS (LA HISTORIA DEL FALLO)
# ------------------------------------------------------------------------------
with tab2:
    st.header("Diagnóstico de Modelos Predictivos (Machine Learning)")
    st.markdown("""
    Se intentó predecir el costo total usando algoritmos tradicionales. 
    **Resultado:** Los modelos fallaron debido a la naturaleza escalonada de las tarifas y la falta de datos en rangos altos.
    """)
    
    # Datos hardcodeados de tu tabla de resultados anterior
    data_fallos = {
        'Modelo': ['Gradient Boosting', 'XGBoost (Default)', 'XGBoost (Optimizado)', 'Regresión Lineal'],
        'R² Test': [0.5848, 0.5670, 0.4119, -0.0765],
        'R² CV (Validación)': [-1.0156, -0.9409, -1.5192, -1.5028],
        'Estado': ['Sobreajustado 🚩', 'Inestable 🚩', 'Inestable 🚩', 'No Converge ❌']
    }
    df_fallos = pd.DataFrame(data_fallos)
    
    st.table(df_fallos)
    
    st.error("""
    **Conclusión Técnica:**
    Los valores negativos en **R² CV** indican que el modelo es peor que usar un promedio simple.
    Esto validó el cambio de estrategia hacia un **Modelo Paramétrico (Calculadora)** basado en reglas de negocio.
    """)

# ------------------------------------------------------------------------------
# TAB 3: CALCULADORA FINAL (INTERACTIVA)
# ------------------------------------------------------------------------------
with tab3:
    st.header("🛠️ Calculadora Paramétrica de Costos")
    st.markdown("Ingrese las variables operativas para obtener una cotización exacta basada en el tarifario maestro.")
    
    # --- INPUTS ---
    with st.container():
        col_in1, col_in2, col_in3, col_in4 = st.columns(4)
        
        with col_in1:
            aspirantes_in = st.number_input("Número de Aspirantes", min_value=1, value=500, step=50)
        
        with col_in2:
            ciudad_in = st.selectbox("Ciudad de Aplicación", 
                                     ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga", "Quibdó", "San Andrés"])
        
        with col_in3:
            tipo_in = st.radio("Modalidad", ["Escrita", "Virtual"], horizontal=True)
            
        with col_in4:
            st.write("") # Espacio
            st.write("") # Espacio
            btn_calc = st.button("Calcular Cotización", type="primary", use_container_width=True)

    # --- RESULTADOS ---
    if btn_calc:
        resultado = calcular_costo_parametrico(aspirantes_in, ciudad_in, tipo_in)
        log = resultado['logistica']
        fin = resultado['financiero']
        
        st.divider()
        
        # 1. KPIs Principales
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Costo Total Estimado", f"${fin['Total']:,.0f}")
        kpi2.metric("Costo Unitario / Aspirante", f"${fin['Total']/aspirantes_in:,.0f}")
        kpi3.metric("Total Sitios", log['Sitios'])
        kpi4.metric("Total Staff Humano", log['Staff Total'])
        
        st.divider()
        
        # 2. Desglose Gráfico y Tabla
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Distribución del Presupuesto")
            df_fin = pd.DataFrame([
                {'Rubro': 'Impresión', 'Valor': fin['Impresión']},
                {'Rubro': 'Personal', 'Valor': fin['Personal']},
                {'Rubro': 'Insumos (Kits)', 'Valor': fin['Insumos']},
                {'Rubro': 'Logística', 'Valor': fin['Logística']}
            ])
            fig_pie = px.pie(df_fin, values='Valor', names='Rubro', hole=0.4,
                           color_discrete_sequence=[ESAP_PALETTE['primary'], 
                                                   ESAP_PALETTE['secondary'],
                                                   ESAP_PALETTE['accent'], 
                                                   ESAP_PALETTE['orange']])
            fig_pie.update_layout(
                font=dict(family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"),
                title=dict(font=dict(color=ESAP_PALETTE['primary'])),
                paper_bgcolor=ESAP_PALETTE['neutral_light']
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_g2:
            st.subheader("Detalle Operativo Generado")
            st.markdown(f"""
            Para atender a **{aspirantes_in}** aspirantes en **{ciudad_in}**, el sistema ha calculado los siguientes recursos físicos:
            """)
            
            detalles_op = {
                "Recurso": ["Salones", "Jefes de Salón", "Dactiloscopistas", "Kits de Aseo", "Personal Seguridad"],
                "Cantidad": [log['Salones'], log['Jefes de Salón'], log['Dactiloscopistas'], math.ceil(log['Salones']/6), log['Sitios']*2]
            }
            st.dataframe(pd.DataFrame(detalles_op), use_container_width=True)
            
            st.info("💡 *Nota: Estos cálculos aplican las reglas de negocio (ej. 1 Dactiloscopista cada 4 salones) extraídas del análisis de datos.*")