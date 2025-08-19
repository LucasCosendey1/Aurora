# main.py - Arquivo principal da AURORA
import os
import sys
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

try:
    from aurora_ai import AuroraAI
except ImportError:
    AuroraAI = None
    st.warning("Módulo aurora_ai não encontrado. Funcionalidades de IA desabilitadas.")

# Configuração da página
st.set_page_config(
    page_title="AURORA - Gestão Inteligente",
    page_icon="🌅",
    layout="wide"
)

# Inicializar IA
@st.cache_resource
def init_ai():
    # Para Ollama, não precisamos da OpenAI API Key
    try:
        return AuroraAI()  # Usar detecção automática de URL
    except Exception as e:
        st.error(f"⚠️ Erro ao inicializar IA: {str(e)}")
        return None

# Função para carregar dados de exemplo
@st.cache_data
def carregar_dados_exemplo():
    """Cria dados de exemplo para teste"""
    
    dados = {
        'id': range(1, 21),
        'nome': [
            'Migração Database Principal', 'Configurar Azure AD', 'Migrar APIs REST',
            'Testar Integração SAP', 'Documentar Processos', 'Treinar Equipe Técnica',
            'Backup Sistemas Legados', 'Validar Segurança', 'Migrar Storage Files',
            'Configurar Load Balancer', 'Atualizar DNS', 'Migrar Email Server',
            'Configurar Monitoring', 'Testar Disaster Recovery', 'Migrar App Mobile',
            'Validar Performance', 'Configurar Firewall', 'Migrar Data Warehouse',
            'Homologar Ambiente', 'Go-Live Preparação'
        ],
        'descricao': [
            'Migrar 500GB de SQL Server para Azure SQL',
            'Configurar autenticação SSO com Azure AD',
            'Portar 15 APIs para Azure Functions',
            'Validar integração com SAP após migração',
            'Criar documentação técnica completa',
            'Capacitar time em Azure DevOps',
            'Realizar backup completo antes da migração',
            'Auditoria de segurança pós-migração',
            'Migrar 2TB de arquivos para Blob Storage',
            'Implementar Azure Load Balancer',
            'Atualizar registros DNS para novo ambiente',
            'Migrar Exchange para Office 365',
            'Configurar Azure Monitor e Alerts',
            'Teste completo de DR',
            'Adaptar app mobile para novos endpoints',
            'Teste de carga e performance',
            'Configurar Azure Firewall e NSGs',
            'Migrar 5TB de DW para Synapse',
            'Homologação com usuários chave',
            'Preparação final para produção'
        ],
        'responsavel': [
            'João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Lima', 'Carlos Souza',
            'João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Lima', 'Carlos Souza',
            'João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Lima', 'Carlos Souza',
            'João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Lima', 'Carlos Souza'
        ],
        'status': [
            'Em Progresso', 'Concluído', 'Em Progresso', 'Atrasado', 'Não Iniciado',
            'Em Progresso', 'Concluído', 'Em Progresso', 'Atrasado', 'Não Iniciado',
            'Concluído', 'Em Progresso', 'Não Iniciado', 'Em Progresso', 'Atrasado',
            'Em Progresso', 'Concluído', 'Em Progresso', 'Não Iniciado', 'Não Iniciado'
        ],
        'prioridade': [
            'Alta', 'Alta', 'Alta', 'Média', 'Baixa',
            'Média', 'Alta', 'Alta', 'Média', 'Baixa',
            'Alta', 'Alta', 'Média', 'Alta', 'Média',
            'Alta', 'Alta', 'Alta', 'Média', 'Alta'
        ],
        'data_inicio': pd.date_range(start='2024-01-15', periods=20, freq='3D'),
        'data_fim': pd.date_range(start='2024-02-01', periods=20, freq='3D'),
        'percentual_completo': [
            75, 100, 60, 30, 0, 45, 100, 80, 25, 10,
            100, 55, 0, 40, 20, 65, 100, 70, 15, 5
        ]
    }
    
    df = pd.DataFrame(dados)
    
    # Calcular se está atrasado
    hoje = datetime.now()
    df['atrasada'] = (df['data_fim'] < hoje) & (df['status'] != 'Concluído')
    df['dias_atraso'] = df.apply(
        lambda x: (hoje - x['data_fim']).days if x['atrasada'] else 0, 
        axis=1
    )
    
    return df

