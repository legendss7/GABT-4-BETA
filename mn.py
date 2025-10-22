import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px # Importación necesaria para los gráficos profesionales
import plotly.graph_objects as go # Para el gráfico de Radar
import streamlit.components.v1 as components # Necesario para la función de scroll

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
    """Clasifica el percentil en rangos."""
    if porcentaje >= 90: return 96, "Superior (90-99)"
    elif porcentaje >= 80: return 88, "Alto (80-89)"
    elif porcentaje >= 60: return 70, "Promedio Alto (60-79)"
    elif porcentaje >= 40: return 50, "Promedio (40-59)"
    elif porcentaje >= 20: return 30, "Promedio Bajo (20-39)"
    elif porcentaje >= 10: return 15, "Bajo (10-19)"
    else: return 5, "Muy Bajo (0-9)"

def calificar_global(avg_percentil):
    """Genera la calificación ejecutiva."""
    if avg_percentil >= 85: return "Potencial Ejecutivo 🌟", "El perfil indica un potencial excepcionalmente alto y equilibrado para roles directivos, estratégicos y de alta complejidad.", "#008000"
    elif avg_percentil >= 65: return "Nivel Profesional Avanzado 🏆", "El perfil es sólido, con fortalezas claras y un buen balance aptitudinal. Excelente para roles técnicos especializados, de gestión de proyectos y consultoría.", "#4682b4"
    elif avg_percentil >= 40: return "Perfil Competitivo 💼", "El perfil se sitúa en el promedio superior, demostrando suficiencia en todas las áreas. Apto para la mayoría de roles operativos y de coordinación.", "#ff8c00"
    else: return "Período de Desarrollo 🛠️", "El perfil requiere un período de enfoque intensivo en el desarrollo de aptitudes clave. Se recomienda comenzar con roles de soporte y entrenamiento continuo.", "#dc143c"

