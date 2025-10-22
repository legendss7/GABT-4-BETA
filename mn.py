import streamlit as st
import pandas as pd
import numpy as np
import time

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="Batería de Aptitudes GATB Profesional")

# Colocamos un ancla invisible al inicio de la página para referencia, aunque el scroll se modificará.
st.html('<a id="top-anchor"></a>')

# Mapeo de Aptitudes (se mantiene)
APTITUDES_MAP = {
    "Razonamiento General": {"code": "G", "color": "#1f77b4"}, # Azul
    "Razonamiento Verbal": {"code": "V", "color": "#ff7f0e"}, # Naranja
    "Razonamiento Numérico": {"code": "N", "color": "#2ca02c"}, # Verde
    "Razonamiento Espacial": {"code": "S", "color": "#d62728"}, # Rojo
    "Velocidad Perceptiva": {"code": "P", "color": "#9467bd"}, # Morado
    "Precisión Manual": {"code": "Q", "color": "#8c564b"}, # Marrón
    "Coordinación Manual": {"code": "K", "color": "#e377c2"}, # Rosa
    "Atención Concentrada": {"code": "A", "color": "#7f7f7f"}, # Gris
    "Razonamiento Mecánico": {"code": "M", "color": "#bcbd22"}, # Oliva
    "Razonamiento Abstracto": {"code": "R", "color": "#17becf"}, # Cian
    "Razonamiento Clerical": {"code": "C", "color": "#98df8a"}, # Verde Menta
    "Razonamiento Técnico": {"code": "T", "color": "#ff9896"}, # Rojo Claro
}
AREAS = list(APTITUDES_MAP.keys())
N_PREGUNTAS_POR_AREA = 12

# --- SOLUCIÓN SCROLL MODIFICADA (NO AL TOP ABSOLUTO) ---
def scroll_to_not_top():
    """
    Injecta JS para forzar el scroll a una posición que NO es el top (ej. 400px abajo).
    Esto evita subir agresivamente al inicio de la página.
    """
    js_code = """
        <script>
            setTimeout(function() {
                // Scroll a una posición fija (ej. 400px) para evitar el tope absoluto.
                window.parent.scrollTo({ top: 400, behavior: 'auto' });
                
                // Intento alternativo para contenedores de Streamlit
                var mainContent = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                if (mainContent) {
                    mainContent.scrollTo({ top: 400, behavior: 'auto' });
                }
            }, 250);
        </script>
        """
    st.html(js_code)


# Clasificación y Calificación Global (se mantiene la lógica)
def clasificar_percentil(porcentaje):
    if porcentaje >= 90: return 96, "Superior (90-99)"
    elif porcentaje >= 80: return 88, "Alto (80-89)"
    elif porcentaje >= 60: return 70, "Promedio Alto (60-79)"
    elif porcentaje >= 40: return 50, "Promedio (40-59)"
    elif porcentaje >= 20: return 30, "Promedio Bajo (20-39)"
    elif porcentaje >= 10: return 15, "Bajo (10-19)"
    else: return 5, "Muy Bajo (0-9)"

def calificar_global(avg_percentil):
    if avg_percentil >= 85: return "Potencial Ejecutivo 🌟", "El perfil indica un potencial excepcionalmente alto y equilibrado para roles directivos, estratégicos y de alta complejidad. Capacidad de aprendizaje superior y adaptación rápida a cualquier entorno.", "#008000"
    elif avg_percentil >= 65: return "Nivel Profesional Avanzado 🏆", "El perfil es sólido, con fortalezas claras y un buen balance aptitudinal. Excelente para roles técnicos especializados, de gestión de proyectos y consultoría.", "#4682b4"
    elif avg_percentil >= 40: return "Perfil Competitivo 💼", "El perfil se sitúa en el promedio superior, demostrando suficiencia en todas las áreas. Apto para la mayoría de roles operativos y de coordinación. Requiere enfoque en el desarrollo de fortalezas clave.", "#ff8c00"
    else: return "Período de Desarrollo 🛠️", "El perfil requiere un período de enfoque intensivo en el desarrollo de aptitudes clave. Se recomienda comenzar con roles de soporte y entrenamiento continuo.", "#dc143c"

