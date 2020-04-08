import numpy as np
from .R_wrappers import ABF, ATF, calculate

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
   def fromATF(cls, atf: ATF, *, channels=[2,3], unit="nS"):
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
      return cls(abf.path, data_frame, unit)


   def __init__(self, path, data_frame, unit = None):
      """
      This constructor should only be used directly in rare cases. The
      preferred methods for creating a Dataset object are Dataset.fromATF
      and Dataset.fromABF.
      """
      self.path = path # type: str
      # data_frame is expected to have type rpy2.robjects.vectors.DataFrame
      # with exactly two columns of type rpy2.robjects.vectors.FloatVector:
      self.time, self.data = data_frame
      self.results = {} # from parameters to fits []
      length_of_array=len(self.time)-1
      self.metadata = { "Sampling rate in Hz" : length_of_array/(self.time[length_of_array]-self.time[0]),
                        "Cut-off frequency in Hz" : "NA",
                        "Filter type": "NA",
                        "Description" : "Edit metadata via 'Edit datasets'. Please ensure that the values above specify the filter correctly before starting computation. You may also want to edit this description and the values below.",
                        "Quantile provided" : False,
                        "Quantile" : None,
                        "Significance level": 0.05,
                        "Repetitions" : 10000,
                        "Unit" : unit}

   def calculate(self, params, messages) -> bool:
      """
      Starts the calculation of the fit. 
      If the fit got cancelled, it will return a False value for error reasons, otherwise returns True.
      """
      # `params` is a tuple, see its structure in R_wrappers.calculate
      # `messages` is a function that accepts integers i, r, each and returns
      # bool, it is needed for communication with the GUI (progress bar,
      # cancelling). It can also be an int (a nice default value is 1).
      result = calculate(self.data, params, messages)
      if result is not None:
         self.metadata["Quantile"] = np.asarray(result.q)[0]
         self.metadata["Quantile provided"] = True
         self.results = result
         return False # For error reasons
      else:
         return True # If we cancelled, return True
