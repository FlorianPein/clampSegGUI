from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Button, Entry, Frame, Label
from ...model.R_wrappers import ATF   # TODO: think about architecture etc.
from .test import test1


class MultipleATFEditor(Toplevel):
    def __init__(self, parent, paths, dispatch_event):
        """
        Initialises a window for loading datasets.
        First loads a datafile.
        After waiting for this process, creates a window to select different channels and specify the unit of the data.
        """
        super().__init__(None)
        self.parent = parent
        self.dispatch_event = dispatch_event
        self.title("ATF data set")
        self.editor = None
        self.paths = paths
        self.paths_new = []
        if not test1.alpha:
            self.path = paths[0]
            self.atf = ATF(self.path)
            self.values = None
            self.values1 = None
            self.resizable(width=False, height=False)
            waiting_popup = Toplevel(parent)
            waiting_popup.attributes("-topmost", True)
            waiting_label = Label(waiting_popup, text="Preparing data...")
            waiting_label.pack()
            waiting_popup.update()
            waiting_popup.destroy()
        try:
            if not test1.alpha:
                self.attributes("-topmost", True)

                self.attributes("-topmost", True)

                path_lab = Label(self, text="Path: {}".format(self.paths[0]))
                path_lab.pack(padx=10, pady=10)

                channel_selector = Frame(self)
                warning = Label(channel_selector,
                                text="Select a channel, optionally divide it by another channel")
                dividends = self.atf.names
                # if you have to change this constant, change it in self.params, too
                divisors = dividends + ['none']
                self.dividend_var = StringVar(self)  # usually contains current
                self.divisor_var = StringVar(self)  # usually contains voltage
                self.dividend_var.set(dividends[1])
                self.divisor_var.set(divisors[2])
                dividend_menu = OptionMenu(channel_selector,
                                           self.dividend_var,
                                           *dividends)
                divisor_menu = OptionMenu(channel_selector,
                                          self.divisor_var,
                                          *divisors)
                warning.pack()
                dividend_menu.pack()
                divisor_menu.pack()

                channel_selector.pack(padx=10, pady=10)

                unit_selector = Frame(self)
                unit_lab = Label(unit_selector, text="Unit: ")
                unit_lab.pack(side="left", fill="x")
                self.unit = Entry(unit_selector)
                self.unit.delete(0, "end")
                self.unit.insert(0, "nS")
                self.unit.pack(side="left", fill="x")
                unit_selector.pack(padx=10, pady=10)

                self.ok = Button(self, text="Load", command=self.load)

                self.ok.pack(side="left", fill="x", padx=10, pady=10)

                self.ok_all = Button(self, text="Load All", command=self.load_all)

                self.ok_all.pack()
                self.ok_all.place(relx=0.5, rely=0.88, anchor=CENTER)
                cancel = Button(self, text="Don't load", command=self.destroy)
                cancel.pack(side="right", fill="x", padx=10, pady=10)
                self.bind('<Return>', self.load)


        except:
            messagebox.showwarning(
                "Error loading file", self.paths[0] + " could not be loaded.")
            self.destroy()

    @property
    def params(self):
        """
        Parameters which will be given to the controller.
        """

        dividend = self.dividend_var.get()
        divisor = self.divisor_var.get()
        channels = [self.atf.names.index(dividend) + 1]
        if divisor != 'none':
            channels += [self.atf.names.index(divisor) + 1]
        return dict(channels=channels, unit=self.unit.get())

    def load(self, test=None):
        """
        Gives the dataset and parameters to the controller, then destroys the editor.
        """
        self.ok.config(state=DISABLED)
        self.ok_all.config(state=DISABLED)
        if len(self.paths) > 0:
            del self.paths[0]

        self.dispatch_event("add_atf_dataset", self.atf, self.params)
        if len(self.paths) != 0:
            test1.alpha = False
            Editor = MultipleATFEditor
            self.editor = Editor(self.parent, self.paths, self.dispatch_event)

        else:
            test1.alpha = True
        self.destroy()

    def load_all(self, test=None):
        """
        Gives the datasets with same channel names , channel units , same number of channels and parameters( same
        parameters to all data sets with same  channel names , channel units , same number of channels  )to the
        controller, then destroys the editor.
        """
        self.ok_all.config(state=DISABLED)
        self.ok.config(state=DISABLED)
        self.values = self.atf.names
        values = set(self.values)
        params1 = self.params
        for path in self.paths:
            self.atf = ATF(path)
            dividends = self.atf.names
            dividends = set(dividends)


            if len(self.values) == len(dividends) and (values == dividends):
                self.dispatch_event("add_atf_dataset", self.atf, params1)

            else:
                self.paths_new.append(path)

        if len(self.paths_new) != 0:
            test1.alpha = False
            Editor = MultipleATFEditor
            self.editor = Editor(self.parent, self.paths_new, self.dispatch_event)

        else:
            test1.alpha = True

        self.destroy()
