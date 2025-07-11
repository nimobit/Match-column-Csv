import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
import re

class CSVComparer:
    def __init__(self, root):
        self.root = root
        self.root.title("Match tra colonne CSV")
        self.df1 = None
        self.df2 = None
        self.csv1_path = None

        # Bottone info
        info_button = tk.Button(root, text="ℹ️", font=("Arial", 12), command=self.mostra_info)
        info_button.place(x=5, y=5)

        # Caricamento CSV
        tk.Button(root, text="📂 Carica CSV 1", command=self.load_csv1).pack(pady=3)
        tk.Button(root, text="📂 Carica CSV 2", command=self.load_csv2).pack(pady=3)

        # Ordinamento colonne
        tk.Label(root, text="Ordina colonne per:").pack()
        self.sort_mode = tk.StringVar(value="originale")
        tk.Radiobutton(root, text="🔢 Originale", variable=self.sort_mode, value="originale", command=self.update_column_choices).pack(anchor="w")
        tk.Radiobutton(root, text="🔠 A → Z", variable=self.sort_mode, value="asc", command=self.update_column_choices).pack(anchor="w")
        tk.Radiobutton(root, text="🔡 Z → A", variable=self.sort_mode, value="desc", command=self.update_column_choices).pack(anchor="w")

        # ComboBox selezioni
        tk.Label(root, text="Colonna 1 (origine)").pack()
        self.combo_col1 = Combobox(root, state="normal")
        self.combo_col1.pack(pady=2)

        tk.Label(root, text="Colonna 2 (target)").pack()
        self.combo_col2 = Combobox(root, state="normal")
        self.combo_col2.pack(pady=2)

        tk.Label(root, text="Nome colonna di output").pack()
        self.combo_output = Combobox(root, state="normal")
        self.combo_output.pack(pady=2)

        # Testo match
        tk.Label(root, text="Testo da scrivere se c'è match").pack()
        self.match_text_entry = tk.Entry(root)
        self.match_text_entry.insert(0, "✔️")
        self.match_text_entry.pack(pady=2)

        # Solo se vuoto
        self.only_if_empty = tk.BooleanVar()
        tk.Checkbutton(root, text="Scrivi solo se la cella è vuota", variable=self.only_if_empty).pack(pady=2)

        # Separatore
        tk.Label(root, text="Separatore da usare (es: , | spazio)").pack()
        self.separator_entry = tk.Entry(root)
        self.separator_entry.insert(0, " | ")
        self.separator_entry.pack(pady=2)

        # Azioni
        tk.Button(root, text="✅ Esegui Match e SALVA nuovo file", command=self.esegui_match_salva).pack(pady=4)
        tk.Button(root, text="✍️ Esegui Match e SCRIVI su CSV1", command=self.esegui_match_scrivi).pack(pady=4)

    def mostra_info(self):
        messagebox.showinfo(
            "Info",
            "Utility di confronto colonne CSV con match.\n\n"
            "Funzionalit\u00e0:\n"
            "- Carica uno (o due) file CSV e confronta i valori tra due colonne a scelta.\n"
            "- In caso di match (confronto normalizzato e case-insensitive), scrive un testo personalizzato in una colonna (già esistente o nuova).\n"
            "- Pu\u00f2 aggiungere o aggiornare la colonna nel CSV 1 oppure salvare un nuovo file (nel secondo caso sono riportate solo le colonne confrontate e colonna output).\n"
            "- Supporta ordinamento delle colonne, scelta del separatore e scrittura solo su celle vuote.\n\n"
            "nCoded by Riccardo Martuzzi\n\n"
            "Hello World!\n\n"
        )

    def load_csv1(self):
        path = filedialog.askopenfilename(title="Seleziona CSV 1", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        try:
            self.df1 = pd.read_csv(path, sep=";", dtype=str, engine='python', on_bad_lines='skip').fillna("")
            self.csv1_path = path
        except Exception as e:
            messagebox.showerror("Errore", f"Errore CSV1:\n{e}")
            return
        self.update_column_choices()

    def load_csv2(self):
        path = filedialog.askopenfilename(title="Seleziona CSV 2", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        try:
            self.df2 = pd.read_csv(path, sep=";", dtype=str, engine='python', on_bad_lines='skip').fillna("")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore CSV2:\n{e}")
            return
        self.update_column_choices()

    def update_column_choices(self):
        colonne_totali = []
        if self.df1 is not None:
            colonne_totali += list(self.df1.columns)
        if self.df2 is not None:
            colonne_totali += [c for c in self.df2.columns if c not in colonne_totali]

        if self.sort_mode.get() == "asc":
            col_list = sorted(colonne_totali)
        elif self.sort_mode.get() == "desc":
            col_list = sorted(colonne_totali, reverse=True)
        else:
            col_list = colonne_totali

        self.combo_col1["values"] = col_list
        self.combo_col2["values"] = col_list
        if self.df1 is not None:
            output_col_list = list(self.df1.columns) + ["Match (new col)"]
        else:
            output_col_list = ["Match (new col)"]
        self.combo_output["values"] = output_col_list

        if col_list:
            self.combo_col1.set(col_list[0])
            self.combo_col2.set(col_list[0])
        if self.df1 is not None and len(self.df1.columns) > 0:
            self.combo_output.set("Match (new col)")

    def normalizza(self, val):
        val = str(val)
        val = val.strip()
        val = re.sub(r"\s+", " ", val)
        return val.lower()

    def esegui_match(self, scrivi_su_df1=False, salva_nuovo=False):
        col1 = self.combo_col1.get()
        col2 = self.combo_col2.get()
        col_output_gui = self.combo_output.get().strip()
        col_output = "Match" if col_output_gui == "Match (new col)" else col_output_gui
        testo_match = self.match_text_entry.get().strip()
        separator = self.separator_entry.get()

        if not all([col1, col2, col_output, testo_match]):
            messagebox.showwarning("Attenzione", "Compila tutte le selezioni e l’input.")
            return
        if self.df1 is None:
            messagebox.showerror("Errore", "CSV1 non caricato.")
            return

        col1_values = self.df1[col1] if col1 in self.df1.columns else self.df2[col1] if self.df2 is not None and col1 in self.df2.columns else None
        col2_values = self.df2[col2] if self.df2 is not None and col2 in self.df2.columns else self.df1[col2] if col2 in self.df1.columns else None

        if col1_values is None or col2_values is None:
            messagebox.showerror("Errore", "Colonne non trovate.")
            return

        col1_norm = col1_values.apply(self.normalizza)
        col2_norm = col2_values.apply(self.normalizza)
        matched_values = set(col2_norm)

        def costruisci_output(index):
            matchato = col1_norm.iat[index] in matched_values
            if not matchato:
                return self.df1[col_output].iat[index] if col_output in self.df1.columns else ""

            valore_attuale = self.df1[col_output].iat[index] if col_output in self.df1.columns else ""

            if self.only_if_empty.get() and valore_attuale.strip():
                return valore_attuale

            if valore_attuale.strip():
                return f"{valore_attuale}{separator}{testo_match}"
            else:
                return testo_match

        output_series = pd.Series([costruisci_output(i) for i in range(len(self.df1))]).astype(str).str.strip()

        if scrivi_su_df1:
            self.df1[col_output] = output_series
            risposta = messagebox.askyesno("Salvataggio", f"Vuoi sovrascrivere il file originale CSV1?\n\n{self.csv1_path}")
            if risposta and self.csv1_path:
                try:
                    self.df1.to_csv(self.csv1_path, sep=";", index=False, encoding="utf-8-sig")
                    messagebox.showinfo("✅ Salvato", f"CSV1 aggiornato:\n{self.csv1_path}")
                except Exception as e:
                    messagebox.showerror("Errore salvataggio", str(e))
            else:
                save_path = filedialog.asksaveasfilename(title="Salva come", defaultextension=".csv",
                                                         filetypes=[("CSV files", "*.csv")],
                                                         initialfile="match_modificato.csv")
                if not save_path:
                    return
                try:
                    self.df1.to_csv(save_path, sep=";", index=False, encoding="utf-8-sig")
                    messagebox.showinfo("✅ Salvato", f"File salvato:\n{save_path}")
                except Exception as e:
                    messagebox.showerror("Errore salvataggio", str(e))

        elif salva_nuovo:
            df_output = pd.DataFrame({
                col1: col1_values,
                col2: col2_values if len(col2_values) == len(col1_values) else [""] * len(col1_values),
                col_output: output_series
            })
            save_path = filedialog.asksaveasfilename(title="Salva come", defaultextension=".csv",
                                                     filetypes=[("CSV files", "*.csv")],
                                                     initialfile="match_output.csv")
            if not save_path:
                return
            try:
                df_output.to_csv(save_path, sep=";", index=False, encoding="utf-8-sig")
                messagebox.showinfo("✅ Salvato", f"File salvato:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Errore salvataggio", str(e))

    def esegui_match_salva(self):
        self.esegui_match(scrivi_su_df1=False, salva_nuovo=True)

    def esegui_match_scrivi(self):
        self.esegui_match(scrivi_su_df1=True, salva_nuovo=False)

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVComparer(root)
    root.mainloop()