def generate_gatb_questions():
    """Genera preguntas simuladas originales y sin derechos de autor."""
    
    # Preguntas detalladas (12 por área) y su respuesta correcta esperada (Simulada: 'a')
    detailed_questions = {
        "Razonamiento General": [
            "1. (Silogismo) Todos los abogados son elocuentes. Ningún matemático es abogado. ¿Qué se deduce?", 
            "2. ¿Cuál es la palabra que NO encaja en la serie: Lápiz, Pincel, Borrador, Pluma, Tinta?", 
            "3. Complete la analogía: Semilla es a Árbol como Célula es a:", 
            "4. Si 'Todo A es B' y 'Algún C es A', entonces 'Algún C es B'. ¿Verdadero o Falso?", 
            "5. Encuentre el patrón en la secuencia: 3, 9, 27, 81, ...",
            "6. Si la temperatura subió 5°C y luego bajó 8°C, el cambio neto es:",
            "7. Si un cliente compra 3 productos por $15, ¿cuánto cuestan 7 productos iguales?",
            "8. ¿Qué conclusión es la más lógica dada la siguiente premisa: 'Solo los peces viven bajo el agua'?",
            "9. Si un evento ocurre antes que el evento B, y B ocurre después del evento C, ¿cuál es el orden posible?",
            "10. ¿Cuál es el número primo consecutivo al 19?",
            "11. Si la mitad de X es 10, ¿cuánto es el doble de X?",
            "12. Si una persona es hija única, su padre tiene un hermano. ¿Qué relación tiene ese hermano con la persona?"
        ],
        "Razonamiento Verbal": [
            "1. Sinónimo más cercano de 'Recalcitrante':", "2. Antónimo de 'Lánguido':", "3. ¿Qué palabra se usa para describir una expresión breve y concisa?", 
            "4. El significado de la frase 'Subir el telón' es:", "5. 'Vituperio' se relaciona mejor con:", "6. ¿Cuál es el adjetivo de 'Intuir'?", 
            "7. Complete: La ____ del paisaje dejó a todos sin aliento.", "8. Encuentre el error gramatical en: 'Ella y yo fuimos al cine ayer'.", 
            "9. ¿Qué palabra NO es un sinónimo de 'Diligencia'?", "10. ¿Cuál es el prefijo que significa 'contra'?", 
            "11. La palabra 'Efemérides' se refiere a:", "12. ¿Qué significa la expresión 'Tocar madera' en el contexto cultural?"
        ],
        "Razonamiento Numérico": [
            "1. Resuelva: (1/3) + (1/6) = ", "2. Calcule el 25% de 360.", "3. Si el precio baja 10% y luego sube 5%, ¿cuál es el cambio neto?", 
            "4. Si un auto recorre 180 km en 2 horas, ¿cuál es su velocidad promedio en km/h?", "5. Resuelva: 4! / 2! =", 
            "6. Si 2x - 5 = 15, ¿cuál es el valor de x?", "7. Un producto cuesta $80. Se ofrece un descuento del 15%. ¿Precio final?", 
            "8. ¿Cuál es el número siguiente en la serie: 1, 4, 9, 16, ...?", "9. ¿Cuántos múltiplos de 3 hay entre 1 y 15?", 
            "10. Si la hipotenusa de un triángulo rectángulo mide 5 y un cateto 3, ¿cuánto mide el otro cateto?", "11. Si 4 impresoras imprimen 100 páginas en 5 minutos, ¿cuánto tardan 8 impresoras?", 
            "12. ¿Cuál es el volumen de un cubo cuyo lado mide 3 cm?"
        ],
        "Razonamiento Espacial": [
            "1. Identifique la vista lateral izquierda de esta figura geométrica (simulada).", "2. ¿Cuál de estos patrones planos puede formar un cilindro al doblarse?", 
            "3. Elija el objeto que proyecta la sombra de un círculo y un cuadrado (simulada).", "4. ¿Qué pieza es necesaria para completar la vista en planta de este mecanismo?", 
            "5. Si la figura A se fusiona con la figura B, ¿qué forma final obtienen?", "6. Indique la pieza que falta para completar la simetría axial de la imagen.", 
            "7. ¿Cuántos cubos están tocando el suelo en la pila tridimensional?", "8. Si esta letra 'F' se refleja en un espejo vertical, ¿cuál es el resultado?", 
            "9. ¿Cuál es el resultado de hacer dos perforaciones en el papel doblado por la mitad y luego desdoblarlo?", "10. Encuentre el ángulo que se forma entre las manecillas del reloj a las 10:00.", 
            "11. ¿Qué imagen completa la serie de transformaciones espaciales?", "12. Si se invierte horizontalmente la figura, ¿cuál es la nueva orientación de sus componentes?"
        ],
        "Velocidad Perceptiva": [
            "1. ¿Cuál de los siguientes códigos es IDÉNTICO a C5B9A-J10?", "2. Compare las parejas: 99M45/99N45. ¿Son iguales o diferentes?", 
            "3. ¿Cuál dirección postal coincide exactamente: 'Calle Falsa 123 B, Ciudad A'?", "4. Busque el error en la secuencia de números: 101102103105...", 
            "5. Encuentre el código que NO es alfanumérico: A23X, 45B7, 12345, Y9Z0.", "6. ¿Cuántas 'O' mayúsculas hay en el siguiente párrafo corto?", 
            "7. ¿Es 'Distribuidora Central' igual a 'Distr. Central Ltda.'?", "8. Encuentre el listado que contiene un error de transcripción de nombre.", 
            "9. ¿Qué número está repetido en la lista: 1, 2, 3, 5, 2, 7, 9?", "10. Compare las siguientes cifras de inventario: 1.450.000 y 1450000.", 
            "11. Localice la única 's' minúscula que está en cursiva en el texto.", "12. ¿Cuál de estas palabras se lee igual de derecha a izquierda?"
        ],
        "Precisión Manual": [
            "1. (Simulado) Identifique el punto con el menor margen de error con respecto al objetivo.", "2. (Simulado) Seleccione el trazo de línea recta más consistente y fino.", 
            "3. (Simulado) ¿Cuál círculo se acerca más a ser una figura perfecta?", "4. (Simulado) Marque la casilla más pequeña con una X dentro de los bordes.", 
            "5. (Simulado) ¿Cuál de las siguientes uniones parece la más exacta sin solapamientos?", "6. (Simulado) Mida el segmento de línea que tiene una longitud de 4.25 cm.", 
            "7. (Simulado) Elija el diagrama donde el componente electrónico está perfectamente centrado.", "8. (Simulado) En la rejilla, localice el cruce de línea más preciso.", 
            "9. (Simulado) ¿Cuál de estos iconos fue dibujado con el detalle más minucioso?", "10. (Simulado) Seleccione el área de enfoque donde los píxeles son más definidos.", 
            "11. (Simulado) Identifique el elemento de la imagen que está ligeramente desplazado del centro.", "12. (Simulado) ¿Cuál de estas herramientas simula mayor control de movimiento fino?"
        ],
        "Coordinación Manual": [
            "1. (Simulado) ¿Cuál es el patrón de movimiento necesario para seguir esta línea curva continua?", "2. (Simulado) ¿Qué combinación de controles (Joystick y Botón) produce la acción de salto?", 
            "3. (Simulado) Si gira la perilla izquierda y presiona el pedal derecho, ¿cuál es el resultado esperado en el simulador?", "4. (Simulado) Muestre la trayectoria para interceptar un objeto en movimiento diagonal.", 
            "5. (Simulado) ¿Qué secuencia de pulsaciones genera un ritmo constante y rápido?", "6. (Simulado) Para balancear este objeto, ¿qué movimientos deben ser sincronizados?", 
            "7. (Simulado) Identifique el patrón rítmico que falta en la secuencia TIK-TAK-TOK, TIK-TAK-...", "8. (Simulado) La acción de golpear una pelota en movimiento requiere coordinación de:", 
            "9. (Simulado) ¿Qué actividad requiere la mayor coordinación de todo el cuerpo (global)?", "10. (Simulado) Si la mano guía un proceso y el pie activa un interruptor, ¿qué pasa si el pie es lento?", 
            "11. (Simulado) ¿Cuál es el orden cinemático correcto para levantar una carga con una grúa?", "12. (Simulado) Elija el patrón de movimiento que permite esquivar un obstáculo en movimiento."
        ],
        "Atención Concentrada": [
            "1. ¿Cuántas veces aparece el número '7' en la segunda línea de datos?", "2. Corrija el error de mayúsculas en el tercer párrafo.", 
            "3. Si 'A' vale 1, 'B' vale 2, etc., ¿cuál es el valor numérico de la palabra 'CONSCIENCIA'?", "4. Encuentre el número de factura oculto entre el texto legal.", 
            "5. ¿Cuál es la única palabra en **Negrita** en la primera frase?", "6. ¿Cuántos puntos y comas hay en el siguiente párrafo corto?", 
            "7. ¿Cuál es el único color que no se menciona en la lista de seis colores?", "8. Identifique la única discrepancia de precio entre el catálogo A y el catálogo B.", 
            "9. Si una persona puede procesar 5 datos/segundo, ¿cuántos datos procesa en 2 minutos?", "10. Encuentre el paso ilógico en el proceso de verificación de 4 etapas.", 
            "11. ¿Cuál es la palabra que está duplicada en el texto?", "12. ¿Cuántas figuras geométricas de borde discontinuo hay en la imagen?"
        ],
        "Razonamiento Mecánico": [
            "1. Si la rueda A gira a la derecha, ¿en qué dirección gira la rueda C, conectada por una correa cruzada?", "2. ¿Qué clase de palanca es un cascanueces (punto de apoyo, esfuerzo, resistencia)?", 
            "3. ¿Cuántas poleas fijas se necesitan para cambiar la dirección de la fuerza, sin aumentar la ventaja mecánica?", "4. Si un motor levanta una carga de 100 kg en 10 segundos, ¿cuál es su potencia (simulada)?", 
            "5. ¿Qué ley de Newton explica por qué un objeto en movimiento tiende a seguir moviéndose?", "6. Si reduce el diámetro de la cabeza de un tornillo, ¿cómo afecta la fuerza necesaria para girarlo?", 
            "7. ¿Cuál de estos es un ejemplo de energía cinética?", "8. Si aumenta la superficie de contacto al empujar, ¿aumenta o disminuye la presión?", 
            "9. ¿Qué sistema de frenado utiliza la fricción para detener el movimiento?", "10. ¿Qué se necesita para que una lámpara incandescente ilumine?", 
            "11. ¿Cuál es la unidad de medida del voltaje?", "12. ¿Qué principio explica el funcionamiento de un sifón?"
        ],
        "Razonamiento Abstracto": [
            "1. Complete la matriz de figuras 3x3 (la figura del centro debe ser la suma de la primera y la tercera).", "2. ¿Cuál figura es la quinta en la secuencia: Cuadrado, Triángulo, Círculo, Cuadrado, ...?", 
            "3. Identifique el patrón de cambio de color/sombreado en las figuras de la serie.", "4. ¿Cuál de las figuras es el 'intruso' que no sigue la regla de rotación/reflexión?", 
            "5. Si el patrón gira 180 grados y el color se invierte, ¿cuál es la figura resultante?", "6. ¿Qué figura es el resultado de superponer el conjunto A y el conjunto B?", 
            "7. Encuentre la relación: Triángulo Grande es a Triángulo Pequeño, como Círculo Rayado es a:", "8. Si la figura inicial tiene 3 puntos, y la siguiente 5 puntos, ¿cuántos tiene la tercera (progresión)?", 
            "9. Complete el cuadrado faltante basado en las transformaciones lógicas de filas y columnas.", "10. ¿Cuál figura se obtiene al sobreponer las dos imágenes y solo mantener las áreas comunes?", 
            "11. ¿Qué línea se mantiene fija mientras el resto rota?", "12. Si cada figura representa una operación matemática, ¿cuál es la expresión visual correcta?"
        ],
        "Razonamiento Clerical": [
            "1. Clasifique el documento 'Z-2025-MARK-05' según el código (M=Marketing, Z=Zona).", "2. ¿Cuál es el orden alfabético correcto de estos 4 nombres: Castro, Pérez, Díaz, Alonso?", 
            "3. Encuentre el número de teléfono incorrecto en la lista de contactos.", "4. ¿Cuántos errores de tipeo hay en la siguiente tabla (letras en campos numéricos)?", 
            "5. Archive el documento con fecha 15/01/2024 en el sistema 'LIFO' (Last In, First Out).", "6. ¿Cuál es la diferencia de stock entre el registro de entrada y el registro de salida?", 
            "7. Corrija el error en la transcripción de la fecha:", "8. ¿Qué documento tiene la mayor antigüedad (fecha de emisión)?", 
            "9. Calcule el número total de ítems en el rango A1 a B10 de la hoja de cálculo.", "10. Verifique si el código de producto 'XYZ-99' existe en ambas bases de datos.", 
            "11. ¿Qué letra falta en la serie: C, F, I, L, ...?", "12. ¿Cuál es el procedimiento correcto para la indexación de archivos digitales?"
        ],
        "Razonamiento Técnico": [
            "1. Identifique el diagrama de un circuito en serie.", "2. ¿Qué herramienta es la más adecuada para medir el diámetro exterior de una pieza con alta precisión?", 
            "3. Si un equipo electrónico se sobrecalienta, ¿cuál es la causa más común relacionada con el flujo de aire?", "4. ¿Qué tipo de martillo tiene una cabeza redonda utilizada para remachar y dar forma al metal?", 
            "5. ¿Cuál es el propósito de un fusible en un sistema eléctrico?", "6. Interprete el símbolo en el plano que representa una válvula de cierre.", 
            "7. Si la tubería tiene fugas, ¿cuál es la acción correctiva más rápida y temporal?", "8. ¿Cuál es la función principal de un transformador?", 
            "9. ¿Qué sistema de coordenadas (X, Y, Z) se utiliza para describir la posición en el espacio de una máquina CNC?", "10. ¿Qué se mide con un voltímetro?", 
            "11. Para aislar acústicamente una habitación, ¿qué material es el más eficiente?", "12. ¿Qué indica un alto nivel de vibración en una máquina rotativa?"
        ]
    }
    
    questions = []
    current_id = 1
    for area_name in AREAS:
        # La respuesta correcta forzada será 'a' en la simulación
        expected_answer = "a" 
        spec = APTITUDES_MAP.get(area_name)
        code = spec["code"]
            
        for i in range(N_PREGUNTAS_POR_AREA):
            # Usamos las preguntas detalladas por índice
            pregunta_text = detailed_questions[area_name][i]
            
            # Se usan opciones genéricas, pero la pregunta es específica
            q_opciones = {
                "a": "Respuesta A (Correcta Simulada)",
                "b": "Respuesta B",
                "c": "Respuesta C",
                "d": "Respuesta D"
            }
            
            questions.append({
                "id": current_id, 
                "area": area_name,
                "code": code,
                "pregunta": f"P{code}-{i+1}. {pregunta_text}",
                "opciones": q_opciones, 
                "respuesta_correcta": expected_answer 
            })
            current_id += 1
          
    return pd.DataFrame(questions)

