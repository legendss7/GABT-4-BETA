import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components 

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
    """Genera preguntas simuladas originales y profesionales."""
    
    # --- PREGUNTAS ACTUALIZADAS Y PROFESIONALES ---
    detailed_questions = {
        "Razonamiento General": [
            {"pregunta": "(Silogismo) Todos los analistas son metódicos. Ningún creativo es analista. ¿Qué se deduce lógicamente?", 
             "opciones": {"a": "Ningún creativo es metódico.", "b": "Algunos metódicos no son creativos.", "c": "Todo metódico es analista.", "d": "Algunos creativos son metódicos."}},
            {"pregunta": "Identifique el elemento que rompe la coherencia semántica en la siguiente serie: Efímero, Fugaz, Transitorio, Perpetuo, Breve.", 
             "opciones": {"a": "Perpetuo", "b": "Efímero", "c": "Fugaz", "d": "Transitorio"}},
            {"pregunta": "Complete la analogía relacional: **Principio** es a **Postulado** como **Objetivo** es a:", 
             "opciones": {"a": "Meta", "b": "Resultado", "c": "Propósito", "d": "Medio"}},
            {"pregunta": "Encuentre el número que continúa la progresión geométrica con patrón de doble suma creciente: 1, 3, 7, 15, 31, ...", 
             "opciones": {"a": "63", "b": "47", "c": "61", "d": "58"}},
            {"pregunta": "Si la afirmación 'La mayoría de los proyectos son exitosos' es falsa, ¿cuál de las siguientes es necesariamente verdadera?", 
             "opciones": {"a": "Muchos proyectos no son exitosos.", "b": "Ningún proyecto es exitoso.", "c": "Todos los proyectos son fallidos.", "d": "Algunos proyectos son muy exitosos."}},
            {"pregunta": "Un cliente devuelve un producto con falla A, que fue causada por un defecto B. Si no se soluciona B, el producto fallará de nuevo. ¿Cuál es la causa raíz?", 
             "opciones": {"a": "El defecto B.", "b": "La falla A.", "c": "La devolución del cliente.", "d": "El producto devuelto."}},
            {"pregunta": "Un algoritmo usa tres condiciones: P (Verdadero), Q (Falso) y R (Verdadero). ¿Cuál es el valor lógico de la expresión (P AND Q) OR R?", 
             "opciones": {"a": "Verdadero", "b": "Falso", "c": "Depende de Q", "d": "Depende de P"}},
            {"pregunta": "Si un vehículo recorre 18 km en 12 minutos, ¿cuánto tiempo tardará en recorrer 45 km a la misma velocidad constante?", 
             "opciones": {"a": "30 minutos", "b": "25 minutos", "c": "32 minutos", "d": "40 minutos"}},
            {"pregunta": "La figura A es una variante incompleta de la figura B. Para completarla, se debe aplicar el concepto de:", 
             "opciones": {"a": "Simetría axial", "b": "Rotación de 90°", "c": "Inversión cromática", "d": "Extensión lineal"}},
            {"pregunta": "Si M está a la izquierda de N, y O está a la derecha de P, y P está a la derecha de N. ¿Cuál es el orden de izquierda a derecha?", 
             "opciones": {"a": "M, N, P, O", "b": "N, M, P, O", "c": "P, N, M, O", "d": "O, P, N, M"}},
            {"pregunta": "El concepto de 'Entropía' en la termodinámica se relaciona mejor con el principio de:", 
             "opciones": {"a": "Desorden y tendencia al equilibrio", "b": "Conservación de la energía", "c": "Transferencia de calor por convección", "d": "Trabajo y potencia"}},
            {"pregunta": "En la frase 'El comité **consideró** la propuesta cuidadosamente', la palabra resaltada implica una acción de:", 
             "opciones": {"a": "Evaluación", "b": "Aprobación", "c": "Descarte", "d": "Presentación"}}
        ],
        "Razonamiento Verbal": [
            {"pregunta": "Sinónimo contextual más adecuado para la palabra **'Acuciante'** en la frase: 'Una necesidad acuciante de liquidez'.", 
             "opciones": {"a": "Apremiante", "b": "Molesta", "c": "Lejana", "d": "Extraña"}},
            {"pregunta": "Antónimo más preciso de la palabra **'Prosaico'**:", 
             "opciones": {"a": "Exquisito", "b": "Ordinario", "c": "Simple", "d": "Común"}},
            {"pregunta": "Elija la analogía correcta: **Escultor** es a **Cincel** como **Escritor** es a:", 
             "opciones": {"a": "Pluma", "b": "Libro", "c": "Lector", "d": "Tinta"}},
            {"pregunta": "Definición más exacta de la palabra **'Recalcitrante'**:", 
             "opciones": {"a": "Terco, opuesto a obedecer o cambiar.", "b": "Que se repite con frecuencia.", "c": "Que carece de color.", "d": "Que es muy antiguo."}},
            {"pregunta": "La frase **'Hacer mutis por el foro'** en lenguaje coloquial significa:", 
             "opciones": {"a": "Retirarse discretamente de un lugar.", "b": "Hablar en voz baja.", "c": "Asumir un papel principal.", "d": "Aparecer de repente."}},
            {"pregunta": "Identifique el error de concordancia en la frase:", 
             "opciones": {"a": "La gente estuvo de acuerdo con los resultados.", "b": "Los libros y las revistas está organizado.", "c": "Los informes fueron revisados.", "d": "Mi equipo y yo viajamos."}},
            {"pregunta": "Elija el prefijo que significa **'totalidad'** o **'entero'**:", 
             "opciones": {"a": "Omni-", "b": "Hipo-", "c": "Extra-", "d": "Sub-"}},
            {"pregunta": "La palabra **'Exacerbar'** significa:", 
             "opciones": {"a": "Irritar o agravar un sentimiento o dolor.", "b": "Disminuir la intensidad de algo.", "c": "Alabar en exceso.", "d": "Entender un concepto."}},
            {"pregunta": "Sustituya la palabra **'Inefable'** en la frase: 'Una belleza inefable.'", 
             "opciones": {"a": "Indescriptible", "b": "Fea", "c": "Común", "d": "Oscura"}},
            {"pregunta": "El término **'Pleonasmo'** se refiere a:", 
             "opciones": {"a": "Uso de palabras innecesarias que refuerzan lo dicho.", "b": "Elipsis de una palabra.", "c": "Comparación directa.", "d": "Metáfora."}},
            {"pregunta": "Una persona **'lúcida'** es aquella que posee:", 
             "opciones": {"a": "Claridad mental y raciocinio.", "b": "Mucha fuerza física.", "c": "Poca energía.", "d": "Una voz muy fuerte."}},
            {"pregunta": "Elija el concepto que **NO** se relaciona con la retórica:", 
             "opciones": {"a": "Aritmética", "b": "Persuasión", "c": "Oratoria", "d": "Discurso"}}
        ],
        "Razonamiento Numérico": [
            {"pregunta": "Resuelva: $\\frac{2}{5} + \\frac{1}{10} - \\frac{1}{2} = $", 
             "opciones": {"a": "0", "b": "1/10", "c": "3/5", "d": "-1/2"}},
            {"pregunta": "Calcule el 15% del 40% de 500.", 
             "opciones": {"a": "30", "b": "20", "c": "45", "d": "60"}},
            {"pregunta": "Si el área de un círculo es $16\\pi \\text{ cm}^2$, ¿cuál es la longitud de su circunferencia?", 
             "opciones": {"a": "$8\\pi$ cm", "b": "$4\\pi$ cm", "c": "$16\\pi$ cm", "d": "$32\\pi$ cm"}},
            {"pregunta": "Un inversor compra acciones por $1200 y las vende por $1500. ¿Cuál es el porcentaje de ganancia sobre el costo?", 
             "opciones": {"a": "25%", "b": "20%", "c": "30%", "d": "15%"}},
            {"pregunta": "¿Qué número continúa la serie cuadrática: 2, 5, 10, 17, 26, ...?", 
             "opciones": {"a": "37", "b": "35", "c": "40", "d": "39"}},
            {"pregunta": "Si un automóvil gasta 5 litros de combustible para recorrer 60 km, ¿cuántos litros necesita para un viaje de 180 km?", 
             "opciones": {"a": "15 litros", "b": "12 litros", "c": "18 litros", "d": "20 litros"}},
            {"pregunta": "Despeje el valor de $x$ en la ecuación: $3(x - 2) = 2x + 8$", 
             "opciones": {"a": "14", "b": "10", "c": "12", "d": "16"}},
            {"pregunta": "El precio de un producto, incluyendo el IVA (19%), es de $119.00. ¿Cuál es el precio base sin IVA?", 
             "opciones": {"a": "$100.00", "b": "$99.00", "c": "$105.00", "d": "$95.00"}},
            {"pregunta": "Calcule el volumen de un prisma rectangular con dimensiones de 4 cm x 5 cm x 10 cm.", 
             "opciones": {"a": "$200 \\text{ cm}^3$", "b": "$190 \\text{ cm}^3$", "c": "$180 \\text{ cm}^3$", "d": "$90 \\text{ cm}^3$"}},
            {"pregunta": "Si 8 obreros tardan 6 días en hacer una zanja, ¿cuánto tardarán 4 obreros con la misma eficiencia?", 
             "opciones": {"a": "12 días", "b": "10 días", "c": "8 días", "d": "9 días"}},
            {"pregunta": "El promedio de 4 números es 15. Si se añade un quinto número (25), ¿cuál es el nuevo promedio?", 
             "opciones": {"a": "17", "b": "18", "c": "19", "d": "20"}},
            {"pregunta": "Si la raíz cuadrada de $Y$ es 9, ¿cuánto es el valor de $2Y + 5$?", 
             "opciones": {"a": "167", "b": "162", "c": "157", "d": "170"}}
        ],
        "Razonamiento Espacial": [
            {"pregunta": "(Visualización 3D) Si se rota un cubo 90° sobre su eje vertical (eje Y) y luego se invierte verticalmente (eje X), ¿cuál es la orientación de la cara superior (Simulación)?", 
             "opciones": {"a": "Queda en la posición frontal izquierda.", "b": "Queda en la posición inferior.", "c": "Vuelve a la posición original.", "d": "Queda en la posición frontal derecha."}},
            {"pregunta": "Identifique la figura que corresponde a la vista en planta (superior) de un cono truncado (Simulación).", 
             "opciones": {"a": "Dos círculos concéntricos.", "b": "Un círculo con una línea central.", "c": "Un óvalo.", "d": "Un cuadrado."}},
            {"pregunta": "Al desdoblar un patrón de papel doblado en tercios y cortado con una forma de diamante en el centro, ¿cuántos cortes se aprecian?", 
             "opciones": {"a": "Tres cortes de diamante alineados.", "b": "Dos cortes de diamante.", "c": "Un solo corte grande.", "d": "Cuatro cortes de diamante."}},
            {"pregunta": "De un set de 4 piezas, ¿cuál es la pieza faltante para completar un cuadrado perfecto mediante el proceso de teselación?", 
             "opciones": {"a": "La pieza que completa la geometría y encaja.", "b": "Una pieza simétrica al original.", "c": "La pieza más pequeña.", "d": "Una pieza con curva."}},
            {"pregunta": "Si un objeto se ilumina desde el lado superior derecho, ¿hacia dónde se proyectará la sombra de mayor longitud?", 
             "opciones": {"a": "Hacia el lado inferior izquierdo.", "b": "Directamente hacia abajo.", "c": "Hacia el lado superior izquierdo.", "d": "Hacia el centro."}},
            {"pregunta": "Cuál es el resultado de superponer un triángulo equilátero sobre un cuadrado, alineando sus bases (Simulación).", 
             "opciones": {"a": "Un pentágono irregular.", "b": "Un hexágono.", "c": "Un trapecio.", "d": "Un rectángulo."}},
            {"pregunta": "Una flecha apunta al Norte. Si gira 135° en sentido horario, ¿hacia dónde apunta ahora?", 
             "opciones": {"a": "Sureste", "b": "Noreste", "c": "Suroeste", "d": "Oeste"}},
            {"pregunta": "Elija la representación bidimensional que se obtiene al cortar un cilindro por un plano diagonal (Simulación).", 
             "opciones": {"a": "Un óvalo (elipse).", "b": "Un círculo.", "c": "Un rectángulo.", "d": "Un trapezoide."}},
            {"pregunta": "Si la figura de un reloj se refleja en un espejo horizontal (eje X), ¿la imagen reflejada mantendrá la misma hora si es simétrica?", 
             "opciones": {"a": "Sí, si la hora es simétrica (Ej: 9:00, 3:00).", "b": "No, siempre cambia.", "c": "Sí, en todas las horas.", "d": "Solo si es un reloj digital."}},
            {"pregunta": "Determine la figura que se obtiene al unir un cubo y una pirámide cuadrada por sus bases, sin solapamiento.", 
             "opciones": {"a": "Un poliedro de 9 caras.", "b": "Un dodecaedro.", "c": "Un prisma hexagonal.", "d": "Un cono."}},
            {"pregunta": "Cuál de estas formas planas NO puede formar un poliedro al doblarse: Un triángulo, un cuadrado, o un patrón en forma de T.", 
             "opciones": {"a": "La forma en T.", "b": "El cuadrado.", "c": "El triángulo.", "d": "Cualquiera puede formarlo."}},
            {"pregunta": "Si la figura A está a la izquierda de B, y B está rotada 45° con respecto a C. ¿Cuál es la relación espacial más probable entre A y C?", 
             "opciones": {"a": "A está ligeramente desalineada con C.", "b": "A está directamente encima de C.", "c": "A está directamente debajo de C.", "d": "A y C son paralelas."}}
        ],
        "Velocidad Perceptiva": [
            {"pregunta": "Identifique el código IDÉNTICO a 58R39A-JL45B, sin errores de tipografía o espaciado:", 
             "opciones": {"a": "58R39A-JL45B", "b": "58R39A JL45B", "c": "58B39A-JL45B", "d": "58R39A-JLA5B"}},
            {"pregunta": "¿Cuál de las siguientes direcciones postales es DIFERENTE a las demás?:", 
             "opciones": {"a": "Av. Colón 1234, Of. 5B", "b": "Av. Colon 1234, Of. 5B", "c": "Av. Colón 1234, Of. 5B", "d": "Av. Colón 1234, Of. 5B"}},
            {"pregunta": "Encuentre el único número que NO contiene el dígito '7' en la siguiente lista:", 
             "opciones": {"a": "54826", "b": "75421", "c": "67390", "d": "12753"}},
            {"pregunta": "¿Cuántos errores de mayúsculas (minúscula donde va mayúscula o viceversa) hay en la frase: 'El sistema de gestión de calidaD (SGC)'?", 
             "opciones": {"a": "1", "b": "2", "c": "0", "d": "3"}},
            {"pregunta": "Busque la secuencia de letras que NO se repite en la siguiente fila: XYZ, ABC, XYZ, CBA, XYZ, ABC.", 
             "opciones": {"a": "CBA", "b": "XYZ", "c": "ABC", "d": "Todas se repiten."}},
            {"pregunta": "Compare las cifras: 1.567.890 vs 1'567'890. ¿Son iguales o diferentes en valor numérico?", 
             "opciones": {"a": "Iguales", "b": "Diferentes", "c": "Depende de la región", "d": "No se puede determinar"}},
            {"pregunta": "¿Cuál de estos nombres y apellidos está mal transcrito respecto a 'Martínez Pérez, Juan G.'?", 
             "opciones": {"a": "Martinez Peréz, Juan G.", "b": "Martínez Pérez, Juan G.", "c": "Martínez Pérez, Juan G.", "d": "Martínez Pérez, Juan G."}},
            {"pregunta": "Encuentre el código de producto que NO es alfanumérico (solo números):", 
             "opciones": {"a": "789012", "b": "A789B", "c": "890C12", "d": "D789E"}},
            {"pregunta": "¿Cuántas veces aparece la conjunción 'que' en el siguiente texto corto? 'Dile que venga y que traiga el informe que te pedí'", 
             "opciones": {"a": "3", "b": "2", "c": "4", "d": "1"}},
            {"pregunta": "Identifique el número de factura que coincide exactamente con: INV-2024/05-334", 
             "opciones": {"a": "INV-2024/05-334", "b": "INV-2024/05-343", "c": "INB-2024/05-334", "d": "INV-2024/05-330"}},
            {"pregunta": "Localice el único símbolo diferente entre: # # # @ # # #", 
             "opciones": {"a": "@", "b": "#", "c": "No hay diferente", "d": "Depende del contexto"}},
            {"pregunta": "¿Cuál de las siguientes parejas de palabras es idéntica?:", 
             "opciones": {"a": "Sistema/Sistema", "b": "Proceso/Proseso", "c": "Análisis/Analisis", "d": "Gerencia/Gerenciaa"}}
        ],
        "Precisión Manual": [
            {"pregunta": "(Simulación de Trazo Fino) Elija el punto que se encuentra a 0.5 mm del centro del objetivo (Simulación gráfica).", 
             "opciones": {"a": "Punto A (más cercano al centro)", "b": "Punto B", "c": "Punto C", "d": "Punto D (más alejado)"}},
            {"pregunta": "(Simulación de Ensamblaje) Identifique la micro-pieza que encaja perfectamente sin solapamiento en la ranura (Simulación gráfica).", 
             "opciones": {"a": "Pieza con tolerancia de 0.01mm", "b": "Pieza con tolerancia de 0.1mm", "c": "Pieza con margen de 1mm", "d": "Pieza demasiado grande"}},
            {"pregunta": "(Simulación de Alineación) Seleccione el par de líneas paralelas cuya separación es constante y exacta (Simulación gráfica).", 
             "opciones": {"a": "Líneas A (mejor alineación)", "b": "Líneas B", "c": "Líneas C", "d": "Líneas D (desviación visible)"}},
            {"pregunta": "(Simulación de Medición) Un vernier marca 45.20 mm. ¿Cuál es el error de lectura si el objeto real mide 45.25 mm?", 
             "opciones": {"a": "0.05 mm por defecto", "b": "0.05 mm por exceso", "c": "0.20 mm", "d": "0.25 mm"}},
            {"pregunta": "(Simulación de Detalle) ¿Cuál de los siguientes dibujos a escala tiene el mayor nivel de detalle de las uniones?", 
             "opciones": {"a": "Dibujo A (mayor densidad de líneas)", "b": "Dibujo B", "c": "Dibujo C", "d": "Dibujo D (boceto)"}},
            {"pregunta": "(Simulación de Recorte) Se requiere un corte de papel a lo largo de una curva de radio 10 cm. ¿Cuál trazo demuestra la mayor consistencia?", 
             "opciones": {"a": "Trazo 1 (radio uniforme)", "b": "Trazo 2 (radio variable)", "c": "Trazo 3 (línea recta)", "d": "Trazo 4 (línea entrecortada)"}},
            {"pregunta": "(Simulación de Manipulación) Para realizar una soldadura de precisión en un componente SMD (dispositivo de montaje superficial), ¿qué cualidad es más crítica?", 
             "opciones": {"a": "Pulso firme y control microscópico.", "b": "Rapidez en el movimiento.", "c": "Fuerza manual.", "d": "Resistencia a la temperatura."}},
            {"pregunta": "(Simulación de Pintura) Seleccione el área donde la aplicación del pigmento respeta el límite exacto del borde (Simulación gráfica).", 
             "opciones": {"a": "Área 1 (sin desbordes)", "b": "Área 2 (ligero desborde)", "c": "Área 3 (gran desborde)", "d": "Área 4 (incompleta)"}},
            {"pregunta": "(Simulación de Equilibrio) Al colocar un objeto pequeño sobre una superficie, ¿qué posición minimiza el riesgo de caída por inestabilidad?", 
             "opciones": {"a": "La posición con la base más amplia y centro de gravedad bajo.", "b": "La posición con la base más pequeña.", "c": "La posición vertical alta.", "d": "Cualquier posición es estable."}},
            {"pregunta": "(Simulación de Enfoque) Para leer un texto de letra muy pequeña, ¿qué factor de visión es más relevante?", 
             "opciones": {"a": "Agudeza visual y capacidad de enfoque.", "b": "Visión periférica.", "c": "Velocidad de lectura.", "d": "Visión de colores."}},
            {"pregunta": "(Simulación de Trazado) Dibuje una circunferencia de 3 cm de diámetro. ¿Qué resultado es el más preciso con respecto al radio?", 
             "opciones": {"a": "Un radio de 1.5 cm.", "b": "Un radio de 3.0 cm.", "c": "Un diámetro de 1.5 cm.", "d": "Un radio de 2.0 cm."}},
            {"pregunta": "(Simulación) ¿Cuál es el movimiento de mano requerido para introducir un hilo en el ojo de una aguja?", 
             "opciones": {"a": "Movimiento lento, controlado y preciso.", "b": "Movimiento rápido y brusco.", "c": "Movimiento de rotación.", "d": "Movimiento de barrido."}}
        ],
        "Coordinación Manual": [
            {"pregunta": "(Simulación de Patrón) Para replicar el patrón rítmico 'Palmada-Golpe-Silencio', ¿qué combinación motora requiere la mejor coordinación?", 
             "opciones": {"a": "Sincronización de manos y cuerpo con pausas temporales.", "b": "Solo coordinación de manos.", "c": "Solo coordinación de voz.", "d": "Coordinación de pies."}},
            {"pregunta": "(Simulación de Trayectoria) Si debe seguir una línea curva y un punto de cruce simultáneamente, ¿qué tipo de control se exige?", 
             "opciones": {"a": "Control dual y anticipación visomotora.", "b": "Solo velocidad de reacción.", "c": "Solo precisión estática.", "d": "Control de respiración."}},
            {"pregunta": "(Simulación de Instrumento) La acción de operar un freno de mano mientras se presiona el embrague en un vehículo requiere:", 
             "opciones": {"a": "Coordinación bimanual y bipedal asimétrica.", "b": "Coordinación solo de las manos.", "c": "Solo fuerza en las piernas.", "d": "Visión de túnel."}},
            {"pregunta": "(Simulación de Secuencia) Una cadena de producción requiere: Agarrar (Mano Izq.), Girar (Mano Der.), Soltar (Mano Izq.). ¿Qué habilidad se mide principalmente?", 
             "opciones": {"a": "Secuenciación y ritmo en la alternancia motora.", "b": "Velocidad perceptiva.", "c": "Precisión manual.", "d": "Fuerza de agarre."}},
            {"pregunta": "(Simulación de Mando) En un simulador, ¿qué movimiento de joystick compensa una desviación de trayectoria en diagonal?", 
             "opciones": {"a": "Movimiento compuesto (ejes X e Y simultáneos).", "b": "Movimiento solo en eje X.", "c": "Movimiento solo en eje Y.", "d": "Un movimiento de rotación."}},
            {"pregunta": "(Simulación de Destreza) Lanzar un objeto a un blanco en movimiento exige la coordinación de:", 
             "opciones": {"a": "Cálculo de trayectoria, velocidad de brazo y liberación oportuna.", "b": "Solo fuerza de lanzamiento.", "c": "Solo enfoque visual.", "d": "Control de respiración."}},
            {"pregunta": "(Simulación de Respuesta) El estímulo es una luz roja. La respuesta es presionar un botón con el pie. ¿Qué factor puede causar el mayor retraso en la acción?", 
             "opciones": {"a": "Tiempo de reacción psicomotora (Ojo-Pie).", "b": "La fuerza del pie.", "c": "La luminosidad de la luz.", "d": "El color del botón."}},
            {"pregunta": "(Simulación) Para martillar un clavo, se requiere la coordinación de:", 
             "opciones": {"a": "Visión, sujeción y movimiento rítmico del brazo.", "b": "Solo fuerza bruta.", "c": "Solo la precisión de la punta.", "d": "Velocidad de la mano."}},
            {"pregunta": "La habilidad de operar un montacargas moviendo la palanca de dirección y la palanca de elevación simultáneamente, mide la aptitud de:", 
             "opciones": {"a": "Coordinación motora compleja (independencia de miembros).", "b": "Velocidad de percepción.", "c": "Razonamiento espacial.", "d": "Atención concentrada."}},
            {"pregunta": "(Simulación de Ritmo) ¿Cuál es la cualidad motora clave para mantener un ritmo constante al escribir a máquina (mecanografía)?", 
             "opciones": {"a": "Ritmo de pulsación y sincronización de dedos.", "b": "Fuerza en los dedos.", "c": "Memoria muscular.", "d": "Conocimiento del teclado."}},
            {"pregunta": "(Simulación) Si debe pasar un objeto de una mano a la otra a gran velocidad, ¿qué aptitud es esencial para evitar la caída?", 
             "opciones": {"a": "Coordinación bimanual y timing.", "b": "Fuerza en los dedos.", "c": "Precisión manual.", "d": "Velocidad perceptiva."}},
            {"pregunta": "El acto de lanzar una jabalina requiere una coordinación que involucra principalmente:", 
             "opciones": {"a": "Coordinación global del cuerpo, equilibrio y secuencia cinética.", "b": "Solo la fuerza del brazo.", "c": "Solo el impulso de las piernas.", "d": "Precisión manual."}}
        ],
        "Atención Concentrada": [
            {"pregunta": "¿Cuántos números '9' se pueden contar en la siguiente línea de datos, sin errores de omisión o doble conteo?: 1923945967891290", 
             "opciones": {"a": "5", "b": "4", "c": "6", "d": "3"}},
            {"pregunta": "Encuentre el error de transcripción en la serie de códigos de barras (Busque el código diferente): A45B90-D, A45B90-D, A45B90-E, A45B90-D", 
             "opciones": {"a": "A45B90-E", "b": "A45B90-D", "c": "A45B90-D (el primero)", "d": "No hay errores"}},
            {"pregunta": "Si tiene una lista de 500 ítems y debe verificar que cada código empieza con 'INV-', ¿qué aptitud se mide primariamente?", 
             "opciones": {"a": "Atención sostenida y selectiva.", "b": "Velocidad perceptiva.", "c": "Razonamiento Clerical.", "d": "Memoria a corto plazo."}},
            {"pregunta": "Al corregir un informe de 10 páginas, ¿cuál es el error más difícil de detectar si la atención decae?", 
             "opciones": {"a": "Errores sutiles de puntuación o concordancia.", "b": "Errores obvios de ortografía.", "c": "Errores de formato.", "d": "Errores de impresión."}},
            {"pregunta": "Localice el valor de inventario que NO coincide en las dos columnas: Columna A: [150, 200, 310, 450]; Columna B: [150, 200, 301, 450]", 
             "opciones": {"a": "310/301", "b": "150/150", "c": "200/200", "d": "450/450"}},
            {"pregunta": "En un texto, la palabra 'documentos' aparece 4 veces. Si se le pide contarlas sin marcar el texto, ¿qué proceso cognitivo está bajo prueba?", 
             "opciones": {"a": "Foco y conteo mental.", "b": "Memoria de largo plazo.", "c": "Razonamiento abstracto.", "d": "Visión periférica."}},
            {"pregunta": "¿Cuántas letras 'S' en mayúscula se encuentran en el siguiente fragmento: 'SISTEMA de gestión de Seguridad e Higiene'?", 
             "opciones": {"a": "3", "b": "4", "c": "2", "d": "5"}},
            {"pregunta": "Si un auditor verifica que un procedimiento de 8 pasos se haya cumplido rigurosamente, ¿qué tipo de atención se necesita en el paso 5?", 
             "opciones": {"a": "Atención focalizada y sostenida.", "b": "Atención dividida.", "c": "Distracción.", "d": "Atención pasiva."}},
            {"pregunta": "En una matriz de 10x10 llena de letras 'X' y un único 'Y', ¿cuánto tiempo tarda en promedio una persona para localizar la 'Y'?", 
             "opciones": {"a": "Depende de la capacidad de exploración visual (selectiva).", "b": "Menos de 1 segundo.", "c": "Más de 1 minuto.", "d": "Depende de la fuerza."}},
            {"pregunta": "Determine el único número impar en la serie: 2, 4, 6, 8, 11, 12, 14.", 
             "opciones": {"a": "11", "b": "8", "c": "2", "d": "14"}},
            {"pregunta": "La capacidad de ignorar un ruido fuerte mientras se completa una tarea de cálculo mide:", 
             "opciones": {"a": "Atención selectiva (resistencia a la distracción).", "b": "Coordinación manual.", "c": "Velocidad perceptiva.", "d": "Memoria."}},
            {"pregunta": "¿Cuál es la hora marcada por un reloj si las manecillas están en 12 y 6, y se pide ignorar el color (Simulación)?", 
             "opciones": {"a": "6:00 (o 18:00)", "b": "12:30", "c": "6:30", "d": "12:00"}}
        ],
        "Razonamiento Mecánico": [
            {"pregunta": "En un sistema de poleas, si se desea levantar una carga de 100 kg con una fuerza de 50 kg, ¿cuántas poleas móviles mínimas se necesitan idealmente?", 
             "opciones": {"a": "Una polea móvil.", "b": "Dos poleas móviles.", "c": "Ninguna.", "d": "Cuatro poleas fijas."}},
            {"pregunta": "Si se aumenta el radio de la rueda motriz (engranaje de entrada) en un sistema de engranajes, ¿cómo afecta esto la velocidad del engranaje conducido?", 
             "opciones": {"a": "Disminuye la velocidad del engranaje conducido.", "b": "Aumenta la velocidad del engranaje conducido.", "c": "No afecta la velocidad.", "d": "Afecta solo la fuerza."}},
            {"pregunta": "¿Qué ley de la física establece que 'la energía no se crea ni se destruye, solo se transforma'?", 
             "opciones": {"a": "Principio de conservación de la energía.", "b": "Primera Ley de Newton.", "c": "Ley de Ohm.", "d": "Principio de Arquímedes."}},
            {"pregunta": "¿Qué clase de palanca es una carretilla, donde la carga (resistencia) está entre el punto de apoyo y la fuerza aplicada (esfuerzo)?", 
             "opciones": {"a": "Palanca de Segundo Grado.", "b": "Palanca de Primer Grado.", "c": "Palanca de Tercer Grado.", "d": "Cuarta clase."}},
            {"pregunta": "En un circuito hidráulico, ¿qué componente es responsable de convertir la energía de presión del fluido en movimiento mecánico lineal?", 
             "opciones": {"a": "Cilindro hidráulico (actuador).", "b": "Bomba.", "c": "Válvula de control.", "d": "Reservorio."}},
            {"pregunta": "Si un resorte se estira el doble de su longitud inicial (dentro del límite elástico), ¿cómo varía la fuerza requerida?", 
             "opciones": {"a": "Se duplica la fuerza (Ley de Hooke).", "b": "Se cuadruplica la fuerza.", "c": "Se reduce a la mitad.", "d": "Permanece constante."}},
            {"pregunta": "¿Cuál es la función principal de un condensador en un circuito eléctrico de corriente continua (DC)?", 
             "opciones": {"a": "Almacenar energía eléctrica temporalmente.", "b": "Regular el flujo de corriente.", "c": "Convertir AC a DC.", "d": "Actuar como interruptor."}},
            {"pregunta": "Para apretar un tornillo con mayor torque (fuerza de giro), ¿qué se debe hacer con la llave o herramienta?", 
             "opciones": {"a": "Aumentar la longitud del brazo de palanca (mango).", "b": "Disminuir la longitud del brazo de palanca.", "c": "Aplicar más velocidad.", "d": "Usar menos fricción."}},
            {"pregunta": "Si se enciende un motor y empieza a vibrar excesivamente, la causa más probable de esta vibración es:", 
             "opciones": {"a": "Un desequilibrio en las piezas giratorias.", "b": "Un aumento de voltaje.", "c": "Una baja temperatura.", "d": "Demasiada lubricación."}},
            {"pregunta": "¿Qué principio explica por qué un barco flota en el agua?", 
             "opciones": {"a": "Principio de Arquímedes (fuerza de flotación).", "b": "Ley de Pascal.", "c": "Principio de Bernoulli.", "d": "Ley de gravitación universal."}},
            {"pregunta": "Si una viga está apoyada en ambos extremos y se le aplica una carga en el centro, ¿dónde se produce la mayor tensión de flexión?", 
             "opciones": {"a": "En el centro de la viga.", "b": "En los puntos de apoyo.", "c": "Uniformemente a lo largo de la viga.", "d": "En la parte superior."}},
            {"pregunta": "En un circuito en serie, si una resistencia se quema (circuito abierto), ¿qué sucede con la corriente que fluye por las demás resistencias?", 
             "opciones": {"a": "El circuito se abre y la corriente se detiene por completo.", "b": "La corriente aumenta.", "c": "La corriente solo disminuye ligeramente.", "d": "La corriente se mantiene igual."}}
        ],
        "Razonamiento Abstracto": [
            {"pregunta": "Identifique la figura que completa la matriz 3x3, aplicando la regla de que la tercera columna es la inversión de la primera (Simulación gráfica).", 
             "opciones": {"a": "La figura reflejada del patrón opuesto.", "b": "La misma figura que el centro.", "c": "Un cuadrado vacío.", "d": "Un círculo sombreado."}},
            {"pregunta": "Encuentre el patrón de la secuencia figurativa: Triángulo (negro), Cuadrado (blanco), Pentágono (negro), Hexágono (blanco), ...", 
             "opciones": {"a": "Heptágono (negro).", "b": "Octágono (blanco).", "c": "Círculo (negro).", "d": "Rombo (blanco)."}},
            {"pregunta": "La figura A se transforma en B por **Rotación** y **Cambio de color**. ¿Qué transformación aplica B para convertirse en C (Simulación)?", 
             "opciones": {"a": "Reflexión vertical y adición de un elemento.", "b": "Solo cambio de posición.", "c": "Rotación de 180°.", "d": "Eliminación del color."}},
            {"pregunta": "Si el símbolo [A] significa 'SUMAR' y el símbolo [B] significa 'INVERTIR', ¿cuál es el resultado de [A] (X, Y) y luego [B] (Resultado)?", 
             "opciones": {"a": "La suma de X e Y, luego reflejada.", "b": "Solo la suma de X e Y.", "c": "La inversión de X e Y.", "d": "El producto de X e Y."}},
            {"pregunta": "Elija la figura que NO pertenece al grupo, pues es la única que tiene un número impar de lados y está sombreada.", 
             "opciones": {"a": "Figura 1 (un pentágono sombreado).", "b": "Figura 2 (un cuadrado vacío).", "c": "Figura 3 (un círculo sombreado).", "d": "Figura 4 (un hexágono vacío)."}},
            {"pregunta": "El conjunto de figuras de la izquierda obedece a la regla 'Tiene líneas rectas'. ¿Cuál de las figuras de la derecha pertenece al conjunto?", 
             "opciones": {"a": "Una figura con solo líneas rectas.", "b": "Una figura con líneas curvas.", "c": "Un círculo.", "d": "Un óvalo."}},
            {"pregunta": "Si un patrón de puntos se mueve una posición hacia la derecha y se añade un nuevo punto. ¿Cuál es el patrón que sigue (Simulación)?", 
             "opciones": {"a": "El patrón con un punto adicional desplazado.", "b": "El patrón original sin cambios.", "c": "El patrón con un punto eliminado.", "d": "El patrón movido hacia arriba."}},
            {"pregunta": "La figura final es la intersección de dos figuras iniciales. ¿Cuál es la figura que se obtuvo (Simulación)?", 
             "opciones": {"a": "La figura que corresponde al área común.", "b": "La figura que corresponde a la suma de áreas.", "c": "La figura inicial más grande.", "d": "La figura inicial más pequeña."}},
            {"pregunta": "En la secuencia ▵, ▿, ▹, ◃, ¿cuál es el movimiento de transformación que se aplica en cada paso?", 
             "opciones": {"a": "Rotación de 90° en sentido horario.", "b": "Reflexión vertical.", "c": "Rotación de 45°.", "d": "Inversión."}},
            {"pregunta": "Complete la relación: Círculo (pequeño) es a Círculo (grande), como Cuadrado (rayado) es a:", 
             "opciones": {"a": "Cuadrado (rayado, grande).", "b": "Cuadrado (vacío, grande).", "c": "Círculo (rayado, grande).", "d": "Rectángulo (rayado)."}},
            {"pregunta": "Si el color representa la magnitud y la forma el tipo. Un Círculo Azul es a un Cuadrado Rojo, como un Triángulo Grande es a:", 
             "opciones": {"a": "Un Círculo Pequeño.", "b": "Un Cuadrado Azul.", "c": "Un Triángulo Rojo.", "d": "Un Pentágono Grande."}},
            {"pregunta": "¿Qué figura completa la serie lógica: El primer elemento más el segundo dan el tercero (Simulación)?", 
             "opciones": {"a": "La figura resultante de la combinación de reglas.", "b": "La figura idéntica al segundo elemento.", "c": "La figura idéntica al primer elemento.", "d": "Una figura nueva sin patrón."}}
        ],
        "Razonamiento Clerical": [
            {"pregunta": "¿Cuál es el orden alfabético-numérico correcto para archivar los siguientes códigos?: INV-2024-A, INV-2023-B, INV-2024-C, INV-2023-A.", 
             "opciones": {"a": "INV-2023-A, INV-2023-B, INV-2024-A, INV-2024-C", "b": "INV-2024-A, INV-2024-C, INV-2023-A, INV-2023-B", "c": "INV-2023-B, INV-2023-A, INV-2024-C, INV-2024-A", "d": "INV-2024-C, INV-2024-A, INV-2023-B, INV-2023-A"}},
            {"pregunta": "Identifique el error de transcripción en la siguiente lista de nombres y números de identificación:", 
             "opciones": {"a": "Juan Pérez | 56-432-198-7", "b": "Juan Pérez | 56-432-189-7", "c": "Juan Pérez | 56-432-198-7", "d": "Juan Pérez | 56-432-198-7"}},
            {"pregunta": "Si se utiliza el sistema de archivo LIFO (Last In, First Out), ¿cuál de los siguientes documentos debe retirarse primero?", 
             "opciones": {"a": "Documento con la última fecha de ingreso.", "b": "Documento con la primera fecha de ingreso.", "c": "El documento más importante.", "d": "El documento con menos páginas."}},
            {"pregunta": "¿Cuál es la fecha que NO corresponde al formato DÍA/MES/AÑO (DD/MM/AAAA) en la siguiente lista?: 15/01/2024, 31/04/2023, 01/12/2025.", 
             "opciones": {"a": "31/04/2023 (Abril solo tiene 30 días).", "b": "15/01/2024", "c": "01/12/2025", "d": "Todas son correctas."}},
            {"pregunta": "En un registro contable, ¿cuál es el campo más importante para asegurar la trazabilidad del movimiento de fondos?", 
             "opciones": {"a": "El número de asiento y la fecha.", "b": "El nombre del cliente.", "c": "El tipo de cambio.", "d": "La descripción breve."}},
            {"pregunta": "Determine cuántos errores de puntuación (puntos y comas faltantes) hay en la siguiente frase: 'El informe esta listo pero falta la firma del director'", 
             "opciones": {"a": "2 (falta coma y punto final)", "b": "1 (falta solo el punto final)", "c": "3 (falta coma, punto y dos puntos)", "d": "0"}},
            {"pregunta": "Si un archivo debe ser indexado por nombre, luego por fecha y finalmente por departamento, ¿cuál es el criterio de tercer nivel?", 
             "opciones": {"a": "Departamento.", "b": "Nombre.", "c": "Fecha.", "d": "Tipo de documento."}},
            {"pregunta": "En una hoja de cálculo, ¿cuál de estas celdas no está en el rango A1:C5?", 
             "opciones": {"a": "D2", "b": "B3", "c": "A5", "d": "C1"}},
            {"pregunta": "Calcule la diferencia de inventario entre el registro de entrada (450 unidades) y el registro de salida (385 unidades).", 
             "opciones": {"a": "65 unidades restantes.", "b": "75 unidades restantes.", "c": "85 unidades faltantes.", "d": "55 unidades restantes."}},
            {"pregunta": "¿Cuál es el código que se repite en la lista: S789-A, S789-B, S798-A, S789-A?", 
             "opciones": {"a": "S789-A", "b": "S789-B", "c": "S798-A", "d": "Todos son únicos."}},
            {"pregunta": "La habilidad para organizar información de manera secuencial y lógica se relaciona directamente con:", 
             "opciones": {"a": "Razonamiento Clerical.", "b": "Razonamiento Abstracto.", "c": "Coordinación Manual.", "d": "Precisión Manual."}},
            {"pregunta": "¿Qué nombre debe ir al principio de una lista alfabética?: Pérez, Castro, Díaz, Alonso.", 
             "opciones": {"a": "Alonso", "b": "Castro", "c": "Díaz", "d": "Pérez"}}
        ],
        "Razonamiento Técnico": [
            {"pregunta": "En un circuito eléctrico, si el voltaje (V) es constante, ¿cómo se relaciona la corriente (I) con la resistencia (R) (Ley de Ohm)?", 
             "opciones": {"a": "La corriente es inversamente proporcional a la resistencia.", "b": "La corriente es directamente proporcional a la resistencia.", "c": "La resistencia no afecta la corriente.", "d": "Son independientes."}},
            {"pregunta": "¿Qué herramienta es la más precisa para medir el diámetro interior de un orificio?", 
             "opciones": {"a": "Calibrador (Vernier) con mordazas internas.", "b": "Cinta métrica.", "c": "Regla graduada.", "d": "Micrómetro de exteriores."}},
            {"pregunta": "¿Cuál es la función principal de una válvula de retención (check valve) en un sistema de tuberías?", 
             "opciones": {"a": "Permitir el flujo en una sola dirección.", "b": "Regular el caudal.", "c": "Reducir la presión.", "d": "Detener el flujo completamente."}},
            {"pregunta": "En una red informática, si el *ping* entre dos equipos es alto y errático, ¿cuál es la causa técnica más probable?", 
             "opciones": {"a": "Latencia y congestión en la red.", "b": "Baja velocidad de la CPU.", "c": "Falta de espacio en disco.", "d": "Cable de alimentación suelto."}},
            {"pregunta": "Si un transformador tiene 100 vueltas en el primario y 50 en el secundario, y se aplica 120V al primario, ¿cuál es el voltaje de salida ideal?", 
             "opciones": {"a": "60V", "b": "240V", "c": "120V", "d": "30V"}},
            {"pregunta": "¿Qué tipo de esfuerzo soporta un cable que se utiliza para izar una carga verticalmente?", 
             "opciones": {"a": "Tensión (tracción).", "b": "Compresión.", "c": "Cizalladura.", "d": "Flexión."}},
            {"pregunta": "Para mejorar la eficiencia térmica de un motor, ¿qué se puede hacer con el sistema de refrigeración?", 
             "opciones": {"a": "Aumentar la superficie de intercambio de calor (radiador).", "b": "Disminuir la presión del refrigerante.", "c": "Usar menos refrigerante.", "d": "Aumentar la temperatura del motor."}},
            {"pregunta": "Un motor de combustión interna tiene un ciclo de cuatro tiempos (admisión, compresión, combustión, escape). ¿En qué tiempo se produce el trabajo útil?", 
             "opciones": {"a": "Combustión (expansión).", "b": "Admisión.", "c": "Compresión.", "d": "Escape."}},
            {"pregunta": "Identifique el diagrama de flujo que representa un circuito en **paralelo**.", 
             "opciones": {"a": "Un circuito con componentes conectados en diferentes ramas.", "b": "Un circuito con componentes conectados en serie.", "c": "Un circuito con una sola rama.", "d": "Un circuito abierto."}},
            {"pregunta": "¿Cuál es el propósito del control de realimentación (feedback loop) en un sistema automatizado?", 
             "opciones": {"a": "Comparar la salida con la entrada deseada para corregir el error.", "b": "Aumentar la velocidad de operación.", "c": "Disminuir la potencia de entrada.", "d": "Eliminar la necesidad de sensores."}},
            {"pregunta": "Si un fusible se funde repetidamente, ¿cuál es la causa técnica subyacente más probable?", 
             "opciones": {"a": "Un cortocircuito o una sobrecarga persistente.", "b": "Un voltaje bajo.", "c": "Un cable demasiado largo.", "d": "Un ambiente frío."}},
            {"pregunta": "En un plano de arquitectura, el símbolo de dos líneas paralelas con una separación entre ellas representa comúnmente:", 
             "opciones": {"a": "Una pared o muro con separación de aire.", "b": "Una ventana.", "c": "Una puerta.", "d": "Una columna."}}
        ]
    }
    
    questions = []
    current_id = 1
    for area_name in AREAS:
        spec = APTITUDES_MAP.get(area_name)
        code = spec["code"]
            
        for i in range(N_PREGUNTAS_POR_AREA):
            q_data = detailed_questions[area_name][i]
            
            # Usamos las opciones profesionales, pero forzamos 'a' como la correcta para la simulación
            q_opciones = q_data["opciones"]
            expected_answer = "a" 
            
            questions.append({
                "id": current_id, 
                "area": area_name,
                "code": code,
                "pregunta": f"P{code}-{i+1}. {q_data['pregunta']}",
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

# --- 4. FUNCIONES DE REPORTE PROFESIONAL (ANÁLISIS) ---

def get_analisis_detalle(df_resultados):
    """Genera un análisis detallado de las fortalezas y debilidades, y el potencial ocupacional."""
    
    df_sorted = df_resultados.sort_values(by='Percentil', ascending=False)
    
    # Top 3 Fortalezas
    top_3 = df_sorted.head(3)
    fortalezas_text = "<ul>"
    for index, row in top_3.iterrows():
        # Mapeo de descripción de fortalezas
        desc_map = {
            "Razonamiento General": "abstracción, juicio lógico y resolución de problemas complejos.",
            "Razonamiento Verbal": "comunicación ejecutiva, redacción de informes y comprensión de textos.",
            "Razonamiento Numérico": "cálculo rápido, análisis cuantitativo y toma de decisiones financieras.",
            "Razonamiento Espacial": "visualización 3D, lectura de planos y modelado conceptual.",
            "Velocidad Perceptiva": "revisión rápida, control de calidad visual y cotejo de datos.",
            "Precisión Manual": "manipulación fina, micro-ensamblaje y tareas que exigen detalle minucioso.",
            "Coordinación Manual": "operación de maquinaria, conducción y sincronización ojo-mano-pie.",
            "Atención Concentrada": "foco sostenido, resistencia a la distracción y auditoría de datos.",
            "Razonamiento Mecánico": "diagnóstico de fallas en sistemas físicos y comprensión de principios de ingeniería.",
            "Razonamiento Abstracto": "detección de patrones no verbales, pensamiento lateral e innovación.",
            "Razonamiento Clerical": "organización, archivo, gestión documental y verificación de registros.",
            "Razonamiento Técnico": "aplicación de conocimientos de electricidad, electrónica y mecánica.",
        }
        key_application = desc_map.get(row['Área'], "habilidades cognitivas generales.")
        fortalezas_text += f"<li>**{row['Área']} ({row['Percentil']:.1f}%)**: Una habilidad sobresaliente en esta área sugiere un alto potencial para la **{key_application}**.</li>"
    fortalezas_text += "</ul>"
    
    # Bottom 3 a Mejorar
    bottom_3 = df_sorted.tail(3)
    mejoras_text = "<ul>"
    for index, row in bottom_3.iterrows():
        # Mapeo de descripción de mejoras
        desc_map_improvement = {
            "Razonamiento General": "el desarrollo de estrategias lógicas y análisis de inferencias.",
            "Razonamiento Verbal": "la claridad, la estructura del lenguaje y la amplitud del vocabulario técnico.",
            "Razonamiento Numérico": "la agilidad y precisión en el manejo de datos y problemas aritméticos.",
            "Razonamiento Espacial": "la capacidad de rotación mental y la interpretación de diagramas.",
            "Velocidad Perceptiva": "la eficiencia en la búsqueda y comparación de información detallada.",
            "Precisión Manual": "la exactitud y el control motor fino en tareas de manipulación.",
            "Coordinación Manual": "la sincronización entre los sentidos y los movimientos del cuerpo.",
            "Atención Concentrada": "el mantenimiento del foco en tareas monótonas o de larga duración.",
            "Razonamiento Mecánico": "la comprensión de sistemas de fuerza, movimiento y fluidos.",
            "Razonamiento Abstracto": "la identificación de reglas subyacentes en patrones no figurativos.",
            "Razonamiento Clerical": "la organización, el ordenamiento y la verificación de información alfanumérica.",
            "Razonamiento Técnico": "la aplicación práctica de conocimientos de electricidad o instrumentación.",
        }
        improvement_focus = desc_map_improvement.get(row['Área'], "la mejora de habilidades básicas.")
        mejoras_text += f"<li>**{row['Área']} ({row['Percentil']:.1f}%)**: Esta área requiere enfoque. El entrenamiento debe priorizar **{improvement_focus}**.</li>"
    mejoras_text += "</ul>"

    # Potencial Ocupacional (Basado en el perfil simulado)
    top_area = top_3.iloc[0]['Área']
    if top_area in ["Razonamiento Abstracto", "Razonamiento General", "Razonamiento Numérico"]:
        potencial = "Roles Estratégicos, de Análisis Avanzado, Liderazgo, I+D y Consultoría."
        perfil = "Alto Potencial Cognitivo (G-Factor) y Capacidad Analítica Avanzada."
    elif top_area in ["Razonamiento Mecánico", "Razonamiento Espacial", "Razonamiento Técnico", "Coordinación Manual"]:
        potencial = "Roles de Ingeniería, Diseño, Mantenimiento Industrial, Arquitectura y Operación de Maquinaria Pesada."
        perfil = "Fuerte Perfil Técnico-Estructural y Habilidad Visomotora."
    else:
        potencial = "Roles Administrativos, de Control de Calidad, Logística, Soporte al Cliente y Operaciones de Detalle."
        perfil = "Sólido Perfil Operativo y de Detalle (Foco en Velocidad, Precisión y Atención)."

    return {
        "fortalezas": fortalezas_text,
        "mejoras": mejoras_text,
        "potencial": potencial,
        "perfil": perfil,
        "top_area": top_area
    }


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
        
        <p>El perfil aptitudinal, reflejado en el **Gráfico de Radar**, muestra una forma **{'equilibrada' if abs(max_percentil - min_percentil) < 40 else 'puntiaguda y desequilibrada'}**. Esto indica que el evaluado tiene una distribución de habilidades {'relativamente homogénea.' if abs(max_percentil - min_percentil) < 40 else 'con marcados picos y valles.'}</p>

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
        Esta prueba simula una evaluación aptitudinal de alto nivel, midiendo su potencial en **12 áreas cognitivas y motrices** fundamentales para el éxito profesional. Las preguntas han sido redactadas para ser profesionales y originales (sin violación de derechos de autor).
        
        **🎯 Estructura del Test:**
        - **Total de Aptitudes Evaluadas:** **{len(AREAS)}**
        - **Total de Preguntas:** **{N_TOTAL_PREGUNTAS}** (12 ítems por área)
        - **Resultado:** Informe profesional con análisis de percentiles, fortalezas y plan de desarrollo.
        
        **🔍 Áreas Clave:** Razonamiento (General, Verbal, Numérico, Abstracto), Habilidades Operativas (Clerical, Perceptiva) y Factores Psicomotores (Precisión, Coordinación).
        """)
        
        st.markdown("""
        **Guía Rápida de Inicio:**
        1. **Concentración:** Asegúrese de estar en un ambiente libre de distracciones.
        2. **Honestidad:** Responda según su mejor juicio.
        3. **Navegación:** Al hacer click en 'Siguiente', la página se actualizará y el **scroll volverá al inicio** de la nueva sección.
        """)
    
    with col_start:
        st.subheader("Iniciar Test")
        st.warning("⚠️ **Nota de Simulación:** Esta es una prueba demostrativa. Los resultados y el análisis son ilustrativos.")
        
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
            
            # Formato de opciones: 'a) Respuesta A (Correcta Simulada)'
            opciones_dict = row['opciones']
            opciones_radio = [f"{k}) {v}" for k, v in opciones_dict.items()]
            
            default_value_key = st.session_state.respuestas.get(pregunta_id)
            default_index = None
            if default_value_key:
                # Buscamos la opción completa para establecer el índice por defecto
                full_option_text = f"{default_value_key}) {opciones_dict[default_value_key]}"
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
                    # Extrae solo la letra de la opción ('a', 'b', 'c', 'd')
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

        # Resumen Detallado de Interpretación
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
