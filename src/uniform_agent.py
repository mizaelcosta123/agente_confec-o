from __future__ import annotations

import base64
import json
import os
import time
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
    tamanho_camiseta: str
    modelo_camiseta: str
    aplicacao_lado: str
    modelagem: str
    tecnica_impressao: str


def build_creation_prompt(briefing: UniformBriefing) -> str:
    return f"""
Você é um designer especialista em confecção de uniformes.
Crie um layout visual profissional de uniforme com realismo de produto e padrão de produção industrial.

INFORMAÇÕES DO PEDIDO:
- Segmento: {briefing.segmento or 'Não informado'}
- Cores principais: {briefing.cores or 'Não informado'}
- Detalhes: {briefing.detalhes or 'Não informado'}
- Cor HEX confirmada: {briefing.cor_hex or 'Não informado'}
- Proporção da logo: {briefing.logo_proporcao or 'Não informado'}
- Tamanho do mockup técnico: {briefing.tamanho_mockup or 'TBU'}
- Tamanho da camiseta final: {briefing.tamanho_camiseta or 'M'}
- Modelo da camiseta: {briefing.modelo_camiseta or 'Polo'}
- Aplicação da arte: {briefing.aplicacao_lado or 'Frente'}
- Modelagem: {briefing.modelagem or 'Regular'}
- Técnica de impressão: {briefing.tecnica_impressao or 'Sublimação'}

REGRAS CRÍTICAS (OBRIGATÓRIO):
1) NUNCA alterar a logo anexada: não redesenhar, não simplificar, não distorcer, não trocar cores, não remover elementos.
2) Usar a logo original exatamente como recebida, preservando 100% da identidade visual.
3) Respeitar rigorosamente os dados de briefing e as cores definidas.
4) Gerar visual profissional no estilo mockup de uniforme comercial (frente/verso conforme aplicação).
5) Não inventar marca diferente da logo anexada.

FORMATO DA SAÍDA:
- Entregar um resumo técnico curto do layout criado.
- Priorizar render com camisa realista e acabamento de confecção.
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
        with urllib.request.urlopen(req, timeout=60) as resp:
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

    parts_out = candidates[0].get("content", {}).get("parts", [])
    texts = [p.get("text", "") for p in parts_out if "text" in p]
    text = "\n".join(t for t in texts if t.strip())
    if not text:
        raise RuntimeError("Gemini respondeu sem texto utilizável.")
    return text


def generate_layout_image_with_gemini(
    api_key: str,
    model: str,
    prompt: str,
    logo_path: str,
    output_dir: str = "generated",
) -> tuple[str | None, str]:
    """Retorna (caminho_imagem_ou_none, texto_resumo)."""
    url = f"{GEMINI_API_BASE}/models/{urllib.parse.quote(model)}:generateContent?key={urllib.parse.quote(api_key)}"

    payload = {
        "contents": [{"parts": [{"text": prompt}, encode_logo_inline_part(logo_path)]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.4,
            "maxOutputTokens": 800,
        },
    }

    data = _http_json(url, method="POST", payload=payload)
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"Resposta sem candidatos para geração de layout: {data}")

    parts = candidates[0].get("content", {}).get("parts", [])

    text_chunks = []
    image_b64 = None
    image_mime = "image/png"

    for part in parts:
        if "text" in part:
            text_chunks.append(part.get("text", ""))

        inline_data = part.get("inlineData") or part.get("inline_data")
        if inline_data and inline_data.get("data"):
            image_b64 = inline_data.get("data")
            image_mime = inline_data.get("mimeType") or inline_data.get("mime_type") or "image/png"

    summary = "\n".join([t for t in text_chunks if t.strip()]).strip()

    if not image_b64:
        return None, summary or "Modelo não retornou imagem; apenas texto."

    os.makedirs(output_dir, exist_ok=True)
    ext = ".png"
    if "jpeg" in image_mime:
        ext = ".jpg"
    filename = f"layout_uniforme_{int(time.time())}{ext}"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, "wb") as f:
        f.write(base64.b64decode(image_b64))

    return output_path, (summary or "Layout gerado com sucesso.")


def generate_local_mock_response(briefing: UniformBriefing) -> str:
    return f"""A) Resumo do pedido interpretado
- Segmento: {briefing.segmento or 'Não informado'}
- Modelo da camiseta: {briefing.modelo_camiseta or 'Polo'}
- Aplicação: {briefing.aplicacao_lado or 'Frente'}

B) Proposta de design
- Paleta (HEX): {briefing.cor_hex or 'Não informado'}
- Tamanho mockup: {briefing.tamanho_mockup or 'TBU'}
- Tamanho final: {briefing.tamanho_camiseta or 'M'}
- Técnica: {briefing.tecnica_impressao or 'Sublimação'}

C) Regra da logo
- Logo original preservada sem alterações.

D) Observações
- Resultado local de contingência sem geração real de imagem.

E) Próximo passo
- Revisar prompt e executar com modelo Gemini com suporte a imagem."""
