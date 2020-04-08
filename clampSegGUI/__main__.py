from .controller import ClampSegController
from .model import ClampSegModel

from .views import TkView

def run():
   """
   Initializes the Controller and TkView class.
   Subscribes the TkView and then starts the tk mainloop.
   """
   controller = ClampSegController(ClampSegModel)
   tk_view = TkView(controller.dispatch_event)
   controller.subscribe(tk_view)
   tk_view.mainloop()

if __name__ == "__main__":
   run()
