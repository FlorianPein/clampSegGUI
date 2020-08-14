import os
from tkinter import Toplevel, Label, TOP, BOTH, Button
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.widgets import RectangleSelector
import matplotlib.pyplot as plt
import numpy as np

up = {',': '.', '.': 'o', 'o': 'o'}
down = {',': ',', '.': ',', 'o': '.'}


class MatplotlibFrame(Toplevel):
    def line_select_callback(self, eclick, erelease):
        """
        Line selection callback function.
        """
        #'eclick and erelease are the press and release events'
        self.x_start, self.y_start = eclick.xdata, eclick.ydata
        self.x_end, self.y_end = erelease.xdata, erelease.ydata

    def __init__(self, dataset):
        """
        Initialises the plotwindow. Creates a dedicated canvas and adds it to the Toplevel.
        Reads all relevant data and saves them in a usable way.
        """
        # Initialising
        super().__init__()
        fig, self.axes = plt.subplots(1, 1)
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.dataset = dataset
        self.unit = dataset.metadata["Unit"]
        self.time = np.asarray(dataset.time)
        self.data = np.asarray(dataset.data)
        self.histframe = None
        self.histcanvas = None
        self.histaxes = None
        # Setting Titles, Drawing Plots
        self.axes.set_title("Scatter Plot")  # TODO Find better Name
        self.title(os.path.basename(self.dataset.path))
        Label(self, text="Select points by click-and-drag to create a square\nAfter selection press Enter\nPressing u will unselect all datapoints\n+/- to change thickness of points\nPress ,/. to change opacity").pack(side=TOP)
        # Implementing
        self.alpha = 5
        self.selecting, self.adding = False, False
        self.x_selected, self.y_selected = np.array([]), np.array([])
        self.x_start, self.y_start = None, None
        self.marker = ","
        self.scatter()
        # Packing etc.
        #self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.histbutton = Button(
            self, text="Plot histogram", compound="bottom", command=self.hist)
        self.histbutton.pack(side="left", fill="x", expand=True)
        self.canvas.draw()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def on_exit(self):
        """
        Destroys the histogram frame, if it exists, before closing the plot frame.
        """
        if (self.histframe):
            self.histframe.destroy()
        self.destroy()


    def hist(self):
        """
        Function to coordinate the dedicated histogram plots.
        """
        def create_histframe():
            """
            Creates a frame dedicated for the histogram plots.
            """
            self.histframe = Toplevel()
            self.histframe.title(os.path.basename(self.dataset.path))
            fighist, self.histaxes = plt.subplots(1, 1)
            self.histcanvas = FigureCanvasTkAgg(fighist, master=self.histframe)
            self.histaxes.set_title("Histogram Plot")
            histtoolbar = NavigationToolbar2Tk(self.histcanvas, self.histframe)
            histtoolbar.update()
            self.histcanvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            self.histcanvas.draw()
            self.draw_hist()
        if (self.histframe is None):
            create_histframe()
        else:
            if (not self.histframe.winfo_exists()):
                create_histframe()
            else:
                self.histframe.focus_set()
                self.histframe.lift()

    def draw_hist(self):
        """
        Draws the histogram in the dedicated histogram frame.
        """
        self.bins = self.histaxes.hist(self.data, color="black",bins=int(np.sqrt(len(self.data))))[
            1]  # counts and patches currently not used
        self.histaxes.set_xlabel("Conductance ["+self.unit+"]")
        self.histaxes.set_ylabel("Density")
        if len(self.x_selected):
            self.histaxes.hist(self.y_selected, bins=self.bins,
                               hatch="////", color="blue", linestyle="dotted")
        self.histcanvas.draw()

    def plot_fit(self):
        """
        Plots the calculated fit, if it exists.
        """
        def create_plot_array(results):
            """
            Creates an resorted array for easier plotting.
            """
            xl = np.asarray(results.xl)
            xr = np.asarray(results.xr)
            y = np.asarray(results.y)
            arrlist = []
            for n in range(len(xl)):
                arrlist.append((xl[n], y[n]))
                arrlist.append((xr[n], y[n]))
            return np.asarray(arrlist)

        if self.dataset.results:
            results = self.dataset.results
            fit_array = create_plot_array(results)
            self.axes.plot(
                fit_array[:, 0], fit_array[:, 1], "r", label="idealization")
            self.canvas.draw()
        else:
            return

    def scatter(self):
        """
        Plots all datapoints as a scatterplot.
        """
        def onkey(event):
            """
            Checks for different key events.
            """
            if event.key == "+":
                self.marker = up[self.marker]
                for line in self.axes.lines:
                    line.set_marker(self.marker)
                    line.set_markeredgecolor('none')
                self.canvas.draw()
            elif event.key == "-":
                self.marker = down[self.marker]
                for line in self.axes.lines:
                    line.set_marker(self.marker)
                    line.set_markeredgecolor('none')
                self.canvas.draw()
            elif event.key == "." and self.alpha < 5:
                self.alpha += 1
                for line in self.axes.lines:
                    line.set_alpha(self.alpha/5)
                self.canvas.draw()
            elif event.key == "," and self.alpha > 1:
                self.alpha -= 1
                for line in self.axes.lines:
                    line.set_alpha(self.alpha/5)
                self.canvas.draw()
            elif event.key == "u":
                self.x_selected, self.y_selected = np.array([]), np.array([])
                clearSelection()
                self.canvas.draw()
            elif event.key == "a":
                self.adding = not self.adding
                self.selector.set_active(True)
            elif event.key == 'enter':
                draw_selection()

        def draw_selection():
            """
            Draws the selection in a dedicated color.
            """
            try:
                xMin, xMax = (self.x_start, self.x_end) if self.x_start < self.x_end else (
                    self.x_end, self.x_start)
                yMin, yMax = (self.y_start, self.y_end) if self.y_start < self.y_end else (
                    self.y_end, self.y_start)
                idx = (xMin < self.time) & (self.time < xMax) & (
                    yMin < self.data) & (self.data < yMax)
                x1 = (self.time[idx])
                y1 = (self.data[idx])
                if self.adding:
                    self.x_selected = np.concatenate((self.x_selected, x1))
                    self.y_selected = np.concatenate((self.y_selected, y1))
                else:
                    self.x_selected, self.y_selected = x1, y1
                    clearSelection()

                if self.histaxes:
                    self.histaxes.hist(
                        self.y_selected, bins=self.bins, hatch="////", color="blue", linestyle="dotted")
                if self.histcanvas:
                    self.histcanvas.draw()
                self.selecting, self.adding = False, False
                self.axes.plot(x1, y1, "b"+self.marker)
                self.axes.lines[-1].set_markeredgecolor('none')
                self.axes.lines[-1].set_alpha(self.alpha/5)
                self.canvas.draw()
                self.plot_fit()
            except IndexError:
                return

        def clearSelection():
            """
            Clears the selection, if possible.
            """
            try:
                while len(self.axes.lines) > 1:
                    self.axes.lines.remove(self.axes.lines[-1])
                if self.histaxes:
                    self.histaxes.cla()
                    self.draw_hist()
                self.plot_fit()
                self.canvas.draw()
            except IndexError:
                pass
        self.axes.plot(self.time, self.data, "k"+self.marker)
        self.axes.set_xlim(xmin=0, xmax=np.max(self.time))
        self.axes.set_xlabel("Time [s]")
        self.axes.set_ylabel("Conductance ["+self.unit+"]")
        if len(self.x_selected):
            self.axes.plot(self.x_selected, self.y_selected, "b"+self.marker)
            self.axes.lines[-1].set_markeredgecolor('none')
            self.axes.lines[-1].set_alpha(self.alpha/5)

        self.selector = RectangleSelector(self.axes, self.line_select_callback,
                                          drawtype='box', useblit=True,
                                          button=[1, 3],
                                          spancoords='pixels',
                                          interactive=True)

        self.canvas.mpl_connect('key_press_event', onkey)

    def inform(self, data):
        """
        Informs the plot window. If a fit exists, it will plot it.
        """
        self.plot_fit()
