from tkinter.ttk import Frame, PanedWindow
from .widgets import Toolbar, LeftTree, RightTree, CalculateButton, StatusBar

# Built-in grid and pack layouts weren't flexible enough (or maybe I was using
# them wrong), so I've implemented my own layout with pack and frames:

class LeftPane(Frame):
   def __init__(self, parent, dispatch_event):
      """
      Initialisies and packs the left tree, the calculate button and the status bar.
      """
      super().__init__(parent)
      self.tree = LeftTree(self, dispatch_event)
      self.calculate_button = CalculateButton(self, dispatch_event)
      self.status_bar = StatusBar(self, dispatch_event)
      self.tree.pack(fill="both", expand=True)
      self.calculate_button.pack(fill="x")
      self.status_bar.pack(side="left", fill="x")

class BothPanes(PanedWindow):
   def __init__(self, parent, dispatch_event):
      """
      Initialises and packsthe left panel and the right tree.
      """
      super().__init__(parent, orient="horizontal")
      self.left = LeftPane(self, dispatch_event)
      self.right = RightTree(self, dispatch_event)
      self.add(self.left)
      self.add(self.right)

class MainFrame(Frame):
   def __init__(self, parent, dispatch_event):
      """
      Initialises and packs the Main frame and adds the panes and the toolbar.
      """
      super().__init__(parent)
      self.toolbar = Toolbar(self, dispatch_event)
      self.panes = BothPanes(self, dispatch_event)
      self.toolbar.pack(fill="x")
      self.panes.pack(fill="both", expand=True)
