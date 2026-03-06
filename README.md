# Uniform Design Automation (Desktop • Gemini)

Aplicação desktop em Python/Tkinter com layout 3x3 estilo dashboard SaaS para automação de design de uniformes.

## O que foi implementado
- Login por **API Key Gemini** com validação real da chave (formato + consulta de modelos na API).
- Recusa de login para chave inválida/inativa.
- Dropdown dinâmico para escolher versão da IA (modelos Gemini disponíveis na chave).
- Painéis em grade 3x3 no estilo da referência visual:
  - API Login
  - Briefing de Uniforme
  - Upload de Logo
  - Selecionar Cor (picker horizontal + HEX)
  - Configuração da Peça
  - Técnica de Impressão
  - Mockup de Uniforme
  - Ficha Técnica
  - Console GPT
- Envio de prompt + logo para Gemini (`generateContent`).
- Teste interno E2E local via botão e por testes automatizados.

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
3. Preencha briefing, escolha cor e técnica.
4. Anexe logo e clique em **Gerar Prompt**.
5. Clique em **Enviar para Gemini**.

## Testes
```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile src/app.py src/uniform_agent.py
```
