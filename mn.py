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

# Sistema de Clasificación por Percentil (SIMULADO)
def clasificar_percentil(porcentaje):
    """Convierte el porcentaje de acierto en un percentil simulado y clasificación."""
    if porcentaje >= 90:
        return 96, "Superior (90-99)"
    elif porcentaje >= 80:
        return 88, "Alto (80-89)"
    elif porcentaje >= 60:
        return 70, "Promedio Alto (60-79)"
    elif porcentaje >= 40:
        return 50, "Promedio (40-59)"
    elif porcentaje >= 20:
        return 30, "Promedio Bajo (20-39)"
    elif porcentaje >= 10:
        return 15, "Bajo (10-19)"
    else:
        return 5, "Muy Bajo (0-9)"

# Función para la Calificación Global
def calificar_global(avg_percentil):
    """Asigna una calificación general al perfil basado en el percentil promedio."""
    if avg_percentil >= 85:
        return "Potencial Ejecutivo 🌟", "El perfil indica un potencial excepcionalmente alto y equilibrado para roles directivos, estratégicos y de alta complejidad. Capacidad de aprendizaje superior y adaptación rápida a cualquier entorno.", "#008000" # Green
    elif avg_percentil >= 65:
        return "Nivel Profesional Avanzado 🏆", "El perfil es sólido, con fortalezas claras y un buen balance aptitudinal. Excelente para roles técnicos especializados, de gestión de proyectos y consultoría.", "#4682b4" # Steel Blue
    elif avg_percentil >= 40:
        return "Perfil Competitivo 💼", "El perfil se sitúa en el promedio superior, demostrando suficiencia en todas las áreas. Apto para la mayoría de roles operativos y de coordinación. Requiere enfoque en el desarrollo de fortalezas clave.", "#ff8c00" # Dark Orange
    else:
        return "Período de Desarrollo 🛠️", "El perfil requiere un período de enfoque intensivo en el desarrollo de aptitudes clave. Se recomienda comenzar con roles de soporte y entrenamiento continuo.", "#dc143c" # Crimson

# Función para forzar el scroll al inicio de la página (Solución agresiva)
def js_scroll_to_top():
    """Injecta JS para forzar el scroll al inicio de la página."""
    # Apunta al elemento principal de Streamlit para garantizar que el scroll funcione.
    js_code = """
    <script>
        try {
            const mainContainer = window.parent.document.querySelector('.main');
            if (mainContainer) {
                mainContainer.scrollTop = 0;
            } else {
                document.documentElement.scrollTop = 0;
                document.body.scrollTop = 0;
            }
        } catch (e) {
            console.error("No se pudo forzar el scroll:", e);
        }
    </script>
    """
    st.html(js_code)


# --- 2. DEFINICIÓN DEL TEST (144 Items Únicos, sin Copyright) ---

PREGUNTAS_GATB = []
current_id = 1

