import tkinter
from tkinter import Toplevel, Text
from tkinter import ttk, SEL, END, INSERT
from tkinter import messagebox
from tkinter import LEFT
from tkinter.ttk import Scrollbar
import os
import numpy as np


class datasetEditor(Toplevel):
    def __init__(self, dispatch_event, project,parent=None):
        """
        A Toplevel window to input the metadata.
        First it builds a grid for the metadata input. Then it takes the metadata of the first selected dataset and uses them as standard values.
        The self.apply function then checks whether the input is valid or not and hands the metadata to the controller for saving.
        """
        super().__init__(parent)
        self.dispatch_event = dispatch_event
        self.title("Dataset Metadata Editor")
        
        items = []
        for it in project.selection:
            items.append(os.path.basename(project.datasets[it].path))
        self.metadata = project.datasets[project.selection[0]].metadata.copy()
        ttk.Label(self, text="Edit dataset parameters",justify=LEFT, font=(
            "Helvetica", 20)).grid(row=0, column=0, columnspan=2,padx = (20,0))
        ttk.Label(self, text="The following datasets are being edited:",justify=LEFT).grid(
            row=1, column=0, columnspan=2,padx = (20,0))
        ttk.Label(self, text=", ".join(items)).grid(
            row=2, column=0, columnspan=2,padx = (20,0))
        ttk.Label(self, text="Sampling rate in Hz",justify=LEFT).grid(row=4, column=0,sticky="e",padx = (20,0))
        self.sr = Text(self, width=50, height=1)
        self.sr.grid(row=4, column=1, sticky="e",padx = (20,0))
        self.sr.insert(
            "end", (self.metadata["Sampling rate in Hz"]))

        ttk.Label(self, text="Cut-off frequency in Hz",justify=LEFT).grid(row=5, column=0,sticky="e",padx = (20,0))
        self.cof = tkinter.Text(self, width=50, height=1)
        self.cof.grid(row=5, column=1, sticky="e",padx = (20,0))
        self.cof.insert(
            "end", (self.metadata["Cut-off frequency in Hz"]))

        ttk.Label(self, text="Filter type",justify=LEFT).grid(row=6, column=0,sticky="e",padx = (20,0))
        FILTER_TYPES = ["%d-pole Bessel" % n for n in [2, 4, 6, 8]]
        self.filter_type = tkinter.StringVar(self)
        self.ft = tkinter.OptionMenu(self, self.filter_type, *FILTER_TYPES)
        self.ft.grid(row=6, column=1, sticky="w",padx = (20,0))
        self.filter_type.set(self.metadata["Filter type"])

        ttk.Label(self, text="Description",anchor="w").grid(row=7, column=0,sticky="e",padx = (20,0))
        self.descr = tkinter.Text(self, width=50, height=8)
        self.descr.grid(row=7, column=1, sticky="e",padx = (20,0))
        self.descr.insert("end", self.metadata["Description"])
        #Scrollbar for description
        self.scrollbar = Scrollbar(self)
        self.descr.config(yscrollcommand= self.scrollbar.set)
        self.scrollbar.config(command= self.descr.yview)
        self.scrollbar.grid(row=7, column=2, sticky="nsw",padx=(0,20))


        self.quant_provided = tkinter.IntVar()
        ttk.Radiobutton(self, text="Provide parameters for quantile simulation",
                        variable=self.quant_provided, value=0).grid(row=8, column=1, sticky="w",padx = (20,0))
        ttk.Radiobutton(self, text="Provide quantile", variable=self.quant_provided, value=1).grid(
            row=9, column=1, sticky="w",padx = (20,0))

        def ask_quantile(*args):
            """
            Changes the grid layout depending on whether the radiobutton indicates a provided quantile.
            """
            if self.quant_provided.get():
                significance_level_label.grid_forget()
                self.significance_level_entry.grid_forget()
                repetitions_label.grid_forget()
                self.repetitions_entry.grid_forget()
                quant_label.grid(row=10, column=0, sticky="e",padx = (20,0))
                self.quant_entry.grid(row=10, column=1, sticky="e",padx = (20,0))
            else:
                quant_label.grid_forget()
                self.quant_entry.grid_forget()
                significance_level_label.grid(row=10, column=0, sticky="e",padx = (20,0))
                self.significance_level_entry.grid(
                    row=10, column=1, sticky="e",padx = (20,0))
                repetitions_label.grid(row=11, column=0, sticky="e",padx = (20,0))
                self.repetitions_entry.grid(row=11, column=1, sticky="e",padx = (20,0))
        self.quant_provided.set(
            int(self.metadata["Quantile provided"]))
        quant_label = ttk.Label(self, text="Quantile",justify=LEFT)
        self.quant_entry = tkinter.Text(self, width=50, height=1)
        significance_level_label = ttk.Label(self, text="Significance level",justify=LEFT)
        self.significance_level_entry = tkinter.Text(self, width=50, height=1)
        repetitions_label = ttk.Label(self, text="Repetitions",justify=LEFT)
        self.repetitions_entry = tkinter.Text(self, width=50, height=1)
        if self.quant_provided.get():
            self.quant_entry.insert(
                "end", (self.metadata["Quantile"]))
            pass
        else:
            self.significance_level_entry.insert(
                "end", (self.metadata["Significance level"]))
            self.repetitions_entry.insert(
                "end", (self.metadata["Repetitions"]))
            pass
        self.quant_provided.trace("w", ask_quantile)
        ask_quantile()
        self.descr.bind('<Control-a>', self.select_all)
        applycancel = ttk.Frame(self)
        applycancel.grid(row=14, column=0, columnspan=2)
        ttk.Button(applycancel, text="Apply",
                   command=self.apply).grid(row=0, column=0,padx=10,pady=10)
        ttk.Button(applycancel, text="Cancel",
                   command=self.destroy).grid(row=0, column=1,padx=10,pady=10)
        self.resizable(width=False, height=False)

    def select_all(self, event):
        """
        Selects everything in the description textbox.
        """
        self.descr.tag_add(SEL, "1.0", END)
        self.descr.mark_set(INSERT, "1.0")
        self.descr.see(INSERT)
        return "break"

    def apply(self, *args):
        """
        Checks the values of the data input, if everything is valid, it saves them in self.metadata and hands the controller the metadata.
        """
        try:
            text = self.sr.get(1.0, 'end')
            text = ''.join(text.split("\n"))
            self.sr.delete(1.0, 'end')
            self.sr.insert('end', text)
            if float(self.sr.get(1.0, 'end')) <= 0:
                messagebox.showwarning(
                    "Invalid input", "Sampling rate must be positive")
                return
        except ValueError:
            messagebox.showwarning(
                "Invalid input", "Sampling rate must be a valid float")
            return
        try:
            text = self.cof.get(1.0, 'end')
            text = ''.join(text.split("\n"))
            self.cof.delete(1.0, 'end')
            self.cof.insert('end', text)
            if float(self.cof.get(1.0, 'end')) <= 0:
                messagebox.showwarning(
                    "Invalid input", "Cut-off frequency must be positive")
                return
        except ValueError:
            messagebox.showwarning(
                "Invalid input", "Cut-off frequency must be a valid float")
            return
        if self.quant_provided.get():
            try:
                text = self.quant_entry.get(1.0, 'end')
                text = ''.join(text.split("\n"))
                self.quant_entry.delete(1.0, 'end')
                self.quant_entry.insert('end', text)
                float(self.quant_entry.get("0.0", "end"))
            except ValueError:
                messagebox.showwarning(
                    "Invalid input", "Quantile must be a valid float")
                return
        else:
            try:
                text = self.significance_level_entry.get(1.0, 'end')
                text = ''.join(text.split("\n"))
                self.significance_level_entry.delete(1.0, 'end')
                self.significance_level_entry.insert('end', text)
                if not 0 < float(self.significance_level_entry.get("1.0", "end")) < 1:
                    messagebox.showwarning(
                        "Invalid input", "Significance level must be between 0 and 1")
                    return
            except ValueError:
                messagebox.showwarning(
                    "Invalid input", "Significance level must be a valid float")
                return
            try:
                text = self.repetitions_entry.get(1.0, 'end')
                text = ''.join(text.split("\n"))
                self.repetitions_entry.delete(1.0, 'end')
                self.repetitions_entry.insert('end', text)
                if int(self.repetitions_entry.get("1.0", "end")) <= 0:
                    messagebox.showwarning(
                        "Invalid input", "Repetitions number must be positive")
                    return
            except ValueError:
                messagebox.showwarning(
                    "Invalid input", "Repetitions number must be a valid int")
                return
            # Validation succeeded, writing edited metadata to datasets
        self.metadata["Sampling rate in Hz"] = float(self.sr.get("0.0", "end"))
        self.metadata["Cut-off frequency in Hz"] = float(
            self.cof.get("0.0", "end"))
        self.metadata["Filter type"] = self.filter_type.get()
        description_string = self.descr.get("0.0", "end")
        self.metadata["Description"] = description_string.replace(
            '\n', ' ').replace('\r', '')
        if self.quant_provided.get():
            self.metadata["Quantile provided"] = True
            self.metadata["Quantile"] = float(
                self.quant_entry.get("0.0", "end"))
            self.metadata["Significance level"] = None
            self.metadata["Repetitions"] = None
        else:
            self.metadata["Quantile provided"] = False
            self.metadata["Quantile"] = None
            self.metadata["Significance level"] = float(
                self.significance_level_entry.get("0.0", "end"))
            self.metadata["Repetitions"] = int(
                self.repetitions_entry.get("0.0", "end"))
        self.dispatch_event("set_metadata", self.metadata)
        for obj in self.grid_slaves():
            obj.grid_remove()
        self.destroy()