# mn.py
import streamlit as st
import pandas as pd
import random 
import base64 
import os # Importar 'os' para la ruta del logo

# ---------------------------
# CONFIGURACIÓN INICIAL
# ---------------------------
st.set_page_config(
    page_title="Simulador GATB Profesional",
    page_icon="🧠",
    layout="wide"
)

# --- RUTAS DE ARCHIVOS ---
LOGO_PATH = "logo empresa.JPG" 

# ---------------------------
# Carga y Codificación del Logo
# ---------------------------
if "logo_base64" not in st.session_state:
    logo_file_exists = os.path.exists(LOGO_PATH)
    if logo_file_exists:
        try:
            with open(LOGO_PATH, "rb") as f:
                logo_bytes = f.read()
                st.session_state.logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")
            st.session_state.logo_found = True
        except Exception as e:
            st.warning(f"Error al cargar el logo: {e}")
            st.session_state.logo_found = False
    else:
        st.warning(f"Advertencia: No se encontró el logo en {LOGO_PATH}. La aplicación continuará sin logo en la cabecera.")
        st.session_state.logo_found = False

# ---------------------------
# Estilos (CSS)
# ---------------------------
logo_css = ""
if st.session_state.logo_found:
    logo_css = f"""
    [data-testid="stHeader"] {{
        background-image: url("data:image/jpeg;base64,{st.session_state.logo_base64}");
        background-repeat: no-repeat;
        background-position: right 1rem top 0.5rem; 
        background-size: 100px; 
        background-color: transparent;
    }}
    """

st.markdown(f"""
<style>
    /* Ocultar "Made with Streamlit" y Footer */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: visible;}} 

    {logo_css}

    /* Contenedor principal */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    /* Tarjeta de bienvenida y resultados */
    .welcome-card {{
        background: #ffffff;
        border-radius: 12px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }}
    
    /* Tarjeta de pregunta */
    .question-card {{
        background: #ffffff;
        border-radius: 12px;
        padding: 20px 25px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #007BFF; 
    }}
    
    .question-card b {{
        font-size: 1.15rem; 
    }}

    /* Radio buttons horizontales */
    div[role="radiogroup"] {{
        flex-direction: row;
        justify-content: space-around;
        gap: 10px;
    }}

    /* Estilo de botones en la barra lateral */
    .stSidebar .stButton>button {{
        width: 100%;
        background-color: #007BFF;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 8px 18px;
        border: none;
    }}
    .stSidebar .stButton>button:hover {{
        background-color: #0056b3;
    }}
    
    /* Botón de Finalizar (Verde) */
    .stSidebar .stButton>button[kind="secondary"] {{
        background-color: #28a745; 
    }}
    .stSidebar .stButton>button[kind="secondary"]:hover {{
        background-color: #218838;
    }}
    
    /* Botones de descarga (CSV) */
    .stDownloadButton button {{
        border-color: #007BFF;
        color: #007BFF;
    }}

</style>
""", unsafe_allow_html=True)


