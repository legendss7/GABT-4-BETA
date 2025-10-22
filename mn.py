import streamlit as st
import pandas as pd
import numpy as np

# --- 1. DEFINICIÓN DEL TEST (Datos en código Python) ---
# Adaptación del GATB con 12 subtests (2 preguntas por área para una muestra funcional).
# La versión completa del GATB incluye entre 300 y 400 ítems, distribuidos en estas 12 áreas.

PREGUNTAS_GATB = [
    # G: Razonamiento General (Lógica, Inducción/Deducción)
    {"id": 1, "area": "Razonamiento General (G)", "pregunta": "Si todos los A son B y ningún C es A, ¿qué se puede concluir?", "opciones": {"a": "Ningún B es C", "b": "Algunos B son C", "c": "Algunos B no son C", "d": "Todos los C son B"}, "respuesta_correcta": "c"},
    {"id": 2, "area": "Razonamiento General (G)", "pregunta": "En un grupo de 5 personas, A es más rápido que B, C es más lento que D, y D es más lento que B. ¿Quién es el más lento?", "opciones": {"a": "A", "b": "B", "c": "C", "d": "D"}, "respuesta_correcta": "c"},

    # V: Razonamiento Verbal (Comprensión de vocabulario)
    {"id": 3, "area": "Razonamiento Verbal (V)", "pregunta": "¿Cuál es el antónimo de 'Inerte'?", "opciones": {"a": "Estático", "b": "Quieto", "c": "Animado", "d": "Pasivo"}, "respuesta_correcta": "c"},
    {"id": 4, "area": "Razonamiento Verbal (V)", "pregunta": "Analogía: Faro es a Navegación como Brújula es a:", "opciones": {"a": "Tierra", "b": "Polo", "c": "Orientación", "d": "Mapa"}, "respuesta_correcta": "c"},

    # N: Razonamiento Numérico (Series y operaciones lógicas)
    {"id": 5, "area": "Razonamiento Numérico (N)", "pregunta": "Serie: 3, 6, 12, 24, ¿Cuál sigue?", "opciones": {"a": "30", "b": "36", "c": "48", "d": "60"}, "respuesta_correcta": "c"},
    {"id": 6, "area": "Razonamiento Numérico (N)", "pregunta": "Si un producto cuesta $150 y tiene un 20% de descuento, ¿cuál es el precio final?", "opciones": {"a": "$120", "b": "$130", "c": "$140", "d": "$100"}, "respuesta_correcta": "a"},

    # S: Razonamiento Espacial (Visualización de figuras)
    {"id": 7, "area": "Razonamiento Espacial (S)", "pregunta": "Un cubo tiene una cara azul y la opuesta roja. Si la cara superior es azul, ¿qué color tiene la cara inferior?", "opciones": {"a": "Azul", "b": "Rojo", "c": "Verde", "d": "Amarillo"}, "respuesta_correcta": "b"},
    {"id": 8, "area": "Razonamiento Espacial (S)", "pregunta": "Si doblas un papel por la mitad y cortas una esquina, ¿cuántos agujeros tendrá al desdoblarlo?", "opciones": {"a": "1", "b": "2", "c": "4", "d": "Ninguno"}, "respuesta_correcta": "b"},

    # P: Velocidad Perceptiva (Detección rápida de similitudes)
    {"id": 9, "area": "Velocidad Perceptiva (P)", "pregunta": "¿Qué par es diferente al resto? (A) 8295 / 8295 (B) 4710 / 4711 (C) 5050 / 5050", "opciones": {"a": "Par A", "b": "Par B", "c": "Par C", "d": "Todos son iguales"}, "respuesta_correcta": "b"},
    {"id": 10, "area": "Velocidad Perceptiva (P)", "pregunta": "Encuentre el error en la secuencia: ABCCBA / ABCCAB", "opciones": {"a": "Aparece una 'D'", "b": "La primera secuencia es simétrica", "c": "La segunda secuencia es diferente al final", "d": "No hay errores"}, "respuesta_correcta": "c"},

    # Q: Precisión Manual (Analogía de la coordinación fina)
    {"id": 11, "area": "Precisión Manual (Q)", "pregunta": "La precisión de un cirujano con el bisturí es análoga a la precisión de un:", "opciones": {"a": "Pintor de brocha gorda", "b": "Escultor de mármol", "c": "Mecánico de motores grandes", "d": "Joyero engastando una piedra"}, "respuesta_correcta": "d"},
    {"id": 12, "area": "Precisión Manual (Q)", "pregunta": "Al coser un botón, ¿cuál habilidad es más crítica?", "opciones": {"a": "Fuerza física", "b": "Visión periférica", "c": "Coordinación ojo-mano", "d": "Resistencia"}, "respuesta_correcta": "c"},

    # K: Coordinación Manual (Analogía de la destreza de movimiento)
    {"id": 13, "area": "Coordinación Manual (K)", "pregunta": "Para ensamblar una pieza compleja, ¿cuál es el orden correcto de acciones?", "opciones": {"a": "Inspeccionar, Armar, Ajustar", "b": "Armar, Ajustar, Inspeccionar", "c": "Ajustar, Inspeccionar, Armar", "d": "Armar, Inspeccionar, Ajustar"}, "respuesta_correcta": "a"},
    {"id": 14, "area": "Coordinación Manual (K)", "pregunta": "El acto de teclear a alta velocidad se basa principalmente en:", "opciones": {"a": "Memoria espacial", "b": "Velocidad de reacción", "c": "Destreza digital", "d": "Razonamiento abstracto"}, "respuesta_correcta": "c"},

    # A: Atención Concentrada (Detección de detalles bajo distracción)
    {"id": 15, "area": "Atención Concentrada (A)", "pregunta": "Encuentre la palabra que NO se repite en el texto: 'El costo del producto se calcula sumando el costo, el costo de transporte y el costo de almacenamiento.'", "opciones": {"a": "costo", "b": "producto", "c": "sumando", "d": "almacenamiento"}, "respuesta_correcta": "b"},
    {"id": 16, "area": "Atención Concentrada (A)", "pregunta": "¿Cuántos errores hay en la siguiente lista de precios? A12.99, B$15, C14.90$, D$1.0", "opciones": {"a": "1", "b": "2", "c": "3", "d": "4"}, "respuesta_correcta": "b"}, # Errores: A12.99 (falta $), C14.90$ (signo al final)

    # M: Razonamiento Mecánico (Principios de física simple)
    {"id": 17, "area": "Razonamiento Mecánico (M)", "pregunta": "Si se aumenta el diámetro de una polea, ¿qué sucede con la fuerza necesaria para levantar una carga?", "opciones": {"a": "Aumenta", "b": "Disminuye", "c": "Se mantiene igual", "d": "Depende de la velocidad"}, "respuesta_correcta": "b"},
    {"id": 18, "area": "Razonamiento Mecánico (M)", "pregunta": "En un balancín, si el peso está cerca del centro, ¿qué sucede con el esfuerzo necesario para levantarlo?", "opciones": {"a": "Se necesita más esfuerzo", "b": "Se necesita menos esfuerzo", "c": "El esfuerzo no cambia", "d": "Depende del largo del balancín"}, "respuesta_correcta": "b"},

    # R: Razonamiento Abstracto (Secuencias y matrices no verbales)
    {"id": 19, "area": "Razonamiento Abstracto (R)", "pregunta": "Si un patrón es: (Línea, Doble línea, Círculo, Línea), ¿qué sigue?", "opciones": {"a": "Doble línea", "b": "Círculo", "c": "Línea", "d": "Triple línea"}, "respuesta_correcta": "a"},
    {"id": 20, "area": "Razonamiento Abstracto (R)", "pregunta": "La figura 1 tiene 4 lados. La figura 2 tiene 5 lados. ¿Cuántos lados tendrá la figura 3 si el patrón continúa?", "opciones": {"a": "4", "b": "5", "c": "6", "d": "7"}, "respuesta_correcta": "c"},

    # C: Razonamiento Clerical (Clasificación, archivo, organización)
    {"id": 21, "area": "Razonamiento Clerical (C)", "pregunta": "¿Qué nombre debe ir primero en orden alfabético? (A) López, Juan (B) Landa, José (C) Lagos, Pedro (D) Lara, Miguel", "opciones": {"a": "(A) López, Juan", "b": "(B) Landa, José", "c": "(C) Lagos, Pedro", "d": "(D) Lara, Miguel"}, "respuesta_correcta": "b"},
    {"id": 22, "area": "Razonamiento Clerical (C)", "pregunta": "¿Cuál de las siguientes series está mal archivada? (A) Enero, Febrero, Marzo (B) Pez, Pato, Perro (C) 1, 3, 2, 4 (D) Norte, Sur, Este", "opciones": {"a": "Serie A", "b": "Serie B", "c": "Serie C", "d": "Serie D"}, "respuesta_correcta": "c"},

    # T: Razonamiento Técnico (Conocimiento práctico)
    {"id": 23, "area": "Razonamiento Técnico (T)", "pregunta": "¿Qué herramienta se usa para medir ángulos con precisión?", "opciones": {"a": "Martillo", "b": "Destornillador", "c": "Escuadra", "d": "Transportador"}, "respuesta_correcta": "d"},
    {"id": 24, "area": "Razonamiento Técnico (T)", "pregunta": "¿Cuál principio permite a un flotador mantenerse a flote en el agua?", "opciones": {"a": "Gravedad", "b": "Rozamiento", "c": "Empuje de Arquímedes", "d": "Tensión superficial"}, "respuesta_correcta": "c"},
]