# --- GENERACIÓN DE PREGUNTAS (Se mantiene, solo se añade el Dataframe) ---
def generate_gatb_questions():
    """Genera 144 preguntas simuladas para el test GATB con redacción revisada."""
    # (El contenido detallado de las 144 preguntas se omite aquí por espacio, 
    # pero se asume que la estructura de 'test_data' es la misma que la provista
    # en la iteración anterior, con 12 items por área y redacción revisada.)
    
    # Datos específicos para cada factor (ejemplos funcionales con redacción revisada)
    test_data = {
        "Razonamiento General": {
            "code": "G",
            "type": "Analogías y Series Lógicas",
            "items": [
                ("HACHA es a MADERA como CINCEL es a...", {"a": "Pintura", "b": "Metal", "c": "Escultura", "d": "Papel"}, "c"),
                ("Complete la serie: $2, 5, 11, 23, ?$", {"a": "45", "b": "47", "c": "49", "d": "51"}, "b"),
                ("Día es a LUZ como Noche es a...", {"a": "Luna", "b": "Estrellas", "c": "Oscuridad", "d": "Silencio"}, "c"),
                ("Si ARBOL vale $7$ y FLOR vale $6$, ¿cuánto vale AGUA?", {"a": "5", "b": "6", "c": "7", "d": "8"}, "a"),
                ("¿Cuál palabra no pertenece al grupo? Piano, Violín, Guitarra, Tambor, Trompeta.", {"a": "Piano", "b": "Violín", "c": "Tambor", "d": "Trompeta"}, "c"),
                ("Complete la serie: $8, 11, 15, 20, ?$", {"a": "26", "b": "27", "c": "28", "d": "29"}, "a"),
                ("PILOTO es a AVIÓN como CAPITÁN es a...", {"a": "Barco", "b": "Puerto", "c": "Tripulación", "d": "Mar"}, "a"),
                ("Figura geométrica: ¿Qué sigue? Cuadrado, Triángulo, Círculo, Cuadrado, Triángulo, ?", {"a": "Cuadrado", "b": "Círculo", "c": "Rombo", "d": "Estrella"}, "b"),
                ("La excepción: Gato, Perro, Vaca, Pollo, Caballo.", {"a": "Gato", "b": "Perro", "c": "Vaca", "d": "Pollo"}, "d"),
                ("Si $3=9$ y $4=16$, ¿qué es $7$?", {"a": "49", "b": "21", "c": "14", "d": "35"}, "a"),
                ("Libro es a PÁGINA como ÁRBOL es a...", {"a": "Raíz", "b": "Bosque", "c": "Hoja", "d": "Fruto"}, "c"),
                ("Continúe la secuencia: $Z, X, V, T, ?$", {"a": "S", "b": "R", "c": "Q", "d": "P"}, "b"),
            ]
        },
        "Razonamiento Verbal": {
            "code": "V",
            "type": "Vocabulario: Sinónimos y Antónimos",
            "items": [
                ("Sinónimo de 'EFÍMERO'.", {"a": "Duradero", "b": "Fugaz", "c": "Eterno", "d": "Grande"}, "b"),
                ("Antónimo de 'OPULENCIA'.", {"a": "Riqueza", "b": "Afluencia", "c": "Pobreza", "d": "Magnificencia"}, "c"),
                ("Sinónimo de 'PERSPICACIA'.", {"a": "Torpeza", "b": "Clarividencia", "c": "Obstrucción", "d": "Duda"}, "b"),
                ("Antónimo de 'TACITURNO'.", {"a": "Melancólico", "b": "Alegre", "c": "Callado", "d": "Reservado"}, "b"),
                ("Sinónimo de 'CONCISO'.", {"a": "Extenso", "b": "Breve", "c": "Vago", "d": "Detallado"}, "b"),
                ("Antónimo de 'DILECTO'.", {"a": "Querido", "b": "Estimado", "c": "Odiado", "d": "Predilecto"}, "c"),
                ("Sinónimo de 'SUTILEZA'.", {"a": "Brusquedad", "b": "Delicadeza", "c": "Grosería", "d": "Fuerza"}, "b"),
                ("Antónimo de 'INSIPIDEZ'.", {"a": "Sabor", "b": "Hastío", "c": "Neutralidad", "d": "Suavidad"}, "a"),
                ("Sinónimo de 'VEHEMENTE'.", {"a": "Calmado", "b": "Apático", "c": "Impetuoso", "d": "Lento"}, "c"),
                ("Antónimo de 'PROFANAR'.", {"a": "Desacralizar", "b": "Respetar", "c": "Violentar", "d": "Degradar"}, "b"),
                ("Sinónimo de 'PRISTINO'.", {"a": "Antiguo", "b": "Novedoso", "c": "Corrupto", "d": "Inicial"}, "d"),
                ("Antónimo de 'INOCUO'.", {"a": "Inofensivo", "b": "Dañino", "c": "Benigno", "d": "Suave"}, "b"),
            ]
        },
        "Razonamiento Numérico": {
            "code": "N",
            "type": "Cálculo y Problemas Aritméticos",
            "items": [
                ("Resuelva: $72 \div 9 + 4 \times 3 - 10$.", {"a": "6", "b": "10", "c": "12", "d": "14"}, "b"),
                ("Si una camisa cuesta $45 y tiene un $20\%$ de descuento, ¿cuál es su precio final?", {"a": "$36", "b": "$38", "c": "$40", "d": "$42"}, "a"),
                ("¿Cuál es el siguiente número primo después de $29$?", {"a": "31", "b": "33", "c": "35", "d": "37"}, "a"),
                ("Calcule el promedio de: $15, 25, 10, 30$.", {"a": "18", "b": "20", "c": "22", "d": "25"}, "b"),
                ("¿Qué número completa la fracción? $\\frac{3}{4} = \\frac{?}{16}$", {"a": "9", "b": "12", "c": "15", "d": "18"}, "b"),
                ("Un coche viaja a $60$ km/h. ¿Cuánto tardará en recorrer $210$ km?", {"a": "3 horas", "b": "3.5 horas", "c": "4 horas", "d": "4.5 horas"}, "b"),
                ("Resuelva: $\\frac{1}{2} + \\frac{1}{4}$.", {"a": "1/3", "b": "3/4", "c": "2/6", "d": "1/8"}, "b"),
                ("Si tiene $5$ cajas con $8$ manzanas cada una, y regala $12$ manzanas, ¿cuántas le quedan?", {"a": "28", "b": "32", "c": "40", "d": "24"}, "a"),
                ("¿Qué número es el doble de $14$ y la mitad de $56$?", {"a": "24", "b": "28", "c": "32", "d": "36"}, "b"),
                ("Si $x-5 = 12$, ¿cuánto es $x+5$?", {"a": "17", "b": "22", "c": "27", "d": "10"}, "b"),
                ("Un reloj adelanta $3$ minutos cada hora. ¿Cuánto adelanta en $5$ horas?", {"a": "12 minutos", "b": "15 minutos", "c": "18 minutos", "d": "20 minutos"}, "b"),
                ("Resuelva: $10^2 - 5^2$.", {"a": "50", "b": "75", "c": "100", "d": "25"}, "b"),
            ]
        },
        "Razonamiento Espacial": {
            "code": "S",
            "type": "Visualización y Rotación 3D",
            "items": [
                ("¿Qué figura resulta al rotar $90^{\circ}$ a la derecha un cuadrado con un triángulo sombreado en la esquina superior izquierda?", {"a": "Opción A (Triángulo en esquina superior derecha)", "b": "Opción B (Triángulo en esquina inferior derecha)", "c": "Opción C (Triángulo en esquina inferior izquierda)", "d": "Opción D (Triángulo en esquina superior izquierda)"}, "b"),
                ("Si se pliega un cubo desde su plantilla, ¿qué cara queda opuesta a la cara con un círculo?", {"a": "Una estrella", "b": "Un triángulo", "c": "Un cuadrado", "d": "Un punto"}, "a"),
                ("Imagine una $L$ mayúscula. Si la gira $180^{\circ}$, ¿cómo se ve?", {"a": "L invertida", "b": "L reflejada", "c": "J", "d": "Una $T$"}, "c"),
                ("De las siguientes figuras $A, B, C, D$, ¿cuál no se puede obtener girando la figura $A$?", {"a": "Figura B", "b": "Figura C", "c": "Figura D", "d": "Todas se pueden obtener"}, "c"),
                ("Si un reloj está a las 3:00, ¿qué hora marcaría en un espejo?", {"a": "9:00", "b": "3:00", "c": "6:00", "d": "12:00"}, "a"),
                ("Identifique el objeto 3D que se ve desde arriba como un círculo y desde el lado como un cuadrado.", {"a": "Cono", "b": "Cilindro", "c": "Esfera", "d": "Cubo"}, "b"),
                ("¿Cuál es la vista frontal de una pirámide de base cuadrada?", {"a": "Cuadrado", "b": "Triángulo", "c": "Trapecio", "d": "Pentágono"}, "b"),
                ("Si dobla una hoja a la mitad y luego la corta en el centro, ¿cuántos agujeros obtiene al desdoblarla?", {"a": "1", "b": "2", "c": "3", "d": "4"}, "b"),
                ("¿Qué figura sigue en la secuencia de pliegues? Pliegue horizontal $\to$ Pliegue vertical $\to$ Corte en diagonal.", {"a": "Triángulo", "b": "Círculo", "c": "Rombo", "d": "Dos triángulos"}, "c"),
                ("Si un punto está en la parte inferior de una figura, ¿dónde estará después de rotarla $270^{\circ}$ a la izquierda?", {"a": "Parte superior", "b": "Parte derecha", "c": "Parte izquierda", "d": "Parte inferior"}, "b"),
                ("¿Cuál figura ($A, B, C, D$) es la reflexión de la figura $A$?", {"a": "Figura A (misma)", "b": "Figura B", "c": "Figura C", "d": "Figura D (reflexión)"}, "d"),
                ("Si un objeto tiene $5$ caras, ¿cuál podría ser?", {"a": "Cubo", "b": "Pirámide de base triangular", "c": "Prisma rectangular", "d": "Tubo"}, "b"),
            ]
        },
        "Velocidad Perceptiva": {
            "code": "P",
            "type": "Comparación Rápida de Pares",
            "items": [
                ("Identifique el par IGUAL: A) $7T84P/7T84R$, B) $5E62M/5E62M$, C) $P01V9/P0IV9$, D) $WX3ZA/WX3ZE$", {"a": "A", "b": "B", "c": "C", "d": "D"}, "b"),
                ("Identifique el par DIFERENTE: A) $93X61/93X61$, B) $LMN77/LMN77$, C) $F2Y5Q/F2Y5R$, D) $B8D1K/B8D1K$", {"a": "A", "b": "B", "c": "C", "d": "D"}, "c"),
                ("¿Cuál es el par de números telefónicos idénticos? (A) $555-4321$, (B) $555-4321$, (C) $555-1234$, (D) $555-4321$", {"a": "A y C", "b": "B y D", "c": "A y B", "d": "A, B y D"}, "d"),
                ("¿Cuántas veces aparece el código 'TRX' en esta lista? TRX, TRW, T RX, TYX, TRX, TRX.", {"a": "2", "b": "3", "c": "4", "d": "5"}, "b"),
                ("Encuentre el par exacto: A) $G2H5K - G2H5K$, B) $1A3B5 - 1A3BS$, C) $PQR9 - PQR09$, D) $8Y7Z - 8YIZ$", {"a": "A", "b": "B", "c": "C", "d": "D"}, "a"),
                ("¿Cuál nombre está mal escrito si el original es 'Hernández González'? A) Fernandez González, B) Hernández Gonzalez, C) Hernández González, D) Hernández Gnzalez", {"a": "A", "b": "B", "c": "C", "d": "D"}, "d"),
                ("Identifique el error en la secuencia de dígitos: $12345678901234567890123456789$.", {"a": "Falta el $1$", "b": "Hay un $9$ repetido", "c": "Está incompleta", "d": "No hay error visible"}, "d"),
                ("Encuentre la dirección que no se repite: A) Calle Sol 15, B) Calle Sol 15, C) Av. Luna 22, D) Calle Sol 15", {"a": "A", "b": "B", "c": "C", "d": "D"}, "c"),
                ("¿Qué código es diferente? ZB890, ZB89O, ZB890, ZB890.", {"a": "ZB890", "b": "ZB89O", "c": "Son iguales", "d": "ZB890 (el tercero)"}, "b"),
                ("Marque el único par que son exactamente iguales: (A) $3K7R / 3K7R$, (B) $\$50.00 / \$500.0$, (C) $M1XQ / MI XQ$, (D) $9A2B / 9A2V$", {"a": "A", "b": "B", "c": "C", "d": "D"}, "a"),
                ("¿Cuál factura es idéntica? A) $F45-A1 / F45-A1$, B) $F45-A1 / F45-A7$, C) $F45-A1 / F4S-A1$, D) $F45-A1 / F45-1A$", {"a": "A", "b": "B", "c": "C", "d": "D"}, "a"),
                ("Encuentre el grupo donde todos los elementos son idénticos: (A) L10, L10, L11. (B) R9W, R9W, R9W. (C) T2Z, T2Z, T3Z.", {"a": "A", "b": "B", "c": "C", "d": "Ninguno"}, "b"),
            ]
        },
        "Precisión Manual": {
            "code": "Q",
            "type": "Detalle Fino y Coordinación (Simulado)",
            "items": [
                ("En un plano de circuito, ¿cuál es el símbolo de una resistencia?", {"a": "Rectángulo con líneas", "b": "Círculo con cruz", "c": "Dos líneas paralelas", "d": "Flecha en diagonal"}, "a"),
                ("Para ensamblar un reloj de pulsera, ¿qué herramienta requiere mayor control de fuerza mínima?", {"a": "Pinzas", "b": "Destornillador grande", "c": "Martillo", "d": "Llave inglesa"}, "a"),
                ("Si un punto está ligeramente fuera de un círculo, ¿qué acción es más difícil de realizar con precisión?", {"a": "Mover el punto adentro", "b": "Mover el punto afuera", "c": "Dibujar otro círculo", "d": "Borrar el punto"}, "a"),
                ("Identifique el error de alineación más pequeño en el siguiente diagrama de barras ($A, B, C, D$).", {"a": "Barra A", "b": "Barra B", "c": "Barra C", "d": "Barra D (ligero desnivel)"}, "d"),
                ("Al escribir a mano, la precisión manual es necesaria para controlar...", {"a": "El vocabulario", "b": "La gramática", "c": "El tamaño de la letra", "d": "La velocidad de lectura"}, "c"),
                ("¿Qué representa la pequeña desviación en la línea roja de este gráfico?", {"a": "Una tendencia", "b": "Un error de medición", "c": "Un valor máximo", "d": "Un promedio"}, "b"),
                ("Si necesita pegar una etiqueta de $1$mm $\\times 1$mm, ¿qué aptitud es más relevante?", {"a": "Fuerza", "b": "Velocidad", "c": "Precisión", "d": "Razonamiento"}, "c"),
                ("En una muestra de tejido, ¿qué detalle requiere mayor precisión al ser examinado con un microscopio?", {"a": "El color general", "b": "La forma de la célula", "c": "El brillo de la muestra", "d": "El tamaño del campo visual"}, "b"),
                ("¿Qué acción en la siguiente secuencia requiere más precisión: A) Cortar, B) Llenar, C) Lijar, D) Pegar un borde fino?", {"a": "A", "b": "B", "c": "C", "d": "D"}, "d"),
                ("Para un cirujano, la Precisión Manual es más importante que la Coordinación Manual para...", {"a": "Correr a urgencias", "b": "Suturar un vaso fino", "c": "Levantar un peso", "d": "Hablar con el paciente"}, "b"),
                ("En la impresión, la nitidez de un borde es una medida de...", {"a": "Velocidad", "b": "Precisión", "c": "Color", "d": "Contraste"}, "b"),
                ("Si debe mover un objeto diminuto con un palillo, ¿qué cualidad de movimiento es clave?", {"a": "Rapidez impulsiva", "b": "Movimiento tembloroso", "c": "Control sutil", "d": "Fuerza bruta"}, "c"),
            ]
        },
        "Coordinación Manual": {
            "code": "K",
            "type": "Control Ojo-Mano y Movimiento (Simulado)",
            "items": [
                ("Al conducir un vehículo, ¿qué acción combina mejor la Coordinación Manual?", {"a": "Mirar el paisaje", "b": "Acelerar y girar el volante", "c": "Escuchar música", "d": "Detener el motor"}, "b"),
                ("¿Qué secuencia de movimientos requiere un ritmo continuo y suave?", {"a": "Martillar un clavo", "b": "Escribir un texto largo en teclado", "c": "Atarse los zapatos", "d": "Levantar una caja"}, "b"),
                ("Para trazar una línea curva perfecta con una pluma, ¿qué factor es predominante?", {"a": "Fuerza del brazo", "b": "Coordinación Ojo-Mano", "c": "Rapidez mental", "d": "Peso del papel"}, "b"),
                ("En un videojuego, la habilidad de seguir un objetivo en movimiento mientras se dispara requiere:", {"a": "Memoria", "b": "Coordinación Manual", "c": "Razonamiento verbal", "d": "Toma de decisiones"}, "b"),
                ("Si ensambla un mueble, ¿qué paso exige más Coordinación Manual: A) Clasificar piezas, B) Leer el manual, C) Insertar un tornillo mientras sostiene la pieza, D) Pintar el mueble?", {"a": "A", "b": "B", "c": "d", "d": "C"}, "d"),
                ("¿Cuál actividad motriz es puramente secuencial y rítmica?", {"a": "Levantar pesas", "b": "Caminar", "c": "Lanzar un dardo", "d": "Barrer el suelo"}, "d"),
                ("La capacidad de mantener el equilibrio mientras se manipula un objeto pesado es un ejemplo de:", {"a": "Fuerza bruta", "b": "Precisión Manual", "c": "Coordinación Global", "d": "Agilidad mental"}, "c"),
                ("Si un pintor de brocha gorda cubre una pared, ¿qué movimiento requiere la mejor Coordinación?", {"a": "Abrir el bote de pintura", "b": "Aplicar la pintura en trazos uniformes", "c": "Limpiar el pincel", "d": "Mezclar colores"}, "b"),
                ("¿Qué requiere más Coordinación Manual en el boxeo?", {"a": "Respirar", "b": "Bloquear un golpe", "c": "Lanzar un jab y recuperarse", "d": "Mantener la postura"}, "c"),
                ("Para un guitarrista, la acción de la mano derecha al rasguear requiere...", {"a": "Concentración", "b": "Coordinación Rítmica", "c": "Fuerza", "d": "Velocidad perceptiva"}, "b"),
                ("De los siguientes, ¿cuál es un acto de Precisión Manual más que Coordinación? A) Escribir en un pizarrón, B) Enhebrar una aguja, C) Jugar al tenis, D) Batear en béisbol.", {"a": "A", "b": "B", "c": "C", "d": "D"}, "b"),
                ("La coordinación manual se mide típicamente por:", {"a": "El peso que se levanta", "b": "La velocidad del movimiento", "c": "El control y la fluidez del movimiento", "d": "La memoria muscular"}, "c"),
            ]
        },
        "Atención Concentrada": {
            "code": "A",
            "type": "Vigilancia y Detección de Errores",
            "items": [
                ("¿Cuántas letras 'e' minúsculas hay en el siguiente texto? 'El experto examinó el expediente y encontró que el error se debe a la excesiva envergadura del esfuerzo.'", {"a": "10", "b": "11", "c": "12", "d": "13"}, "c"),
                ("En la lista de códigos, ¿cuál NO es 'X793R'? $X793R, X793R, X793R, X793S$.", {"a": "El primero", "b": "El segundo", "c": "El tercero", "d": "El cuarto"}, "d"),
                ("Cuente el número de veces que aparece el dígito '5' en la serie: $125345675895051253$.", {"a": "5", "b": "6", "c": "7", "d": "8"}, "c"),
                ("En la siguiente tabla de nombres y códigos, ¿cuál tiene un error de digitación? (A) Juan P. $1234, (B) María L. 1234, (C) Carlos M. 1243, (D) Ana S. 1234$", {"a": "A", "b": "B", "c": "C", "d": "D"}, "c"),
                ("¿Cuántas veces aparece la palabra 'LA' escrita en mayúsculas? La casa es grande. LA pared es blanca. La lámpara, LA mejor. LA ventana.", {"a": "1", "b": "2", "c": "3", "d": "4"}, "c"),
                ("Encuentre la única línea donde el $7$ NO es el último dígito: $1357, 2467, 8027, 9136$.", {"a": "1357", "b": "2467", "c": "8027", "d": "9136"}, "d"),
                ("Marque la figura que no coincide con el patrón: Cuadrado, Círculo, Cuadrado, Círculo, Triángulo.", {"a": "Primer Cuadrado", "b": "Segundo Círculo", "c": "Triángulo", "d": "Primer Círculo"}, "c"),
                ("¿Cuál código postal está incompleto? A) 28001, B) 2801, C) 28002, D) 28003.", {"a": "A", "b": "B", "c": "C", "d": "D"}, "b"),
                ("Dada la regla: 'solo se aceptan números pares', ¿cuál es el error? $2, 4, 6, 9, 10$.", {"a": "2", "b": "6", "c": "9", "d": "10"}, "c"),
                ("¿Cuántos ceros hay en este número? $1001000101001000$.", {"a": "8", "b": "9", "c": "10", "d": "7"}, "b"),
                ("Encuentre la palabra mal deletreada: A) Ocurrencia, B) Ocurrancia, C) Ocurrencia, D) Ocurrencia.", {"a": "A", "b": "B", "c": "C", "d": "D"}, "b"),
                ("Si el patrón es $A>B$, ¿cuál es el error? $C>D, F>E, G>H, I>J$.", {"a": "C>D", "b": "F>E", "c": "G>H", "d": "I>J"}, "b"),
            ]
        },
        "Razonamiento Mecánico": {
            "code": "M",
            "type": "Principios Físicos y Maquinaria",
            "items": [
                ("En un sistema de poleas, si se duplica el número de cuerdas que sostienen la carga, la fuerza necesaria se...", {"a": "Duplica", "b": "Reduce a la mitad", "c": "Mantiene igual", "d": "Triplica"}, "b"),
                ("Si el engranaje $A$ gira en sentido horario, ¿en qué sentido gira el engranaje $B$ conectado directamente a él?", {"a": "Horario", "b": "Antihorario", "c": "No gira", "d": "Depende de la velocidad"}, "b"),
                ("Al usar una palanca, para levantar un peso grande con una fuerza pequeña, se debe:", {"a": "Acercar el punto de apoyo al peso", "b": "Alejar el punto de apoyo del peso", "c": "Usar una palanca más corta", "d": "Aumentar el peso"}, "a"),
                ("¿Qué principio rige el funcionamiento de un gato hidráulico?", {"a": "Ley de Newton", "b": "Principio de Bernoulli", "c": "Principio de Pascal", "d": "Ley de Ohm"}, "c"),
                ("Si dos pesos, uno de $10$ kg y otro de $5$ kg, caen desde la misma altura (sin resistencia del aire), ¿cuál toca el suelo primero?", {"a": "El de $10$ kg", "b": "El de $5$ kg", "c": "Ambos al mismo tiempo", "d": "Depende de la forma"}, "c"),
                ("¿Qué tipo de energía almacena un resorte comprimido?", {"a": "Cinética", "b": "Potencial elástica", "c": "Térmica", "d": "Eléctrica"}, "b"),
                ("Si la rueda de una bicicleta tiene mayor diámetro, ¿qué sucede con la velocidad a la misma cadencia (giro de pedales)?", {"a": "Disminuye", "b": "Aumenta", "c": "Se mantiene", "d": "Oscila"}, "b"),
                ("¿Qué componente convierte el movimiento lineal en movimiento rotatorio en un motor de combustión?", {"a": "El cigüeñal", "b": "La biela", "c": "El pistón", "d": "El árbol de levas"}, "a"),
                ("Una cuña es un ejemplo de:", {"a": "Polea", "b": "Tornillo", "c": "Plano inclinado", "d": "Rueda"}, "c"),
                ("En el agua, ¿por qué un objeto flota?", {"a": "Densidad del objeto es menor que la del agua", "b": "Es más ligero que el agua", "c": "Tiene forma plana", "d": "Tiene más volumen"}, "a"),
                ("La capacidad de un material de estirarse sin romperse se llama:", {"a": "Dureza", "b": "Tenacidad", "c": "Elasticidad", "d": "Fragilidad"}, "c"),
                ("Para una bisagra de puerta, ¿dónde se requiere la menor fuerza para mover la puerta?", {"a": "Cerca de la bisagra", "b": "En el centro", "c": "En el borde opuesto a la bisagra", "d": "En la parte superior"}, "c"),
            ]
        },
        "Razonamiento Abstracto": {
            "code": "R",
            "type": "Series de Figuras y Matrices",
            "items": [
                ("La figura que completa la secuencia: Cuadrado (negro) $\\to$ Círculo (blanco) $\\to$ Triángulo (negro) $\\to$ Círculo (negro) $\\to$ ?", {"a": "Cuadrado (blanco)", "b": "Triángulo (blanco)", "c": "Círculo (negro)", "d": "Cuadrado (negro)"}, "b"),
                ("¿Qué figura es la siguiente? I. Un punto, II. Dos puntos, III. Tres puntos en línea, IV. Cuatro puntos en cuadrado, V. ?", {"a": "Cinco puntos en pentágono", "b": "Cinco puntos en línea", "c": "Seis puntos en línea", "d": "Seis puntos en un hexágono"}, "a"),
                ("¿Cuál es el patrón que falta en la matriz $3 \times 3$?", {"a": "Figura A (combina color/forma)", "b": "Figura B", "c": "Figura C", "d": "Figura D (patrón que falta)"}, "d"),
                ("Identifique la figura intrusa: A) Triángulo equilátero, B) Círculo, C) Cuadrado, D) Rectángulo (lados diferentes).", {"a": "A", "b": "B", "c": "C", "d": "D"}, "b"),
                ("Si $A \\triangle B$ se transforma en $A \\square B$, y $X \\circ Y$ se transforma en $X \\diamond Y$, ¿en qué se transforma $P \\diamond Q$?", {"a": "P $\\circ$ Q", "b": "P $\\triangle$ Q", "c": "P $\\square$ Q", "d": "P $\\times$ Q"}, "a"),
                ("Continúe la serie: $/\backslash, I, \\/, II, /\\, III, ?$", {"a": "IV", "b": "\\/", "c": "//", "d": "III"}, "b"),
                ("El círculo de la izquierda se mueve al centro y se llena. El cuadrado de la derecha se mueve a la izquierda y se vacía. ¿Cuál es el resultado?", {"a": "Círculo lleno a la izquierda, cuadrado vacío a la derecha", "b": "Círculo vacío al centro, cuadrado lleno a la izquierda", "c": "Círculo lleno al centro, cuadrado vacío a la izquierda", "d": "Círculo lleno a la izquierda, cuadrado vacío al centro"}, "c"),
                ("¿Qué figura se obtiene al sobreponer las figuras $A$ (rectángulo) y $B$ (círculo que lo interseca)?", {"a": "Círculo", "b": "Solo rectángulo", "c": "Las dos figuras visibles", "d": "Solo la intersección"}, "c"),
                ("Una figura con $4$ lados se convierte en una con $5$. Una con $3$ lados se convierte en una con $4$. Una con $6$ lados se convierte en una con:", {"a": "6 lados", "b": "7 lados", "c": "8 lados", "d": "5 lados"}, "b"),
                ("El punto se mueve $90^{\circ}$ en sentido horario. ¿Cuál es el siguiente paso?", {"a": "Arriba a la derecha", "b": "Abajo a la derecha", "c": "Abajo a la izquierda", "d": "Arriba a la izquierda"}, "b"),
                ("¿Cuál figura no pertenece? A) Un rayo, B) Una nube, C) Un sol, D) Un coche.", {"a": "A", "b": "B", "c": "C", "d": "D"}, "d"),
                ("Dada la regla: la figura se refleja en el eje $X$. ¿Cuál es el resultado de reflejar la figura $Y$?", {"a": "Y reflejada horizontalmente", "b": "Y reflejada verticalmente", "c": "Y rotada", "d": "Y rotada $90^{\circ}$"}, "a"),
            ]
        },
        "Razonamiento Clerical": {
            "code": "C",
            "type": "Clasificación, Archivo y Verificación",
            "items": [
                ("Ordene alfabéticamente por apellido: A) Pérez, Juan; B) García, Ana; C) López, Luis.", {"a": "A, B, C", "b": "B, C, A", "c": "B, A, C", "d": "C, B, A"}, "b"),
                ("¿Cuál es el número de factura más alto? A) $10245, B) 10542, C) 10425, D) 10524$.", {"a": "A", "b": "B", "c": "C", "d": "D"}, "b"),
                ("¿Qué archivo debe ir primero? A) $Z-155$, B) $Z-105$, C) $Y-199$, D) $X-200$.", {"a": "A", "b": "B", "c": "C", "d": "D"}, "d"),
                ("Verifique la consistencia: Tarea A ($15); Tarea B ($20); Tarea C ($15). ¿Cuál es la inconsistencia?", {"a": "Tarea A", "b": "Tarea B", "c": "Tarea C", "d": "Ninguna"}, "d"),
                ("Clasifique por fecha (más reciente primero): A) $05/2023, B) 01/2024, C) 12/2023, D) 06/2023$.", {"a": "A, B, C, D", "b": "B, C, D, A", "c": "B, D, C, A", "d": "A, D, C, B"}, "b"),
                ("¿Cuál nombre está ordenado incorrectamente en una lista alfabética?: Álvarez, Castro, Gómez, Ruiz, Torres.", {"a": "Álvarez", "b": "Gómez", "c": "Ruiz", "d": "Torres"}, "d"),
                ("Identifique el código que pertenece a la clasificación 'Urgente': URG-A1, STD-A1, URG-B2, URG-B1.", {"a": "URG-A1, STD-A1", "b": "URG-A1, URG-B2, URG-B1", "c": "Solo URG-A1", "d": "Todos"}, "b"),
                ("En una tabla de datos, ¿qué campo es más difícil de verificar clericalmente?", {"a": "ID (números)", "b": "Fecha (día/mes/año)", "c": "Nombre (texto)", "d": "Observaciones (texto largo)"}, "d"),
                ("Ordene numéricamente (mayor a menor): $500, 50, 5000, 5$.", {"a": "5, 50, 500, 5000", "b": "5000, 500, 50, 5", "c": "500, 5000, 50, 5", "d": "5000, 50, 500, 5"}, "b"),
                ("¿Cuál es el nombre correcto según el registro? A) Maria López (Registro: María López), B) Juan Pérez (Registro: Juan Perez), C) Ana Gomez (Registro: Ana Gómez), D) Todos correctos.", {"a": "A", "b": "B", "c": "C", "d": "D"}, "b"),
                ("¿Cuántos números de $4$ dígitos hay en la lista? $1234, 567, 8901, 23456$.", {"a": "1", "b": "2", "c": "3", "d": "4"}, "c"),
                ("Si la regla de archivo es 'Clasificar por primera letra del código', ¿qué va después de $C123$?", {"a": "B999", "b": "C124", "c": "D001", "d": "A500"}, "b"),
            ]
        },
        "Razonamiento Técnico": {
            "code": "T",
            "type": "Diagramas de Flujo y Resolución de Fallas",
            "items": [
                ("En un diagrama de flujo, ¿qué símbolo representa una decisión (Sí/No)?", {"a": "Rectángulo", "b": "Óvalo", "c": "Rombo", "d": "Flecha"}, "c"),
                ("¿Cuál es el paso lógico para diagnosticar una falla eléctrica si el equipo no enciende?", {"a": "Revisar la batería", "b": "Verificar la conexión a la fuente de poder", "c": "Desarmar el motor", "d": "Cambiar el interruptor"}, "b"),
                ("Si una máquina se sobrecalienta, ¿qué factor debe inspeccionar primero?", {"a": "El cableado interno", "b": "El sistema de enfriamiento (ventilador/radiador)", "c": "El color de la pintura", "d": "El manual de usuario"}, "b"),
                ("En una secuencia de programación, si $X=5$ y se ejecuta $X=X+1$, ¿cuál es el nuevo valor de $X$?", {"a": "5", "b": "6", "c": "7", "d": "1"}, "b"),
                ("Dada la secuencia: A) Inspección, B) Diagnóstico, C) Reparación, D) Prueba final. ¿Cuál es el orden lógico de mantenimiento?", {"a": "A, B, C, D", "b": "B, A, C, D", "c": "A, C, B, D", "d": "B, C, A, D"}, "a"),
                ("Si un circuito en serie se abre en un punto, ¿qué sucede con el flujo de corriente?", {"a": "Aumenta", "b": "Disminuye", "c": "Se detiene completamente", "d": "Se mantiene igual"}, "c"),
                ("En un sistema de tuberías, si la presión es demasiado baja, ¿cuál es la causa técnica probable?", {"a": "El diámetro de la tubería es pequeño", "b": "Hay una fuga", "c": "El líquido es muy denso", "d": "La bomba es muy grande"}, "b"),
                ("¿Qué significa el estado 'Loop' en un diagrama de control?", {"a": "Fin del proceso", "b": "Repetición de pasos", "c": "Error crítico", "d": "Inicio del proceso"}, "b"),
                ("Si la luz de advertencia de aceite se enciende en un motor, ¿cuál es el diagnóstico técnico más urgente?", {"a": "Falta de combustible", "b": "Baja presión o nivel de aceite", "c": "Sobrecalentamiento", "d": "Falla eléctrica"}, "b"),
                ("¿Cuál es el propósito principal de un fusible en un circuito eléctrico?", {"a": "Aumentar el voltaje", "b": "Proteger el circuito de sobrecargas", "c": "Almacenar energía", "d": "Regular la corriente"}, "b"),
                ("Dada la instrucción: 'Si el sensor A es True Y el sensor B es False, activar la alarma'. ¿Cuándo se activa la alarma?", {"a": "A y B son True", "b": "A es False y B es True", "c": "A es True y B es False", "d": "Ambos son False"}, "c"),
                ("En el diagnóstico de software, si la aplicación falla al cargar, ¿qué se revisa primero?", {"a": "El código fuente", "b": "La compatibilidad del sistema operativo", "c": "La versión del navegador", "d": "El estado de la base de datos"}, "b"),
            ]
        },
    }

    questions = []
    current_id = 1
    for area_name in AREAS:
        code = APTITUDES_MAP[area_name]["code"]
        data = test_data.get(area_name)
        items_to_use = data["items"][:N_PREGUNTAS_POR_AREA]
        for i, (pregunta, opciones, respuesta) in enumerate(items_to_use):
            questions.append({
                "id": current_id, 
                "area": area_name,
                "code": code,
                "pregunta": pregunta, 
                "opciones": opciones, 
                "respuesta_correcta": respuesta
            })
            current_id += 1
            
    return pd.DataFrame(questions)