# ---------------------------
# BANCO DE PREGUNTAS (105 preguntas totales)
# CORRECCIÓN: Se reemplazan preguntas de multiplicación/notación compleja.
# ---------------------------
def get_full_question_bank():
    """Define y retorna el banco completo de preguntas."""
    
    banco_aritmetica = [
        # Las 10 preguntas reemplazadas están marcadas con 'REEMPLAZADA'
        {"txt": "¿Cuánto es 85 + 15?", "ops": ["90", "100", "105", "110"], "r": "100", "exp": "Es una suma simple: 85 + 15 = 100."}, # REEMPLAZADA (7 x 6)
        {"txt": "Calcula el 25% de 200.", "ops": ["25", "50", "75", "100"], "r": "50", "exp": "25% es 1/4. Un cuarto de 200 es 50."},
        {"txt": "Suma: 150 + 350.", "ops": ["400", "450", "500", "550"], "r": "500", "exp": "150 + 350 = 500."},
        {"txt": "Si un libro cuesta $10.000 y tiene 10% de descuento, ¿cuál es el precio final?", "ops": ["$8.000", "$9.000", "$9.500", "$1.000"], "r": "$9.000", "exp": "El 10% de 10.000 es 1.000. 10.000 - 1.000 = 9.000."},
        {"txt": "¿Cuál es la mitad de 128?", "ops": ["60", "64", "68", "70"], "r": "64", "exp": "128 dividido por 2 es 64."},
        {"txt": "¿Cuál es el resultado de 60 / 4 + 5?", "ops": ["20", "25", "15", "10"], "r": "20", "exp": "60/4 = 15. 15+5 = 20."}, # REEMPLAZADA (15 x 3 - 5)
        {"txt": "Si el precio de un artículo es $800 y sube 20%, ¿cuál es el nuevo precio?", "ops": ["$960", "$820", "$900", "$1000"], "r": "$960", "exp": "20% de 800 es 160. 800 + 160 = 960."},
        {"txt": "¿Cuál es el resultado de 1000 - 250?", "ops": ["700", "750", "800", "850"], "r": "750", "exp": "1000 - 250 = 750."}, # REEMPLAZADA ($4^3$)
        {"txt": "Resta: 1000 - 450.", "ops": ["650", "550", "500", "450"], "r": "550", "exp": "1000 - 450 = 550."},
        {"txt": "Convierte la fracción 1/4 a decimal.", "ops": ["0.4", "0.25", "0.5", "0.14"], "r": "0.25", "exp": "1 dividido por 4 es 0.25."},
        {"txt": "¿Cuánto es 120 - 45?", "ops": ["65", "70", "75", "80"], "r": "75", "exp": "120 - 45 = 75."}, # REEMPLAZADA (9 x 8 + 3)
        {"txt": "Si un producto cuesta $12.000 con IVA (19%), ¿cuál es el precio sin IVA?", "ops": ["$10.084", "$9.800", "$10.500", "$11.000"], "r": "$10.084", "exp": "$12.000 / 1.19 ≈ $10.084."},
        {"txt": "El área de un cuadrado de lado 7 cm es:", "ops": ["14 cm²", "28 cm²", "49 cm²", "70 cm²"], "r": "49 cm²", "exp": "Área = lado * lado. 7 * 7 = 49."},
        {"txt": "Divide: 720 entre 9.", "ops": ["8", "70", "80", "90"], "r": "80", "exp": "720 / 9 = 80."},
        {"txt": "El resultado de 10 + 22 es:", "ops": ["30", "32", "34", "36"], "r": "32", "exp": "10 + 22 = 32."}, # REEMPLAZADA ($2^5$)
        {"txt": "Si tienes 45 y sumas 32, ¿cuál es el total?", "ops": ["72", "75", "77", "80"], "r": "77", "exp": "45 + 32 = 77."}, # REEMPLAZADA (150% de 60)
        {"txt": "Resuelve: 5 + 7 + 2 - 1.", "ops": ["11", "12", "13", "14"], "r": "13", "exp": "5 + 7 + 2 = 14. 14 - 1 = 13."}, # REEMPLAZADA (10 + (3 x 4) - 2)
        {"txt": "¿Cuál es el número primo más pequeño?", "ops": ["0", "1", "2", "3"], "r": "2", "exp": "El 2 es el único número primo par."},
        {"txt": "Si 5 cajas pesan 75 kg, ¿cuánto pesan 3 cajas?", "ops": ["25 kg", "45 kg", "50 kg", "60 kg"], "r": "45 kg", "exp": "Cada caja pesa 15 kg. 3 * 15 = 45."},
        {"txt": "El MCM (Mínimo Común Múltiplo) de 4 y 6 es:", "ops": ["12", "6", "24", "2"], "r": "12", "exp": "Múltiplos de 4: 4, 8, 12... Múltiplos de 6: 6, 12..."},
        {"txt": "Calcula la raíz cuadrada de 144.", "ops": ["10", "11", "12", "72"], "r": "12", "exp": "12 * 12 = 144."},
        {"txt": "Convierte la fracción 3/5 a porcentaje.", "ops": ["30%", "50%", "60%", "75%"], "r": "60%", "exp": "3/5 = 0.6. 0.6 * 100 = 60%."},
        {"txt": "¿Cuánto es $0.2 \times 50$?", "ops": ["5", "10", "50", "100"], "r": "10", "exp": "0.2 es 1/5. 1/5 de 50 es 10."}, # REEMPLAZADA (0.05 x 1000)
        {"txt": "Resuelve: 1/2 + 1/3.", "ops": ["1/5", "2/5", "5/6", "1/6"], "r": "5/6", "exp": "3/6 + 2/6 = 5/6."},
        {"txt": "El $1\%$ de $10.000$ es:", "ops": ["10", "100", "1.000", "10.000"], "r": "100", "exp": "10.000 / 100 = 100."},
        {"txt": "¿Qué número sigue en la secuencia: 1, 3, 5, 7, ...?", "ops": ["8", "9", "10", "11"], "r": "9", "exp": "Es la secuencia de números impares. 7 + 2 = 9."}, # REEMPLAZADA (2, 4, 8, 16, ...)
        {"txt": "El G.C.D (Máximo Común Divisor) de 12 y 18 es:", "ops": ["2", "3", "6", "12"], "r": "6", "exp": "El divisor más grande que comparten 12 y 18 es 6."},
        {"txt": "Si el área de un círculo es $9\pi$, ¿cuál es su radio?", "ops": ["3", "9", "6", "18"], "r": "3", "exp": "Área = $\pi r^2$. $9\pi = \pi r^2$. $r^2 = 9$. $r = 3$."},
        {"txt": "Resta los números negativos: $-5 - (-8)$.", "ops": ["-13", "-3", "3", "13"], "r": "3", "exp": "-5 + 8 = 3."},
        {"txt": "¿Cuál es el resultado de 30 + 15?", "ops": ["40", "45", "50", "60"], "r": "45", "exp": "30 + 15 = 45."}, # REEMPLAZADA (0.75 x 40)
        {"txt": "Calcula el valor de $x$ en la ecuación $2x + 5 = 15$.", "ops": ["5", "10", "7.5", "2"], "r": "5", "exp": "$2x = 10$. $x = 5$."},
        {"txt": "Si un ángulo de un triángulo rectángulo es $45^\circ$, ¿cuál es el otro ángulo agudo?", "ops": ["30", "45", "55", "90"], "r": "45", "exp": "La suma de ángulos es $180^\circ$. $180 - 90 - 45 = 45$."},
        {"txt": "El resultado de $\\frac{15}{3} + 5$ es:", "ops": ["5", "8", "10", "15"], "r": "10", "exp": "15/3 = 5. 5 + 5 = 10."}, # REEMPLAZADA (fracción x 2)
        {"txt": "¿Cuánto es 12.5% de 80?", "ops": ["10", "12", "15", "20"], "r": "10", "exp": "12.5% es 1/8. 80 / 8 = 10."},
        {"txt": "Divide: 100 entre 4.", "ops": ["15", "20", "25", "30"], "r": "25", "exp": "100 / 4 = 25."}, # REEMPLAZADA (2.5 x 6)
    ]

    banco_verbal = [
        {"txt": "El antónimo de 'ABRIR' es:", "ops": ["CERRAR", "COMENZAR", "ENTRAR", "MOVER"], "r": "CERRAR", "exp": "Antónimo es lo opuesto. Lo opuesto de abrir es cerrar."},
        {"txt": "El sinónimo de 'CONTENTO' es:", "ops": ["TRISTE", "ENOJADO", "ALEGRE", "CANSADO"], "r": "ALEGRE", "exp": "Sinónimo es un significado similar. Contento es similar a alegre."},
        {"txt": "ZAPATO es a PIE como GUANTE es a...", "ops": ["CABEZA", "MANO", "BRAZO", "DEDO"], "r": "MANO", "exp": "Es una analogía de uso. El zapato se usa en el pie, el guante se usa en la mano."},
        {"txt": "¿Qué palabra no pertenece al grupo: Rojo, Azul, Amarillo, Silla?", "ops": ["ROJO", "AZUL", "AMARILLO", "SILLA"], "r": "SILLA", "exp": "Rojo, Azul y Amarillo son colores. Silla es un mueble."},
        {"txt": "Identifica el error: 'Los niño juegan en el parque.'", "ops": ["niño", "juegan", "en el", "parque"], "r": "niño", "exp": "Debería ser 'Los niños' (plural) para concordar con 'juegan' (plural)."},
        {"txt": "El sinónimo de 'BRILLANTE' es:", "ops": ["OPACO", "OSCURO", "LUMINOSO", "SÓLIDO"], "r": "LUMINOSO", "exp": "Brillante y luminoso son sinónimos."},
        {"txt": "El antónimo de 'TEMPORAL' es:", "ops": ["FUGAZ", "PERMANENTE", "RÁPIDO", "MOMENTÁNEO"], "r": "PERMANENTE", "exp": "Temporal significa por un tiempo limitado. Permanente es lo opuesto."},
        {"txt": "DOCTOR es a HOSPITAL como PROFESOR es a...", "ops": ["LIBRO", "ESTUDIANTE", "ESCUELA", "MÉDICO"], "r": "ESCUELA", "exp": "Es una analogía de lugar de trabajo."},
        {"txt": "¿Qué palabra es la intrusa: Mesa, Silla, Sofá, Cocina?", "ops": ["MESA", "SILLA", "SOFÁ", "COCINA"], "r": "COCINA", "exp": "Mesa, silla y sofá son muebles. Cocina es un área o habitación."},
        {"txt": "El significado más cercano a 'DILIGENTE' es:", "ops": ["LENTO", "PEREZOSO", "RÁPIDO", "ACTIVO"], "r": "ACTIVO", "exp": "Diligente significa que actúa con cuidado y actividad."},
        {"txt": "El antónimo de 'ÉXODO' es:", "ops": ["SALIDA", "REGRESO", "MIGRACIÓN", "VIAJE"], "r": "REGRESO", "exp": "Éxodo es una salida masiva, el opuesto es un regreso o retorno."},
        {"txt": "El sinónimo de 'VEROSÍMIL' es:", "ops": ["FALSO", "INCREÍBLE", "CREÍBLE", "IMPOSIBLE"], "r": "CREÍBLE", "exp": "Verosímil significa que parece verdadero o es creíble."},
        {"txt": "AGUA es a BEBER como ALIMENTO es a...", "ops": ["VIVIR", "COCINAR", "COMER", "SALUD"], "r": "COMER", "exp": "Relación de función principal (acción)."},
        {"txt": "¿Qué oración es gramaticalmente correcta?", "ops": ["Haber muchos carros.", "Hay muchos carros.", "Ha haber muchos carros.", "Hubo a muchos carros."], "r": "Hay muchos carros.", "exp": "El verbo 'haber' en impersonal se usa como 'hay'."},
        {"txt": "El antónimo de 'EFÍMERO' es:", "ops": ["DURADERO", "BREVE", "CORTO", "VELOZ"], "r": "DURADERO", "exp": "Efímero es algo que dura poco; duradero es lo opuesto."},
        {"txt": "El sinónimo de 'DISPARIDAD' es:", "ops": ["SIMILITUD", "IGUALDAD", "DIFERENCIA", "UNIÓN"], "r": "DIFERENCIA", "exp": "Disparidad significa desigualdad o diferencia."},
        {"txt": "OÍDO es a ESCUCHAR como OJO es a...", "ops": ["MIRAR", "VISTA", "LENTE", "NARIZ"], "r": "MIRAR", "exp": "Relación órgano-función (verbo de acción)."},
        {"txt": "¿Cuál es el sustantivo en la frase: 'El perro corre rápido'?", "ops": ["EL", "PERRO", "CORRE", "RÁPIDO"], "r": "PERRO", "exp": "Perro es el animal, un sustantivo común."},
        {"txt": "El antónimo de 'CAUTELOSO' es:", "ops": ["PRUDENTE", "IMPRUDENTE", "CUIDADOSO", "LENTO"], "r": "IMPRUDENTE", "exp": "Cauteloso es actuar con cautela. Imprudente es lo opuesto."},
        {"txt": "El sinónimo de 'HOSTIL' es:", "ops": ["AMABLE", "AMIGABLE", "AGRESIVO", "CÁLIDO"], "r": "AGRESIVO", "exp": "Hostil significa contrario o agresivo."},
        {"txt": "PLUMA es a ESCRIBIR como CUCHILLO es a...", "ops": ["CORTAR", "COMIDA", "FILO", "COCINA"], "r": "CORTAR", "exp": "Relación objeto-función."},
        {"txt": "¿Qué palabra es correcta en su uso:", "ops": ["Hiba", "Iba", "Yba", "Hiva"], "r": "Iba", "exp": "La conjugación del verbo ir es 'iba'."},
        {"txt": "El antónimo de 'MENGUAR' es:", "ops": ["DISMINUIR", "REDUCIR", "AUMENTAR", "DECAER"], "r": "AUMENTAR", "exp": "Menguar es disminuir; lo opuesto es aumentar."},
        {"txt": "El sinónimo de 'CONCISO' es:", "ops": ["EXTENSO", "LARGO", "BREVE", "DETALLADO"], "r": "BREVE", "exp": "Conciso significa que se expresa con brevedad."},
        {"txt": "DÍA es a LUZ como NOCHE es a...", "ops": ["SOL", "ESTRELLAS", "OSCURIDAD", "LUNA"], "r": "OSCURIDAD", "exp": "Relación de estado característico."},
        {"txt": "¿Cuál es el adjetivo en la frase: 'Casa grande'?", "ops": ["CASA", "GRANDE", "LA", "ES"], "r": "GRANDE", "exp": "Grande es la cualidad de la casa."},
        {"txt": "El antónimo de 'FÁCIL' es:", "ops": ["SENCILLO", "COMPLICADO", "SIMPLE", "CLARO"], "r": "COMPLICADO", "exp": "Fácil y complicado son opuestos."},
        {"txt": "El sinónimo de 'APROXIMAR' es:", "ops": ["ALEJAR", "DISTANCIAR", "ACERCAR", "SEPARAR"], "r": "ACERCAR", "exp": "Aproximar y acercar tienen un significado similar."},
        {"txt": "CALOR es a DILATACIÓN como FRÍO es a...", "ops": ["AGUA", "HIELO", "CONTRACCIÓN", "TEMPERATURA"], "r": "CONTRACCIÓN", "exp": "Relación causa-efecto físico."},
        {"txt": "¿Qué palabra es un adverbio de modo?", "ops": ["AQUÍ", "AYER", "RÁPIDAMENTE", "MUCHO"], "r": "RÁPIDAMENTE", "exp": "Termina en -mente e indica el modo."},
        {"txt": "El antónimo de 'OSCURIDAD' es:", "ops": ["NOCHE", "SOMBRA", "CLARIDAD", "SILENCIO"], "r": "CLARIDAD", "exp": "Oscuridad y claridad son opuestos."},
        {"txt": "El sinónimo de 'PRESTO' es:", "ops": ["LENTO", "RÁPIDO", "DUDOSO", "TARDÍO"], "r": "RÁPIDO", "exp": "Presto significa rápido o pronto."},
        {"txt": "NARANJA es a CÍTRICO como PAPA es a...", "ops": ["FRUTA", "VERDURA", "TUBÉRCULO", "CEREAL"], "r": "TUBÉRCULO", "exp": "Relación de especie a género."},
        {"txt": "¿En qué palabra hay un error de ortografía?", "ops": ["VACA", "BACA", "VASO", "BALÓN"], "r": "BACA", "exp": "BACA (portaequipaje) se confunde con VACA (animal). El contexto es ambiguo, pero es un par problemático."},
        {"txt": "El antónimo de 'PERFECCIÓN' es:", "ops": ["CALIDAD", "EXCELENCIA", "DEFECTO", "INMACULADO"], "r": "DEFECTO", "exp": "Perfección es ausencia de defectos. Defecto es lo opuesto."},
    ]

    banco_problemas = [
        # Las 7 preguntas reemplazadas están marcadas con 'REEMPLAZADA'
        {"txt": "Tenías $100$ dólares y gastaste $45$. ¿Cuánto queda?", "ops": ["$50", "$55", "$60", "$65"], "r": "$55", "exp": "100 - 45 = 55."}, # REEMPLAZADA (Distancia: 100 km/h * 3h)
        {"txt": "Juan tiene 10 manzanas y le da 3 a Ana. ¿Cuántas le quedan?", "ops": ["3", "5", "7", "13"], "r": "7", "exp": "Es una resta simple: 10 - 3 = 7."},
        {"txt": "En una clase de $30$ estudiantes, $1/3$ son hombres. ¿Cuántas mujeres hay?", "ops": ["10", "15", "20", "25"], "r": "20", "exp": "Hombres: 30 / 3 = 10. Mujeres: 30 - 10 = 20."}, # REEMPLAZADA (Costo de lápices)
        {"txt": "Hoy es miércoles. ¿Qué día fue anteayer?", "ops": ["Lunes", "Martes", "Jueves", "Viernes"], "r": "Lunes", "exp": "Ayer fue martes. Anteayer fue lunes."},
        {"txt": "Un evento empieza a las 10:00 AM y dura 90 minutos. ¿A qué hora termina?", "ops": ["11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM"], "r": "11:30 AM", "exp": "90 minutos son 1 hora y 30 minutos. 10:00 AM + 1h 30m = 11:30 AM."},
        {"txt": "Una piscina se llena con 100 litros por hora. Si necesita 500 litros, ¿cuánto tardará?", "ops": ["5 horas", "6 horas", "10 horas", "4 horas"], "r": "5 horas", "exp": "500 litros / 100 litros/hora = 5 horas."},
        {"txt": "Si un trabajo toma $4$ horas, y lo empiezas a las $8:30$ AM, ¿a qué hora terminas?", "ops": ["12:00 PM", "12:30 PM", "1:30 PM", "2:00 PM"], "r": "12:30 PM", "exp": "8:30 AM + 4 horas = 12:30 PM."}, # REEMPLAZADA (Reloj que se adelanta)
        {"txt": "Un muro de 10 m² es pintado por 2 personas en 5 horas. ¿Cuánto tardarán 4 personas?", "ops": ["2.5 horas", "5 horas", "10 horas", "20 horas"], "r": "2.5 horas", "exp": "Relación inversa. (2 personas * 5 horas) / 4 personas = 2.5 horas."},
        {"txt": "Si en un curso hay 20 hombres y 30 mujeres, ¿qué porcentaje son mujeres?", "ops": ["40%", "50%", "60%", "70%"], "r": "60%", "exp": "Total: 50. 30/50 = 0.6. 0.6 * 100 = 60%."},
        {"txt": "Compré 3 kg de manzanas a $1.500/kg y 2 kg de peras a $2.000/kg. ¿Cuánto gasté en total?", "ops": ["$3.500", "$5.500", "$7.500", "$8.500"], "r": "$8.500", "exp": "Manzanas: 4.500. Peras: 4.000. Total: 8.500."},
        {"txt": "Un ciclista recorre 15 km en media hora. ¿Cuál es su velocidad promedio en km/h?", "ops": ["15 km/h", "30 km/h", "45 km/h", "60 km/h"], "r": "30 km/h", "exp": "30 minutos es media hora. 15 km * 2 = 30 km en 1 hora."},
        {"txt": "Si $x + y = 10$ y $x - y = 4$, ¿cuál es el valor de $x$?", "ops": ["3", "5", "7", "6"], "r": "7", "exp": "Sumando ambas ecuaciones: $2x = 14$. $x = 7$. (7+y=10 -> y=3)."},
        {"txt": "Una camisa cuesta $25.000. Si tiene un descuento del $20\%$, ¿cuánto se ahorra?", "ops": ["$2.500", "$5.000", "$10.000", "$20.000"], "r": "$5.000", "exp": "20% de 25.000 es 5.000."},
        {"txt": "Si hoy es martes, ¿qué día será en $5$ días?", "ops": ["Miércoles", "Jueves", "Viernes", "Domingo"], "r": "Domingo", "exp": "Miércoles (1), Jueves (2), Viernes (3), Sábado (4), Domingo (5)."}, # REEMPLAZADA (4 pares de zapatos)
        {"txt": "El $50\%$ de un número es $150$. ¿Cuál es el número?", "ops": ["75", "100", "200", "300"], "r": "300", "exp": "Si 150 es el 50%, el número completo es 300."}, # REEMPLAZADA (Longitud del tren)
        {"txt": "El precio de un boleto subió de $500 a $600. ¿Cuál fue el porcentaje de aumento?", "ops": ["10%", "15%", "20%", "25%"], "r": "20%", "exp": "Aumento de 100. (100 / 500) * 100 = 20%."},
        {"txt": "En una caja hay el doble de pelotas rojas que azules. Si hay 18 pelotas en total, ¿cuántas son rojas?", "ops": ["6", "9", "12", "15"], "r": "12", "exp": "R + A = 18. R = 2A. $3A = 18$. $A = 6$. $R = 12$."},
        {"txt": "Si un número se divide entre $3$ y el resultado es $9$, ¿cuál es el número?", "ops": ["12", "18", "27", "30"], "r": "27", "exp": "Número / 3 = 9. Número = 9 * 3 = 27."}, # REEMPLAZADA (Volumen del cubo)
        {"txt": "Tres pintores pintan una casa en 6 días. ¿Cuánto tardarían 9 pintores?", "ops": ["1 día", "2 días", "3 días", "4 días"], "r": "2 días", "exp": "Proporción inversa. (3 * 6) / 9 = 2 días."},
        {"txt": "Si Juan tiene el triple de edad que Pedro, y la suma de sus edades es 36, ¿cuántos años tiene Pedro?", "ops": ["8", "9", "12", "18"], "r": "9", "exp": "J + P = 36. J = 3P. $4P = 36$. $P = 9$."},
        {"txt": "Un depósito tiene 2/5 de su capacidad llena. Si le caben 100 litros, ¿cuántos litros faltan para llenarse?", "ops": ["40", "50", "60", "70"], "r": "60", "exp": "Lleno: 40 litros. Faltan 3/5. 3/5 de 100 = 60 litros."},
        {"txt": "Si tengo $50$ caramelos y los reparto entre $8$ niños, ¿cuántos caramelos sobran?", "ops": ["2", "4", "6", "8"], "r": "2", "exp": "50 / 8 = 6 con un resto de 2."},
        {"txt": "Un rectángulo tiene $8$ cm de largo y $5$ cm de ancho. ¿Cuál es su perímetro?", "ops": ["13 cm", "26 cm", "30 cm", "40 cm"], "r": "26 cm", "exp": "Perímetro = $2(L + A)$. $2(8 + 5) = 26$."},
        {"txt": "Si un número se multiplica por 3 y luego se resta 5, el resultado es 10. ¿Cuál es el número?", "ops": ["3", "5", "15", "45"], "r": "5", "exp": "3x - 5 = 10. $3x = 15$. $x = 5$."},
        {"txt": "Hace 5 años, mi edad era 10. ¿Qué edad tendré dentro de 5 años?", "ops": ["15", "20", "25", "30"], "r": "20", "exp": "Edad actual: 15. Dentro de 5 años: 20."},
        {"txt": "Si un paquete de $10$ pilas cuesta $4.000$, ¿cuánto cuesta cada pila?", "ops": ["$40", "$200", "$400", "$4.000"], "r": "$400", "exp": "$4.000 / 10 = $400$."},
        {"txt": "Si un círculo tiene un diámetro de $10$ cm, ¿cuál es su radio?", "ops": ["5 cm", "10 cm", "20 cm", "2.5 cm"], "r": "5 cm", "exp": "El radio es la mitad del diámetro. 10 / 2 = 5 cm."}, # REEMPLAZADA (Doble de azúcar)
        {"txt": "Si en un hexágono, 5 lados miden 10 cm cada uno, y el perímetro es 60 cm, ¿cuánto mide el sexto lado?", "ops": ["5 cm", "10 cm", "6 cm", "15 cm"], "r": "10 cm", "exp": "5 lados * 10 cm = 50 cm. $60 - 50 = 10$ cm."},
        {"txt": "La temperatura es $-5^\circ C$ y sube $12^\circ C$. ¿Cuál es la temperatura final?", "ops": ["$5^\circ C$", "$7^\circ C$", "$12^\circ C$", "$17^\circ C$"], "r": "$7^\circ C$", "exp": "-5 + 12 = 7."},
        {"txt": "Si el $30\%$ de un número es $60$, ¿cuál es el número?", "ops": ["100", "150", "180", "200"], "r": "200", "exp": "Número = $60 / 0.30 = 200$."},
        {"txt": "Un corredor tarda $45$ minutos en dar 3 vueltas. ¿Cuánto tarda en dar 1 vuelta?", "ops": ["10 min", "15 min", "20 min", "25 min"], "r": "15 min", "exp": "45 / 3 = 15 minutos."},
        {"txt": "Un terreno rectangular mide $100$ metros por $50$ metros. ¿Cuál es su área en metros cuadrados?", "ops": ["150", "500", "5.000", "10.000"], "r": "5.000", "exp": "Área = $100 \times 50 = 5.000$ $m^2$."},
        {"txt": "El resultado de $\\frac{1}{2} + \\frac{1}{4}$ es:", "ops": ["$1/2$", "$3/4$", "$1/6$", "$1/8$"], "r": "$3/4$", "exp": "1/2 + 1/4 = 2/4 + 1/4 = 3/4."}, # REEMPLAZADA (Fracción x fracción)
        {"txt": "En un bus hay $15$ personas. En la primera parada suben $5$ y bajan $2$. ¿Cuántas quedan?", "ops": ["18", "19", "20", "22"], "r": "18", "exp": "15 + 5 - 2 = 18."}, # REEMPLAZADA (4 hombres en 8 días)
        {"txt": "Una bolsa tiene $5$ bolitas rojas, $3$ azules y $2$ verdes. ¿Cuál es la probabilidad de sacar una azul?", "ops": ["$3/10$", "$5/10$", "$2/10$", "$1/10$"], "r": "$3/10$", "exp": "3 bolitas azules / 10 bolitas totales."},
    ]
    
    return {
        "Aritmética": banco_aritmetica,
        "Verbal": banco_verbal,
        "Problema": banco_problemas
    }

