# Uniform Design Automation (Desktop • Gemini)

Aplicação desktop em Python/Tkinter para automação de mockups de uniformes com visual dark profissional no estilo dashboard.

## O que foi implementado
- Interface reorganizada em 3 áreas funcionais (configuração, resultados, execução), inspirada no layout de referência.
- Botão principal **GERAR MOCKUP** implementado e funcional.
- Botões de topo: **Novo Projeto**, **Salvar Projeto**, **Exportar Ficha Técnica**.
- Login com API Key Gemini + validação real da chave + carregamento de versões da IA no dropdown.
- Fluxo completo:
  - briefing (segmento, cores, detalhes),
  - upload da logo,
  - seleção de modelo/tamanho/lado de aplicação,
  - técnica de impressão,
  - geração de prompt e tentativa de geração de imagem.
- Regra crítica aplicada no prompt: **jamais alterar a logo anexada**.

## Campos de produção
- Modelo da camiseta: `PV`, `Social`, `Brim`, `Polo`, `Moletom`
- Tamanho mockup: `TBU`, `PP`, `P`, `M`, `G`, `GG`, `XGG`
- Tamanho camiseta final: `PP`, `P`, `M`, `G`, `GG`, `XGG`
- Aplicação: `Frente`, `Verso`, `Frente e Verso`
- Técnica: `Bordado`, `Silk Screen`, `Sublimação`

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

## Fluxo rápido
1. Informe API key e conecte.
2. Preencha briefing e configuração da peça.
3. Importe a logo.
4. Clique em **GERAR MOCKUP**.
5. Revise resultado, console e ficha técnica.

## Testes
```bash
python3 -m py_compile src/app.py src/uniform_agent.py
python3 -m unittest discover -s tests -v
```
