# ============================================================
# AURORA - Chat com Inteligência Artificial
# Arquivo: chat_aurora.py
# Interface compatível com a classe AuroraAI
# ============================================================

import streamlit as st
import pandas as pd
from datetime import datetime


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def obter_coluna(df, coluna, valor_padrao="Não informado"):
    """
    Retorna uma coluna do DataFrame.
    Se a coluna não existir, retorna uma série com valores padrão.
    """
    if coluna in df.columns:
        return df[coluna]

    return pd.Series(
        [valor_padrao] * len(df),
        index=df.index
    )


def contar_valores(df, coluna):
    """
    Conta os valores de uma coluna, caso ela exista.
    """
    if coluna not in df.columns:
        return pd.Series(dtype="int64")

    return df[coluna].fillna("Não informado").value_counts()


def formatar_lista_unica(df, coluna):
    """
    Retorna os valores únicos de uma coluna em formato de texto.
    """
    if coluna not in df.columns:
        return "Informação indisponível"

    valores = (
        df[coluna]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if not valores:
        return "Nenhum registro encontrado"

    return ", ".join(valores)


def preparar_contexto(df):
    """
    Prepara um resumo dos dados do projeto para exibição.
    """
    total = len(df)

    status = contar_valores(df, "status")
    prioridades = contar_valores(df, "prioridade")
    responsaveis = contar_valores(df, "responsavel")

    return {
        "total": total,
        "status": status,
        "prioridades": prioridades,
        "responsaveis": responsaveis
    }


# ============================================================
# PÁGINA PRINCIPAL DO CHAT
# ============================================================

def pagina_chat_ia(df, ai):
    """
    Página de conversa com a IA da AURORA.

    Parâmetros:
        df: DataFrame contendo as atividades do projeto.
        ai: Instância da classe AuroraAI.
    """

    st.title("🤖 Chat com AURORA IA")

    st.markdown(
        """
        Converse com a inteligência artificial da AURORA para
        consultar atividades, analisar prioridades e entender
        melhor o andamento do seu projeto.
        """
    )

    # --------------------------------------------------------
    # VERIFICAÇÃO DOS DADOS
    # --------------------------------------------------------

    if df is None:
        st.error(
            "Não foi possível carregar os dados do projeto."
        )
        return

    if not isinstance(df, pd.DataFrame):
        st.error(
            "Os dados recebidos não estão no formato esperado."
        )
        return

    if df.empty:
        st.warning(
            "Ainda não existem atividades para consultar."
        )

    # --------------------------------------------------------
    # VERIFICAÇÃO DA INTELIGÊNCIA ARTIFICIAL
    # --------------------------------------------------------

    if ai is None:
        st.error(
            "A inteligência artificial não foi inicializada."
        )

        st.info(
            """
            **Como resolver:**

            1. Confira se o arquivo `aurora_ai.py` existe.
            2. Verifique se a classe `AuroraAI` está implementada.
            3. Confira se a configuração da API DeepSeek está correta.
            4. Verifique se a variável `DEEPSEEK_API_KEY` está
               configurada no arquivo `.env`.
            5. Consulte o terminal para identificar possíveis erros.
            """
        )

        return

    if not callable(getattr(ai, "responder_pergunta", None)):
        st.error(
            "A classe AuroraAI não possui o método "
            "`responder_pergunta()` esperado pelo chat."
        )
        return

    # --------------------------------------------------------
    # RESUMO DOS DADOS DISPONÍVEIS
    # --------------------------------------------------------

    with st.expander(
        "📊 Dados disponíveis para consulta",
        expanded=False
    ):

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total de atividades",
                len(df)
            )

        with col2:
            total_responsaveis = (
                df["responsavel"].nunique()
                if "responsavel" in df.columns
                else 0
            )

            st.metric(
                "Responsáveis",
                total_responsaveis
            )

        with col3:
            total_tipos = (
                df["nome"].nunique()
                if "nome" in df.columns
                else 0
            )

            st.metric(
                "Tipos de atividade",
                total_tipos
            )

        st.markdown("#### 👥 Responsáveis")

        st.write(
            formatar_lista_unica(df, "responsavel")
        )

        st.markdown("#### 📌 Status disponíveis")

        st.write(
            formatar_lista_unica(df, "status")
        )

        st.markdown("#### 🚦 Prioridades")

        st.write(
            formatar_lista_unica(df, "prioridade")
        )

    # --------------------------------------------------------
    # INICIALIZAÇÃO DO HISTÓRICO
    # --------------------------------------------------------

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "chat_aurora_ultima_pergunta" not in st.session_state:
        st.session_state.chat_aurora_ultima_pergunta = None

    # --------------------------------------------------------
    # ÁREA DA CONVERSA
    # --------------------------------------------------------

    st.markdown("---")
    st.subheader("💬 Conversa")

    st.caption(
        "Faça perguntas sobre as atividades, responsáveis, "
        "prioridades e andamento do projeto."
    )

    # Mensagem inicial quando não há histórico.
    if not st.session_state.chat_history:

        with st.chat_message("assistant"):

            st.markdown(
                """
                Olá! 👋 Sou a **AURORA IA**.

                Posso ajudar você a compreender os dados do projeto,
                identificar tarefas prioritárias e consultar o
                andamento das atividades.

                **O que você gostaria de saber?**
                """
            )

    # Exibição das mensagens anteriores.
    for mensagem in st.session_state.chat_history:

        papel = mensagem.get("role", "assistant")
        conteudo = mensagem.get("content", "")

        if papel not in ("user", "assistant"):
            continue

        with st.chat_message(papel):
            st.markdown(conteudo)

    # --------------------------------------------------------
    # CAMPO PARA ENVIAR PERGUNTAS
    # --------------------------------------------------------

    pergunta = st.chat_input(
        "Digite sua pergunta sobre o projeto..."
    )

    if pergunta:

        pergunta = pergunta.strip()

        if pergunta:

            # Salva a pergunta no histórico.
            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": pergunta
                }
            )

            # Exibe a pergunta imediatamente.
            with st.chat_message("user"):
                st.markdown(pergunta)

            # Consulta a inteligência artificial.
            with st.chat_message("assistant"):

                with st.spinner(
                    "🧠 A AURORA está analisando sua pergunta..."
                ):

                    try:

                        resposta = ai.responder_pergunta(
                            pergunta,
                            df
                        )

                        if resposta is None:
                            resposta = (
                                "Não consegui gerar uma resposta "
                                "neste momento. Tente novamente."
                            )

                        resposta = str(resposta).strip()

                        if not resposta:
                            resposta = (
                                "A IA não retornou uma resposta. "
                                "Tente reformular sua pergunta."
                            )

                    except Exception as erro:

                        resposta = (
                            "Não foi possível obter uma resposta "
                            "da inteligência artificial.\n\n"
                            "Verifique a conexão com a API DeepSeek, "
                            "a chave de acesso e os registros do "
                            "terminal para identificar o problema."
                        )

                        # Detalhes técnicos ficam no terminal,
                        # sem expor informações sensíveis na tela.
                        print(
                            "[AURORA] Erro ao consultar a IA:",
                            repr(erro)
                        )

                st.markdown(resposta)

            # Salva a resposta no histórico.
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": resposta
                }
            )

            # Atualiza a página para exibir a conversa completa.
            st.rerun()

    # --------------------------------------------------------
    # EXEMPLOS DE PERGUNTAS
    # --------------------------------------------------------

    st.markdown("---")

    with st.expander("💡 Exemplos de perguntas"):

        st.markdown(
            """
            Você pode perguntar coisas como:

            **📊 Sobre o projeto**
            - Quantas atividades existem no projeto?
            - Qual é o status geral das atividades?
            - Quantas atividades estão concluídas?

            **👥 Sobre os responsáveis**
            - Quem tem mais atividades atribuídas?
            - Quantas tarefas cada responsável possui?
            - Quem tem mais tarefas concluídas?

            **🚦 Sobre prioridades**
            - Quais atividades têm prioridade alta?
            - Quais tarefas precisam de atenção primeiro?
            - Quais atividades estão atrasadas?

            **📈 Sobre o andamento**
            - Liste as atividades em andamento.
            - Quais tarefas ainda estão pendentes?
            - Qual é o percentual de conclusão do projeto?

            **🧠 Para análise**
            - Quais tarefas merecem atenção imediata?
            - Quais são os principais riscos do projeto?
            - O que podemos fazer para melhorar o andamento?
            """
        )

    # --------------------------------------------------------
    # AÇÕES DO CHAT
    # --------------------------------------------------------

    st.markdown("---")

    col_limpar, col_exportar = st.columns(2)

    with col_limpar:

        if st.button(
            "🗑️ Limpar conversa",
            use_container_width=True
        ):

            st.session_state.chat_history = []

            st.rerun()

    with col_exportar:

        historico = st.session_state.chat_history

        texto_conversa = "\n\n".join(
            (
                "Você: "
                if mensagem["role"] == "user"
                else "AURORA IA: "
            ) + mensagem["content"]
            for mensagem in historico
        )

        st.download_button(
            label="📥 Exportar conversa",
            data=texto_conversa or "Nenhuma mensagem registrada.",
            file_name=(
                "conversa_aurora_"
                + datetime.now().strftime("%Y%m%d_%H%M%S")
                + ".txt"
            ),
            mime="text/plain",
            use_container_width=True
        )

    # ========================================================
    # BARRA LATERAL: ESTATÍSTICAS DO PROJETO
    # ========================================================

    with st.sidebar:

        st.markdown("---")
        st.header("📈 Estatísticas do projeto")

        # Total de atividades.
        st.metric(
            "Total de atividades",
            len(df)
        )

        # ----------------------------------------------------
        # DISTRIBUIÇÃO POR STATUS
        # ----------------------------------------------------

        st.markdown("#### 📌 Atividades por status")

        status_counts = contar_valores(df, "status")

        if status_counts.empty:

            st.caption(
                "Não há dados de status disponíveis."
            )

        else:

            for status, quantidade in status_counts.items():

                st.write(
                    f"• **{status}:** {quantidade}"
                )

        # ----------------------------------------------------
        # DISTRIBUIÇÃO POR PRIORIDADE
        # ----------------------------------------------------

        st.markdown("#### 🚦 Atividades por prioridade")

        prioridade_counts = contar_valores(
            df,
            "prioridade"
        )

        if prioridade_counts.empty:

            st.caption(
                "Não há dados de prioridade disponíveis."
            )

        else:

            emojis_prioridade = {
                "alta": "🔴",
                "média": "🟡",
                "media": "🟡",
                "baixa": "🟢",
                "urgente": "🚨"
            }

            for prioridade, quantidade in prioridade_counts.items():

                chave = str(prioridade).strip().lower()

                emoji = emojis_prioridade.get(
                    chave,
                    "⚪"
                )

                st.write(
                    f"{emoji} **{prioridade}:** {quantidade}"
                )

        # ----------------------------------------------------
        # DISTRIBUIÇÃO POR RESPONSÁVEL
        # ----------------------------------------------------

        st.markdown("#### 👥 Atividades por responsável")

        responsavel_counts = contar_valores(
            df,
            "responsavel"
        )

        if responsavel_counts.empty:

            st.caption(
                "Não há dados de responsáveis disponíveis."
            )

        else:

            for responsavel, quantidade in (
                responsavel_counts.head(5).items()
            ):

                st.write(
                    f"👤 **{responsavel}:** {quantidade}"
                )

            if len(responsavel_counts) > 5:

                st.caption(
                    "Exibindo os cinco responsáveis com mais atividades."
                )

        # ----------------------------------------------------
        # TAREFAS ATRASADAS
        # ----------------------------------------------------

        st.markdown("#### ⏰ Atividades atrasadas")

        if "atrasada" in df.columns:

            atrasadas = (
                df["atrasada"]
                .fillna(False)
                .astype(str)
                .str.strip()
                .str.lower()
                .isin(["true", "1", "sim", "yes"])
                .sum()
            )

            if atrasadas > 0:

                st.error(
                    f"⚠️ {atrasadas} atividade(s) atrasada(s)"
                )

            else:

                st.success(
                    "✅ Nenhuma atividade atrasada registrada."
                )

        else:

            st.caption(
                "O conjunto de dados não possui a coluna "
                "`atrasada`."
            )

        # ----------------------------------------------------
        # RODAPÉ
        # ----------------------------------------------------

        st.markdown("---")

        st.caption(
            "🤖 AURORA IA | Assistente inteligente do projeto"
        )