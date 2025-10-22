import streamlit as st
import pandas as pd
import numpy as np
import base64

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="Batería de Aptitudes GATB Profesional")

# Mapeo de Aptitudes y Colores para el display
APTITUDES_MAP = {
    "Razonamiento General": {"code": "G", "color": "orange"},
    "Razonamiento Verbal": {"code": "V", "color": "blue"},
    "Razonamiento Numérico": {"code": "N", "color": "green"},
    "Razonamiento Espacial": {"code": "S", "color": "red"},
    "Velocidad Perceptiva": {"code": "P", "color": "purple"},
    "Precisión Manual": {"code": "Q", "color": "cyan"},
    "Coordinación Manual": {"code": "K", "color": "magenta"},
    "Atención Concentrada": {"code": "A", "color": "lime"},
    "Razonamiento Mecánico": {"code": "M", "color": "teal"},
    "Razonamiento Abstracto": {"code": "R", "color": "yellow"},
    "Razonamiento Clerical": {"code": "C", "color": "pink"},
    "Razonamiento Técnico": {"code": "T", "color": "brown"},
}
AREAS = list(APTITUDES_MAP.keys())
N_PREGUNTAS_POR_AREA = 12

# Sistema de Clasificación por Percentil (SIMULADO para esta muestra)
def clasificar_percentil(porcentaje):
    """Convierte el porcentaje de acierto en un percentil simulado y clasificación."""
    if porcentaje >= 90:
        return 96, "Muy Alto 🟢"
    elif porcentaje >= 70:
        return 85, "Alto ⬆️"
    elif porcentaje >= 30:
        return 50, "Promedio 🟠"
    elif porcentaje >= 10:
        return 20, "Bajo ⬇️"
    else:
        return 5, "Muy Bajo 🔻"

# Función para generar interpretación detallada y animada (en HTML/CSS)
def obtener_interpretacion(percentil, area_code, area_name):
    """Genera una interpretación detallada y formateada basada en el percentil y el código de área."""
    interpretacion_base = {
        "G": "Capacidad para percibir y comprender relaciones, aprender y emitir juicios. Es el factor 'g' de la inteligencia, clave para el éxito en cualquier campo.",
        "V": "Habilidad para entender ideas expresadas en palabras, dominar vocabulario y redactar informes. Esencial para la comunicación eficaz.",
        "N": "Rapidez y precisión para trabajar con números, realizar cálculos y resolver problemas matemáticos. Crucial en finanzas y análisis de datos.",
        "S": "Habilidad para percibir formas en dos o tres dimensiones, rotar objetos mentalmente y visualizar relaciones espaciales. Importante en diseño e ingeniería.",
        "P": "Rapidez para ver detalles en un objeto o tabla, realizar comparaciones y detectar pequeñas diferencias. Fundamental para el control de calidad.",
        "Q": "Destreza y coordinación fina de los dedos y las manos, necesaria para ensamblar piezas pequeñas o manipular instrumentos. Típica de la cirugía o la relojería.",
        "K": "Habilidad para coordinar movimientos oculares y manuales, controlando la mano con precisión. Importante en deportes, conducción y mecanografía.",
        "A": "Capacidad de mantener la atención en una tarea monótona o repetitiva durante períodos prolongados, minimizando errores. Clave en roles de auditoría o ingreso de datos.",
        "M": "Comprensión de principios físicos básicos, máquinas simples, fuerzas y movimiento. Esencial para técnicos, mecánicos y operarios de maquinaria.",
        "R": "Capacidad para descubrir patrones y relaciones en figuras no verbales o simbólicas, crucial para la lógica pura y la programación.",
        "C": "Rapidez y precisión para observar detalles verbales y numéricos, como en la clasificación, archivo y verificación de documentos. Típico de roles administrativos.",
        "T": "Aplicación de la lógica y principios para identificar fallas, diseñar soluciones o seguir procesos técnicos complejos. Combina G, S, y M.",
    }
    
    base_text = interpretacion_base.get(area_code, f"Mide una habilidad cognitiva o motriz específica.")

    if percentil >= 90:
        color_bg = "#38c172"  # Verde brillante (Muy Alto)
        color_text = "white"
        title = "🟢 Fortaleza Excepcional"
        detalle = f"Su desempeño supera a más del 90% de la población. Esta aptitud es una **ventaja competitiva** que debe ser el foco de su carrera. Demuestra una **alta facilidad y eficiencia** para el aprendizaje y la ejecución de tareas relacionadas con **{area_name}**. ({base_text})"
    elif percentil >= 70:
        color_bg = "#6cb2eb"  # Azul claro (Alto)
        color_text = "white"
        title = "⬆️ Nivel Superior al Promedio"
        detalle = f"Posee una capacidad sólida que lo sitúa en el cuartil superior. Puede manejar tareas de complejidad media-alta de forma autónoma. Es un recurso valioso en actividades que requieran **{area_name}**. ({base_text})"
    elif percentil >= 30:
        color_bg = "#ff9900"  # Naranja (Promedio)
        color_text = "white"
        title = "🟠 Nivel Promedio"
        detalle = f"Su capacidad es consistente con la media de la población. Puede desempeñar roles sin mayores dificultades, pero el desarrollo continuo será clave si el puesto exige un alto dominio de **{area_name}**. ({base_text})"
    elif percentil >= 10:
        color_bg = "#e3342f"  # Rojo (Bajo)
        color_text = "white"
        title = "⬇️ Área de Oportunidad"
        detalle = f"El desempeño se encuentra por debajo del promedio. Las tareas dependientes de **{area_name}** pueden ser desafiantes. Se sugiere **entrenamiento específico** o buscar roles donde esta aptitud sea menos crítica. ({base_text})"
    else:
        color_bg = "#490705"  # Rojo Oscuro (Muy Bajo)
        color_text = "white"
        title = "🔻 Necesidad Crítica de Soporte"
        detalle = f"El rendimiento está muy por debajo del estándar. La exposición a tareas de alta demanda en **{area_name}** debe ser minimizada y acompañada de un **plan de desarrollo intensivo**. ({base_text})"
        
    return f"""
        <div style="background-color: {color_bg}; padding: 20px; border-radius: 12px; color: {color_text}; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h4 style="margin-top: 0; color: {color_text};">{title} - {area_name} ({area_code})</h4>
            <p style="font-size: 0.9em; margin-bottom: 0;">**Percentil:** {percentil}</p>
            <p style="font-size: 0.9em; margin-bottom: 0;">{detalle}</p>
        </div>
    """

