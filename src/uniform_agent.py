from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


@dataclass
class UniformBriefing:
    segmento: str
    cores: str
    detalhes: str
    cor_hex: str
    logo_proporcao: str
    tamanho_mockup: str
    modelagem: str
    tecnica_impressao: str


def build_prompt(briefing: UniformBriefing) -> str:
    return f"""
Crie um mockup técnico profissional de uniforme com base no briefing abaixo.

- Segmento: {briefing.segmento or 'Não informado'}
- Cores principais: {briefing.cores or 'Não informado'}
- Detalhes: {briefing.detalhes or 'Não informado'}
- Cor HEX confirmada: {briefing.cor_hex or 'Não informado'}
- Proporção da logo: {briefing.logo_proporcao or 'Não informado'}
- Tamanho do mockup: {briefing.tamanho_mockup or 'TBU'}
- Modelagem: {briefing.modelagem or 'Regular'}
- Técnica de impressão: {briefing.tecnica_impressao or 'Sublimação'}

Formato de resposta obrigatório:
A) Resumo do pedido interpretado
B) Proposta de design (mockup em TBU)
C) Especificação técnica
D) Decisões automáticas assumidas
E) Próximo passo (solicitar tamanho real e grade)
""".strip()


def encode_logo_inline_part(logo_path: str) -> dict[str, Any]:
    ext = os.path.splitext(logo_path)[1].lower()
    mime_type = "image/png"
    if ext in [".jpg", ".jpeg"]:
        mime_type = "image/jpeg"
    elif ext == ".svg":
        mime_type = "image/svg+xml"

    with open(logo_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    return {"inline_data": {"mime_type": mime_type, "data": data}}


def _http_json(url: str, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url=url, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Falha de conexão: {exc}") from exc


def list_gemini_models(api_key: str) -> list[str]:
    url = f"{GEMINI_API_BASE}/models?key={urllib.parse.quote(api_key)}"
    data = _http_json(url)
    models = []
    for model in data.get("models", []):
        name = model.get("name", "")
        methods = model.get("supportedGenerationMethods", [])
        if "generateContent" in methods and name.startswith("models/"):
            models.append(name.replace("models/", ""))
    return sorted(set(models))


def validate_gemini_key(api_key: str) -> tuple[bool, str, list[str]]:
    if not api_key.strip():
        return False, "API key vazia.", []

    if not api_key.startswith("AIza"):
        return False, "Formato inválido para chave Gemini (esperado prefixo AIza).", []

    try:
        models = list_gemini_models(api_key)
    except Exception as exc:
        return False, f"Chave recusada: {exc}", []

    if not models:
        return False, "Chave válida, mas sem modelos disponíveis para generateContent.", []

    return True, "Chave Gemini válida e ativa.", models


def generate_with_gemini(api_key: str, model: str, prompt: str, logo_path: str | None = None) -> str:
    url = f"{GEMINI_API_BASE}/models/{urllib.parse.quote(model)}:generateContent?key={urllib.parse.quote(api_key)}"

    parts: list[dict[str, Any]] = [{"text": prompt}]
    if logo_path:
        parts.append(encode_logo_inline_part(logo_path))

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.5,
            "topK": 32,
            "topP": 0.95,
            "maxOutputTokens": 2048,
        },
    }

    data = _http_json(url, method="POST", payload=payload)

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"Resposta sem candidatos: {data}")

    candidate = candidates[0]
    content = candidate.get("content", {})
    parts_out = content.get("parts", [])
    texts = [p.get("text", "") for p in parts_out if "text" in p]
    text = "\n".join(t for t in texts if t.strip())
    if not text:
        raise RuntimeError("Gemini respondeu sem texto utilizável.")
    return text


def generate_local_mock_response(briefing: UniformBriefing) -> str:
    return f"""A) Resumo do pedido interpretado
- Segmento: {briefing.segmento or 'Não informado'}
- Objetivo visual: Uniforme profissional para {briefing.segmento or 'uso geral'}
- Público de uso: Operacional/técnico
- Restrições detectadas: {briefing.detalhes or 'Não informado'}

B) Proposta de design (mockup em {briefing.tamanho_mockup or 'TBU'})
- Paleta (HEX): {briefing.cor_hex or 'Não informado'}
- Modelagem: {briefing.modelagem or 'Regular'}
- Técnica de impressão: {briefing.tecnica_impressao or 'Sublimação'}

C) Especificação técnica
- Tamanho: {briefing.tamanho_mockup or 'TBU'}
- Peito: 56 cm
- Comprimento: 72 cm
- Método: {briefing.tecnica_impressao or 'Sublimação'}

D) Decisões automáticas assumidas
- Priorizada legibilidade e contraste
- Posicionamento padrão de logo em peito esquerdo

E) Próximo passo
- Informe tamanho real e quantidades por grade"""
