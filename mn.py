# test_gatb_pro_final.py
import streamlit as st
import pandas as pd
import random
from fpdf import FPDF # Asegúrate de tener instalado: pip install fpdf

# ---------------------------
# Configuración de la página
# ---------------------------
st.set_page_config(
    page_title="Simulador GATB Profesional",
    page_icon="🧠",
    layout="wide"
)

# ---------------------------
# Estilos (CSS)
# ---------------------------
st.markdown("""
<style>
    /* Ocultar "Made with Streamlit" */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Contenedor principal */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Tarjeta de bienvenida y resultados */
    .welcome-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    
    /* Tarjeta de pregunta */
    .question-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px 25px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #007BFF; /* Azul profesional */
    }
    
    .question-card b {
        font-size: 1.15rem; /* Letra de pregunta más grande */
    }

    /* Radio buttons horizontales */
    div[role="radiogroup"] {
        flex-direction: row;
        justify-content: space-around;
        gap: 10px;
    }

    /* Estilo de botones en la barra lateral */
    .stSidebar .stButton>button {
        width: 100%;
        background-color: #007BFF;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 8px 18px;
        border: none;
    }
    .stSidebar .stButton>button:hover {
        background-color: #0056b3;
    }
    
    /* Botón de Finalizar (Verde) */
    .stSidebar .stButton>button[kind="secondary"] {
        background-color: #28a745; /* Verde */
    }
    .stSidebar .stButton>button[kind="secondary"]:hover {
        background-color: #218838;
    }
    
    /* Botones de descarga (PDF/CSV) - estilo secundario pero no en sidebar */
    .stDownloadButton button {
        border-color: #007BFF;
        color: #007BFF;
    }

</style>
""", unsafe_allow_html=True)