# Función para forzar el scroll al inicio de la página
def js_scroll_to_top():
    """Injecta JS para forzar el scroll al inicio de la página."""
    js_code = """
    <script>
        try {
            // Intenta hacer scroll en el contenedor principal de Streamlit dentro del iframe
            const mainContainer = document.querySelector('.main');
            if (mainContainer) {
                mainContainer.scrollTop = 0;
            } else {
                // Fallback: scroll al inicio del documento
                document.documentElement.scrollTop = 0;
                document.body.scrollTop = 0;
            }
        } catch (e) {
            console.error("No se pudo forzar el scroll:", e);
        }
    </script>
    """
    st.html(js_code)


# --- 2. DEFINICIÓN DEL TEST (144 Items) ---

# Generación de preguntas representativas y uso de placeholders para las 144 preguntas
PREGUNTAS_GATB = []
current_id = 1

for area, data in APTITUDES_MAP.items():
    code = data['code']
    
    for i in range(1, N_PREGUNTAS_POR_AREA + 1):
        pregunta = f"[{code}-{i}] "
        opciones = {"a": "Opción A", "b": "Opción B", "c": "Opción C", "d": "Opción D"}
        
        # Personalizar las primeras preguntas de algunas áreas
        if code == "G" and i == 1:
            pregunta += "Si todos los A son B y ningún C es A, ¿qué se puede concluir lógicamente?"
            opciones = {"a": "Ningún B es C", "b": "Algunos B son C", "c": "Algunos B no son C", "d": "Todos los C son B"}
            respuesta = "c"
        elif code == "V" and i == 1:
            pregunta += "¿Cuál es el sinónimo de 'Ubicuo'?"
            opciones = {"a": "Raro", "b": "Presente", "c": "Imposible", "d": "Fugaz"}
            respuesta = "b"
        elif code == "N" and i == 1:
            pregunta += "Serie: 7, 14, 21, 28, ¿Cuál sigue?"
            opciones = {"a": "30", "b": "35", "c": "40", "d": "42"}
            respuesta = "b"
        elif code == "S" and i == 1:
            # Pregunta con necesidad de imagen para Rotación de Figuras
            pregunta += f"Observa la figura de la izquierda. ¿Cuál de las opciones muestra la figura rotada 90 grados a la derecha? "
            opciones = {"a": "Figura A (rotada)", "b": "Figura B (reflejada)", "c": "Figura C (incorrecta)", "d": "Figura D (original)"}
            respuesta = "a"
        elif code == "M" and i == 1:
            # Pregunta con necesidad de imagen para Principios Mecánicos
            pregunta += f"En el sistema de palanca que se muestra, ¿en qué punto aplicarías menos fuerza para levantar la carga? "
            opciones = {"a": "Cerca del fulcro", "b": "Lejos del fulcro", "c": "Directamente sobre la carga", "d": "La fuerza es constante"}
            respuesta = "b"
        else:
            # Preguntas genéricas para completar la muestra de 144
            pregunta += f"Pregunta genérica de {area} para la medición de aptitud."
            respuesta = "c" # Asignar una respuesta por defecto

        PREGUNTAS_GATB.append({
            "id": current_id, 
            "area": area,
            "code": code,
            "pregunta": pregunta, 
            "opciones": opciones, 
            "respuesta_correcta": respuesta
        })
        current_id += 1