# Função para mostrar alertas do dia
def mostrar_alertas():
    with st.container():
        st.markdown("### 🚨 Alertas do Dia")
        
        # Container com alertas dinâmicos baseados nos dados
        alertas = [
            {"tipo": "⚠️", "texto": "Reunião às 14h - Revisão do projeto MG"},
            {"tipo": "📋", "texto": "Pendente - Aprovação relatório MT"},
            {"tipo": "🔔", "texto": "Deadline SE - Finalizar amanhã"},
            {"tipo": "🚨", "texto": "3 tarefas atrasadas requerem atenção"}
        ]
        
        for alerta in alertas:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(alerta["tipo"])
            with col2:
                st.markdown(f"**{alerta['texto']}**")

# Função para página de atividades
def pagina_atividades(df):
    st.title("📋 Atividades")
    
    # Filtros específicos para atividades
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filtrar por Status",
            ["Todos"] + list(df['status'].unique())
        )
    
    with col2:
        responsavel_filter = st.selectbox(
            "Filtrar por Responsável",
            ["Todos"] + list(df['responsavel'].unique())
        )
    
    with col3:
        prioridade_filter = st.selectbox(
            "Filtrar por Prioridade",
            ["Todos"] + list(df['prioridade'].unique())
        )
    
    # Aplicar filtros
    df_filtered = df.copy()
    if status_filter != "Todos":
        df_filtered = df_filtered[df_filtered['status'] == status_filter]
    if responsavel_filter != "Todos":
        df_filtered = df_filtered[df_filtered['responsavel'] == responsavel_filter]
    if prioridade_filter != "Todos":
        df_filtered = df_filtered[df_filtered['prioridade'] == prioridade_filter]
    
    # Lista de atividades
    for _, atividade in df_filtered.iterrows():
        with st.expander(f"{atividade['nome']} - {atividade['status']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Descrição:** {atividade['descricao']}")
                st.write(f"**Responsável:** {atividade['responsavel']}")
                st.write(f"**Prioridade:** {atividade['prioridade']}")
                st.progress(atividade['percentual_completo'] / 100)
                st.write(f"**Progresso:** {atividade['percentual_completo']}%")
            
            with col2:
                if atividade['atrasada']:
                    st.error(f"Atrasada: {atividade['dias_atraso']} dias")
                else:
                    st.success("No prazo")
                
                st.write(f"**Início:** {atividade['data_inicio'].strftime('%d/%m/%Y')}")
                st.write(f"**Fim:** {atividade['data_fim'].strftime('%d/%m/%Y')}")

# Função para página de membros
def pagina_membros(df):
    st.title("👥 Membros da Equipe")
    
    # Estatísticas por membro
    membros_stats = df.groupby('responsavel').agg({
        'id': 'count',
        'percentual_completo': 'mean',
        'atrasada': 'sum'
    }).round(1)
    
    membros_stats.columns = ['Total Tarefas', 'Progresso Médio', 'Tarefas Atrasadas']
    
    # Adicionar taxa de conclusão
    conclusao_por_membro = df[df['status'] == 'Concluído'].groupby('responsavel').size()
    membros_stats['Tarefas Concluídas'] = conclusao_por_membro.fillna(0).astype(int)
    membros_stats['Taxa Conclusão (%)'] = (membros_stats['Tarefas Concluídas'] / membros_stats['Total Tarefas'] * 100).round(1)
    
    st.dataframe(membros_stats, use_container_width=True)
    
    # Gráfico de performance dos membros
    fig_membros = px.bar(
        x=membros_stats.index,
        y=membros_stats['Taxa Conclusão (%)'],
        title='Taxa de Conclusão por Membro',
        labels={'x': 'Membro', 'y': 'Taxa de Conclusão (%)'}
    )
    st.plotly_chart(fig_membros, use_container_width=True)

