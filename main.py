from __future__ import annotations

import math
import os
import re
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

try:
    from pypdf import PdfReader, PdfWriter
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "A biblioteca 'pypdf' não está instalada.\n"
        "Instale com: pip install pypdf"
    ) from exc


APP_TITLE = "Robô Divisor de PDF"


def resource_path(relative_path: str) -> Path:
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_dir / relative_path


def configure_tk_environment() -> None:
    tcl_dir = resource_path("_tcl_data")
    tk_dir = resource_path("_tk_data")

    if tcl_dir.exists():
        os.environ.setdefault("TCL_LIBRARY", str(tcl_dir))
    if tk_dir.exists():
        os.environ.setdefault("TK_LIBRARY", str(tk_dir))


configure_tk_environment()

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


@dataclass
class SplitResult:
    output_files: List[Path]
    details: str


def sanitize_filename(name: str) -> str:
    name = name.strip()
    if not name:
        return "arquivo"
    name = re.sub(r'[\\/*?:\"<>|]+', '_', name)
    name = re.sub(r'\s+', '_', name)
    return name[:150]


def ensure_output_dir(base_pdf: Path, output_dir: str | None) -> Path:
    if output_dir and output_dir.strip():
        out = Path(output_dir).expanduser().resolve()
    else:
        out = base_pdf.with_name(f"{base_pdf.stem}_dividido")
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_pdf(reader: PdfReader, page_indices: List[int], output_path: Path) -> None:
    writer = PdfWriter()
    for idx in page_indices:
        writer.add_page(reader.pages[idx])
    with output_path.open("wb") as f:
        writer.write(f)


def split_one_per_page(pdf_path: Path, output_dir: Path, base_name: str) -> SplitResult:
    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    width = max(3, len(str(total_pages)))
    files: List[Path] = []

    for i in range(total_pages):
        output = output_dir / f"{sanitize_filename(base_name)}_{i + 1:0{width}d}.pdf"
        write_pdf(reader, [i], output)
        files.append(output)

    return SplitResult(files, f"PDF dividido em {total_pages} arquivos, um por página.")


def split_every_n_pages(pdf_path: Path, output_dir: Path, base_name: str, pages_per_file: int) -> SplitResult:
    if pages_per_file <= 0:
        raise ValueError("A quantidade de páginas por arquivo deve ser maior que zero.")

    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    total_files = math.ceil(total_pages / pages_per_file)
    width = max(3, len(str(total_files)))
    files: List[Path] = []

    file_no = 1
    for start in range(0, total_pages, pages_per_file):
        end = min(start + pages_per_file, total_pages)
        output = output_dir / f"{sanitize_filename(base_name)}_{file_no:0{width}d}_pag_{start + 1}_a_{end}.pdf"
        write_pdf(reader, list(range(start, end)), output)
        files.append(output)
        file_no += 1

    return SplitResult(files, f"PDF dividido em {len(files)} arquivos com até {pages_per_file} páginas cada.")


def parse_ranges(ranges_text: str, total_pages: int) -> List[Tuple[int, int]]:
    """
    Recebe texto como: 1-3, 4-8, 9, 10-12
    Retorna lista de tuplas zero-based: [(0,2), (3,7), ...]
    """
    if not ranges_text.strip():
        raise ValueError("Informe os intervalos de páginas.")

    ranges: List[Tuple[int, int]] = []
    parts = [p.strip() for p in ranges_text.split(",") if p.strip()]

    for part in parts:
        if "-" in part:
            a_text, b_text = [x.strip() for x in part.split("-", 1)]
            if not a_text.isdigit() or not b_text.isdigit():
                raise ValueError(f"Intervalo inválido: {part}")
            a, b = int(a_text), int(b_text)
        else:
            if not part.isdigit():
                raise ValueError(f"Página inválida: {part}")
            a = b = int(part)

        if a < 1 or b < 1:
            raise ValueError(f"Páginas devem começar em 1: {part}")
        if a > b:
            raise ValueError(f"Intervalo invertido: {part}")
        if b > total_pages:
            raise ValueError(
                f"O intervalo {part} ultrapassa o total de páginas do PDF ({total_pages})."
            )

        ranges.append((a - 1, b - 1))

    return ranges


def split_custom_ranges(pdf_path: Path, output_dir: Path, base_name: str, ranges_text: str) -> SplitResult:
    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    ranges = parse_ranges(ranges_text, total_pages)
    width = max(3, len(str(len(ranges))))
    files: List[Path] = []

    for idx, (start, end) in enumerate(ranges, start=1):
        output = output_dir / (
            f"{sanitize_filename(base_name)}_{idx:0{width}d}_pag_{start + 1}_a_{end + 1}.pdf"
        )
        write_pdf(reader, list(range(start, end + 1)), output)
        files.append(output)

    return SplitResult(files, f"PDF dividido em {len(files)} arquivos pelos intervalos informados.")


