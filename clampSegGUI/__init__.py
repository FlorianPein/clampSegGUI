import sys
"""
Checks for imports and version of python.
"""
if sys.version_info < (3, 5):
   sys.exit("Please use Python 3.5 or later to run clampSegGUI")

try:
   import tkinter
except:
   sys.exit("Your Python installation doesn't can't import tkinter (maybe it isn't installed)")

try:
   import numpy
except:
   sys.exit("Your Python installation can't import numpy (maybe it isn't installed)")

try:
   import matplotlib
   matplotlib.use('Agg') 
except:
   sys.exit("Your Python installation can't import matplotlib (maybe it isn't installed)")

try:
   import rpy2
except:
   sys.exit("Your Python installation can't import rpy2 (maybe it isn't installed)")

# In this file, we test the installation status of the required Python packages
# The installation status of the required R packages is tested in R_wrappers.py