# Função para projetos de migração
def pagina_projeto_migracao(projeto, df):
    st.title(f"🔄 {projeto}")
    
    # Simular dados específicos do projeto
    if "Minas Gerais" in projeto:
        projeto_filter = ["Migração Database Principal", "Configurar Azure AD", "Migrar APIs REST"]
        descricao_projeto = "Migração completa da infraestrutura de TI do escritório de Minas Gerais para a nuvem Azure."
        progress_geral = 65
    elif "Mato Grosso" in projeto:
        projeto_filter = ["Testar Integração SAP", "Documentar Processos", "Treinar Equipe Técnica"]
        descricao_projeto = "Migração e modernização dos sistemas do escritório de Mato Grosso."
        progress_geral = 45
    else:  # Sergipe
        projeto_filter = ["Backup Sistemas Legados", "Validar Segurança", "Migrar Storage Files"]
        descricao_projeto = "Implementação de nova infraestrutura no escritório de Sergipe."
        progress_geral = 30
    
    st.info(descricao_projeto)
    
    # Progresso geral do projeto
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Progresso Geral", f"{progress_geral}%")
    with col2:
        tarefas_projeto = df[df['nome'].isin(projeto_filter)]
        st.metric("Total Tarefas", len(tarefas_projeto))
    with col3:
        concluidas = len(tarefas_projeto[tarefas_projeto['status'] == 'Concluído'])
        st.metric("Concluídas", concluidas)
    
    # Barra de progresso visual
    st.progress(progress_geral / 100)
    
    # Tarefas do projeto
    st.subheader("Tarefas do Projeto")
    df_projeto = df[df['nome'].isin(projeto_filter)]
    
    st.dataframe(
        df_projeto[['nome', 'responsavel', 'status', 'prioridade', 'data_fim', 'percentual_completo']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "percentual_completo": st.column_config.ProgressColumn(
                "Progresso",
                min_value=0,
                max_value=100,
            ),
            "data_fim": st.column_config.DateColumn("Data Fim", format="DD/MM/YYYY"),
        }
    )