df_preguntas = generate_gatb_questions()
N_TOTAL_PREGUNTAS = len(df_preguntas)

# --- 2. FUNCIONES DE ESTADO Y NAVEGACIÓN Y SCROLL ---

if 'stage' not in st.session_state: st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'area_actual_index' not in st.session_state: st.session_state.area_actual_index = 0
if 'is_navigating' not in st.session_state: st.session_state.is_navigating = False 
if 'error_msg' not in st.session_state: st.session_state.error_msg = ""
if 'resultados_df' not in st.session_state: st.session_state.resultados_df = pd.DataFrame()
# NUEVA VARIABLE DE ESTADO PARA EL SCROLL
if 'should_scroll' not in st.session_state: st.session_state.should_scroll = False

# Función MAXIMAMENTE FORZADA para el scroll al top (SOLUCIÓN DEL USUARIO)
def forzar_scroll_al_top():
    """Fuerza el scroll al inicio de la página usando JavaScript y el ancla 'top-anchor'."""
    js_code = f"""
        <script>
            setTimeout(function() {{
                var topAnchor = window.parent.document.getElementById('top-anchor');
                if (topAnchor) {{
                    topAnchor.scrollIntoView({{ behavior: 'auto', block: 'start' }});
                }} else {{
                    window.parent.scrollTo({{ top: 0, behavior: 'auto' }});
                    var mainContent = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                    if (mainContent) {{
                        mainContent.scrollTo({{ top: 0, behavior: 'auto' }});
                    }}
                }}
            }}, 250); 
        </script>
        """
    components.html(js_code, height=0, scrolling=False)


