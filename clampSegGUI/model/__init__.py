from functools import wraps
from typing import Any, Dict, List, Optional, Set
from .dataset import Dataset
from .project import Project
import numpy as np


def informs(f):
    """
    A decorator forcing a model method to inform the controller.
    """
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        result = f(self, *args, **kwargs)
        data = self.current_data()
        self.controller.inform(data)
        return result
    return wrapper


class ClampSegModel:
    """
    Please decorate with @informs any public method that changes the model.
    """

    _inform_about = ("n_waiting", "project")

    def current_data(self):
        return {name: getattr(self, name) for name in self._inform_about}

    def __init__(self) -> None:
        self.project = None

    @informs
    def new_project(self) -> None:
        """ 
        Creates a new project and saves it in self.project.
        """
        self.project = Project()

    @informs
    def load_project(self, path: str) -> None:
        """
        Uses the Project.load class funtion to load a project and saves it in self.project.
        """
        self.project = Project.load(path)

    @informs
    def add_atf_dataset(self, atf_object, **params) -> None:
        """
        Reads atf_object and converts it into dataset class.
        """
        dataset = Dataset.fromATF(atf_object, **params)
        self.project.add(dataset)

    @informs
    def add_abf_dataset(self, abf_object, **params) -> None:
        """
        Reads abf_object and converts it into dataset class.
        """
        dataset = Dataset.fromABF(abf_object, **params)
        self.project.add(dataset)

    @informs
    def remove_datasets(self) -> None:
        """
        Removes the datasets selected in the project.selection parameter. 
        """
        indices = self.project.selection
        for i in sorted(indices, reverse=True):
            self.project.remove(i)
        self.project.change_selection_to(None)

    @informs
    def add_to_queue(self, ptr) -> None:
        """
        Adds the dataset identified by the Int value ptr to the calculation queue.
        """
        self.project.add_queue(ptr)
        pass

    @informs
    def remove_from_queue(self, ptr) -> None:
        """
        Removes the dataset identified by the Int value ptr from the calculation queue.
        """
        self.project.remove_queue(ptr)
        pass

    @informs
    def change_selection(self, sel) -> None:
        """
        Changes the dataset selection to the list sel.
        """
        self.project.change_selection_to(sel)
        pass

    @informs
    def calculate(self, message, dataset_setup,errormessage) -> None:
        """
        For every dataset in the queue does the following:
        First checks the parameters. If they are wrong, project an errormessage.
        Then setup the calculate_wait_window.
        Then starts the calculate function of the dataset.
        If this function returns True, it stops the calculation.
        Afterwards it will clear the queue.
        """
        stopcheck = False
        for dataset in self.project.queue:
            if  "NA" in (self.project.datasets[dataset].metadata["Cut-off frequency in Hz"] ,self.project.datasets[dataset].metadata["Filter type"]):
                errormessage(self.project.datasets[dataset])
            else:
                dataset_setup(self.project.datasets[dataset])
                stopcheck = self.project.datasets[dataset].calculate((
                    "bessel",
                    int(self.project.datasets[dataset].metadata["Filter type"].split(
                        '-')[0]),
                    self.project.datasets[dataset].metadata["Cut-off frequency in Hz"],
                    self.project.datasets[dataset].metadata["Sampling rate in Hz"],
                    self.project.datasets[dataset].metadata["Quantile"],
                    self.project.datasets[dataset].metadata["Significance level"],
                    self.project.datasets[dataset].metadata["Repetitions"]), message)
            if stopcheck:
                break
        self.project.clear_queue()

    @informs
    def set_metadata(self, metadata) -> None:
        """
        Starts the set_metadata class function of the project and hands the metadata to said function.
        """
        self.project.set_metadata(metadata)

    @informs
    def save_project_as(self, path: str) -> None:
        """
        Starts the save classfunction of the project, if the path String is not None.
        """
        if path is not None:
            self.project.save(path)
        else:
            print("None argument in path, aborting save")

    def export_fit_as_CSV(self, index, path: str) -> None:
        """
        Saves the Fitparameters of the dataset indicated by the Integer 'index' to a file indicated by the String 'path'.
        """
        xl = np.asarray(self.project.datasets[index].results.xl)
        xr = np.asarray(self.project.datasets[index].results.xr)
        y = np.asarray(self.project.datasets[index].results.y)
        dat = np.asarray((xl, xr, y))
        unit = self.project.datasets[index].metadata["Unit"]
        with open(path, "w") as f:
            f.write('"Time_start","Time_end","Value in [%s]"\n' % (unit))
            for i in range(0, len(dat[0, :])):
                f.write('%f,%f,%f\n' % (dat[0, i], dat[1, i], dat[2, i]))

    def HTML_report(self, path: str) -> None:
        """
        Not Implemented yet.
        """
        raise NotImplementedError

    @property
    def n_waiting(self) -> int:
        """ 
        Returns the length of the calculation queue.
        """
        if self.project:
            return len(self.project.queue)
        else:
            return 0