df_preguntas = pd.DataFrame(PREGUNTAS_GATB)
N_TOTAL_PREGUNTAS = len(df_preguntas)


# --- 3. FUNCIONES DE ESTADO Y NAVEGACIÓN ---

# Inicialización de Session State
if 'stage' not in st.session_state: st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'area_actual_index' not in st.session_state: st.session_state.area_actual_index = 0

def set_stage(new_stage):
    """Cambia la etapa de la aplicación y fuerza el scroll al inicio."""
    st.session_state.stage = new_stage
    js_scroll_to_top() # Forzar scroll

def siguiente_area():
    """Avanza a la siguiente área o finaliza el test."""
    # 1. Guardar la respuesta actual (ya manejado por el radio en tiempo real, pero es buena práctica refrescar)
    
    # 2. Navegar
    if st.session_state.area_actual_index < len(AREAS) - 1:
        st.session_state.area_actual_index += 1
        set_stage('test_activo')
    else:
        # Última área, calcular y mostrar resultados
        calcular_resultados()
        set_stage('resultados')

def calcular_resultados():
    """Calcula y almacena los resultados finales."""
    resultados_data = []
    
    for area in AREAS:
        preguntas_area = df_preguntas[df_preguntas['area'] == area]
        total_area = len(preguntas_area)
        aciertos_area = 0

        for index, row in preguntas_area.iterrows():
            pregunta_id = row['id']
            respuesta_usuario = st.session_state.respuestas.get(pregunta_id)
            
            if respuesta_usuario == row['respuesta_correcta']:
                aciertos_area += 1
        
        # Cálculo de métricas
        porcentaje = (aciertos_area / total_area) * 100 if total_area > 0 else 0
        percentil, clasificacion_texto = clasificar_percentil(porcentaje)
        
        resultados_data.append({
            "Área": area,
            "Código": APTITUDES_MAP[area]["code"],
            "Puntuación Bruta": aciertos_area,
            "Máxima Puntuación": total_area,
            "Porcentaje (%)": f"{porcentaje:.1f}%",
            "Percentil (Simulado)": percentil,
            "Clasificación": clasificacion_texto,
            "Color": APTITUDES_MAP[area]["color"]
        })
    
    st.session_state.resultados_df = pd.DataFrame(resultados_data)


# --- 4. VISTAS DE STREAMLIT ---

def vista_inicio():
    """Muestra la página de inicio e instrucciones."""
    st.title("🧠 Batería de Aptitudes Generales – GATB Profesional")
    st.header("Evaluación Estructurada de 12 Factores Aptitudinales")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        st.info(f"""
        **🎯 Objetivo:** Medir 12 factores clave de aptitud, siguiendo la estructura del General Aptitude Test Battery (GATB).
        
        **📋 Estructura del Test:**
        - **Total de Secciones:** **{len(AREAS)}**
        - **Preguntas por Sección:** **{N_PREGUNTAS_POR_AREA}**
        - **Total de Ítems:** **{N_TOTAL_PREGUNTAS}**
        
        **📝 Instrucciones:**
        1.  Responda cada pregunta seleccionando la opción que considere correcta.
        2.  Su respuesta se guardará automáticamente.
        3.  Use el botón "Siguiente Sección" para avanzar.
        """)
    
    with col2:
        st.subheader("Simulación Profesional")
        st.warning("⚠️ **Nota:** Esta es una simulación de la estructura del GATB. Las clasificaciones (Percentil) son **ilustrativas** y no representan las tablas de estandarización reales del test.")
        if st.button("🚀 Iniciar Evaluación", type="primary", use_container_width=True):
            st.session_state.area_actual_index = 0
            set_stage('test_activo')

    st.markdown("---")
    st.subheader("Resumen de Áreas de Aptitud")
    
    # Mostrar las áreas en columnas para una vista limpia
    cols = st.columns(3)
    for i, area in enumerate(AREAS):
        col = cols[i % 3]
        col.markdown(f"**{APTITUDES_MAP[area]['code']} - {area}**")

