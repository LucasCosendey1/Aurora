# main.py - Arquivo principal da AURORA

import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px
from dotenv import load_dotenv

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="AURORA - Gestão Inteligente",
    page_icon="🌅",
    layout="wide",
)

load_dotenv()


# ============================================================
# IMPORTAÇÃO DOS MÓDULOS DE IA
# ============================================================

try:
    from aurora_ai import AuroraAI
except ImportError as e:
    AuroraAI = None
    st.error(f"Erro ao importar aurora_ai.py: {e}")

try:
    from chat_aurora import pagina_chat_ia
except ImportError as e:
    pagina_chat_ia = None
    st.error(f"Erro ao importar chat_aurora.py: {e}")


# ============================================================
# INICIALIZAÇÃO DA IA
# ============================================================

@st.cache_resource
def init_ai():
    if AuroraAI is None:
        return None

    try:
        return AuroraAI()
    except Exception as e:
        st.warning(f"Não foi possível inicializar a IA: {e}")
        return None


# ============================================================
# DADOS DE EXEMPLO
# ============================================================

@st.cache_data
def carregar_dados_exemplo():
    """Cria dados de exemplo para teste."""

    dados = {
        "id": range(1, 21),

        "nome": [
            "Migração Database Principal",
            "Configurar Azure AD",
            "Migrar APIs REST",
            "Testar Integração SAP",
            "Documentar Processos",
            "Treinar Equipe Técnica",
            "Backup Sistemas Legados",
            "Validar Segurança",
            "Migrar Storage Files",
            "Configurar Load Balancer",
            "Atualizar DNS",
            "Migrar Email Server",
            "Configurar Monitoring",
            "Testar Disaster Recovery",
            "Migrar App Mobile",
            "Validar Performance",
            "Configurar Firewall",
            "Migrar Data Warehouse",
            "Homologar Ambiente",
            "Go-Live Preparação",
        ],

        "descricao": [
            "Migrar 500GB de SQL Server para Azure SQL",
            "Configurar autenticação SSO com Azure AD",
            "Portar 15 APIs para Azure Functions",
            "Validar integração com SAP após migração",
            "Criar documentação técnica completa",
            "Capacitar time em Azure DevOps",
            "Realizar backup completo antes da migração",
            "Auditoria de segurança pós-migração",
            "Migrar 2TB de arquivos para Blob Storage",
            "Implementar Azure Load Balancer",
            "Atualizar registros DNS para novo ambiente",
            "Migrar Exchange para Office 365",
            "Configurar Azure Monitor e Alerts",
            "Teste completo de Disaster Recovery",
            "Adaptar app mobile para novos endpoints",
            "Teste de carga e performance",
            "Configurar Azure Firewall e NSGs",
            "Migrar 5TB de DW para Synapse",
            "Homologação com usuários-chave",
            "Preparação final para produção",
        ],

        "responsavel": [
            "João Silva", "Maria Santos", "Pedro Costa",
            "Ana Lima", "Carlos Souza", "João Silva",
            "Maria Santos", "Pedro Costa", "Ana Lima",
            "Carlos Souza", "João Silva", "Maria Santos",
            "Pedro Costa", "Ana Lima", "Carlos Souza",
            "João Silva", "Maria Santos", "Pedro Costa",
            "Ana Lima", "Carlos Souza",
        ],

        "status": [
            "Em Progresso", "Concluído", "Em Progresso",
            "Atrasado", "Não Iniciado", "Em Progresso",
            "Concluído", "Em Progresso", "Atrasado",
            "Não Iniciado", "Concluído", "Em Progresso",
            "Não Iniciado", "Em Progresso", "Atrasado",
            "Em Progresso", "Concluído", "Em Progresso",
            "Não Iniciado", "Não Iniciado",
        ],

        "prioridade": [
            "Alta", "Alta", "Alta", "Média", "Baixa",
            "Média", "Alta", "Alta", "Média", "Baixa",
            "Alta", "Alta", "Média", "Alta", "Média",
            "Alta", "Alta", "Alta", "Média", "Alta",
        ],

        "data_inicio": pd.date_range(
            start="2024-01-15",
            periods=20,
            freq="3D",
        ),

        "data_fim": pd.date_range(
            start="2024-02-01",
            periods=20,
            freq="3D",
        ),

        "percentual_completo": [
            75, 100, 60, 30, 0, 45, 100, 80, 25, 10,
            100, 55, 0, 40, 20, 65, 100, 70, 15, 5,
        ],
    }

    df = pd.DataFrame(dados)

    hoje = datetime.now()

    df["atrasada"] = (
        (df["data_fim"] < hoje)
        & (df["status"] != "Concluído")
    )

    df["dias_atraso"] = df.apply(
        lambda linha: (
            max(0, (hoje - linha["data_fim"].to_pydatetime()).days)
            if linha["atrasada"]
            else 0
        ),
        axis=1,
    )

    return df


