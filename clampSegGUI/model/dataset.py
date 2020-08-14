import numpy as np
from .R_wrappers import ABF, ATF, calculate_HILDE_HOMOGENEOUS, calculate_HILDE_HETEROGENEOUS, \
    calculate_JSMURF_HETEROGENEOUS, calculate_JSMURF_HOMOGENEOUS, calculate_JULES_HOMOGENEOUS


class Dataset:
    """
   Why can't we read a dataset from a path, you may ask? Because, while ATF
   datasets are all basically the same (three columns that contain time in s,
   current in pA and voltage in mV), ABF datasets can be very different, so
   the user should load the file first into an ABF object, look at its
   structure and only then convert it to a data frame. For more flexibility and
   consistency we have made the process identical the same for ATF and ABF.
   """

    @classmethod
    def fromATF(cls, atf: ATF, *, channels=[2, 3], unit="nS"):
        """
      Creates a dataframe from an ATF object, then uses the class initialization to create a dataset.
      """
        data_frame = atf.as_data_frame(channels, unit)
        return cls(atf.path, data_frame, unit)

    @classmethod
    def fromABF(cls, abf: ABF, *, sweep=1, channels=[1], unit=None):
        """
      Creates a dataframe from an ABF object, then uses the class initialization to create a dataset.
      """
        data_frame = abf.as_data_frame(sweep, channels, unit)
        # print("new", data_frame)
        return cls(abf.path, data_frame, unit)

    def __init__(self, path, data_frame, unit=None):
        """
      This constructor should only be used directly in rare cases. The
      preferred methods for creating a Dataset object are Dataset.fromATF
      and Dataset.fromABF.
      """
        self.path = path  # type: str
        # data_frame is expected to have type rpy2.robjects.vectors.DataFrame
        # with exactly two columns of type rpy2.robjects.vectors.FloatVector:
        self.time, self.data = data_frame
        self.results = {}  # from parameters to fits []
        length_of_array = len(self.time) - 1
        self.metadata = {"Sampling rate in Hz": round(length_of_array / (self.time[length_of_array] - self.time[0]), 6),
                         "Method": "JULES-Homogeneous",
                         "Cut-off frequency in Hz": "NA",
                         "Filter type": "NA",
                         "Description": "Edit metadata via 'Edit datasets'. Please ensure that the values above specify the filter correctly before starting computation. You may also want to edit this description and the values below.",
                         "Quantile_JULES_HOMOGENEOUS provided": False,
                         "Quantile_JSMURF_HOMOGENEOUS provided": False,
                         "Quantile_JSMURF_HETEROGENEOUS provided": False,
                         "Quantile1_HILDE_HOMOGENEOUS provided": False,
                         "Quantile2_HILDE_HOMOGENEOUS provided": False,
                         "Quantile1_HILDE_HETEROGENEOUS provided": False,
                         "Quantile2_HILDE_HETEROGENEOUS provided": False,
                         "Quantile_JULES_HOMOGENEOUS": None,
                         "Quantile_JSMURF_HOMOGENEOUS": None,
                         "Quantile_JSMURF_HETEROGENEOUS": None,
                         "Quantile1_HILDE_HOMOGENEOUS": None,
                         "Quantile2_HILDE_HOMOGENEOUS": None,
                         "Quantile1_HILDE_HETEROGENEOUS": None,
                         "Quantile2_HILDE_HETEROGENEOUS": None,
                         "quantile_jules_store provided": False,
                         "quantile_jsmurf_store provided": False,
                         "quantile_jules_store": None,
                         "quantile_jsmurf_store":  None,
                         "Significance level": 0.05,
                         "Significance level 1": 0.01,
                         "Significance level 2": 0.04,
                         "Repetitions": 10000, "Repetitions_Hilde": 1000, "Unit": unit}


    def calculate_JULES_HOMOGENEOUS(self, params, messages) -> bool:
        """
      Starts the calculation of the fit. 
      If the fit got cancelled, it will return a False value for error reasons, otherwise returns True.
      """
        # `params` is a tuple, see its structure in R_wrappers.calculate
        # `messages` is a function that accepts integers i, r, each and returns
        # bool, it is needed for communication with the GUI (progress bar,
        # cancelling). It can also be an int (a nice default value is 1).
        result = calculate_JULES_HOMOGENEOUS(self.data, params, messages)
        if result is not None:
            self.metadata["Quantile_JULES_HOMOGENEOUS"] = np.asarray(result.q)[0]
            self.metadata["quantile_jules_store"] = np.asarray(result.q)[0]
            self.metadata["Quantile_JULES_HOMOGENEOUS provided"] = True
            self.metadata["quantile_jules_store provided"] = True
            self.results = result
            return False  # For error reasons
        else:
            return True  # If we cancelled, return True

    def calculate_JSMURF_HOMOGENEOUS(self, params, messages) -> bool:
        """
      Starts the calculation of the fit.
      If the fit got cancelled, it will return a False value for error reasons, otherwise returns True.
      """
        # `params` is a tuple, see its structure in R_wrappers.calculate
        # `messages` is a function that accepts integers i, r, each and returns
        # bool, it is needed for communication with the GUI (progress bar,
        # cancelling). It can also be an int (a nice default value is 1).
        result = calculate_JSMURF_HOMOGENEOUS(self.data, params, messages)
        if result is not None:
            self.metadata["Quantile_JSMURF_HOMOGENEOUS"] = np.asarray(result.q)[0]
            self.metadata["quantile_jsmurf_store"] = np.asarray(result.q)[0]
            self.metadata["Quantile_JSMURF_HOMOGENEOUS provided"] = True
            self.metadata["quantile_jsmurf_store provided"] = True
            self.results = result
            return False  # For error reasons
        else:
            return True  # If we cancelled, return True

    def calculate_JSMURF_HETEROGENEOUS(self, params, messages) -> bool:
        """
      Starts the calculation of the fit.
      If the fit got cancelled, it will return a False value for error reasons, otherwise returns True.
      """
        # `params` is a tuple, see its structure in R_wrappers.calculate
        # `messages` is a function that accepts integers i, r, each and returns
        # bool, it is needed for communication with the GUI (progress bar,
        # cancelling). It can also be an int (a nice default value is 1).
        result = calculate_JSMURF_HETEROGENEOUS(self.data, params, messages)
        if result is not None:
            # self.metadata["Quantile_JSMURF_HETEROGENEOUS"] = np.asarray(result.q)
            self.metadata["Quantile_JSMURF_HETEROGENEOUS provided"] = True
            self.results = result
            return False  # For error reasons
        else:
            return True  # If we cancelled, return True

    def calculate_HILDE_HETEROGENEOUS(self, params, messages) -> bool:
        """
      Starts the calculation of the fit.
      If the fit got cancelled, it will return a False value for error reasons, otherwise returns True.
      """
        # `params` is a tuple, see its structure in R_wrappers.calculate
        # `messages` is a function that accepts integers i, r, each and returns
        # bool, it is needed for communication with the GUI (progress bar,
        # cancelling). It can also be an int (a nice default value is 1).
        result = calculate_HILDE_HETEROGENEOUS(self.data, params, messages)
        if result is not None:
            self.metadata["Quantile1_HILDE_HETEROGENEOUS provided"] = True
            self.metadata["Quantile2_HILDE_HETEROGENEOUS provided"] = True
            self.results = result
            return False  # For error reasons
        else:
            return True  # If we cancelled, return True

    def calculate_HILDE_HOMOGENEOUS(self, params, messages) -> bool:
        """
      Starts the calculation of the fit.
      If the fit got cancelled, it will return a False value for error reasons, otherwise returns True.
      """
        # `params` is a tuple, see its structure in R_wrappers.calculate
        # `messages` is a function that accepts integers i, r, each and returns
        # bool, it is needed for communication with the GUI (progress bar,
        # cancelling). It can also be an int (a nice default value is 1).
        result = calculate_HILDE_HOMOGENEOUS(self.data, params, messages)
        if result is not None:
            self.metadata["Quantile1_HILDE_HOMOGENEOUS provided"] = True
            self.metadata["Quantile2_HILDE_HOMOGENEOUS provided"] = True
            self.results = result
            return False  # For error reasons
        else:
            return True  # If we cancelled, return True
