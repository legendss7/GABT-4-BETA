# --- INICIO DE CORRECCIÓN 3: Instrucciones de UI/UX añadidas como comentario ---
"""
Aquí tienes varios prompts detallados para generar una pantalla de resultados profesional para un test "GABT Pro Max".
He basado los prompts en la suposición de que "GABT" es un test de aptitudes (similar al GATB - General Aptitude Test Battery, un test de aptitudes vocacionales) y que el "Pro Max" implica un diseño de alta gama, tecnológico y moderno.

Prompt 1: Moderno, Corporativo y Centrado en Datos (Estilo Dashboard)
Este prompt es ideal para una vista de escritorio o web, enfocado en la analítica.

UI/UX design de una pantalla de resultados de un test de aptitud profesional llamado 'GABT Pro Max'. La interfaz es un dashboard web, limpio, moderno y de alta fidelidad.

Elementos clave:
1. Un 'Puntaje General' prominente (ej. '92%') en una tarjeta principal.
2. Un gráfico de radar (radar chart) elegante que desglosa 8 aptitudes clave (Verbal, Numérica, Espacial, Percepción, etc.).
3. Gráficos de barras horizontales comparando el puntaje del usuario con el promedio de la industria.
4. Una sección de 'Recomendaciones de Carrera' o 'Fortalezas Clave' con íconos minimalistas.

Estilo y Paleta:
- Paleta de colores corporativa: azules profundos (#003366), blancos, grises claros (#F4F7FA) y un toque de verde azulado (teal, #00AAB5) o dorado como color de acento.
- Tipografía sans-serif nítida (como Inter o Roboto).
- Uso de espacio en blanco, sombras sutiles y bordes redondeados.
- Mockup de Figma, tendencia en Behance, diseño profesional.

Prompt 2: Elegante, Minimalista y en Modo Oscuro (Dark Mode)
Este prompt busca un acabado más "premium" y tecnológico, muy popular en aplicaciones modernas.

Diseño de interfaz (UI) para la pantalla de resultados del 'GABT Pro Max', en modo oscuro (dark mode) profesional. La pantalla debe sentirse premium y analítica.

Elementos clave:
1. Un saludo al usuario y su puntaje principal en un medidor circular (gauge chart) con un gradiente brillante (cian o verde neón).
2. Tarjetas (cards) de vidrio esmerilado (frosted glass / glassmorphism) que muestran los puntajes de las sub-categorías.
3. Un gráfico de líneas o área que muestra el 'Progreso de Aptitud' (si aplica).
4. Un botón (CTA) claro que dice 'Ver Informe Detallado' o 'Explorar Carreras'.

Estilo y Paleta:
- Fondo: Gris muy oscuro o azul noche (#12182B).
- Texto: Blanco y gris claro.
- Acentos: Cian brillante (#00E0FF) o dorado (#FFD700) para gráficos y botones.
- Diseño limpio, minimalista, con mucho espacio negativo.
- Alta fidelidad, mockup de UI/UX, fotorrealista.
"""
# --- FIN DE CORRECCIÓN 3: Instrucciones de UI/UX añadidas como comentario ---

import streamlit as st
import pandas as pd
import numpy as np
import time

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="Batería de Aptitudes GABT Pro Max")

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
    """Clasifica el percentil en rangos y devuelve un valor numérico para la barra (aunque se usa el percentil real para la animación)."""
    if porcentaje >= 90: return 96, "Superior (90-99)"
    elif porcentaje >= 80: return 88, "Alto (80-89)"
    elif porcentaje >= 60: return 70, "Promedio Alto (60-79)"
    elif porcentaje >= 40: return 50, "Promedio (40-59)"
    elif porcentaje >= 20: return 30, "Promedio Bajo (20-39)"
    elif porcentaje >= 10: return 15, "Bajo (10-19)"
    else: return 5, "Muy Bajo (0-9)"