df_preguntas = generate_gatb_questions()
N_TOTAL_PREGUNTAS = len(df_preguntas)


# --- 2. FUNCIONES DE ESTADO Y NAVEGACIÓN ---

# Inicialización de Session State (se mantiene)
if 'stage' not in st.session_state: st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'area_actual_index' not in st.session_state: st.session_state.area_actual_index = 0
if 'is_navigating' not in st.session_state: st.session_state.is_navigating = False # Solución anti-doble clic
if 'error_msg' not in st.session_state: st.session_state.error_msg = ""
if 'resultados_df' not in st.session_state: st.session_state.resultados_df = pd.DataFrame()


def set_stage(new_stage):
    """Cambia la etapa de la aplicación, desbloquea la navegación y fuerza el scroll modificado."""
    st.session_state.stage = new_stage
    st.session_state.is_navigating = False # Desbloquear al cambiar de etapa
    st.session_state.error_msg = "" # Limpiar mensaje de error
    scroll_to_not_top() # Usar el scroll modificado


def check_all_answered(area):
    """Verifica si todas las preguntas del área actual han sido respondidas."""
    preguntas_area = df_preguntas[df_preguntas['area'] == area]
    pregunta_ids_area = set(preguntas_area['id'])
    answered_count = sum(1 for q_id in pregunta_ids_area if st.session_state.respuestas.get(q_id) is not None)
    return answered_count == N_PREGUNTAS_POR_AREA