for area, data in APTITUDES_MAP.items():
    code = data['code']
    
    for i in range(1, N_PREGUNTAS_POR_AREA + 1):
        pregunta = f"[{code}-{i}] "
        opciones = {"a": "Opción A", "b": "Opción B", "c": "Opción C", "d": "Opción D"}
        respuesta = "c" # Respuesta por defecto

        # --- PREGUNTAS ÚNICAS Y DESCRIPTIVAS (12 ítems por área) ---
        if code == "G": # Razonamiento General
            if i == 1: pregunta = "Selecciona el par de conceptos que mantienen la misma relación: HACHA es a MADERA como CINCEL es a..." ; opciones = {"a": "Pintura", "b": "Metal", "c": "Escultura", "d": "Papel"} ; respuesta = "c"
            elif i == 2: pregunta = "La secuencia numérica es: 5, 8, 13, 20, ¿Cuál es el siguiente número?" ; opciones = {"a": "27", "b": "29", "c": "31", "d": "33"} ; respuesta = "b" # +3, +5, +7, +9
            elif i == 3: pregunta = "Si todos los Z son Y, y algunos X son Z, ¿qué se puede concluir con certeza?" ; opciones = {"a": "Todos los Y son X", "b": "Algunos X son Y", "c": "Ningún Y es X", "d": "Todos los X son Z"} ; respuesta = "b"
            elif i == 4: pregunta = "Encuentre la palabra que sobra: Mercurio, Saturno, Júpiter, Cometa, Marte." ; opciones = {"a": "Mercurio", "b": "Saturno", "c": "Júpiter", "d": "Cometa"} ; respuesta = "d"
            elif i == 5: pregunta = "Si 3 gatos atrapan 3 ratones en 3 minutos, ¿cuántos gatos atraparían 10 ratones en 10 minutos?" ; opciones = {"a": "3", "b": "5", "c": "10", "d": "30"} ; respuesta = "a"
            elif i == 6: pregunta = "Analogía: CUERPO es a CÉLULA como ESTADO es a..." ; opciones = {"a": "Leyes", "b": "Poder", "c": "Ciudadano", "d": "Gobierno"} ; respuesta = "c"
            elif i == 7: pregunta = "Serie de letras: A, C, F, J, ¿Qué letra sigue?" ; opciones = {"a": "L", "b": "M", "c": "N", "d": "O"} ; respuesta = "d" # +2, +3, +4, +5
            elif i == 8: pregunta = "Si la afirmación 'Hoy llueve O hace sol' es verdadera, y hoy NO llueve. ¿Qué se concluye?" ; opciones = {"a": "No hace sol", "b": "La afirmación es falsa", "c": "Hace sol", "d": "Lloverá mañana"} ; respuesta = "c"
            elif i == 9: pregunta = "El 8% de 500 es igual al 40% de qué número?" ; opciones = {"a": "100", "b": "150", "c": "200", "d": "400"} ; respuesta = "a"
            elif i == 10: pregunta = "Identifica el concepto más general: Mesa, Silla, Mueble, Sofá." ; opciones = {"a": "Mesa", "b": "Silla", "c": "Mueble", "d": "Sofá"} ; respuesta = "c"
            elif i == 11: pregunta = "Un reloj se adelanta 1 minuto cada hora. Si se ajusta a las 12:00 PM, ¿qué hora marcará a las 3:00 PM?" ; opciones = {"a": "3:00", "b": "3:03", "c": "3:01", "d": "3:04"} ; respuesta = "b"
            elif i == 12: pregunta = "Completa la serie: 1/2, 1/4, 1/8, ¿Cuál sigue?" ; opciones = {"a": "1/10", "b": "1/12", "c": "1/16", "d": "1/32"} ; respuesta = "c"

        elif code == "V": # Razonamiento Verbal (Vocabulario, Comprensión, Sinónimos/Antónimos)
            if i == 1: pregunta = "Sinónimo de 'EFÍMERO'." ; opciones = {"a": "Duradero", "b": "Fugaz", "c": "Eterno", "d": "Grande"} ; respuesta = "b"
            elif i == 2: pregunta = "Antónimo de 'BELIGERANTE'." ; opciones = {"a": "Guerrero", "b": "Pacífico", "c": "Hostil", "d": "Fuerte"} ; respuesta = "b"
            elif i == 3: pregunta = "El término 'IDIOSINCRASIA' se refiere a:" ; opciones = {"a": "Una enfermedad rara", "b": "El temperamento distintivo de un grupo", "c": "Un tipo de gobierno", "d": "Una fórmula química"} ; respuesta = "b"
            elif i == 4: pregunta = "Complete: La ________ del artista fue evidente en la sutileza de su obra." ; opciones = {"a": "Pereza", "b": "Torpeza", "c": "Maestría", "d": "Ruptura"} ; respuesta = "c"
            elif i == 5: pregunta = "Sinónimo de 'PALPABLE'." ; opciones = {"a": "Invisible", "b": "Intangible", "c": "Evidente", "d": "Suave"} ; respuesta = "c"
            elif i == 6: pregunta = "Antónimo de 'DISPENSA'." ; opciones = {"a": "Permiso", "b": "Prohibición", "c": "Obligación", "d": "Concesión"} ; respuesta = "c"
            elif i == 7: pregunta = "La palabra 'OBSEQUIO' tiene el mismo significado que:" ; opciones = {"a": "Castigo", "b": "Regalo", "c": "Deuda", "d": "Retorno"} ; respuesta = "b"
            elif i == 8: pregunta = "El significado de 'PROSCRIBIR' es:" ; opciones = {"a": "Aceptar", "b": "Permitir", "c": "Prohibir o desterrar", "d": "Escribir mucho"} ; respuesta = "c"
            elif i == 9: pregunta = "Identifique la palabra mal escrita:" ; opciones = {"a": "Exhibición", "b": "Exuberante", "c": "Exajerar", "d": "Expirar"} ; respuesta = "c"
            elif i == 10: pregunta = "Sinónimo de 'ALTRUISTA'." ; opciones = {"a": "Egoísta", "b": "Generoso", "c": "Amargado", "d": "Solitario"} ; respuesta = "b"
            elif i == 11: pregunta = "Complete: El historiador tuvo que ________ los hechos para encontrar la verdad." ; opciones = {"a": "Imaginar", "b": "Cuestionar", "c": "Alterar", "d": "Omitir"} ; respuesta = "b"
            elif i == 12: pregunta = "Antónimo de 'SUTILEZA'." ; opciones = {"a": "Delicadeza", "b": "Aspereza", "c": "Amabilidad", "d": "Claridad"} ; respuesta = "b"

        elif code == "N": # Razonamiento Numérico (Cálculo rápido, problemas aritméticos)
            if i == 1: pregunta = "Resuelva: $72 \div 9 + 4 \times 3 - 10$." ; opciones = {"a": "6", "b": "10", "c": "12", "d": "14"} ; respuesta = "b"
            elif i == 2: pregunta = "Un tren viaja a 60 km/h. ¿Cuántos kilómetros recorrerá en 2 horas y 30 minutos?" ; opciones = {"a": "120 km", "b": "150 km", "c": "180 km", "d": "200 km"} ; respuesta = "b"
            elif i == 3: pregunta = "Calcule el 15% de 300." ; opciones = {"a": "30", "b": "35", "c": "45", "d": "50"} ; respuesta = "c"
            elif i == 4: pregunta = "Resuelva: $(9 + 3) \times 2 - (15 \div 3)$." ; opciones = {"a": "19", "b": "24", "c": "28", "d": "31"} ; respuesta = "a"
            elif i == 5: pregunta = "Si $x + 5 = 12$, entonces $2x - 1$ es igual a:" ; opciones = {"a": "13", "b": "14", "c": "15", "d": "16"} ; respuesta = "a"
            elif i == 6: pregunta = "Si una camisa cuesta $80 y tiene un 25% de descuento, ¿cuál es el precio final?" ; opciones = {"a": "$55", "b": "$60", "c": "$65", "d": "$70"} ; respuesta = "b"
            elif i == 7: pregunta = "Serie: 2, 4, 8, 16, ¿Cuál sigue?" ; opciones = {"a": "20", "b": "24", "c": "32", "d": "64"} ; respuesta = "c"
            elif i == 8: pregunta = "Calcule $\frac{2}{3} + \frac{1}{6}$." ; opciones = {"a": "1/2", "b": "3/4", "c": "5/6", "d": "1"} ; respuesta = "c"
            elif i == 9: pregunta = "Si el área de un cuadrado es 64 $m^2$, ¿cuál es su perímetro?" ; opciones = {"a": "8 m", "b": "16 m", "c": "32 m", "d": "64 m"} ; respuesta = "c"
            elif i == 10: pregunta = "Resuelva: $0.75 + 1.25 + 0.5$." ; opciones = {"a": "2.0", "b": "2.5", "c": "2.75", "d": "3.0"} ; respuesta = "b"
            elif i == 11: pregunta = "Un vendedor ganó $150 de comisión, lo que representa el 5% de sus ventas. ¿Cuánto vendió?" ; opciones = {"a": "$3000", "b": "$2500", "c": "$1500", "d": "$5000"} ; respuesta = "a"
            elif i == 12: pregunta = "Calcule el promedio de 10, 20, y 30." ; opciones = {"a": "15", "b": "20", "c": "25", "d": "60"} ; respuesta = "b"

        elif code == "S": # Razonamiento Espacial (Visualización de formas y rotaciones)
            if i == 1: pregunta = "Imagine una 'L' mayúscula rotada 90 grados en sentido antihorario. ¿Cómo se vería?" ; opciones = {"a": "Una 'L' normal", "b": "Una 'L' de cabeza", "c": "Una 'J'", "d": "Un ángulo recto en la parte inferior izquierda"} ; respuesta = "d"
            elif i == 2: pregunta = "Si dobla una plantilla con 5 cuadrados en forma de cruz, ¿qué forma geométrica tridimensional se obtiene?" ; opciones = {"a": "Pirámide", "b": "Cono", "c": "Cubo", "d": "Cilindro"} ; respuesta = "c"
            elif i == 3: pregunta = "Si un objeto cilíndrico es cortado transversalmente, ¿qué figura bidimensional resulta en el corte?" ; opciones = {"a": "Triángulo", "b": "Rectángulo", "c": "Círculo", "d": "Trapezoide"} ; respuesta = "c"
            elif i == 4: pregunta = "Observe un reloj. Si el minutero está en el 12 y el horario en el 3, ¿cuál es el ángulo menor entre ellos?" ; opciones = {"a": "60°", "b": "90°", "c": "120°", "d": "180°"} ; respuesta = "b"
            elif i == 5: pregunta = "Si se reflejara la letra 'B' en un espejo, ¿cuál de las opciones mostraría la imagen invertida?" ; opciones = {"a": "B", "b": "A", "c": "E", "d": "Su imagen reflejada"} ; respuesta = "d"
            elif i == 6: pregunta = "Si apila 3 cubos y los pinta de rojo, ¿cuántas caras internas no pintadas hay?" ; opciones = {"a": "2", "b": "4", "c": "6", "d": "8"} ; respuesta = "b"
            elif i == 7: pregunta = "En un plano de planta (vista superior), ¿qué representa mejor una puerta en un pasillo?" ; opciones = {"a": "Un círculo", "b": "Una línea recta", "c": "Un arco", "d": "Un rectángulo sólido"} ; respuesta = "c"
            elif i == 8: pregunta = "Si un triángulo equilátero gira 180 grados, ¿su orientación visual cambia?" ; opciones = {"a": "Sí", "b": "No", "c": "Depende del eje", "d": "Solo si es isósceles"} ; respuesta = "b"
            elif i == 9: pregunta = "Si un prisma rectangular tiene 6 caras, 12 aristas y 8 vértices. ¿Cuántas aristas tiene un cubo?" ; opciones = {"a": "6", "b": "8", "c": "10", "d": "12"} ; respuesta = "d"
            elif i == 10: pregunta = "Si un mapa está orientado al Norte, y caminas hacia el Oeste. ¿Hacia dónde está tu sombra al mediodía (hemisferio norte)?" ; opciones = {"a": "Norte", "b": "Este", "c": "Oeste", "d": "Sur"} ; respuesta = "b"
            elif i == 11: pregunta = "Visualice una estrella de 5 puntas. Si traza una línea desde el centro a una de las puntas, ¿cuántos triángulos equiláteros se forman?" ; opciones = {"a": "0", "b": "5", "c": "10", "d": "20"} ; respuesta = "b"
            elif i == 12: pregunta = "Si cortamos una esfera exactamente por la mitad, ¿qué forma tiene la superficie de corte?" ; opciones = {"a": "Elipse", "b": "Cuadrado", "c": "Círculo", "d": "Semisfera"} ; respuesta = "c"

        elif code == "P": # Velocidad Perceptiva (Comparación de detalles bajo velocidad)
            if i == 1: pregunta = "Identifique cuál par es IDÉNTICO: (A) 5920-A / 5920-A, (B) 6074-Z / 6072-Z, (C) MNT-11 / MTT-11." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "Ninguno"} ; respuesta = "a"
            elif i == 2: pregunta = "Identifique cuál par es DIFERENTE: (A) LIMA-02 / LIMA-02, (B) BOGOTA-15 / BOGOTA-15, (C) PARIS-99 / PARID-99." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "Todos idénticos"} ; respuesta = "c"
            elif i == 3: pregunta = "Compara en menos de 5 segundos. ¿Cuál par coincide?: (A) G4H2P / G4H2Q, (B) S8T9W / S8T9W, (C) 123X4 / 123Y4." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "Ninguno"} ; respuesta = "b"
            elif i == 4: pregunta = "Identifique cuál par es IDÉNTICO: (A) J-11234 / J-11243, (B) K-5000 / K-5000, (C) L-7890 / L-789." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "Ninguno"} ; respuesta = "b"
            elif i == 5: pregunta = "Identifique cuál par es DIFERENTE: (A) CODES-A / CODES-A, (B) DATOS-B / DATA-B, (C) LOGICA-C / LOGICA-C." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "Todos idénticos"} ; respuesta = "b"
            elif i == 6: pregunta = "Identifique cuál par es IDÉNTICO: (A) XYZ-987 / YXZ-987, (B) ABC-123 / ABC-123, (C) DEF-456 / DF-456." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "Ninguno"} ; respuesta = "b"
            elif i == 7: pregunta = "Identifique cuál par es DIFERENTE: (A) PROYECTO / PROYECTO, (B) EJECUTIVO / EJECUTIVO, (C) GERENCIA / GERANCIA." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "Todos idénticos"} ; respuesta = "c"
            elif i == 8: pregunta = "Compara: 12456-A / 12456-B." ; opciones = {"a": "Idénticos", "b": "Diferentes"} ; respuesta = "b"
            elif i == 9: pregunta = "Compara: Z99-T-50 / Z99-T-50." ; opciones = {"a": "Idénticos", "b": "Diferentes"} ; respuesta = "a"
            elif i == 10: pregunta = "Compara: P300-X / P300-Y." ; opciones = {"a": "Idénticos", "b": "Diferentes"} ; respuesta = "b"
            elif i == 11: pregunta = "Compara: CABLE-R45 / CABLE-R45." ; opciones = {"a": "Idénticos", "b": "Diferentes"} ; respuesta = "a"
            elif i == 12: pregunta = "Compara: $789.00 / $798.00." ; opciones = {"a": "Idénticos", "b": "Diferentes"} ; respuesta = "b"

        elif code == "Q": # Precisión Manual (Destreza fina y manipulación) - Preguntas Teóricas
             if i == 1: pregunta = "Si tuviera que insertar un chip diminuto en una placa electrónica, ¿qué tipo de control muscular sería esencial?" ; opciones = {"a": "Control grueso del brazo", "b": "Control fino de los dedos y la muñeca", "c": "Fuerza de agarre", "d": "Rapidez general"} ; respuesta = "b"
             elif i == 2: pregunta = "La Precisión Manual se asocia directamente con la habilidad de:" ; opciones = {"a": "Correr rápido", "b": "Manipular instrumentos delicados", "c": "Cargar objetos pesados", "d": "Mantener el equilibrio"} ; respuesta = "b"
             elif i == 3: pregunta = "¿Qué acción requiere el mayor grado de destreza manual fina?" ; opciones = {"a": "Escribir en una pizarra", "b": "Usar un destornillador grande", "c": "Realizar una sutura quirúrgica", "d": "Lanzar una pelota"} ; respuesta = "c"
             elif i == 4: pregunta = "En un trabajo de ensamblaje de joyería, una alta puntuación en Q sugiere que el individuo es:" ; opciones = {"a": "Fuerte", "b": "Rápido mentalmente", "c": "Hábil con piezas pequeñas", "d": "Sociable"} ; respuesta = "c"
             elif i == 5: pregunta = "El movimiento de la mano al dibujar un círculo de un centímetro de diámetro evalúa principalmente:" ; opciones = {"a": "Coordinación", "b": "Precisión", "c": "Velocidad", "d": "Resistencia"} ; respuesta = "b"
             elif i == 6: pregunta = "¿Cuál es un buen sustituto teórico para una tarea que requiere alta precisión manual?" ; opciones = {"a": "Tiro con arco", "b": "Mecanografía veloz", "c": "Talla de madera", "d": "Jugar fútbol"} ; respuesta = "c"
             elif i == 7: pregunta = "Un factor que NO impacta negativamente la precisión manual es:" ; opciones = {"a": "Temblor", "b": "Fatiga", "c": "El conocimiento del objetivo", "d": "Ansiedad"} ; respuesta = "c"
             elif i == 8: pregunta = "La aptitud Q se relaciona fuertemente con carreras como:" ; opciones = {"a": "Contador", "b": "Odontólogo", "c": "Abogado", "d": "Vendedor"} ; respuesta = "b"
             elif i == 9: pregunta = "La habilidad de Q se evalúa midiendo la rapidez y la _________ para manipular objetos pequeños." ; opciones = {"a": "Imaginación", "b": "Fuerza", "c": "Exactitud", "d": "Simpatía"} ; respuesta = "c"
             elif i == 10: pregunta = "¿Qué profesión requiere mayor Precisión Manual, más que fuerza?" ; opciones = {"a": "Albañil", "b": "Mecánico", "c": "Relojero", "d": "Soldador"} ; respuesta = "c"
             elif i == 11: pregunta = "El test de Precisión Manual usualmente involucra:" ; opciones = {"a": "Levantar pesas", "b": "Insertar clavijas o alfileres en orificios", "c": "Resolver ecuaciones", "d": "Leer planos"} ; respuesta = "b"
             elif i == 12: pregunta = "En la manipulación de pinzas finas, la aptitud Q es crucial para evitar:" ; opciones = {"a": "Errores de cálculo", "b": "Daño al material", "c": "Decisiones equivocadas", "d": "El aburrimiento"} ; respuesta = "b"
        
        elif code == "K": # Coordinación Manual (Coordinación ojo-mano) - Preguntas Teóricas
             if i == 1: pregunta = "La aptitud K (Coordinación) es esencial para la actividad de:" ; opciones = {"a": "Memorizar textos", "b": "Conducir un vehículo", "c": "Escribir un ensayo", "d": "Hacer un presupuesto"} ; respuesta = "b"
             elif i == 2: pregunta = "La coordinación ojo-mano se pone a prueba al:" ; opciones = {"a": "Escuchar música", "b": "Tirar una pelota a un blanco", "c": "Contar dinero", "d": "Estar quieto"} ; respuesta = "b"
             elif i == 3: pregunta = "¿Qué tipo de trabajo requiere más la Coordinación Manual que la Precisión Manual?" ; opciones = {"a": "Engarzar joyas", "b": "Uso de un taladro de columna", "c": "Cirugía ocular", "d": "Mecanografía rápida"} ; respuesta = "b"
             elif i == 4: pregunta = "El factor K mide la habilidad para hacer que la mano o el brazo sigan los dictados del:" ; opciones = {"a": "Oído", "b": "Codo", "c": "Ojo", "d": "Pie"} ; respuesta = "c"
             elif i == 5: pregunta = "En el deporte del tenis, la aptitud K es fundamental para:" ; opciones = {"a": "La resistencia física", "b": "El saque y el golpeo de la pelota", "c": "La estrategia mental", "d": "La elección del equipo"} ; respuesta = "b"
             elif i == 6: pregunta = "¿Cuál es el componente clave de la Coordinación Manual?" ; opciones = {"a": "Fuerza muscular", "b": "Integración sensorial", "c": "Memoria espacial", "d": "Velocidad de lectura"} ; respuesta = "b"
             elif i == 7: pregunta = "El factor K se utiliza para predecir el éxito en tareas que requieren movimientos:" ; opciones = {"a": "Estacionarios y repetitivos", "b": "Rápidos y guiados por la vista", "c": "Lentos y pesados", "d": "Absolutos y fijos"} ; respuesta = "b"
             elif i == 8: pregunta = "Una persona con alta K probablemente sería buena en:" ; opciones = {"a": "Programación", "b": "Dibujo técnico a mano alzada", "c": "Venta al por mayor", "d": "Análisis estadístico"} ; respuesta = "b"
             elif i == 9: pregunta = "¿Qué actividad combina K y Q?" ; opciones = {"a": "Ciclismo", "b": "Manejo de torno CNC", "c": "Jardinería", "d": "Pintura de murales"} ; respuesta = "b"
             elif i == 10: pregunta = "El equilibrio y la orientación espacial en movimiento se relacionan con:" ; opciones = {"a": "Razón", "b": "Velocidad", "c": "Coordinación", "d": "Verbal"} ; respuesta = "c"
             elif i == 11: pregunta = "En la danza, la aptitud K se refleja en la capacidad de:" ; opciones = {"a": "Recordar pasos", "b": "Ejecutar movimientos complejos con fluidez", "c": "Elegir la música", "d": "Diseñar vestuario"} ; respuesta = "b"
             elif i == 12: pregunta = "La coordinación de movimientos para alcanzar un objeto en el aire evalúa principalmente:" ; opciones = {"a": "Fuerza", "b": "K", "c": "G", "d": "P"} ; respuesta = "b"

        elif code == "A": # Atención Concentrada (Concentración en tareas monótonas/repetitivas)
            if i == 1: pregunta = "En el texto 'la casa es blanca, la casa está limpia, la casa tiene jardín'. ¿Cuántas veces aparece la palabra 'la'?" ; opciones = {"a": "2", "b": "3", "c": "4", "d": "5"} ; respuesta = "c"
            elif i == 2: pregunta = "Un test de Atención Concentrada típico mide la capacidad de mantener la atención durante un período de tiempo sin caer en..." ; opciones = {"a": "El sueño", "b": "La fatiga", "c": "El error", "d": "La distracción"} ; respuesta = "d"
            elif i == 3: pregunta = "Identifique la secuencia que se repite en: ABCA BCAA BCAB CABA A B C A B C" ; opciones = {"a": "ABC", "b": "ABCA", "c": "BCAB", "d": "CABA"} ; respuesta = "b"
            elif i == 4: pregunta = "Si debe verificar la exactitud de 500 facturas, la aptitud A es más importante que la aptitud V (Verbal)." ; opciones = {"a": "Verdadero", "b": "Falso"} ; respuesta = "a"
            elif i == 5: pregunta = "¿Cuál es el principal enemigo de la Atención Concentrada?" ; opciones = {"a": "El hambre", "b": "La rutina", "c": "La falta de interés en la tarea", "d": "El café"} ; respuesta = "c"
            elif i == 6: pregunta = "En la serie de dígitos: 847291035. Si reemplaza cada número impar por el siguiente par, ¿cuál es el nuevo número?" ; opciones = {"a": "848202046", "b": "847291035", "c": "84820046", "d": "848202040"} ; respuesta = "a"
            elif i == 7: pregunta = "Busque la única diferencia en los dos códigos: LMN-0123-PQRS y LMN-0123-PRQS" ; opciones = {"a": "LMN", "b": "0123", "c": "PQRS/PRQS", "d": "No hay diferencia"} ; respuesta = "c"
            elif i == 8: pregunta = "Una tarea que requiere rellenar formularios idénticos durante 8 horas al día demanda una alta aptitud de:" ; opciones = {"a": "Razonamiento General", "b": "Coordinación Manual", "c": "Atención Concentrada", "d": "Razonamiento Mecánico"} ; respuesta = "c"
            elif i == 9: pregunta = "¿Cuántas 'a' minúsculas encuentra en esta frase, excluyendo la primera palabra?: El análisis de la data actual es complejo." ; opciones = {"a": "5", "b": "6", "c": "7", "d": "8"} ; respuesta = "b"
            elif i == 10: pregunta = "Si un auditor tiene que revisar 1000 asientos contables, su capacidad para mantener la 'A' será clave para evitar:" ; opciones = {"a": "Conflictos laborales", "b": "Fraudes", "c": "Errores de transcripción", "d": "Demoras"} ; respuesta = "c"
            elif i == 11: pregunta = "Marque la letra que no se repite en: R O T O R A S T R O" ; opciones = {"a": "R", "b": "O", "c": "T", "d": "S"} ; respuesta = "d"
            elif i == 12: pregunta = "El tiempo de reacción en tareas de vigilancia o monitoreo se relaciona directamente con:" ; opciones = {"a": "La fuerza física", "b": "La capacidad de mantener A", "c": "La memoria", "d": "La imaginación"} ; respuesta = "b"

        elif code == "M": # Razonamiento Mecánico (Principios físicos, máquinas simples)
            if i == 1: pregunta = "Si una palanca tiene el fulcro cerca de la carga, ¿se requiere más o menos fuerza para levantar la carga que si estuviera lejos?" ; opciones = {"a": "Más fuerza", "b": "Menos fuerza", "c": "La misma fuerza", "d": "Depende del material"} ; respuesta = "a"
            elif i == 2: pregunta = "En un sistema de engranajes donde el engranaje A mueve al B, y B mueve al C. Si A gira en sentido horario, ¿en qué sentido gira C?" ; opciones = {"a": "Horario", "b": "Antihorario", "c": "Depende de la velocidad", "d": "Se detiene"} ; respuesta = "a"
            elif i == 3: pregunta = "¿Cuál es el principio fundamental de una bomba de agua que eleva líquido?" ; opciones = {"a": "Presión positiva", "b": "Flotabilidad", "c": "Gravedad", "d": "Equilibrio estático"} ; respuesta = "a"
            elif i == 4: pregunta = "Si empuja un objeto por una rampa en lugar de levantarlo verticalmente, está aplicando el principio de:" ; opciones = {"a": "Rueda y eje", "b": "Cuña", "c": "Plano inclinado", "d": "Tornillo"} ; respuesta = "c"
            elif i == 5: pregunta = "Si un circuito eléctrico está en 'serie', ¿qué sucede si una bombilla se quema?" ; opciones = {"a": "Todas las demás se apagan", "b": "Solo esa se apaga", "c": "Todas brillan más", "d": "El voltaje aumenta"} ; respuesta = "a"
            elif i == 6: pregunta = "¿Qué máquina simple convierte un movimiento rotatorio en movimiento lineal?" ; opciones = {"a": "Palanca", "b": "Polea", "c": "Tornillo", "d": "Cuña"} ; respuesta = "c"
            elif i == 7: pregunta = "El centro de gravedad de un objeto es clave para su:" ; opciones = {"a": "Color", "b": "Densidad", "c": "Estabilidad", "d": "Temperatura"} ; respuesta = "c"
            elif i == 8: pregunta = "Si se calienta un gas en un recipiente cerrado, ¿qué le sucede a la presión, según la Ley de Gay-Lussac?" ; opciones = {"a": "Disminuye", "b": "Se mantiene igual", "c": "Aumenta", "d": "Se condensa"} ; respuesta = "c"
            elif i == 9: pregunta = "¿Cuál es el propósito principal de un fusible en un circuito eléctrico?" ; opciones = {"a": "Regular el voltaje", "b": "Aumentar la corriente", "c": "Proteger contra sobrecargas", "d": "Almacenar energía"} ; respuesta = "c"
            elif i == 10: pregunta = "Para reducir la fricción en un eje giratorio, se utiliza comúnmente:" ; opciones = {"a": "Agua", "b": "Arena", "c": "Lubricante (aceite o grasa)", "d": "Lija"} ; respuesta = "c"
            elif i == 11: pregunta = "¿Qué tipo de herramienta utiliza el principio del plano inclinado?" ; opciones = {"a": "Martillo", "b": "Destornillador", "c": "Hacha o cuchillo", "d": "Alicate"} ; respuesta = "c"
            elif i == 12: pregunta = "En un sistema hidráulico, ¿qué se transmite con mayor eficiencia?" ; opciones = {"a": "El volumen", "b": "La fuerza", "c": "La presión", "d": "El calor"} ; respuesta = "c"

        elif code == "R": # Razonamiento Abstracto (Patrones en figuras no verbales)
            if i == 1: pregunta = "Serie de figuras: Cuadrado, Triángulo, Círculo, Cuadrado, Triángulo, ¿Cuál sigue?" ; opciones = {"a": "Cuadrado", "b": "Triángulo", "c": "Círculo", "d": "Rombo"} ; respuesta = "c"
            elif i == 2: pregunta = "Un patrón se basa en invertir el color de la figura anterior y rotarla 90 grados. Si la figura actual es un cuadrado negro, ¿cuál será la siguiente?" ; opciones = {"a": "Cuadrado negro rotado", "b": "Cuadrado blanco rotado", "c": "Círculo negro", "d": "Círculo blanco"} ; respuesta = "b"
            elif i == 3: pregunta = "Identifique la figura que NO sigue el patrón: (A) Tres líneas paralelas, (B) Tres líneas que se cruzan en un punto, (C) Tres líneas perpendiculares, (D) Cuatro líneas paralelas." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "D"} ; respuesta = "d"
            elif i == 4: pregunta = "En una matriz 3x3, si la regla es 'El elemento de la fila 3 es la combinación del 1 y 2'. ¿Qué figura falta si 1 es un círculo y 2 es una línea vertical?" ; opciones = {"a": "Círculo con línea vertical", "b": "Solo la línea", "c": "Solo el círculo", "d": "Línea horizontal"} ; respuesta = "a"
            elif i == 5: pregunta = "El patrón es una estrella de 6 puntas que pierde una punta en cada paso. ¿Cuántas puntas tendrá después de 4 pasos?" ; opciones = {"a": "0", "b": "1", "c": "2", "d": "3"} ; respuesta = "c"
            elif i == 6: pregunta = "Si un conjunto de símbolos representa 'Clase de Aves', ¿qué símbolo no pertenecería si la regla es 'tener alas'?" ; opciones = {"a": "Símbolo de Buitre", "b": "Símbolo de Pingüino", "c": "Símbolo de Águila", "d": "Símbolo de Gorrión"} ; respuesta = "b"
            elif i == 7: pregunta = "Serie: un punto, dos puntos, cuatro puntos, ocho puntos, ¿Cuántos puntos siguen?" ; opciones = {"a": "10", "b": "12", "c": "16", "d": "32"} ; respuesta = "c"
            elif i == 8: pregunta = "El patrón muestra que la figura dentro del círculo se mueve 1 paso a la derecha. Si la figura está en la posición 4 (de 5), ¿dónde estará en 2 pasos?" ; opciones = {"a": "Posición 1", "b": "Posición 5", "c": "Posición 2", "d": "Posición 3"} ; respuesta = "a"
            elif i == 9: pregunta = "En un diagrama de Venn que representa 'Animales', 'Mamíferos' y 'Perros'. ¿Cuál es la relación lógica?" ; opciones = {"a": "Tres círculos separados", "b": "Tres círculos anidados", "c": "Dos círculos superpuestos", "d": "Un círculo grande con dos pequeños separados"} ; respuesta = "b"
            elif i == 10: pregunta = "Si la primera figura es un óvalo y la segunda un cuadrado, la tercera es un triángulo y la cuarta un rombo. ¿Cuál es el patrón que rige la forma?" ; opciones = {"a": "Número de lados creciente", "b": "Número de ángulos", "c": "Figuras con curvas", "d": "Figuras simétricas"} ; respuesta = "a"
            elif i == 11: pregunta = "Una serie de figuras aumenta el número de lados en 1 en cada paso. Si comienza con un triángulo, ¿qué figura tendrá después de 3 pasos?" ; opciones = {"a": "Pentágono", "b": "Hexágono", "c": "Heptágono", "d": "Octágono"} ; respuesta = "b"
            elif i == 12: pregunta = "En un conjunto de figuras, la regla es que debe ser de color sólido. ¿Qué figura no cumple si es punteada?" ; opciones = {"a": "Círculo punteado", "b": "Cuadrado sólido", "c": "Triángulo sólido", "d": "Rombo sólido"} ; respuesta = "a"
        
        elif code == "C": # Razonamiento Clerical (Verificación y clasificación de datos)
            if i == 1: pregunta = "Identifique la opción que representa una clasificación alfabética correcta de los siguientes nombres: (A) Alba, Beto, Carlos, (B) Beto, Alba, Carlos, (C) Carlos, Alba, Beto." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "Ninguno"} ; respuesta = "a"
            elif i == 2: pregunta = "¿Cuántos errores encuentra al comparar la columna 1 con la columna 2? Columna 1: 1245-A, 8901-B, 4423-C. Columna 2: 1245-A, 8910-B, 4423-D." ; opciones = {"a": "1", "b": "2", "c": "3", "d": "0"} ; respuesta = "b"
            elif i == 3: pregunta = "Si archiva por código numérico ascendente, ¿cuál iría primero? (A) 00123, (B) 01001, (C) 00099, (D) 00124." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "D"} ; respuesta = "c"
            elif i == 4: pregunta = "En una lista de precios, el artículo 'Aceite de Oliva Extra Virgen, 5L' debe ser clasificado en la categoría 'Comestibles'." ; opciones = {"a": "Verdadero", "b": "Falso"} ; respuesta = "a"
            elif i == 5: pregunta = "En la dirección 'Av. Principal #45-12, Piso 3'. Si solo se pide el número de apartamento, ¿cuál es el dato relevante?" ; opciones = {"a": "Av. Principal", "b": "45-12", "c": "Piso 3", "d": "El número no está claro"} ; respuesta = "d"
            elif i == 6: pregunta = "¿Cuál de las siguientes categorías no es un criterio de clasificación común en una oficina? (A) Alfabético, (B) Numérico, (C) Cromático (por color), (D) Geográfico." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "D"} ; respuesta = "c"
            elif i == 7: pregunta = "Compara: $1,450.50 y 1.450,50$. ¿Son el mismo valor numérico?" ; opciones = {"a": "Sí (diferentes notaciones)", "b": "No (son diferentes valores)", "c": "No se puede saber"} ; respuesta = "a"
            elif i == 8: pregunta = "La tarea de 'conciliar' cuentas bancarias se relaciona directamente con la aptitud de:" ; opciones = {"a": "Razonamiento Espacial", "b": "Velocidad Perceptiva/Clerical", "c": "Coordinación Manual", "d": "Razonamiento Mecánico"} ; respuesta = "b"
            elif i == 9: pregunta = "Si una ficha de cliente contiene datos desactualizados, la habilidad de clerical debe llevar a:" ; opciones = {"a": "Ignorar la ficha", "b": "Actualizar los datos", "c": "Crear una nueva ficha", "d": "Consultar al gerente"} ; respuesta = "b"
            elif i == 10: pregunta = "Para la clasificación de archivos, ¿qué método es más rápido para grandes volúmenes?" ; opciones = {"a": "Alfabético por nombre", "b": "Numérico por código", "c": "Por color de carpeta", "d": "Por peso del documento"} ; respuesta = "b"
            elif i == 11: pregunta = "¿Qué error es más difícil de detectar en una revisión clerical rápida? (A) Un nombre mal escrito, (B) Un dígito incorrecto en un código largo, (C) Un espacio extra en un texto." ; opciones = {"a": "A", "b": "B", "c": "C", "d": "Todos son fáciles"} ; respuesta = "b"
            elif i == 12: pregunta = "Clasifique de más a menos importante para la facturación: (1) Nombre del cliente, (2) Teléfono del cliente, (3) Monto total." ; opciones = {"a": "1, 2, 3", "b": "3, 1, 2", "c": "2, 1, 3", "d": "1, 3, 2"} ; respuesta = "b"

        elif code == "T": # Razonamiento Técnico (Lógica de procesos, diagramas y solución de fallas)
             if i == 1: pregunta = "En un diagrama de flujo, ¿qué símbolo representa una acción o proceso específico?" ; opciones = {"a": "Rombo", "b": "Rectángulo", "c": "Óvalo", "d": "Flecha"} ; respuesta = "b"
             elif i == 2: pregunta = "Si una máquina no enciende, y la luz indicadora del fusible está apagada, ¿cuál es el paso de diagnóstico más lógico?" ; opciones = {"a": "Reemplazar la máquina", "b": "Revisar el cable de alimentación", "c": "Cambiar el fusible", "d": "Llamar a soporte"} ; respuesta = "b"
             elif i == 3: pregunta = "Un manual de usuario indica que 'Si A sucede, entonces B no puede ser verdad'. Si B es verdad, ¿qué conclusión se extrae?" ; opciones = {"a": "A es verdad", "b": "A no sucede", "c": "B no es relevante", "d": "La máquina está rota"} ; respuesta = "b"
             elif i == 4: pregunta = "En un proceso de ensamblaje, el paso 3 requiere que el paso 1 y 2 estén completos. ¿Qué tipo de relación es esta?" ; opciones = {"a": "Lineal", "b": "Paralela", "c": "Jerárquica/Dependiente", "d": "Opcional"} ; respuesta = "c"
             elif i == 5: pregunta = "La fase final en el ciclo de solución de problemas técnicos es:" ; opciones = {"a": "Identificación de la causa", "b": "Implementación de la solución", "c": "Verificación del resultado", "d": "Recopilación de información"} ; respuesta = "c"
             elif i == 6: pregunta = "¿Cuál es el propósito de un 'buffer' o zona de amortiguación en una línea de producción?" ; opciones = {"a": "Aumentar la velocidad", "b": "Almacenar temporalmente producto para evitar paros", "c": "Reducir el personal", "d": "Mejorar la calidad"} ; respuesta = "b"
             elif i == 7: pregunta = "Un termostato utiliza el principio de retroalimentación para:" ; opciones = {"a": "Medir la humedad", "b": "Ajustar la temperatura automáticamente", "c": "Encender la luz", "d": "Contar ciclos"} ; respuesta = "b"
             elif i == 8: pregunta = "En la programación de un sistema, la lógica 'SI (Condición) ENTONCES (Acción)' se conoce como:" ; opciones = {"a": "Sentencia de bucle", "b": "Sentencia condicional", "c": "Declaración de variable", "d": "Función recursiva"} ; respuesta = "b"
             elif i == 9: pregunta = "Si un motor produce humo, ¿qué paso de diagnóstico es el más urgente?" ; opciones = {"a": "Revisar el nivel de aceite", "b": "Apagar inmediatamente la fuente de energía", "c": "Continuar operando con cuidado", "d": "Añadir refrigerante"} ; respuesta = "b"
             elif i == 10: pregunta = "La interconexión de diferentes módulos en un sistema complejo se gestiona mejor con:" ; opciones = {"a": "Un protocolo", "b": "Un manual de estilo", "c": "Un color", "d": "Un supervisor"} ; respuesta = "a"
             elif i == 11: pregunta = "¿Cuál es la función principal de un 'interruptor de límite' en una máquina automática?" ; opciones = {"a": "Regular la temperatura", "b": "Detener un movimiento cuando alcanza un punto específico", "c": "Medir la presión", "d": "Indicar el tiempo de funcionamiento"} ; respuesta = "b"
             elif i == 12: pregunta = "Para un flujo de trabajo óptimo, la secuencia de pasos debe ser:" ; opciones = {"a": "Aleatoria", "b": "Paralela", "c": "Lógica y secuencial", "d": "Independiente"} ; respuesta = "c"

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

