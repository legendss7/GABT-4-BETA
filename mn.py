import streamlit as st
import pandas as pd
import numpy as np
import time

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="Batería de Aptitudes GATB Profesional")

# Colocamos un ancla invisible al inicio de la página para referencia
st.html('<a id="top-anchor"></a>')

# Mapeo de Aptitudes
APTITUDES_MAP = {
    "Razonamiento General": {"code": "G", "color": "#1f77b4"},
    "Razonamiento Verbal": {"code": "V", "color": "#ff7f0e"},
    "Razonamiento Numérico": {"code": "N", "color": "#2ca02c"},
    "Razonamiento Espacial": {"code": "S", "color": "#d62728"},
    "Velocidad Perceptiva": {"code": "P", "color": "#9467bd"},
    "Precisión Manual": {"code": "Q", "color": "#8c564b"},
    "Coordinación Manual": {"code": "K", "color": "#e377c2"},
    "Atención Concentrada": {"code": "A", "color": "#7f7f7f"},
    "Razonamiento Mecánico": {"code": "M", "color": "#bcbd22"},
    "Razonamiento Abstracto": {"code": "R", "color": "#17becf"},
    "Razonamiento Clerical": {"code": "C", "color": "#98df8a"},
    "Razonamiento Técnico": {"code": "T", "color": "#ff9896"},
}
AREAS = list(APTITUDES_MAP.keys())
N_PREGUNTAS_POR_AREA = 12

# Clasificación y Calificación Global
def clasificar_percentil(porcentaje):
    if porcentaje >= 90: return 96, "Superior (90-99)"
    elif porcentaje >= 80: return 88, "Alto (80-89)"
    elif porcentaje >= 60: return 70, "Promedio Alto (60-79)"
    elif porcentaje >= 40: return 50, "Promedio (40-59)"
    elif porcentaje >= 20: return 30, "Promedio Bajo (20-39)"
    elif porcentaje >= 10: return 15, "Bajo (10-19)"
    else: return 5, "Muy Bajo (0-9)"

def calificar_global(avg_percentil):
    if avg_percentil >= 85: 
        return "Potencial Ejecutivo 🌟", "El perfil indica un potencial excepcionalmente alto y equilibrado para roles directivos, estratégicos y de alta complejidad. Capacidad de aprendizaje superior y adaptación rápida a cualquier entorno.", "#008000"
    elif avg_percentil >= 65: 
        return "Nivel Profesional Avanzado 🏆", "El perfil es sólido, con fortalezas claras y un buen balance aptitudinal. Excelente para roles técnicos especializados, de gestión de proyectos y consultoría.", "#4682b4"
    elif avg_percentil >= 40: 
        return "Perfil Competitivo 💼", "El perfil se sitúa en el promedio superior, demostrando suficiencia en todas las áreas. Apto para la mayoría de roles operativos y de coordinación. Requiere enfoque en el desarrollo de fortalezas clave.", "#ff8c00"
    else: 
        return "Período de Desarrollo 🛠️", "El perfil requiere un período de enfoque intensivo en el desarrollo de aptitudes clave. Se recomienda comenzar con roles de soporte y entrenamiento continuo.", "#dc143c"

