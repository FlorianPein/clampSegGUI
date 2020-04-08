from tkinter.ttk import Button, Frame, Label, Scrollbar

from .toolbar import Toolbar
from .left_tree import LeftTree
from .right_tree import RightTree
from .calculate_wait_window import waitWindowProgressBar

class CalculateButton(Button):

   def __init__(self, parent, dispatch_event):
      """
      Builds the Calculatebutton.
      """
      
      from .icons import icons
      super().__init__(parent,
                       text = "Start computation for selected dataset(s)",
                       image = icons["calculate"],
                       compound = "left",
                       command = lambda: dispatch_event("calculate", waitWindowProgressBar()))
      self.dispatch_event = dispatch_event

   def inform(self, data):
      """
      Activates / Deactivates the button if the Queue is non-empty/empty.
      """
      
      self["state"] = "normal" if data["n_waiting"] else "disabled"

class StatusBar(Label):

   def __init__(self, parent, dispatch_event):
      """
      Initialises the Statusbar.
      """
      
      super().__init__(parent)
      self.dispatch_event = dispatch_event

   def inform(self, data):
      """
      Informs the Statusbar of how many datasets are awaiting computation.
      """
      
      n = data["n_waiting"]
      self["text"] = "Number of datasets waiting for computation: {}".format(n)