# Inicialización de Session State (Agregado 'is_navigating' para el fix del doble click)
if 'stage' not in st.session_state: st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'area_actual_index' not in st.session_state: st.session_state.area_actual_index = 0
if 'is_navigating' not in st.session_state: st.session_state.is_navigating = False # Freno de doble clic

def set_stage(new_stage):
    """Cambia la etapa de la aplicación, desbloquea la navegación y fuerza el scroll."""
    st.session_state.stage = new_stage
    st.session_state.is_navigating = False # Desbloquear al cambiar de etapa
    js_scroll_to_top() # Forzar scroll AGRESIVAMENTE

def siguiente_area():
    """Avanza a la siguiente área o finaliza el test, implementando el bloqueo de doble clic."""
    
    # 1. Bloquear inmediatamente para evitar la doble ejecución
    st.session_state.is_navigating = True 
    
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
            "Escala de Clasificación (Percentil)": percentil,
            "Clasificación": clasificacion_texto,
            "Color": APTITUDES_MAP[area]["color"]
        })
    
    st.session_state.resultados_df = pd.DataFrame(resultados_data)
    st.session_state.is_navigating = False # Desbloquear después de calcular


# --- 4. VISTAS DE STREAMLIT ---

def vista_inicio():
    """Muestra la página de inicio e instrucciones."""
    js_scroll_to_top() # Forzar scroll

    st.title("🧠 Batería de Aptitudes Generales – GATB Profesional")
    st.header("Evaluación Estructurada de 12 Factores Aptitudinales")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        st.info(f"""
        **🎯 Objetivo:** Medir 12 factores clave de aptitud con 144 ítems originales.
        
        **📋 Estructura del Test:**
        - **Total de Secciones:** **{len(AREAS)}**
        - **Preguntas por Sección:** **{N_PREGUNTAS_POR_AREA}**
        - **Total de Ítems:** **{N_TOTAL_PREGUNTAS}**
        
        **📝 Instrucciones:**
        1.  Responda cada pregunta seleccionando la opción que considere correcta.
        2.  Su respuesta se guarda automáticamente al seleccionar.
        3.  Use el botón "Siguiente Sección" para avanzar. **El scroll se forzará al inicio al cambiar de sección.**
        """)
    
    with col2:
        st.subheader("Simulación Profesional")
        st.warning("⚠️ **Nota:** Esta es una simulación. Las clasificaciones (Percentil) son **ilustrativas** y la aptitud se evalúa con preguntas originales creadas para representar el tipo de tarea.")
        
        if st.button("🚀 Iniciar Evaluación", type="primary", use_container_width=True, disabled=st.session_state.is_navigating):
            st.session_state.area_actual_index = 0
            set_stage('test_activo')

    st.markdown("---")
    st.subheader("Resumen de Áreas de Aptitud")
    
    cols = st.columns(3)
    for i, area in enumerate(AREAS):
        col = cols[i % 3]
        col.markdown(f"**{APTITUDES_MAP[area]['code']} - {area}**")