def calificar_global(avg_percentil):
    """Genera la calificación ejecutiva basada en el promedio global de percentiles."""
    if avg_percentil >= 85: return "Potencial Ejecutivo 🌟", "El perfil indica un potencial excepcionalmente alto y equilibrado para roles directivos, estratégicos y de alta complejidad. Capacidad de aprendizaje superior y adaptación rápida a cualquier entorno.", "#008000"
    elif avg_percentil >= 65: return "Nivel Profesional Avanzado 🏆", "El perfil es sólido, con fortalezas claras y un buen balance aptitudinal. Excelente para roles técnicos especializados, de gestión de proyectos y consultoría.", "#4682b4"
    elif avg_percentil >= 40: return "Perfil Competitivo 💼", "El perfil se sitúa en el promedio superior, demostrando suficiencia en todas las áreas. Apto para la mayoría de roles operativos y de coordinación. Requiere enfoque en el desarrollo de fortalezas clave.", "#ff8c00"
    else: return "Período de Desarrollo 🛠️", "El perfil requiere un período de enfoque intensivo en el desarrollo de aptitudes clave. Se recomienda comenzar con roles de soporte y entrenamiento continuo.", "#dc143c"

def generate_gatb_questions():
    """Genera 144 preguntas simuladas con respuestas esperadas para el cálculo. (CORREGIDO con preguntas más variadas)."""
    
    # Estructura base para 12 preguntas por área con opciones genéricas
    base_opciones = {"a": "Opción A", "b": "Opción B", "c": "Opción C", "d": "Opción D"}
    
    # Preguntas simuladas y su respuesta correcta esperada
    test_specs = {
        "Razonamiento General": {"code": "G", "pregunta_base": "¿Cuál de las siguientes palabras no encaja con las demás?", "correcta": "c"},
        "Razonamiento Verbal": {"code": "V", "pregunta_base": "Sinónimo de 'Eficaz':", "correcta": "a"},
        "Razonamiento Numérico": {"code": "N", "pregunta_base": "Si 3x + 5 = 20, ¿cuál es el valor de x?", "correcta": "d"},
        "Razonamiento Espacial": {"code": "S", "pregunta_base": "Elija la figura que continúa la secuencia de rotación.", "correcta": "b"},
        "Velocidad Perceptiva": {"code": "P", "pregunta_base": "¿Cuál código es idéntico a 8G49C2?", "correcta": "a"},
        "Precisión Manual": {"code": "Q", "pregunta_base": "Marque la pequeña 'x' dentro del círculo pequeño.", "correcta": "c"},
        "Coordinación Manual": {"code": "K", "pregunta_base": "Seleccione el camino correcto en el laberinto.", "correcta": "b"},
        "Atención Concentrada": {"code": "A", "pregunta_base": "Encuentre el número de errores en el siguiente párrafo.", "correcta": "d"},
        "Razonamiento Mecánico": {"code": "M", "pregunta_base": "Si el engranaje A gira a la derecha, ¿hacia dónde gira el engranaje B?", "correcta": "a"},
        "Razonamiento Abstracto": {"code": "R", "pregunta_base": "Complete la matriz de figuras (ej. Test de Raven).", "correcta": "c"},
        "Razonamiento Clerical": {"code": "C", "pregunta_base": "Clasifique el documento 'Z-2024-FISC-10' correctamente.", "correcta": "d"},
        "Razonamiento Técnico": {"code": "T", "pregunta_base": "Identifique el diagrama de un circuito en serie.", "correcta": "b"},
    }
    
    questions = []
    current_id = 1
    for area_name in AREAS:
        spec = test_specs.get(area_name)
        code = spec["code"]
        expected_answer = spec["correcta"]
            
        for i in range(N_PREGUNTAS_POR_AREA):
            questions.append({
                "id": current_id, 
                "area": area_name,
                "code": code,
                "pregunta": f"Pregunta {code}-{i+1}. {spec['pregunta_base']} (Simulada)",
                "opciones": base_opciones, 
                "respuesta_correcta": expected_answer 
            })
            current_id += 1
          
    return pd.DataFrame(questions)

df_preguntas = generate_gatb_questions()
N_TOTAL_PREGUNTAS = len(df_preguntas)

# --- 2. FUNCIONES DE ESTADO Y NAVEGACIÓN ---