# ============================================================
# MENU DE NAVEGAÇÃO
# ============================================================

def menu_navegacao():
    """Menu lateral com botões fixos e destaque da página ativa."""

    opcoes = [
        ("🏠 Principal", "Principal", "nav_principal"),
        ("📋 Atividades", "Atividades", "nav_atividades"),
        ("👥 Membros", "Membros", "nav_membros"),
        ("📁 Meus Projetos", "Meus Projetos", "nav_projetos"),
        ("🤖 Chat IA", "🤖 Chat IA", "nav_chat_ia"),
    ]

    if "pagina_atual" not in st.session_state:
        st.session_state.pagina_atual = "Principal"

    chave_ativa = next(
        (
            chave
            for _, pagina, chave in opcoes
            if pagina == st.session_state.pagina_atual
        ),
        "nav_principal",
    )

    st.markdown(
        f"""
        <style>
        section[data-testid="stSidebar"] div[class*="st-key-nav_"] button {{
            background-color: #e32636 !important;
            color: white !important;
            border: 1px solid #e32636 !important;
            border-radius: 8px !important;
            width: 100%;
            min-height: 45px;
            font-weight: 600;
            transition: background-color 0.2s ease;
        }}

        section[data-testid="stSidebar"] div[class*="st-key-nav_"] button:hover {{
            background-color: #b71c2c !important;
            border-color: #b71c2c !important;
            color: white !important;
        }}

        section[data-testid="stSidebar"] div.st-key-{chave_ativa} button {{
            background-color: #242424 !important;
            border-color: #555555 !important;
            color: white !important;
        }}

        section[data-testid="stSidebar"] div.st-key-{chave_ativa} button:hover {{
            background-color: #383838 !important;
            border-color: #666666 !important;
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📋 Navegação")

    for rotulo, pagina, chave in opcoes:
        if st.button(
            rotulo,
            key=chave,
            use_container_width=True,
        ):
            if st.session_state.pagina_atual != pagina:
                st.session_state.pagina_atual = pagina
                st.rerun()

    return st.session_state.pagina_atual


# ============================================================
# PÁGINA DE ATIVIDADES
# ============================================================

def pagina_atividades(df):
    st.title("📋 Atividades")

    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filtrar por Status",
            ["Todos"] + list(df["status"].unique()),
        )

    with col2:
        responsavel_filter = st.selectbox(
            "Filtrar por Responsável",
            ["Todos"] + list(df["responsavel"].unique()),
        )

    with col3:
        prioridade_filter = st.selectbox(
            "Filtrar por Prioridade",
            ["Todos"] + list(df["prioridade"].unique()),
        )

    df_filtrado = df.copy()

    if status_filter != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["status"] == status_filter
        ]

    if responsavel_filter != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["responsavel"] == responsavel_filter
        ]

    if prioridade_filter != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["prioridade"] == prioridade_filter
        ]

    st.caption(f"{len(df_filtrado)} atividade(s) encontrada(s).")

    for _, atividade in df_filtrado.iterrows():
        with st.expander(
            f"{atividade['nome']} — {atividade['status']}"
        ):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Descrição:** {atividade['descricao']}")
                st.write(f"**Responsável:** {atividade['responsavel']}")
                st.write(f"**Prioridade:** {atividade['prioridade']}")

                st.progress(
                    int(atividade["percentual_completo"]),
                    text=f"Progresso: {atividade['percentual_completo']}%",
                )

            with col2:
                if atividade["atrasada"]:
                    st.error(
                        f"Atrasada: {atividade['dias_atraso']} dias"
                    )
                else:
                    st.success("No prazo")

                st.write(
                    "**Início:** "
                    f"{atividade['data_inicio'].strftime('%d/%m/%Y')}"
                )
                st.write(
                    "**Fim:** "
                    f"{atividade['data_fim'].strftime('%d/%m/%Y')}"
                )


# ============================================================
# PÁGINA DE MEMBROS
# ============================================================

def pagina_membros(df):
    st.title("👥 Membros da Equipe")

    membros_stats = df.groupby("responsavel").agg(
        total_tarefas=("id", "count"),
        progresso_medio=("percentual_completo", "mean"),
        tarefas_atrasadas=("atrasada", "sum"),
    ).round(1)

    membros_stats["tarefas_concluidas"] = (
        df[df["status"] == "Concluído"]
        .groupby("responsavel")
        .size()
        .reindex(membros_stats.index, fill_value=0)
    )

    membros_stats["taxa_conclusao"] = (
        membros_stats["tarefas_concluidas"]
        / membros_stats["total_tarefas"]
        * 100
    ).round(1)

    membros_stats = membros_stats.rename(
        columns={
            "total_tarefas": "Total Tarefas",
            "progresso_medio": "Progresso Médio (%)",
            "tarefas_atrasadas": "Tarefas Atrasadas",
            "tarefas_concluidas": "Tarefas Concluídas",
            "taxa_conclusao": "Taxa Conclusão (%)",
        }
    )

    st.dataframe(
        membros_stats,
        use_container_width=True,
    )

    fig_membros = px.bar(
        x=membros_stats.index,
        y=membros_stats["Taxa Conclusão (%)"],
        title="Taxa de Conclusão por Membro",
        labels={
            "x": "Membro",
            "y": "Taxa de Conclusão (%)",
        },
    )

    st.plotly_chart(fig_membros, use_container_width=True)


# ============================================================
# PÁGINA DE PROJETOS
# ============================================================

def pagina_projeto_migracao(projeto, df):
    st.title(f"🔄 {projeto}")

    if "Minas Gerais" in projeto:
        tarefas_nomes = [
            "Migração Database Principal",
            "Configurar Azure AD",
            "Migrar APIs REST",
        ]
        descricao = (
            "Migração da infraestrutura de TI de Minas Gerais "
            "para a nuvem Azure."
        )
        progresso = 65

    elif "Mato Grosso" in projeto:
        tarefas_nomes = [
            "Testar Integração SAP",
            "Documentar Processos",
            "Treinar Equipe Técnica",
        ]
        descricao = (
            "Migração e modernização dos sistemas "
            "do escritório de Mato Grosso."
        )
        progresso = 45

    else:
        tarefas_nomes = [
            "Backup Sistemas Legados",
            "Validar Segurança",
            "Migrar Storage Files",
        ]
        descricao = (
            "Implementação de nova infraestrutura "
            "no escritório de Sergipe."
        )
        progresso = 30

    st.info(descricao)

    tarefas_projeto = df[df["nome"].isin(tarefas_nomes)]

    col1, col2, col3 = st.columns(3)

    col1.metric("Progresso Geral", f"{progresso}%")
    col2.metric("Total de Tarefas", len(tarefas_projeto))

    concluidas = (
        tarefas_projeto["status"] == "Concluído"
    ).sum()

    col3.metric("Tarefas Concluídas", int(concluidas))

    st.progress(progresso / 100)

    st.subheader("Tarefas do Projeto")

    st.dataframe(
        tarefas_projeto[
            [
                "nome",
                "responsavel",
                "status",
                "prioridade",
                "data_fim",
                "percentual_completo",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "percentual_completo": st.column_config.ProgressColumn(
                "Progresso",
                min_value=0,
                max_value=100,
            ),
            "data_fim": st.column_config.DateColumn(
                "Data Fim",
                format="DD/MM/YYYY",
            ),
        },
    )


# ============================================================
# ALERTAS
# ============================================================

def mostrar_alertas(df):
    st.subheader("🚨 Alertas do Dia")

    atrasadas = df[df["atrasada"]]

    if atrasadas.empty:
        st.success("Nenhuma tarefa atrasada.")
    else:
        st.warning(
            f"Existem {len(atrasadas)} tarefa(s) atrasada(s)."
        )

        for _, tarefa in atrasadas.head(5).iterrows():
            st.write(
                f"• **{tarefa['nome']}** — "
                f"{tarefa['dias_atraso']} dia(s) de atraso."
            )


# ============================================================
# DASHBOARD PRINCIPAL
# ============================================================

def dashboard_principal(df, ai):
    st.title("🌅 AURORA")
    st.markdown("---")

    st.header("📈 Indicadores Principais")

    total_tarefas = len(df)
    concluidas = (df["status"] == "Concluído").sum()
    em_progresso = (df["status"] == "Em Progresso").sum()
    atrasadas = df["atrasada"].sum()
    nao_iniciadas = (df["status"] == "Não Iniciado").sum()

    percentual_conclusao = (
        concluidas / total_tarefas * 100
        if total_tarefas
        else 0
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total de Tarefas", total_tarefas)
    col2.metric(
        "Concluídas",
        int(concluidas),
        f"{percentual_conclusao:.1f}%",
    )
    col3.metric("Em Progresso", int(em_progresso))
    col4.metric(
        "Atrasadas",
        int(atrasadas),
        delta_color="inverse",
    )
    col5.metric("Não Iniciadas", int(nao_iniciadas))

    st.markdown("---")

    if ai:
        st.header("🤖 Resumo Executivo com IA")

        if st.button("🔄 Gerar Análise Executiva"):
            with st.spinner("Analisando os dados..."):
                try:
                    resumo = ai.gerar_resumo_executivo(df)
                    st.session_state["ultima_analise"] = {
                        "timestamp": datetime.now(),
                        "resumo": resumo,
                    }
                except Exception as e:
                    st.error(f"Erro ao gerar análise: {e}")

        if "ultima_analise" in st.session_state:
            analise = st.session_state["ultima_analise"]

            st.info(analise["resumo"])

            st.caption(
                "Última análise: "
                f"{analise['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}"
            )

    st.markdown("---")

    st.header("📊 Visualizações")

    col1, col2 = st.columns(2)

    with col1:
        fig_status = px.pie(
            df,
            names="status",
            title="Distribuição por Status",
            color="status",
            color_discrete_map={
                "Concluído": "#00CC88",
                "Em Progresso": "#36A2EB",
                "Atrasado": "#FF6384",
                "Não Iniciado": "#FFCE56",
            },
        )

        st.plotly_chart(
            fig_status,
            use_container_width=True,
        )

    with col2:
        contagem_responsavel = (
            df.groupby(["responsavel", "status"])
            .size()
            .reset_index(name="quantidade")
        )

        fig_responsaveis = px.bar(
            contagem_responsavel,
            x="responsavel",
            y="quantidade",
            color="status",
            title="Tarefas por Responsável",
            color_discrete_map={
                "Concluído": "#00CC88",
                "Em Progresso": "#36A2EB",
                "Atrasado": "#FF6384",
                "Não Iniciado": "#FFCE56",
            },
        )

        st.plotly_chart(
            fig_responsaveis,
            use_container_width=True,
        )

    st.header("📅 Timeline do Projeto")

    fig_gantt = px.timeline(
        df,
        x_start="data_inicio",
        x_end="data_fim",
        y="nome",
        color="responsavel",
        title="Cronograma de Tarefas",
        hover_data=[
            "status",
            "percentual_completo",
        ],
    )

    fig_gantt.update_yaxes(
        categoryorder="total ascending",
    )

    st.plotly_chart(
        fig_gantt,
        use_container_width=True,
    )

    st.markdown("---")

    mostrar_alertas(df)


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def main():
    """Coordena os dados, a navegação e as páginas da AURORA."""

    df = carregar_dados_exemplo()
    ai = init_ai()

    with st.sidebar:
        st.title("🌅 AURORA")
        st.caption("Gestão Inteligente de Projetos")

        st.markdown("---")

        menu_opcao = menu_navegacao()

        st.markdown("---")

        projeto_selecionado = None

        if menu_opcao == "Meus Projetos":
            st.subheader("📁 Selecionar Projeto")

            projetos = [
                "Migração Minas Gerais",
                "Migração Mato Grosso",
                "Migração Sergipe",
            ]

            projeto_selecionado = st.radio(
                "Projetos disponíveis",
                projetos,
                key="projeto_selecionado",
            )

        if menu_opcao in ["Principal", "Atividades"]:
            st.markdown("---")
            st.subheader("🔎 Filtros Gerais")

            responsaveis = ["Todos"] + sorted(
                df["responsavel"].unique().tolist()
            )

            responsavel_filtro = st.selectbox(
                "Responsável",
                responsaveis,
                key="filtro_responsavel_global",
            )

            if responsavel_filtro != "Todos":
                df = df[
                    df["responsavel"] == responsavel_filtro
                ]

    # ========================================================
    # EXIBIÇÃO DAS PÁGINAS
    # ========================================================

    if menu_opcao == "Principal":
        dashboard_principal(df, ai)

    elif menu_opcao == "Atividades":
        pagina_atividades(df)

    elif menu_opcao == "Membros":
        pagina_membros(df)

    elif menu_opcao == "Meus Projetos":
        if projeto_selecionado:
            pagina_projeto_migracao(
                projeto_selecionado,
                df,
            )

    elif menu_opcao == "🤖 Chat IA":
        st.title("🤖 Chat IA")

        if pagina_chat_ia is not None:
            try:
                pagina_chat_ia(df, ai)
            except Exception as e:
                st.error(f"Erro ao abrir o Chat IA: {e}")
        else:
            st.error(
                "O módulo de Chat IA não está disponível."
            )
            st.info(
                "Verifique se chat_aurora.py está no mesmo diretório "
                "que main.py."
            )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()
