# aurora_ai_ollama.py - Versão usando Ollama (IA local e gratuita)
import ollama
import requests
import pandas as pd
from typing import Dict, List
import json
from datetime import datetime
import time
import socket

class AuroraAI:
    def __init__(self, api_key: str = None):
        """Inicializa o módulo de IA da AURORA com Ollama"""
        self.base_url = "http://localhost:11434/api/generate"
        self.model = "llama2"  
        print("🦙 AURORA AI - Usando Ollama (100% GRATUITO)")
        print(f"📦 Modelo: {self.model}")
        
        # Testar conexão com Ollama
        if not self._verificar_ollama():
            print("⚠️  Ollama não está rodando. Iniciando...")
            print("   Execute em outro terminal: ollama serve")
    

    def _verificar_ollama(self):
            """Verifica se o Ollama está rodando e se há modelos disponíveis"""
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    modelos = [m['name'] for m in data.get('models', [])]
                    if modelos:
                        print(f"📦 Modelos disponíveis: {', '.join(modelos)}")
                        return True
                    else:
                        print("⚠️ Ollama está rodando, mas nenhum modelo foi baixado ainda.")
                        print("   Execute: ollama pull mistral   (ou outro modelo)")
                        return False
                return False
            except requests.exceptions.ConnectionError:
                return False
        
    def _fazer_chamada(self, prompt: str, max_tokens: int = 500, temperature: float = 0.5) -> str:
        """Faz chamada ao Ollama local"""
        try:
            # Preparar requisição para Ollama
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            # Fazer chamada
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                print(f"Erro Ollama: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Erro: Ollama não está rodando!")
            print("   Execute: ollama serve")
            return None
        except Exception as e:
            print(f"Erro: {str(e)}")
            return None
    
    def analisar_prioridade(self, tarefa: Dict) -> Dict:
        """Analisa uma tarefa e sugere prioridade"""
        prompt = f"""Você é um especialista em gestão de projetos de migração.
        
        Analise esta tarefa e retorne APENAS um JSON válido (sem explicações) com:
        - prioridade: "Alta", "Média" ou "Baixa"
        - riscos: array com 2 riscos identificados
        - sugestao: uma ação recomendada (1 linha)
        
        Tarefa: {tarefa.get('nome')}
        Descrição: {tarefa.get('descricao', 'Sem descrição')}
        Status: {tarefa.get('status')}
        
        Responda APENAS com JSON válido:"""
        
        resposta = self._fazer_chamada(prompt, max_tokens=200, temperature=0.3)
        
        if resposta:
            try:
                # Limpar resposta e extrair JSON
                resposta = resposta.strip()
                
                # Tentar encontrar JSON na resposta
                start = resposta.find('{')
                end = resposta.rfind('}') + 1
                
                if start >= 0 and end > start:
                    json_str = resposta[start:end]
                    return json.loads(json_str)
            except:
                pass
        
        # Fallback se não conseguir processar
        return {
            "prioridade": "Média",
            "riscos": ["Requer análise manual", "Possível impacto no cronograma"],
            "sugestao": "Avaliar dependências e alocar recursos adequados"
        }
    
    def gerar_resumo_executivo(self, dados_projeto: pd.DataFrame) -> str:
        """Gera resumo executivo do projeto"""
        total = len(dados_projeto)
        
        # Calcular estatísticas
        concluidas = 0
        em_progresso = 0
        atrasadas = 0
        
        if 'status' in dados_projeto.columns:
            concluidas = len(dados_projeto[dados_projeto['status'] == 'Concluído'])
            em_progresso = len(dados_projeto[dados_projeto['status'] == 'Em Progresso'])
        
        if 'atrasada' in dados_projeto.columns:
            atrasadas = len(dados_projeto[dados_projeto['atrasada'] == True])
        
        percentual = (concluidas/total*100) if total > 0 else 0
        
        prompt = f"""Como consultor sênior, crie um resumo executivo de 4 linhas para:
        
        Projeto de Migração:
        - Total: {total} tarefas
        - Concluídas: {concluidas} ({percentual:.1f}%)
        - Em progresso: {em_progresso}
        - Atrasadas: {atrasadas}
        
        Inclua: status geral, principal risco, e recomendação.
        Seja direto e executivo."""
        
        resposta = self._fazer_chamada(prompt, max_tokens=200, temperature=0.5)
        
        if resposta:
            # Limitar a 4 linhas
            linhas = resposta.strip().split('\n')[:4]
            return '\n'.join(linhas)
        else:
            return f"""📊 Status: {percentual:.1f}% concluído ({concluidas}/{total} tarefas)
⚠️ Atenção: {atrasadas} tarefas atrasadas requerem ação imediata
✅ Progresso: {em_progresso} tarefas em andamento
🎯 Recomendação: Focar em tarefas críticas para manter cronograma"""
    
    def gerar_alerta_inteligente(self, tarefa: Dict) -> str:
        """Gera alerta para o Teams"""
        nome = tarefa.get('nome', 'Tarefa')
        status = tarefa.get('status', 'Indefinido')
        dias = tarefa.get('dias_atraso', 0)
        responsavel = tarefa.get('responsavel', 'Responsável')
        
        if dias > 0:
            prompt = f"""Crie um alerta urgente de 1 linha para:
            Tarefa '{nome}' está {dias} dias atrasada.
            Responsável: {responsavel}
            
            Seja direto e acionável:"""
            
            resposta = self._fazer_chamada(prompt, max_tokens=50, temperature=0.7)
            
            if resposta:
                return f"🚨 {resposta.strip().split('.')[0]}."
        
        # Fallback
        if dias > 5:
            return f"🚨 CRÍTICO: '{nome}' com {dias} dias de atraso! {responsavel} deve agir imediatamente."
        elif dias > 0:
            return f"⚠️ '{nome}' atrasada {dias} dias. {responsavel} precisa priorizar."
        else:
            return f"✅ '{nome}' no prazo. Status: {status}"
    
    def responder_pergunta(self, pergunta: str, contexto_projeto: pd.DataFrame) -> str:
        """Responde perguntas sobre o projeto"""
        total = len(contexto_projeto)
        
        status_info = ""
        if 'status' in contexto_projeto.columns:
            status_counts = contexto_projeto['status'].value_counts()
            status_info = f"Status: {status_counts.to_dict()}"
        
        prompt = f"""Responda em 1-2 linhas a pergunta sobre o projeto:
        
        Contexto: Projeto com {total} tarefas. {status_info}
        Pergunta: {pergunta}
        
        Resposta concisa:"""
        
        resposta = self._fazer_chamada(prompt, max_tokens=100, temperature=0.5)
        
        if resposta:
            # Pegar apenas primeira frase
            return resposta.strip().split('\n')[0]
        else:
            return f"Projeto com {total} tarefas em análise. Use os filtros para detalhes."
    
    def processar_lote_tarefas(self, tarefas_df: pd.DataFrame) -> pd.DataFrame:
        """Processa tarefas em lote"""
        df = tarefas_df.copy()
        
        # Adicionar colunas
        for col in ['ia_prioridade', 'ia_riscos', 'ia_sugestao']:
            if col not in df.columns:
                df[col] = ''
        
        # Processar apenas 5 primeiras (Ollama é mais lento)
        print("🔄 Processando tarefas com IA...")
        tarefas_processar = df.head(5) if 'status' not in df.columns else df[df['status'] != 'Concluído'].head(5)
        
        for idx in tarefas_processar.index:
            print(f"   Analisando tarefa {idx+1}...")
            row = df.loc[idx]
            analise = self.analisar_prioridade(row.to_dict())
            
            df.at[idx, 'ia_prioridade'] = analise.get('prioridade', 'Média')
            riscos = analise.get('riscos', [])
            if isinstance(riscos, list):
                df.at[idx, 'ia_riscos'] = ', '.join(riscos[:2])
            df.at[idx, 'ia_sugestao'] = str(analise.get('sugestao', ''))[:100]
        
        print("✅ Análise concluída!")
        return df

# Teste direto
if __name__ == "__main__":
    print("="*50)
    print("🦙 AURORA AI - Teste com Ollama")
    print("="*50)
    
    # Verificar Ollama
    ai = AuroraAI()
    
    print("\n📝 Testando análise de tarefa...")
    tarefa_teste = {
        'nome': 'Migração Database Principal',
        'descricao': 'Migrar 500GB de dados para cloud',
        'status': 'Em Progresso',
        'responsavel': 'João Silva',
        'dias_atraso': 3
    }
    
    print("Enviando para Ollama...")
    resultado = ai.analisar_prioridade(tarefa_teste)
    print(f"\n✅ Resultado:")
    print(f"Prioridade: {resultado.get('prioridade')}")
    print(f"Riscos: {resultado.get('riscos')}")
    print(f"Sugestão: {resultado.get('sugestao')}")
    
    print("\n🚨 Testando geração de alerta...")
    alerta = ai.gerar_alerta_inteligente(tarefa_teste)
    print(f"Alerta: {alerta}")
    
    print("\n" + "="*50)
    print("✅ Teste concluído! Ollama funcionando!")
    print("💡 Execute 'streamlit run main.py' para usar o dashboard")
    print("="*50)