# Inicialización de Session State
if 'stage' not in st.session_state: st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'area_actual_index' not in st.session_state: st.session_state.area_actual_index = 0
if 'is_navigating' not in st.session_state: st.session_state.is_navigating = False 
if 'error_msg' not in st.session_state: st.session_state.error_msg = ""
if 'resultados_df' not in st.session_state: st.session_state.resultados_df = pd.DataFrame()


# Función MAXIMAMENTE FORZADA para el scroll al top (SOLUCIÓN CLAVE)
def forzar_scroll_al_top():
    """
    Injecta JS para forzar el scroll al tope ABSOLUTO de la página (top: 0).
    """
    js_code = """
        <script>
            setTimeout(function() {
                // Intento principal: scroll de la ventana
                window.parent.scrollTo({ top: 0, behavior: 'auto' });
                
                // Intento secundario: scroll del contenedor principal de Streamlit
                var mainContent = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                if (mainContent) {
                    mainContent.scrollTo({ top: 0, behavior: 'auto' });
                }
            }, 250); 
        </script>
        """
    # Se usa st.html para inyectar el script forzado
    st.html(js_code)


def set_stage(new_stage):
    """Cambia la etapa de la aplicación, desbloquea la navegación y llama a la función de scroll."""
    st.session_state.stage = new_stage
    st.session_state.is_navigating = False # Desbloquear al cambiar de etapa
    st.session_state.error_msg = "" # Limpiar mensaje de error
    forzar_scroll_al_top() # <<-- LLAMADA A LA FUNCIÓN DE SCROLL AL TOP


def check_all_answered(area):
    """Verifica si todas las preguntas del área actual han sido respondidas."""
    preguntas_area = df_preguntas[df_preguntas['area'] == area]
    pregunta_ids_area = set(preguntas_area['id'])
    answered_count = sum(1 for q_id in pregunta_ids_area if st.session_state.respuestas.get(q_id) is not None)
    return answered_count == N_PREGUNTAS_POR_AREA

def siguiente_area():
    """Avanza a la siguiente área o finaliza el test, con validación y bloqueo."""
    
    area_actual = AREAS[st.session_state.area_actual_index]
    
    if not check_all_answered(area_actual):
        st.session_state.error_msg = "🚨 ¡Alerta! Por favor, complete las 12 preguntas de la sección actual antes de avanzar."
        return
        
    st.session_state.is_navigating = True # Bloqueo temporal mientras se navega

    if st.session_state.area_actual_index < len(AREAS) - 1:
        st.session_state.area_actual_index += 1
        set_stage('test_activo')
    else:
        calcular_resultados()
        set_stage('resultados')

def solve_all():
    """Resuelve automáticamente todas las preguntas con la respuesta correcta (simulación) y navega a resultados."""
    for index, row in df_preguntas.iterrows():
        pregunta_id = row['id']
        st.session_state.respuestas[pregunta_id] = row['respuesta_correcta']

    st.session_state.area_actual_index = len(AREAS) - 1
    
    calcular_resultados()
    set_stage('resultados')