def vista_test_activo():
    """Muestra la sección de preguntas del área actual."""
    js_scroll_to_top() # Forzar scroll al cargar la vista

    area_actual = AREAS[st.session_state.area_actual_index]
    total_areas = len(AREAS)
    current_area_index = st.session_state.area_actual_index
    progress_percentage = (current_area_index + 1) / total_areas

    # --- Cabecera y Barra de Progreso ---
    st.title(f"Sección {current_area_index + 1} de {total_areas}: {area_actual}")
    st.progress(progress_percentage, text=f"Progreso General: **{area_actual}** ({APTITUDES_MAP[area_actual]['code']})")
    st.markdown("---")
    
    preguntas_area = df_preguntas[df_preguntas['area'] == area_actual]
    
    with st.container(border=True):
        st.subheader(f"Tarea: Responda a los {N_PREGUNTAS_POR_AREA} ítems de {area_actual}")
        
        q_num = 1 # Contador local para la pregunta dentro de la sección
        for index, row in preguntas_area.iterrows():
            pregunta_id = row['id']
            opciones_radio = [f"{k}) {v}" for k, v in row['opciones'].items()]
            
            # Recuperar la respuesta anterior
            default_value_key = st.session_state.respuestas.get(pregunta_id)
            try:
                keys_list = list(row['opciones'].keys())
                default_index = keys_list.index(default_value_key)
            except (ValueError, AttributeError):
                default_index = None

            with st.container(border=True):
                st.markdown(f"**Pregunta {q_num}.**") 
                st.markdown(row['pregunta']) # Pregunta con texto descriptivo
                
                # Callback para guardar la respuesta inmediatamente al seleccionar
                def on_radio_change(q_id):
                    selected_option_full = st.session_state[f'q_{q_id}']
                    selected_key = selected_option_full.split(')')[0]
                    st.session_state.respuestas[q_id] = selected_key
                
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

    st.button(
        submit_label, 
        type="primary", 
        on_click=siguiente_area, 
        use_container_width=True,
        disabled=st.session_state.is_navigating # Control de doble click
    )