def siguiente_area():
    """Avanza a la siguiente área o finaliza el test, con validación y bloqueo (doble click)."""
    st.session_state.is_navigating = True 
    area_actual = AREAS[st.session_state.area_actual_index]
    
    if not check_all_answered(area_actual):
        st.session_state.error_msg = "🚨 ¡Alerta! Por favor, complete las 12 preguntas de la sección actual antes de avanzar."
        st.session_state.is_navigating = False 
        return
        
    if st.session_state.area_actual_index < len(AREAS) - 1:
        st.session_state.area_actual_index += 1
        set_stage('test_activo')
    else:
        calcular_resultados()
        set_stage('resultados')

def solve_all():
    """Resuelve automáticamente todas las preguntas con la respuesta correcta y navega a resultados."""
    st.session_state.is_navigating = True 

    for index, row in df_preguntas.iterrows():
        pregunta_id = row['id']
        st.session_state.respuestas[pregunta_id] = row['respuesta_correcta']

    st.session_state.area_actual_index = len(AREAS) - 1
    
    calcular_resultados()
    set_stage('resultados')

def calcular_resultados():
    """Calcula y almacena los resultados finales, incluyendo el percentil numérico."""
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
        percentil, clasificacion_texto = clasificar_percentil(porcentaje)
        
        resultados_data.append({
            "Área": area,
            "Código": APTITUDES_MAP[area]["code"],
            "Puntuación Bruta": aciertos_area,
            "Máxima Puntuación": total_area,
            "Porcentaje (%)": float(f"{porcentaje:.1f}"), # Se guarda como float para animación
            "Percentil": float(percentil), 
            "Clasificación": clasificacion_texto,
            "Color": APTITUDES_MAP[area]["color"]
        })
    
    st.session_state.resultados_df = pd.DataFrame(resultados_data)
    st.session_state.is_navigating = False