def get_questions():
    """Selecciona 50 preguntas aleatorias y sin repetición de los bancos."""
    
    bancos = get_full_question_bank()
    
    # Cantidades deseadas por categoría para sumar 50
    num_aritmetica = 17
    num_verbal = 16
    num_problemas = 17
    
    # 1. Seleccionar sin repetición de cada banco
    try:
        selected_aritmetica = random.sample(bancos["Aritmética"], num_aritmetica)
        selected_verbal = random.sample(bancos["Verbal"], num_verbal)
        selected_problemas = random.sample(bancos["Problema"], num_problemas)
    except ValueError as e:
        st.error(f"Error en la selección de preguntas: El banco es demasiado pequeño para sacar el número de preguntas requerido. {e}")
        return []

    # 2. Combinar todas las preguntas seleccionadas
    all_questions = selected_aritmetica + selected_verbal + selected_problemas
    
    # 3. Mezclar el orden de las 50 preguntas combinadas
    random.shuffle(all_questions)
    
    # 4. Asignar IDs de 1 a 50 y la categoría
    final_questions = []
    for i, q in enumerate(all_questions):
        cat = ""
        # Determinar la categoría (necesario ya que random.sample rompe el vínculo)
        for name, bank in bancos.items():
            if q in bank:
                cat = name
                break
        
        final_questions.append({
            "id": i + 1,
            "categoria": cat,
            "texto": q["txt"],
            "opciones": q["ops"],
            "respuesta": q["r"],
            "explicacion": q["exp"]
        })
    
    return final_questions

