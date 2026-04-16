import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
from datetime import datetime

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

MONTHS_RU = [
    "", "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря"
]

DEFAULT_CONFIG = {
    "position_fio": "",
    "signature": "",
    "fio_short": ""
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class RaportApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Конструктор рапорта ОСБ")
        self.resizable(True, True)
        self.configure(bg="#f0f0f0")
        self.minsize(800, 700)

        self.config_data = load_config()
        self.attachment_rows = []   # list of (frame, name_var, url_var)

        self._build_ui()
        self._load_config_to_form()

    # ─────────────────────────── UI ───────────────────────────
    def _build_ui(self):
        main = tk.Frame(self, bg="#f0f0f0")
        main.pack(fill="both", expand=True, padx=12, pady=8)

        # ── БЛОК НАСТРОЕК ──────────────────────────────────────
        cfg_frame = tk.LabelFrame(main, text=" Настройки (сохраняются в файл) ",
                                  bg="#f0f0f0", font=("Segoe UI", 9, "bold"), padx=6, pady=4)
        cfg_frame.pack(fill="x", pady=(0, 6))

        tk.Label(cfg_frame, text="Должность и ФИО полностью:", bg="#f0f0f0",
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.var_position_fio = tk.StringVar()
        tk.Entry(cfg_frame, textvariable=self.var_position_fio, width=55,
                 font=("Segoe UI", 9)).grid(row=0, column=1, sticky="we", padx=4, pady=2)

        # Строка 1: кнопка сохранить | Подпись | ФИО кратко
        row1_cfg = tk.Frame(cfg_frame, bg="#f0f0f0")
        row1_cfg.grid(row=1, column=0, columnspan=2, sticky="we", padx=4, pady=2)

        tk.Button(row1_cfg, text="💾 Сохранить", command=self._save_config,
                  bg="#4CAF50", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=6, pady=2).pack(side="left", padx=(0, 10))

        tk.Label(row1_cfg, text="Подпись:", bg="#f0f0f0",
                 font=("Segoe UI", 9)).pack(side="left")
        self.var_signature = tk.StringVar()
        tk.Entry(row1_cfg, textvariable=self.var_signature, width=18,
                 font=("Segoe UI", 9)).pack(side="left", padx=(2, 10))

        tk.Label(row1_cfg, text="ФИО для подписи:", bg="#f0f0f0",
                 font=("Segoe UI", 9)).pack(side="left")
        self.var_fio_short = tk.StringVar()
        tk.Entry(row1_cfg, textvariable=self.var_fio_short, font=("Segoe UI", 9),
                 width=24).pack(side="left", padx=(2, 0))

        cfg_frame.columnconfigure(1, weight=1)

        # ── СКРОЛЛИРУЕМАЯ ОБЛАСТЬ С ПОЛЯМИ ─────────────────────
        canvas_outer = tk.Frame(main, bg="#f0f0f0")
        canvas_outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_outer, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.form_frame = tk.Frame(canvas, bg="#f0f0f0")
        self.canvas_window = canvas.create_window((0, 0), window=self.form_frame,
                                                   anchor="nw")

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_resize(e):
            canvas.itemconfig(self.canvas_window, width=e.width)

        self.form_frame.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # ── ПОЛЯ РАПОРТА ───────────────────────────────────────
        ff = self.form_frame

        def _label(text, row):
            tk.Label(ff, text=text, bg="#f0f0f0",
                     font=("Segoe UI", 9, "bold")).grid(row=row, column=0,
                                                         sticky="nw", padx=6, pady=(8, 0))

        def _textarea(row, height=4):
            t = scrolledtext.ScrolledText(ff, height=height, font=("Segoe UI", 9),
                                          wrap="word", relief="solid", bd=1)
            t.grid(row=row, column=0, sticky="we", padx=6, pady=(2, 0))
            return t

        def _entry(row):
            e = tk.Entry(ff, font=("Segoe UI", 9), relief="solid", bd=1)
            e.grid(row=row, column=0, sticky="we", padx=6, pady=(2, 0))
            return e

        _label("О чем (нарушении устава ОВД, нарушении законодательства)", 0)
        self.entry_subject = _entry(1)

        _label("Основание рапорта (подробно: дата, суть, ссылки на законы):", 2)
        self.text_basis = _textarea(3, 6)

        _label("Прошу руководство ГУ МВД:", 4)
        self.text_request = _textarea(5, 3)

        # ── ПРИЛОЖЕНИЯ ─────────────────────────────────────────
        att_outer = tk.LabelFrame(ff, text=" Приложения ", bg="#f0f0f0",
                                  font=("Segoe UI", 9, "bold"), padx=6, pady=6)
        att_outer.grid(row=6, column=0, sticky="we", padx=6, pady=(10, 0))
        att_outer.columnconfigure(0, weight=1)

        # Фиксированное — USB-Flash
        usb_row = tk.Frame(att_outer, bg="#f0f0f0")
        usb_row.pack(fill="x", pady=2)
        tk.Label(usb_row, text="Перенос доказательств на USB-Flash — URL:",
                 bg="#f0f0f0", font=("Segoe UI", 9)).pack(side="left")
        self.var_usb_url = tk.StringVar()
        tk.Entry(usb_row, textvariable=self.var_usb_url, font=("Segoe UI", 9),
                 relief="solid", bd=1, width=40).pack(side="left", fill="x",
                                                       expand=True, padx=(6, 0))

        # Динамический список ссылок (фото/видео)
        tk.Label(att_outer, text="Фото/видео фиксации:", bg="#f0f0f0",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 0))

        self.att_container = tk.Frame(att_outer, bg="#f0f0f0")
        self.att_container.pack(fill="x")
        self.att_container.columnconfigure(1, weight=1)
        self.att_container.columnconfigure(3, weight=1)

        btn_row = tk.Frame(att_outer, bg="#f0f0f0")
        btn_row.pack(anchor="w", pady=(4, 0))
        tk.Button(btn_row, text="  +  Добавить", command=self._add_attachment,
                  bg="#2196F3", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=6, pady=2).pack(side="left", padx=(0, 4))
        tk.Button(btn_row, text="  −  Удалить последнее", command=self._remove_last_attachment,
                  bg="#f44336", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=6, pady=2).pack(side="left")

        # Добавим одну строку по умолчанию
        self._add_attachment()

        ff.columnconfigure(0, weight=1)

        # ── КНОПКА ГЕНЕРАЦИИ ───────────────────────────────────
        gen_frame = tk.Frame(main, bg="#f0f0f0")
        gen_frame.pack(fill="x", pady=(10, 4))

        tk.Button(gen_frame, text="Сгенерировать BB-код",
                  command=self._generate,
                  bg="#FF9800", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=8, pady=3).pack(side="left")

        tk.Button(gen_frame, text="Скопировать в буфер",
                  command=self._copy_to_clipboard,
                  bg="#9C27B0", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=8, pady=3).pack(side="left", padx=(6, 0))

        tk.Button(gen_frame, text="Очистить вывод",
                  command=self._clear_output,
                  bg="#607D8B", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=8, pady=3).pack(side="left", padx=(6, 0))

        # ── ВЫВОД BB-КОДА ──────────────────────────────────────
        out_frame = tk.LabelFrame(main, text=" Готовый BB-код (для вставки на форум) ",
                                  bg="#f0f0f0", font=("Segoe UI", 9, "bold"),
                                  padx=6, pady=6)
        out_frame.pack(fill="both", expand=False, pady=(0, 4))

        self.output_text = scrolledtext.ScrolledText(
            out_frame, height=7, font=("Courier New", 9),
            wrap="none", relief="solid", bd=1, bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white"
        )
        self.output_text.pack(fill="both", expand=True)

    # ─────────────────── ВЛОЖЕНИЯ ──────────────────────────────
    def _add_attachment(self):
        idx = len(self.attachment_rows)
        row_frame = tk.Frame(self.att_container, bg="#f0f0f0")
        row_frame.pack(fill="x", pady=1)

        num_label = tk.Label(row_frame, text=f"{idx + 1}.", bg="#f0f0f0",
                             font=("Segoe UI", 9), width=3, anchor="e")
        num_label.pack(side="left")

        tk.Label(row_frame, text="Название:", bg="#f0f0f0",
                 font=("Segoe UI", 9)).pack(side="left", padx=(2, 2))
        name_var = tk.StringVar(value=f"Доказательства №{idx + 1}")
        name_entry = tk.Entry(row_frame, textvariable=name_var, width=22,
                              font=("Segoe UI", 9), relief="solid", bd=1)
        name_entry.pack(side="left", padx=(0, 4))

        tk.Label(row_frame, text="URL:", bg="#f0f0f0",
                 font=("Segoe UI", 9)).pack(side="left")
        url_var = tk.StringVar()
        url_entry = tk.Entry(row_frame, textvariable=url_var, font=("Segoe UI", 9),
                             relief="solid", bd=1)
        url_entry.pack(side="left", fill="x", expand=True, padx=(4, 0))

        self.attachment_rows.append((row_frame, name_var, url_var))

    def _remove_last_attachment(self):
        if not self.attachment_rows:
            return
        row_frame, _, _ = self.attachment_rows.pop()
        row_frame.destroy()

    # ─────────────────── КОНФИГ ────────────────────────────────
    def _load_config_to_form(self):
        self.var_position_fio.set(self.config_data.get("position_fio", ""))
        self.var_signature.set(self.config_data.get("signature", ""))
        self.var_fio_short.set(self.config_data.get("fio_short", ""))

    def _save_config(self):
        self.config_data["position_fio"] = self.var_position_fio.get().strip()
        self.config_data["signature"] = self.var_signature.get().strip()
        self.config_data["fio_short"] = self.var_fio_short.get().strip()
        save_config(self.config_data)
        messagebox.showinfo("Сохранено", "Настройки успешно сохранены.")

    # ─────────────────── ГЕНЕРАЦИЯ ─────────────────────────────
    def _generate(self):
        position_fio = self.var_position_fio.get().strip() or "[Должность и ФИО не указаны]"
        signature = self.var_signature.get().strip() or "________________"
        fio_short = self.var_fio_short.get().strip() or "[ФИО]"

        subject = self.entry_subject.get().strip() or "[суть нарушения не указана]"
        basis = self.text_basis.get("1.0", "end").strip() or "[основание не указано]"
        request = self.text_request.get("1.0", "end").strip() or "[требования не указаны]"

        # Дата
        now = datetime.now()
        day = str(now.day)
        month = MONTHS_RU[now.month]
        year2 = str(now.year)[2:]   # последние 2 цифры для "20XX г."
        year_full = str(now.year)

        # ── Приложения ──────────────────────────────────────────
        att_lines = []

        usb_url = self.var_usb_url.get().strip()
        for _frame, name_var, url_var in self.attachment_rows:
            name = name_var.get().strip()
            url = url_var.get().strip()
            if name and url:
                att_lines.append(f"[URL={url}]{name}[/URL]")
            elif name:
                att_lines.append(f"{name} — [ссылка не указана]")
        if usb_url:
            att_lines.append(
                f"[URL={usb_url}]Перенос доказательств на USB-Flash[/URL]"
            )
        else:
            att_lines.append("Перенос доказательств на USB-Flash — [ссылка не указана]")



        attachments_bb = "\n".join(att_lines)

        # ── BB-код ───────────────────────────────────────────────
        bb = (
            f"[RIGHT][SIZE=15px][FONT=Times New Roman]"
            f"Руководству ГУ МВД по Нижегородской области"
            f"[/FONT][/SIZE]\n"
            f"[FONT=Times New Roman][SIZE=15px]от {position_fio}[/SIZE][/FONT]\n"
            f"[/RIGHT]\n"
            f"[HEADING=2][CENTER][FONT=Times New Roman][SIZE=15px]"
            f"[B]РАПОРТ О ДИСЦИПЛИНАРНОМ ПРОСТУПКЕ[/B]"
            f"[/SIZE][/FONT][/CENTER][/HEADING]\n"
            f"[CENTER][FONT=Times New Roman][SIZE=15px]о {subject}[/SIZE][/FONT]\n"
            f"[/CENTER]\n"
            f"[FONT=Times New Roman][SIZE=15px][B]Основание рапорта: [/B]"
            f"{basis}[/SIZE][/FONT]\n"
            f"[RIGHT][/RIGHT]\n"
            f"[FONT=Times New Roman][SIZE=15px][FONT=Times New Roman][SIZE=15px]"
            f"[B]Прошу руководство ГУ МВД: [/B]{request}"
            f"[/SIZE][/FONT][/SIZE][/FONT]\n"
            f"[RIGHT][/RIGHT]\n"
            f"[FONT=Times New Roman][SIZE=15px][FONT=Times New Roman][SIZE=15px]"
            f"[B]Приложения:[/B]\n"
            f"{attachments_bb}"
            f"[/SIZE][/FONT][/SIZE][/FONT]\n"
            f"[RIGHT]\n"
            f"[FONT=Times New Roman][SIZE=15px][FONT=Times New Roman][SIZE=15px]"
            f"Дата: «{day}[B]» {month} [/B]{year_full} г.[/SIZE][/FONT]\n"
            f"[SIZE=15px][FONT=Times New Roman]"
            f"Подпись: {signature} / {fio_short}"
            f"[/FONT][/SIZE][/SIZE][/FONT]\n"
            f"[/RIGHT]"
        )

        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", bb)

    def _copy_to_clipboard(self):
        content = self.output_text.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("Буфер обмена", "Сначала сгенерируйте BB-код.")
            return
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Скопировано", "BB-код скопирован в буфер обмена.")

    def _clear_output(self):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")


if __name__ == "__main__":
    app = RaportApp()
    app.mainloop()
