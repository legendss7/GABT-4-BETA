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
import plotly.express as px # Importación necesaria para los gráficos profesionales
import plotly.graph_objects as go # Para el gráfico de Radar

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="Batería de Aptitudes GABT Pro Max")

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
    """Genera las 144 preguntas simuladas detalladas y su respuesta esperada."""
    
    # Opciones por defecto para todas las preguntas
    base_opciones = {"a": "Opción A", "b": "Opción B", "c": "Opción C", "d": "Opción D"}
    
    # Preguntas detalladas (12 por área) y su respuesta correcta esperada (Simulada: 'a')
    detailed_questions = {
        "Razonamiento General": [
            "1. (Silogismo) Todos los 'M' son 'P'. Ningún 'S' es 'M'. ¿Qué se puede concluir?", 
            "2. ¿Cuál de los siguientes términos es el más distinto de los demás?", 
            "3. Complete la analogía: Arquitecto es a Edificio como Músico es a:", 
            "4. Si la afirmación 'Algunos científicos son idealistas' es verdadera, ¿cuál debe ser falsa?", 
            "5. Encuentre el patrón: 2, 6, 18, 54, ...",
            "6. Si un 'Globber' nunca es 'Flippy' y todos los 'Flippy' son 'Zippy', ¿es cierto que algunos 'Zippy' no son 'Globbers'?",
            "7. Si hoy es martes, ¿qué día de la semana será dentro de 100 días?",
            "8. ¿Cuál es el número que falta en la secuencia: 121, 144, 169, 196, ...?",
            "9. Si un libro cuesta $30 más la mitad de su precio, ¿cuánto cuesta el libro?",
            "10. ¿Qué palabra completa mejor la frase: 'La ____ del testigo fue esencial para el veredicto'?",
            "11. Un objeto tiene un volumen de 15m³. Si su densidad es 3kg/m³, ¿cuál es su masa?",
            "12. Si se reorganizan las letras de 'NAPATRA', ¿el resultado es el nombre de un animal, país o ciudad?"
        ],
        "Razonamiento Verbal": [
            "1. Sinónimo más apropiado de 'Inefable':", "2. Antónimo de 'Exacerbar':", "3. ¿Qué palabra significa 'Actuar con premeditación'?", 
            "4. El significado de la frase 'A diestra y siniestra' es:", "5. 'Prolífico' se relaciona mejor con:", "6. ¿Cuál es el sustantivo de 'Persuadir'?", 
            "7. Complete: La ____ de los argumentos debilitó la defensa.", "8. Encuentre el error gramatical en la siguiente oración.", 
            "9. ¿Qué palabra NO es un sinónimo de 'Austeridad'?", "10. ¿Cuál es el prefijo que significa 'después'?", 
            "11. La palabra 'Ubicuidad' se refiere a:", "12. ¿Qué significa la expresión 'Un cisne negro' en el contexto de eventos?"
        ],
        "Razonamiento Numérico": [
            "1. Resuelva: (1/4) + (2/5) = ", "2. Calcule el 15% de 480.", "3. Si el precio sube 20% y luego baja 10%, ¿cuál es el cambio neto?", 
            "4. ¿Cuánto tiempo se necesita para llenar un tanque de 300 litros a razón de 5 litros/minuto?", "5. Resuelva: 5! / (3! * 2!) =", 
            "6. Si x/3 + 4 = 10, ¿cuál es el valor de x?", "7. Un producto cuesta $50. Se ofrece un descuento de $10 y un 20% adicional. ¿Precio final?", 
            "8. ¿Cuál es la media (promedio) de 12, 18, 24 y 30?", "9. ¿Cuántos números primos hay entre 10 y 20?", 
            "10. La ecuación de la recta que pasa por (0,0) y (2,6) es:", "11. Si 5 obreros tardan 6 días, ¿cuánto tardan 3 obreros (regla de tres inversa)?", 
            "12. ¿Cuál es el área de un círculo con radio de 5 cm (usando π ≈ 3.14)?"
        ],
        "Razonamiento Espacial": [
            "1. Identifique la figura que resulta de rotar 90 grados a la derecha.", "2. ¿Cuál de las figuras tridimensionales puede formarse con este patrón plano?", 
            "3. Elija la sombra que corresponde al objeto mostrado.", "4. ¿Qué parte se necesita para completar el cubo?", 
            "5. Si se unen las piezas A y B, ¿qué forma obtienen?", "6. Indique qué vista (frontal, lateral o superior) NO corresponde a la figura.", 
            "7. ¿Cuántos cubos pequeños componen la figura (visualización 3D)?", "8. Si este objeto se ve en un espejo, ¿cuál es su reflejo?", 
            "9. ¿Cuál es el resultado de doblar el papel por la línea punteada?", "10. Encuentre el ángulo que se forma entre la manecilla de la hora y el minutero a las 3:30.", 
            "11. ¿Qué imagen completa la serie de rotación espacial?", "12. Si la figura se invierte de arriba abajo, ¿cuál es el resultado?"
        ],
        "Velocidad Perceptiva": [
            "1. ¿Cuál de los siguientes códigos es IDÉNTICO a MZA94B-Q2?", "2. Compare las parejas: 74G8C/74GB8. ¿Son iguales o diferentes?", 
            "3. ¿Cuál nombre coincide exactamente: 'Ramírez Soto, Juan C.'?", "4. Busque el error en la secuencia de números: 8930184752...", 
            "5. Encuentre el código que NO tiene 4 dígitos: 2311, 4005, 120, 5678, 9090.", "6. ¿Cuántos 'T' mayúsculas hay en el siguiente texto de 10 palabras?", 
            "7. ¿Es 'Suministros Técnicos' igual a 'Suministros Técnicos Ltda.'?", "8. Encuentre la dirección postal correcta: Av. Libertador 1205 A, Santiago.", 
            "9. ¿Qué número está repetido en la lista: 45, 67, 88, 45, 99?", "10. Compare las siguientes fechas: 01/10/2024 y 10/01/2024.", 
            "11. Localice la única 'o' minúscula que está en negrita en el párrafo.", "12. ¿Cuál de estas palabras está escrita al revés?"
        ],
        "Precisión Manual": [
            "1. (Simulado) Identifique el área de 'trazo' más fino dentro del cuadro.", "2. (Simulado) Seleccione el punto que está exactamente en el centro.", 
            "3. (Simulado) ¿Cuál línea es más precisa en su finalización?", "4. (Simulado) Marque la casilla más pequeña con un punto.", 
            "5. (Simulado) ¿Cuál de las siguientes figuras tiene la simetría más exacta?", "6. (Simulado) Mida el segmento de línea más cercano a 5.0 cm.", 
            "7. (Simulado) Elija el diagrama donde el punto está dentro del área permitida.", "8. (Simulado) En la rejilla, localice la coordenada (3, F).", 
            "9. (Simulado) ¿Cuál 'círculo' dibujado es el más perfecto?", "10. (Simulado) Seleccione el área de enfoque más nítida en la imagen.", 
            "11. (Simulado) Identifique la única diferencia minúscula entre las dos imágenes.", "12. (Simulado) ¿Cuál herramienta de dibujo se usó con mayor precisión?"
        ],
        "Coordinación Manual": [
            "1. (Simulado) ¿Cuál es el camino más rápido para trazar del punto A al B sin tocar los bordes (Laberinto)?", "2. (Simulado) ¿Qué flecha indica un movimiento coordinado?", 
            "3. (Simulado) Si presiona el botón 'Z' mientras gira la palanca, ¿cuál es el resultado?", "4. (Simulado) Muestre la trayectoria de un objeto lanzado con precisión.", 
            "5. (Simulado) ¿Qué secuencia de pulsaciones de teclado lleva al objetivo?", "6. (Simulado) Si se usa la mano izquierda para el control 1 y la derecha para el control 2, ¿qué acción se logra?", 
            "7. (Simulado) Identifique el patrón rítmico correcto.", "8. (Simulado) La acción de levantar un objeto pesado requiere coordinación de:", 
            "9. (Simulado) ¿Qué deporte requiere mayor coordinación ojo-mano?", "10. (Simulado) Si el pedal y el volante deben sincronizarse, ¿qué sucede si uno falla?", 
            "11. (Simulado) ¿Cuál es el orden correcto para ensamblar la pieza (secuencia de movimientos)?", "12. (Simulado) Elija el patrón de movimiento que evita el obstáculo."
        ],
        "Atención Concentrada": [
            "1. ¿Cuántas veces aparece la letra 'e' en la primera línea del texto?", "2. Corrija el error de ortografía en el segundo párrafo.", 
            "3. Si 'A' es 1, 'B' es 2, etc., ¿cuál es el valor numérico de la palabra 'CONCENTRACIÓN'?", "4. Encuentre el número de teléfono oculto en el cuerpo del correo.", 
            "5. ¿Cuál es la única palabra que está en MAYÚSCULAS en el texto?", "6. ¿Cuántos puntos de puntuación (comas, puntos) faltan en la frase?", 
            "7. ¿Cuál es el día de la semana mencionado en el tercer punto?", "8. Identifique la única discrepancia entre la lista A y la lista B.", 
            "9. Si el tiempo de respuesta promedio es 0.5 segundos, ¿cuántas tareas puede realizar en 5 minutos?", "10. Encuentre el error lógico en el proceso de tres pasos.", 
            "11. ¿Cuál es el sinónimo de la palabra marcada con un asterisco (*)?", "12. ¿Cuántas figuras de color azul están incompletas en la imagen?"
        ],
        "Razonamiento Mecánico": [
            "1. Si el engranaje A gira en sentido horario, ¿en qué dirección gira el engranaje C?", "2. ¿Qué palanca requiere menos fuerza para levantar la carga (ley de la palanca)?", 
            "3. ¿Qué polea proporciona mayor ventaja mecánica?", "4. Si un motor tiene 10 CV (Caballos de Vapor), ¿cuántos Watts son (aproximado)?", 
            "5. ¿Qué principio explica por qué un barco flota (Arquímedes)?", "6. Si se usa una llave más larga, ¿aumenta o disminuye el torque (momento de fuerza)?", 
            "7. ¿Cuál de estos es un ejemplo de energía potencial?", "8. Si se aplica presión a un fluido incompresible, ¿qué principio aplica (Pascal)?", 
            "9. ¿Qué sistema de transmisión es más eficiente (cadena, correa, engranaje)?", "10. Para que un circuito eléctrico funcione, ¿qué elemento es esencial?", 
            "11. ¿Cómo se mide la resistencia eléctrica?", "12. ¿Qué tornillo permite ejercer más fuerza (diámetro y paso)?"
        ],
        "Razonamiento Abstracto": [
            "1. Complete la matriz de figuras 3x3 (tipo Raven).", "2. ¿Cuál figura sigue lógicamente en la secuencia A, B, C, D, ...?", 
            "3. Identifique el patrón de cambio de color/forma/tamaño en la serie.", "4. ¿Cuál de las figuras es el 'intruso' que no sigue la regla?", 
            "5. Si el patrón gira 45 grados y se invierte, ¿cuál es la figura resultante?", "6. ¿Qué figura es la suma o resta lógica de las dos anteriores?", 
            "7. Encuentre la relación entre el par 1 y aplíquela al par 2.", "8. Si la figura tiene 'X' lados y 'Y' puntos, ¿cuál es el patrón numérico?", 
            "9. Complete el cuadrado faltante basado en las transformaciones de filas y columnas.", "10. ¿Cuál figura se obtiene al sobreponer las dos imágenes?", 
            "11. ¿Qué línea se mueve de forma independiente en la secuencia?", "12. Si cada figura representa una variable, ¿cuál es la ecuación visual correcta?"
        ],
        "Razonamiento Clerical": [
            "1. Clasifique el documento 'Z-2024-FISC-10' según el código (Z=Zonas, F=Finanzas).", "2. ¿Cuál es el orden alfabético correcto de estos 4 nombres?", 
            "3. Encuentre la cuenta bancaria incorrecta en el listado.", "4. ¿Cuántos errores de tipeo hay en la siguiente tabla de datos (ej. números en lugar de letras)?", 
            "5. Archive el documento con fecha 10/05/2023 en el sistema 'FIFO' (First In, First Out).", "6. ¿Cuál es la diferencia de saldo entre los registros A y B?", 
            "7. Corrija el error en la transcripción de la dirección:", "8. ¿Qué documento está vencido (fecha de vencimiento 01/01/2024)?", 
            "9. Calcule el número total de ítems en las columnas 'Inventario' y 'Pendiente'.", "10. Verifique la coincidencia del número de ID en dos bases de datos.", 
            "11. ¿Qué letra falta en la serie: A, C, E, G, I, ...?", "12. ¿Cuál es el procedimiento correcto para la recepción de facturas?"
        ],
        "Razonamiento Técnico": [
            "1. Identifique el diagrama de un circuito en paralelo.", "2. ¿Qué herramienta es la más adecuada para cortar metal delgado?", 
            "3. Si un motor no arranca, ¿cuál es la causa más probable de falla eléctrica?", "4. ¿Qué tipo de soldadura se utiliza para unir dos metales ferrosos?", 
            "5. ¿Cuál es el propósito de un disyuntor en un sistema eléctrico?", "6. Interprete el símbolo en el plano arquitectónico.", 
            "7. Si la presión de una tubería disminuye, ¿cuál es una posible causa?", "8. ¿Cuál es la función principal de un capacitor?", 
            "9. ¿Qué sistema de coordenadas se utiliza en la mayoría de los tornos CNC?", "10. ¿Qué se mide con un micrómetro?", 
            "11. Para aislar térmicamente una habitación, ¿qué material es el más eficiente?", "12. Si una bomba centrífuga hace ruido, ¿qué indica generalmente?"
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

# --- 2. FUNCIONES DE ESTADO Y NAVEGACIÓN ---

if 'stage' not in st.session_state: st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'area_actual_index' not in st.session_state: st.session_state.area_actual_index = 0
if 'is_navigating' not in st.session_state: st.session_state.is_navigating = False 
if 'error_msg' not in st.session_state: st.session_state.error_msg = ""
if 'resultados_df' not in st.session_state: st.session_state.resultados_df = pd.DataFrame()


def forzar_scroll_al_top():
    """Injecta JS para forzar el scroll al tope ABSOLUTO de la página."""
    js_code = """
        <script>
            setTimeout(function() {
                window.parent.scrollTo({ top: 0, behavior: 'auto' });
                var mainContent = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                if (mainContent) {
                    mainContent.scrollTo({ top: 0, behavior: 'auto' });
                }
            }, 250); 
        </script>
        """
    st.html(js_code)


def set_stage(new_stage):
    """Cambia la etapa de la aplicación, desbloquea la navegación y llama a la función de scroll."""
    st.session_state.stage = new_stage
    st.session_state.is_navigating = False
    st.session_state.error_msg = ""
    forzar_scroll_al_top() # LLAMADA A LA FUNCIÓN DE SCROLL AL TOP


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


# --- 3. COMPONENTES DE VISUALIZACIÓN ---

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
            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
            width: 0%; 
            font-weight: bold;
            font-size: 1em;
            background-color: {color};
            display: flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
        }}
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

