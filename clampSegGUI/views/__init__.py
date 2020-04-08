from tkinter import messagebox, Tk
from .layout import MainFrame
import rpy2
import rpy2.rinterface as ri

@ri.rternalize        
def create_rcache_yes_no(prompt: str) -> str:
   if messagebox.askokcancel("Create Rcache", "Create permanent Rcache ? Cancelling will create a temporary Rcache."):
      return "Y"
   else:
      return "n"



class TkView:
   def __init__(self, dispatch_event):
      """
      Initialises the TKview. 
      Defines the Tk root, creates the window and starts packing the frames
      """
      self.dispatch_event = dispatch_event
      self.root = Tk()
      self.root.title("ClampSegGUI")
      self.root.protocol("WM_DELETE_WINDOW", self.on_delete_window)

      self.frame = MainFrame(self.root, dispatch_event)
      self.frame.pack(fill="both", expand=True)

      # prevent certaing resizing problems:
      self.root.update_idletasks() # needed for winfo_X to work properly
      self.root.minsize(width=self.root.winfo_width(),
                        height=self.root.winfo_height()+200)
      try:
         rpy2.rinterface_lib.callbacks.consoleread = create_rcache_yes_no
      except:
         rpy2.rinterface.consoleread = create_rcache_yes_no

   def inform(self, model_data):
      """
      Informs subframes.
      """
      self.frame.toolbar.inform(model_data)
      self.frame.panes.left.tree.inform(model_data)
      self.frame.panes.left.calculate_button.inform(model_data)
      self.frame.panes.left.status_bar.inform(model_data)
      self.frame.panes.right.inform(model_data)

   def on_delete_window(self):
      """
      On delete it will ask whether you want to quit the GUI. Also destroys and quits to prevent freezing.
      """
      if messagebox.askokcancel("Exit clampSegGUI",
                                "Do you want to exit clampSegGUI?"):
         #TODO self.root.destroy() can lead to lots of error messages on closing the programm
         # Idea: Close all subprocesses manually then destroy rest
         #for child in self.root.winfo_children():
         #   child.destroy()
         self.root.destroy()
         self.root.quit()
         # Why do we need both .destroy() and .quit()? Well, the first command
         # terminates the mainloop and deletes all of our widgets, but only if
         # they are children of the main window (so e.g. doesn't close plots).
         # It also waits for running callbacks to return.
         # The second command kills tcl. In practice, however, some windows
         # like a file dialog or a custom Toplevel instance might remain alive
         # and responsive and keep the main window unresponsive but still open.
         # And that's why we need both.
         # In some scenarios, like when a file dialog is open, .destroy() leads
         # to a TclError, e.g "can't invoke "grab" command: application has
         # been destroyed". Catching them here will NOT work because that's not
         # where they are being raised. However, they don't do any harm other
         # than printing annoying messages.
         # Using sys.exit() here will NOT help.

         # TODO: test how it plays with running callbacks, especially
         # calculations, maybe you should terminate them first. Also plots.

   def mainloop(self):
      """
      Starts the mainloop.
      """
      self.root.mainloop()
