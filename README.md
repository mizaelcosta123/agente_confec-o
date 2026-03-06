# Uniform Design Automation (Desktop • Gemini)

Aplicação desktop em Python/Tkinter com layout 3x3 estilo dashboard SaaS para automação de design de uniformes.

## O que foi implementado
- Login por **API Key Gemini** com validação real da chave (formato + consulta de modelos na API).
- Recusa de login para chave inválida/inativa.
- Dropdown dinâmico para escolher versão da IA (modelos Gemini disponíveis na chave).
- Painéis em grade 3x3 no estilo da referência visual.
- Campos de produção adicionados:
  - tamanho da camiseta (`PP` a `XGG`)
  - modelo da camiseta (`PV`, `Social`, `Brim`, `Polo`, `Moletom`)
  - aplicação (`Frente`, `Verso`, `Frente e Verso`)
- Botão **Criar Layout** com validação completa dos campos obrigatórios.
- Geração de prompt de criação com regra crítica de originalidade:
  - **nunca alterar a logo anexada**
  - preservar identidade visual 100%
- Tentativa de geração de imagem via Gemini (texto + logo anexa).
- Exibição da imagem gerada no painel de mockup quando o modelo retornar imagem.

## Requisitos
- Python 3.10+

## Executar local
```bash
python3 -m pip install -r requirements.txt
python3 src/app.py
```

## Compilar executável
```bash
./build_executable.sh
```

Saída esperada:
- `dist/agente_uniformes`

## Fluxo de uso
1. Informe API key Gemini e clique em **Connect**.
2. Se a chave for real/ativa, o sistema loga e carrega modelos no dropdown.
3. Preencha briefing, escolha cor, tamanho, modelo e aplicação (frente/verso).
4. Importe a logo.
5. Clique em **Criar Layout** para gerar imagem.
6. Se o modelo não retornar imagem, troque para um modelo Gemini com suporte a imagem.

## Testes
```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile src/app.py src/uniform_agent.py
```