def create_radar_chart(df):
    """Crea un gráfico de radar interactivo con Plotly."""
    
    # Crea un DataFrame para el radar chart, usando Percentil como valor
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
            height=600 # Altura ajustada para mejor visualización
        )
    )
    
    return fig

def create_bar_chart(df):
    """Crea un gráfico de barras horizontal comparativo con Plotly."""
    
    # Añadimos una columna para el promedio de referencia (simulado en 50%)
    df['Promedio de Referencia (50%)'] = 50 
    
    fig = px.bar(
        df.sort_values(by='Percentil', ascending=True), # Ordenar para que el gráfico quede mejor
        y='Área',
        x=['Percentil', 'Promedio de Referencia (50%)'], # Barras apiladas (no es lo ideal) o agrupadas
        barmode='group', # Agrupadas para comparación directa
        orientation='h',
        color='Clasificación', # Colorear por la clasificación cualitativa
        color_discrete_map={
            "Superior (90-99)": "#008000", "Alto (80-89)": "#4682b4", "Promedio Alto (60-79)": "#ff8c00",
            "Promedio (40-59)": "#ffd700", "Promedio Bajo (20-39)": "#ffa07a", "Bajo (10-19)": "#dc143c",
            "Muy Bajo (0-9)": "#8b0000"
        },
        title='Comparativa de Aptitudes vs. Promedio General (50%)'
    )
    
    # Ajustes finos de layout
    fig.update_layout(
        xaxis_title="Puntuación Percentil",
        yaxis_title="Área Aptitudinal",
        legend_title="Clasificación",
        height=700
    )
    # Mostramos solo la barra del usuario y una línea o punto para el promedio. Usaremos un Scatter en lugar de una barra.
    # Versión mejorada con línea de referencia para el promedio (50)
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
        title='Comparativa de Aptitudes y Clasificación'
    )
    fig.add_vline(x=50, line_width=2, line_dash="dash", line_color="gray", annotation_text="Promedio (50%)")
    fig.update_layout(xaxis_title="Puntuación Percentil", yaxis_title="Área Aptitudinal", legend_title="Clasificación", height=700)
    
    return fig