def generate_gatb_questions():
    """Genera 144 preguntas simuladas con contenido realista."""
    
    # Definimos preguntas más específicas por área
    preguntas_templates = {
        "Razonamiento General": [
            ("Si todos los A son B, y todos los B son C, entonces:", 
             {"a": "Todos los A son C", "b": "Algunos A son C", "c": "Ningún A es C", "d": "No se puede determinar"}, "a"),
            ("¿Qué número sigue en la serie: 2, 6, 12, 20, 30, ?", 
             {"a": "40", "b": "42", "c": "44", "d": "38"}, "b"),
        ],
        "Razonamiento Verbal": [
            ("Sinónimo de ELOCUENTE:", 
             {"a": "Callado", "b": "Expresivo", "c": "Confuso", "d": "Torpe"}, "b"),
            ("Antónimo de ADVERSO:", 
             {"a": "Favorable", "b": "Contrario", "c": "Hostil", "d": "Negativo"}, "a"),
        ],
        "Razonamiento Numérico": [
            ("Si 3x + 5 = 20, entonces x =", 
             {"a": "5", "b": "6", "c": "7", "d": "8"}, "a"),
            ("El 25% de 80 es:", 
             {"a": "15", "b": "20", "c": "25", "d": "30"}, "b"),
        ],
        "Razonamiento Espacial": [
            ("Si rotamos un cubo 90° hacia la derecha, ¿qué cara queda al frente?", 
             {"a": "La que estaba a la izquierda", "b": "La que estaba arriba", "c": "La que estaba atrás", "d": "La que estaba abajo"}, "a"),
            ("¿Cuántas caras tiene un prisma rectangular?", 
             {"a": "4", "b": "5", "c": "6", "d": "8"}, "c"),
        ],
        "Velocidad Perceptiva": [
            ("¿Son iguales? 4789236 vs 4789236", 
             {"a": "Sí", "b": "No", "c": "Casi", "d": "Parcialmente"}, "a"),
            ("¿Son iguales? ABCDEF vs ABCDFE", 
             {"a": "Sí", "b": "No", "c": "Casi", "d": "Parcialmente"}, "b"),
        ],
        "Precisión Manual": [
            ("En tareas de ensamblaje fino, lo más importante es:", 
             {"a": "Velocidad", "b": "Precisión", "c": "Fuerza", "d": "Tamaño"}, "b"),
            ("Para enhebrar una aguja se requiere principalmente:", 
             {"a": "Fuerza", "b": "Coordinación fina", "c": "Velocidad", "d": "Concentración visual"}, "b"),
        ],
        "Coordinación Manual": [
            ("La coordinación ojo-mano es más importante en:", 
             {"a": "Leer", "b": "Conducir", "c": "Escuchar", "d": "Pensar"}, "b"),
            ("¿Qué actividad requiere más coordinación manual?", 
             {"a": "Escribir a mano", "b": "Recordar", "c": "Oír música", "d": "Ver TV"}, "a"),
        ],
        "Atención Concentrada": [
            ("Encuentra el error: El gato esta en el tejado", 
             {"a": "gato", "b": "esta (falta tilde)", "c": "tejado", "d": "No hay error"}, "b"),
            ("¿Cuántas veces aparece la letra 'a' en: La casa grande?", 
             {"a": "2", "b": "3", "c": "4", "d": "5"}, "c"),
        ],
        "Razonamiento Mecánico": [
            ("Si una rueda grande gira una vez, ¿cuántas veces gira una rueda conectada que es la mitad de tamaño?", 
             {"a": "1 vez", "b": "2 veces", "c": "0.5 veces", "d": "4 veces"}, "b"),
            ("Una palanca es más eficiente cuando:", 
             {"a": "El fulcro está cerca de la carga", "b": "El fulcro está lejos de la carga", "c": "No tiene fulcro", "d": "Es muy corta"}, "a"),
        ],
        "Razonamiento Abstracto": [
            ("En la serie: ○ △ ○ △ ○ ?, ¿qué sigue?", 
             {"a": "○", "b": "△", "c": "□", "d": "◇"}, "b"),
            ("Si A=1, B=2, C=3, entonces ABC=", 
             {"a": "123", "b": "6", "c": "321", "d": "111"}, "a"),
        ],
        "Razonamiento Clerical": [
            ("¿En qué orden alfabético van estos apellidos: Pérez, Martínez, López?", 
             {"a": "López, Martínez, Pérez", "b": "Martínez, López, Pérez", "c": "Pérez, Martínez, López", "d": "López, Pérez, Martínez"}, "a"),
            ("Al archivar por fecha, ¿cuál va primero?", 
             {"a": "15/03/2024", "b": "10/03/2024", "c": "20/03/2024", "d": "05/04/2024"}, "b"),
        ],
        "Razonamiento Técnico": [
            ("En un diagrama de flujo, un rombo representa:", 
             {"a": "Inicio", "b": "Proceso", "c": "Decisión", "d": "Fin"}, "c"),
            ("Si un sistema no arranca, el primer paso es:", 
             {"a": "Reiniciar", "b": "Revisar conexiones", "c": "Llamar soporte", "d": "Comprar uno nuevo"}, "b"),
        ],
    }
    
    questions = []
    current_id = 1
    
    for area_name in AREAS:
        code = APTITUDES_MAP[area_name]["code"]
        templates = preguntas_templates.get(area_name, [])
        
        # Generar 12 preguntas para cada área
        for i in range(N_PREGUNTAS_POR_AREA):
            # Ciclar entre las plantillas disponibles
            template_idx = i % len(templates) if templates else 0
            
            if templates:
                pregunta_text, opciones, respuesta_correcta = templates[template_idx]
                pregunta_final = f"{pregunta_text} (Variante {i+1})"
            else:
                # Fallback si no hay plantillas
                pregunta_final = f"Pregunta {code}-{i+1}: Evalúa {area_name}"
                opciones = {"a": "Opción A", "b": "Opción B", "c": "Opción C", "d": "Opción D"}
                respuesta_correcta = "a"
            
            questions.append({
                "id": current_id, 
                "area": area_name,
                "code": code,
                "pregunta": pregunta_final,
                "opciones": opciones,
                "respuesta_correcta": respuesta_correcta
            })
            current_id += 1
    
    return pd.DataFrame(questions)

