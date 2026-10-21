# aurora_ai.py
# AURORA AI - Integração com a API DeepSeek
#
# Dependências:
#   pip install openai python-dotenv pandas
#
# Arquivo .env (na raiz do projeto):
#   DEEPSEEK_API_KEY=sua_chave_real
#
# Não publique a chave no GitHub.

import json
import os
from typing import Dict, Any

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI


class AuroraAI:
    """Lógica de IA da AURORA usando a API DeepSeek."""

    def __init__(self, api_key: str = None):
        load_dotenv()

        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Chave da DeepSeek não encontrada. Configure "
                "DEEPSEEK_API_KEY no arquivo .env."
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
            timeout=45.0,
            max_retries=2,
        )
        # Modelo padrão da API DeepSeek. Se sua conta/documentação
        # indicar outro identificador disponível, altere esta variável.
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        print(f"🤖 AURORA AI - Usando API DeepSeek ({self.model})")

    def _fazer_chamada(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.5,
    ) -> str:
        """Envia um prompt para a DeepSeek e retorna o texto gerado."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é a AURORA, uma assistente de gestão de "
                            "projetos. Responda em português brasileiro, "
                            "com clareza, sem inventar dados que não estejam "
                            "no contexto fornecido."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
            )

            if not response.choices:
                print("[AURORA] A DeepSeek retornou uma resposta vazia.")
                return None

            conteudo = response.choices[0].message.content
            return conteudo.strip() if conteudo else None

        except Exception as erro:
            # Não exibe nem registra a chave de API.
            print(f"[AURORA] Erro na chamada à API DeepSeek: {erro}")
            return None

    @staticmethod
    def _valor(tarefa: Dict[str, Any], chave: str, padrao: str = "Não informado"):
        valor = tarefa.get(chave, padrao)
        if pd.isna(valor) if not isinstance(valor, (dict, list, tuple)) else False:
            return padrao
        return padrao if valor is None else valor

    def analisar_prioridade(self, tarefa: Dict) -> Dict:
        """Analisa uma tarefa e sugere prioridade, riscos e ação."""
        prompt = f"""
Analise a tarefa de gestão de projeto abaixo. Retorne APENAS um objeto
JSON válido, sem bloco Markdown, com estas chaves:
- "prioridade": "Alta", "Média" ou "Baixa"
- "riscos": lista com exatamente 2 riscos
- "sugestao": uma ação recomendada em uma frase

Tarefa: {self._valor(tarefa, 'nome')}
Descrição: {self._valor(tarefa, 'descricao', 'Sem descrição')}
Status: {self._valor(tarefa, 'status')}
Responsável: {self._valor(tarefa, 'responsavel')}
Dias de atraso: {self._valor(tarefa, 'dias_atraso', 0)}