# --- 4. FUNCIONES DE REPORTE PROFESIONAL (ANÁLISIS) ---

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

    # Potencial Ocupacional (Basado en el perfil simulado)
    top_area = top_3.iloc[0]['Área']
    if top_area in ["Razonamiento Abstracto", "Razonamiento General", "Razonamiento Numérico"]:
        potencial = "Roles Estratégicos, de Análisis Avanzado y Liderazgo (Consultoría, Finanzas, I+D)."
        perfil = "Alto Potencial Cognitivo (G-Factor) y Capacidad de Gestión de Información (Clerical, Abstracto)."
    elif top_area in ["Razonamiento Mecánico", "Razonamiento Espacial", "Razonamiento Técnico"]:
        potencial = "Roles de Ingeniería, Diseño y Mantenimiento de Infraestructura Crítica."
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


# --- 5. VISTAS DE STREAMLIT ---

def vista_inicio():
    """Muestra la página de inicio e instrucciones."""

    st.title("🧠 Batería de Aptitudes Generales – GABT Pro Max")
    st.header("Evaluación Estructurada de 12 Factores Aptitudinales")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        st.info(f"""
        **🎯 Objetivo:** Medir **12 factores clave** de aptitud con **{N_TOTAL_PREGUNTAS} ítems simulados** para fines educativos y profesionales.
        
        **📋 Estructura del Test:**
        - **Total de Secciones:** **{len(AREAS)}**
        - **Preguntas por Sección:** **{N_PREGUNTAS_POR_AREA}**
        """)
    
    with col2:
        st.subheader("Simulación Profesional")
        st.warning("⚠️ **Nota:** Esta es una simulación. Los resultados son ilustrativos para el análisis. Todas las preguntas han sido creadas de forma específica.")
        
        if st.button("🚀 Iniciar Evaluación", type="primary", use_container_width=True, on_click=lambda: set_stage('test_activo')):
            pass 

        if st.button("✨ Resolver Todo (Demo) y Ver Informe", type="secondary", use_container_width=True, on_click=solve_all):
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
    """Muestra el informe de resultados profesional, detallado, con gráficos y animado."""

    df_resultados = st.session_state.resultados_df
    analisis = get_analisis_detalle(df_resultados)
    
    st.title("🏆 Informe Ejecutivo de Perfil Aptitudinal GABT Pro Max")
    st.markdown("---")
    
    # --- 1. Calificación Global (Resumen Ejecutivo) ---
    avg_percentil = df_resultados['Percentil'].mean()
    calificacion, detalle_calificacion, color_calificacion = calificar_global(avg_percentil)

    st.subheader("1. Resumen Ejecutivo y Perfil Global")
    
    st.markdown(f"""
    <div style="background-color: {color_calificacion}; padding: 25px; border-radius: 15px; color: white; margin-bottom: 30px; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,0.4);">
        <h2 style="margin: 0; font-size: 2.5em; font-weight: 900; letter-spacing: 1px;">{calificacion}</h2>
        <p style="margin: 5px 0 15px 0; font-size: 1.3em; font-weight: 500;">Percentil Promedio Global: **{avg_percentil:.1f}%**</p>
        <p style="font-size: 1.1em; margin: 0; border-top: 1px solid rgba(255,255,255,0.5); padding-top: 10px; opacity: 0.9;">**Diagnóstico:** {detalle_calificacion}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="padding: 15px; border-left: 5px solid #003366; background-color: #e6f0ff; border-radius: 5px; margin-bottom: 20px;">
        <p style="font-weight: bold; margin: 0; color: #003366;">Conclusiones del Evaluador:</p>
        <p style="margin: 5px 0 0 0;">El perfil muestra una base **{analisis['perfil']}**, con una clara inclinación hacia **{analisis['top_area']}**. El individuo es particularmente apto para {analisis['potencial']}. Se recomienda un plan de desarrollo focalizado en las áreas de menor rendimiento para lograr un perfil más holístico.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # --- 2. Análisis Estadístico y Visualización (GRÁFICOS) ---
    st.subheader("2. Visualización Profesional del Perfil Aptitudinal")
    
    col_radar, col_metrics = st.columns([1, 1])

    with col_radar:
        # Gráfico de Radar
        st.markdown("**Gráfico de Radar: Distribución de Percentiles**")
        st.plotly_chart(create_radar_chart(df_resultados), use_container_width=True)

    with col_metrics:
        # Métricas Clave
        st.markdown("#### Métricas Clave")
        st.metric(label="Percentil General Promedio", value=f"{avg_percentil:.1f}%", delta=f"{df_resultados['Puntuación Bruta'].sum()} aciertos totales")
        st.metric(label="Máxima Aptitud (Percentil)", value=f"{df_resultados['Percentil'].max():.1f}%", help=f"Área: {df_resultados.loc[df_resultados['Percentil'].idxmax()]['Área']}")
        st.metric(label="Mínima Aptitud (Percentil)", value=f"{df_resultados['Percentil'].min():.1f}%", help=f"Área: {df_resultados.loc[df_resultados['Percentil'].idxmin()]['Área']}")
        st.metric(label="Aptitudes Promedio/Superior (≥ 60%)", value=df_resultados[df_resultados['Percentil'] >= 60].shape[0], help="Número de áreas por encima de la media.")


    # Gráfico de Barras Horizontal
    st.markdown("---")
    st.subheader("3. Detalle de Puntuaciones y Clasificación (Percentiles)")
    st.plotly_chart(create_bar_chart(df_resultados), use_container_width=True)

    # Barras animadas (como complemento a los gráficos, para el efecto "Pro Max")
    st.markdown("---")
    st.markdown("#### **Representación Animada (Percentiles Detallados)**")
    st.info("Visualización por área con la clasificación cualitativa.")
    for index, row in df_resultados.sort_values(by='Percentil', ascending=False).iterrows():
        label = f"**{row['Área']}** ({row['Clasificación']})"
        percentil = row['Percentil']
        color = row['Color']
        animated_progress_bar(label, percentil, color)

    st.markdown("---")

    # --- 4. Análisis de Fortalezas y Áreas de Mejora ---
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

    # --- 5. Potencial Ocupacional y Estrategia de Desarrollo ---
    st.subheader("5. Potencial de Rol y Plan de Desarrollo")
    
    st.markdown(f"""
    <div style="padding: 20px; border: 1px solid #003366; background-color: #f0f8ff; border-radius: 10px; margin-bottom: 20px;">
        <h5 style="margin-top: 0; color: #003366;">Potencial Ocupacional Recomendado (Enfoque Primario)</h5>
        <p style="font-size: 1.1em; font-weight: bold;">{analisis['potencial']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
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

    # Botón de reinicio que asegura el scroll al top
    st.button("⏪ Realizar Nueva Evaluación", type="secondary", on_click=lambda: set_stage('inicio'), use_container_width=True)

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