# Convertir la lista de preguntas a un DataFrame de Pandas para fácil manejo
df_preguntas = pd.DataFrame(PREGUNTAS_GATB)
AREAS = df_preguntas['area'].unique().tolist()
N_TOTAL_PREGUNTAS = len(df_preguntas)

# --- 2. CONFIGURACIÓN INICIAL DE STREAMLIT ---
st.set_page_config(layout="centered", page_title="Batería de Aptitudes Generales – GATB Digital")

# Inicialización de Session State para gestión del estado de la aplicación
if 'stage' not in st.session_state:
    st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {}
if 'area_actual_index' not in st.session_state:
    st.session_state.area_actual_index = 0

# --- 3. LÓGICA DE NAVEGACIÓN Y CÁLCULO ---

def set_stage(new_stage):
    """Cambia la etapa de la aplicación."""
    st.session_state.stage = new_stage

def siguiente_area():
    """Avanza a la siguiente área del test."""
    if st.session_state.area_actual_index < len(AREAS) - 1:
        # Corregido: Usar st.session_state
        st.session_state.area_actual_index += 1
    else:
        # Si es la última área, pasa a resultados
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
        
        porcentaje = (aciertos_area / total_area) * 100 if total_area > 0 else 0
        
        # Clasificación
        if porcentaje < 40:
            clasificacion = "Bajo"
        elif 40 <= porcentaje <= 69:
            clasificacion = "Promedio"
        else:
            clasificacion = "Alto"

        resultados_data.append({
            "Área": area,
            "Aciertos": aciertos_area,
            "Total": total_area,
            "Porcentaje (%)": f"{porcentaje:.1f}",
            "Nivel": clasificacion
        })
    
    st.session_state.resultados_df = pd.DataFrame(resultados_data)