# Função principal do Dashboard
def dashboard_principal(df, ai):
    st.title("🌅 AURORA")

    st.markdown("---")
    # KPIs principais
    st.header("📈 Indicadores Principais")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_tarefas = len(df)
        st.metric("Total Tarefas", total_tarefas)
    
    with col2:
        concluidas = len(df[df['status'] == 'Concluído'])
        percentual_conclusao = (concluidas / total_tarefas * 100) if total_tarefas > 0 else 0
        st.metric("Concluídas", concluidas, f"{percentual_conclusao:.1f}%")
    
    with col3:
        em_progresso = len(df[df['status'] == 'Em Progresso'])
        st.metric("Em Progresso", em_progresso)
    
    with col4:
        atrasadas = len(df[df['atrasada'] == True])
        st.metric("Atrasadas", atrasadas, f"-{atrasadas}", delta_color="inverse")
    
    with col5:
        nao_iniciadas = len(df[df['status'] == 'Não Iniciado'])
        st.metric("Não Iniciadas", nao_iniciadas)
    
    st.markdown("---")
    
    
    # Seção de IA - Resumo Executivo
    if ai:
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.container():
                
                if st.button("🔄 Gerar Análise"):
                    with st.spinner("Analisando dados com IA..."):
                        resumo = ai.gerar_resumo_executivo(df)
                        st.info(resumo)
                        
                        # Salvar análise
                        st.session_state['ultima_analise'] = {
                            'timestamp': datetime.now(),
                            'resumo': resumo
                        }
                
                # Mostrar última análise se existir
                if 'ultima_analise' in st.session_state:
                    st.caption(f"Última análise: {st.session_state['ultima_analise']['timestamp'].strftime('%H:%M:%S')}")
        
        with col2:
            st.subheader("⚠️ Alertas Críticos") 
            
            # Identificar tarefas críticas
            tarefas_criticas = df[
                (df['atrasada'] == True) | 
                (df['prioridade'] == 'Alta')
            ].head(3)
            
            for _, tarefa in tarefas_criticas.iterrows():
                if tarefa['atrasada']:
                    st.error(f"🚨 **{tarefa['nome']}** - {tarefa['dias_atraso']} dias de atraso")
                else:
                    st.warning(f"⚡ **{tarefa['nome']}** - Prioridade Alta")
    
    st.markdown("---")
    
    # Gráficos
    st.header("📊 Visualizações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de Pizza - Status
        fig_status = px.pie(
            df, 
            names='status', 
            title='Distribuição por Status',
            color_discrete_map={
                'Concluído': '#00CC88',
                'Em Progresso': '#36A2EB',
                'Atrasado': '#FF6384',
                'Não Iniciado': '#FFCE56'
            }
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Gráfico de Barras - Por Responsável
        responsavel_counts = df.groupby(['responsavel', 'status']).size().reset_index(name='count')
        fig_resp = px.bar(
            responsavel_counts,
            x='responsavel',
            y='count',
            color='status',
            title='Tarefas por Responsável',
            color_discrete_map={
                'Concluído': '#00CC88',
                'Em Progresso': '#36A2EB',
                'Atrasado': '#FF6384',
                'Não Iniciado': '#FFCE56'
            }
        )
        st.plotly_chart(fig_resp, use_container_width=True)
        
    
    # Timeline de Tarefas
    st.header("📅 Timeline do Projeto")
    
    # Preparar dados para Gantt
    gantt_data = []
    for _, row in df.iterrows():
        gantt_data.append(dict(
            Task=row['nome'],
            Start=row['data_inicio'],
            Finish=row['data_fim'],
            Resource=row['responsavel'],
            Complete=row['percentual_completo']
        ))
    
    if gantt_data:
        fig_gantt = px.timeline(
            gantt_data,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color="Resource",
            title="Cronograma de Tarefas",
            height=400
        )
        fig_gantt.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_gantt, use_container_width=True)
    st.markdown("---")
def main():
    # Inicializar IA
    ai = init_ai()
    
    # Carregar dados
    df = carregar_dados_exemplo()
    
    # SIDEBAR COM MENU E ALERTAS
    with st.sidebar:
        st.title("🌅 AURORA")
        st.markdown("*Gestão Inteligente*")
        st.markdown("---")
        
        # Menu principal
        menu_opcao = st.selectbox(
            "📋 Navegação:",
            ["Principal", "Atividades", "Membros", "Meus Projetos"]
        )
        
        # Submenu para "Meus Projetos"
        projeto_selecionado = None
        if menu_opcao == "Meus Projetos":
            st.markdown("#### 🔄 Projetos Disponíveis:")
            projeto_selecionado = st.radio(
                "Selecione um projeto:",
                ["Migração Minas Gerais", "Migração Mato Grosso", "Migração Sergipe"],
                label_visibility="collapsed"
            )
        
        # Filtros gerais (apenas para algumas páginas)
        if menu_opcao in ["Principal", "Atividades"]:
            st.markdown("---")
            st.header("⚙️ Filtros")
            
            status_filter = st.multiselect(
                "Status",
                options=df['status'].unique(),
                default=df['status'].unique()
            )
            
            responsavel_filter = st.multiselect(
                "Responsável",
                options=df['responsavel'].unique(),
                default=df['responsavel'].unique()
            )
            
            prioridade_filter = st.multiselect(
                "Prioridade",
                options=df['prioridade'].unique(),
                default=df['prioridade'].unique()
            )
            
            # Aplicar filtros
            df = df[
                (df['status'].isin(status_filter)) &
                (df['responsavel'].isin(responsavel_filter)) &
                (df['prioridade'].isin(prioridade_filter))
            ]
        
        # Caixinha de alertas
        st.markdown("---")
        mostrar_alertas()
    
    # CONTEÚDO PRINCIPAL BASEADO NA SELEÇÃO
    if menu_opcao == "Principal":
        dashboard_principal(df, ai)
        
        # Tabela de Tarefas (mantendo da versão original)
        st.header("📋 Lista Detalhada de Tarefas")
        
        # Adicionar análise IA para tarefas selecionadas
        if ai and st.button("🤖 Analisar Prioridades com IA"):
            with st.spinner("Processando tarefas com IA..."):
                df = ai.processar_lote_tarefas(df)
                st.success("✅ Análise concluída!")
        
        # Exibir tabela
        columns_to_show = ['nome', 'responsavel', 'status', 'prioridade', 'data_fim', 'percentual_completo', 'atrasada']
        
        # Se tiver análise IA, mostrar também
        if 'ia_prioridade' in df.columns:
            columns_to_show.extend(['ia_prioridade', 'ia_sugestao'])
        
        st.dataframe(
            df[columns_to_show],
            use_container_width=True,
            hide_index=True,
            column_config={
                "percentual_completo": st.column_config.ProgressColumn(
                    "Progresso",
                    min_value=0,
                    max_value=100,
                ),
                "atrasada": st.column_config.CheckboxColumn("Atrasada"),
                "data_fim": st.column_config.DateColumn("Data Fim", format="DD/MM/YYYY"),
            }
        )
    
    elif menu_opcao == "Atividades":
        pagina_atividades(df)
    
    elif menu_opcao == "Membros":
        pagina_membros(df)
    
    elif menu_opcao == "Meus Projetos" and projeto_selecionado:
        pagina_projeto_migracao(projeto_selecionado, df)
    
    # Rodapé
    st.markdown("---")
    st.caption("🌅 AURORA v1.0 - MVP | Atualizado a cada 30 minutos")

if __name__ == "__main__":
    main()