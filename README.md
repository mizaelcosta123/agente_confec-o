# Agente de Mockups de Uniformes (Desktop)

Aplicação desktop em Python/Tkinter para:
- login com API key da OpenAI;
- preenchimento de briefing para criação de uniforme;
- anexo de logo em `svg`, `png`, `jpg` ou `jpeg`;
- seleção de cor da camiseta com paleta e extração do HEX;
- seleção de tamanho de mockup, modelo da peça e técnica (`bordado` ou `silk`);
- geração de prompt completo e envio direto para o ChatGPT.

## Requisitos
- Python 3.10+

## Rodar localmente
```bash
python3 -m pip install -r requirements.txt
python3 src/app.py
```

## Compilar executável
```bash
./build_executable.sh
```

Saída esperada:
- Linux/macOS: `dist/agente_uniformes`

## Fluxo da interface
1. Abra o app e informe sua API key.
2. Preencha os dados do uniforme.
3. Anexe a logo (opcional).
4. Clique em **Gerar prompt completo** para revisar o payload.
5. Clique em **Enviar para ChatGPT** para receber o mockup técnico textual.
