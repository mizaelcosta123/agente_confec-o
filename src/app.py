import os
import tkinter as tk
from tkinter import filedialog, messagebox

from uniform_agent import (
    UniformBriefing,
    build_creation_prompt,
    generate_layout_image_with_gemini,
    generate_local_mock_response,
    generate_with_gemini,
    validate_gemini_key,
)

BG = "#0F172A"
PANEL_BG = "#1E293B"
PANEL_BORDER = "#334155"
TEXT = "#E2E8F0"
ACCENT = "#38BDF8"
ENTRY_BG = "#0B1220"

CAMISETA_MODELOS = ["PV", "Social", "Brim", "Polo", "Moletom"]
TAMANHOS = ["PP", "P", "M", "G", "GG", "XGG"]
LADOS = ["Frente", "Verso", "Frente e Verso"]


class UniformAgentApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Uniform Design Automation • Gemini")
        self.root.geometry("1440x930")
        self.root.configure(bg=BG)

        self.api_key = ""
        self.logo_file: str | None = None
        self.available_models: list[str] = []

        self.selected_hex = tk.StringVar(value="#1E73BE")
        self.model_var = tk.StringVar(value="")
        self.modelagem_var = tk.StringVar(value="Regular")
        self.tecnica_var = tk.StringVar(value="Sublimação")
        self.mockup_size_var = tk.StringVar(value="TBU")
        self.tamanho_camiseta_var = tk.StringVar(value="M")
        self.modelo_camiseta_var = tk.StringVar(value="Polo")
        self.aplicacao_lado_var = tk.StringVar(value="Frente")

        self.generated_image_path: str | None = None
        self.generated_photo = None

        self._build_layout()

    def _panel(self, parent, title: str):
        panel = tk.Frame(parent, bg=PANEL_BG, highlightbackground=PANEL_BORDER, highlightthickness=1)
        header = tk.Frame(panel, bg=PANEL_BG)
        header.pack(fill="x", padx=12, pady=(10, 6))
        tk.Label(header, text=title, fg=TEXT, bg=PANEL_BG, font=("Segoe UI", 15, "bold")).pack(side="left")
        tk.Label(header, text="•••   ✕", fg="#94A3B8", bg=PANEL_BG, font=("Segoe UI", 10)).pack(side="right")
        tk.Frame(panel, bg=PANEL_BORDER, height=1).pack(fill="x")
        return panel

    def _button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=ACCENT,
            fg="#0B1220",
            activebackground="#7DD3FC",
            activeforeground="#0B1220",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=10,
            pady=7,
            cursor="hand2",
        )

    def _entry(self, parent, show=None):
        return tk.Entry(parent, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 11), show=show)

    def _build_layout(self):
        grid = tk.Frame(self.root, bg=BG)
        grid.pack(fill="both", expand=True, padx=18, pady=18)

        for c in range(3):
            grid.grid_columnconfigure(c, weight=1, uniform="col")
        for r in range(3):
            grid.grid_rowconfigure(r, weight=1, uniform="row")

        self._build_api_login(self._panel(grid, "API Login"), grid)
        self._build_briefing(self._panel(grid, "Briefing de Uniforme"), grid)
        self._build_upload(self._panel(grid, "Upload de Logo"), grid)
        self._build_color_picker(self._panel(grid, "Selecionar Cor"), grid)
        self._build_configuracao(self._panel(grid, "Configuração da Peça"), grid)
        self._build_tecnica(self._panel(grid, "Técnica de Impressão"), grid)
        self._build_mockup(self._panel(grid, "Mockup de Uniforme"), grid)
        self._build_ficha(self._panel(grid, "Ficha Técnica"), grid)
        self._build_console(self._panel(grid, "Console GPT"), grid)

    def _build_api_login(self, panel, grid):
        panel.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(body, text="API Key:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.api_key_entry = self._entry(body, show="*")
        self.api_key_entry.pack(fill="x", pady=(6, 10), ipady=9)

        tk.Label(body, text="Versão da IA:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.model_dropdown = tk.OptionMenu(body, self.model_var, "")
        self.model_dropdown.configure(bg=ENTRY_BG, fg=TEXT, activebackground=ENTRY_BG, activeforeground=TEXT, relief="flat")
        self.model_dropdown["menu"].configure(bg=ENTRY_BG, fg=TEXT)
        self.model_dropdown.pack(fill="x", pady=(6, 12))

        self._button(body, "Connect", self.connect_api).pack(fill="x")
        self.api_status = tk.Label(body, text="Status: aguardando chave Gemini", bg=PANEL_BG, fg="#94A3B8", font=("Segoe UI", 10))
        self.api_status.pack(anchor="w", pady=(10, 0))

    def _build_briefing(self, panel, grid):
        panel.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(body, text="Segmento:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.segmento_entry = self._entry(body)
        self.segmento_entry.pack(fill="x", pady=(4, 8), ipady=8)

        tk.Label(body, text="Cores:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.cores_entry = self._entry(body)
        self.cores_entry.pack(fill="x", pady=(4, 8), ipady=8)

        tk.Label(body, text="Detalhes:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.detalhes_text = tk.Text(body, height=5, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 11))
        self.detalhes_text.pack(fill="both", expand=True, pady=(4, 10))

        self._button(body, "Gerar Prompt", self.gerar_prompt).pack(fill="x")

    def _build_upload(self, panel, grid):
        panel.grid(row=0, column=2, sticky="nsew", padx=8, pady=8)
        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        self._button(body, "Selecionar Arquivo", self.selecionar_logo).pack(fill="x", pady=(0, 10))

        self.logo_preview = tk.Label(body, text="LOGO", bg=ENTRY_BG, fg="#93C5FD", font=("Segoe UI", 20, "bold"), relief="groove")
        self.logo_preview.pack(fill="both", expand=True)
        self.logo_name = tk.Label(body, text="Nenhum arquivo selecionado", bg=PANEL_BG, fg="#94A3B8", font=("Segoe UI", 9))
        self.logo_name.pack(anchor="w", pady=(8, 8))

        self._button(body, "Upload", self.upload_logo).pack(fill="x")

    def _build_color_picker(self, panel, grid):
        panel.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        self.color_canvas = tk.Canvas(body, height=70, bg=ENTRY_BG, highlightthickness=0)
        self.color_canvas.pack(fill="x")
        self._draw_gradient(self.color_canvas)
        self.color_canvas.bind("<Button-1>", self.pick_color_from_gradient)

        hex_row = tk.Frame(body, bg=PANEL_BG)
        hex_row.pack(fill="x", pady=10)
        tk.Label(hex_row, text="HEX:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")
        self.hex_box = self._entry(hex_row)
        self.hex_box.pack(side="left", fill="x", expand=True, padx=(8, 0), ipady=6)
        self.hex_box.insert(0, self.selected_hex.get())

        self._button(body, "Confirmar Cor", self.confirmar_cor).pack(fill="x")

    def _build_configuracao(self, panel, grid):
        panel.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(body, text="Tamanho Mockup:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        mockup_menu = tk.OptionMenu(body, self.mockup_size_var, "TBU", *TAMANHOS)
        mockup_menu.configure(bg=ENTRY_BG, fg=TEXT, activebackground=ENTRY_BG, activeforeground=TEXT, relief="flat")
        mockup_menu["menu"].configure(bg=ENTRY_BG, fg=TEXT)
        mockup_menu.pack(fill="x", pady=(4, 8))

        tk.Label(body, text="Tamanho Camiseta:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tamanho_menu = tk.OptionMenu(body, self.tamanho_camiseta_var, *TAMANHOS)
        tamanho_menu.configure(bg=ENTRY_BG, fg=TEXT, activebackground=ENTRY_BG, activeforeground=TEXT, relief="flat")
        tamanho_menu["menu"].configure(bg=ENTRY_BG, fg=TEXT)
        tamanho_menu.pack(fill="x", pady=(4, 8))

        tk.Label(body, text="Modelo da Camiseta:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        modelo_menu = tk.OptionMenu(body, self.modelo_camiseta_var, *CAMISETA_MODELOS)
        modelo_menu.configure(bg=ENTRY_BG, fg=TEXT, activebackground=ENTRY_BG, activeforeground=TEXT, relief="flat")
        modelo_menu["menu"].configure(bg=ENTRY_BG, fg=TEXT)
        modelo_menu.pack(fill="x", pady=(4, 8))

        tk.Label(body, text="Aplicação:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        lado_menu = tk.OptionMenu(body, self.aplicacao_lado_var, *LADOS)
        lado_menu.configure(bg=ENTRY_BG, fg=TEXT, activebackground=ENTRY_BG, activeforeground=TEXT, relief="flat")
        lado_menu["menu"].configure(bg=ENTRY_BG, fg=TEXT)
        lado_menu.pack(fill="x", pady=(4, 8))

        row = tk.Frame(body, bg=PANEL_BG)
        row.pack(fill="x", pady=(6, 0))
        tk.Label(row, text="Modelagem:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")
        for name in ["Regular", "Slim", "Oversize"]:
            tk.Radiobutton(
                row,
                text=name,
                value=name,
                variable=self.modelagem_var,
                bg=PANEL_BG,
                fg=TEXT,
                selectcolor=ENTRY_BG,
                activebackground=PANEL_BG,
                activeforeground=TEXT,
                highlightthickness=0,
                font=("Segoe UI", 10),
            ).pack(side="left", padx=8)

    def _build_tecnica(self, panel, grid):
        panel.grid(row=1, column=2, sticky="nsew", padx=8, pady=8)
        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        for value in ["Bordado", "Silk Screen", "Sublimação"]:
            tk.Radiobutton(
                body,
                text=value,
                value=value,
                variable=self.tecnica_var,
                bg=PANEL_BG,
                fg=TEXT,
                selectcolor=ENTRY_BG,
                activebackground=PANEL_BG,
                activeforeground=TEXT,
                highlightthickness=0,
                font=("Segoe UI", 12),
            ).pack(anchor="w", pady=6)

        tk.Label(body, text="Proporção da logo (ex: 12x8 cm):", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(18, 4))
        self.logo_prop_entry = self._entry(body)
        self.logo_prop_entry.pack(fill="x", ipady=8)
        self.logo_prop_entry.insert(0, "12x8 cm")

    def _build_mockup(self, panel, grid):
        panel.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        self.mockup_canvas = tk.Canvas(body, bg="#0B1220", highlightthickness=0)
        self.mockup_canvas.pack(fill="both", expand=True)
        self._draw_mockup_placeholder()

    def _build_ficha(self, panel, grid):
        panel.grid(row=2, column=1, sticky="nsew", padx=8, pady=8)
        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        self.ficha_text = tk.Text(body, bg=ENTRY_BG, fg=TEXT, relief="flat", font=("Segoe UI", 12), wrap="word")
        self.ficha_text.pack(fill="both", expand=True)
        self.ficha_text.insert("1.0", "- Tamanho: TBU\n- Peito: 56 cm\n- Comprimento: 72 cm\n- Método: Sublimação")

    def _build_console(self, panel, grid):
        panel.grid(row=2, column=2, sticky="nsew", padx=8, pady=8)
        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        self.console_text = tk.Text(body, bg="#0B1220", fg=TEXT, relief="flat", font=("Consolas", 11), wrap="word")
        self.console_text.pack(fill="both", expand=True, pady=(0, 10))
        self.console_text.insert("1.0", "Pronto. Informe sua API Key Gemini e clique em Connect.\n")

        self._button(body, "Criar Layout", self.criar_layout).pack(fill="x")
        self._button(body, "Enviar Texto para Gemini", self.enviar_para_gemini).pack(fill="x", pady=(8, 0))
        self._button(body, "Teste interno", self.teste_interno).pack(fill="x", pady=(8, 0))

    def _draw_gradient(self, canvas: tk.Canvas):
        canvas.delete("all")
        width = 600
        colors = ["#ff0000", "#ffff00", "#00ff00", "#00ffff", "#0000ff", "#ff00ff"]
        segment = width // (len(colors) - 1)
        for i in range(width):
            idx = min(i // segment, len(colors) - 2)
            frac = (i % segment) / segment
            c1 = colors[idx]
            c2 = colors[idx + 1]
            r = int(int(c1[1:3], 16) * (1 - frac) + int(c2[1:3], 16) * frac)
            g = int(int(c1[3:5], 16) * (1 - frac) + int(c2[3:5], 16) * frac)
            b = int(int(c1[5:7], 16) * (1 - frac) + int(c2[5:7], 16) * frac)
            canvas.create_line(i, 0, i, 70, fill=f"#{r:02x}{g:02x}{b:02x}")

    def _draw_mockup_placeholder(self):
        c = self.mockup_canvas
        c.delete("all")
        w = max(c.winfo_width(), 300)
        h = max(c.winfo_height(), 240)
        cx = w // 2
        c.create_polygon(cx - 80, 60, cx - 120, 110, cx - 85, 120, cx - 65, 250, cx + 65, 250, cx + 85, 120, cx + 120, 110, cx + 80, 60, cx + 40, 70, cx + 20, 50, cx - 20, 50, cx - 40, 70, fill="#2563EB", outline="#1D4ED8", width=2)
        c.create_text(cx, 145, text="Pré-visualização", fill="#BAE6FD", font=("Segoe UI", 12, "bold"))

    def _show_generated_image(self, path: str):
        try:
            self.generated_photo = tk.PhotoImage(file=path)
            self.mockup_canvas.delete("all")
            self.mockup_canvas.create_image(10, 10, anchor="nw", image=self.generated_photo)
        except Exception:
            self._log(f"Imagem gerada salva em: {path}")
            self._draw_mockup_placeholder()

    def _log(self, message: str):
        self.console_text.insert("end", message + "\n")
        self.console_text.see("end")

    def connect_api(self):
        key = self.api_key_entry.get().strip()
        self._log("Validando chave Gemini...")
        ok, msg, models = validate_gemini_key(key)
        if not ok:
            self.api_status.configure(text=f"Status: {msg}", fg="#FCA5A5")
            self._log(f"Falha no login: {msg}")
            messagebox.showerror("API Login", msg)
            return

        self.api_key = key
        self.available_models = models
        self._refresh_model_dropdown(models)
        self.api_status.configure(text="Status: conectado", fg="#86EFAC")
        self._log("API conectada com sucesso.")

    def _refresh_model_dropdown(self, models: list[str]):
        menu = self.model_dropdown["menu"]
        menu.delete(0, "end")
        self.model_var.set(models[0])
        for m in models:
            menu.add_command(label=m, command=lambda value=m: self.model_var.set(value))

    def selecionar_logo(self):
        path = filedialog.askopenfilename(
            title="Selecione o arquivo da logo",
            filetypes=[("Imagens", "*.svg *.png *.jpg *.jpeg")],
        )
        if path:
            self.logo_file = path
            self.logo_name.configure(text=os.path.basename(path))
            self._log(f"Arquivo selecionado: {os.path.basename(path)}")

    def upload_logo(self):
        if not self.logo_file:
            messagebox.showwarning("Upload", "Selecione um arquivo antes do upload.")
            return
        self._log("Upload preparado (arquivo será enviado junto ao prompt).")
        messagebox.showinfo("Upload", "Logo anexada com sucesso para o próximo envio.")

    def pick_color_from_gradient(self, event):
        width = max(self.color_canvas.winfo_width(), 1)
        x = max(0, min(event.x, width - 1))
        hue = x / width
        import colorsys

        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.9)
        hex_color = f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"
        self.selected_hex.set(hex_color)
        self.hex_box.delete(0, "end")
        self.hex_box.insert(0, hex_color)

    def confirmar_cor(self):
        color = self.hex_box.get().strip() or "#1E73BE"
        self.selected_hex.set(color)
        self._log(f"Cor confirmada: {color}")

    def _briefing(self) -> UniformBriefing:
        return UniformBriefing(
            segmento=self.segmento_entry.get().strip(),
            cores=self.cores_entry.get().strip(),
            detalhes=self.detalhes_text.get("1.0", "end").strip(),
            cor_hex=self.selected_hex.get().strip(),
            logo_proporcao=self.logo_prop_entry.get().strip(),
            tamanho_mockup=self.mockup_size_var.get().strip(),
            tamanho_camiseta=self.tamanho_camiseta_var.get().strip(),
            modelo_camiseta=self.modelo_camiseta_var.get().strip(),
            aplicacao_lado=self.aplicacao_lado_var.get().strip(),
            modelagem=self.modelagem_var.get().strip(),
            tecnica_impressao=self.tecnica_var.get().strip(),
        )

    def _validate_required_inputs(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "Conecte uma API key Gemini válida."
        if not self.model_var.get().strip():
            return False, "Selecione a versão da IA no dropdown."
        if not self.segmento_entry.get().strip():
            return False, "Preencha o campo Segmento."
        if not self.cores_entry.get().strip():
            return False, "Preencha o campo Cores."
        if not self.detalhes_text.get("1.0", "end").strip():
            return False, "Preencha o campo Detalhes."
        if not self.logo_file:
            return False, "Importe a logo antes de criar layout."
        if not self.hex_box.get().strip():
            return False, "Confirme a cor (HEX)."
        if not self.logo_prop_entry.get().strip():
            return False, "Preencha a proporção da logo."
        return True, "OK"

    def gerar_prompt(self):
        briefing = self._briefing()
        prompt = build_creation_prompt(briefing)

        self.console_text.delete("1.0", "end")
        self._log("Prompt de criação gerado com sucesso.")
        self._log("--- PROMPT ---")
        self._log(prompt)

        ficha = (
            f"- Tamanho mockup: {briefing.tamanho_mockup}\n"
            f"- Tamanho final: {briefing.tamanho_camiseta}\n"
            f"- Modelo camiseta: {briefing.modelo_camiseta}\n"
            f"- Aplicação: {briefing.aplicacao_lado}\n"
            f"- Método: {briefing.tecnica_impressao}\n"
            f"- Cor: {briefing.cor_hex}\n"
            f"- Regra da logo: manter original sem alteração"
        )
        self.ficha_text.delete("1.0", "end")
        self.ficha_text.insert("1.0", ficha)

    def criar_layout(self):
        valid, msg = self._validate_required_inputs()
        if not valid:
            messagebox.showwarning("Dados obrigatórios", msg)
            self._log(f"Validação falhou: {msg}")
            return

        briefing = self._briefing()
        prompt = build_creation_prompt(briefing)

        self._log("Enviando prompt de criação de layout para Gemini...")
        self._log("Regra aplicada: logo original não pode ser alterada.")

        try:
            image_path, summary = generate_layout_image_with_gemini(
                self.api_key,
                self.model_var.get().strip(),
                prompt,
                self.logo_file,
            )
        except Exception as exc:
            self._log(f"Falha ao criar layout de imagem: {exc}")
            messagebox.showerror("Criar Layout", str(exc))
            return

        if image_path:
            self.generated_image_path = image_path
            self._show_generated_image(image_path)
            self._log(f"Layout criado com sucesso: {image_path}")
            if summary:
                self._log(summary)
            messagebox.showinfo("Criar Layout", f"Imagem gerada com sucesso em:\n{image_path}")
        else:
            self._draw_mockup_placeholder()
            self._log("Modelo retornou somente texto, sem imagem. Exibindo resumo no console.")
            self._log(summary)
            messagebox.showwarning(
                "Criar Layout",
                "O modelo selecionado não retornou imagem.\n"
                "Troque para uma versão Gemini com suporte a imagem e tente novamente.",
            )

    def enviar_para_gemini(self):
        if not self.api_key:
            messagebox.showwarning("API", "Conecte uma chave Gemini válida antes de enviar.")
            return

        model = self.model_var.get().strip()
        if not model:
            messagebox.showwarning("Modelo", "Selecione uma versão da IA no dropdown.")
            return

        prompt = build_creation_prompt(self._briefing())
        self._log("Enviando prompt textual para Gemini...")

        try:
            answer = generate_with_gemini(self.api_key, model, prompt, self.logo_file)
        except Exception as exc:
            self._log(f"Erro ao gerar resposta: {exc}")
            messagebox.showerror("Gemini", str(exc))
            return

        self._log("Resposta textual recebida com sucesso.")
        self._log("--- RESPOSTA GEMINI ---")
        self._log(answer)

    def teste_interno(self):
        briefing = self._briefing()
        prompt = build_creation_prompt(briefing)
        local = generate_local_mock_response(briefing)

        checks = [
            "OK" if "NUNCA alterar a logo anexada" in prompt else "FALHA",
            "OK" if "Logo original preservada" in local else "FALHA",
        ]

        self._log("[TESTE INTERNO E2E]")
        self._log(f"- Prompt com regra de originalidade da logo: {checks[0]}")
        self._log(f"- Estrutura de contingência local: {checks[1]}")
        self._log(local)
        messagebox.showinfo("Teste interno", "Teste interno executado com sucesso.")


def main():
    root = tk.Tk()
    app = UniformAgentApp(root)
    app.mockup_canvas.bind("<Configure>", lambda _e: app._draw_mockup_placeholder())
    root.mainloop()


if __name__ == "__main__":
    main()