# ---------------------------
# Banco de Preguntas
# ---------------------------
def get_questions():
    """
    Retorna la lista completa de 50 preguntas.
    """
    
    # --- BANCOS DE PREGUNTAS DE RELLENO ---
    banco_aritmetica = [
        {"txt": "¿Cuánto es 7 x 6?", "ops": ["40", "42", "48", "56"], "r": "42", "exp": "7 multiplicado por 6 es 42."},
        {"txt": "Calcula el 25% de 200.", "ops": ["25", "50", "75", "100"], "r": "50", "exp": "25% es 1/4. Un cuarto de 200 es 50."},
        {"txt": "Suma: 150 + 350.", "ops": ["400", "450", "500", "550"], "r": "500", "exp": "150 + 350 = 500."},
        {"txt": "Si un libro cuesta $10.000 y tiene 10% de descuento, ¿cuál es el precio final?", "ops": ["$8.000", "$9.000", "$9.500", "$1.000"], "r": "$9.000", "exp": "El 10% de 10.000 es 1.000. 10.000 - 1.000 = 9.000."},
        {"txt": "¿Cuál es la mitad de 128?", "ops": ["60", "64", "68", "70"], "r": "64", "exp": "128 dividido por 2 es 64."}
    ]

    banco_verbal = [
        {"txt": "El antónimo de 'ABRIR' es:", "ops": ["CERRAR", "COMENZAR", "ENTRAR", "MOVER"], "r": "CERRAR", "exp": "Antónimo es lo opuesto. Lo opuesto de abrir es cerrar."},
        {"txt": "El sinónimo de 'CONTENTO' es:", "ops": ["TRISTE", "ENOJADO", "ALEGRE", "CANSADO"], "r": "ALEGRE", "exp": "Sinónimo es un significado similar. Contento es similar a alegre."},
        {"txt": "ZAPATO es a PIE como GUANTE es a...", "ops": ["CABEZA", "MANO", "BRAZO", "DEDO"], "r": "MANO", "exp": "Es una analogía de uso. El zapato se usa en el pie, el guante se usa en la mano."},
        {"txt": "¿Qué palabra no pertenece al grupo: Rojo, Azul, Amarillo, Silla?", "ops": ["ROJO", "AZUL", "AMARILLO", "SILLA"], "r": "SILLA", "exp": "Rojo, Azul y Amarillo son colores. Silla es un mueble."},
        {"txt": "Identifica el error: 'Los niño juegan en el parque.'", "ops": ["niño", "juegan", "en el", "parque"], "r": "niño", "exp": "Debería ser 'Los niños' (plural) para concordar con 'juegan' (plural)."}
    ]

    banco_problemas = [
        {"txt": "Un auto viaja a 100 km/h. ¿Qué distancia recorre en 3 horas?", "ops": ["100 km", "200 km", "300 km", "30 km"], "r": "300 km", "exp": "Distancia = Velocidad x Tiempo. 100 km/h * 3 h = 300 km."},
        {"txt": "Juan tiene 10 manzanas y le da 3 a Ana. ¿Cuántas le quedan?", "ops": ["3", "5", "7", "13"], "r": "7", "exp": "Es una resta simple: 10 - 3 = 7."},
        {"txt": "Si 3 lápices cuestan $600, ¿cuánto cuestan 5 lápices?", "ops": ["$600", "$800", "$1000", "$1200"], "r": "$1000", "exp": "Cada lápiz cuesta $200 ($600/3). 5 lápices cuestan 5 * $200 = $1000."},
        {"txt": "Hoy es miércoles. ¿Qué día fue anteayer?", "ops": ["Lunes", "Martes", "Jueves", "Viernes"], "r": "Lunes", "exp": "Ayer fue martes. Anteayer fue lunes."},
        {"txt": "Un evento empieza a las 10:00 AM y dura 90 minutos. ¿A qué hora termina?", "ops": ["11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM"], "r": "11:30 AM", "exp": "90 minutos son 1 hora y 30 minutos. 10:00 AM + 1h 30m = 11:30 AM."}
    ]
    
    # --- Preguntas Iniciales (1-5) ---
    preguntas = [
        {
            "id": 1,
            "categoria": "Aritmética",
            "texto": "Si 3 operarios tardan 6 horas en cavar una zanja, ¿cuánto tardarían 2 operarios?",
            "opciones": ["4 horas", "8 horas", "9 horas", "12 horas"],
            "respuesta": "9 horas",
            "explicacion": "Es una proporción inversa. (3 operarios * 6 horas) = 18 horas-operario. 18 / 2 operarios = 9 horas."
        },
        {
            "id": 2,
            "categoria": "Verbal",
            "texto": "Elige el par de palabras que tenga una relación similar a: ÁRBOL es a BOSQUE como...",
            "opciones": ["LADRILLO es a PARED", "RÍO es a AGUA", "FLOR es a JARDÍN", "PÁJARO es a NIDO"],
            "respuesta": "LADRILLO es a PARED",
            "explicacion": "Un conjunto de árboles forma un bosque. Un conjunto de ladrillos forma una pared. (Relación parte-todo colectivo)."
        },
        {
            "id": 3,
            "categoria": "Problema",
            "texto": "Un tren viaja a 60 km/h y entra en un túnel de 1 km de largo. El tren mide 0.5 km de largo. ¿Cuánto tiempo tarda el tren en salir completamente del túnel?",
            "opciones": ["1 minuto", "1.5 minutos", "2 minutos", "3 minutos"],
            "respuesta": "1.5 minutos",
            "explicacion": "El tren debe recorrer la longitud del túnel (1 km) más su propia longitud (0.5 km) para salir por completo. Distancia total = 1.5 km. A 60 km/h (1 km/minuto), tarda 1.5 minutos."
        },
        {
            "id": 4,
            "categoria": "Aritmética",
            "texto": "¿Cuál es el 20% del 80% de 200?",
            "opciones": ["16", "32", "40", "64"],
            "respuesta": "32",
            "explicacion": "El 80% de 200 es (0.80 * 200) = 160. El 20% de 160 es (0.20 * 160) = 32."
        },
        {
            "id": 5,
            "categoria": "Verbal",
            "texto": "El antónimo de 'INOCUO' es:",
            "opciones": ["INOFENSIVO", "PERJUDICIAL", "SALUDABLE", "APROPIADO"],
            "respuesta": "PERJUDICIAL",
            "explicacion": "Inocuo significa que no hace daño (inofensivo). Su antónimo (lo opuesto) es algo que sí hace daño (perjudicial)."
        },
    ]

    # --- Relleno de Plantilla (Preguntas 6-50) ---
    
    for i in range(6, 51):
        cat = "Aritmética" if i % 3 == 1 else ("Verbal" if i % 3 == 2 else "Problema")
        
        if cat == "Aritmética":
            banco = banco_aritmetica
        elif cat == "Verbal":
            banco = banco_verbal
        else:
            banco = banco_problemas
            
        # Rotamos las preguntas
        q_data = banco[(i // 3) % len(banco)] 
        
        preguntas.append({
            "id": i,
            "categoria": cat,
            "texto": q_data["txt"],
            "opciones": q_data["ops"],
            "respuesta": q_data["r"],
            "explicacion": q_data["exp"]
        })
    
    return preguntas

# ---------------------------
# Funciones para el PDF
# ---------------------------

def create_pdf_report(df_resultados, total_correctas, total_preguntas, categorias_data):
    """Genera un informe PDF profesional con los resultados y gráficos de rendimiento."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- Configuración de Título y Fuente ---
    pdf.set_font('Arial', 'B', 16)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(0, 15, 'INFORME DE RESULTADOS - SIMULADOR GATB', 0, 1, 'C', 1)
    pdf.ln(5)

    # --- Resumen General ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '1. Resumen de Rendimiento General', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    
    porcentaje_total = (total_correctas / total_preguntas) * 100
    
    pdf.cell(0, 7, f'  • Fecha del Test: {pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")}', 0, 1)
    pdf.cell(0, 7, f'  • Preguntas Totales: {total_preguntas}', 0, 1)
    pdf.cell(0, 7, f'  • Respuestas Correctas: {total_correctas} ({porcentaje_total:.1f}%)', 0, 1)
    pdf.ln(5)

    # --- Gráfico de Rendimiento por Categoría (simulación de texto) ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '2. Detalle de Rendimiento por Aptitud', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)

    categorias = list(categorias_data.keys())
    # Colores para la gráfica (RGB)
    colores = [(10, 132, 255), (40, 200, 120), (255, 180, 50)] 

    for i, cat in enumerate(categorias):
        data = categorias_data[cat]
        porcentaje = (data['correctas'] / data['total']) * 100
        
        # Etiqueta de la categoría
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 7, f'{cat}:', 0, 0, 'L')
        
        # Barra de Rendimiento (Gráfico Simulado)
        fill_color = colores[i % len(colores)]
        pdf.set_fill_color(fill_color[0], fill_color[1], fill_color[2])
        pdf.cell(porcentaje, 7, '', 1, 0, 'L', 1) # La longitud es el porcentaje
        
        # Texto del porcentaje
        pdf.set_font('Arial', '', 10)
        pdf.cell(40, 7, f' {porcentaje:.1f}% ({data["correctas"]}/{data["total"]})', 0, 1, 'L')
        
    pdf.ln(5)

    # --- Tabla de Resultados Detallados ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '3. Revisión Pregunta a Pregunta', 0, 1, 'L')
    pdf.set_font('Arial', '', 8)
    pdf.set_fill_color(200, 200, 200)

    # Encabezados de la tabla
    col_widths = [10, 30, 70, 30, 30]
    headers = ["ID", "Categoría", "Pregunta (Extracto)", "Tu Resp.", "Respuesta Correcta"]
    
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 7, header, 1, 0, 'C', 1)
    pdf.ln()

    # Filas de la tabla
    pdf.set_font('Arial', '', 7)
    for index, row in df_resultados.iterrows():
        # ID
        pdf.cell(col_widths[0], 5, str(row["ID"]), 1, 0, 'C')
        # Categoría
        pdf.cell(col_widths[1], 5, row["Categoría"], 1, 0, 'C')
        # Pregunta (Limitamos el largo para que quepa)
        extracto = row["Pregunta"][:30] + "..." if len(row["Pregunta"]) > 30 else row["Pregunta"]
        pdf.cell(col_widths[2], 5, extracto, 1, 0, 'L')
        # Tu Respuesta
        pdf.cell(col_widths[3], 5, row["Tu Respuesta"], 1, 0, 'C')
        # Respuesta Correcta
        pdf.cell(col_widths[4], 5, row["Respuesta Correcta"], 1, 1, 'C')
        
    return pdf.output(dest='S').encode('latin-1') # Retorna como bytes


# ---------------------------
# Funciones de la App (Logica y Estado)
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
        st.session_state.questions = get_questions()
    if "answers" not in st.session_state:
        st.session_state.answers = {str(q["id"]): "" for q in st.session_state.questions}

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
    """)
    if st.button("🚀 Comenzar Prueba", type="primary"):
        st.session_state.test_started = True
        st.session_state.show_results = False
        st.session_state.page_idx = 0
        st.session_state.questions = get_questions() 
        st.session_state.answers = {str(q["id"]): "" for q in st.session_state.questions}
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def show_test_screen():
    """Muestra la interfaz del test (preguntas y barra lateral)."""
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
    start = st.session_state["page_idx"] * per_page
    end = start + per_page
    
    st.header(f"Preguntas {start + 1} - {min(end, len(preguntas))}")

    for q in preguntas[start:end]:
        key = f"q_{q['id']}"
        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
        
        st.caption(f"Categoría: {q['categoria']}")
        st.markdown(f"<b>{q['id']}. {q['texto']}</b>", unsafe_allow_html=True)
        
        prev_answer = st.session_state["answers"].get(str(q["id"]))
        
        selected = st.radio(
            "Selecciona tu respuesta:",
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
    """Muestra la pantalla de resultados detallados y los botones de descarga."""
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
    
    col_pdf, col_csv, col_reintentar = st.columns([1, 1, 3])

    # 1. Botón para Descargar PDF (Informe Profesional)
    pdf_output = create_pdf_report(df, total_correctas, total_preguntas, categorias)

    col_pdf.download_button(
        "📄 Descargar Informe PDF",
        data=pdf_output,
        file_name="informe_gatb_profesional.pdf",
        mime="application/octet-stream" # MIME para PDF
    )
    
    # 2. Botón para Descargar CSV (Arreglado para Excel)
    csv = df.to_csv(index=False, sep=';').encode('utf-8') # Usamos ';' como separador
    col_csv.download_button(
        "📥 Descargar Datos (CSV)",
        data=csv,
        file_name="resultados_gatb_ordenado.csv",
        mime="text/csv"
    )
    
    # 3. Botón Reintentar
    if col_reintentar.button("🔄 Volver a intentar"):
        st.session_state.test_started = False
        st.session_state.show_results = False
        st.rerun()

# ---------------------------
# Lógica Principal de la App
# ---------------------------

initialize_state()

if not st.session_state.test_started:
    show_welcome_screen()
elif st.session_state.show_results:
    show_results_screen()
else:
    show_test_screen()