df_preguntas = generate_gatb_questions()
N_TOTAL_PREGUNTAS = len(df_preguntas)

# --- 2. FUNCIONES DE ESTADO Y NAVEGACIÓN ---

# Inicialización de Session State
if 'stage' not in st.session_state: 
    st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state: 
    st.session_state.respuestas = {}
if 'area_actual_index' not in st.session_state: 
    st.session_state.area_actual_index = 0
if 'is_navigating' not in st.session_state: 
    st.session_state.is_navigating = False 
if 'error_msg' not in st.session_state: 
    st.session_state.error_msg = ""
if 'resultados_df' not in st.session_state: 
    st.session_state.resultados_df = pd.DataFrame()

def forzar_scroll_al_top():
    """Injecta JS para forzar el scroll al tope de la página."""
    js_code = """
        <script>
            setTimeout(function() {
                window.parent.scrollTo({ top: 0, behavior: 'auto' });
                var mainContent = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                if (mainContent) {
                    mainContent.scrollTo({ top: 0, behavior: 'auto' });
                }
            }, 100); 
        </script>
        """
    st.html(js_code)

def set_stage(new_stage):
    """Cambia la etapa de la aplicación."""
    st.session_state.stage = new_stage
    st.session_state.is_navigating = False
    st.session_state.error_msg = ""
    forzar_scroll_al_top()

def check_all_answered(area):
    """Verifica si todas las preguntas del área han sido respondidas."""
    preguntas_area = df_preguntas[df_preguntas['area'] == area]
    pregunta_ids_area = set(preguntas_area['id'])
    answered_count = sum(1 for q_id in pregunta_ids_area if st.session_state.respuestas.get(q_id) is not None)
    return answered_count == N_PREGUNTAS_POR_AREA

def siguiente_area():
    """Avanza a la siguiente área o finaliza el test."""
    area_actual = AREAS[st.session_state.area_actual_index]
    
    if not check_all_answered(area_actual):
        st.session_state.error_msg = "🚨 ¡Alerta! Por favor, complete las 12 preguntas de la sección actual antes de avanzar."
        st.rerun()
        return
        
    st.session_state.is_navigating = True

    if st.session_state.area_actual_index < len(AREAS) - 1:
        st.session_state.area_actual_index += 1
        set_stage('test_activo')
        st.rerun()
    else:
        calcular_resultados()
        set_stage('resultados')
        st.rerun()

def solve_all():
    """Resuelve automáticamente todas las preguntas."""
    for index, row in df_preguntas.iterrows():
        pregunta_id = row['id']
        st.session_state.respuestas[pregunta_id] = row['respuesta_correcta']

    st.session_state.area_actual_index = len(AREAS) - 1
    calcular_resultados()
    set_stage('resultados')
    st.rerun()