def extract_page_text(page) -> str:
    try:
        text = page.extract_text() or ""
    except Exception:
        text = ""
    return text


def split_by_keyword(pdf_path: Path, output_dir: Path, base_name: str, keyword: str) -> SplitResult:
    keyword = keyword.strip()
    if not keyword:
        raise ValueError("Informe a palavra-chave.")

    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    normalized_keyword = keyword.casefold()

    hit_pages: List[int] = []
    for i, page in enumerate(reader.pages):
        text = extract_page_text(page)
        if normalized_keyword in text.casefold():
            hit_pages.append(i)

    if not hit_pages:
        raise ValueError(
            "Nenhuma página com a palavra-chave foi encontrada.\n\n"
            "Observação: esse modo funciona melhor em PDFs de texto. Se o PDF for imagem/escaneado, será preciso OCR."
        )

    files: List[Path] = []
    chunks: List[Tuple[int, int, str]] = []

    if hit_pages[0] > 0:
        chunks.append((0, hit_pages[0] - 1, "antes_da_palavra_chave"))

    for idx, start in enumerate(hit_pages):
        end = hit_pages[idx + 1] - 1 if idx + 1 < len(hit_pages) else total_pages - 1
        chunks.append((start, end, f"{idx + 1:03d}"))

    for start, end, suffix in chunks:
        output = output_dir / f"{sanitize_filename(base_name)}_{suffix}_pag_{start + 1}_a_{end + 1}.pdf"
        write_pdf(reader, list(range(start, end + 1)), output)
        files.append(output)

    details = (
        f"PDF dividido em {len(files)} arquivos com base na palavra-chave '{keyword}'.\n"
        f"Páginas com ocorrência: {', '.join(str(i + 1) for i in hit_pages)}"
    )
    return SplitResult(files, details)


class PdfSplitterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("760x620")
        self.root.minsize(700, 560)

        self.pdf_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.base_name_var = tk.StringVar(value="arquivo_dividido")
        self.mode_var = tk.StringVar(value="one_per_page")
        self.pages_per_file_var = tk.StringVar(value="1")
        self.ranges_var = tk.StringVar(value="1-3, 4-6")
        self.keyword_var = tk.StringVar(value="Unidade")

        self._build_ui()
        self._refresh_mode_help()

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill="both", expand=True)

        title = ttk.Label(main, text="Divisor local de PDF", font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w")

        subtitle = ttk.Label(
            main,
            text="Sem upload, sem limite artificial de tamanho. O processamento roda no seu computador.",
            wraplength=700,
        )
        subtitle.pack(anchor="w", pady=(4, 14))

        file_frame = ttk.LabelFrame(main, text="1) Arquivos", padding=12)
        file_frame.pack(fill="x", pady=(0, 10))

        self._build_path_row(file_frame, "PDF de entrada:", self.pdf_path_var, self.select_pdf)
        self._build_path_row(file_frame, "Pasta de saída:", self.output_dir_var, self.select_output_dir)

        name_row = ttk.Frame(file_frame)
        name_row.pack(fill="x", pady=(8, 0))
        ttk.Label(name_row, text="Nome base dos arquivos:", width=22).pack(side="left")
        ttk.Entry(name_row, textvariable=self.base_name_var).pack(side="left", fill="x", expand=True)

        mode_frame = ttk.LabelFrame(main, text="2) Modo de divisão", padding=12)
        mode_frame.pack(fill="x", pady=(0, 10))

        options = [
            ("Um arquivo por página", "one_per_page"),
            ("A cada X páginas", "every_n"),
            ("Por intervalos personalizados", "custom_ranges"),
            ("Por palavra-chave", "keyword"),
        ]

        for text, value in options:
            ttk.Radiobutton(
                mode_frame,
                text=text,
                value=value,
                variable=self.mode_var,
                command=self._refresh_mode_help,
            ).pack(anchor="w", pady=2)

        config_frame = ttk.LabelFrame(main, text="3) Configuração", padding=12)
        config_frame.pack(fill="x", pady=(0, 10))

        row1 = ttk.Frame(config_frame)
        row1.pack(fill="x", pady=4)
        ttk.Label(row1, text="Páginas por arquivo:", width=22).pack(side="left")
        ttk.Entry(row1, textvariable=self.pages_per_file_var).pack(side="left", fill="x", expand=True)

        row2 = ttk.Frame(config_frame)
        row2.pack(fill="x", pady=4)
        ttk.Label(row2, text="Intervalos:", width=22).pack(side="left")
        ttk.Entry(row2, textvariable=self.ranges_var).pack(side="left", fill="x", expand=True)

        row3 = ttk.Frame(config_frame)
        row3.pack(fill="x", pady=4)
        ttk.Label(row3, text="Palavra-chave:", width=22).pack(side="left")
        ttk.Entry(row3, textvariable=self.keyword_var).pack(side="left", fill="x", expand=True)

        self.help_label = ttk.Label(
            config_frame,
            text="",
            foreground="#333333",
            wraplength=680,
            justify="left",
        )
        self.help_label.pack(anchor="w", pady=(10, 0))

        action_frame = ttk.Frame(main)
        action_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(action_frame, text="Dividir PDF", command=self.run_split).pack(side="left")
        ttk.Button(action_frame, text="Abrir pasta de saída", command=self.open_output_dir).pack(side="left", padx=8)
        ttk.Button(action_frame, text="Fechar", command=self.root.destroy).pack(side="right")

        log_frame = ttk.LabelFrame(main, text="Resultado", padding=10)
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_frame, height=16, wrap="word")
        self.log_text.pack(fill="both", expand=True)
        self.log("Pronto. Selecione um PDF e escolha o modo de divisão.")

    def _build_path_row(self, parent, label_text: str, variable: tk.StringVar, command) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label_text, width=22).pack(side="left")
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Selecionar", command=command).pack(side="left", padx=(8, 0))

    def _refresh_mode_help(self) -> None:
        mode = self.mode_var.get()
        helps = {
            "one_per_page": "Cria um PDF para cada página do arquivo original.",
            "every_n": "Divide o PDF em blocos. Exemplo: 5 páginas por arquivo.",
            "custom_ranges": "Use intervalos separados por vírgula. Exemplo: 1-3, 4-8, 9, 10-12.",
            "keyword": "Inicia um novo arquivo sempre que encontrar a palavra-chave em uma página. Ideal para PDFs de texto; PDFs escaneados podem exigir OCR.",
        }
        self.help_label.config(text=helps.get(mode, ""))

    def select_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione o PDF",
            filetypes=[("PDF", "*.pdf")],
        )
        if path:
            self.pdf_path_var.set(path)
            if not self.output_dir_var.get().strip():
                self.output_dir_var.set(str(Path(path).with_name(f"{Path(path).stem}_dividido")))
            if self.base_name_var.get().strip() in {"", "arquivo_dividido"}:
                self.base_name_var.set(Path(path).stem)

    def select_output_dir(self) -> None:
        path = filedialog.askdirectory(title="Selecione a pasta de saída")
        if path:
            self.output_dir_var.set(path)

    def open_output_dir(self) -> None:
        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showwarning(APP_TITLE, "Escolha ou gere uma pasta de saída primeiro.")
            return

        path = Path(output_dir)
        if not path.exists():
            messagebox.showwarning(APP_TITLE, "A pasta de saída ainda não existe.")
            return

        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Não foi possível abrir a pasta.\n\n{exc}")

    def log(self, message: str) -> None:
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.root.update_idletasks()

    def run_split(self) -> None:
        pdf_path_text = self.pdf_path_var.get().strip()
        if not pdf_path_text:
            messagebox.showwarning(APP_TITLE, "Selecione um PDF de entrada.")
            return

        pdf_path = Path(pdf_path_text)
        if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
            messagebox.showwarning(APP_TITLE, "O arquivo informado não é um PDF válido.")
            return

        base_name = self.base_name_var.get().strip() or pdf_path.stem
        output_dir = ensure_output_dir(pdf_path, self.output_dir_var.get().strip())
        self.output_dir_var.set(str(output_dir))

        self.log("-" * 80)
        self.log(f"Processando: {pdf_path}")
        self.log(f"Saída: {output_dir}")

        try:
            mode = self.mode_var.get()

            if mode == "one_per_page":
                result = split_one_per_page(pdf_path, output_dir, base_name)
            elif mode == "every_n":
                pages_per_file = int(self.pages_per_file_var.get().strip())
                result = split_every_n_pages(pdf_path, output_dir, base_name, pages_per_file)
            elif mode == "custom_ranges":
                result = split_custom_ranges(pdf_path, output_dir, base_name, self.ranges_var.get())
            elif mode == "keyword":
                result = split_by_keyword(pdf_path, output_dir, base_name, self.keyword_var.get())
            else:
                raise ValueError("Modo de divisão inválido.")

            self.log(result.details)
            self.log("Arquivos gerados:")
            for file_path in result.output_files[:20]:
                self.log(f"  - {file_path.name}")
            if len(result.output_files) > 20:
                self.log(f"  ... e mais {len(result.output_files) - 20} arquivo(s)")

            messagebox.showinfo(
                APP_TITLE,
                f"Concluído com sucesso.\n\n{result.details}\n\nPasta: {output_dir}",
            )
        except Exception as exc:
            self.log(f"ERRO: {exc}")
            self.log(traceback.format_exc())
            messagebox.showerror(APP_TITLE, f"Erro ao dividir o PDF.\n\n{exc}")


def main() -> None:
    root = tk.Tk()
    icon_path = resource_path("pdf.ico")
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
        except Exception:
            pass
    style = ttk.Style()
    try:
        style.theme_use("vista")
    except Exception:
        pass
    PdfSplitterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
