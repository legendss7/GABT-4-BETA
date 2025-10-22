import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# =============================================================================
# CONFIGURACIÓN INICIAL
# =============================================================================

st.set_page_config(
    layout="wide", 
    page_title="Batería GATB Profesional",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CAPA DE DATOS - CONFIGURACIÓN
# =============================================================================

@dataclass
class AptitudConfig:
    """Configuración de cada aptitud."""
    code: str
    color: str
    description: str

APTITUDES_MAP = {
    "Razonamiento General": AptitudConfig("G", "#1f77b4", "Capacidad para razonar y resolver problemas complejos"),
    "Razonamiento Verbal": AptitudConfig("V", "#ff7f0e", "Comprensión y uso efectivo del lenguaje"),
    "Razonamiento Numérico": AptitudConfig("N", "#2ca02c", "Habilidad para trabajar con números y datos"),
    "Razonamiento Espacial": AptitudConfig("S", "#d62728", "Visualización y manipulación mental de objetos"),
    "Velocidad Perceptiva": AptitudConfig("P", "#9467bd", "Rapidez en identificar detalles visuales"),
    "Precisión Manual": AptitudConfig("Q", "#8c564b", "Exactitud en movimientos manuales finos"),
    "Coordinación Manual": AptitudConfig("K", "#e377c2", "Sincronización ojo-mano en tareas complejas"),
    "Atención Concentrada": AptitudConfig("A", "#7f7f7f", "Capacidad de mantener foco prolongado"),
    "Razonamiento Mecánico": AptitudConfig("M", "#bcbd22", "Comprensión de principios mecánicos"),
    "Razonamiento Abstracto": AptitudConfig("R", "#17becf", "Identificación de patrones abstractos"),
    "Razonamiento Clerical": AptitudConfig("C", "#98df8a", "Precisión en tareas administrativas"),
    "Razonamiento Técnico": AptitudConfig("T", "#ff9896", "Solución de problemas técnicos"),
}

AREAS = list(APTITUDES_MAP.keys())
N_PREGUNTAS_POR_AREA = 12
N_TOTAL_PREGUNTAS = len(AREAS) * N_PREGUNTAS_POR_AREA

# =============================================================================
# CAPA DE DATOS - GENERADOR DE PREGUNTAS
# =============================================================================

class QuestionBank:
    """Banco de preguntas del test GATB."""
    
    @staticmethod
    def generate_questions() -> pd.DataFrame:
        """Genera las 144 preguntas del test."""
        preguntas_templates = {
            "Razonamiento General": [
                ("Si todos los A son B, y todos los B son C, entonces:", 
                 {"a": "Todos los A son C", "b": "Algunos A son C", "c": "Ningún A es C", "d": "No se puede determinar"}, "a"),
                ("¿Qué número sigue en la serie: 2, 6, 12, 20, 30, ?", 
                 {"a": "40", "b": "42", "c": "44", "d": "38"}, "b"),
            ],
            "Razonamiento Verbal": [
                ("Sinónimo de ELOCUENTE:", 
                 {"a": "Callado", "b": "Expresivo", "c": "Confuso", "d": "Torpe"}, "b"),
                ("Antónimo de ADVERSO:", 
                 {"a": "Favorable", "b": "Contrario", "c": "Hostil", "d": "Negativo"}, "a"),
            ],
            "Razonamiento Numérico": [
                ("Si 3x + 5 = 20, entonces x =", 
                 {"a": "5", "b": "6", "c": "7", "d": "8"}, "a"),
                ("El 25% de 80 es:", 
                 {"a": "15", "b": "20", "c": "25", "d": "30"}, "b"),
            ],
            "Razonamiento Espacial": [
                ("Si rotamos un cubo 90° hacia la derecha, ¿qué cara queda al frente?", 
                 {"a": "La que estaba a la izquierda", "b": "La que estaba arriba", "c": "La que estaba atrás", "d": "La que estaba abajo"}, "a"),
                ("¿Cuántas caras tiene un prisma rectangular?", 
                 {"a": "4", "b": "5", "c": "6", "d": "8"}, "c"),
            ],
            "Velocidad Perceptiva": [
                ("¿Son iguales? 4789236 vs 4789236", 
                 {"a": "Sí", "b": "No", "c": "Casi", "d": "Parcialmente"}, "a"),
                ("¿Son iguales? ABCDEF vs ABCDFE", 
                 {"a": "Sí", "b": "No", "c": "Casi", "d": "Parcialmente"}, "b"),
            ],
            "Precisión Manual": [
                ("En tareas de ensamblaje fino, lo más importante es:", 
                 {"a": "Velocidad", "b": "Precisión", "c": "Fuerza", "d": "Tamaño"}, "b"),
                ("Para enhebrar una aguja se requiere principalmente:", 
                 {"a": "Fuerza", "b": "Coordinación fina", "c": "Velocidad", "d": "Concentración visual"}, "b"),
            ],
            "Coordinación Manual": [
                ("La coordinación ojo-mano es más importante en:", 
                 {"a": "Leer", "b": "Conducir", "c": "Escuchar", "d": "Pensar"}, "b"),
                ("¿Qué actividad requiere más coordinación manual?", 
                 {"a": "Escribir a mano", "b": "Recordar", "c": "Oír música", "d": "Ver TV"}, "a"),
            ],
            "Atención Concentrada": [
                ("Encuentra el error: El gato esta en el tejado", 
                 {"a": "gato", "b": "esta (falta tilde)", "c": "tejado", "d": "No hay error"}, "b"),
                ("¿Cuántas veces aparece la letra 'a' en: La casa grande?", 
                 {"a": "2", "b": "3", "c": "4", "d": "5"}, "c"),
            ],
            "Razonamiento Mecánico": [
                ("Si una rueda grande gira una vez, ¿cuántas veces gira una rueda conectada que es la mitad de tamaño?", 
                 {"a": "1 vez", "b": "2 veces", "c": "0.5 veces", "d": "4 veces"}, "b"),
                ("Una palanca es más eficiente cuando:", 
                 {"a": "El fulcro está cerca de la carga", "b": "El fulcro está lejos de la carga", "c": "No tiene fulcro", "d": "Es muy corta"}, "a"),
            ],
            "Razonamiento Abstracto": [
                ("En la serie: ○ △ ○ △ ○ ?, ¿qué sigue?", 
                 {"a": "○", "b": "△", "c": "□", "d": "◇"}, "b"),
                ("Si A=1, B=2, C=3, entonces ABC=", 
                 {"a": "123", "b": "6", "c": "321", "d": "111"}, "a"),
            ],
            "Razonamiento Clerical": [
                ("¿En qué orden alfabético van estos apellidos: Pérez, Martínez, López?", 
                 {"a": "López, Martínez, Pérez", "b": "Martínez, López, Pérez", "c": "Pérez, Martínez, López", "d": "López, Pérez, Martínez"}, "a"),
                ("Al archivar por fecha, ¿cuál va primero?", 
                 {"a": "15/03/2024", "b": "10/03/2024", "c": "20/03/2024", "d": "05/04/2024"}, "b"),
            ],
            "Razonamiento Técnico": [
                ("En un diagrama de flujo, un rombo representa:", 
                 {"a": "Inicio", "b": "Proceso", "c": "Decisión", "d": "Fin"}, "c"),
                ("Si un sistema no arranca, el primer paso es:", 
                 {"a": "Reiniciar", "b": "Revisar conexiones", "c": "Llamar soporte", "d": "Comprar uno nuevo"}, "b"),
            ],
        }
        
        questions = []
        current_id = 1
        
        for area_name in AREAS:
            code = APTITUDES_MAP[area_name].code
            templates = preguntas_templates.get(area_name, [])
            
            for i in range(N_PREGUNTAS_POR_AREA):
                template_idx = i % len(templates) if templates else 0
                
                if templates:
                    pregunta_text, opciones, respuesta_correcta = templates[template_idx]
                    pregunta_final = f"{pregunta_text} (Variante {i+1})"
                else:
                    pregunta_final = f"Pregunta {code}-{i+1}: Evalúa {area_name}"
                    opciones = {"a": "Opción A", "b": "Opción B", "c": "Opción C", "d": "Opción D"}
                    respuesta_correcta = "a"
                
                questions.append({
                    "id": current_id, 
                    "area": area_name,
                    "code": code,
                    "pregunta": pregunta_final,
                    "opciones": opciones,
                    "respuesta_correcta": respuesta_correcta
                })
                current_id += 1
        
        return pd.DataFrame(questions)

# =============================================================================
# CAPA DE LÓGICA - CALCULADORA DE RESULTADOS
# =============================================================================

class ResultsCalculator:
    """Calculadora de resultados y percentiles."""
    
    @staticmethod
    def clasificar_percentil(porcentaje: float) -> Tuple[int, str]:
        """Clasifica el percentil según el porcentaje."""
        if porcentaje >= 90: return 96, "Superior (90-99)"
        elif porcentaje >= 80: return 88, "Alto (80-89)"
        elif porcentaje >= 60: return 70, "Promedio Alto (60-79)"
        elif porcentaje >= 40: return 50, "Promedio (40-59)"
        elif porcentaje >= 20: return 30, "Promedio Bajo (20-39)"
        elif porcentaje >= 10: return 15, "Bajo (10-19)"
        else: return 5, "Muy Bajo (0-9)"
    
    @staticmethod
    def calificar_global(avg_percentil: float) -> Tuple[str, str, str]:
        """Calificación global del perfil."""
        if avg_percentil >= 85: 
            return "Potencial Ejecutivo 🌟", "El perfil indica un potencial excepcionalmente alto y equilibrado para roles directivos, estratégicos y de alta complejidad. Capacidad de aprendizaje superior y adaptación rápida a cualquier entorno.", "#008000"
        elif avg_percentil >= 65: 
            return "Nivel Profesional Avanzado 🏆", "El perfil es sólido, con fortalezas claras y un buen balance aptitudinal. Excelente para roles técnicos especializados, de gestión de proyectos y consultoría.", "#4682b4"
        elif avg_percentil >= 40: 
            return "Perfil Competitivo 💼", "El perfil se sitúa en el promedio superior, demostrando suficiencia en todas las áreas. Apto para la mayoría de roles operativos y de coordinación. Requiere enfoque en el desarrollo de fortalezas clave.", "#ff8c00"
        else: 
            return "Período de Desarrollo 🛠️", "El perfil requiere un período de enfoque intensivo en el desarrollo de aptitudes clave. Se recomienda comenzar con roles de soporte y entrenamiento continuo.", "#dc143c"
    
    @staticmethod
    def calcular_resultados(df_preguntas: pd.DataFrame, respuestas: Dict) -> pd.DataFrame:
        """Calcula los resultados completos del test."""
        resultados_data = []
        
        for area in AREAS:
            preguntas_area = df_preguntas[df_preguntas['area'] == area]
            aciertos = 0
            
            for _, row in preguntas_area.iterrows():
                respuesta_usuario = respuestas.get(row['id'])
                if respuesta_usuario == row['respuesta_correcta']:
                    aciertos += 1
            
            porcentaje = (aciertos / N_PREGUNTAS_POR_AREA) * 100
            percentil = min(99, max(1, porcentaje + np.random.randint(-5, 5)))
            clasificacion_val, clasificacion_texto = ResultsCalculator.clasificar_percentil(percentil)
            
            resultados_data.append({
                "Área": area,
                "Código": APTITUDES_MAP[area].code,
                "Puntuación Bruta": aciertos,
                "Máxima Puntuación": N_PREGUNTAS_POR_AREA,
                "Porcentaje (%)": float(f"{porcentaje:.1f}"),
                "Percentil": float(percentil), 
                "Clasificación": clasificacion_texto,
                "Color": APTITUDES_MAP[area].color
            })
        
        return pd.DataFrame(resultados_data)

# =============================================================================
# CAPA DE VISUALIZACIÓN - GENERADOR DE GRÁFICOS
# =============================================================================

class ChartGenerator:
    """Generador de gráficos profesionales."""
    
    @staticmethod
    def create_radar_chart(df_resultados: pd.DataFrame) -> go.Figure:
        """Crea gráfico de radar del perfil aptitudinal."""
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=df_resultados['Percentil'].tolist(),
            theta=df_resultados['Código'].tolist(),
            fill='toself',
            name='Perfil Aptitudinal',
            line=dict(color='rgb(0, 123, 255)', width=2),
            fillcolor='rgba(0, 123, 255, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=10)
                ),
                angularaxis=dict(tickfont=dict(size=12))
            ),
            showlegend=False,
            title=dict(
                text="<b>Perfil Aptitudinal GATB</b>",
                font=dict(size=20, color='#2c3e50'),
                x=0.5,
                xanchor='center'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    @staticmethod
    def create_bar_chart(df_resultados: pd.DataFrame) -> go.Figure:
        """Crea gráfico de barras horizontales."""
        df_sorted = df_resultados.sort_values('Percentil', ascending=True)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=df_sorted['Código'],
            x=df_sorted['Percentil'],
            orientation='h',
            marker=dict(
                color=df_sorted['Percentil'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Percentil")
            ),
            text=df_sorted['Percentil'].round(1).astype(str) + '%',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Percentil: %{x:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text="<b>Ranking de Aptitudes por Percentil</b>",
                font=dict(size=20, color='#2c3e50'),
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="Percentil (%)",
            yaxis_title="Aptitud",
            height=500,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(245,245,245,1)',
            xaxis=dict(range=[0, 105])
        )
        
        return fig
    
    @staticmethod
    def create_distribution_chart(df_resultados: pd.DataFrame) -> go.Figure:
        """Crea gráfico de distribución de clasificaciones."""
        clasificaciones = df_resultados['Clasificación'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=clasificaciones.index,
            values=clasificaciones.values,
            hole=0.4,
            marker=dict(colors=['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#95a5a6']),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(
                text="<b>Distribución de Clasificaciones</b>",
                font=dict(size=20, color='#2c3e50'),
                x=0.5,
                xanchor='center'
            ),
            height=400,
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    @staticmethod
    def create_heatmap(df_resultados: pd.DataFrame) -> go.Figure:
        """Crea mapa de calor de fortalezas/debilidades."""
        # Crear matriz para heatmap
        data_matrix = []
        for _, row in df_resultados.iterrows():
            data_matrix.append([row['Percentil']])
        
        fig = go.Figure(data=go.Heatmap(
            z=data_matrix,
            x=['Nivel de Competencia'],
            y=df_resultados['Código'].tolist(),
            colorscale='RdYlGn',
            text=[[f"{val:.0f}%" for val in row] for row in data_matrix],
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="Percentil"),
            hovertemplate='<b>%{y}</b><br>Percentil: %{z:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text="<b>Mapa de Calor - Fortalezas y Debilidades</b>",
                font=dict(size=20, color='#2c3e50'),
                x=0.5,
                xanchor='center'
            ),
            height=500,
            yaxis_title="Aptitud",
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    @staticmethod
    def create_comparison_chart(df_resultados: pd.DataFrame, avg_percentil: float) -> go.Figure:
        """Crea gráfico de comparación con la media."""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Percentil Actual',
            x=df_resultados['Código'],
            y=df_resultados['Percentil'],
            marker=dict(color=df_resultados['Color'])
        ))
        
        fig.add_trace(go.Scatter(
            name='Promedio General',
            x=df_resultados['Código'],
            y=[avg_percentil] * len(df_resultados),
            mode='lines',
            line=dict(color='red', width=3, dash='dash')
        ))
        
        fig.update_layout(
            title=dict(
                text="<b>Comparación con Promedio Personal</b>",
                font=dict(size=20, color='#2c3e50'),
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="Aptitud",
            yaxis_title="Percentil (%)",
            height=400,
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(245,245,245,1)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig

# =============================================================================
# CAPA DE LÓGICA - ADMINISTRADOR DE ESTADO
# =============================================================================

class StateManager:
    """Gestor centralizado del estado de la aplicación."""
    
    @staticmethod
    def initialize():
        """Inicializa el estado de la aplicación."""
        if 'stage' not in st.session_state:
            st.session_state.stage = 'inicio'
        if 'respuestas' not in st.session_state:
            st.session_state.respuestas = {}
        if 'area_actual_index' not in st.session_state:
            st.session_state.area_actual_index = 0
        if 'error_msg' not in st.session_state:
            st.session_state.error_msg = ""
        if 'resultados_df' not in st.session_state:
            st.session_state.resultados_df = pd.DataFrame()
        if 'df_preguntas' not in st.session_state:
            st.session_state.df_preguntas = QuestionBank.generate_questions()
        if 'navigation_flag' not in st.session_state:
            st.session_state.navigation_flag = False
    
    @staticmethod
    def set_stage(new_stage: str):
        """Cambia la etapa sin usar st.rerun() en callback."""
        st.session_state.stage = new_stage
        st.session_state.error_msg = ""
        st.session_state.navigation_flag = True
    
    @staticmethod
    def check_all_answered(area: str) -> Tuple[bool, int]:
        """Verifica si todas las preguntas del área han sido respondidas."""
        preguntas_area = st.session_state.df_preguntas[st.session_state.df_preguntas['area'] == area]
        pregunta_ids_area = set(preguntas_area['id'])
        answered_count = sum(1 for q_id in pregunta_ids_area if st.session_state.respuestas.get(q_id) is not None)
        return answered_count == N_PREGUNTAS_POR_AREA, answered_count
    
    @staticmethod
    def get_current_area() -> str:
        """Obtiene el área actual."""
        return AREAS[st.session_state.area_actual_index]

# =============================================================================
# CAPA DE LÓGICA - CONTROLADOR DE NAVEGACIÓN
# =============================================================================

class NavigationController:
    """Controlador de navegación entre secciones."""
    
    @staticmethod
    def siguiente_area():
        """Avanza a la siguiente área o finaliza el test."""
        area_actual = StateManager.get_current_area()
        all_answered, _ = StateManager.check_all_answered(area_actual)
        
        if not all_answered:
            st.session_state.error_msg = "🚨 ¡Alerta! Por favor, complete las 12 preguntas de la sección actual antes de avanzar."
            return
        
        if st.session_state.area_actual_index < len(AREAS) - 1:
            st.session_state.area_actual_index += 1
            StateManager.set_stage('test_activo')
        else:
            NavigationController.finalizar_test()
    
    @staticmethod
    def finalizar_test():
        """Finaliza el test y calcula resultados."""
        st.session_state.resultados_df = ResultsCalculator.calcular_resultados(
            st.session_state.df_preguntas,
            st.session_state.respuestas
        )
        StateManager.set_stage('resultados')
    
    @staticmethod
    def resolver_todo():
        """Resuelve automáticamente todas las preguntas (demo)."""
        for _, row in st.session_state.df_preguntas.iterrows():
            st.session_state.respuestas[row['id']] = row['respuesta_correcta']
        
        st.session_state.area_actual_index = len(AREAS) - 1
        NavigationController.finalizar_test()
    
    @staticmethod
    def reiniciar():
        """Reinicia la aplicación."""
        st.session_state.respuestas = {}
        st.session_state.area_actual_index = 0
        st.session_state.resultados_df = pd.DataFrame()
        st.session_state.error_msg = ""
        StateManager.set_stage('inicio')

# =============================================================================
# CAPA DE PRESENTACIÓN - COMPONENTES UI
# =============================================================================

class UIComponents:
    """Componentes de interfaz de usuario."""
    
    @staticmethod
    def progress_bar_area(area_index: int, total: int, area_name: str, code: str):
        """Muestra barra de progreso del área actual."""
        progress = (area_index + 1) / total
        st.progress(progress, text=f"Progreso: **{area_name}** ({code})")
    
    @staticmethod
    def error_alert(message: str):
        """Muestra alerta de error."""
        if message:
            st.error(message)
    
    @staticmethod
    def scroll_to_top():
        """JavaScript para scroll al inicio."""
        st.html("""
            <script>
                setTimeout(function() {
                    window.parent.scrollTo({ top: 0, behavior: 'smooth' });
                }, 50);
            </script>
        """)

# =============================================================================
# CAPA DE PRESENTACIÓN - GENERADOR DE REPORTES
# =============================================================================

class ReportGenerator:
    """Generador de informes profesionales."""
    
    @staticmethod
    def get_analisis_detallado(df_resultados: pd.DataFrame) -> Dict:
        """Genera análisis detallado de fortalezas y debilidades."""
        df_sorted = df_resultados.sort_values(by='Percentil', ascending=False)
        
        # Top 3 Fortalezas
        top_3 = df_sorted.head(3)
        fortalezas_text = "<ul>"
        for _, row in top_3.iterrows():
            fortalezas_text += f"<li><strong>{row['Área']} ({row['Percentil']:.0f}%)</strong>: Capacidad sobresaliente que puede ser aprovechada en contextos profesionales especializados.</li>"
        fortalezas_text += "</ul>"
        
        # Bottom 3 a Mejorar
        bottom_3 = df_sorted.tail(3)
        mejoras_text = "<ul>"
        for _, row in bottom_3.iterrows():
            mejoras_text += f"<li><strong>{row['Área']} ({row['Percentil']:.0f}%)</strong>: Área que requiere desarrollo mediante entrenamiento específico y práctica continua.</li>"
        mejoras_text += "</ul>"
        
        # Potencial Ocupacional
        top_area = top_3.iloc[0]['Área']
        if top_area in ["Razonamiento General", "Razonamiento Verbal", "Razonamiento Numérico"]:
            potencial = "Roles Estratégicos y de Gestión (Consultoría, Finanzas, Liderazgo de Proyectos)"
            perfil = "Alto Potencial Cognitivo"
        elif top_area in ["Razonamiento Mecánico", "Razonamiento Espacial", "Razonamiento Técnico"]:
            potencial = "Roles de Ingeniería, Arquitectura y Mantenimiento Técnico"
            perfil = "Fuerte Perfil Técnico-Estructural"
        else:
            potencial = "Roles Administrativos, Control de Calidad y Operaciones"
            perfil = "Sólido Perfil Operativo"
        
        return {
            "fortalezas": fortalezas_text,
            "mejoras": mejoras_text,
            "potencial": potencial,
            "perfil": perfil,
            "top_area": top_area
        }
    
    @staticmethod
    def get_estrategias_mejora(area: str) -> str:
        """Estrategias de mejora específicas por área."""
        estrategias = {
            "Razonamiento General": "Practicar juegos de lógica, resolver acertijos y leer material complejo. **Aplicación:** Liderazgo estratégico y toma de decisiones.",
            "Razonamiento Verbal": "Ampliar vocabulario con lectura activa y redacción estructurada. **Aplicación:** Comunicación ejecutiva y negociación.",
            "Razonamiento Numérico": "Ejercicios de cálculo mental y análisis estadístico. **Aplicación:** Análisis financiero y presupuestario.",
            "Razonamiento Espacial": "Puzzles 3D, rotación mental y lectura de planos. **Aplicación:** Diseño y planeación arquitectónica.",
            "Velocidad Perceptiva": "Ejercicios de búsqueda y comparación rápida. **Aplicación:** Revisión documental y control de calidad.",
            "Precisión Manual": "Manipulación fina y ensamblaje detallado. **Aplicación:** Cirugía, joyería y micro-ensamblaje.",
            "Coordinación Manual": "Actividades ojo-mano como deportes de precisión. **Aplicación:** Operación de maquinaria compleja.",
            "Atención Concentrada": "Técnica Pomodoro y sesiones de enfoque. **Aplicación:** Auditoría y vigilancia.",
            "Razonamiento Mecánico": "Estudio de máquinas simples y física aplicada. **Aplicación:** Mantenimiento industrial.",
            "Razonamiento Abstracto": "Matrices figurativas y patrones lógicos. **Aplicación:** Análisis predictivo.",
            "Razonamiento Clerical": "Organización y archivo sistemático. **Aplicación:** Gestión documental.",
            "Razonamiento Técnico": "Diagramas de flujo y troubleshooting. **Aplicación:** Soporte técnico.",
        }
        return estrategias.get(area, "Entrenamiento específico recomendado.")
    
    @staticmethod
    def get_metricas_estadisticas(df_resultados: pd.DataFrame) -> Dict:
        """Calcula métricas estadísticas del perfil."""
        return {
            "media": df_resultados['Percentil'].mean(),
            "mediana": df_resultados['Percentil'].median(),
            "desviacion": df_resultados['Percentil'].std(),
            "minimo": df_resultados['Percentil'].min(),
            "maximo": df_resultados['Percentil'].max(),
            "rango": df_resultados['Percentil'].max() - df_resultados['Percentil'].min(),
            "coef_variacion": (df_resultados['Percentil'].std() / df_resultados['Percentil'].mean()) * 100
        }

# =============================================================================
# VISTAS DE LA APLICACIÓN
# =============================================================================

def vista_inicio():
    """Página de inicio."""
    UIComponents.scroll_to_top()
    
    st.title("🧠 Batería de Aptitudes Generales – GATB Profesional")
    st.header("Evaluación Estructurada de 12 Factores Aptitudinales")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"""
        **🎯 Objetivo:** Medir **12 factores clave** de aptitud con **{N_TOTAL_PREGUNTAS} ítems**.
        
        **📋 Estructura del Test:**
        - **Total de Secciones:** {len(AREAS)}
        - **Preguntas por Sección:** {N_PREGUNTAS_POR_AREA}
        
        **⏱️ Duración estimada:** 45-60 minutos
        """)
        
        with st.expander("📚 Ver todas las aptitudes evaluadas"):
            for area, config in APTITUDES_MAP.items():
                st.markdown(f"**{config.code} - {area}:** {config.description}")
    
    with col2:
        st.subheader("Simulación Profesional")
        st.warning("⚠️ **Nota:** Esta es una simulación educativa.")
        
        if st.button("🚀 Iniciar Evaluación", type="primary", use_container_width=True):
            st.session_state.area_actual_index = 0
            StateManager.set_stage('test_activo')
            st.rerun()
        
        if st.button("✨ Resolver Todo (Demo)", type="secondary", use_container_width=True):
            NavigationController.resolver_todo()
            st.rerun()

def vista_test_activo():
    """Sección de preguntas."""
    area_actual = StateManager.get_current_area()
    total_areas = len(AREAS)
    current_area_index = st.session_state.area_actual_index
    
    st.title(f"Sección {current_area_index + 1} de {total_areas}: {area_actual}")
    UIComponents.progress_bar_area(
        current_area_index, 
        total_areas, 
        area_actual, 
        APTITUDES_MAP[area_actual].code
    )
    st.markdown("---")
    
    preguntas_area = st.session_state.df_preguntas[st.session_state.df_preguntas['area'] == area_actual]
    all_answered, answered_count = StateManager.check_all_answered(area_actual)
    
    UIComponents.error_alert(st.session_state.error_msg)
    
    with st.container(border=True):
        st.subheader(f"Responda a los {N_PREGUNTAS_POR_AREA} ítems de {area_actual}")
        st.caption(f"📝 {APTITUDES_MAP[area_actual].description}")
        
        q_num = 1
        for _, row in preguntas_area.iterrows():
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
                    selected_option_full = st.session_state[f'q_{q_id}']
                    selected_key = selected_option_full.split(')')[0].strip()
                    st.session_state.respuestas[q_id] = selected_key
                    st.session_state.error_msg = ""
                
                st.radio(
                    f"Seleccione su respuesta:",
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
        submit_label = f"➡️ Siguiente: {next_area_name}"
    else:
        submit_label = "✅ Finalizar y Ver Resultados"
    
    is_disabled = not all_answered
    
    if st.button(submit_label, type="primary", use_container_width=True, disabled=is_disabled, key="btn_siguiente"):
        NavigationController.siguiente_area()
        st.rerun()
    
    if not all_answered:
        st.warning(f"Faltan **{N_PREGUNTAS_POR_AREA - answered_count}** preguntas por responder.")

def vista_resultados():
    """Informe de resultados profesional."""
    UIComponents.scroll_to_top()
    
    df_resultados = st.session_state.resultados_df
    analisis = ReportGenerator.get_analisis_detallado(df_resultados)
    metricas = ReportGenerator.get_metricas_estadisticas(df_resultados)
    
    st.title("🏆 Informe Ejecutivo de Perfil Aptitudinal GATB")
    st.markdown("---")
    
    # === 1. RESUMEN EJECUTIVO ===
    avg_percentil = df_resultados['Percentil'].mean()
    calificacion, detalle_calificacion, color_calificacion = ResultsCalculator.calificar_global(avg_percentil)
    
    st.subheader("1. Resumen Ejecutivo")
    
    st.markdown(f"""
    <div style="background-color: {color_calificacion}; padding: 25px; border-radius: 15px; color: white; margin-bottom: 30px; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,0.4);">
        <h2 style="margin: 0; font-size: 2.5em;">{calificacion}</h2>
        <p style="margin: 10px 0; font-size: 1.3em;">Percentil Promedio: {avg_percentil:.1f}%</p>
        <p style="font-size: 1.1em; margin: 0; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.5);">{detalle_calificacion}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas Estadísticas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Media", f"{metricas['media']:.1f}%")
    with col2:
        st.metric("Mediana", f"{metricas['mediana']:.1f}%")
    with col3:
        st.metric("Desv. Estándar", f"{metricas['desviacion']:.1f}")
    with col4:
        st.metric("Rango", f"{metricas['rango']:.1f}")
    
    st.markdown(f"""
    <div style="padding: 15px; border-left: 5px solid #ff9900; background-color: #fff8e1; border-radius: 5px; margin: 20px 0;">
        <p style="font-weight: bold; margin: 0;">Perfil Identificado:</p>
        <p style="margin: 5px 0 0 0;">{analisis['perfil']} con orientación hacia <strong>{analisis['top_area']}</strong>. Potencial ocupacional en: {analisis['potencial']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === 2. VISUALIZACIONES PROFESIONALES ===
    st.subheader("2. Análisis Visual del Perfil")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Gráfico Radar",
        "📈 Ranking",
        "🎯 Comparación",
        "🔥 Mapa de Calor",
        "🥧 Distribución"
    ])
    
    with tab1:
        st.plotly_chart(ChartGenerator.create_radar_chart(df_resultados), use_container_width=True)
    
    with tab2:
        st.plotly_chart(ChartGenerator.create_bar_chart(df_resultados), use_container_width=True)
    
    with tab3:
        st.plotly_chart(ChartGenerator.create_comparison_chart(df_resultados, avg_percentil), use_container_width=True)
    
    with tab4:
        st.plotly_chart(ChartGenerator.create_heatmap(df_resultados), use_container_width=True)
    
    with tab5:
        st.plotly_chart(ChartGenerator.create_distribution_chart(df_resultados), use_container_width=True)
    
    st.markdown("---")
    
    # === 3. ANÁLISIS COMPARATIVO ===
    st.subheader("3. Análisis Comparativo del Perfil")
    
    col_fortaleza, col_mejora = st.columns(2)
    
    with col_fortaleza:
        st.markdown('<h4 style="color: #008000;">🌟 Fortalezas Principales (Top 3)</h4>', unsafe_allow_html=True)
        st.markdown(analisis['fortalezas'], unsafe_allow_html=True)
        st.success("Estas aptitudes son pilares para su desarrollo profesional.")
    
    with col_mejora:
        st.markdown('<h4 style="color: #dc143c;">📉 Áreas de Oportunidad (Bottom 3)</h4>', unsafe_allow_html=True)
        st.markdown(analisis['mejoras'], unsafe_allow_html=True)
        st.error("Estas áreas requieren atención y desarrollo continuo.")
    
    st.markdown("---")
    
    # === 4. POTENCIAL OCUPACIONAL ===
    st.subheader("4. Potencial de Rol y Estrategia de Desarrollo")
    
    st.markdown(f"""
    <div style="padding: 20px; border: 2px solid #4682b4; background-color: #f0f8ff; border-radius: 10px; margin-bottom: 20px;">
        <h5 style="margin-top: 0; color: #4682b4;">🎯 Potencial Ocupacional Recomendado</h5>
        <p style="font-size: 1.15em; font-weight: bold; margin: 10px 0;">{analisis['potencial']}</p>
        <p style="margin: 5px 0 0 0; color: #555;">Basado en su perfil <strong>{analisis['perfil']}</strong>, se recomienda enfocarse en roles que aprovechen sus fortalezas en <strong>{analisis['top_area']}</strong>.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === 5. ESTRATEGIAS DE DESARROLLO ===
    st.markdown("#### **Estrategias Individualizadas de Desarrollo**")
    st.info("Plan de acción para las áreas con percentiles ≤ 40% o que requieran mejora continua.")
    
    bottom_areas = df_resultados[df_resultados['Percentil'] <= 40]['Área'].tolist()
    
    if bottom_areas:
        for area in bottom_areas:
            estrategia = ReportGenerator.get_estrategias_mejora(area)
            with st.expander(f"📚 Estrategia para **{area}** (`{APTITUDES_MAP[area].code}`)", expanded=False):
                st.markdown(f"**Nivel de Prioridad:** ALTA")
                st.markdown(f"**Plan de Acción:** {estrategia}")
    else:
        st.balloons()
        st.success("¡Excelente! Su perfil es equilibrado. Continúe desarrollando sus fortalezas para alcanzar la maestría profesional.")
    
    st.markdown("---")
    
    # === 6. TABLA DETALLADA ===
    with st.expander("📊 Ver Tabla Completa de Resultados", expanded=False):
        st.dataframe(
            df_resultados[['Área', 'Código', 'Puntuación Bruta', 'Máxima Puntuación', 'Porcentaje (%)', 'Percentil', 'Clasificación']],
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # === 7. ACCIONES ===
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Realizar Nueva Evaluación", type="primary", use_container_width=True):
            NavigationController.reiniciar()
            st.rerun()

# =============================================================================
# FLUJO PRINCIPAL
# =============================================================================

def main():
    """Función principal de la aplicación."""
    StateManager.initialize()
    
    # Manejo de navegación sin st.rerun() en callbacks
    if st.session_state.navigation_flag:
        st.session_state.navigation_flag = False
        st.rerun()
    
    if st.session_state.stage == 'inicio':
        vista_inicio()
    elif st.session_state.stage == 'test_activo':
        vista_test_activo()
    elif st.session_state.stage == 'resultados':
        vista_resultados()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <p style='text-align: center; font-size: small; color: grey;'>
        📋 Batería GATB Profesional - Versión Simulada para Fines Educativos<br>
        Los resultados son ilustrativos y no constituyen un diagnóstico profesional oficial.<br>
        © 2025 - Desarrollado con Streamlit | Arquitectura Modular Profesional
    </p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
