# chat_aurora.py - Chat com Llama no Streamlit
import streamlit as st
import pandas as pd

def pagina_chat_ia(df, ai):
    """Página de chat com a IA Aurora"""
    st.title("🤖 Chat com AURORA IA")
    st.markdown("Faça perguntas sobre as atividades e projetos!")
    
    # Verificar se IA está disponível
    if not ai:
        st.error("❌ IA não está disponível. Verifique se o Ollama está rodando.")
        st.info("Execute em outro terminal: `ollama serve`")
        return
    
    # Informações sobre os dados disponíveis
    with st.expander("📊 Dados Disponíveis para Consulta"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Atividades", len(df))
            
        with col2:
            responsaveis = df['responsavel'].nunique()
            st.metric("Responsáveis", responsaveis)
            
        with col3:
            tipos_atividade = len(df['nome'].unique())
            st.metric("Tipos de Atividade", tipos_atividade)
        
        st.write("**Responsáveis disponíveis:**", ", ".join(df['responsavel'].unique()))
        st.write("**Status disponíveis:**", ", ".join(df['status'].unique()))
        st.write("**Prioridades:**", ", ".join(df['prioridade'].unique()))
    
    # Inicializar histórico do chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Área do chat
    st.markdown("### 💬 Conversa")
    
    # Container para o chat
    chat_container = st.container()
    
    with chat_container:
        # Mostrar histórico
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
    
    # Input para nova pergunta
    pergunta = st.chat_input("Digite sua pergunta sobre as atividades...")
    
    if pergunta:
        # Adicionar pergunta do usuário ao histórico
        st.session_state.chat_history.append({
            "role": "user", 
            "content": pergunta
        })
        
        # Processar resposta da IA
        with st.spinner("🤔 Pensando..."):
            resposta = ai.responder_pergunta(pergunta, df)
        
        # Adicionar resposta ao histórico
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": resposta
        })
        
        # Rerun para atualizar o chat
        st.rerun()
    
    # Botões de ação
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Limpar Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("💡 Exemplos de Perguntas"):
            with st.expander("💡 Sugestões de Perguntas", expanded=True):
                st.markdown("""
                **Exemplos de perguntas que você pode fazer:**
                
                • Quais são os 3 usuários com mais demandas de prioridade alta?
                • Quantas atividades estão atrasadas?
                • Qual responsável tem mais tarefas concluídas?
                • Me liste as atividades em progresso
                • Quem tem a melhor taxa de conclusão?
                • Quais atividades têm prioridade alta?
                • Mostre o status geral do projeto
                • Qual é o percentual de conclusão por pessoa?
                """)
    
    # Sidebar com estatísticas rápidas
    with st.sidebar:
        st.markdown("### 📈 Estatísticas Rápidas")
        
        # Atividades por prioridade
        prioridade_counts = df['prioridade'].value_counts()
        st.write("**Por Prioridade:**")
        for prioridade, count in prioridade_counts.items():
            emoji = {"Alta": "🔴", "Média": "🟡", "Baixa": "🟢"}.get(prioridade, "⚪")
            st.write(f"{emoji} {prioridade}: {count}")
        
        # Atividades por responsável
        st.write("**Por Responsável:**")
        responsavel_counts = df['responsavel'].value_counts()
        for responsavel, count in responsavel_counts.head(5).items():
            st.write(f"👤 {responsavel}: {count}")
        
        # Tarefas atrasadas
        if 'atrasada' in df.columns:
            atrasadas = len(df[df['atrasada'] == True])
            if atrasadas > 0:
                st.error(f"⚠️ {atrasadas} atividades atrasadas")
            else:
                st.success("✅ Nenhuma atividade atrasada")