def vista_resultados():
    """Muestra el informe de resultados profesional con calificación global, escala de nota y detalles extendidos."""
    js_scroll_to_top() # Forzar scroll al cargar resultados

    st.title("📄 Informe de Resultados GATB Profesional")
    st.header("Perfil Aptitudinal Detallado")
    
    df_resultados = st.session_state.resultados_df

    st.markdown("---")
    
    # --- 1. Calificación Global ---
    df_resultados['Percentil Num'] = df_resultados['Escala de Clasificación (Percentil)'].astype(int)
    avg_percentil = df_resultados['Percentil Num'].mean()
    
    calificacion, detalle_calificacion, color_calificacion = calificar_global(avg_percentil)

    st.subheader("📊 Calificación Global del Perfil")
    
    st.markdown(f"""
    <div style="background-color: {color_calificacion}; padding: 25px; border-radius: 15px; color: white; margin-bottom: 20px; text-align: center; box-shadow: 0 6px 10px rgba(0,0,0,0.2);">
        <h2 style="margin: 0; font-size: 2em;">{calificacion}</h2>
        <p style="margin: 5px 0 10px 0; font-size: 1.1em; font-weight: 500;">Percentil Promedio Global: {avg_percentil:.1f}</p>
        <p style="font-size: 0.9em; margin: 0; border-top: 1px solid rgba(255,255,255,0.3); padding-top: 10px;">{detalle_calificacion}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- 2. Escala de Clasificación (Nota) ---
    st.subheader("📈 Escala de Clasificación (Percentiles)")
    st.info("La puntuación de Percentil indica qué porcentaje de la población obtuvo una puntuación igual o menor a la suya. Un 90% es excelente.")
    
    escala_data = {
        "Clasificación": ["Superior", "Alto", "Promedio Alto", "Promedio", "Promedio Bajo", "Bajo", "Muy Bajo"],
        "Rango Percentil (Simulado)": ["90-99", "80-89", "60-79", "40-59", "20-39", "10-19", "0-9"]
    }
    df_escala = pd.DataFrame(escala_data)
    
    st.table(df_escala)

    st.markdown("---")
    
    # --- 3. Tabla de Resultados Detallada ---
    st.subheader("Puntuaciones Detalladas por Aptitud")
    
    # Estilos de celda para la clasificación
    def highlight_classification(s):
        if 'Superior' in s['Clasificación'] or 'Alto' in s['Clasificación']:
            return ['background-color: #d4edda'] * len(s) # Verde claro
        elif 'Bajo' in s['Clasificación']:
            return ['background-color: #f8d7da'] * len(s) # Rojo claro
        else:
            return [''] * len(s)

    df_display = df_resultados.copy()
    df_display = df_display[['Código', 'Área', 'Puntuación Bruta', 'Porcentaje (%)', 'Escala de Clasificación (Percentil)', 'Clasificación']]
    
    st.dataframe(
        df_display.style.apply(highlight_classification, axis=1),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Puntuación Bruta": st.column_config.NumberColumn("Puntaje Bruto", format="%d"),
            "Escala de Clasificación (Percentil)": st.column_config.Progress(
                "Percentil",
                format="%d",
                min_value=0,
                max_value=100,
                width='small'
            )
        }
    )
    
    st.markdown("---")
    
    # --- 4. Interpretación Profesional Detallada ---
    st.subheader("Informe Profesional e Interpretación")
    
    # Reutilizando la función de interpretación para el formato profesional
    def generar_interpretacion_profesional(row):
        percentil = row['Percentil Num']
        area_code = row['Código']
        area_name = row['Área']
        clasificacion = row['Clasificación']

        interpretacion_base = {
            "G": "Capacidad para percibir y comprender relaciones, aprender y emitir juicios lógicos. El factor 'g' de la inteligencia, clave para el éxito en cualquier campo.",
            "V": "Habilidad para entender ideas expresadas en palabras, dominar vocabulario y redactar informes. Esencial para la comunicación eficaz y la comprensión de instrucciones.",
            "N": "Rapidez y precisión para trabajar con números, realizar cálculos y resolver problemas matemáticos. Crucial en análisis de datos, finanzas y contabilidad.",
            "S": "Habilidad para percibir formas en dos o tres dimensiones, rotar objetos mentalmente y visualizar diseños. Importante en diseño, ingeniería, arquitectura y mecánica.",
            "P": "Rapidez para ver detalles en un objeto o tabla, realizar comparaciones y detectar pequeñas diferencias. Fundamental para el control de calidad y roles de auditoría.",
            "Q": "Destreza y coordinación fina de los dedos y las manos, necesaria para ensamblar piezas pequeñas o manipular instrumentos delicados. Típica de la cirugía o la relojería.",
            "K": "Habilidad para coordinar movimientos oculares y manuales, controlando la mano con precisión en movimientos amplios. Importante en oficios, conducción y mecanografía.",
            "A": "Capacidad de mantener la atención en una tarea monótona o repetitiva durante períodos prolongados, minimizando errores. Clave en roles de auditoría o ingreso de datos masivos.",
            "M": "Comprensión de principios físicos básicos, máquinas simples, fuerzas y movimiento. Esencial para técnicos, mecánicos y operarios de maquinaria pesada.",
            "R": "Capacidad para descubrir patrones y relaciones en figuras no verbales o simbólicas, crucial para la lógica pura, la resolución de problemas abstractos y la programación.",
            "C": "Rapidez y precisión para observar detalles verbales y numéricos, como en la clasificación, archivo y verificación de documentos. Típico de roles administrativos y de oficina.",
            "T": "Aplicación de la lógica y principios para identificar fallas, diseñar soluciones o seguir procesos técnicos complejos. Combina G, S, y M en un contexto de solución de problemas.",
        }

        detalle = interpretacion_base.get(area_code, "Mide una habilidad cognitiva o motriz específica.")

        # Definir estilo basado en la clasificación
        if "Superior" in clasificacion: color_bg = "#d4edda"; color_text = "#155724"
        elif "Alto" in clasificacion: color_bg = "#cce5ff"; color_text = "#004085"
        elif "Promedio" in clasificacion: color_bg = "#fff3cd"; color_text = "#856404"
        else: color_bg = "#f8d7da"; color_text = "#721c24"

        return f"""
            <div style="background-color: {color_bg}; padding: 15px; border-radius: 8px; color: {color_text}; margin-bottom: 10px; border-left: 5px solid {color_text};">
                <h5 style="margin-top: 0; color: {color_text}; font-weight: bold;">{area_name} ({area_code}) - Clasificación: {clasificacion}</h5>
                <p style="font-size: 0.9em; margin-bottom: 5px;">**Percentil:** {percentil}</p>
                <p style="font-size: 0.9em; margin-bottom: 0;">**Descripción:** {detalle}</p>
            </div>
        """
        
    for index, row in df_resultados.sort_values(by='Percentil Num', ascending=False).iterrows():
        st.markdown(generar_interpretacion_profesional(row), unsafe_allow_html=True)
        
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
st.markdown("<p style='text-align: center; font-size: small; color: grey;'>Desarrollado para simular la estructura del GATB (General Aptitude Test Battery). Las puntuaciones son ilustrativas y no deben usarse para toma de decisiones sin un profesional cualificado.</p>", unsafe_allow_html=True)