Não invente informações que não foram fornecidas.
Responda somente com JSON válido.
"""
        resposta = self._fazer_chamada(
            prompt, max_tokens=250, temperature=0.3
        )

        if resposta:
            try:
                texto = resposta.strip()
                if texto.startswith("```"):
                    texto = texto.replace("```json", "").replace("```", "").strip()
                inicio = texto.find("{")
                fim = texto.rfind("}") + 1
                if inicio >= 0 and fim > inicio:
                    resultado = json.loads(texto[inicio:fim])
                    prioridade = resultado.get("prioridade", "Média")
                    if prioridade not in ("Alta", "Média", "Baixa"):
                        prioridade = "Média"
                    riscos = resultado.get("riscos", [])
                    if not isinstance(riscos, list):
                        riscos = [str(riscos)]
                    return {
                        "prioridade": prioridade,
                        "riscos": [str(risco) for risco in riscos[:2]],
                        "sugestao": str(
                            resultado.get(
                                "sugestao",
                                "Avaliar dependências e recursos necessários.",
                            )
                        ),
                    }
            except (json.JSONDecodeError, TypeError, ValueError) as erro:
                print(f"[AURORA] Não foi possível interpretar o JSON: {erro}")

        return {
            "prioridade": "Média",
            "riscos": [
                "Requer análise manual",
                "Possível impacto no cronograma",
            ],
            "sugestao": "Avaliar dependências e alocar recursos adequados.",
        }

    def gerar_resumo_executivo(self, dados_projeto: pd.DataFrame) -> str:
        """Gera um resumo executivo baseado nos dados do projeto."""
        if dados_projeto is None:
            dados_projeto = pd.DataFrame()

        total = len(dados_projeto)
        concluidas = 0
        em_progresso = 0
        atrasadas = 0

        if "status" in dados_projeto.columns:
            status = dados_projeto["status"].fillna("").astype(str).str.lower()
            concluidas = int(status.str.contains(r"conclu|finaliz", regex=True).sum())
            em_progresso = int(
                status.str.contains(r"progresso|andamento|em curso", regex=True).sum()
            )

        if "atrasada" in dados_projeto.columns:
            atrasada = (
                dados_projeto["atrasada"]
                .fillna(False)
                .astype(str)
                .str.strip()
                .str.lower()
                .isin(["true", "1", "sim", "yes"])
            )
            atrasadas = int(atrasada.sum())

        percentual = (concluidas / total * 100) if total else 0.0

        prompt = f"""
Crie um resumo executivo em até 4 linhas, em português, para o projeto:
- Total de atividades: {total}
- Concluídas: {concluidas} ({percentual:.1f}%)
- Em andamento: {em_progresso}
- Atrasadas: {atrasadas}

Inclua o status geral, o principal ponto de atenção e uma recomendação.
Use somente os números fornecidos.
"""
        resposta = self._fazer_chamada(prompt, max_tokens=220, temperature=0.4)

        if resposta:
            return "\n".join(resposta.strip().splitlines()[:4])

        return (
            f"📊 Status: {percentual:.1f}% concluído ({concluidas}/{total} atividades).\n"
            f"⚠️ Atenção: {atrasadas} atividade(s) marcada(s) como atrasada(s).\n"
            f"🔄 Em andamento: {em_progresso} atividade(s).\n"
            "🎯 Recomendação: revisar prioridades, bloqueios e prazos das atividades."
        )

    def gerar_alerta_inteligente(self, tarefa: Dict) -> str:
        """Gera um alerta curto para uma tarefa."""
        nome = self._valor(tarefa, "nome", "Tarefa")
        status = self._valor(tarefa, "status", "Indefinido")
        responsavel = self._valor(tarefa, "responsavel", "Responsável")

        try:
            dias = int(self._valor(tarefa, "dias_atraso", 0) or 0)
        except (TypeError, ValueError):
            dias = 0

        if dias > 0:
            prompt = f"""
Crie um alerta curto, direto e acionável em português.
Tarefa: {nome}
Dias de atraso: {dias}
Responsável: {responsavel}
Peça uma ação concreta, sem inventar detalhes.
"""
            resposta = self._fazer_chamada(prompt, max_tokens=80, temperature=0.5)
            if resposta:
                return f"🚨 {resposta.strip()}"

            if dias > 5:
                return (
                    f"🚨 CRÍTICO: '{nome}' está {dias} dias atrasada. "
                    f"{responsavel} deve avaliar e agir imediatamente."
                )
            return (
                f"⚠️ '{nome}' está {dias} dia(s) atrasada. "
                f"{responsavel} deve revisar a prioridade."
            )

        return f"✅ '{nome}' está sem atraso informado. Status: {status}."

    def responder_pergunta(
        self,
        pergunta: str,
        contexto_projeto: pd.DataFrame,
    ) -> str:
        """Responde perguntas sobre as atividades usando o contexto real do DataFrame."""
        if not isinstance(pergunta, str) or not pergunta.strip():
            return "Digite uma pergunta para que eu possa ajudar."

        if contexto_projeto is None:
            contexto_projeto = pd.DataFrame()

        total = len(contexto_projeto)
        resumo = {"total_atividades": total}

        # Incluir estatísticas resumidas, sem enviar o DataFrame inteiro.
        for coluna in ("status", "prioridade", "responsavel", "nome"):
            if coluna in contexto_projeto.columns:
                contagem = (
                    contexto_projeto[coluna]
                    .fillna("Não informado")
                    .astype(str)
                    .value_counts()
                    .to_dict()
                )
                resumo[f"contagem_{coluna}"] = contagem

        if "atrasada" in contexto_projeto.columns:
            atrasadas = (
                contexto_projeto["atrasada"]
                .fillna(False)
                .astype(str)
                .str.strip()
                .str.lower()
                .isin(["true", "1", "sim", "yes"])
                .sum()
            )
            resumo["atividades_atrasadas"] = int(atrasadas)

        # Adiciona algumas linhas para permitir perguntas sobre tarefas específicas.
        amostra = contexto_projeto.head(40)
        registros = amostra.where(pd.notna(amostra), None).to_dict(orient="records")

        prompt = f"""
