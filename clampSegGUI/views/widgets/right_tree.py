from tkinter.ttk import Frame, Scrollbar, Treeview, Notebook
import tkinter
from tkinter import font as ft
import textwrap
from .mplframe import MatplotlibFrame


class RightTree(Frame):
    def get_size_in_pixels(self, text):
        """
        Returns the length of the String 'text' in pixels.
        """
        font = ft.Font()
        w = font.measure(text)
        return w

    def __init__(self, parent, dispatch_event):
        """
        Builds the lower right tree, which informs the user about the metadata information.
        Initialisation creates a frame, a treeview and two scrollbars for the treeview element. 
        
        On Inform, if there is a dataset selected it will build a Treeview with the metadata.
        """
        super().__init__(parent)
        self.dispatch_event = dispatch_event
        self.tree = Treeview(self, columns=["value"],
                             show="tree")
        #self.configure(height=1000)
        self.scrollbar_y = Scrollbar(self.tree, orient="vertical")
        self.scrollbar = Scrollbar(self.tree, orient="horizontal")
        self.scrollbar.config(command=self.tree.xview)
        self.scrollbar_y.config(command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set,
                            xscrollcommand=self.scrollbar.set)
        self.tree.pack(fill="both", expand=True)
        self.scrollbar.pack(side="bottom", fill="x")
        self.scrollbar_y.pack(side="right", fill="y")
        self.pack(expand=1, fill='both')
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        """
        Sets the width of column 0 to an arbitrary, long enough value, to fix issue nr.005.
        """
        self.scrollbar.config(command=self.tree.xview)
        self.scrollbar.pack(side="bottom", fill="x")
        self.tree.column(0, width=600)
        self.update()
        pass

    def inform(self, data):
        """
        Inform function of the RightTree class. 
        Loads available data. If there is a project, it clears the Treeview.
        If there is exactly 1 selection, it will build a tree with the metadata shown in it.
        If there is no selection or more than 1, it will show an appropriate message.
        """
        project = data["project"]
        if project:
            # First delete everything - Selection might have changed
            self.tree.delete(*self.tree.get_children())
            # 3 ifs : no selection, 1 selected, multiple selections
            sel = project.selection
            if len(sel) == 0:
                self.tree.column("#0", width=1100)
                self.tree.insert("", tkinter.END, "Project information",
                                 text="Please add and select a dataset")
            elif len(sel) == 1:
                index = sel[0]  # For legacy reasons variable named name
                self.tree.insert(
                    "", tkinter.END, "Project information", text="Project information")
                self.tree.insert("Project information", tkinter.END,
                                 "Project Path", text="Path", values=[project.path])
                self.tree.insert(
                    "", tkinter.END, "Dataset information", text="Dataset information")
                self.tree.insert("Dataset information", tkinter.END, "Dataset Path", text="Path", values=[
                    project.datasets[index].path])
                self.tree.insert("Dataset information", tkinter.END, "Rows", text="Rows", values=[len(
                    project.datasets[index].data)])  # example: 120000 rows with time from 0 to 59.9995 s.
                # HERE I AM
                textlines = textwrap.wrap((project.datasets[index].metadata["Description"]), width=70)
                if textlines == []:
                    textlines.append("No description given.")
                self.tree.insert("Dataset information", tkinter.END,
                                 "Dataset Description", text="Description", values=[textlines[0]])
                if len(textlines) > 1:
                    for i in range(1, len(textlines)):
                        self.tree.insert("Dataset information", tkinter.END, "Dataset Description %d" % (
                            i), text="", values=[textlines[i]])
                self.tree.insert(
                    "", tkinter.END, "Method", text="Method")
                if project.datasets[index].metadata["Method"] == "HILDE-Homogeneous":
                    self.tree.insert("Method", tkinter.END, value=textwrap.wrap("HILDE (homogeneous noise)"))
                elif project.datasets[index].metadata["Method"] == "HILDE-Heterogeneous":
                    self.tree.insert("Method", tkinter.END, value=textwrap.wrap("HILDE (heterogeneous noise)"))
                elif project.datasets[index].metadata["Method"] == "JULES-Homogeneous":
                    self.tree.insert("Method", tkinter.END, value=textwrap.wrap("JULES (homogeneous noise)"))
                elif project.datasets[index].metadata["Method"] == "JSMURF-Homogeneous":
                    self.tree.insert("Method", tkinter.END, value=textwrap.wrap("JSMURF (homogeneous noise)"))
                else:
                    self.tree.insert("Method", tkinter.END, value=textwrap.wrap("JSMURF (heterogeneous noise)"))
                # Here i will go

                self.tree.insert(
                    "", tkinter.END, "Dataset parameters", text="Dataset parameters")
                self.tree.insert("Dataset parameters", tkinter.END, "Sampling rate in Hz",
                                 text="Sampling rate in Hz",
                                 values=project.datasets[index].metadata["Sampling rate in Hz"])
                self.tree.insert("Dataset parameters", tkinter.END, "Cut-off frequency in Hz",
                                 text="Cut-off frequency in Hz",
                                 values=[project.datasets[index].metadata["Cut-off frequency in Hz"]])
                self.tree.insert("Dataset parameters", tkinter.END, "Filter type", text="Filter type", values=[
                    project.datasets[index].metadata["Filter type"]])

                if project.datasets[index].metadata["Method"] == "HILDE-Homogeneous":
                    self.tree.insert("Dataset parameters", tkinter.END, "Quantile 1", text="Quantile 1", values=[
                        "will be computed by MC simulation"])
                    self.tree.insert("Quantile 1", tkinter.END, "Significance level 1", text="Alpha1", values=[
                        project.datasets[index].metadata["Significance level 1"]])
                    # self.tree.insert("Quantile 1", tkinter.END, "Repetitions 1", text="Repetitions", values=[
                    #     project.datasets[index].metadata["Repetitions"]])
                    self.tree.insert("Quantile 1", tkinter.END, "Repetitions ", text="Repetitions", values=[
                        project.datasets[index].metadata["Repetitions_Hilde"]])

                    self.tree.insert("Dataset parameters", tkinter.END, "Quantile 2", text="Quantile 2", values=[
                        "will be computed by MC simulation"])
                    self.tree.insert("Quantile 2", tkinter.END, "Significance level 2", text="Alpha2", values=[
                        project.datasets[index].metadata["Significance level 2"]])
                    self.tree.insert("Quantile 2", tkinter.END, "Repetitions", text="Repetitions", values=[
                        project.datasets[index].metadata["Repetitions_Hilde"]])

                elif project.datasets[index].metadata["Method"] == "HILDE-Heterogeneous":
                    self.tree.insert("Dataset parameters", tkinter.END, "Quantile 1", text="Quantile 1", values=[
                        "will be computed by MC simulation"])
                    self.tree.insert("Quantile 1", tkinter.END, "Significance level 1", text="Alpha1",
                                     values=[
                                         project.datasets[index].metadata["Significance level 1"]])
                    self.tree.insert("Quantile 1", tkinter.END, "Repetitions ", text="Repetitions", values=[
                        project.datasets[index].metadata["Repetitions_Hilde"]])

                    self.tree.insert("Dataset parameters", tkinter.END,  "Quantile 2", text="Quantile 2", values=[
                        "will be computed by MC simulation"])
                    self.tree.insert("Quantile 2", tkinter.END, "Significance level 2", text="Alpha2",
                                     values=[
                                         project.datasets[index].metadata["Significance level 2"]])
                    self.tree.insert("Quantile 2", tkinter.END, "Repetitions", text="Repetitions", values=[
                        project.datasets[index].metadata["Repetitions_Hilde"]])

                elif project.datasets[index].metadata["Method"] == "JULES-Homogeneous":
                    if project.datasets[index].metadata["Quantile_JULES_HOMOGENEOUS provided"]:
                        self.tree.insert("Dataset parameters", tkinter.END, "Quantile", text="Quantile", values=[
                            project.datasets[index].metadata["Quantile_JULES_HOMOGENEOUS"]])
                    else:
                        self.tree.insert("Dataset parameters", tkinter.END, "Quantile", text="Quantile", values=[
                            "will be computed by MC simulation"])
                        self.tree.insert("Quantile", tkinter.END, "Significance level", text="Alpha",
                                         values=[
                                             project.datasets[index].metadata["Significance level"]])
                        self.tree.insert("Quantile", tkinter.END, "Repetitions", text="Repetitions", values=[
                            project.datasets[index].metadata["Repetitions"]])

                elif project.datasets[index].metadata["Method"] == "JSMURF-Homogeneous":
                    if project.datasets[index].metadata["Quantile_JSMURF_HOMOGENEOUS provided"]:
                        self.tree.insert("Dataset parameters", tkinter.END, "Quantile", text="Quantile", values=[
                            project.datasets[index].metadata["Quantile_JSMURF_HOMOGENEOUS"]])
                    else:

                        self.tree.insert("Dataset parameters", tkinter.END, "Quantile", text="Quantile", values=[
                            "will be computed by MC simulation"])
                        self.tree.insert("Quantile", tkinter.END, "Significance level", text="Alpha",
                                         values=[
                                             project.datasets[index].metadata["Significance level"]])
                        self.tree.insert("Quantile", tkinter.END, "Repetitions", text="Repetitions", values=[
                            project.datasets[index].metadata["Repetitions"]])

                else:
                    self.tree.insert("Dataset parameters", tkinter.END,  "Quantile", text="Quantile", values=[
                        "will be computed by MC simulation"])
                    self.tree.insert("Quantile", tkinter.END, "Significance level", text="Alpha", values=[
                        project.datasets[index].metadata["Significance level"]])
                    self.tree.insert("Quantile", tkinter.END, "Repetitions", text="Repetitions", values=[
                        project.datasets[index].metadata["Repetitions"]])

                maxw = 600
                #600
                for child in self.tree.get_children():
                    self.tree.see(child)
                    w = self.get_size_in_pixels(
                        str(self.tree.item(child)['values']))
                    if (w > maxw):
                        maxw = w
                    for grandchild in self.tree.get_children(child):
                        self.tree.see(grandchild)
                        w = self.get_size_in_pixels(
                            str(self.tree.item(grandchild)['values']))
                        if (w > maxw):
                            maxw = w
                        for ggrandchild in self.tree.get_children(grandchild):
                            self.tree.see(ggrandchild)
                            w = self.get_size_in_pixels(
                                str(self.tree.item(ggrandchild)['values']))

                            if (w > maxw):
                                maxw = w

                self.tree.column(0, width=maxw)
                self.tree.column("#0", width=200, stretch=False)
                #200

            else:
                self.tree.column("#0", width=1000)
                #1000
                self.tree.insert("", tkinter.END, "Project information",
                                 text="Multiple Datasets have been selected, select single dataset to show project information.")
