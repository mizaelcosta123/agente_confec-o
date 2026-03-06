# Agente de Mockups de Uniformes (Desktop)

Aplicação desktop em Python/Tkinter para:
- login com API key da OpenAI;
- preenchimento de briefing para criação de uniforme;
- anexo de logo em `svg`, `png`, `jpg` ou `jpeg`;
- seleção de cor da camiseta com paleta e extração do HEX;
- seleção de tamanho de mockup, modelo da peça e técnica (`bordado` ou `silk`);
- geração de prompt completo e envio direto para o ChatGPT;
- modo de contingência quando houver erro de quota (`429 insufficient_quota`);
- botão de **teste interno E2E local** sem chamada externa.

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
5. Clique em **Enviar para ChatGPT** para usar a API.
6. Se ocorrer erro de quota, o app ativa contingência local e continua entregando resposta estruturada.
7. Clique em **Teste interno (E2E local)** para validar fluxo interno sem dependência de saldo na API.

## Testes automáticos
```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile src/app.py src/uniform_agent.py
```

## Sobre o erro 429 (insufficient_quota)
Esse erro indica falta de saldo/quota na conta da API. Para reabilitar chamadas reais:
1. Acesse `https://platform.openai.com/`.
2. Verifique billing e limites da chave.
3. Refaça o envio no app.
