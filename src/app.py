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
PANEL_BG_ALT = "#243447"
PANEL_BORDER = "#334155"
TEXT = "#E2E8F0"
MUTED = "#94A3B8"
ACCENT = "#38BDF8"
ACCENT_2 = "#2563EB"
ENTRY_BG = "#0B1220"

CAMISETA_MODELOS = ["PV", "Social", "Brim", "Polo", "Moletom"]
TAMANHOS = ["PP", "P", "M", "G", "GG", "XGG"]
LADOS = ["Frente", "Verso", "Frente e Verso"]


class UniformAgentApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Agente de Mockups de Uniformes")
        self.root.geometry("1520x940")
        self.root.configure(bg=BG)

        self.api_key = ""
        self.logo_file: str | None = None
        self.available_models: list[str] = []
        self.generated_image_path: str | None = None
        self.generated_photo = None

        self.selected_hex = tk.StringVar(value="#1E73BE")
        self.model_var = tk.StringVar(value="")
        self.modelagem_var = tk.StringVar(value="Regular")
        self.tecnica_var = tk.StringVar(value="Sublimação")
        self.mockup_size_var = tk.StringVar(value="TBU")
        self.tamanho_camiseta_var = tk.StringVar(value="M")
        self.modelo_camiseta_var = tk.StringVar(value="Polo")
        self.aplicacao_lado_var = tk.StringVar(value="Frente")

        self._build_ui()

    def _mk_panel(self, parent, title):
        panel = tk.Frame(parent, bg=PANEL_BG, highlightthickness=1, highlightbackground=PANEL_BORDER)
        head = tk.Frame(panel, bg=PANEL_BG_ALT, height=42)
        head.pack(fill="x")
        tk.Label(head, text=title, bg=PANEL_BG_ALT, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(side="left", padx=14, pady=8)
        tk.Label(head, text="•••", bg=PANEL_BG_ALT, fg=MUTED, font=("Segoe UI", 12)).pack(side="right", padx=12)
        return panel

    def _btn(self, parent, text, command, big=False):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=ACCENT_2 if big else ACCENT,
            fg="#F8FAFC",
            activebackground="#3B82F6",
            activeforeground="#FFFFFF",
            relief="flat",
            font=("Segoe UI", 12 if big else 11, "bold"),
            padx=10,
            pady=9 if big else 7,
            cursor="hand2",
        )

    def _entry(self, parent, show=None):
        return tk.Entry(parent, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 12), show=show)

    def _option(self, parent, var, first, *others):
        op = tk.OptionMenu(parent, var, first, *others)
        op.configure(bg=ENTRY_BG, fg=TEXT, activebackground=ENTRY_BG, activeforeground=TEXT, relief="flat")
        op["menu"].configure(bg=ENTRY_BG, fg=TEXT)
        return op

    def _build_ui(self):
        self._build_topbar()

        content = tk.Frame(self.root, bg=BG)
        content.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_columnconfigure(2, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self._build_left_panel(content)
        self._build_center_panel(content)
        self._build_right_panel(content)

    def _build_topbar(self):
        top = tk.Frame(self.root, bg=PANEL_BG, highlightthickness=1, highlightbackground=PANEL_BORDER)
        top.pack(fill="x", padx=18, pady=16)

        tk.Label(top, text="🧊  Agente de Mockups de Uniformes", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 20, "bold")).pack(side="left", padx=16, pady=10)

        self._btn(top, "+ Novo Projeto", self.novo_projeto).pack(side="left", padx=8)
        self._btn(top, "Salvar Projeto", self.salvar_projeto).pack(side="left", padx=8)
        self._btn(top, "Exportar Ficha Técnica", self.exportar_ficha).pack(side="left", padx=8)

        tk.Label(top, text="API Key:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(side="left", padx=(22, 8))
        self.api_key_entry = self._entry(top, show="*")
        self.api_key_entry.pack(side="left", padx=(0, 8), ipady=6)

        self.model_var.set("")
        self.model_dropdown = self._option(top, self.model_var, "")
        self.model_dropdown.configure(width=18)
        self.model_dropdown.pack(side="left", padx=6)

        self._btn(top, "Connect", self.connect_api).pack(side="left", padx=8)

    def _build_left_panel(self, parent):
        panel = self._mk_panel(parent, "Configurar Camisa")
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(body, text="1. Briefing", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 8))

        tk.Label(body, text="Segmento", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.segmento_entry = self._entry(body)
        self.segmento_entry.pack(fill="x", ipady=8, pady=(4, 8))

        tk.Label(body, text="Cores", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.cores_entry = self._entry(body)
        self.cores_entry.pack(fill="x", ipady=8, pady=(4, 8))

        tk.Label(body, text="Detalhes", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.detalhes_entry = self._entry(body)
        self.detalhes_entry.pack(fill="x", ipady=8, pady=(4, 12))

        tk.Label(body, text="2. Logo", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(4, 8))
        self._btn(body, "Selecionar Arquivo", self.selecionar_logo).pack(fill="x")

        logo_box = tk.Frame(body, bg=ENTRY_BG, highlightthickness=1, highlightbackground=PANEL_BORDER)
        logo_box.pack(fill="x", pady=10)
        self.logo_label = tk.Label(logo_box, text="LOGO", bg=ENTRY_BG, fg="#93C5FD", font=("Segoe UI", 16, "bold"))
        self.logo_label.pack(pady=14)
        self.logo_name = tk.Label(body, text="Nenhum arquivo selecionado", bg=PANEL_BG, fg=MUTED, font=("Segoe UI", 9))
        self.logo_name.pack(anchor="w", pady=(0, 10))

        tk.Label(body, text="3. Camisa", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(4, 8))

        row_model = tk.Frame(body, bg=PANEL_BG)
        row_model.pack(fill="x", pady=4)
        tk.Label(row_model, text="Modelagem:", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left")
        for opt in ["Regular", "Slim", "Oversize"]:
            tk.Radiobutton(
                row_model,
                text=opt,
                value=opt,
                variable=self.modelagem_var,
                bg=PANEL_BG,
                fg=TEXT,
                selectcolor=ENTRY_BG,
                activebackground=PANEL_BG,
                activeforeground=TEXT,
                highlightthickness=0,
                font=("Segoe UI", 11),
            ).pack(side="left", padx=8)

        tk.Label(body, text="Tamanho Mockup", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(8, 0))
        self._option(body, self.mockup_size_var, "TBU", *TAMANHOS).pack(fill="x", pady=(4, 8))

        tk.Label(body, text="Tamanho Camiseta", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self._option(body, self.tamanho_camiseta_var, *TAMANHOS).pack(fill="x", pady=(4, 8))

        tk.Label(body, text="Modelo da Camiseta", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self._option(body, self.modelo_camiseta_var, *CAMISETA_MODELOS).pack(fill="x", pady=(4, 8))

        tk.Label(body, text="Aplicação", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self._option(body, self.aplicacao_lado_var, *LADOS).pack(fill="x", pady=(4, 8))

        tk.Label(body, text="4. Técnica", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(4, 8))
        row_tec = tk.Frame(body, bg=PANEL_BG)
        row_tec.pack(fill="x")
        for opt in ["Bordado", "Silk Screen", "Sublimação"]:
            tk.Radiobutton(
                row_tec,
                text=opt,
                value=opt,
                variable=self.tecnica_var,
                bg=PANEL_BG,
                fg=TEXT,
                selectcolor=ENTRY_BG,
                activebackground=PANEL_BG,
                activeforeground=TEXT,
                highlightthickness=0,
                font=("Segoe UI", 11),
            ).pack(side="left", padx=(0, 12))

        self._btn(body, "Confirmar Cor", self.confirmar_cor).pack(fill="x", pady=(12, 0))

    def _build_center_panel(self, parent):
        panel = self._mk_panel(parent, "Resultados")
        panel.grid(row=0, column=1, sticky="nsew", padx=10)

        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        self.mockup_canvas = tk.Canvas(body, bg="#1B2A44", highlightthickness=1, highlightbackground=PANEL_BORDER)
        self.mockup_canvas.pack(fill="both", expand=True)
        self._draw_mockup_placeholder()

        footer = tk.Frame(body, bg=PANEL_BG)
        footer.pack(fill="x", pady=(10, 0))

        tk.Label(footer, text="5. Cor (HEX)", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w")

        color_row = tk.Frame(footer, bg=PANEL_BG)
        color_row.pack(fill="x", pady=8)

        self.color_canvas = tk.Canvas(color_row, height=42, bg=ENTRY_BG, highlightthickness=1, highlightbackground=PANEL_BORDER)
        self.color_canvas.pack(side="left", fill="x", expand=True)
        self._draw_gradient(self.color_canvas)
        self.color_canvas.bind("<Button-1>", self.pick_color_from_gradient)

        self.hex_entry = self._entry(color_row)
        self.hex_entry.pack(side="left", padx=(8, 0), ipady=9)
        self.hex_entry.insert(0, self.selected_hex.get())

        self._btn(footer, "GERAR MOCKUP", self.gerar_mockup, big=True).pack(fill="x", pady=10)

    def _build_right_panel(self, parent):
        panel = self._mk_panel(parent, "Resultado & Execução")
        panel.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(body, text="Prompt Gerado", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.prompt_info = tk.Text(body, height=9, bg=ENTRY_BG, fg=TEXT, relief="flat", wrap="word", font=("Segoe UI", 12))
        self.prompt_info.pack(fill="x", pady=(6, 12))

        tk.Label(body, text="Ficha Técnica", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.ficha_text = tk.Text(body, height=8, bg=ENTRY_BG, fg=TEXT, relief="flat", wrap="word", font=("Segoe UI", 12))
        self.ficha_text.pack(fill="x", pady=(6, 12))

        tk.Label(body, text="Console", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.console = tk.Text(body, bg=ENTRY_BG, fg=TEXT, relief="flat", wrap="word", font=("Consolas", 12))
        self.console.pack(fill="both", expand=True, pady=(6, 12))

        self._btn(body, "ENVIAR PARA GPT", self.enviar_para_gpt, big=True).pack(fill="x")
        self._btn(body, "EXPORTAR FICHA", self.exportar_ficha).pack(fill="x", pady=(8, 0))

        self._log("Sistema iniciado. Conecte sua API Key Gemini.")

    def _draw_gradient(self, canvas: tk.Canvas):
        canvas.delete("all")
        width = 620
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
            canvas.create_line(i, 0, i, 42, fill=f"#{r:02x}{g:02x}{b:02x}")

    def _draw_mockup_placeholder(self):
        c = self.mockup_canvas
        c.delete("all")
        w = max(c.winfo_width(), 520)
        h = max(c.winfo_height(), 580)
        cx = w // 2
        cy = h // 2 - 30

        c.create_polygon(
            cx - 140, cy - 190,
            cx - 220, cy - 90,
            cx - 150, cy - 70,
            cx - 120, cy + 170,
            cx + 120, cy + 170,
            cx + 150, cy - 70,
            cx + 220, cy - 90,
            cx + 140, cy - 190,
            cx + 60, cy - 165,
            cx + 25, cy - 205,
            cx - 25, cy - 205,
            cx - 60, cy - 165,
            fill="#2563EB", outline="#1D4ED8", width=3,
        )
        c.create_polygon(cx - 220, cy - 90, cx - 260, cy + 30, cx - 190, cy + 48, cx - 150, cy - 70, fill="#1E40AF", outline="")
        c.create_polygon(cx + 220, cy - 90, cx + 260, cy + 30, cx + 190, cy + 48, cx + 150, cy - 70, fill="#1E40AF", outline="")
        c.create_polygon(cx - 126, cy - 185, cx - 180, cy - 120, cx - 150, cy - 112, cx - 80, cy - 168, fill="#FACC15", outline="")
        c.create_polygon(cx + 126, cy - 185, cx + 180, cy - 120, cx + 150, cy - 112, cx + 80, cy - 168, fill="#FACC15", outline="")
        c.create_rectangle(cx - 120, cy + 15, cx + 120, cy + 45, fill="#93C5FD", outline="", stipple="gray50")
        c.create_text(cx + 70, cy - 85, text="LOGO", fill="#BAE6FD", font=("Segoe UI", 18, "bold"))

    def _show_generated_image(self, path: str):
        try:
            self.generated_photo = tk.PhotoImage(file=path)
            self.mockup_canvas.delete("all")
            self.mockup_canvas.create_image(10, 10, anchor="nw", image=self.generated_photo)
        except Exception:
            self._draw_mockup_placeholder()
            self._log(f"Imagem salva em: {path} (preview PNG/JPG pode exigir Pillow para render no Tk).")

    def _log(self, message: str):
        self.console.insert("end", message + "\n")
        self.console.see("end")

    def _briefing(self) -> UniformBriefing:
        return UniformBriefing(
            segmento=self.segmento_entry.get().strip(),
            cores=self.cores_entry.get().strip(),
            detalhes=self.detalhes_entry.get().strip(),
            cor_hex=self.selected_hex.get().strip(),
            logo_proporcao="10x8 cm",
            tamanho_mockup=self.mockup_size_var.get().strip(),
            tamanho_camiseta=self.tamanho_camiseta_var.get().strip(),
            modelo_camiseta=self.modelo_camiseta_var.get().strip(),
            aplicacao_lado=self.aplicacao_lado_var.get().strip(),
            modelagem=self.modelagem_var.get().strip(),
            tecnica_impressao=self.tecnica_var.get().strip(),
        )

    def _validate_form(self):
        if not self.api_key:
            return False, "Conecte a API Key Gemini primeiro."
        if not self.model_var.get().strip():
            return False, "Selecione uma versão da IA no dropdown."
        if not self.segmento_entry.get().strip() or not self.cores_entry.get().strip() or not self.detalhes_entry.get().strip():
            return False, "Preencha briefing (segmento, cores e detalhes)."
        if not self.logo_file:
            return False, "Importe a logo antes de gerar mockup."
        return True, "OK"

    def connect_api(self):
        key = self.api_key_entry.get().strip()
        self._log("Validando API Key Gemini...")
        ok, msg, models = validate_gemini_key(key)
        if not ok:
            self._log(f"Falha: {msg}")
            messagebox.showerror("API Login", msg)
            return

        self.api_key = key
        self.available_models = models
        self._refresh_model_dropdown(models)
        self._log("API conectada. Modelos carregados com sucesso.")

    def _refresh_model_dropdown(self, models):
        menu = self.model_dropdown["menu"]
        menu.delete(0, "end")
        if not models:
            self.model_var.set("")
            return
        self.model_var.set(models[0])
        for m in models:
            menu.add_command(label=m, command=lambda v=m: self.model_var.set(v))

    def pick_color_from_gradient(self, event):
        width = max(self.color_canvas.winfo_width(), 1)
        hue = max(0, min(event.x / width, 1))
        import colorsys

        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.9)
        hex_color = f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"
        self.selected_hex.set(hex_color)
        self.hex_entry.delete(0, "end")
        self.hex_entry.insert(0, hex_color)

    def confirmar_cor(self):
        cor = self.hex_entry.get().strip() or "#1E73BE"
        self.selected_hex.set(cor)
        self._log(f"Cor confirmada: {cor}")

    def selecionar_logo(self):
        path = filedialog.askopenfilename(
            title="Selecione a logo",
            filetypes=[("Imagens", "*.svg *.png *.jpg *.jpeg")],
        )
        if path:
            self.logo_file = path
            self.logo_name.configure(text=os.path.basename(path))
            self._log(f"Logo carregada: {os.path.basename(path)}")

    def gerar_mockup(self):
        ok, msg = self._validate_form()
        if not ok:
            messagebox.showwarning("Validação", msg)
            self._log(f"Validação: {msg}")
            return

        briefing = self._briefing()
        prompt = build_creation_prompt(briefing)

        self.prompt_info.delete("1.0", "end")
        self.prompt_info.insert("1.0", (
            f"Segmento: {briefing.segmento}\n"
            f"Cor: {briefing.cores} / {briefing.cor_hex}\n"
            f"Logo: carregada\n"
            f"Modelo: {briefing.modelo_camiseta}\n"
            f"Lado: {briefing.aplicacao_lado}\n"
            f"Método: {briefing.tecnica_impressao}"
        ))

        self.ficha_text.delete("1.0", "end")
        self.ficha_text.insert("1.0", (
            f"- Tamanho Mockup: {briefing.tamanho_mockup}\n"
            f"- Tamanho Camiseta: {briefing.tamanho_camiseta}\n"
            f"- Modelo: {briefing.modelo_camiseta}\n"
            f"- Aplicação: {briefing.aplicacao_lado}\n"
            f"- Método: {briefing.tecnica_impressao}\n"
            f"- Regra: logo original sem alteração"
        ))

        self._log("Gerando prompt...")
        self._log("Enviando para Gemini (imagem)...")

        try:
            image_path, summary = generate_layout_image_with_gemini(
                self.api_key,
                self.model_var.get().strip(),
                prompt,
                self.logo_file,
            )
        except Exception as exc:
            self._log(f"Falha na geração de imagem: {exc}")
            messagebox.showerror("Gerar Mockup", str(exc))
            return

        if image_path:
            self.generated_image_path = image_path
            self._show_generated_image(image_path)
            self._log("Mockup gerado com sucesso.")
            if summary:
                self._log(summary)
        else:
            self._draw_mockup_placeholder()
            self._log("Modelo não retornou imagem. Mantendo preview padrão.")
            self._log(summary)

    def enviar_para_gpt(self):
        ok, msg = self._validate_form()
        if not ok:
            messagebox.showwarning("Validação", msg)
            return

        briefing = self._briefing()
        prompt = build_creation_prompt(briefing)
        self._log("Enviando prompt textual para Gemini...")
        try:
            text = generate_with_gemini(self.api_key, self.model_var.get().strip(), prompt, self.logo_file)
        except Exception as exc:
            self._log(f"Erro envio texto: {exc}")
            messagebox.showerror("Enviar para GPT", str(exc))
            return

        self._log("Resposta textual recebida.")
        self._log(text)

    def exportar_ficha(self):
        content = self.ficha_text.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("Exportar", "Ficha técnica vazia.")
            return

        path = filedialog.asksaveasfilename(
            title="Salvar Ficha Técnica",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
            initialfile="ficha_tecnica_uniforme.txt",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self._log(f"Ficha exportada: {path}")
        messagebox.showinfo("Exportar", "Ficha técnica exportada com sucesso.")

    def novo_projeto(self):
        self.segmento_entry.delete(0, "end")
        self.cores_entry.delete(0, "end")
        self.detalhes_entry.delete(0, "end")
        self.logo_file = None
        self.logo_name.configure(text="Nenhum arquivo selecionado")
        self.prompt_info.delete("1.0", "end")
        self.ficha_text.delete("1.0", "end")
        self.ficha_text.insert("1.0", "- Tamanho: TBU\n- Peito: 56 cm\n- Comprimento: 72 cm\n- Método: Sublimação")
        self._draw_mockup_placeholder()
        self._log("Novo projeto iniciado.")

    def salvar_projeto(self):
        data = {
            "segmento": self.segmento_entry.get().strip(),
            "cores": self.cores_entry.get().strip(),
            "detalhes": self.detalhes_entry.get().strip(),
            "hex": self.selected_hex.get().strip(),
            "modelo": self.modelo_camiseta_var.get().strip(),
            "tamanho_mockup": self.mockup_size_var.get().strip(),
            "tamanho_camiseta": self.tamanho_camiseta_var.get().strip(),
            "lado": self.aplicacao_lado_var.get().strip(),
            "tecnica": self.tecnica_var.get().strip(),
            "modelagem": self.modelagem_var.get().strip(),
            "logo": self.logo_file or "",
        }
        path = filedialog.asksaveasfilename(
            title="Salvar Projeto",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
            initialfile="projeto_uniforme.txt",
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            for k, v in data.items():
                f.write(f"{k}: {v}\n")

        self._log(f"Projeto salvo: {path}")
        messagebox.showinfo("Salvar", "Projeto salvo com sucesso.")


def main():
    root = tk.Tk()
    app = UniformAgentApp(root)
    app.mockup_canvas.bind("<Configure>", lambda _e: app._draw_mockup_placeholder())
    root.mainloop()


if __name__ == "__main__":
    main()
