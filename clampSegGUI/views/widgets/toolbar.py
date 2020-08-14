import os
from collections import OrderedDict
from typing import Optional
from tkinter import filedialog, messagebox
from tkinter.ttk import Button, Frame, Label, Treeview, Scrollbar

# from clampSegGUI.views.widgets.multiple_datasets_editor import MultipleEditor

from .MultipleEditor import MultipleABFEditor
from .Multiple_atf_Editor import MultipleATFEditor
from .dataset_editor import datasetEditor
from .mplframe import MatplotlibFrame
from .test import test1
from ...model.R_wrappers import ABF


class Toolbar(Frame):
    ## Changes in keys should also be changed in icons.py
    keys = ("new_project", "load_project", "save_project", "save_project_as",
            "add_datasets", "remove_datasets", "edit_datasets",
            "export_fit_as_CSV", "create_plots")

    @staticmethod
    def label(s: str) -> str:
        """
        Similar to str.capitalize but handles whitespace and words like HTML
        differently.
        """
        return ' '.join((s[0].upper() + s[1:]).split('_'))

    def __init__(self, parent, dispatch_event):
        super().__init__(parent)
        self.dispatch_event = dispatch_event
        self.buttons = OrderedDict()
        from .icons import icons
        for key in self.keys:
            self.buttons[key] = Button(
                self, text=self.label(key), compound="bottom")
            self.buttons[key].config(image=icons[key],
                                     command=getattr(self, key))
        # self.buttons["load_project"].config(image=u"\u128449" )

        for i, button in enumerate(self.buttons.values()):
            button.pack(side="left", fill="x", expand=True)

        # relevant state:
        self.project = None
        self.project_exists = False
        self.project_path = None

        # children windows:
        self.editor = None

    def inform(self, data):
        """
        Informs the Toolbar class. 
        Enables or disables the appropriate buttons depending on whether there is a project open, there is a selection and whether there is a dataset with calculated fit.
        """
        for button in self.buttons.values():
            button.config(state="disabled")

        for key in ["new_project", "load_project"]:
            self.buttons[key].config(state="normal")

        self.project = data["project"]
        self.project_exists = self.project is not None

        if self.project:
            for key in ["save_project", "save_project_as", "add_datasets"]:
                self.buttons[key].config(state="normal")
            self.project_path = self.project.path  # type: Optional[str]

            if self.project.datasets:
                sel = self.project.selection

                if len(sel) > 0:
                    for key in ["remove_datasets", "edit_datasets", "create_plots"]:
                        self.buttons[key].config(state="normal")
                    for i in sel:
                        if self.project.datasets[i].results:
                            self.buttons["export_fit_as_CSV"].config(
                                state="normal")

    def new_project(self):
        """
        Opens a messagebox asking the user to confirm that he/she wants to open a new project. 
        If yes dispatches the controller to start a new project.
        """
        if self.project_exists:
            if not messagebox.askokcancel("New empty project",
                                          "Do you want to create a new project? "
                                          "The current project will be closed."):
                return
        self.dispatch_event("new_project")

    def load_project(self):
        """
        Opens a messagebox asking the user to confirm that he/she wants to load a new project. 
        If yes opens a filedialog to open the project file and dispatches the controller to load the selected file.
        """
        if self.project_exists:
            if not messagebox.askokcancel("Load project",
                                          "Do you want to load another project? "
                                          "The current project will be closed."):
                return
        path = filedialog.askopenfilename(title="Load project",
                                          filetypes=[
                                              ('clampSegGUI project files', '.csg'),
                                              ('All files', '.*')
                                          ])
        if path:
            self.dispatch_event("load_project", path)

    def save_project(self):
        """
        If there is a project path, saves the file. Else it starts the save_project_as() function
        """
        if self.project_path:
            self.dispatch_event("save_project_as", self.project_path)
        else:
            self.save_project_as()

    def save_project_as(self):
        """
        Saves the project at a path selected by a filedialog.
        """
        if self.project_path:
            _, name = os.path.split(self.project_path)
        else:
            name = "Untitled.csg"
        path = filedialog.asksaveasfilename(title="Save project as...",
                                            defaultextension=".csg",  # TODO: testing
                                            filetypes=[
                                                ('csg', '.csg'),
                                                ('All files', '.*')

                                            ],
                                            initialfile=name)
        if type(path) == str:
            if path != "":
                self.dispatch_event("save_project_as", path)

    def add_datasets(self):
        """
        Adds a dataset.
        First opens a filedialog to select the datasets.
        Then for every file selected opens the appropriate editor.
        """
        test1.alpha = False
        paths = filedialog.askopenfilenames(title="Add datasets",
                                            filetypes=[
                                                ('Axon Binary Files', '.abf'),
                                                ('ATF', '.atf'),
                                                ('All files', '.*')])
        # TODO: display tkinter message in case of error
        # TODO: Check ob path bereits im project ist. Falls ja skip it ?

        lst1 = []
        lst2 = []

        skipped = set()  # type: Set[str]
        for path in paths:
            _, ext = os.path.splitext(path)
            ext = ext.lower()
            if ext == ".atf":
                lst2.append(path)
            elif ext == ".abf":
                lst1.append(path)
            else:
                skipped.add(ext)

        if len(lst1) != 0:
            Editor = MultipleABFEditor
            self.editor = Editor(self, lst1, self.dispatch_event)
        if len(lst2) != 0:
            Editor = MultipleATFEditor
            self.editor = Editor(self, lst2, self.dispatch_event)


        if skipped:
            messagebox.showwarning("Warning",
                                   "Skipped files with unknown extensions {}".
                                   format(", ".join(skipped)))



        test1.alpha = False

    def remove_datasets(self):
        """
        Removes the selected datasets via communication with the controller.
        """
        if not messagebox.askokcancel("Remove selected datasets",
                                      "This will remove the selected datasets from the project."):
            return
        self.dispatch_event("delete_selected_dataset")

    def edit_datasets(self):
        """
        Starts the datasetEditor for the selected datasets.
        """
        Editor = datasetEditor
        self.editor = Editor(self.dispatch_event, self.project)
        self.editor.grab_set()
        self.wait_window(self.editor)
        self.editor = None

    def new_dataset_from_existing(self):
        """
        Not implemented yet
        """
        raise NotImplementedError  # TODO

    def HTML_report(self):
        """
        Not implemented yet
        """
        raise NotImplementedError  # TODO

    def create_plots(self):
        """
        Opens the plotframe for all selected datasets.
        """
        for i in self.project.selection:
            plotframe = MatplotlibFrame(self.project.datasets[i])
            self.dispatch_event("plot_frame_subscribe", plotframe)

    def export_fit_as_CSV(self):
        """
        Saves the calculated fit for all selected datasets. Savefile is selected via a filedialog.
        """
        for i in self.project.selection:
            if self.project.datasets[i].results:
                name = os.path.basename(self.project.datasets[i].path)
                name = os.path.splitext(name)[0] + ".csv"
                path = filedialog.asksaveasfilename(title=os.path.basename(self.project.datasets[i].path),
                                                    filetypes=(
                                                        ("csv files", "*.csv"), ("all files", "*.*")),
                                                    initialfile=name)
                if path:
                    self.dispatch_event("export_as_csv", i, path)