Responda à pergunta do usuário em português brasileiro, com clareza e de
forma objetiva. Use os dados abaixo. Se a informação não estiver disponível,
diga isso explicitamente; não invente nomes, números ou status.

RESUMO ESTATÍSTICO:
{json.dumps(resumo, ensure_ascii=False, default=str)}

AMOSTRA DE ATÉ 40 ATIVIDADES:
{json.dumps(registros, ensure_ascii=False, default=str)}

PERGUNTA:
{pergunta}

Responda diretamente. Se a pergunta exigir cálculo, use os dados fornecidos
e deixe claro quando a amostra não for suficiente para uma conclusão completa.
"""
        resposta = self._fazer_chamada(
            prompt, max_tokens=350, temperature=0.3
        )

        if resposta:
            return resposta.strip()

        return (
            "Não consegui consultar a DeepSeek neste momento. Verifique a "
            "conexão com a internet, a variável DEEPSEEK_API_KEY no arquivo "
            ".env e os detalhes do erro exibidos no terminal."
        )

    def processar_lote_tarefas(self, tarefas_df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona sugestões da IA às primeiras 5 tarefas não concluídas."""
        if tarefas_df is None:
            return pd.DataFrame()

        df = tarefas_df.copy()

        for coluna in ("ia_prioridade", "ia_riscos", "ia_sugestao"):
            if coluna not in df.columns:
                df[coluna] = ""

        if "status" in df.columns:
            status = df["status"].fillna("").astype(str).str.lower()
            mascara = ~status.str.contains(r"conclu|finaliz", regex=True)
            tarefas_processar = df[mascara].head(5)
        else:
            tarefas_processar = df.head(5)

        print("🔄 Processando até 5 tarefas com a DeepSeek...")

        for idx, row in tarefas_processar.iterrows():
            analise = self.analisar_prioridade(row.to_dict())
            df.at[idx, "ia_prioridade"] = analise.get("prioridade", "Média")

            riscos = analise.get("riscos", [])
            if isinstance(riscos, list):
                df.at[idx, "ia_riscos"] = ", ".join(
                    str(risco) for risco in riscos[:2]
                )
            else:
                df.at[idx, "ia_riscos"] = str(riscos)

            df.at[idx, "ia_sugestao"] = str(
                analise.get("sugestao", "")
            )[:250]

        print("✅ Análise de tarefas concluída.")
        return df


if __name__ == "__main__":
    print("Testando a conexão da AURORA com a API DeepSeek...")
    try:
        ai = AuroraAI()
        teste = pd.DataFrame(
            [
                {
                    "nome": "Migração do banco de dados",
                    "descricao": "Migrar os dados para a nuvem",
                    "status": "Em Progresso",
                    "responsavel": "Equipe de TI",
                    "prioridade": "Alta",
                    "atrasada": False,
                }
            ]
        )
        print(ai.responder_pergunta("Resuma a atividade cadastrada.", teste))
    except Exception as erro:
        print(f"Falha no teste da AURORA: {erro}")