def set_stage(new_stage):
    """Cambia la etapa de la aplicación, desbloquea la navegación y activa el scroll."""
    st.session_state.stage = new_stage
    st.session_state.is_navigating = False
    st.session_state.error_msg = ""
    # Activa la bandera de scroll
    st.session_state.should_scroll = True 

def reiniciar_test():
    """Borra el estado y fuerza el inicio, asegurando un test nuevo."""
    st.session_state.respuestas = {}
    st.session_state.area_actual_index = 0
    st.session_state.resultados_df = pd.DataFrame()
    set_stage('inicio')

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
        
    st.session_state.is_navigating = True

    if st.session_state.area_actual_index < len(AREAS) - 1:
        st.session_state.area_actual_index += 1
        set_stage('test_activo')
    else:
        calcular_resultados()
        set_stage('resultados')

def solve_all():
    """Resuelve automáticamente todas las preguntas con la respuesta correcta (simulación) y navega a resultados."""
    # Aseguramos el borrado antes de resolver (para la demo)
    st.session_state.respuestas = {}
    
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
    # Distribución de percentiles simulados para un perfil 'Gestor-Técnico'
    simulated_percentiles = {
        "Razonamiento General": 90, "Razonamiento Verbal": 80, "Razonamiento Numérico": 85,
        "Razonamiento Espacial": 70, "Velocidad Perceptiva": 55, "Precisión Manual": 45,
        "Coordinación Manual": 35, "Atención Concentrada": 65, "Razonamiento Mecánico": 75,
        "Razonamiento Abstracto": 92, "Razonamiento Clerical": 95, "Razonamiento Técnico": 60
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


# --- 3. COMPONENTES DE VISUALIZACIÓN Y GRÁFICOS ---

def create_radar_chart(df):
    """Crea un gráfico de radar interactivo con Plotly."""
    df_radar = df[['Área', 'Percentil']].rename(columns={'Área': 'Aptitud', 'Percentil': 'Valor'})

    fig = go.Figure(data=[
        go.Scatterpolar(
            r=df_radar['Valor'],
            theta=df_radar['Aptitud'],
            fill='toself',
            name='Percentil del Usuario',
            line_color='#007ACC' # Azul corporativo
        )],
        layout=go.Layout(
            title=go.layout.Title(text='Distribución Aptitudinal (Percentiles)', x=0.5),
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickvals=[20, 40, 60, 80, 100],
                    ticktext=['Muy Bajo', 'Bajo', 'Promedio', 'Alto', 'Superior']
                )
            ),
            showlegend=False,
            height=600 
        )
    )
    return fig