# --- 4. VISTAS DE STREAMLIT ---

def vista_inicio():
    """Muestra la página de inicio e instrucciones."""
    st.title("Batería de Aptitudes Generales – GATB Digital")
    st.markdown("## Evaluación de Aptitudes Cognitivas y Laborales")
    
    st.info(f"""
    **Instrucciones Generales:**
    Este test consta de **{len(AREAS)} áreas** que miden distintas aptitudes cruciales para el desempeño laboral y cognitivo. 
    El GATB original incluye entre 300 y 400 ítems con una duración aproximada de **2 a 3 horas**. Esta versión es una **muestra funcional**.
    Se recomienda responder con honestidad y la máxima atención.
    """)
    
    st.subheader(f"Estructura del Test (Muestra Funcional de {N_TOTAL_PREGUNTAS} preguntas)")
    
    # Tabla con las áreas y el número de preguntas (basado en la muestra actual)
    df_resumen = df_preguntas.groupby('area').size().reset_index(name='Nº de preguntas')
    st.dataframe(df_resumen.rename(columns={'area': 'Área de Aptitud'}).set_index('Área de Aptitud'), use_container_width=True)

    if st.button("Comenzar Test", type="primary"):
        st.session_state.area_actual_index = 0
        set_stage('test_activo')

def vista_test_activo():
    """Muestra la sección de preguntas del área actual."""
    area_actual = AREAS[st.session_state.area_actual_index]
    
    st.header(f"Sección {st.session_state.area_actual_index + 1} de {len(AREAS)}: {area_actual}")
    st.markdown("---")
    
    # Filtrar las preguntas para el área actual
    preguntas_area = df_preguntas[df_preguntas['area'] == area_actual]

    # Se ha eliminado el wrapper st.form para evitar el error de callback.
    # Las respuestas se guardan en el estado (st.session_state) inmediatamente usando on_change.
    for index, row in preguntas_area.iterrows():
        pregunta_id = row['id']
        
        # Crear la lista de opciones para el radio
        opciones_radio = [f"{k}) {v}" for k, v in row['opciones'].items()]
        
        # Recuperar la respuesta anterior si existe
        default_value = st.session_state.respuestas.get(pregunta_id)
        
        # Determinar el índice de la respuesta guardada
        try:
            # Buscamos la clave (a, b, c, d) de la respuesta guardada
            default_index = list(row['opciones'].keys()).index(default_value)
        except (ValueError, AttributeError):
            default_index = -1 # No seleccionada o respuesta inválida

        st.markdown(f"**{row['id']}. {row['pregunta']}**")
        
        # Callback para guardar la respuesta inmediatamente al seleccionar
        def on_radio_change(q_id, opciones):
            selected_option_full = st.session_state[f'q_{q_id}']
            # Extraer solo la clave (a, b, c, d)
            selected_key = selected_option_full.split(')')[0]
            st.session_state.respuestas[q_id] = selected_key
        
        # Si no hay respuesta anterior, el índice es None para que no seleccione nada
        index_to_use = default_index if default_index != -1 else None

        st.radio(
            "Selecciona tu respuesta:", 
            opciones_radio, 
            key=f'q_{pregunta_id}', 
            index=index_to_use,
            on_change=on_radio_change,
            args=(pregunta_id, row['opciones'])
        )
        st.markdown("---")
    
    # Botón para pasar a la siguiente sección / finalizar
    if st.session_state.area_actual_index < len(AREAS) - 1:
        next_area_name = AREAS[st.session_state.area_actual_index + 1].split('(')[0].strip()
        submit_label = f"Continuar a {next_area_name}"
        callback_func = siguiente_area
    else:
        submit_label = "Finalizar Test y Ver Resultados"
        callback_func = siguiente_area

    # Usamos st.button con on_click para avanzar la navegación
    st.button(submit_label, type="primary", on_click=callback_func)


