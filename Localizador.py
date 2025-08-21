import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading


class FileLocatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Localizador e Copiador de Arquivos")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        self.search_path = tk.StringVar()
        self.dest_path = tk.StringVar()
        self.search_term = tk.StringVar()
        self.all_files = []
        self.found_files = []
        main_frame = tk.Frame(root, padx=15, pady=15, bg="#f0f0f0")
        main_frame.pack(expand=True, fill=tk.BOTH)

        controls_frame = tk.Frame(main_frame, bg="#f0f0f0")
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(controls_frame, text="1. Escolha a pasta para carregar os arquivos:", font=("Helvetica", 10, "bold"),
                 bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=2)
        entry_search = tk.Entry(controls_frame, textvariable=self.search_path, width=70, state='readonly')
        entry_search.grid(row=1, column=0, padx=(0, 10), sticky="we")
        self.btn_select_source = tk.Button(controls_frame, text="Selecionar Pasta",
                                           command=self.select_search_path_and_preload)
        self.btn_select_source.grid(row=1, column=1, sticky="ew")

        tk.Label(controls_frame, text="2. Digite o termo para filtrar (em pastas ou arquivos):",
                 font=("Helvetica", 10, "bold"), bg="#f0f0f0").grid(row=2, column=0, sticky="w", pady=(10, 2))
        entry_term = tk.Entry(controls_frame, textvariable=self.search_term, width=70)
        entry_term.grid(row=3, column=0, padx=(0, 10), sticky="we")
        entry_term.bind("<KeyRelease>", self.start_filter_thread)
        tk.Label(controls_frame, text="3. Escolha a pasta para salvar as cópias:", font=("Helvetica", 10, "bold"),
                 bg="#f0f0f0").grid(row=4, column=0, sticky="w", pady=(10, 2))
        entry_dest = tk.Entry(controls_frame, textvariable=self.dest_path, width=70, state='readonly')
        entry_dest.grid(row=5, column=0, padx=(0, 10), sticky="we")
        btn_dest_path = tk.Button(controls_frame, text="Selecionar Pasta", command=self.select_dest_path)
        btn_dest_path.grid(row=5, column=1, sticky="ew")
        controls_frame.grid_columnconfigure(0, weight=1)

        action_frame = tk.Frame(main_frame, bg="#f0f0f0")
        action_frame.pack(fill=tk.X, pady=10)

        self.btn_filter = tk.Button(action_frame, text="🔍 Filtrar", font=("Helvetica", 12, "bold"), bg="#007bff",
                                    fg="white", command=self.start_filter_thread, state=tk.DISABLED)
        self.btn_filter.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.btn_copy = tk.Button(action_frame, text="📋 Copiar Arquivos Filtrados", font=("Helvetica", 12, "bold"),
                                  bg="#28a745", fg="white", command=self.start_copy_thread, state=tk.DISABLED)
        self.btn_copy.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        results_frame = tk.Frame(main_frame, bg="#f0f0f0")
        results_frame.pack(expand=True, fill=tk.BOTH)
        self.results_label = tk.Label(results_frame, text="Arquivos Carregados:", font=("Helvetica", 10, "bold"),
                                      bg="#f0f0f0")
        self.results_label.pack(anchor="w")

        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, state='disabled', wrap=tk.WORD,
                                                      bg="#ffffff")
        self.results_text.pack(expand=True, fill=tk.BOTH)

        self.status_label = tk.Label(root, text="Pronto. Selecione uma pasta de origem para começar.", bd=1,
                                     relief=tk.SUNKEN, anchor=tk.W, padx=5)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def select_search_path_and_preload(self):
        path = filedialog.askdirectory()
        if not path:
            return

        self.search_path.set(path)
        self.all_files.clear()
        self.found_files.clear()
        self.update_results("")
        self.btn_filter.config(state=tk.DISABLED)
        self.btn_copy.config(state=tk.DISABLED)
        self.btn_select_source.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.preload_files)
        thread.daemon = True
        thread.start()

    def preload_files(self):
        search_path = self.search_path.get()
        self.update_status(f"Carregando todos os arquivos de '{search_path}'...")

        temp_file_list = []
        try:
            for root_dir, _, files in os.walk(search_path):
                for file_name in files:
                    temp_file_list.append(os.path.join(root_dir, file_name))

                if len(temp_file_list) % 100 == 0 and len(temp_file_list) > 0:
                    self.root.after(0, self.update_status, f"Carregando... {len(temp_file_list)} arquivos encontrados.")
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Erro no Carregamento", f"Ocorreu um erro: {e}")

        self.all_files = temp_file_list

        def on_finish():
            display_list = [os.path.basename(f) for f in self.all_files]
            self.update_results("\n".join(display_list))
            self.update_status(
                f"Carregamento concluído. {len(self.all_files)} arquivos carregados. Pronto para filtrar.")
            self.btn_filter.config(state=tk.NORMAL)
            self.btn_select_source.config(state=tk.NORMAL)
            self.start_filter_thread()

        self.root.after(0, on_finish)

    def start_filter_thread(self, event=None):
        if not self.all_files:
            return
        self.filter_files()

    def filter_files(self):
        search_term_cleaned = self.search_term.get().lower().strip()

        if not search_term_cleaned:
            self.found_files = self.all_files[:]
        else:
            search_words = search_term_cleaned.split()
            self.found_files = [
                f for f in self.all_files if all(word in f.lower() for word in search_words)
            ]

        display_list = [os.path.basename(f) for f in self.found_files]
        self.update_results("\n".join(display_list))
        self.results_label.config(text=f"Resultados do Filtro ({len(self.found_files)} encontrados):")

        if self.found_files:
            self.btn_copy.config(state=tk.NORMAL)
        else:
            self.btn_copy.config(state=tk.DISABLED)

    def select_dest_path(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_path.set(path)
            self.update_status(f"Pasta de destino definida: {path}")

    def start_copy_thread(self):
        if not self.dest_path.get():
            messagebox.showerror("Erro", "Por favor, selecione a pasta de destino para as cópias.")
            return

        if not self.found_files:
            messagebox.showinfo("Informação", "Nenhum arquivo para copiar.")
            return

        self.btn_copy.config(state=tk.DISABLED, text="Copiando...")
        self.btn_filter.config(state=tk.DISABLED)
        self.btn_select_source.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.copy_files)
        thread.daemon = True
        thread.start()

    def copy_files(self):
        dest_path = self.dest_path.get()
        total_files = len(self.found_files)

        try:
            for i, src_file_path in enumerate(self.found_files):
                original_file_name = os.path.basename(src_file_path)
                self.root.after(0, self.update_status, f"Copiando {i + 1}/{total_files}: {original_file_name}")

                dest_file_path = os.path.join(dest_path, original_file_name)

                counter = 1
                while os.path.exists(dest_file_path):
                    name, extension = os.path.splitext(original_file_name)
                    new_file_name = f"{name} ({counter}){extension}"
                    dest_file_path = os.path.join(dest_path, new_file_name)
                    counter += 1

                shutil.copy2(src_file_path, dest_file_path)

        except Exception as e:
            self.root.after(0, messagebox.showerror, "Erro na Cópia", f"Ocorreu um erro ao copiar os arquivos: {e}")

        def on_finish():
            self.update_status(f"Cópia concluída! {total_files} arquivos copiados para '{dest_path}'.")
            messagebox.showinfo("Sucesso", f"Todos os {total_files} arquivos foram copiados com sucesso!")
            self.btn_copy.config(state=tk.NORMAL, text="📋 Copiar Arquivos Filtrados")
            self.btn_filter.config(state=tk.NORMAL)
            self.btn_select_source.config(state=tk.NORMAL)

        self.root.after(0, on_finish)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def update_results(self, text):
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = FileLocatorApp(root)
    root.mainloop()
