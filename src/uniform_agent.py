from __future__ import annotations

import base64
import os
from dataclasses import dataclass


@dataclass
class UniformBriefing:
    segmento: str
    objetivo_visual: str
    publico_uso: str
    restricoes: str
    cor_nome: str
    cor_hex: str
    logo_proporcao: str
    tamanho_mockup: str
    modelo_peca: str
    metodo_aplicacao: str


def build_prompt(briefing: UniformBriefing) -> str:
    return f"""
Pedido de criação de mockup de uniforme:
- Segmento: {briefing.segmento or 'Não informado'}
- Objetivo visual: {briefing.objetivo_visual or 'Não informado'}
- Público de uso: {briefing.publico_uso or 'Não informado'}
- Restrições: {briefing.restricoes or 'Não informado'}
- Cor da camiseta selecionada: {briefing.cor_nome or 'Não informado'}
- Código HEX extraído: {briefing.cor_hex or 'Não informado'}
- Proporção da impressão da logo: {briefing.logo_proporcao or 'Não informado'}
- Tamanho do mockup: {briefing.tamanho_mockup or 'TBU'}
- Modelo da peça: {briefing.modelo_peca or 'Não informado'}
- Método de aplicação: {briefing.metodo_aplicacao or 'Não informado'}

Instruções obrigatórias:
1) Gere mockup profissional seguindo padrões de confecção.
2) Mantenha coerência técnica de posicionamento e proporção.
3) Produza resposta em 5 blocos: resumo, proposta visual, especificação técnica, decisões automáticas e próximo passo.
4) Considere que o usuário poderá informar o tamanho real após aprovação do mockup.
""".strip()


def encode_logo_as_data_url(logo_path: str) -> str:
    ext = os.path.splitext(logo_path)[1].lower()
    mime_type = "image/png"
    if ext in [".jpg", ".jpeg"]:
        mime_type = "image/jpeg"
    elif ext == ".svg":
        mime_type = "image/svg+xml"

    with open(logo_path, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{b64_data}"


def is_quota_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "insufficient_quota" in message or "exceeded your current quota" in message or "429" in message


def generate_local_mock_response(briefing: UniformBriefing) -> str:
    return f"""A) Resumo do pedido interpretado
- Segmento: {briefing.segmento or 'Não informado'}
- Objetivo visual: {briefing.objetivo_visual or 'Não informado'}
- Público de uso: {briefing.publico_uso or 'Não informado'}
- Restrições detectadas: {briefing.restricoes or 'Não informado'}

B) Proposta de design (mockup em {briefing.tamanho_mockup or 'TBU'})
- Base da camisa: {briefing.modelo_peca or 'Camisa padrão'}
- Paleta (HEX): {briefing.cor_hex or 'Não informado'}
- Frente: logo centralizada no peito esquerdo com escala proporcional {briefing.logo_proporcao or 'padrão de 10x8 cm'}
- Costas: área reservada para identificação e numeração opcional
- Mangas: aplicação de faixa técnica com continuidade visual
- Gola e punhos: acabamento compatível com {briefing.modelo_peca or 'modelo selecionado'}
- Aplicações (logo/nome/número/patrocínio): método {briefing.metodo_aplicacao or 'não informado'}

C) Especificação técnica
- Tamanho aplicado no mockup: {briefing.tamanho_mockup or 'TBU'}
- Método sugerido: {briefing.metodo_aplicacao or 'Silk'}
- Áreas de impressão: frente, costas e manga conforme briefing
- Distância mínima de segurança: 1,5 cm das costuras principais
- Observações de produção: validar prova de cor com o HEX selecionado

D) Decisões automáticas assumidas
- Grade visual regular e alinhamento técnico das aplicações
- Legibilidade priorizada para uso profissional
- Proporção da logo respeitada conforme campo informado

E) Próximo passo
- Informe tamanho real (único ou grade)
- Quantidade por tamanho
- Tipo de tecido
- Prazo"""