# ---------------------------
# LÓGICA DEL ESTADO Y NAVEGACIÓN
# ---------------------------

def initialize_state():
    """Inicializa el estado de la sesión."""
    if "test_started" not in st.session_state:
        st.session_state.test_started = False
    if "show_results" not in st.session_state:
        st.session_state.show_results = False
    if "page_idx" not in st.session_state:
        st.session_state.page_idx = 0
    if "questions" not in st.session_state:
        st.session_state.questions = [] 
    if "answers" not in st.session_state:
        st.session_state.answers = {}

def start_new_test():
    """Resetea todas las variables y genera un nuevo conjunto de preguntas ÚNICAS."""
    st.session_state.test_started = True
    st.session_state.show_results = False
    st.session_state.page_idx = 0
    st.session_state.questions = get_questions() 
    st.session_state.answers = {str(q["id"]): "" for q in st.session_state.questions}
    st.rerun()

def get_option_index(question, stored_answer):
    """Obtiene el índice de la respuesta guardada, o None si no hay respuesta."""
    if stored_answer in question["opciones"]:
        return question["opciones"].index(stored_answer)
    return None

def show_welcome_screen():
    """Muestra la pantalla de bienvenida."""
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.title("🧠 Simulador Interactivo GATB Profesional")
    st.markdown("### Prueba de práctica de 50 preguntas")
    st.markdown("---")
    st.write("""
    Esta simulación está diseñada para familiarizarte con el formato de las preguntas 
    de aptitud verbal, aritmética y resolución de problemas.
    
    Cada vez que inicies un nuevo test, se te presentarán **50 preguntas únicas y aleatorias**.
    """)
    if st.button("🚀 Comenzar Nueva Prueba", type="primary"):
        start_new_test()
    st.markdown('</div>', unsafe_allow_html=True)

