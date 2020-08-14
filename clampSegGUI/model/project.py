from .dataset import Dataset
import pickle


class Project:
    def __init__(self):
        """
        Initialises the project. sets the path to None, initialises lists for the path, datasets, selection and queue.
        """
        self.path = None  # type: Optional[str]
        self.datasets = []  # type: List[Dataset]
        self.selection = []
        self.queue = []

    @classmethod
    def load(cls, path):
        """
        Loads a project from a file and sets it as the new project.
        'path' is a string with the location of the file.
        First pickled data is integer with the amount of datasets saved in the file. Then loads that many datasets and adds them to the project.
        """
        project = cls()
        project.path = path
        with open(path, 'rb') as f:  # TODO Testing, What happens if i open different files?
            for _ in range(pickle.load(f)):
                project.add(pickle.load(f))
        return project

    def save(self, path: str):
        """
        The `path` argument should never be None even if `self.path` is valid.
        Handling of invalid paths is done outside of this function. If you call
        it manually, you should handle invalid paths (including None) yourself.
        """
        with open(path, 'wb') as f:
            pickle.dump(len(self.datasets), f)
            for name in self.datasets:
                pickle.dump(name, f)
                pass
        self.path = path
        pass

    def add(self, dataset: Dataset):
        """
        Adds the dataset 'dataset' to the project.
        """
        self.datasets.append(dataset)

    def remove(self, i):
        """
        Removes dataset with index 'i' from the project.
        """
        del self.datasets[i]

    def add_queue(self, ptr):
        """
        Adds the dataset with index 'ptr' to the calculation queue.
        """
        self.queue.append(ptr)

    def remove_queue(self, ptr):
        """
        Removes the dataset with index 'ptr' from the calculation queue.
        """
        self.queue.remove(ptr)

    def clear_queue(self):
        """
        Clears the calculation queue.
        """
        self.queue = []

    # def set_metadata(self, metadata):
    #     """
    #     Sets the metadata given in 'metadata' for all datasets in the selection.
    #     """
    #     for name in self.selection:
    #         self.datasets[name].metadata = metadata.copy()

    def set_metadata(self, metadata):
        """
        Sets the metadata given in 'metadata' for all datasets in the selection.
        """
        for name in self.selection:
            self.datasets[name].metadata = metadata[name].copy()

    def change_selection_to(self, sel):
        """
        Changes the selection to the selection given by 'sel'.
        """
        self.selection = []
        if sel is not None:
            for name in sel:
                self.selection.append(name)