# --- 3. COMPONENTE DE BARRA DE PROGRESO ANIMADA (NUEVO) ---

def animated_progress_bar(label, percentil, color):
    """Genera una barra de progreso animada usando HTML/CSS."""
    # Clasificación de color para el texto interno de la barra
    text_color = "white" if percentil > 30 else "black"
    
    html_code = f"""
    <style>
        .progress-container {{ 
            width: 100%; 
            background: #e9ecef; 
            border-radius: 8px; 
            margin: 10px 0; 
            overflow: hidden; 
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        .progress-bar {{ 
            height: 30px; 
            line-height: 30px; 
            color: {text_color}; 
            text-align: center; 
            border-radius: 8px;
            transition: width 1.5s ease-out; /* La animación */
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
            width: 0%; /* Comienza en 0% */
            font-weight: bold;
            font-size: 0.9em;
            background-color: {color};
        }}
        /* Animación forzada para Streamlit - inyectamos el ancho final */
        .progress-bar[data-percentil="{percentil:.0f}"] {{
            width: {percentil:.0f}%;
        }}
    </style>
    <div class="progress-container">
        <div class="progress-bar" data-percentil="{percentil:.0f}" style="background-color: {color}; color: {text_color};">
            {label} ({percentil:.0f}%)
        </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# --- 4. FUNCIONES DE REPORTE PROFESIONAL (NUEVO) ---

def get_fortalezas_y_mejoras(df_resultados):
    """Clasifica áreas según el percentil para el informe profesional."""
    fortalezas = []
    mejoras = []

    for index, row in df_resultados.iterrows():
        area = row['Área']
        percentil = row['Percentil']
        
        if percentil >= 70: # Percentil Alto o Superior
            fortalezas.append(area)
        elif percentil <= 40: # Percentil Bajo o Muy Bajo
            mejoras.append(area)
            
    return fortalezas, mejoras

def get_estrategias_de_mejora(area):
    """Proporciona estrategias de mejora específicas para cada área aptitudinal."""
    estrategias = {
        "Razonamiento General": "Practicar juegos de lógica, resolver acertijos complejos y leer material de alta complejidad para expandir la capacidad de abstracción y juicio.",
        "Razonamiento Verbal": "Ampliar el vocabulario con lectura activa y usar herramientas de redacción para estructurar ideas complejas en informes y correos.",
        "Razonamiento Numérico": "Realizar ejercicios diarios de cálculo mental, practicar la resolución rápida de problemas aritméticos y familiarizarse con la interpretación de datos estadísticos.",
        "Razonamiento Espacial": "Usar aplicaciones o puzzles 3D para la rotación mental, practicar el dibujo técnico o la lectura de planos y mapas.",
        "Velocidad Perceptiva": "Entrenar con ejercicios de 'búsqueda y comparación' rápida de códigos, números y patrones en columnas. Ideal para la revisión de documentos.",
        "Precisión Manual": "Realizar tareas que requieran manipulación fina, como el ensamblaje de modelos pequeños o la práctica de caligrafía y dibujo detallado.",
        "Coordinación Manual": "Participar en actividades que sincronicen ojo-mano, como deportes con raqueta (tenis, ping pong), mecanografía rápida o el uso de software de dibujo.",
        "Atención Concentrada": "Implementar la técnica Pomodoro o sesiones de enfoque ininterrumpido. Eliminar distracciones y practicar la revisión de textos largos buscando errores específicos.",
        "Razonamiento Mecánico": "Estudiar diagramas de máquinas simples (palancas, poleas, engranajes) y leer libros sobre principios de física aplicada y mantenimiento industrial.",
        "Razonamiento Abstracto": "Resolver secuencias de matrices figurativas (tipo Raven), puzzles no verbales y practicar el reconocimiento de patrones lógicos abstractos.",
        "Razonamiento Clerical": "Entrenar la organización y archivo de documentos. Practicar la clasificación rápida y la verificación cruzada de datos alfanuméricos.",
        "Razonamiento Técnico": "Analizar diagramas de flujo y resolución de problemas técnicos (troubleshooting) de sistemas conocidos (eléctricos, mecánicos, informáticos).",
    }
    return estrategias.get(area, "Se recomienda entrenamiento específico en tareas que requieran la aplicación práctica y secuencial de esta habilidad.")


# --- 5. VISTAS DE STREAMLIT ---

def vista_inicio():
    """Muestra la página de inicio e instrucciones."""
    scroll_to_not_top()

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
        st.warning("⚠️ **Nota:** Esta es una simulación basada en la estructura GATB, con contenido original para respetar derechos de autor. Los resultados son ilustrativos.")
        
        is_disabled = st.session_state.is_navigating
        
        if st.button("🚀 Iniciar Evaluación", type="primary", use_container_width=True, disabled=is_disabled):
            st.session_state.area_actual_index = 0
            set_stage('test_activo')

        # Botón "Resolver Todo"
        if st.button("✨ Resolver Todo (Demo)", type="secondary", use_container_width=True, disabled=is_disabled):
            solve_all()


def vista_test_activo():
    """Muestra la sección de preguntas del área actual."""
    scroll_to_not_top() # Scroll modificado

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
            # Aseguramos el uso de MathJax para las fórmulas
            question_text = row['pregunta'].replace('$', '$$').replace('$$$$', '$')
            opciones_radio = [f"{k}) {v}" for k, v in row['opciones'].items()]
            
            default_value_key = st.session_state.respuestas.get(pregunta_id)
            default_index = None
            if default_value_key:
                full_option_text = f"{default_value_key}) {row['opciones'][default_value_key]}"
                try:
                    default_index = opciones_radio.index(full_option_text)
                except ValueError:
                    default_index = None

            with st.container(border=True):
                st.markdown(f"**Pregunta {q_num}.**") 
                st.markdown(question_text) # Mostramos la pregunta con formato MathJax
                
                # Callback para guardar la respuesta inmediatamente al seleccionar
                def on_radio_change(q_id):
                    selected_option_full = st.session_state[f'q_{q_id}']
                    selected_key = selected_option_full.split(')')[0].strip() # Obtener la clave (a, b, c, d)
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

    is_disabled = st.session_state.is_navigating or not all_answered
    
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
    """Muestra el informe de resultados profesional sin gráficos, pero con barras animadas y análisis de Fortalezas/Mejoras."""
    scroll_to_not_top()

    st.title("📄 Informe de Resultados GATB Profesional")
    st.header("Perfil Aptitudinal Detallado")
    
    df_resultados = st.session_state.resultados_df

    st.markdown("---")
    
    # --- 1. Calificación Global ---
    avg_percentil = df_resultados['Percentil'].mean()
    calificacion, detalle_calificacion, color_calificacion = calificar_global(avg_percentil)

    st.subheader("📊 Calificación Global del Perfil")
    
    st.markdown(f"""
    <div style="background-color: {color_calificacion}; padding: 25px; border-radius: 15px; color: white; margin-bottom: 30px; text-align: center; box-shadow: 0 6px 15px rgba(0,0,0,0.3);">
        <h2 style="margin: 0; font-size: 2.2em; font-weight: 800;">{calificacion}</h2>
        <p style="margin: 5px 0 10px 0; font-size: 1.2em; font-weight: 500;">Percentil Promedio Global: {avg_percentil:.1f}</p>
        <p style="font-size: 1em; margin: 0; border-top: 1px solid rgba(255,255,255,0.4); padding-top: 10px; opacity: 0.9;">{detalle_calificacion}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- 2. Barras de Progreso Animadas (Reemplaza los gráficos) ---
    st.subheader("📈 Percentiles Aptitudinales (Visualización Animada)")
    
    for index, row in df_resultados.sort_values(by='Percentil', ascending=False).iterrows():
        label = f"{row['Área']} ({row['Código']})"
        percentil = row['Percentil']
        color = row['Color']
        animated_progress_bar(label, percentil, color)

    st.markdown("---")

    # --- 3. Análisis Profesional: Fortalezas y Áreas de Mejora ---
    fortalezas, mejoras = get_fortalezas_y_mejoras(df_resultados)
    estrategias_map = get_estrategias_de_mejora("") # Obtener el mapa completo
    
    col_fortaleza, col_mejora = st.columns(2)

    # FORTALEZAS
    with col_fortaleza:
        st.markdown('<h3 style="color: #008000;">💪 Fortalezas Clave (Percentil ≥ 70)</h3>', unsafe_allow_html=True)
        if fortalezas:
            st.success(f"Se identificaron **{len(fortalezas)}** áreas de alto rendimiento:")
            for area in fortalezas:
                st.markdown(f"- **{area}** (`{APTITUDES_MAP[area]['code']}`)")
        else:
            st.info("No se identificaron áreas con percentiles Superior o Alto. Enfóquese en el desarrollo balanceado.")

    # ÁREAS A MEJORAR
    with col_mejora:
        st.markdown('<h3 style="color: #dc143c;">⚠️ Áreas a Potenciar (Percentil ≤ 40)</h3>', unsafe_allow_html=True)
        if mejoras:
            st.error(f"Se identificaron **{len(mejoras)}** áreas que requieren mayor desarrollo:")
            for area in mejoras:
                st.markdown(f"- **{area}** (`{APTITUDES_MAP[area]['code']}`)")
        else:
            st.success("¡Excelente! No se identificaron áreas críticas que requieran intervención inmediata.")

    st.markdown("---")

    # --- 4. Estrategias de Desarrollo Personalizado ---
    st.subheader("💡 Plan de Desarrollo: Estrategias de Mejora")
    
    if mejoras:
        st.info("Priorizar el desarrollo de estas aptitudes puede aumentar significativamente su rendimiento global.")
        
        for area in mejoras:
            estrategia = estrategias_map[area]
            with st.expander(f"Estrategia para: {area} ({APTITUDES_MAP[area]['code']})"):
                st.markdown(f"**Recomendación:** {estrategia}")
                st.markdown("---")
                st.markdown("Dedicar tiempo diario a ejercicios focalizados en esta aptitud puede generar mejoras notables en 4-6 semanas.")
    else:
        st.balloons()
        st.success("Su perfil es robusto. Continúe fortaleciendo sus habilidades clave y explore nuevos desafíos para el crecimiento continuo.")


    st.markdown("---")

    if st.button("⏪ Realizar Nueva Evaluación", type="secondary"):
        st.session_state.respuestas = {}
        st.session_state.area_actual_index = 0
        set_stage('inicio')


# --- 6. CONTROL DEL FLUJO PRINCIPAL ---

if st.session_state.stage == 'inicio':
    vista_inicio()
elif st.session_state.stage == 'test_activo':
    vista_test_activo()
elif st.session_state.stage == 'resultados':
    vista_resultados()

# --- 7. FOOTER Y ACERCA DE ---
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: small; color: grey;'>Desarrollado para simular la estructura del GATB (General Aptitude Test Battery). Las puntuaciones son ilustrativas y no deben usarse para toma de decisiones sin un profesional cualificado.</p>", unsafe_allow_html=True)