def create_bar_chart(df):
    """Crea un gráfico de barras horizontal comparativo con Plotly."""
    fig = px.bar(
        df.sort_values(by='Percentil', ascending=True),
        y='Área',
        x='Percentil',
        orientation='h',
        color='Clasificación',
        color_discrete_map={
            "Superior (90-99)": "#008000", "Alto (80-89)": "#4682b4", "Promedio Alto (60-79)": "#ff8c00",
            "Promedio (40-59)": "#ffd700", "Promedio Bajo (20-39)": "#ffa07a", "Bajo (10-19)": "#dc143c",
            "Muy Bajo (0-9)": "#8b0000"
        },
        title='Comparativa Detallada de Percentiles'
    )
    fig.add_vline(x=50, line_width=2, line_dash="dash", line_color="gray", annotation_text="Promedio (50%)")
    fig.update_layout(xaxis_title="Puntuación Percentil", yaxis_title="Área Aptitudinal", legend_title="Clasificación", height=700)
    return fig

def get_graficos_interpretacion(df_resultados):
    """Genera un resumen detallado de la interpretación de los gráficos."""
    avg_percentil = df_resultados['Percentil'].mean()
    max_percentil = df_resultados['Percentil'].max()
    min_percentil = df_resultados['Percentil'].min()
    area_max = df_resultados.loc[df_resultados['Percentil'].idxmax()]['Área']
    area_min = df_resultados.loc[df_resultados['Percentil'].idxmin()]['Área']
    
    n_superior = df_resultados[df_resultados['Percentil'] >= 80].shape[0]
    n_bajo = df_resultados[df_resultados['Percentil'] <= 40].shape[0]
    
    interpretacion = f"""
    <div style="background-color: #f7f9fb; padding: 20px; border-radius: 10px; border-left: 5px solid #007ACC; margin-top: 20px;">
        <h4 style="color: #007ACC; margin-top: 0;">Interpretación Detallada del Perfil Aptitudinal</h4>
        
        <p>El perfil aptitudinal, reflejado en el **Gráfico de Radar**, muestra una forma **{
            'equilibrada' if abs(max_percentil - min_percentil) < 40 else 'puntiaguda y desequilibrada'
        }**. Esto indica que el evaluado tiene una distribución de habilidades {
            'relativamente homogénea.' if abs(max_percentil - min_percentil) < 40 else 'con marcados picos y valles.'
        }</p>

        <h5 style="color: #1f77b4;">Análisis de Fortalezas (Percentiles Altos)</h5>
        <ul>
            <li>**Aptitud Máxima:** **{area_max}** ({max_percentil:.1f}%) es el punto más fuerte. Esta habilidad debe ser el foco de la elección de carrera o el rol principal en el trabajo.</li>
            <li>**Puntajes Superiores:** Se identifican **{n_superior}** áreas (Percentil ≥ 80) que superan significativamente a la población de referencia, indicando un potencial avanzado en estas funciones.</li>
        </ul>
        
        <h5 style="color: #d62728;">Análisis de Áreas de Desarrollo (Percentiles Bajos)</h5>
        <ul>
            <li>**Aptitud Mínima:** **{area_min}** ({min_percentil:.1f}%) representa el área con mayor necesidad de entrenamiento.</li>
            <li>**Puntajes Bajos:** Se identifican **{n_bajo}** áreas (Percentil ≤ 40) que están por debajo del promedio. Mejorar estas áreas es crucial para roles que exijan un perfil aptitudinal holístico.</li>
        </ul>
        
        <p style="font-style: italic; margin-bottom: 0;">**Conclusión:** La mayoría de las habilidades se concentran alrededor del promedio de **{avg_percentil:.1f}%**, pero la distinción entre **{area_max}** y **{area_min}** determina el tipo de rol más adecuado.</p>
    </div>
    """
    return interpretacion

