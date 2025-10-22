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

# --- FUNCIÓN CON LAS 144 PREGUNTAS Y RESPUESTAS (REINSERCIÓN COMPLETA) ---

def generate_gatb_questions():
    """Genera 144 preguntas simuladas con respuestas esperadas para el cálculo.
       Se han codificado preguntas y respuestas para cada una de las 12 áreas."""
    test_data = {
        # 12 preguntas por área. La respuesta correcta está en el último elemento de la tupla.
        "Razonamiento General": [
            ("Si A es mayor que B, y B es igual a C, ¿entonces A es mayor que C?", {"a": "Falso", "b": "Inconcluso", "c": "Verdadero"}, "c"),
            ("Completa la serie: 2, 4, 8, 16, ¿...?", {"a": "24", "b": "32", "c": "48", "d": "64"}, "b"),
            ("Si todos los perros son mamíferos y Fido es un perro, ¿qué se puede concluir?", {"a": "Fido es rojo", "b": "Fido es mamífero", "c": "Fido no ladra"}, "b"),
            ("El opuesto de 'efímero' es:", {"a": "Frágil", "b": "Permanente", "c": "Temporal", "d": "Rápido"}, "b"),
            ("Encuentra el intruso: Manzana, Pera, Plátano, Zanahoria.", {"a": "Manzana", "b": "Pera", "c": "Plátano", "d": "Zanahoria"}, "d"),
            ("Si hoy es martes, ¿qué día fue anteayer?", {"a": "Lunes", "b": "Miércoles", "c": "Domingo", "d": "Sábado"}, "c"),
            ("¿Qué es un sinónimo de 'ubicuidad'?", {"a": "Rareza", "b": "Abundancia", "c": "Omnipresencia", "d": "Vacío"}, "c"),
            ("Si X * 5 = 45, ¿cuánto es X - 3?", {"a": "12", "b": "8", "c": "6", "d": "9"}, "c"),
            ("El resultado de 10 - (4 + 2) es:", {"a": "8", "b": "4", "c": "6", "d": "12"}, "b"),
            ("¿Cuál es el siguiente número en la secuencia: 1, 1, 2, 3, 5, 8, ...?", {"a": "11", "b": "12", "c": "13", "d": "15"}, "c"),
            ("La capital de Australia es:", {"a": "Sídney", "b": "Melbourne", "c": "Canberra", "d": "Perth"}, "c"),
            ("Si 'pico' es a 'ave' como 'boca' es a '...':", {"a": "Diente", "b": "Humano", "c": "Lengua", "d": "Animal"}, "b"),
        ],
        "Razonamiento Verbal": [
            ("¿Cuál de las siguientes palabras significa lo contrario a 'mitigar'?", {"a": "Suavizar", "b": "Atenuar", "c": "Exacerbar", "d": "Reducir"}, "c"),
            ("Sinónimo de 'perspicaz':", {"a": "Lento", "b": "Torpe", "c": "Agudo", "d": "Obvio"}, "c"),
            ("Completa la analogía: 'Libro' es a 'Lector' como 'Música' es a '...'", {"a": "Artista", "b": "Oído", "c": "Oyente", "d": "Nota"}, "c"),
            ("¿Qué palabra está mal escrita?", {"a": "Exhibición", "b": "Exprecionar", "c": "Exento", "d": "Extravagante"}, "b"),
            ("¿Qué oración usa correctamente el condicional?", {"a": "Si tendrías tiempo, irías.", "b": "Si tienes tiempo, irás.", "c": "Si tuvieras tiempo, irías.", "d": "Si habrías tenido tiempo."}, "c"),
            ("El significado de 'procrastinar' es:", {"a": "Hacer rápidamente", "b": "Posponer", "c": "Terminar", "d": "Comenzar"}, "b"),
            ("¿Cuál de estos es un par de antónimos?", {"a": "Frío - Helado", "b": "Grande - Enorme", "c": "Claro - Oscuro", "d": "Risa - Alegría"}, "c"),
            ("Selecciona el término que incluye a los demás:", {"a": "Clavel", "b": "Rosa", "c": "Flor", "d": "Margarita"}, "c"),
            ("Una 'hipótesis' es una:", {"a": "Afirmación probada", "b": "Suposición", "c": "Conclusión final", "d": "Ley"}, "b"),
            ("¿Qué significa 'dilucidar'?", {"a": "Oscurecer", "b": "Aclarar", "c": "Confundir", "d": "Ocultar"}, "b"),
            ("¿Cuál es la relación en: 'Coche es a Rueda'?", {"a": "Parte a Todo", "b": "Herramienta a Uso", "c": "Todo a Parte", "d": "Causa a Efecto"}, "c"),
            ("La palabra 'vasto' es homófona con:", {"a": "Basto", "b": "Vaso", "c": "Bala", "d": "Vate"}, "a"),
        ],
        "Razonamiento Numérico": [
            ("Si una camisa cuesta $50 y tiene un 20% de descuento, ¿cuál es el precio final?", {"a": "$40", "b": "$45", "c": "$30", "d": "$35"}, "a"),
            ("¿Cuánto es el 15% de 200?", {"a": "20", "b": "30", "c": "15", "d": "40"}, "b"),
            ("Un tren recorre 120 km en 2 horas. ¿Cuál es su velocidad promedio en km/h?", {"a": "50", "b": "60", "c": "70", "d": "80"}, "b"),
            ("Resuelve: 3 * (5 + 2) - 10", {"a": "15", "b": "11", "c": "14", "d": "21"}, "b"),
            ("Si la razón de niños a niñas en una clase es 3:2 y hay 15 niños, ¿cuántos alumnos hay en total?", {"a": "20", "b": "25", "c": "30", "d": "18"}, "b"),
            ("¿Cuál es el valor de X si $2X + 5 = 17$?", {"a": "6", "b": "7", "c": "11", "d": "8"}, "a"),
            ("La suma de los ángulos internos de un triángulo es:", {"a": "90°", "b": "180°", "c": "360°", "d": "270°"}, "b"),
            ("Si $100 se incrementa en un 10% y luego se reduce en un 10%, ¿cuál es el resultado?", {"a": "$100", "b": "$99", "c": "$98", "d": "$101"}, "b"),
            ("¿Cuántos metros son 3.5 kilómetros?", {"a": "350", "b": "3500", "c": "35000", "d": "35"}, "b"),
            ("Calcula el promedio de 10, 20 y 30.", {"a": "15", "b": "20", "c": "25", "d": "60"}, "b"),
            ("Si se lanza un dado de 6 caras, ¿cuál es la probabilidad de sacar un 4?", {"a": "1/2", "b": "1/6", "c": "1/3", "d": "1/4"}, "b"),
            ("¿Cuál es el área de un cuadrado con lado de 4 cm?", {"a": "8 cm²", "b": "16 cm²", "c": "12 cm²", "d": "20 cm²"}, "b"),
        ],
        "Razonamiento Espacial": [
            ("Si rotas un cubo 90 grados a la derecha y luego 180 grados hacia abajo, ¿qué cara queda arriba?", {"a": "La lateral", "b": "La original de abajo", "c": "La original de atrás", "d": "La original de enfrente"}, "b"),
            ("¿Qué figura completa mejor el espacio vacío? (Asuma un patrón de mosaico simple)", {"a": "Cuadrado", "b": "Círculo", "c": "Triángulo", "d": "Hexágono"}, "a"),
            ("Si doblas esta plantilla, ¿qué forma obtienes? (Asuma una plantilla de cilindro)", {"a": "Cubo", "b": "Pirámide", "c": "Cilindro", "d": "Esfera"}, "c"),
            ("¿Cuál de las opciones es la imagen reflejada en un espejo de la figura original?", {"a": "Opción A", "b": "Opción B", "c": "Opción C", "d": "Opción D"}, "a"),
            ("Si miras una torre desde arriba, ¿qué forma verás?", {"a": "Un cuadrado", "b": "Un círculo", "c": "Depende de la torre", "d": "Un punto"}, "c"),
            ("Si una llave encaja en una cerradura, ¿qué relación espacial tienen?", {"a": "Paralelo", "b": "Perpendicular", "c": "Complementario", "d": "De encaje"}, "d"),
            ("¿Cuál de las siguientes figuras no puede ser armada con dos triángulos rectángulos iguales?", {"a": "Cuadrado", "b": "Romboide", "c": "Pentágono", "d": "Rectángulo"}, "c"),
            ("Identifica la figura que no es posible dibujar sin levantar el lápiz. (Asuma una figura compleja)", {"a": "Figura A", "b": "Figura B", "c": "Figura C", "d": "Figura D"}, "b"),
            ("Si un reloj marca las 3:00, ¿cuál es el ángulo entre las manecillas?", {"a": "30°", "b": "60°", "c": "90°", "d": "180°"}, "c"),
            ("¿Qué sombra proyectaría un cono si la luz viene de un lado?", {"a": "Círculo", "b": "Triángulo", "c": "Rectángulo", "d": "Óvalo"}, "b"),
            ("Si giras la 'T' 45 grados a la izquierda, ¿cómo se verá?", {"a": "T inclinada a la izquierda", "b": "T inclinada a la derecha", "c": "L", "d": "I"}, "a"),
            ("¿Cuál es la vista frontal del objeto si la vista superior es un círculo y la lateral un rectángulo?", {"a": "Círculo", "b": "Rectángulo", "c": "Triángulo", "d": "Cubo"}, "b"),
        ],
        "Velocidad Perceptiva": [
            ("Encuentra el par de números idénticos: 738491 - 738491", {"a": "Idénticos", "b": "Diferentes"}, "a"),
            ("¿El número de teléfono 55219803 es igual a 5521980?", {"a": "Igual", "b": "Diferente"}, "b"),
            ("¿El nombre 'JESÚS SOTO' es igual a 'JESUS SOTO'?", {"a": "Igual", "b": "Diferente"}, "b"),
            ("¿La dirección 'Av. Principal 102' es igual a 'Av. Principal 102'?", {"a": "Igual", "b": "Diferente"}, "a"),
            ("Localiza el código que no es idéntico a 9Q3Y4X:", {"a": "9Q3Y4X", "b": "9Q3Y4X", "c": "9Q3Y4K", "d": "9Q3Y4X"}, "c"),
            ("¿La serie 'H-7-L-P' es la misma que 'H-7-L-R'?", {"a": "Igual", "b": "Diferente"}, "b"),
            ("¿El correo 'jlopez@gmail.com' es igual a 'jlopez@gmal.com'?", {"a": "Igual", "b": "Diferente"}, "b"),
            ("¿La fecha '12/03/2024' es igual a '12-03-2024'?", {"a": "Igual", "b": "Diferente"}, "b"),
            ("Encuentra el error en esta secuencia: A, B, D, C, E:", {"a": "A", "b": "D", "c": "C", "d": "E"}, "c"),
            ("¿El precio '$45.99' es igual a '$45,99'?", {"a": "Igual", "b": "Diferente"}, "a"),
            ("¿La palabra 'Simetría' es igual a 'Simentría'?", {"a": "Igual", "b": "Diferente"}, "b"),
            ("Encuentra la letra que falta en: P, Q, S, T (asuma una secuencia alfabética)", {"a": "R", "b": "U", "c": "V", "d": "O"}, "a"),
        ],
        "Precisión Manual": [
            ("¿El trazo debe conectar el punto A con el B sin salirse del camino? (Asuma un camino estrecho)", {"a": "Sí", "b": "No"}, "a"),
            ("¿Puedes trazar una línea recta perfecta con el mouse? (Simulación de pulso)", {"a": "Sí", "b": "No"}, "a"),
            ("Mueva el objeto al centro de la diana sin tocar el borde. (Simulación de control fino)", {"a": "Lo logré", "b": "Toqué el borde"}, "a"),
            ("Coloque la 'X' justo sobre el centro de la pequeña 'O'. (Simulación de puntería)", {"a": "Lo logré", "b": "Falle"}, "a"),
            ("Presiona el botón solo cuando la luz esté en el punto rojo. (Simulación de tiempo de reacción y precisión)", {"a": "Sí", "b": "No"}, "a"),
            ("¿La herramienta debe ser manipulada con movimientos muy pequeños? (Simulación)", {"a": "Sí", "b": "No"}, "a"),
            ("Copie el patrón con la mayor exactitud posible. (Simulación de copia gráfica)", {"a": "Sí, es idéntico", "b": "No, hay errores"}, "a"),
            ("¿Se requiere fuerza o delicadeza para esta tarea? (Asuma una tarea de ensamblaje de joyas)", {"a": "Fuerza", "b": "Delicadeza"}, "b"),
            ("Si usas un destornillador pequeño, ¿qué habilidad es clave?", {"a": "Fuerza", "b": "Precisión Manual", "c": "Velocidad", "d": "Coordinación"}, "b"),
            ("Una costura requiere:", {"a": "Velocidad Perceptiva", "b": "Precisión Manual", "c": "Razonamiento", "d": "Fuerza"}, "b"),
            ("¿Se puede insertar un hilo en una aguja rápidamente sin precisión?", {"a": "Sí", "b": "No"}, "b"),
            ("¿Cuál es el objetivo principal al manipular componentes electrónicos pequeños?", {"a": "Velocidad", "b": "Cantidad", "c": "Precisión", "d": "Fuerza"}, "c"),
        ],
        "Coordinación Manual": [
            ("¿Puede golpear dos tambores a un ritmo constante con ambas manos? (Simulación de ritmo y coordinación)", {"a": "Sí", "b": "No"}, "a"),
            ("¿La tarea requiere movimientos simultáneos de manos y pies? (Asuma operación de maquinaria)", {"a": "Sí", "b": "No"}, "a"),
            ("Maneje el joystick y presione el pedal al mismo tiempo. (Simulación de coordinación de extremidades)", {"a": "Sí, lo logré", "b": "No, me confundí"}, "a"),
            ("¿Es el tenis un deporte que exige alta coordinación ojo-mano?", {"a": "Sí", "b": "No"}, "a"),
            ("Si se baila, ¿se usa la coordinación de todo el cuerpo?", {"a": "Sí", "b": "No"}, "a"),
            ("¿La coordinación mano-ojo es vital para la mecanografía?", {"a": "Sí", "b": "No"}, "a"),
            ("¿Cuál de los siguientes requiere mayor coordinación motriz gruesa?", {"a": "Escribir", "b": "Correr", "c": "Enhebrar", "d": "Leer"}, "b"),
            ("La coordinación manual se relaciona con:", {"a": "El pulso", "b": "El ritmo y el movimiento sincronizado", "c": "La fuerza"}, "b"),
            ("Para un carpintero, ¿la coordinación es más importante que la fuerza en el lijado fino?", {"a": "Sí", "b": "No"}, "a"),
            ("¿La práctica de instrumentos musicales mejora la coordinación manual?", {"a": "Sí", "b": "No"}, "a"),
            ("¿Se puede operar una grúa sin coordinación mano-pie?", {"a": "Sí", "b": "No"}, "b"),
            ("El ensamblaje de piezas grandes requiere:", {"a": "Razonamiento General", "b": "Coordinación Manual", "c": "Velocidad Perceptiva", "d": "Verbal"}, "b"),
        ],
        "Atención Concentrada": [
            ("Mire fijamente el punto por 30 segundos sin distraerse. (Simulación de enfoque sostenido)", {"a": "Lo logré", "b": "Me distraje"}, "a"),
            ("¿Es fácil ignorar el ruido en un entorno de alta concentración?", {"a": "Sí, si estoy concentrado", "b": "No, es difícil"}, "a"),
            ("Encuentra el número 7 en un texto de números 6. (Simulación de vigilancia)", {"a": "Lo encontré rápido", "b": "Me tomó tiempo"}, "a"),
            ("¿La revisión de errores en un texto legal requiere atención dividida o sostenida?", {"a": "Dividida", "b": "Sostenida"}, "b"),
            ("Mantén la alerta ante un cambio de color. (Simulación de tiempo de reacción prolongado)", {"a": "Sí, lo detecté", "b": "No, lo perdí"}, "a"),
            ("¿La capacidad de atención se ve afectada por el estrés?", {"a": "Sí", "b": "No"}, "a"),
            ("¿Cuál es el factor principal en un puesto de vigilancia o auditoría?", {"a": "Fuerza", "b": "Atención Concentrada", "c": "Verbal", "d": "Numérico"}, "b"),
            ("Si buscas una aguja en un pajar, ¿qué tipo de atención necesitas?", {"a": "Selectiva y Sostenida", "b": "Dividida", "c": "Velocidad", "d": "Memoria"}, "a"),
            ("¿Es la fatiga un enemigo de la atención concentrada?", {"a": "Sí", "b": "No"}, "a"),
            ("¿Cuál de las siguientes es una señal de falta de atención?", {"a": "Completar rápido", "b": "Errores de omisión", "c": "Respuestas correctas", "d": "Silencio"}, "b"),
            ("¿Puede un conductor mantener la atención concentrada en una carretera recta durante horas?", {"a": "Sí, sin esfuerzo", "b": "Sí, con esfuerzo", "c": "No, es imposible"}, "b"),
            ("¿Qué es más importante para la atención: la cantidad de tiempo o la calidad del enfoque?", {"a": "Cantidad", "b": "Calidad"}, "b"),
        ],
        "Razonamiento Mecánico": [
            ("Si la polea A gira en sentido horario, ¿en qué sentido gira la polea B? (Están conectadas por una correa cruzada)", {"a": "Horario", "b": "Antihorario", "c": "No gira"}, "b"),
            ("Para levantar una carga pesada con una palanca, ¿es mejor aplicar la fuerza cerca o lejos del punto de apoyo?", {"a": "Cerca", "b": "Lejos"}, "b"),
            ("¿Qué pasa con la presión del agua si se estrecha el diámetro de la tubería?", {"a": "Aumenta", "b": "Disminuye", "c": "Se mantiene igual"}, "a"),
            ("¿Cuál es la función principal de un engranaje?", {"a": "Almacenar energía", "b": "Transferir movimiento y fuerza", "c": "Generar electricidad", "d": "Reducir la fricción"}, "b"),
            ("Si un objeto flota en el agua, ¿su densidad es mayor o menor que la del agua?", {"a": "Mayor", "b": "Menor", "c": "Igual"}, "b"),
            ("¿En un circuito eléctrico simple, si aumenta la resistencia, qué pasa con la corriente?", {"a": "Aumenta", "b": "Disminuye", "c": "Se mantiene igual"}, "b"),
            ("¿Qué ley de Newton explica por qué un cinturón de seguridad detiene al pasajero?", {"a": "Primera Ley (Inercia)", "b": "Segunda Ley (Fuerza)", "c": "Tercera Ley (Acción y Reacción)"}, "a"),
            ("¿Qué herramienta usarías para medir el voltaje?", {"a": "Amperímetro", "b": "Voltímetro", "c": "Medidor de distancia", "d": "Manómetro"}, "b"),
            ("Si dos objetos de diferente peso caen, ¿cuál llega primero al suelo (ignorando la resistencia del aire)?", {"a": "El más pesado", "b": "El más liviano", "c": "Llegan al mismo tiempo"}, "c"),
            ("¿Para qué se usa un tornillo de banco?", {"a": "Para atornillar", "b": "Para sujetar firmemente", "c": "Para medir", "d": "Para cortar"}, "b"),
            ("¿Cuál es el principio detrás de un gato hidráulico?", {"a": "Principio de Bernoulli", "b": "Principio de Pascal", "c": "Ley de Boyle"}, "b"),
            ("Si empujas un carro, ¿qué fuerza se opone al movimiento?", {"a": "Gravedad", "b": "Fricción", "c": "Normal", "d": "Tensión"}, "b"),
        ],
        "Razonamiento Abstracto": [
            ("Completa la secuencia: O, O O, O O O, ¿...?", {"a": "O O O O", "b": "O O O O O", "c": "O O O O O O", "d": "O O"}, "a"),
            ("Encuentra el patrón y el siguiente: Cuadrado -> Triángulo -> Cuadrado -> ...", {"a": "Círculo", "b": "Cuadrado", "c": "Triángulo", "d": "Rectángulo"}, "c"),
            ("Si (A, B) se transforma en (B, C), ¿cómo se transforma (E, F)?", {"a": "(F, G)", "b": "(D, E)", "c": "(G, H)", "d": "(F, E)"}, "a"),
            ("¿Cuál es el símbolo que rompe la serie? (Asuma una serie de rotación constante)", {"a": "A", "b": "B", "c": "C", "d": "D"}, "c"),
            ("Si en el primer recuadro hay 1 círculo, en el segundo 2, en el tercero 3, ¿qué hay en el cuarto?", {"a": "4 círculos", "b": "1 círculo", "c": "3 círculos", "d": "5 círculos"}, "a"),
            ("La figura se mueve 90 grados en cada paso. ¿Cuál es el siguiente paso?", {"a": "Paso A", "b": "Paso B", "c": "Paso C", "d": "Paso D"}, "b"),
            ("Encuentra la figura que difiere de las otras tres. (Asuma diferencia en el sombreado)", {"a": "Figura A", "b": "Figura B", "c": "Figura C", "d": "Figura D"}, "d"),
            ("Si el patrón es 'suma 2, resta 1', ¿cuál es el siguiente número: 5, 7, 6, 8, ...?", {"a": "9", "b": "7", "c": "10", "d": "6"}, "b"),
            ("¿Cuál es la regla de transformación: Círculo -> Cuadrado; Triángulo -> ...?", {"a": "Hexágono", "b": "Pentágono", "c": "Círculo", "d": "El número de lados aumenta en 1"}, "d"),
            ("Si una flecha apunta al Norte, luego al Este, luego al Sur, ¿a dónde apunta después?", {"a": "Oeste", "b": "Norte", "c": "Este", "d": "Sur"}, "a"),
            ("¿Qué figura es la versión invertida de la original? (Asuma figura simétrica)", {"a": "Figura A", "b": "Figura B", "c": "Figura C", "d": "Figura D"}, "a"),
            ("Completa la matriz: (1, 2); (3, 4); (5, ...)?", {"a": "7", "b": "6", "c": "9", "d": "10"}, "b"),
        ],
        "Razonamiento Clerical": [
            ("Verifica si los códigos son idénticos: 34567-T vs 34567-T", {"a": "Idénticos", "b": "Diferentes"}, "a"),
            ("Clasifica por orden alfabético: Smith, Jonhson, Sneed", {"a": "Jonhson, Smith, Sneed", "b": "Smith, Jonhson, Sneed", "c": "Sneed, Smith, Jonhson"}, "a"),
            ("Encuentra el error de tipeo en: 'La casa es muy heermosa.'", {"a": "La", "b": "casa", "c": "heermosa", "d": "muy"}, "c"),
            ("¿El número de factura #0012390 es el mismo que #001239?", {"a": "Sí", "b": "No"}, "b"),
            ("Compara las direcciones: Calle 10 Sur, 45-23 vs Calle 10 Sur, 45-32", {"a": "Iguales", "b": "Diferentes"}, "b"),
            ("¿Qué número viene antes de 7890 en orden descendente?", {"a": "7889", "b": "7891", "c": "7800", "d": "7890"}, "b"),
            ("Clasifica estos documentos: Factura, Contrato, Recibo", {"a": "Contrato, Factura, Recibo", "b": "Factura, Contrato, Recibo", "c": "Recibo, Factura, Contrato"}, "a"),
            ("¿El código de producto A-409 es idéntico a A409?", {"a": "Sí", "b": "No"}, "b"),
            ("Encuentra el nombre repetido en la lista: Juan, María, Pedro, Juan", {"a": "Pedro", "b": "María", "c": "Juan", "d": "No hay repetidos"}, "c"),
            ("¿El cheque 10245 es igual al cheque 10245?", {"a": "Sí", "b": "No"}, "a"),
            ("¿Qué nombre iría primero en un archivador: López, Álvarez, Gómez?", {"a": "Álvarez", "b": "Gómez", "c": "López", "d": "Gómez"}, "a"),
            ("Identifica la cantidad incorrecta: $1,000.00 vs $1,000.0", {"a": "Incorrecta", "b": "Correcta"}, "a"),
        ],
        "Razonamiento Técnico": [
            ("Si la presión de un gas en un contenedor aumenta, ¿qué le sucede a la temperatura (volumen constante)?", {"a": "Aumenta", "b": "Disminuye", "c": "Se mantiene igual"}, "a"),
            ("¿Cuál es el propósito de un fusible en un circuito eléctrico?", {"a": "Aumentar la potencia", "b": "Actuar como protección contra sobrecargas", "c": "Regular el voltaje", "d": "Almacenar energía"}, "b"),
            ("¿Cómo se llama la herramienta para apretar o aflojar tuercas y tornillos hexagonales?", {"a": "Martillo", "b": "Serrucho", "c": "Llave inglesa", "d": "Destornillador"}, "c"),
            ("¿Qué tipo de energía se almacena en una batería?", {"a": "Mecánica", "b": "Eléctrica", "c": "Química", "d": "Térmica"}, "c"),
            ("¿Qué es la corrosión?", {"a": "Aumento de la resistencia", "b": "Desgaste por fricción", "c": "Deterioro de un material por reacción química o electroquímica", "d": "Expansión térmica"}, "c"),
            ("¿Cuál es el principio detrás de la soldadura?", {"a": "Fusión de metales para unirlos", "b": "Pegado con adhesivo", "c": "Unión mecánica con tornillos", "d": "Vibración sónica"}, "a"),
            ("Para un cable eléctrico, ¿qué propiedad es clave?", {"a": "Baja conductividad", "b": "Alta resistencia", "c": "Alta conductividad", "d": "Rigidez"}, "c"),
            ("¿Qué significa 'CAD' en el ámbito del diseño?", {"a": "Control de Calidad", "b": "Diseño Asistido por Computadora", "c": "Análisis de Datos", "d": "Código de Acceso"}, "b"),
            ("Si un motor se recalienta, ¿cuál podría ser la causa técnica?", {"a": "Falta de combustible", "b": "Fallo en el sistema de enfriamiento", "c": "Bajo voltaje", "d": "Neumáticos desinflados"}, "b"),
            ("¿Cuál de estos materiales es un buen aislante térmico?", {"a": "Cobre", "b": "Acero", "c": "Madera", "d": "Aluminio"}, "c"),
            ("¿Cuál es la función de una válvula en un sistema hidráulico?", {"a": "Generar presión", "b": "Controlar el flujo del fluido", "c": "Filtrar el aceite", "d": "Medir la temperatura"}, "b"),
            ("La calibración de un instrumento busca:", {"a": "Reparar daños", "b": "Asegurar la precisión de las mediciones", "c": "Cambiar el diseño", "d": "Aumentar la velocidad"}, "b"),
        ],
    }
    
    questions = []
    current_id = 1
    for area_name in AREAS:
        code = APTITUDES_MAP[area_name]["code"]
        items_to_use = test_data.get(area_name)
        
        # Iteramos sobre las preguntas y respuestas reales/simuladas
        for i, (pregunta, opciones, respuesta) in enumerate(items_to_use):
            
            # Formato de opción para Streamlit (a) Opción A
            opciones_formato = {k: v for k, v in opciones.items()}
            
            questions.append({
                "id": current_id, 
                "area": area_name,
                "code": code,
                "pregunta": f"P-{code}-{i+1}. {pregunta}",
                "opciones": opciones_formato, 
                "respuesta_correcta": respuesta 
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
    # HE MODIFICADO LA SEMILLA Y LOS VALORES PARA PROVOCAR DIFERENTES RESULTADOS
    np.random.seed(33) 
    simulated_percentiles = {
        "Razonamiento General": np.random.randint(80, 95),  # Alto potencial
        "Razonamiento Verbal": np.random.randint(75, 90),
        "Razonamiento Numérico": np.random.randint(70, 85),
        "Razonamiento Espacial": np.random.randint(65, 80),
        "Velocidad Perceptiva": np.random.randint(40, 55), # Promedio
        "Precisión Manual": np.random.randint(40, 50),
        "Coordinación Manual": np.random.randint(30, 45), # Promedio Bajo
        "Atención Concentrada": np.random.randint(20, 35), # Bajo
        "Razonamiento Mecánico": np.random.randint(70, 85),
        "Razonamiento Abstracto": np.random.randint(60, 75),
        "Razonamiento Clerical": np.random.randint(85, 98), # Muy alto
        "Razonamiento Técnico": np.random.randint(50, 65)
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
    """Genera un análisis detallado de las fortalezas y debilidades, y el potencial ocupacional.
       LÓGICA ACTUALIZADA PARA ROLES Y MENSAJE NO GENÉRICO."""
    
    df_sorted = df_resultados.sort_values(by='Percentil', ascending=False)
    
 
    # Top 3 Fortalezas
    top_3 = df_sorted.head(3)
    fortalezas_text = "<ul>"
    for index, row in top_3.iterrows():
        # Usamos la lógica de la función get_estrategias_de_mejora para obtener la aplicación clave
        # Intentamos obtener solo la aplicación clave de la estrategia
        estrategia_completa = get_estrategias_de_mejora(row['Área'])
        aplicacion_clave = "aplicación de habilidades complejas" 
        try:
             aplicacion_clave = estrategia_completa.split('**Aplicación:** ')[1].split('.')[0].strip()
        except IndexError:
             pass # Si no encuentra el formato, usa el genérico
             
        fortalezas_text += f"<li>**{row['Área']} ({row['Percentil']:.0f}%)**: Una habilidad sobresaliente en **{row['Área']}** sugiere un alto potencial para **{aplicacion_clave}**.</li>"
    fortalezas_text += "</ul>"
    
    # Bottom 3 a Mejorar
    bottom_3 = df_sorted.tail(3)
    mejoras_text = "<ul>"
    for index, row in bottom_3.iterrows():
        
        mejoras_text += f"<li>**{row['Área']} ({row['Percentil']:.0f}%)**: El desarrollo de **{row['Área']}** debe ser una prioridad, ya que es la base para áreas de procesamiento y detalle. Se sugiere el entrenamiento inmediato en ejercicios de {row['Área'].lower().replace('razonamiento ', '').replace('manual', '').strip()}.</li>"
    mejoras_text += "</ul>"

    # --- LÓGICA CORREGIDA DE POTENCIAL OCUPACIONAL (Basada en la Aptitud con MAYOR PERCENTIL) ---
    top_area = top_3.iloc[0]['Área']
    
    if top_area in ["Razonamiento General", "Razonamiento Verbal", "Razonamiento Numérico"]:
        potencial = "Roles Estratégicos, de Consultoría, Análisis de Alto Nivel, Liderazgo de Proyectos, Finanzas y Alta Dirección (G-Factor)."
        perfil = "Alto Potencial Cognitivo (G-Factor)."
    elif top_area in ["Razonamiento Mecánico", "Razonamiento Espacial", "Razonamiento Técnico"]:
        potencial = "Roles de Ingeniería, Arquitectura, Diseño Industrial, Mantenimiento Técnico Especializado, Electricidad y Diseño de Producto."
        perfil = "Fuerte Perfil Técnico-Estructural."
    elif top_area in ["Razonamiento Clerical", "Razonamiento Abstracto"]:
        potencial = "Roles de Análisis de Datos, Detección de Patrones, Gestión Documental Avanzada, Investigación, Programación Lógica y Auditoría."
        perfil = "Potencial Analítico y Organizativo (R-C Factor)."
    elif top_area in ["Velocidad Perceptiva", "Precisión Manual", "Coordinación Manual", "Atención Concentrada"]:
        # ESTE ES EL 'ELSE' DETALLADO QUE EVITA EL MENSAJE GENÉRICO
        potencial = "Roles Operativos, de Control de Calidad, Logística, Ensamblaje Fino, Tareas de Detalle Repetitivo y Soporte al Cliente (Procesamiento Rápido)."
        perfil = "Sólido Perfil Operativo y de Detalle."
    else: # Por si acaso
        potencial = "Roles Generales Administrativos y de Soporte. Requiere un desarrollo focalizado para especializarse."
        perfil = "Perfil Competitivo General."


    # Roles No Aptos
    roles_no_aptos = []
    for area in bottom_3['Área']:
        if area in ["Razonamiento General", "Razonamiento Verbal", "Razonamiento Numérico"]:
            roles_no_aptos.append("Liderazgo Estratégico y Consultoría (G-Factor)")
        elif area in ["Razonamiento Mecánico", "Razonamiento Espacial", "Razonamiento Técnico"]:
            roles_no_aptos.append("Ingeniería, Mantenimiento Técnico y Diseño de Productos")
        elif area in ["Razonamiento Clerical", "Razonamiento Abstracto"]:
            roles_no_aptos.append("Análisis de Datos, Detección de Patrones y Auditoría Documental")
        else: # Velocidad Perceptiva, Precisión Manual, Coordinación Manual, Atención Concentrada
            roles_no_aptos.append("Operaciones de Detalle, Control de Calidad y Ensamblaje Fino")
    
    roles_no_aptos_text = "<ul>" + "".join(f"<li>{rol}</li>" for rol in sorted(list(set(roles_no_aptos)))) + "</ul>"

    return {
        "fortalezas": fortalezas_text,
        "mejoras": mejoras_text,
        "potencial": potencial,
        "perfil": perfil,
 
        "top_area": top_area,
        "roles_no_aptos": roles_no_aptos_text 
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
    st.title("🧠 Batería de Aptitudes Generales – GATB Profesional")
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
            # No necesitamos lógica adicional aquí, set_stage maneja la transición
            pass 

        if st.button("✨ Resolver Todo (Demo)", type="secondary", use_container_width=True, on_click=solve_all):
            # No necesitamos lógica adicional aquí, solve_all maneja la transición
      
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
                    # Esto asegura que el radio se marque correctamente incluso si el texto completo no está
                    # estrictamente disponible en el estado. Se usa el mapeo del diccionario.
                    default_index = opciones_radio.index(full_option_text)
                except ValueError:
                    # En caso de error, intentamos encontrar la clave de la respuesta en las opciones
                    for i, opt in enumerate(opciones_radio):
                        if opt.startswith(f"{default_value_key})"):
                            default_index = i
                            break
                    if default_index is None:
                       default_index = None # Si no se encuentra, se queda sin selección
            
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
    
    st.title("🏆 Informe Ejecutivo de Perfil Aptitudinal GATB")
    st.markdown("---")
    
    # --- 1. Calificación Global (Resumen Ejecutivo) ---
    avg_percentil = df_resultados['Percentil'].mean()
    calificacion, detalle_calificacion, color_calificacion = calificar_global(avg_percentil)

    st.subheader("1. Resumen Ejecutivo y Perfil Global")
    
    # Contenedor para la calificación global
    st.markdown(f"""
    <div style="background-color: {color_calificacion}; padding: 25px; border-radius: 15px; color: white; margin-bottom: 30px; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,0.4);">
        <h2 style="margin: 0; font-size: 2.5em; font-weight: 900; letter-spacing: 1px;">{calificacion}</h2>
        <p style="margin: 5px 0 0 0; font-size: 1.3em; font-weight: 500;">Percentil Promedio Global: **{avg_percentil:.1f}%**</p>
        <p style="font-size: 1.1em; margin: 10px 0 0 0; border-top: 1px solid rgba(255,255,255,0.5); padding-top: 10px; opacity: 0.9;">**Diagnóstico:** {detalle_calificacion}</p>
 
    </div>
    """, unsafe_allow_html=True)
    
    # Conclusiones del Evaluador
    st.markdown(f"""
    <div style="padding: 15px; border-left: 5px solid #ff9900; background-color: #fff8e1; border-radius: 5px; margin-bottom: 20px;">
        <p style="font-weight: bold; margin: 0;">Conclusiones del Evaluador:</p>
        <p style="margin: 5px 0 0 0;">El perfil muestra una base **{analisis['perfil']}**, con una clara inclinación hacia **{analisis['top_area']}**.
        El individuo es particularmente apto para **{analisis['potencial']}**. Se recomienda un plan de desarrollo focalizado en las áreas de menor rendimiento para lograr un perfil más holístico.</p>
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

    # --- 3. Análisis de Fortalezas y Áreas de Mejora (GRID/COLUMNAS MEJORADAS) ---
    st.subheader("3. Análisis Comparativo del Perfil")
    
    # NUEVA ESTRUCTURA DE COLUMNAS / GRILLA
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
    
    col_apto, col_no_apto = st.columns(2)

    with col_apto:
        st.markdown(f"""
        <div style="padding: 20px; border: 1px solid #4682b4; background-color: #f0f8ff; border-radius: 10px; margin-bottom: 20px;">
            <h5 style="margin-top: 0; color: #4682b4;">✅ Potencial Ocupacional Recomendado (Enfoque Primario)</h5>
            <p style="font-size: 1.1em; font-weight: bold;">{analisis['potencial']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_no_apto:
        st.markdown(f"""
        <div style="padding: 20px; border: 1px solid #dc143c; background-color: #ffeaea; border-radius: 10px; margin-bottom: 20px;">
            <h5 style="margin-top: 0; color: #dc143c;">❌ Roles No Aptos (Evitar por Bajo Desempeño)</h5>
            {analisis['roles_no_aptos']}
            <p style="font-size: 0.9em; margin-top: 10px;">*Requerirían un entrenamiento intensivo y sostenido.</p>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("---")

    # --- 5. Estrategias de Desarrollo ---
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
