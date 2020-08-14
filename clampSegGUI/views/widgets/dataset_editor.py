import tkinter
from tkinter import Toplevel, Text
from tkinter import ttk, SEL, END, INSERT
from tkinter import messagebox
from tkinter import LEFT
from tkinter.ttk import Scrollbar
from tkinter import Tk, Text, BOTH, W, N, E, S
import os
import numpy as np


class datasetEditor(Toplevel):
    def __init__(self, dispatch_event, project, parent=None):
        """
        A Toplevel window to input the metadata.
        First it builds a grid for the metadata input. Then it takes the metadata of the first selected dataset and uses them as standard values.
        The self.apply function then checks whether the input is valid or not and hands the metadata to the controller for saving.
        """
        super().__init__(parent)
        self.dispatch_event = dispatch_event
        self.title("Dataset Metadata Editor")
        self.project = project

        items = []
        for it in self.project.selection:
            items.append(os.path.basename(self.project.datasets[it].path))

        self.metadata = self.project.datasets[self.project.selection[0]].metadata.copy()
        self.initial_filter = self.metadata["Filter type"]
        #self.initial_method = self.metadata["Method"]
        self.initial_method = self.check_value(self.metadata["Method"])
        #self.initial_rep_hilde = self.metadata["Repetitions_Hilde"]
        self.initial_description = self.metadata["Description"]
        ttk.Label(self, text="Edit dataset parameters", justify=LEFT, font=(
            "Helvetica", 20)).grid(row=0, column=0, columnspan=3, padx=(20, 0))
        ttk.Label(self, text="The following datasets are being edited:", justify=LEFT).grid(
            row=1, column=0, columnspan=3, padx=(20, 0))
        self.indent = len(items)
        if self.indent > 4:
            for p in range(4):
                ttk.Label(self, text=items[p]).grid(
                    row=p + 2, column=0, columnspan=3, padx=(20, 0))
                v = "...and "
                k = self.indent - 4
                if k == 1:
                    u = " more dataset"
                else:
                    u = " more datasets"
                ttk.Label(self, text=v + str(k) + u).grid(
                    row=7, column=1, columnspan=3, padx=(20, 0))
            self.indent = 4
        else:
            for p in range(self.indent):
                ttk.Label(self, text=items[p]).grid(
                    row=p + 2, column=0, columnspan=3, padx=(20, 0))

        ttk.Label(self, text="Sampling rate in Hz", justify=LEFT).grid(row=self.indent + 4, column=0, sticky="e", padx=(20, 0))
        self.sr = Text(self, width=60, height=1)
        self.initial_sampling = self.metadata["Sampling rate in Hz"]
        self.sr.grid(row=self.indent + 4, column=1, columnspan=2, sticky="w", padx=(20, 0))
        self.sr.insert(
            "end", (self.metadata["Sampling rate in Hz"]))

        ttk.Label(self, text="Cut-off frequency in Hz", justify=LEFT).grid(row=self.indent+5, column=0, sticky="e", padx=(20, 0))
        self.cof = tkinter.Text(self, width=60, height=1)
        self.cof.grid(row=self.indent+5, column=1, columnspan=2, sticky="w", padx=(20, 0))
        self.cof.insert(
            "end", (self.metadata["Cut-off frequency in Hz"]))

        ttk.Label(self, text="Filter type", justify=LEFT).grid(row=self.indent+6, column=0, sticky="e", padx=(20, 0))
        FILTER_TYPES = ["%d-pole Bessel" % n for n in [2, 4, 6, 8]]
        self.filter_type = tkinter.StringVar(self)
        self.ft = tkinter.OptionMenu(self, self.filter_type, *FILTER_TYPES)
        self.ft.grid(row=self.indent+6, column=1, columnspan=2, sticky="w", padx=(20, 0))
        self.filter_type.set(self.metadata["Filter type"])
        ttk.Label(self, text="Method").grid(row=self.indent+8, column=0, sticky="e", padx=(20, 0))
        self.method = tkinter.IntVar()
        self.quant_provided = tkinter.IntVar()
        self.parameters = tkinter.IntVar()
        ttk.Radiobutton(self, text="JULES (homogeneous noise)", variable=self.method, value=10).grid(row=self.indent+9, column=1,
                                                                                             sticky="w",
                                                                                             padx=(20, 0), columnspan=1)

        ttk.Radiobutton(self, text="JSMURF (homogeneous noise)",
                        variable=self.method, value=11).grid(row=self.indent+8, column=1, sticky="w", padx=(20, 0), columnspan=1)

        ttk.Radiobutton(self, text="JSMURF (heterogeneous noise)",
                        variable=self.method, value=12).grid(row=self.indent+8, column=2, sticky="w", padx=(20, 0), columnspan=1)
        ttk.Radiobutton(self, text="HILDE (homogeneous noise)",
                        variable=self.method, value=13).grid(row=self.indent+9, column=2,  sticky="w", padx=(20, 0), columnspan=1)

        ttk.Radiobutton(self, text="HILDE (heterogeneous noise)", variable=self.method, value=14).grid(row=self.indent+10, column=1,
                                                                                               sticky="w", padx=(20, 0),
                                                                                               columnspan=1)

        ttk.Label(self, text="Quantiles", anchor="w").grid(row=self.indent+15, column=0, sticky="e", padx=(20, 0))
        ttk.Label(self, text="Description", anchor="w").grid(row=self.indent+7, column=0, sticky="e", padx=(20, 0))
        self.descr = tkinter.Text(self, width=60, height=8)
        self.descr.grid(row=self.indent+7, column=1, columnspan=2, sticky="w", padx=(20, 0))
        self.descr.insert("end", self.metadata["Description"])
        # Scrollbar for description
        self.scrollbar = Scrollbar(self)
        self.descr.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.descr.yview)
        self.scrollbar.grid(row=self.indent+7, column=3, sticky="nsw", padx=(0, 20))
        self.grid_rowconfigure(14, minsize=10)
        c = ttk.Radiobutton(self, text="Provide parameters for quantile simulation",
                            variable=self.quant_provided, value=0)

        c.grid(row=self.indent+15, column=1, columnspan=2, sticky="w",  padx=(20, 0))
        a = ttk.Radiobutton(self, text="Provide quantile", variable=self.quant_provided, value=1)
        a.grid(row=self.indent+16, column=1, columnspan=2, sticky="w",  padx=(20, 0))

        self.grid_rowconfigure(17, minsize=10)
        self.method.set(
             self.check_value(self.metadata["Method"]))


        def method_HILDE(*args):
            """
            Changes the grid layout depending on whether the radiobutton indicates method hilde is chosen .
            """

            method = self.method.get()

            if method == 13 or method == 14:
                a.grid_forget()
                self.grid_rowconfigure(14, minsize=10)
                c.grid(row=self.indent + 15, column=1, columnspan=2, sticky="w", padx=(20, 0))
                significance_level_label.grid_forget()
                self.significance_level_entry.grid_forget()
                quant_label.grid_forget()
                self.quant_entry.grid_forget()
                self.repetitions_entry.grid_forget()
                self.quant_JULES_HOMOGENEOUS_entry.grid_forget()
                self.quant_JSMURF_HOMOGENEOUS_entry.grid_forget()
                self.grid_rowconfigure(16, minsize=10)
                self.grid_rowconfigure(17, minsize=10)
                significance_level1_label.grid(row=self.indent + 18, column=0, sticky="e", padx=(20, 0))
                significance_level2_label.grid(row=self.indent + 19, column=0, sticky="e",
                                               padx=(20, 0))  # extra significance level for HILDE
                self.significance_level1_entry.grid(
                    row=self.indent + 18, column=1, columnspan=2, sticky="w", padx=(20, 0))
                self.significance_level2_entry.grid(
                    row=self.indent + 19, column=1, columnspan=2, sticky="w", padx=(20, 0))
                repetitions_label.grid(row=self.indent + 20, column=0, sticky="e", padx=(20, 0))
                self.repetitions_hilde_entry.grid(row=self.indent + 20, column=1, columnspan=2, sticky="w", padx=(20, 0))
                self.quant_provided.set(0)

            elif method == 12:
                a.grid_forget()
                self.grid_rowconfigure(14, minsize=10)
                c.grid(row=self.indent + 15, column=1, columnspan=2, sticky="w",  padx=(20, 0))
                significance_level1_label.grid_forget()
                self.significance_level1_entry.grid_forget()
                significance_level2_label.grid_forget()
                self.significance_level2_entry.grid_forget()
                quant_label.grid_forget()
                self.quant_entry.grid_forget()
                self.quant_JULES_HOMOGENEOUS_entry.grid_forget()
                self.quant_JSMURF_HOMOGENEOUS_entry.grid_forget()
                self.repetitions_hilde_entry.grid_forget()
                self.grid_rowconfigure(16, minsize=10)
                self.grid_rowconfigure(17, minsize=10)
                significance_level_label.grid(row=self.indent + 18, column=0, sticky="e", padx=(20, 0))
                self.significance_level_entry.grid(
                    row=self.indent + 18, column=1, columnspan=2, sticky="w", padx=(20, 0))
                repetitions_label.grid(row=self.indent + 19, column=0, sticky="e", padx=(20, 0))
                self.repetitions_entry.grid(row=self.indent + 19, column=1, columnspan=2, sticky="w", padx=(20, 0))
                self.quant_provided.set(0)
            elif method == 11:
                f = self.quant_provided.get()
                if f == 0:
                    self.grid_rowconfigure(14, minsize=10)
                    c.grid(row=self.indent + 15, column=1, columnspan=2, sticky="w",  padx=(20, 0))
                    a.grid(row=self.indent + 16, column=1, columnspan=2, sticky="w",  padx=(20, 0))
                    significance_level1_label.grid_forget()
                    self.significance_level1_entry.grid_forget()
                    significance_level2_label.grid_forget()
                    self.significance_level2_entry.grid_forget()
                    quant_label.grid_forget()
                    self.quant_entry.grid_forget()
                    self.repetitions_hilde_entry.grid_forget()
                    self.quant_JULES_HOMOGENEOUS_entry.grid_forget()
                    self.quant_JSMURF_HOMOGENEOUS_entry.grid_forget()
                    self.grid_rowconfigure(17, minsize=10)
                    significance_level_label.grid(row=self.indent + 18, column=0, sticky="e", padx=(20, 0))
                    self.significance_level_entry.grid(
                        row=self.indent + 18, column=1, columnspan=2, sticky="w", padx=(20, 0))
                    repetitions_label.grid(row=self.indent + 19, column=0, sticky="e", padx=(20, 0))
                    self.repetitions_entry.grid(row=self.indent + 19, column=1, columnspan=2, sticky="w", padx=(20, 0))
                else:
                    self.grid_rowconfigure(14, minsize=10)
                    significance_level_label.grid_forget()
                    self.significance_level_entry.grid_forget()
                    repetitions_label.grid_forget()
                    self.repetitions_entry.grid_forget()
                    significance_level1_label.grid_forget()
                    self.significance_level1_entry.grid_forget()
                    significance_level2_label.grid_forget()
                    self.significance_level2_entry.grid_forget()
                    self.repetitions_hilde_entry.grid_forget()
                    quant_label.grid_forget()
                    self.quant_entry.grid_forget()
                    self.quant_JULES_HOMOGENEOUS_entry.grid_forget()
                    self.grid_rowconfigure(17, minsize=10)
                    quant_label.grid(row=18 + self.indent, column=0, sticky="e", padx=(20, 0))
                    self.quant_JSMURF_HOMOGENEOUS_entry.grid(row=18 + self.indent, column=1, columnspan=2, sticky="w", padx=(20, 0))
            else:
                f = self.quant_provided.get()
                if f == 0:
                    self.grid_rowconfigure(14, minsize=10)
                    a.grid(row=self.indent + 16, column=1, columnspan=2, sticky="w",  padx=(20, 0))
                    c.grid(row=self.indent+15, column=1, columnspan=2, sticky="w",  padx=(20, 0))
                    significance_level1_label.grid_forget()
                    self.significance_level1_entry.grid_forget()
                    significance_level2_label.grid_forget()
                    self.significance_level2_entry.grid_forget()
                    quant_label.grid_forget()
                    self.quant_entry.grid_forget()
                    self.repetitions_hilde_entry.grid_forget()
                    self.quant_JULES_HOMOGENEOUS_entry.grid_forget()
                    self.quant_JSMURF_HOMOGENEOUS_entry.grid_forget()
                    self.grid_rowconfigure(17, minsize=10)
                    significance_level_label.grid(row=self.indent + 18, column=0, sticky="e", padx=(20, 0))
                    self.significance_level_entry.grid(
                        row=self.indent + 18, column=1, columnspan=2, sticky="w", padx=(20, 0))
                    repetitions_label.grid(row=self.indent + 19, column=0, sticky="e", padx=(20, 0))
                    self.repetitions_entry.grid(row=self.indent + 19, column=1, columnspan=2, sticky="w", padx=(20, 0))
                else:
                    self.grid_rowconfigure(14, minsize=10)
                    c.grid(row=self.indent+15, column=1, columnspan=2, sticky="w",  padx=(20, 0))
                    a.grid(row=self.indent + 16, column=1, columnspan=2, sticky="w",  padx=(20, 0))
                    significance_level_label.grid_forget()
                    self.significance_level_entry.grid_forget()
                    repetitions_label.grid_forget()
                    self.repetitions_entry.grid_forget()
                    significance_level1_label.grid_forget()
                    self.significance_level1_entry.grid_forget()
                    significance_level2_label.grid_forget()
                    self.repetitions_hilde_entry.grid_forget()
                    self.significance_level2_entry.grid_forget()
                    quant_label.grid_forget()
                    self.quant_entry.grid_forget()
                    self.quant_JSMURF_HOMOGENEOUS_entry.grid_forget()
                    self.grid_rowconfigure(17, minsize=10)
                    quant_label.grid(row=18 + self.indent, column=0, sticky="e", padx=(20, 0))
                    self.quant_JULES_HOMOGENEOUS_entry.grid(row=18 + self.indent, column=1, columnspan=2, sticky="w", padx=(20, 0))

        significance_level1_label = ttk.Label(self, text=" Alpha1 ", justify=LEFT)
        self.significance_level1_entry = tkinter.Text(self, width=60, height=1)
        significance_level2_label = ttk.Label(self, text=" Alpha2 ")
        self.significance_level2_entry = tkinter.Text(self, width=60, height=1)
        quant_label = ttk.Label(self, text="Quantile", justify=LEFT)
        self.quant_JULES_HOMOGENEOUS_entry = tkinter.Text(self, width=60, height=1)
        self.quant_JSMURF_HOMOGENEOUS_entry = tkinter.Text(self, width=60, height=1)
        self.quant_entry = tkinter.Text(self, width=60, height=1)
        significance_level_label = ttk.Label(self, text="Alpha", justify=LEFT)
        self.significance_level_entry = tkinter.Text(self, width=60, height=1)
        repetitions_label = ttk.Label(self, text="Repetitions", justify=LEFT)
        self.repetitions_entry = tkinter.Text(self, width=60, height=1)
        self.repetitions_hilde_entry = tkinter.Text(self, width=60, height=1)
        method = self.method.get()

        # if method == 10:
        #     if int(self.metadata["Quantile_JULES_HOMOGENEOUS provided"]):
        #         self.quant_provided.set(
        #             int(self.metadata["Quantile_JULES_HOMOGENEOUS provided"]))
        #     else:
        #         self.quant_provided.set(
        #             int(self.metadata["quantile_jules_store provided"]))
        # elif method == 11:
        #     if int(self.metadata["Quantile_JSMURF_HOMOGENEOUS provided"]):
        #         self.quant_provided.set(
        #             int(self.metadata["Quantile_JSMURF_HOMOGENEOUS provided"]))
        #     else:
        #         self.quant_provided.set(
        #             int(self.metadata["quantile_jsmurf_store provided"]))
        # else:
        #     pass
        if method == 10:
            self.quant_provided.set(
                int(self.metadata["quantile_jules_store provided"]))
        elif method == 11:
            self.quant_provided.set(
                int(self.metadata["quantile_jsmurf_store provided"]))
        else:
            pass
        if int(self.metadata["quantile_jules_store provided"]):
            self.quant_JULES_HOMOGENEOUS_entry.insert(
                "end", (self.metadata["quantile_jules_store"]))
        elif int(self.metadata["Quantile_JULES_HOMOGENEOUS provided"]):
            self.quant_JULES_HOMOGENEOUS_entry.insert(
                "end", (self.metadata["Quantile_JULES_HOMOGENEOUS"]))
        else:
            pass

        if int(self.metadata["quantile_jsmurf_store provided"]):
            self.quant_JSMURF_HOMOGENEOUS_entry.insert(
                "end", (self.metadata["quantile_jsmurf_store"]))
        elif int(self.metadata["Quantile_JSMURF_HOMOGENEOUS provided"]):
            self.quant_JSMURF_HOMOGENEOUS_entry.insert(
                "end", (self.metadata["Quantile_JSMURF_HOMOGENEOUS"]))
        else:
            pass

        self.significance_level_entry.insert(
            "end", (self.metadata["Significance level"]))
        self.repetitions_entry.insert(
            "end", (self.metadata["Repetitions"]))
        self.repetitions_hilde_entry.insert(
            "end", (self.metadata["Repetitions_Hilde"]))
        self.significance_level1_entry.insert(
            "end", (self.metadata["Significance level 1"]))
        self.significance_level2_entry.insert(
            "end", (self.metadata["Significance level 2"]))

        self.quant_provided.trace("w", method_HILDE)
        method_HILDE()
        self.descr.bind('<Control-a>', self.select_all)
        applycancel = ttk.Frame(self)
        applycancel.grid(row=21 + self.indent, column=0, columnspan=3)
        ttk.Button(applycancel, text="Apply",
                   command=self.apply).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(applycancel, text="Cancel",
                   command=self.destroy).grid(row=0, column=2, padx=10, pady=10)
        self.resizable(width=False, height=False)
        self.method.trace("w", method_HILDE)
        method_HILDE()
        self.sr.edit_modified(False)
        self.cof.edit_modified(False)
        self.quant_JULES_HOMOGENEOUS_entry.edit_modified(False)
        self.quant_JSMURF_HOMOGENEOUS_entry.edit_modified(False)
        self.significance_level_entry.edit_modified(False)
        self.repetitions_entry.edit_modified(False)
        self.significance_level1_entry.edit_modified(False)
        self.significance_level2_entry.edit_modified(False)
        self.repetitions_hilde_entry.edit_modified(False)

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
        metadata = {}
        value = self.method.get()
        #k = self.repetitions_hilde_entry.get()

        if self.sr.edit_modified():
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

        if self.cof.edit_modified():
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
        if value == 13 or value == 14:

            if self.significance_level1_entry.edit_modified():
                try:

                    text = self.significance_level1_entry.get(1.0, 'end')
                    text = ''.join(text.split("\n"))
                    self.significance_level1_entry.delete(1.0, 'end')
                    self.significance_level1_entry.insert('end', text)
                    if not 0 < float(self.significance_level1_entry.get(1.0, "end")) < 1:
                        messagebox.showwarning(
                            "Invalid input", "Significance level 1 must be between 0 and 1")
                        return
                except ValueError:
                    messagebox.showwarning(
                        "Invalid input", "Significance level 1 must be a valid float")
                    return

            if self.significance_level2_entry.edit_modified():
                try:

                    text = self.significance_level2_entry.get(1.0, 'end')
                    text = ''.join(text.split("\n"))
                    self.significance_level2_entry.delete(1.0, 'end')
                    self.significance_level2_entry.insert('end', text)
                    if not 0 < float(self.significance_level2_entry.get(1.0, "end")) < 1:
                        messagebox.showwarning(
                            "Invalid input", "Significance level 2 must be between 0 and 1")
                        return
                except ValueError:
                    messagebox.showwarning(
                        "Invalid input", "Significance level 2 must be a valid float")
                    return

        elif value == 12:
            if self.significance_level_entry.edit_modified():
                try:

                    text = self.significance_level_entry.get(1.0, 'end')
                    text = ''.join(text.split("\n"))
                    self.significance_level_entry.delete(1.0, 'end')
                    self.significance_level_entry.insert('end', text)
                    if not 0 < float(self.significance_level_entry.get(1.0, "end")) < 1:
                        messagebox.showwarning(
                            "Invalid input", "Significance level must be between 0 and 1")
                        return
                except ValueError:
                    messagebox.showwarning(
                        "Invalid input", "Significance level must be a valid float")

        else:

            if self.quant_JULES_HOMOGENEOUS_entry.edit_modified():
                if self.quant_provided.get():
                    try:
                        text = self.quant_JULES_HOMOGENEOUS_entry.get(1.0, 'end')
                        text = ''.join(text.split("\n"))
                        self.quant_JULES_HOMOGENEOUS_entry.delete(1.0, 'end')
                        self.quant_JULES_HOMOGENEOUS_entry.insert('end', text)
                        float(self.quant_JULES_HOMOGENEOUS_entry.get(1.0, 'end'))
                    except ValueError:
                        messagebox.showwarning(
                            "Invalid input", "Quantile must be a valid float")
                        return

            else:
                if self.significance_level_entry.edit_modified():
                    try:

                        text = self.significance_level_entry.get(1.0, 'end')
                        text = ''.join(text.split("\n"))
                        self.significance_level_entry.delete(1.0, 'end')
                        self.significance_level_entry.insert('end', text)
                        if not 0 < float(self.significance_level_entry.get(1.0, "end")) < 1:
                            messagebox.showwarning(
                                "Invalid input", "Significance level must be between 0 and 1")
                            return
                    except ValueError:
                        messagebox.showwarning(
                            "Invalid input", "Significance level must be a valid float")
                        return

        if self.repetitions_entry.edit_modified():
            try:
                text = self.repetitions_entry.get(1.0, 'end')
                text = ''.join(text.split("\n"))
                self.repetitions_entry.delete(1.0, 'end')
                self.repetitions_entry.insert('end', text)
                if int(self.repetitions_entry.get(1.0, "end")) <= 0:
                    messagebox.showwarning(
                        "Invalid input", "Repetitions number must be positive")
                    return
            except ValueError:
                messagebox.showwarning(
                    "Invalid input", "Repetitions number must be a valid int")
                return
            if self.repetitions_hilde_entry.edit_modified():
                try:
                    text = self.repetitions_hilde_entry.get(1.0, 'end')
                    text = ''.join(text.split("\n"))
                    self.repetitions_hilde_entry.delete(1.0, 'end')
                    self.repetitions_hilde_entry.insert('end', text)
                    if int(self.repetitions_hilde_entry.get(1.0, "end")) <= 0:
                        messagebox.showwarning(
                            "Invalid input", "Repetitions number must be positive")
                        return
                except ValueError:
                    messagebox.showwarning(
                        "Invalid input", "Repetitions number must be a valid int")
                    return

            # Validation succeeded, writing edited metadata to datasets
        #
        #             # Validation succeeded, writing edited metadata to datasets
        for i in self.project.selection:
            metadata[i] = self.project.datasets[i].metadata.copy()
            # if metadata[i]["Quantile_JULES_HOMOGENEOUS provided"]:
            #     metadata[i]["quantile_jules_store"] = metadata[i]["Quantile_JULES_HOMOGENEOUS"]
            # if metadata[i]["Quantile_JSMURF_HOMOGENEOUS provided"]:
            #     metadata[i]["quantile_jsmurf_store"] = metadata[i]["Quantile_JSMURF_HOMOGENEOUS"]
            if value != self.initial_method:
                if value == 10:
                    metadata[i]["Method"] = "JULES-Homogeneous"
                elif value == 11:
                    metadata[i]["Method"] = "JSMURF-Homogeneous"
                elif value == 12:
                    metadata[i]["Method"] = "JSMURF-Heterogeneous"
                elif value == 13:
                    metadata[i]["Method"] = "HILDE-Homogeneous"
                elif value == 14:
                    metadata[i]["Method"] = "HILDE-Heterogeneous"
            else:
                pass
            if self.sr.edit_modified():
                metadata[i]["Sampling rate in Hz"] = float(self.sr.get("0.0", "end"))

            if self.cof.edit_modified():
                metadata[i]["Cut-off frequency in Hz"] = float(
                    self.cof.get("0.0", "end"))

            a = self.filter_type.get()
            if a != self.initial_filter:
                metadata[i]["Filter type"] = a

            description_string = self.descr.get("0.0", "end")
            description_string = description_string.replace(
                    '\n', '').replace('\r', '')
            b = self.initial_description
            if b != description_string:

                metadata[i]["Description"] = description_string.replace(
                    '\n', ' ').replace('\r', '')
            if value == 13 or value == 14:

                metadata[i]["Quantile_HILDE_HOMOGENEOUS provided"] = False
                metadata[i]["Quantile_HILDE_HOMOGENEOUS"] = None
                metadata[i]["Quantile_HILDE_HETEROGENEOUS provided"] = False
                metadata[i]["Quantile_HILDE_HETEROGENEOUS"] = None
                if self.significance_level1_entry.edit_modified():
                    metadata[i]["Significance level 1"] = float(
                        self.significance_level1_entry.get(1.0, "end"))
                if self.significance_level2_entry.edit_modified():
                    metadata[i]["Significance level 2"] = float(
                        self.significance_level2_entry.get(1.0, "end"))

                if self.repetitions_hilde_entry.edit_modified():
                    metadata[i]["Repetitions_Hilde"] = int(
                        self.repetitions_hilde_entry.get("0.0", "end"))
                    #
                    # metadata[i]["Repetitions"] = int(
                    #     self.repetitions_hilde_entry.get("0.0", "end"))
            elif value == 12:
                metadata[i]["Quantile_JSMURF_HETEROGENEOUS provided"] = False
                metadata[i]["Quantile_JSMURF_HETEROGENEOUS"] = None
                if self.significance_level_entry.edit_modified():
                    metadata[i]["Significance level"] = float(
                        self.significance_level_entry.get(1.0, "end"))

                if self.repetitions_entry.edit_modified():
                    metadata[i]["Repetitions"] = int(
                        self.repetitions_entry.get("0.0", "end"))


            elif value == 11:

                if self.quant_provided.get():
                    if self.quant_JSMURF_HOMOGENEOUS_entry.edit_modified():

                        metadata[i]["Quantile_JSMURF_HOMOGENEOUS provided"] = True

                        metadata[i]["Quantile_JSMURF_HOMOGENEOUS"] = float(
                            self.quant_JSMURF_HOMOGENEOUS_entry.get(1.0, "end"))
                        metadata[i]["quantile_jsmurf_store provided"] = True

                        metadata[i]["quantile_jsmurf_store"] = float(
                            self.quant_JSMURF_HOMOGENEOUS_entry.get(1.0, "end"))

                    else:
                        pass

                else:
                    metadata[i]["Quantile_JSMURF_HOMOGENEOUS provided"] = False
                    metadata[i]["Quantile_JSMURF_HOMOGENEOUS"] = None
                    if self.significance_level_entry.edit_modified():
                        metadata[i]["Significance level"] = float(
                            self.significance_level_entry.get(1.0, "end"))

                    if self.repetitions_entry.edit_modified():
                        metadata[i]["Repetitions"] = int(
                            self.repetitions_entry.get("0.0", "end"))

            else:

                if self.quant_provided.get():
                    if self.quant_JULES_HOMOGENEOUS_entry.edit_modified():

                        metadata[i]["Quantile_JULES_HOMOGENEOUS provided"] = True

                        metadata[i]["Quantile_JULES_HOMOGENEOUS"] = float(
                            self.quant_JULES_HOMOGENEOUS_entry.get(1.0, "end"))
                        metadata[i]["quantile_jules_store provided"] = True
                        metadata[i]["quantile_jules_store"] = float(
                            self.quant_JULES_HOMOGENEOUS_entry.get(1.0, "end"))

                    else:
                        pass
                else:
                    metadata[i]["Quantile_JULES_HOMOGENEOUS provided"] = False
                    metadata[i]["Quantile_JULES_HOMOGENEOUS"] = None
                    if self.significance_level_entry.edit_modified():
                        metadata[i]["Significance level"] = float(
                            self.significance_level_entry.get(1.0, "end"))

                    if self.repetitions_entry.edit_modified():
                        metadata[i]["Repetitions"] = int(
                            self.repetitions_entry.get("0.0", "end"))
                        # metadata[i]["Repetitions_Hilde"] = int(
                        #     self.repetitions_entry.get("0.0", "end"))

        self.dispatch_event("set_metadata", metadata)

        for obj in self.grid_slaves():
            obj.grid_remove()
        self.destroy()

    def check_value(self, x):
        if x == "JULES-Homogeneous":
            value_of_method = 10
        elif x == "JSMURF-Homogeneous":
            value_of_method = 11
        elif x == "JSMURF-Heterogeneous":
            value_of_method = 12
        elif x == "HILDE-Homogeneous":
            value_of_method = 13
        elif x == "HILDE-Heterogeneous":
            value_of_method = 14
        return value_of_method