def vista_test_activo():
    """Muestra la sección de preguntas del área actual."""
    
    js_scroll_to_top() # Forzar scroll al cargar la nueva área

    area_actual = AREAS[st.session_state.area_actual_index]
    total_areas = len(AREAS)
    current_area_index = st.session_state.area_actual_index
    progress_percentage = (current_area_index + 1) / total_areas

    # --- Cabecera y Barra de Progreso ---
    st.title(f"Sección {current_area_index + 1} de {total_areas}: {area_actual}")
    st.progress(progress_percentage, text=f"Progreso General: **{area_actual}** ({APTITUDES_MAP[area_actual]['code']})")
    st.markdown("---")
    
    # Filtrar las preguntas para el área actual
    preguntas_area = df_preguntas[df_preguntas['area'] == area_actual]
    
    # Contenedor para las preguntas
    with st.container(border=True):
        st.subheader(f"Instrucciones: {area_actual}")
        
        q_num = 1 # Contador local para la pregunta dentro de la sección
        for index, row in preguntas_area.iterrows():
            pregunta_id = row['id']
            
            # Crear la lista de opciones para el radio
            opciones_radio = [f"{k}) {v}" for k, v in row['opciones'].items()]
            
            # Recuperar la respuesta anterior si existe
            default_value_key = st.session_state.respuestas.get(pregunta_id)
            
            # Determinar el índice de la respuesta guardada
            try:
                # Buscamos la clave (a, b, c, d) de la respuesta guardada
                keys_list = list(row['opciones'].keys())
                default_index = keys_list.index(default_value_key)
            except (ValueError, AttributeError):
                default_index = None # No seleccionada

            # Contenedor para cada pregunta con un borde visual
            with st.container(border=True):
                # Determinar si la pregunta requiere imagen
                pregunta_texto = row['pregunta']
                
                # Muestra el número de pregunta local y el texto de la pregunta
                st.markdown(f"**Pregunta {q_num}.**") 
                
                if '[Image of' in pregunta_texto:
                    image_tag_start = pregunta_texto.find('[Image of')
                    image_tag_end = pregunta_texto.find(']', image_tag_start)
                    image_tag = pregunta_texto[image_tag_start:image_tag_end+1]
                    
                    st.markdown(pregunta_texto.replace(image_tag, ''))
                    st.markdown(f"*(**ESTÍMULO VISUAL REQUERIDO**)*")
                    st.markdown(image_tag) # Mostrar el placeholder de la imagen
                else:
                    st.markdown(pregunta_texto)

                # Callback para guardar la respuesta inmediatamente al seleccionar
                def on_radio_change(q_id, correct_key):
                    selected_option_full = st.session_state[f'q_{q_id}']
                    # Extraer solo la clave (a, b, c, d)
                    selected_key = selected_option_full.split(')')[0]
                    st.session_state.respuestas[q_id] = selected_key
                
                # Radio Button
                st.radio(
                    f"Respuesta {row['code']}-{q_num}:", 
                    opciones_radio, 
                    key=f'q_{pregunta_id}', 
                    index=default_index,
                    on_change=on_radio_change,
                    args=(pregunta_id, row['respuesta_correcta'])
                )
            
            q_num += 1 # Incrementar contador local
    
    st.markdown("---")

    # Botón para pasar a la siguiente sección / finalizar
    if st.session_state.area_actual_index < len(AREAS) - 1:
        next_area_name = AREAS[st.session_state.area_actual_index + 1]
        submit_label = f"➡️ Siguiente Sección: {next_area_name}"
    else:
        submit_label = "✅ Finalizar Test y Generar Informe"

    st.button(submit_label, type="primary", on_click=siguiente_area, use_container_width=True)