def calcular_resultados():
    """Calcula y almacena los resultados finales, incluyendo el percentil numérico. (Simulación de percentiles)"""
    resultados_data = []
    
    # Simulación de resultados para que el informe sea interesante
    np.random.seed(42) # Para resultados consistentes en la simulación
    simulated_percentiles = {
        "Razonamiento General": 90, "Razonamiento Verbal": 85, "Razonamiento Numérico": 80,
        "Razonamiento Espacial": 65, "Velocidad Perceptiva": 55, "Precisión Manual": 45,
        "Coordinación Manual": 35, "Atención Concentrada": 25, "Razonamiento Mecánico": 75,
        "Razonamiento Abstracto": 60, "Razonamiento Clerical": 95, "Razonamiento Técnico": 50
    }

    for area in AREAS:
        # Usamos los percentiles simulados
        percentil = simulated_percentiles.get(area, np.random.randint(20, 95))
        clasificacion_val, clasificacion_texto = clasificar_percentil(percentil)
        
        # Invertimos el cálculo para que el 'Porcentaje' coincida con el Percentil para fines de visualización simplificada.
        porcentaje = percentil
        aciertos_area = round((percentil / 100) * N_PREGUNTAS_POR_AREA) # Puntuación bruta simulada
        
        resultados_data.append({
            "Área": area,
            "Código": APTITUDES_MAP[area]["code"],
            "Puntuación Bruta": aciertos_area,
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
        .progress-bar {{ 
            height: 35px;
            line-height: 35px; 
            color: {text_color}; 
            text-align: center; 
            border-radius: 8px;
            transition: width 1.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            /* Animación más profesional */
            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
            width: 0%; /* Comienza en 0% */
            font-weight: bold;
            font-size: 1em;
            background-color: {color};
            display: flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
        }}
        /* Animación forzada para Streamlit - inyectamos el ancho final */
        .progress-bar[data-percentil="{percentil:.0f}"] {{
            width: {percentil:.0f}%;
        }}
    </style>
    <div class="progress-container">
        <div class="progress-bar" data-percentil="{percentil:.0f}" style="background-color: {color}; color: {text_color};">
            {label} - Puntuación Percentil: {percentil:.0f}%
        </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# --- 4. FUNCIONES DE REPORTE PROFESIONAL (MEJORADO) ---

def get_analisis_detalle(df_resultados):
    """Genera un análisis detallado de las fortalezas y debilidades, y el potencial ocupacional."""
    
    df_sorted = df_resultados.sort_values(by='Percentil', ascending=False)
    
    # Top 3 Fortalezas
    top_3 = df_sorted.head(3)
    fortalezas_text = "<ul>"
    for index, row in top_3.iterrows():
        fortalezas_text += f"<li>**{row['Área']} ({row['Percentil']}%)**: Una habilidad sobresaliente en **{row['Área']}** sugiere un alto potencial para la [aplicación clave de la aptitud].</li>"
    fortalezas_text += "</ul>"
    
    # Bottom 3 a Mejorar
    bottom_3 = df_sorted.tail(3)
    mejoras_text = "<ul>"
    for index, row in bottom_3.iterrows():
        mejoras_text += f"<li>**{row['Área']} ({row['Percentil']}%)**: El desarrollo de **{row['Área']}** debe ser una prioridad, ya que es la base para [área de mejora clave]. Se sugiere el entrenamiento inmediato en ejercicios de [tipo de ejercicio].</li>"
    mejoras_text += "</ul>"

    # Potencial Ocupacional
    top_area = top_3.iloc[0]['Área']
    if top_area in ["Razonamiento General", "Razonamiento Verbal", "Razonamiento Numérico"]:
        potencial = "Roles Estratégicos y de Gestión de Información (Consultoría, Finanzas, Liderazgo de Proyectos)."
        perfil = "Alto Potencial Cognitivo (G-Factor)."
    elif top_area in ["Razonamiento Mecánico", "Razonamiento Espacial", "Razonamiento Técnico"]:
        potencial = "Roles de Ingeniería, Arquitectura, Diseño Industrial y Mantenimiento Técnico Especializado."
        perfil = "Fuerte Perfil Técnico-Estructural."
    else:
        potencial = "Roles Administrativos, de Control de Calidad, Logística, Programación y Operaciones de Alto Volumen."
        perfil = "Sólido Perfil Operativo y de Detalle."

    return {
        "fortalezas": fortalezas_text,
        "mejoras": mejoras_text,
        "potencial": potencial,
        "perfil": perfil,
        "top_area": top_area
    }

def get_estrategias_de_mejora(area):
    """Proporciona estrategias de mejora específicas para cada área aptitudinal."""
    estrategias = {
        "Razonamiento General": "Practicar juegos de lógica, resolver acertijos complejos y leer material de alta complejidad para expandir la capacidad de abstracción y juicio. **Aplicación:** Liderazgo estratégico y toma de decisiones complejas.",
        "Razonamiento Verbal": "Ampliar el vocabulario con lectura activa y usar herramientas de redacción para estructurar ideas complejas en informes y correos. **Aplicación:** Comunicación ejecutiva y negociación.",
        "Razonamiento Numérico": "Realizar ejercicios diarios de cálculo mental, practicar la resolución rápida de problemas aritméticos y familiarizarse con la interpretación de datos estadísticos. **Aplicación:** Análisis financiero y control presupuestario.",
        "Razonamiento Espacial": "Usar aplicaciones o puzzles 3D para la rotación mental, practicar el dibujo técnico o la lectura de planos y mapas. **Aplicación:** Diseño, planeación arquitectónica y montaje.",
        "Velocidad Perceptiva": "Entrenar con ejercicios de 'búsqueda y comparación' rápida de códigos, números y patrones en columnas. Ideal para la revisión de documentos. **Aplicación:** Revisión de contratos y control de calidad masivo.",
        "Precisión Manual": "Realizar tareas que requieran manipulación fina, como el ensamblaje de modelos pequeños o la práctica de caligrafía y dibujo detallado. **Aplicación:** Cirugía, joyería y micro-ensamblaje.",
        "Coordinación Manual": "Participar en actividades que sincronicen ojo-mano, como deportes con raqueta (tenis, ping pong), mecanografía rápida o el uso de software de dibujo. **Aplicación:** Operación de maquinaria compleja y manejo de vehículos.",
        "Atención Concentrada": "Implementar la técnica Pomodoro o sesiones de enfoque ininterrumpido. Eliminar distracciones y practicar la revisión de textos largos buscando errores específicos. **Aplicación:** Tareas de auditoría y vigilancia.",
        "Razonamiento Mecánico": "Estudiar diagramas de máquinas simples (palancas, poleas, engranajes) y leer libros sobre principios de física aplicada y mantenimiento industrial. **Aplicación:** Mantenimiento preventivo y diagnóstico de fallas mecánicas.",
        "Razonamiento Abstracto": "Resolver secuencias de matrices figurativas (tipo Raven), puzzles no verbales y practicar el reconocimiento de patrones lógicos abstractos. **Aplicación:** Detección de tendencias y análisis predictivo sin datos numéricos.",
        "Razonamiento Clerical": "Entrenar la organización y archivo de documentos. Practicar la clasificación rápida y la verificación cruzada de datos alfanuméricos. **Aplicación:** Gestión documental, archivo legal y tareas administrativas.",
        "Razonamiento Técnico": "Analizar diagramas de flujo y resolución de problemas técnicos (troubleshooting) de sistemas conocidos (eléctricos, mecánicos, informáticos). **Aplicación:** Soporte técnico y resolución de problemas informáticos de primer nivel.",
    }
    return estrategias.get(area, "Se recomienda entrenamiento específico en tareas de aplicación práctica.")


# --- 5. VISTAS DE STREAMLIT ---

def vista_inicio():
    """Muestra la página de inicio e instrucciones. (Scroll y Clic Único Corregidos)"""

    st.title("🧠 Batería de Aptitudes Generales – GABT Pro Max")
    st.header("Evaluación Estructurada de 12 Factores Aptitudinales")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        st.info(f"""
        **🎯 Objetivo:** Medir **12 factores clave** de aptitud con **{N_TOTAL_PREGUNTAS} ítems simulados** para fines educativos.
        
        **📋 Estructura del Test:**
        - **Total de Secciones:** **{len(AREAS)}**
        - **Preguntas por Sección:** **{N_PREGUNTAS_POR_AREA}**
        """)
    
    with col2:
        st.subheader("Simulación Profesional")
        st.warning("⚠️ **Nota:** Esta es una simulación. Los resultados son ilustrativos para el análisis.")
        
        # Corregido: La llamada a set_stage dentro de on_click asegura que se ejecuta al inicio
        if st.button("🚀 Iniciar Evaluación", type="primary", use_container_width=True, on_click=lambda: set_stage('test_activo')):
            pass 

        if st.button("✨ Resolver Todo (Demo)", type="secondary", use_container_width=True, on_click=solve_all):
            pass


def vista_test_activo():
    """Muestra la sección de preguntas del área actual."""
    
    area_actual = AREAS[st.session_state.area_actual_index]
    total_areas = len(AREAS)
    current_area_index = st.session_state.area_actual_index
    progress_percentage = (current_area_index + 1) / total_areas

    # --- Cabecera y Barra de Progreso ---
    st.title(f"Sección {current_area_index + 1} de {total_areas}: {area_actual}")
    st.progress(progress_percentage, text=f"Progreso General: **{area_actual}** ({APTITUDES_MAP[area_actual]['code']})")
    st.markdown("---")
    
    preguntas_area = df_preguntas[df_preguntas['area'] == area_actual]
    
    all_answered = check_all_answered(area_actual)
    answered_count = sum(1 for q_id in preguntas_area['id'] if st.session_state.respuestas.get(q_id) is not None)
    
    if st.session_state.error_msg:
        st.error(st.session_state.error_msg)

    with st.container(border=True):
        st.subheader(f"Tarea: Responda a los {N_PREGUNTAS_POR_AREA} ítems de {area_actual}")
        
        q_num = 1
        for index, row in preguntas_area.iterrows():
            pregunta_id = row['id']
            question_text = row['pregunta']
            opciones_radio = [f"{k}) {v}" for k, v in row['opciones'].items()]
            
            # Determinar el índice por defecto para mantener la selección
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
                    """Maneja el cambio en el radio button y actualiza la respuesta en el estado."""
                    selected_option_full = st.session_state[f'q_{q_id}']
                    selected_key = selected_option_full.split(')')[0].strip()
                    st.session_state.respuestas[q_id] = selected_key
                    st.session_state.error_msg = ""
                
                st.radio(
                    f"Respuesta {row['code']}-{q_num}:", 
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
        submit_label = f"➡️ Siguiente Sección: {next_area_name}"
    else:
        submit_label = "✅ Finalizar Test y Generar Informe"

    is_disabled = not all_answered
    
    # Botón Siguiente que llama a la función de navegación (y fuerza el scroll)
    st.button(
        submit_label, 
        type="primary", 
        on_click=siguiente_area, 
        use_container_width=True,
        disabled=is_disabled
    )
    
    if not all_answered:
        st.warning(f"Faltan **{N_PREGUNTAS_POR_AREA - answered_count}** preguntas por responder en esta sección.")


def vista_resultados():
    """Muestra el informe de resultados profesional, detallado y animado."""

    df_resultados = st.session_state.resultados_df
    analisis = get_analisis_detalle(df_resultados)
    
    st.title("🏆 Informe Ejecutivo de Perfil Aptitudinal GABT Pro Max")
    st.markdown("---")
    
    # --- 1. Calificación Global (Resumen Ejecutivo) ---
    avg_percentil = df_resultados['Percentil'].mean()
    calificacion, detalle_calificacion, color_calificacion = calificar_global(avg_percentil)

    st.subheader("1. Resumen Ejecutivo y Perfil Global")
    
    # Contenedor para la calificación global
    st.markdown(f"""
    <div style="background-color: {color_calificacion}; padding: 25px; border-radius: 15px; color: white; margin-bottom: 30px; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,0.4);">
        <h2 style="margin: 0; font-size: 2.5em; font-weight: 900; letter-spacing: 1px;">{calificacion}</h2>
        <p style="margin: 5px 0 15px 0; font-size: 1.3em; font-weight: 500;">Percentil Promedio Global: **{avg_percentil:.1f}%**</p>
        <p style="font-size: 1.1em; margin: 0; border-top: 1px solid rgba(255,255,255,0.5); padding-top: 10px; opacity: 0.9;">**Diagnóstico:** {detalle_calificacion}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Conclusiones del Evaluador
    st.markdown(f"""
    <div style="padding: 15px; border-left: 5px solid #ff9900; background-color: #fff8e1; border-radius: 5px; margin-bottom: 20px;">
        <p style="font-weight: bold; margin: 0;">Conclusiones del Evaluador:</p>
        <p style="margin: 5px 0 0 0;">El perfil muestra una base **{analisis['perfil']}**, con una clara inclinación hacia **{analisis['top_area']}**. El individuo es particularmente apto para {analisis['potencial']}. Se recomienda un plan de desarrollo focalizado en las áreas de menor rendimiento para lograr un perfil más holístico.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # --- 2. Perfil Aptitudinal Detallado (Animado) ---
    st.subheader("2. Detalle de Puntuaciones por Aptitud (Percentiles)")
    st.info("El percentil indica el porcentaje de la población que obtuvo una puntuación igual o inferior a la suya. Un percentil de 90 significa que supera al 90% de la población de referencia.")

    for index, row in df_resultados.sort_values(by='Percentil', ascending=False).iterrows():
        label = f"**{row['Área']}** ({row['Clasificación']})"
        percentil = row['Percentil']
        color = row['Color']
        animated_progress_bar(label, percentil, color)

    st.markdown("---")

    # --- 3. Análisis de Fortalezas y Áreas de Mejora ---
    st.subheader("3. Análisis Comparativo del Perfil")
    
    col_fortaleza, col_mejora = st.columns(2)

    # FORTALEZAS (TOP 3)
    with col_fortaleza:
        st.markdown('<h4 style="color: #008000;">🌟 Fortalezas Intrínsecas (Top 3)</h4>', unsafe_allow_html=True)
        st.markdown(analisis['fortalezas'], unsafe_allow_html=True)
        st.success("Estas aptitudes deben ser los pilares de la trayectoria profesional y la base para el entrenamiento de otras áreas.")

    # ÁREAS A MEJORAR (BOTTOM 3)
    with col_mejora:
        st.markdown('<h4 style="color: #dc143c;">📉 Áreas de Oportunidad (Bottom 3)</h4>', unsafe_allow_html=True)
        st.markdown(analisis['mejoras'], unsafe_allow_html=True)
        st.error("Una puntuación baja en estas áreas puede limitar el potencial en roles específicos y requiere desarrollo.")

    st.markdown("---")

    # --- 4. Potencial Ocupacional y Estrategia de Desarrollo ---
    st.subheader("4. Potencial de Rol y Plan de Desarrollo")
    
    st.markdown(f"""
    <div style="padding: 20px; border: 1px solid #4682b4; background-color: #f0f8ff; border-radius: 10px; margin-bottom: 20px;">
        <h5 style="margin-top: 0; color: #4682b4;">Potencial Ocupacional Recomendado (Enfoque Primario)</h5>
        <p style="font-size: 1.1em; font-weight: bold;">{analisis['potencial']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### **Estrategias Individualizadas de Desarrollo**")
    st.info("Plan de acción basado en las aptitudes con percentiles bajos (≤ 40%) o aquellas que requieran mejora continua.")
    
    # Filtrar áreas con percentil <= 40
    bottom_areas = df_resultados[df_resultados['Percentil'] <= 40]['Área'].tolist()
    
    if bottom_areas:
        for area in bottom_areas:
            estrategia = get_estrategias_de_mejora(area)
            with st.expander(f"📚 Estrategia para desarrollar **{area}** (`{APTITUDES_MAP[area]['code']}`)", expanded=True):
                st.markdown(f"**Nivel de Prioridad:** **ALTA**")
                st.markdown(f"**Plan de Acción Sugerido:** {estrategia}")
    else:
        st.balloons()
        st.success("Su perfil es excepcional y equilibrado. El plan de acción es mantener las fortalezas y buscar la maestría profesional.")


    st.markdown("---")

    if st.button("⏪ Realizar Nueva Evaluación", type="secondary", on_click=lambda: set_stage('inicio')):
        st.session_state.respuestas = {}
        st.session_state.area_actual_index = 0
        # set_stage('inicio') ya es llamado por on_click

# --- 6. CONTROL DEL FLUJO PRINCIPAL ---

if st.session_state.stage == 'inicio':
    vista_inicio()
elif st.session_state.stage == 'test_activo':
    vista_test_activo()
elif st.session_state.stage == 'resultados':
    vista_resultados()

# --- 7. FOOTER Y ACERCA DE ---
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: small; color: grey;'>Informe generado por IA basado en la estructura del GATB. Las puntuaciones son simuladas con fines educativos y de demostración.</p>", unsafe_allow_html=True)
