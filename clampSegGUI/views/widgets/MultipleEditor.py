from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Button, Entry, Frame, Label
from ...model.R_wrappers import ABF  # TODO: think about architecture etc.
from .test import test1


class MultipleABFEditor(Toplevel):
    def __init__(self, parent, paths, dispatch_event):
        """
        Initialises a window for loading datasets.
        First loads a datafile.
        After waiting for this process, creates a window to select different channels and specify the unit of the data.
        """
        super().__init__(None)
        self.parent = parent
        self.dispatch_event = dispatch_event
        self.title("ABF data set")
        self.editor = None
        self.paths = paths
        self.paths_new = []
        if not test1.alpha:
            self.path = paths[0]
            self.abf = ABF(self.path)
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
                dividends = self.abf._abf[self.abf._abf.names.index("channelNames")]
                units = self.abf._abf[self.abf._abf.names.index("channelUnits")]
                for i in range(len(self.abf._abf[self.abf._abf.names.index("channelNames")])):
                    dividends[i] = dividends[i] + " " + \
                                   self.abf._abf[self.abf._abf.names.index("channelUnits")][i]
                divisors = dividends + 'None'
                self.dividend_var = StringVar(self)  # usually contains current
                self.divisor_var = StringVar(self)  # usually contains voltage
                self.dividend_var.set(dividends[0])
                self.divisor_var.set(divisors[1])
                self.dividends = dividends
                self.units = units
                self.divisors = divisors
                path_lab = Label(self, text="Path: {}".format(self.paths[0]))
                path_lab.pack(padx=10, pady=10)
                channel_selector = Frame(self)
                warning = Label(channel_selector,
                                text="Select a channel, optionally divide it by another channel")

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
        # print(dividend)
        divisor = self.divisor_var.get()
        # print(divisor)
        channels = [self.dividends.index(dividend) + 1]
        # print("Channels", channels)

        if divisor != 'None':
            channels += [self.divisors.index(divisor) + 1]
        return dict(sweep=1, channels=channels, unit=self.unit.get())

    def load(self, test=None):
        """
        Gives the dataset and parameters to the controller, then destroys the editor.
        """
        self.ok.config(state = DISABLED)
        self.ok_all.config(state=DISABLED)
        if len(self.paths) > 0:
            del self.paths[0]

        self.dispatch_event("add_abf_dataset", self.abf, self.params)
        if len(self.paths) != 0:
            test1.alpha = False
            Editor = MultipleABFEditor
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
        self.ok_all.config(state = DISABLED)
        self.ok.config(state=DISABLED)
        self.values = ABF.names1(self.abf)
        values = set(self.values)
        self.values1 = ABF.units1(self.abf)
        values1 = set(self.values1)
        params1 = self.params
        for path in self.paths:
            self.abf = ABF(path)
            dividends = self.abf._abf[self.abf._abf.names.index("channelNames")]
            for i in range(len(self.abf._abf[self.abf._abf.names.index("channelNames")])):
                dividends[i] = dividends[i] + " " + \
                               self.abf._abf[self.abf._abf.names.index("channelUnits")][i]
            units = self.abf._abf[self.abf._abf.names.index("channelUnits")]
            dividends = set(dividends)
            units = set(units)

            if len(self.values) == len(dividends) and len(self.values1) == len(units) and (values == dividends) and (
                    values1 == units):
                self.dispatch_event("add_abf_dataset", self.abf, params1)

            else:
                self.paths_new.append(path)

        if len(self.paths_new) != 0:
            test1.alpha = False
            Editor = MultipleABFEditor
            self.editor = Editor(self.parent, self.paths_new, self.dispatch_event)

        else:
            test1.alpha = True

        self.destroy()