def vista_resultados():
    """Muestra el informe de resultados profesional sin gráficos, con detalles extendidos."""
    js_scroll_to_top() # Forzar scroll al cargar resultados

    st.title("📄 Informe de Resultados GATB Profesional")
    st.header("Perfil Aptitudinal Detallado")
    
    df_resultados = st.session_state.resultados_df

    st.markdown("---")
    
    # --- 1. Análisis Consolidado ---
    st.subheader("Sumario Ejecutivo")
    
    df_resultados['Percentil Num'] = df_resultados['Percentil (Simulado)'].astype(int)
    mejor_area = df_resultados.loc[df_resultados['Percentil Num'].idxmax()]
    peor_area = df_resultados.loc[df_resultados['Percentil Num'].idxmin()]

    col_mejor, col_peor = st.columns(2)

    with col_mejor:
        st.success(f"""
        **🚀 Mayor Fortaleza:** **{mejor_area['Área']}** ({mejor_area['Código']})
        - **Clasificación:** {mejor_area['Clasificación']}
        - **Percentil:** {mejor_area['Percentil (Simulado)']}
        - *Recomendación: Excelente potencial para roles que exijan esta aptitud.*
        """)
    
    with col_peor:
        st.error(f"""
        **🚧 Área de Oportunidad:** **{peor_area['Área']}** ({peor_area['Código']})
        - **Clasificación:** {peor_area['Clasificación']}
        - **Percentil:** {peor_area['Percentil (Simulado)']}
        - *Recomendación: Se sugiere entrenamiento o asignación a roles menos dependientes de esta habilidad.*
        """)

    st.markdown("---")
    
    # --- 2. Tabla de Resultados Detallada (Profesional) ---
    st.subheader("Tabla de Puntuaciones y Clasificación")
    
    # Estilos de celda para la clasificación
    def highlight_classification(s):
        if 'Muy Alto' in s['Clasificación'] or 'Alto' in s['Clasificación']:
            return ['background-color: #d4edda'] * len(s) # Verde claro
        elif 'Bajo' in s['Clasificación'] or 'Muy Bajo' in s['Clasificación']:
            return ['background-color: #f8d7da'] * len(s) # Rojo claro
        else:
            return [''] * len(s)

    df_display = df_resultados.copy()
    df_display = df_display[['Código', 'Área', 'Puntuación Bruta', 'Máxima Puntuación', 'Porcentaje (%)', 'Percentil (Simulado)', 'Clasificación']]
    
    st.dataframe(
        df_display.style.apply(highlight_classification, axis=1),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Puntuación Bruta": st.column_config.NumberColumn("Puntaje Bruto", format="%d"),
            "Máxima Puntuación": st.column_config.NumberColumn("Máx. Puntuación", format="%d"),
        }
    )
    
    st.markdown("---")
    
    # --- 3. Interpretación Detallada por Aptitud (Extensa y Animada) ---
    st.subheader("Interpretación Detallada por Aptitud")
    st.info("A continuación, se presenta el análisis de cada aptitud, clasificando su potencial y ofreciendo recomendaciones basadas en el percentil obtenido (Simulado).")
    
    for index, row in df_resultados.sort_values(by='Percentil Num', ascending=False).iterrows():
        interpretacion_html = obtener_interpretacion(
            row['Percentil Num'],
            row['Código'],
            row['Área']
        )
        # Mostrar la interpretación con formato HTML/CSS (animación visual)
        st.markdown(interpretacion_html, unsafe_allow_html=True)
        
    st.markdown("---")

    with st.expander("Glosario de Resultados y Clasificación", expanded=False):
        st.markdown(f"""
        - **Puntuación Bruta:** Número de aciertos en un área (Máx. {N_PREGUNTAS_POR_AREA}).
        - **Porcentaje (%):** Relación de aciertos vs. total de preguntas.
        - **Percentil (Simulado):** Indica el porcentaje de la población de referencia que obtuvo una puntuación igual o inferior a la suya.
            - **Percentil 90+ (Muy Alto):** Superior al 90% de la población.
            - **Percentil 76-90 (Alto):** Superior al 75% de la población.
            - **Percentil 26-75 (Promedio):** Dentro de la media.
            - **Percentil 6-25 (Bajo):** Inferior a la media.
            - **Percentil 5- (Muy Bajo):** Significativamente inferior a la media.
        """)

    st.markdown("---")
    
    if st.button("⏪ Realizar Nueva Evaluación", type="secondary"):
        st.session_state.respuestas = {}
        st.session_state.area_actual_index = 0
        set_stage('inicio')


# --- 5. CONTROL DEL FLUJO PRINCIPAL ---

if st.session_state.stage == 'inicio':
    vista_inicio()
elif st.session_state.stage == 'test_activo':
    vista_test_activo()
elif st.session_state.stage == 'resultados':
    vista_resultados()

# --- 6. FOOTER Y ACERCA DE ---
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: small; color: grey;'>Desarrollado por José Ignacio Taj-Taj</p>", unsafe_allow_html=True)