def vista_resultados():
    """Muestra la tabla de resultados y la clasificación."""
    st.title("✅ Resultados de la Batería GATB Digital")
    st.markdown("---")
    
    df_resultados = st.session_state.resultados_df

    st.subheader("Puntuaciones Detalladas por Área de Aptitud")
    st.dataframe(df_resultados.set_index('Área'), use_container_width=True)
    
    st.markdown("### Interpretación de Niveles:")
    st.markdown("- **Alto (70-100%):** Aptitud superior al promedio, indica potencial destacado en el área.")
    st.markdown("- **Promedio (40-69%):** Aptitud adecuada para tareas comunes, indica un buen desempeño general.")
    st.markdown("- **Bajo (0-39%):** Aptitud que requiere desarrollo o entrenamiento adicional.")
    
    st.markdown("---")
    st.subheader("Análisis General")
    
    # Encontrar la aptitud más alta
    df_resultados['Porcentaje (%)'] = pd.to_numeric(df_resultados['Porcentaje (%)'])
    mejor_area = df_resultados.loc[df_resultados['Porcentaje (%)'].idxmax()]
    
    st.success(f"""
    **Tu Aptitud Más Destacada es:** **{mejor_area['Área']}** con un **{mejor_area['Porcentaje (%)']}%** de aciertos.
    """)
    
    st.warning("¡Importante! Este es un test de muestra. Para una evaluación laboral o clínica formal, siempre consulte a un psicólogo profesional.")

    if st.button("Volver al Inicio", type="secondary"):
        st.session_state.respuestas = {}
        # Corregido: Usar st.session_state
        st.session_state.area_actual_index = 0
        set_stage('inicio')


# --- 5. CONTROL DEL FLUJO PRINCIPAL ---

# Corregido: Usar st.session_state
if st.session_state.stage == 'inicio':
    vista_inicio()
# Corregido: Usar st.session_state
elif st.session_state.stage == 'test_activo':
    vista_test_activo()
# Corregido: Usar st.session_state
elif st.session_state.stage == 'resultados':
    vista_resultados()

# --- 6. FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: small; color: grey;'>TEST CREADO POR JOSÉ IGNACIO TAJ-TAJ</p>", unsafe_allow_html=True)