def get_estrategias_de_mejora(area):
    """Proporciona estrategias de mejora específicas para cada área aptitudinal."""
    # (Mantenido del código anterior)
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


# --- 4. VISTAS DE STREAMLIT ---

def vista_inicio():
    """Muestra la página de inicio e instrucciones, ahora más detallada y visual."""

    st.markdown("""
    <style>
        .title-box {
            background-color: #003366;
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        .title-box h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 900;
        }
        .title-box h3 {
            margin: 5px 0 0 0;
            font-size: 1.2em;
            opacity: 0.8;
        }
    </style>
    <div class="title-box">
        <h1>🧠 Batería de Aptitudes Generales – GABT Pro Max</h1>
        <h3>Evaluación Estructurada de 12 Factores Aptitudinales Clave</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_info, col_start = st.columns([3, 1])

    with col_info:
        st.subheader("📊 Metodología de Evaluación")
        st.info(f"""
        Esta prueba simula una evaluación aptitudinal de alto nivel, midiendo su potencial en **12 áreas cognitivas y motrices** fundamentales para el éxito profesional.
        
        **🎯 Estructura del Test:**
        - **Total de Aptitudes Evaluadas:** **{len(AREAS)}**
        - **Total de Preguntas:** **{N_TOTAL_PREGUNTAS}** (12 ítems por área)
        - **Resultado:** Informe profesional con análisis de percentiles, fortalezas y plan de desarrollo.
        
        **🔍 Áreas Clave:** Razonamiento (General, Verbal, Numérico, Abstracto), Habilidades Operativas (Clerical, Perceptiva) y Factores Psicomotores (Precisión, Coordinación).
        """)
        
        st.markdown("""
        **Guía Rápida de Inicio:**
        1. **Concentración:** Asegúrese de estar en un ambiente libre de distracciones.
        2. **Honestidad:** Responda según su mejor juicio, no hay penalización por fallar.
        3. **Navegación:** Al hacer click en 'Siguiente', la página se actualizará y lo llevará al inicio de la nueva sección.
        """)
    
    with col_start:
        st.subheader("Iniciar Test")
        st.warning("⚠️ **Nota de Simulación:** Esta es una prueba demostrativa. Los resultados y el análisis son ilustrativos para mostrar el potencial del informe profesional.")
        
        # Botón para iniciar el test
        st.button("🚀 Iniciar Evaluación", type="primary", use_container_width=True, on_click=lambda: set_stage('test_activo')) 

        # Botón para la demostración
        st.button("✨ Ver Informe Rápido (Demo)", type="secondary", use_container_width=True, on_click=solve_all)


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
    
    # Botón de navegación (con scroll al principio forzado)
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
    """Muestra el informe de resultados profesional, detallado, con gráficos y estructurado."""

    df_resultados = st.session_state.resultados_df
    analisis = get_analisis_detalle(df_resultados)
    
    st.title("🏆 Informe Ejecutivo de Perfil Aptitudinal GABT Pro Max")
    st.markdown("---")
    
    # --- 1. RESUMEN EJECUTIVO (GLOBAL RATING) ---
    with st.container(border=True):
        st.subheader("1. Resumen Ejecutivo y Perfil Global")
        avg_percentil = df_resultados['Percentil'].mean()
        calificacion, detalle_calificacion, color_calificacion = calificar_global(avg_percentil)

        st.markdown(f"""
        <div style="background-color: {color_calificacion}; padding: 25px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            <h2 style="margin: 0; font-size: 2.2em; font-weight: 800; letter-spacing: 1px;">{calificacion}</h2>
            <p style="margin: 5px 0 10px 0; font-size: 1.2em; font-weight: 500;">Percentil Promedio Global: **{avg_percentil:.1f}%**</p>
            <p style="font-size: 1.0em; margin: 0; border-top: 1px solid rgba(255,255,255,0.4); padding-top: 8px; opacity: 0.9;">**Diagnóstico:** {detalle_calificacion}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="padding: 15px; border-left: 5px solid #003366; background-color: #e6f0ff; border-radius: 5px; margin-top: 15px;">
            <p style="font-weight: bold; margin: 0; color: #003366;">Conclusiones del Evaluador:</p>
            <p style="margin: 5px 0 0 0;">El perfil muestra una base **{analisis['perfil']}**, con una clara inclinación hacia **{analisis['top_area']}**. El individuo es particularmente apto para {analisis['potencial']}.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    # --- 2. KPIS Y MÉTRICAS ---
    with st.container(border=True):
        st.subheader("2. Indicadores Clave de Desempeño (KPIs)")
        
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        
        max_percentil = df_resultados['Percentil'].max()
        min_percentil = df_resultados['Percentil'].min()
        area_max = df_resultados.loc[df_resultados['Percentil'].idxmax()]['Área']
        area_min = df_resultados.loc[df_resultados['Percentil'].idxmin()]['Área']
        n_superior = df_resultados[df_resultados['Percentil'] >= 80].shape[0]
        n_desarrollo = df_resultados[df_resultados['Percentil'] <= 40].shape[0]

        with col_kpi1:
            st.metric(label="Percentil Promedio Global", value=f"{avg_percentil:.1f}%", delta="Nivel General de Aptitud")

        with col_kpi2:
            st.metric(label="Máxima Aptitud (Potencial)", value=f"{max_percentil:.1f}%", help=f"Área: {area_max}")

        with col_kpi3:
            st.metric(label="Áreas Fortalecidas (Percentil ≥ 80)", value=n_superior, delta=f"{n_superior/len(AREAS)*100:.0f}% del total")
            
        with col_kpi4:
            st.metric(label="Áreas de Desarrollo Prioritario (Percentil ≤ 40)", value=n_desarrollo, delta=f"{n_desarrollo} áreas", delta_color="inverse")
            
    st.markdown("---")

    # --- 3. VISUALIZACIÓN PROFESIONAL + INTERPRETACIÓN ---
    with st.container(border=True):
        st.subheader("3. Perfil Aptitudinal Visual y Análisis de Patrones")
        
        col_radar, col_bar = st.columns(2)

        with col_radar:
            st.markdown("#### Gráfico de Radar: Distribución de Percentiles")
            st.plotly_chart(create_radar_chart(df_resultados), use_container_width=True)

        with col_bar:
            st.markdown("#### Comparativa Detallada de Percentiles")
            st.plotly_chart(create_bar_chart(df_resultados), use_container_width=True)

        # NUEVO: Resumen Detallado de Interpretación
        st.markdown(get_graficos_interpretacion(df_resultados), unsafe_allow_html=True)

    st.markdown("---")

    # --- 4. ANÁLISIS COMPARATIVO: FORTALEZAS Y DEBILIDADES ---
    with st.container(border=True):
        st.subheader("4. Análisis Comparativo del Perfil")
        
        col_fortaleza, col_mejora = st.columns(2)

        with col_fortaleza:
            st.markdown('<h4 style="color: #008000;">🌟 Fortalezas Intrínsecas (Top 3)</h4>', unsafe_allow_html=True)
            st.markdown(analisis['fortalezas'], unsafe_allow_html=True)
            st.success("Estas aptitudes deben ser los pilares de la trayectoria profesional y la base para el entrenamiento de otras áreas.")

        with col_mejora:
            st.markdown('<h4 style="color: #dc143c;">📉 Áreas de Oportunidad (Bottom 3)</h4>', unsafe_allow_html=True)
            st.markdown(analisis['mejoras'], unsafe_allow_html=True)
            st.error("Una puntuación baja en estas áreas puede limitar el potencial en roles específicos y requiere desarrollo.")

    st.markdown("---")

    # --- 5. PLAN DE DESARROLLO ---
    with st.container(border=True):
        st.subheader("5. Potencial de Rol y Plan de Desarrollo")
        
        st.markdown(f"""
        <div style="padding: 15px; border: 1px solid #003366; background-color: #f0f8ff; border-radius: 10px; margin-bottom: 20px;">
            <h5 style="margin-top: 0; color: #003366;">Potencial Ocupacional Recomendado (Enfoque Primario)</h5>
            <p style="font-size: 1.1em; font-weight: bold;">{analisis['potencial']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### **Estrategias Individualizadas de Desarrollo**")
        st.info("Plan de acción basado en las aptitudes con percentiles bajos (≤ 40%) o aquellas que requieran mejora continua.")
        
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

    # Botón de reinicio que asegura el borrado de respuestas y el scroll al top
    st.button("⏪ Realizar Nueva Evaluación", type="secondary", on_click=reiniciar_test, use_container_width=True)

# --- 6. CONTROL DEL FLUJO PRINCIPAL Y SCROLL FORZADO ---

if st.session_state.stage == 'inicio':
    vista_inicio()
elif st.session_state.stage == 'test_activo':
    vista_test_activo()
elif st.session_state.stage == 'resultados':
    vista_resultados()

# 3. EJECUCIÓN CONDICIONAL DEL SCROLL
if st.session_state.should_scroll:
    forzar_scroll_al_top()
    # Desactiva la bandera después de ejecutar el scroll
    st.session_state.should_scroll = False

# --- 7. FOOTER Y ACERCA DE ---
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: small; color: grey;'>Informe generado por IA basado en la estructura del GATB. Las puntuaciones son simuladas con fines educativos y de demostración.</p>", unsafe_allow_html=True)
