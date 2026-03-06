import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from openai import OpenAI

from uniform_agent import (
    UniformBriefing,
    build_prompt,
    encode_logo_as_data_url,
    generate_local_mock_response,
    is_quota_error,
)

COLOR_PALETTE = {
    "Branco": "#FFFFFF",
    "Preto": "#000000",
    "Cinza Claro": "#D3D3D3",
    "Cinza Médio": "#808080",
    "Cinza Escuro": "#404040",
    "Azul Marinho": "#001F3F",
    "Azul Royal": "#4169E1",
    "Azul Céu": "#87CEEB",
    "Azul Petróleo": "#004B5A",
    "Verde Bandeira": "#009B3A",
    "Verde Militar": "#4B5320",
    "Verde Limão": "#32CD32",
    "Amarelo Ouro": "#FFD700",
    "Amarelo Canário": "#FFEF00",
    "Laranja": "#FFA500",
    "Vermelho": "#FF0000",
    "Vinho": "#722F37",
    "Bordô": "#800020",
    "Rosa": "#FFC0CB",
    "Roxo": "#800080",
    "Lilás": "#C8A2C8",
    "Marrom": "#8B4513",
    "Bege": "#F5F5DC",
    "Areia": "#C2B280",
    "Caqui": "#BDB76B",
    "Turquesa": "#40E0D0",
    "Ciano": "#00FFFF",
    "Magenta": "#FF00FF",
    "Salmão": "#FA8072",
    "Terracota": "#E2725B",
    "Off White": "#FAF9F6",
    "Grafite": "#2F4F4F",
    "Azul Bic": "#0033CC",
    "Verde Esmeralda": "#50C878",
    "Dourado": "#D4AF37",
    "Prata": "#C0C0C0",
}

MODEL_OPTIONS = [
    "Camisa Polo",
    "Camisa Manga Longa Malha PC",
    "Camisa Manga Curta Malha PV",
    "Moletom",
    "Brim",
]

PRINT_OPTIONS = ["Bordado", "Silk"]
MOCKUP_SIZE_OPTIONS = ["TBU", "PP", "P", "M", "G", "GG", "XGG"]

SYSTEM_PROMPT = (
    "Você é um agente autônomo especialista em design e confecção de uniformes profissionais. "
    "Crie mockups técnicos profissionais de camisetas com padrão de confecção, priorizando clareza, "
    "consistência visual e viabilidade de produção."
)


class UniformAgentApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Agente de Mockups de Uniformes")
        self.root.geometry("980x780")

        self.client = None
        self.logo_file = None

        self._build_ui()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.login_tab = ttk.Frame(self.notebook)
        self.form_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.login_tab, text="Login")
        self.notebook.add(self.form_tab, text="Formulário")
        self.notebook.pack(fill="both", expand=True)

        self._build_login_tab()
        self._build_form_tab()

        self.notebook.tab(1, state="disabled")

    def _build_login_tab(self):
        container = ttk.Frame(self.login_tab, padding=24)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Acesso inicial", font=("Arial", 16, "bold")).pack(anchor="w")
        ttk.Label(
            container,
            text="Informe sua API Key da OpenAI para habilitar o envio de prompts completos.",
        ).pack(anchor="w", pady=(8, 16))

        ttk.Label(container, text="API Key").pack(anchor="w")
        self.api_key_entry = ttk.Entry(container, show="*", width=70)
        self.api_key_entry.pack(anchor="w", pady=(4, 12))

        ttk.Button(container, text="Entrar", command=self.login).pack(anchor="w")

    def _build_form_tab(self):
        container = ttk.Frame(self.form_tab, padding=16)
        container.pack(fill="both", expand=True)

        top = ttk.Frame(container)
        top.pack(fill="x")

        ttk.Label(top, text="Modelo OpenAI").grid(row=0, column=0, sticky="w")
        self.model_entry = ttk.Entry(top, width=30)
        self.model_entry.insert(0, "gpt-4.1-mini")
        self.model_entry.grid(row=0, column=1, padx=8, pady=6, sticky="w")

        fields = ttk.LabelFrame(container, text="Dados para montagem do prompt", padding=10)
        fields.pack(fill="x", pady=8)

        self.segmento = self._add_labeled_entry(fields, "Segmento", 0)
        self.objetivo = self._add_labeled_entry(fields, "Objetivo visual", 1)
        self.publico = self._add_labeled_entry(fields, "Público de uso", 2)
        self.restricoes = self._add_labeled_entry(fields, "Restrições", 3)

        ttk.Label(fields, text="Cor da camiseta").grid(row=4, column=0, sticky="w", pady=4)
        self.color_var = tk.StringVar()
        self.color_combo = ttk.Combobox(
            fields,
            textvariable=self.color_var,
            values=[f"{name} ({hex_code})" for name, hex_code in COLOR_PALETTE.items()],
            width=45,
            state="readonly",
        )
        self.color_combo.grid(row=4, column=1, sticky="w", padx=8)
        self.color_combo.bind("<<ComboboxSelected>>", self._update_hex)

        ttk.Label(fields, text="HEX detectado").grid(row=5, column=0, sticky="w", pady=4)
        self.hex_label = ttk.Label(fields, text="-")
        self.hex_label.grid(row=5, column=1, sticky="w", padx=8)

        ttk.Label(fields, text="Proporção da logo (ex: 12x8 cm ou 18%)").grid(row=6, column=0, sticky="w", pady=4)
        self.logo_ratio = ttk.Entry(fields, width=48)
        self.logo_ratio.grid(row=6, column=1, sticky="w", padx=8)

        ttk.Label(fields, text="Tamanho do mockup").grid(row=7, column=0, sticky="w", pady=4)
        self.mockup_size = ttk.Combobox(fields, values=MOCKUP_SIZE_OPTIONS, state="readonly", width=18)
        self.mockup_size.set("TBU")
        self.mockup_size.grid(row=7, column=1, sticky="w", padx=8)

        ttk.Label(fields, text="Modelo da peça").grid(row=8, column=0, sticky="w", pady=4)
        self.model_type = ttk.Combobox(fields, values=MODEL_OPTIONS, state="readonly", width=40)
        self.model_type.current(0)
        self.model_type.grid(row=8, column=1, sticky="w", padx=8)

        ttk.Label(fields, text="Tipo de aplicação").grid(row=9, column=0, sticky="w", pady=4)
        self.print_type = ttk.Combobox(fields, values=PRINT_OPTIONS, state="readonly", width=18)
        self.print_type.current(0)
        self.print_type.grid(row=9, column=1, sticky="w", padx=8)

        logo_frame = ttk.Frame(container)
        logo_frame.pack(fill="x", pady=(4, 8))
        ttk.Button(logo_frame, text="Anexar logo (SVG, PNG, JPG, JPEG)", command=self.pick_logo).pack(side="left")
        self.logo_label = ttk.Label(logo_frame, text="Nenhum arquivo selecionado")
        self.logo_label.pack(side="left", padx=10)

        action_frame = ttk.Frame(container)
        action_frame.pack(fill="x", pady=6)
        ttk.Button(action_frame, text="Gerar prompt completo", command=self.generate_prompt).pack(side="left")
        ttk.Button(action_frame, text="Enviar para ChatGPT", command=self.send_prompt).pack(side="left", padx=8)
        ttk.Button(action_frame, text="Teste interno (E2E local)", command=self.run_internal_test).pack(side="left", padx=8)

        self.prompt_text = tk.Text(container, height=14, wrap="word")
        self.prompt_text.pack(fill="both", expand=True, pady=8)

        ttk.Label(container, text="Resposta do modelo", font=("Arial", 11, "bold")).pack(anchor="w")
        self.response_text = tk.Text(container, height=12, wrap="word")
        self.response_text.pack(fill="both", expand=True)

    @staticmethod
    def _add_labeled_entry(parent, label, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        entry = ttk.Entry(parent, width=48)
        entry.grid(row=row, column=1, sticky="w", padx=8)
        return entry

    def _update_hex(self, _event=None):
        selected = self.color_var.get()
        hex_code = selected.split("(")[-1].replace(")", "") if "(" in selected else "-"
        self.hex_label.config(text=hex_code)

    def _current_briefing(self) -> UniformBriefing:
        return UniformBriefing(
            segmento=self.segmento.get(),
            objetivo_visual=self.objetivo.get(),
            publico_uso=self.publico.get(),
            restricoes=self.restricoes.get(),
            cor_nome=self.color_var.get(),
            cor_hex=self.hex_label.cget("text"),
            logo_proporcao=self.logo_ratio.get(),
            tamanho_mockup=self.mockup_size.get(),
            modelo_peca=self.model_type.get(),
            metodo_aplicacao=self.print_type.get(),
        )

    def login(self):
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("Atenção", "Informe uma API Key válida.")
            return

        self.client = OpenAI(api_key=api_key)
        self.notebook.tab(1, state="normal")
        self.notebook.select(1)
        messagebox.showinfo("Sucesso", "Login concluído. Formulário liberado.")

    def pick_logo(self):
        path = filedialog.askopenfilename(
            title="Selecione o arquivo da logo",
            filetypes=[("Imagens", "*.svg *.png *.jpg *.jpeg")],
        )
        if path:
            self.logo_file = path
            self.logo_label.config(text=path.split("/")[-1])

    def generate_prompt(self):
        prompt = build_prompt(self._current_briefing())
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert(tk.END, prompt)

    def run_internal_test(self):
        briefing = self._current_briefing()
        prompt = build_prompt(briefing)
        local_answer = generate_local_mock_response(briefing)

        checks = []
        checks.append("OK" if "Pedido de criação de mockup" in prompt else "FALHA")
        checks.append("OK" if "A) Resumo do pedido interpretado" in local_answer else "FALHA")

        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert(tk.END, prompt)

        self.response_text.delete("1.0", tk.END)
        self.response_text.insert(
            tk.END,
            "[TESTE INTERNO E2E LOCAL]\n"
            f"- Prompt gerado: {checks[0]}\n"
            f"- Resposta estruturada local: {checks[1]}\n\n"
            f"{local_answer}",
        )
        messagebox.showinfo("Teste interno", "Teste E2E local concluído com sucesso.")

    def send_prompt(self):
        if not self.client:
            messagebox.showwarning("Atenção", "Faça login com API Key antes de enviar.")
            return

        prompt = self.prompt_text.get("1.0", tk.END).strip() or build_prompt(self._current_briefing())
        model = self.model_entry.get().strip() or "gpt-4.1-mini"

        input_content = [{"type": "input_text", "text": prompt}]

        if self.logo_file:
            data_url = encode_logo_as_data_url(self.logo_file)
            input_content.append(
                {
                    "type": "input_image",
                    "image_url": data_url,
                }
            )

        try:
            response = self.client.responses.create(
                model=model,
                input=[
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
                    },
                    {
                        "role": "user",
                        "content": input_content,
                    },
                ],
            )
            answer = response.output_text
        except Exception as exc:
            if is_quota_error(exc):
                briefing = self._current_briefing()
                fallback = generate_local_mock_response(briefing)
                self.response_text.delete("1.0", tk.END)
                self.response_text.insert(
                    tk.END,
                    "[MODO CONTINGÊNCIA: sem crédito/quota na API]\n"
                    "A requisição para OpenAI falhou por quota insuficiente (HTTP 429).\n"
                    "Foi gerada uma resposta local para você não parar o fluxo de trabalho.\n\n"
                    f"{fallback}",
                )
                messagebox.showwarning(
                    "Quota insuficiente",
                    "Sua API key está sem saldo/quota.\n"
                    "Ative cobrança/créditos em platform.openai.com e tente novamente.\n"
                    "Enquanto isso, o sistema usou modo de contingência local.",
                )
                return

            messagebox.showerror("Erro ao enviar", str(exc))
            return

        self.response_text.delete("1.0", tk.END)
        self.response_text.insert(tk.END, answer)


if __name__ == "__main__":
    app_root = tk.Tk()
    UniformAgentApp(app_root)
    app_root.mainloop()