def show_test_screen():
    """Muestra la interfaz del test (preguntas y barra lateral)."""
    if not st.session_state.questions:
        start_new_test() 

    preguntas = st.session_state.questions
    per_page = 5
    total_pages = (len(preguntas) - 1) // per_page + 1

    # --- Barra Lateral (Sidebar) ---
    with st.sidebar:
        st.title("Progreso")
        
        total_questions = len(preguntas)
        answered_count = len([v for v in st.session_state.answers.values() if v])
        progress_percent = answered_count / total_questions
        
        st.progress(progress_percent)
        st.markdown(f"**{answered_count}** de **{total_questions}** respondidas")
        st.divider()

        st.subheader("Navegación")
        st.markdown(f"**Página {st.session_state['page_idx'] + 1} / {total_pages}**")

        col1, col2 = st.columns(2)
        if col1.button("⬅ Anterior", use_container_width=True):
            if st.session_state["page_idx"] > 0:
                st.session_state["page_idx"] -= 1
                st.rerun()

        if col2.button("Siguiente ➡", use_container_width=True):
            if st.session_state["page_idx"] < total_pages - 1:
                st.session_state["page_idx"] += 1
                st.rerun()
        
        st.divider()
        if st.button("✅ Finalizar y Corregir", type="secondary", use_container_width=True):
            st.session_state.show_results = True
            st.rerun()

    # --- Contenedor Principal (Preguntas) ---
    start_idx = st.session_state["page_idx"] * per_page
    end_idx = start_idx + per_page
    
    st.header(f"Preguntas {start_idx + 1} - {min(end_idx, len(preguntas))}")

    for q in preguntas[start_idx:end_idx]:
        key = f"q_{q['id']}"
        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
        
        st.caption(f"Categoría: {q['categoria']}")
        
        # Se usa st.markdown para renderizar el texto que pueda tener LaTeX,
        # pero las preguntas han sido limpiadas de notación problemática.
        st.markdown(f"<b>{q['id']}. {q['texto']}</b>", unsafe_allow_html=True)
        
        prev_answer = st.session_state["answers"].get(str(q["id"]))
        
        selected = st.radio(
            # CORRECCIÓN DE "ime": Etiqueta vacía y colapsada
            "", 
            options=q["opciones"],
            index=get_option_index(q, prev_answer),
            key=key,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if selected:
            st.session_state["answers"][str(q["id"])] = selected
            
        st.markdown('</div>', unsafe_allow_html=True)

def show_results_screen():
    """Muestra la pantalla de resultados detallados y el botón de descarga CSV."""
    st.title("📈 Resultados de la Simulación")
    st.markdown("---")
    
    preguntas = st.session_state.questions
    respuestas = st.session_state.answers
    
    resultados_data = []
    categorias = {"Aritmética": {"correctas": 0, "total": 0},
                  "Verbal": {"correctas": 0, "total": 0},
                  "Problema": {"correctas": 0, "total": 0}}
    total_correctas = 0

    for q in preguntas:
        user_answer = respuestas.get(str(q["id"]))
        correct_answer = q["respuesta"]
        categoria = q["categoria"]
        es_correcta = user_answer == correct_answer
        
        if es_correcta:
            total_correctas += 1
        
        if categoria in categorias:
            categorias[categoria]["correctas"] += 1 if es_correcta else 0
            categorias[categoria]["total"] += 1
            
        resultados_data.append({
            "ID": q["id"],
            "Pregunta": q["texto"],
            "Categoría": categoria,
            "Tu Respuesta": user_answer if user_answer else "Sin responder",
            "Respuesta Correcta": correct_answer,
            "Resultado": "✅ Correcta" if es_correcta else "❌ Incorrecta",
            "Explicación": q["explicacion"]
        })
    
    df = pd.DataFrame(resultados_data)
    
    # --- Métricas de Resumen ---
    st.subheader("Resumen de Puntaje")
    total_preguntas = len(preguntas)
    score_percent = (total_correctas / total_preguntas) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Puntaje Total", f"{total_correctas} / {total_preguntas}", f"{score_percent:.1f}%")
    
    for i, cat in enumerate(categorias.keys()):
        data = categorias[cat]
        porcentaje = (data['correctas'] / data['total']) * 100 if data['total'] > 0 else 0
        cols = [col2, col3, col4]
        cols[i].metric(cat, f"{data['correctas']} / {data['total']}", f"{porcentaje:.1f}%")

    st.divider()

    # --- Detalle de Respuestas y Botones de Descarga ---
    st.subheader("Revisión Detallada")
    st.dataframe(df.set_index('ID'), use_container_width=True)
    
    col_csv, col_reintentar = st.columns([1, 3])

    # Botón para Descargar CSV (Única opción de descarga)
    csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig') 
    col_csv.download_button(
        "📥 Descargar Datos (CSV)",
        data=csv,
        file_name="resultados_gatb_ordenado.csv",
        mime="text/csv"
    )
    
    # Botón Reintentar: Vuelve a la pantalla de bienvenida
    if col_reintentar.button("🔄 Volver a intentar (Nuevas Preguntas)"):
        st.session_state.test_started = False
        st.session_state.show_results = False
        st.rerun()

# ---------------------------
# LÓGICA PRINCIPAL DE LA APP
# ---------------------------

initialize_state()

if not st.session_state.test_started:
    show_welcome_screen()
elif st.session_state.show_results:
    show_results_screen()
else:
    show_test_screen()
