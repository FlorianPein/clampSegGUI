import os
from tkinter import IntVar, Toplevel, StringVar
from tkinter.ttk import Progressbar, Button, Label
from tkinter import messagebox
import rpy2.rinterface as ri
import numpy as np

class waitWindowProgressBar(Toplevel):
    def __init__(self,parent=None):
        """
        Initialises the calculate wait window. Waits for other processes to finish, then packs everything. 
        messages, setup_dataset and stop are the functions that change the layout of the frame.
        """
        super().__init__(parent)
        self.title("Setting up.......")
        #self.attributes("-topmost", True)
        self.pb_val = IntVar(self)
        self.pb_val.set(0)
        self.pb = Progressbar(self, length = 400, variable=self.pb_val)
        self.pb.pack(pady=20, padx=20)
        self.pb.configure(maximum=10)
        self.labeltext = StringVar()
        self.labeltext.set("Waiting for other process.....")
        self.waiting_label = Label(self, textvariable=self.labeltext)
        self.waiting_label.configure(anchor="center")
        self.waiting_label.pack(pady=20, padx=20, fill='both', expand=True)
        self.stopbutton = Button(self, text="Stop!", compound="bottom", command = self.stop)
        self.stopbutton.pack(side="left",fill="x",expand=True)
        self.stopflag=0
        self.update()
    
    def stop(self):
        """
        Sets the stopflag to 1, thus stopping the calculation.
        """
        self.stopflag=1
    
    def setup_dataset(self,dataset): 
        """
        Sets up the calculation wait window for the different stages of calculation.
        """
        self.dataset = dataset
        self.title("Calculating Dataset %s"%os.path.basename(dataset.path))
        self.waiting_label.pack(pady=20, padx=20)
        self.update()
    
    def errormessage(self, dataset):
            messagebox.showwarning("Invalid parameters", "Dataset %s was skipped in the computation because of invalid parameters. Please configure Cut-off frequency and / or Filter type."%os.path.basename(dataset.path))

    def return_function(self):
        """
        Returns two functions for further use in the model.
        """    
        @ri.rternalize        
        def messages(i,r,each):
            """
            Messages function given to the R environment.
            Gives feedback on the state of the Monte-Carlo simulation. 
            """
            self.pb.step()
            count = np.asarray((i,r))
            if (count[0]==-1):
                self.title("Computation for Dataset %s"%os.path.basename(self.dataset.path))
                self.pb.pack(pady=20, padx=20)
                self.pb_val.set(0)
                self.stopbutton["state"] = "normal" 
                self.pb.configure(maximum=int(self.dataset.metadata["Repetitions"])) 
                self.labeltext.set("Currently computing quantile for Dataset:\n%s \n Press Stop! button to stop computation for current dataset." %os.path.basename(self.dataset.path))
            if (count[0]==-2):
                self.pb.pack_forget()
                self.labeltext.set("Calculating fit for Dataset:\n%s\nThis computation cannot be interrupted and may take a few minutes."%os.path.basename(self.dataset.path))    
                self.stopbutton["state"] = "disabled" 
                self.waiting_label.pack(pady=20, padx=20)
            self.update()
            return self.stopflag    
        return messages, self.setup_dataset, self.errormessage