def calcular_resultados():
    """Calcula los resultados basados en las respuestas del usuario."""
    resultados_data = []

    for area in AREAS:
        preguntas_area = df_preguntas[df_preguntas['area'] == area]
        aciertos = 0
        
        for index, row in preguntas_area.iterrows():
            respuesta_usuario = st.session_state.respuestas.get(row['id'])
            if respuesta_usuario == row['respuesta_correcta']:
                aciertos += 1
        
        # Calcular percentil basado en aciertos
        porcentaje = (aciertos / N_PREGUNTAS_POR_AREA) * 100
        
        # Simulación de percentil con variación (en una app real, usarías tablas normativas)
        # Añadimos algo de variación para hacerlo más realista
        percentil = min(99, max(1, porcentaje + np.random.randint(-5, 5)))
        
        clasificacion_val, clasificacion_texto = clasificar_percentil(percentil)
        
        resultados_data.append({
            "Área": area,
            "Código": APTITUDES_MAP[area]["code"],
            "Puntuación Bruta": aciertos,
            "Máxima Puntuación": N_PREGUNTAS_POR_AREA,
            "Porcentaje (%)": float(f"{porcentaje:.1f}"),
            "Percentil": float(percentil), 
            "Clasificación": clasificacion_texto,
            "Color": APTITUDES_MAP[area]["color"]
        })
    
    st.session_state.resultados_df = pd.DataFrame(resultados_data)
    st.session_state.is_navigating = False

# --- 3. COMPONENTE DE BARRA DE PROGRESO ANIMADA ---

