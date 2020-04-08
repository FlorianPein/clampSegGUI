from tkinter.ttk import Treeview, Scrollbar
import tkinter
import os

class LeftTree(Treeview):

   def __init__(self, parent, dispatch_event):
      """
      Initialises the treeview for selecting the datasets.
      """
      super().__init__(parent, columns = ['Queue', 'Analysed'])
      self.dispatch_event = dispatch_event
      for name in self['columns']:
         self.heading(name, text=name, anchor = "w")
         self.column(name, width=100, anchor = "center")
      self.scrollbar_y = Scrollbar(self, orient="vertical")
      self.scrollbar_y.config(command=self.yview)
      #self.configure(height=1000)
      self.configure(yscrollcommand=self.scrollbar_y.set) 
      self.scrollbar_y.pack(side="right", fill="y")
      self.column("#0", width=130)
      self.column(0, width=60)
      self.column(1, width=60)
      self.bind("<Button-1>", self.on_left_click)
      self.bind("<<TreeviewSelect>>", self.on_left_select)
      
   def inform(self, data):
      """
      Informs the treeview. 
      If a dataset is not present in the treeview but is present in the list of datasets, it adds the dataset. 
      If a dataset is present in the treeview but not in the list of datasets, it removes that dataset.
      """
      project = data["project"]
      self.project_exists = project is not None
      if project:
         if project.datasets:
            for name in project.datasets:
               if self.exists(name):
                  self.set(name, column="Analysed", value= "YES" if name.results else "NO")
                  self.set(name, column="Queue", value= u'\u2611' if self.index(name) in project.queue else u'\u2610')
               else:
                  self.insert("", tkinter.END, name, text = os.path.basename(name.path), values = [u'\u2610',  "YES" if name.results else "NO"])
            for name in self.get_children():
               if name not in str(project.datasets):
                  self.delete(name)
         else:
            self.delete(*self.get_children())   

   def on_left_click(self,event):
      """
      Identifies a click in the queue row and checks / unchecks the queue box.  
      """
      row = self.identify_row(event.y)
      col = self.identify_column(event.x)
      if self.column(col)['id'] == 'Queue':
         if row != "":
            queued = self.set(row, column="Queue")
            if queued == u'\u2610':
               self.set(row, column="Queue", value=u'\u2611')
               self.dispatch_event('add_to_queue',self.index(row))
            else:
               self.set(row, column="Queue", value=u'\u2610')
               self.dispatch_event('remove_from_queue',self.index(row))

   def on_left_select(self,event):
      """
      Creates a list of the datasets selected in the Treeview and dispatches it to the controller.
      """
      sel = []
      for iid in self.selection():
         sel.append(self.index(iid))
      self.dispatch_event('change_selection',sel)