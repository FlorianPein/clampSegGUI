from tkinter import OptionMenu, StringVar, Toplevel
from tkinter.ttk import Button, Entry, Frame, Label
from ...model.R_wrappers import ATF  # TODO: think about architecture etc.
from tkinter import messagebox


class ATFEditor(Toplevel):
    def __init__(self, parent, path, dispatch_event):
        """
        Initialises a window for loading datasets.
        First loads a datafile.
        After waiting for this process, creates a window to select different channels and specify the unit of the data.
        """
        super().__init__(parent)
        self.dispatch_event = dispatch_event
        self.title("ATF data set")
        self.resizable(width=False, height=False)
        waiting_popup = Toplevel(parent)
        waiting_popup.attributes("-topmost", True)
        waiting_label = Label(waiting_popup, text="Preparing data...")
        waiting_label.pack()
        waiting_popup.update()
        try:
            self.atf = ATF(path)
            
            waiting_popup.destroy()
            self.attributes("-topmost", True)

            path_lab = Label(self, text="Path: {}".format(path))
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

            ok = Button(self, text="Load", command=self.load)
            ok_all = Button(self, text="Load All")
            #ok_all = Button(self, text="Load All", command=self.load_all)
            #ok_all.pack(side="middle", fill="x", padx=10, pady=10)
            ok.pack(side="left", fill="x", padx=10, pady=10)
            cancel = Button(self, text="Don't load", command=self.destroy)
            cancel.pack(side="right", fill="x", padx=10, pady=10)

            self.bind('<Return>', self.load)
        except:
            messagebox.showwarning(
                    "Error loading file", path+" could not be loaded.")
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
        
        self.dispatch_event("add_atf_dataset", self.atf, self.params)
        self.destroy()