def animated_progress_bar(label, percentil, color):
    """Genera una barra de progreso animada usando HTML/CSS."""
    text_color = "white" if percentil > 30 else "black"
    
    html_code = f"""
    <style>
        .progress-container {{ 
            width: 100%; 
            background: #e9ecef; 
            border-radius: 8px; 
            margin: 15px 0 5px 0; 
            overflow: hidden; 
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        .progress-bar-{percentil:.0f} {{ 
            height: 35px; 
            line-height: 35px; 
            color: {text_color}; 
            text-align: center; 
            border-radius: 8px;
            transition: width 1.5s ease-out;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15); 
            width: {percentil:.0f}%;
            font-weight: bold;
            font-size: 1em;
            background-color: {color};
            display: flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
            animation: growBar 1.5s ease-out;
        }}
        @keyframes growBar {{
            from {{ width: 0%; }}
            to {{ width: {percentil:.0f}%; }}
        }}
    </style>
    <div class="progress-container">
        <div class="progress-bar-{percentil:.0f}">
            {label} - Percentil: {percentil:.0f}%
        </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# --- 4. FUNCIONES DE REPORTE PROFESIONAL ---

def get_analisis_detalle(df_resultados):
    """Genera análisis detallado de fortalezas y debilidades."""
    
    df_sorted = df_resultados.sort_values(by='Percentil', ascending=False)
    
    # Top 3 Fortalezas
    top_3 = df_sorted.head(3)
    fortalezas_text = "<ul>"
    for index, row in top_3.iterrows():
        fortalezas_text += f"<li><strong>{row['Área']} ({row['Percentil']:.0f}%)</strong>: Capacidad sobresaliente que puede ser aprovechada en contextos profesionales especializados.</li>"
    fortalezas_text += "</ul>"
    
    # Bottom 3 a Mejorar
    bottom_3 = df_sorted.tail(3)
    mejoras_text = "<ul>"
    for index, row in bottom_3.iterrows():
        mejoras_text += f"<li><strong>{row['Área']} ({row['Percentil']:.0f}%)</strong>: Área que requiere desarrollo mediante entrenamiento específico y práctica continua.</li>"
    mejoras_text += "</ul>"

    # Potencial Ocupacional
    top_area = top_3.iloc[0]['Área']
    if top_area in ["Razonamiento General", "Razonamiento Verbal", "Razonamiento Numérico"]:
        potencial = "Roles Estratégicos y de Gestión (Consultoría, Finanzas, Liderazgo de Proyectos)"
        perfil = "Alto Potencial Cognitivo"
    elif top_area in ["Razonamiento Mecánico", "Razonamiento Espacial", "Razonamiento Técnico"]:
        potencial = "Roles de Ingeniería, Arquitectura y Mantenimiento Técnico"
        perfil = "Fuerte Perfil Técnico-Estructural"
    else:
        potencial = "Roles Administrativos, Control de Calidad y Operaciones"
        perfil = "Sólido Perfil Operativo"

    return {
        "fortalezas": fortalezas_text,
        "mejoras": mejoras_text,
        "potencial": potencial,
        "perfil": perfil,
        "top_area": top_area
    }

def get_estrategias_de_mejora(area):
    """Estrategias de mejora específicas por área."""
    estrategias = {
        "Razonamiento General": "Practicar juegos de lógica, resolver acertijos y leer material complejo. **Aplicación:** Liderazgo estratégico y toma de decisiones.",
        "Razonamiento Verbal": "Ampliar vocabulario con lectura activa y redacción estructurada. **Aplicación:** Comunicación ejecutiva y negociación.",
        "Razonamiento Numérico": "Ejercicios de cálculo mental y análisis estadístico. **Aplicación:** Análisis financiero y presupuestario.",
        "Razonamiento Espacial": "Puzzles 3D, rotación mental y lectura de planos. **Aplicación:** Diseño y planeación arquitectónica.",
        "Velocidad Perceptiva": "Ejercicios de búsqueda y comparación rápida. **Aplicación:** Revisión documental y control de calidad.",
        "Precisión Manual": "Manipulación fina y ensamblaje detallado. **Aplicación:** Cirugía, joyería y micro-ensamblaje.",
        "Coordinación Manual": "Actividades ojo-mano como deportes de precisión. **Aplicación:** Operación de maquinaria compleja.",
        "Atención Concentrada": "Técnica Pomodoro y sesiones de enfoque. **Aplicación:** Auditoría y vigilancia.",
        "Razonamiento Mecánico": "Estudio de máquinas simples y física aplicada. **Aplicación:** Mantenimiento industrial.",
        "Razonamiento Abstracto": "Matrices figurativas y patrones lógicos. **Aplicación:** Análisis predictivo.",
        "Razonamiento Clerical": "Organización y archivo sistemático. **Aplicación:** Gestión documental.",
        "Razonamiento Técnico": "Diagramas de flujo y troubleshooting. **Aplicación:** Soporte técnico.",
    }
    return estrategias.get(area, "Entrenamiento específico recomendado.")

# --- 5. VISTAS DE STREAMLIT ---

def vista_inicio():
    """Página de inicio."""
    forzar_scroll_al_top()

    st.title("🧠 Batería de Aptitudes Generales – GATB Profesional")
    st.header("Evaluación Estructurada de 12 Factores Aptitudinales")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        st.info(f"""
        **🎯 Objetivo:** Medir **12 factores clave** de aptitud con **{N_TOTAL_PREGUNTAS} ítems**.
        
        **📋 Estructura del Test:**
        - **Total de Secciones:** {len(AREAS)}
        - **Preguntas por Sección:** {N_PREGUNTAS_POR_AREA}
        
        **⏱️ Duración estimada:** 45-60 minutos
        """)
    
    with col2:
        st.subheader("Simulación Profesional")
        st.warning("⚠️ **Nota:** Esta es una simulación educativa.")
        
        if st.button("🚀 Iniciar Evaluación", type="primary", use_container_width=True):
            st.session_state.area_actual_index = 0
            set_stage('test_activo')
            st.rerun()

        if st.button("✨ Resolver Todo (Demo)", type="secondary", use_container_width=True):
            solve_all()

def vista_test_activo():
    """Sección de preguntas."""
    area_actual = AREAS[st.session_state.area_actual_index]
    total_areas = len(AREAS)
    current_area_index = st.session_state.area_actual_index
    progress_percentage = (current_area_index + 1) / total_areas

    st.title(f"Sección {current_area_index + 1} de {total_areas}: {area_actual}")
    st.progress(progress_percentage, text=f"Progreso: **{area_actual}** ({APTITUDES_MAP[area_actual]['code']})")
    st.markdown("---")
    
    preguntas_area = df_preguntas[df_preguntas['area'] == area_actual]
    
    all_answered = check_all_answered(area_actual)
    answered_count = sum(1 for q_id in preguntas_area['id'] if st.session_state.respuestas.get(q_id) is not None)
    
    if st.session_state.error_msg:
        st.error(st.session_state.error_msg)

    with st.container(border=True):
        st.subheader(f"Responda a los {N_PREGUNTAS_POR_AREA} ítems de {area_actual}")
        
        q_num = 1
        for index, row in preguntas_area.iterrows():
            pregunta_id = row['id']
            question_text = row['pregunta']
            opciones_radio = [f"{k}) {v}" for k, v in row['opciones'].items()]
            
            default_value_key = st.session_state.respuestas.get(pregunta_id)
            default_index = None
            if default_value_key:
                full_option_text = f"{default_value_key}) {row['opciones'][default_value_key]}"
                try:
                    default_index = opciones_radio.index(full_option_text)
                except:
                    default_index = None

            with st.container(border=True):
                st.markdown(f"**Pregunta {q_num}.**") 
                st.markdown(question_text) 
                
                def on_radio_change(q_id):
                    selected_option_full = st.session_state[f'q_{q_id}']
                    selected_key = selected_option_full.split(')')[0].strip()
                    st.session_state.respuestas[q_id] = selected_key
                    st.session_state.error_msg = ""
                
                st.radio(
                    f"Seleccione su respuesta:", 
                    opciones_radio, 
                    key=f'q_{pregunta_id}', 
                    index=default_index,
                    on_change=on_radio_change,
                    args=(pregunta_id,)
                )
            
            q_num += 1
    
    st.markdown("---")

    if st.session_state.area_actual_index < len(AREAS) - 1:
        next_area_name = AREAS[st.session_state.area_actual_index + 1]
        submit_label = f"➡️ Siguiente: {next_area_name}"
    else:
        submit_label = "✅ Finalizar y Ver Resultados"

    is_disabled = not all_answered
    
    st.button(
        submit_label, 
        type="primary", 
        on_click=siguiente_area, 
        use_container_width=True,
        disabled=is_disabled
    )
    
    if not all_answered:
        st.warning(f"Faltan **{N_PREGUNTAS_POR_AREA - answered_count}** preguntas por responder.")

def vista_resultados():
    """Informe de resultados."""
    forzar_scroll_al_top()

    df_resultados = st.session_state.resultados_df
    analisis = get_analisis_detalle(df_resultados)
    
    st.title("🏆 Informe Ejecutivo de Perfil Aptitudinal GATB")
    st.markdown("---")
    
    # Resumen Ejecutivo
    avg_percentil = df_resultados['Percentil'].mean()
    calificacion, detalle_calificacion, color_calificacion = calificar_global(avg_percentil)

    st.subheader("1. Resumen Ejecutivo")
    
    st.markdown(f"""
    <div style="background-color: {color_calificacion}; padding: 25px; border-radius: 15px; color: white; margin-bottom: 30px; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,0.4);">
        <h2 style="margin: 0; font-size: 2.5em;">{calificacion}</h2>
        <p style="margin: 10px 0; font-size: 1.3em;">Percentil Promedio: {avg_percentil:.1f}%</p>
        <p style="font-size: 1.1em; margin: 0; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.5);">{detalle_calificacion}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="padding: 15px; border-left: 5px solid #ff9900; background-color: #fff8e1; border-radius: 5px; margin-bottom: 20px;">
        <p style="font-weight: bold; margin: 0;">Perfil Identificado:</p>
        <p style="margin: 5px 0 0 0;">{analisis['perfil']} con orientación hacia <strong>{analisis['top_area']}</strong>. Potencial ocupacional en: {analisis['potencial']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # Perfil Aptitudinal Detallado
    st.subheader("2. Detalle de Puntuaciones por Aptitud")
    st.info("El percentil indica el porcentaje de la población que obtuvo una puntuación igual o inferior. Un percentil de 90 significa que supera al 90% de la población de referencia.")

    for index, row in df_resultados.sort_values(by='Percentil', ascending=False).iterrows():
        label = f"**{row['Área']}** ({row['Clasificación']})"
        percentil = row['Percentil']
        color = row['Color']
        animated_progress_bar(label, percentil, color)

    st.markdown("---")

    # Análisis de Fortalezas y Mejoras
    st.subheader("3. Análisis Comparativo del Perfil")
    
    col_fortaleza, col_mejora = st.columns(2)

    with col_fortaleza:
        st.markdown('<h4 style="color: #008000;">🌟 Fortalezas Principales (Top 3)</h4>', unsafe_allow_html=True)
        st.markdown(analisis['fortalezas'], unsafe_allow_html=True)
        st.success("Estas aptitudes son pilares para su desarrollo profesional.")

    with col_mejora:
        st.markdown('<h4 style="color: #dc143c;">📉 Áreas de Oportunidad (Bottom 3)</h4>', unsafe_allow_html=True)
        st.markdown(analisis['mejoras'], unsafe_allow_html=True)
        st.error("Estas áreas requieren atención y desarrollo continuo.")

    st.markdown("---")

    # Potencial Ocupacional
    st.subheader("4. Potencial de Rol y Estrategia de Desarrollo")
    
    st.markdown(f"""
    <div style="padding: 20px; border: 2px solid #4682b4; background-color: #f0f8ff; border-radius: 10px; margin-bottom: 20px;">
        <h5 style="margin-top: 0; color: #4682b4;">🎯 Potencial Ocupacional Recomendado</h5>
        <p style="font-size: 1.15em; font-weight: bold; margin: 10px 0;">{analisis['potencial']}</p>
        <p style="margin: 5px 0 0 0; color: #555;">Basado en su perfil <strong>{analisis['perfil']}</strong>, se recomienda enfocarse en roles que aprovechen sus fortalezas en <strong>{analisis['top_area']}</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Estrategias de Desarrollo
    st.markdown("#### **Estrategias Individualizadas de Desarrollo**")
    st.info("Plan de acción para las áreas con percentiles ≤ 40% o que requieran mejora continua.")
    
    bottom_areas = df_resultados[df_resultados['Percentil'] <= 40]['Área'].tolist()
    
    if bottom_areas:
        for area in bottom_areas:
            estrategia = get_estrategias_de_mejora(area)
            with st.expander(f"📚 Estrategia para **{area}** (`{APTITUDES_MAP[area]['code']}`)", expanded=False):
                st.markdown(f"**Nivel de Prioridad:** ALTA")
                st.markdown(f"**Plan de Acción:** {estrategia}")
    else:
        st.balloons()
        st.success("¡Excelente! Su perfil es equilibrado. Continúe desarrollando sus fortalezas para alcanzar la maestría profesional.")

    st.markdown("---")
    
    # Tabla de Resultados Detallados
    with st.expander("📊 Ver Tabla Completa de Resultados", expanded=False):
        st.dataframe(
            df_resultados[['Área', 'Código', 'Puntuación Bruta', 'Máxima Puntuación', 'Porcentaje (%)', 'Percentil', 'Clasificación']],
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    # Botón para nueva evaluación
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Realizar Nueva Evaluación", type="primary", use_container_width=True):
            # Reiniciar todo el estado
            st.session_state.respuestas = {}
            st.session_state.area_actual_index = 0
            st.session_state.resultados_df = pd.DataFrame()
            st.session_state.error_msg = ""
            set_stage('inicio')
            st.rerun()

# --- 6. CONTROL DEL FLUJO PRINCIPAL ---

if st.session_state.stage == 'inicio':
    vista_inicio()
elif st.session_state.stage == 'test_activo':
    vista_test_activo()
elif st.session_state.stage == 'resultados':
    vista_resultados()

# --- 7. FOOTER ---
st.markdown("---")
st.markdown("""
<p style='text-align: center; font-size: small; color: grey;'>
    📋 Batería GATB Profesional - Versión Simulada para Fines Educativos<br>
    Los resultados son ilustrativos y no constituyen un diagnóstico profesional oficial.<br>
    © 2025 - Desarrollado con Streamlit
</p>
""", unsafe_allow_html=True)
