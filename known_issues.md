# Known Issues

## Layout

### Issue Nr ###, Short name

+ Status: Resolved in revision nr### / Unresolved
+ Priority: Low / Medium / High
+ Description:Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
+ Reproducible: Yes / No
  + If yes, write a TODO here
+ Notes:
  + Note 1
  + Note 2

## Issues

### Issue Nr 001, Errors on closing

+ Status: Unresolved
+ Priority: Low
+ Description: On closing the GUI, there will be multiple "TypeError: catching classes that do not inherit from BaseException is not allowed" messages.
+ Reproducible: Yes
  + Start the GUI
  + Create a new project and load a dataset
  + Select the dataset and click on "edit datasets". Close the popup window either by clicking cancel or apply.
  + Close the GUI
+ Notes:
  + To close all windows, which are still open, we use both .destroy() and .quit().
  + One of them already removes all defined exceptions, which the tkinter class tries to catch later, thus ignoring the except: codes somewhere in tkinter library
  + Might be related to messagebox from tkinter. 
  + Since adding a messagebox into the initialization of the views it is always present
    + Check messagebox, maybe use an alternative

### Issue Nr 002, Persistent Histogram plots

+ Status: Resolved in revision 336
+ Priority: Medium
+ Description:  Closing the plotwindow without closing the histogram window will leave the histogram window open, reopening the plot and clicking on create histogram will create a new histogram window.
+ Reproducible: Yes
  + Select a dataset
  + Click create plots
  + click Plot histrogram
  + close the Plot window without closing the histogram window
  + can be repeated infinitely to create infinite histogram plots
+ Notes:
  + Force the plotframe to close connected histogram to resolve issue

### Issue Nr. 003, Progressbar not filling

+ Status: Resolved
+ Priority: Medium
+ Description: When calculating multiple datasets, the progressbar does not fill for all dataset calculations except the first
+ Reproducible: Yes / No?, Can no longer reproduce
  + Select multiple datasets
  + click calculate datasets
  + Tried it again, worked this time?
  + Only there for identical datasets. 
+ Notes:
  + Reset counter after every dataset
  + Might be related to the R environment
  + Only there because of identical datasets. The R environment notices it already calculated the quantile but never communicates this to the GUI. 
  + Might be hard to fix

### Issue Nr. 004, Large number dataset selection

+ Status: Resolved in revision 340
+ Priority: Low
+ Description: When there is a very large of datasets loaded, the left tree selection frame does not have a scrollbar. Some datasets cannot be selected, because they are out of frame.
+ Reproducible: Yes
  + Load a very large amount of datasets
+ Notes:
  + Create a scrollbar for the left treeview
  + Can still scroll through the treeview with mouse wheel, scrollfunction and arrowkeys

### Issue Nr. 005,  Disabling scrollbar via resizing

+ Status: Resolved in revision 337
+ Priority: Medium
+ Description: Resizing up to a size, where the Scrollbar for the right treeview is completely filled and thus disabled, leads to the scrollbar permanently disabling. Resizing to a size where the scrollbar is required again does not reactivate it.
+ Reproducible: Yes
  + Select a single dataset
  + Resize the window to a size where the horizontal scrollbar deactivates
  + Resize to a smaller size, requiring a horizontal scrollbar
+ Notes:
  + What is this sorcery?

### Issue Nr. 006, Slowdown 

+ Status: Unresolved
+ Priority: Low
+ Description: While there is a very large amount of datasets loaded, considerable slowdown is experienced while scrolling through the selection of the datasets.
+ Reproducible: Yes, partially
  + Load a very large amount of datasets
  + scroll through the selection of datasets in the left treeview
  + Strongly dependent on individual CPU core
+ Notes:
  + No idea how to resolve this
  + Either reduce amount of @informs per time, amount of @Informs in code, parallelize code, reduce CPU load of @informs, use stronger CPU


### Issue Nr. 007, Edit wrong dataset

+ Status: Resolved in revision 347
+ Priority: High
+ Description: Editing the last dataset changes also the values of the first dataset.
+ Reproducible: Yes
  + start a new project, add several datasets
  + edit the last dataset
  + look at the first dataset
+ Notes:
  + this bug might cause further instabilities to the project


### Issue Nr. 008, Default values edit datasets

+ Status: Resolved in Revision 348 and xxx
+ Priority: Medium
+ Description: Edited values are the default values when editing a new dataset.
+ Reproducible: Yes
  + edit one dataset
  + open edit datasets
+ Notes:
  + Default values should always be the current setted values of the dataset that is edited.
  + a new dataset should have the following values:
     - Sampling rate in Hz: the value that is calculated when dataset is loaded
     - Cut-off: Are we able to read this from the dataset? Otherwise NA or leave it empty
     - Filter type: same as for Cut-off
     - descritpion: Edit metadata via 'Edit datasets'. Please ensure that the values above specify the filter correctly before starting computation. You may also want to edit this description and the values below.
     - Provide data for quantile simulation should be activated
     - Significance level: 0.05
     - Repetitions: 10000
  + after a computation (for the computed dataset(s) only):
     - Provide quantile should be active
     - Quantile: the calculated quantile


### Issue Nr. 009, Abf should be default

+ Status: Resolved in Revision 349
+ Priority: Medium
+ Description: Abf should be default type in add datasets


### Issue Nr. 010, Number of bins

+ Status: Resolved in revision nr. 358
+ Priority: Medium
+ Description: Number of bins in the histogram plots cannot be changed.
+ Reproducible: Yes
  + open histogram
  + we often see only 3 bins
+ Notes:
  + default number should be the square root choice ceil(sqrt(n))
  + if it does not look well we might want to disable it temporarily
  + ideal solution would be an option to change the number of bins
  + ideally zooming should change the bins


### Issue Nr. 011, Loading of MC simulations

+ Status: probably resolved, testing required
+ Priority: Medium
+ Description: Monte-Carlo simulations have to be repeated when the program is closed.
+ Reproducible: Yes
  + do a computation that requires MC simulations
  + close and reopen the program
  + do a computation that requires the same MC simulations
  + this requires a new simulation
+ Notes:
  + it hopefully requires just a change of the parameters of monteCarloSimulation.R
  + we can do this together when skyping the next time


### Issue Nr. 012, Rename Edit datasets

+ Status: Resolved (nothing to do, just a missunderstanding)
+ Priority: Medium
+ Description: Edit datasets should be renamed to Edit dataset


### Issue Nr. 013, Rename in Edit datasets

+ Status: Resolved in Revision 349
+ Priority: Medium
+ Description: In Edit datasets Provide data for quantile simulation should be Provide parameters for quantile simulation


### Issue Nr. 014, Calculation windows

+ Status: Resolved in revision nr. 358
+ Priority: Medium
+ Description: Calculation window should like this:

while calculating quantiles
Title: Computation for Dataset XXX

progressbar

Currently computing quantile for Dataset:
XXX
Press Stop! button to stop computation for current dataset.

while calculating fit
Title: Computation for Dataset XXX

no progressbar (if possible)

Calculating fit for Dataset:
XXX
This computation cannot be interrupted and may take a few minutes.


### Issue Nr. 015, Empty description

+ Status: Resolved in Revision 350
+ Priority: Medium
+ Description: Saving an empty description is not possible. Doing so causes an expection in the terminal but no visible reaction for the user.
+ Reproducible: Yes
  + in Edit dataset: remove everything written in the decription field and press Apply.
+ Notes:
  + this should either be possible (better solution) or cause an error message


### Issue Nr. 016, Scrollbar for description

+ Status: Resolved in Revision 351
+ Priority: Low
+ Description: In Edit datasets there is no scrollbar for the description field.
+ Notes:
  + it is still possible to use the mouse wheel
  + scrollbar can be added permanently


### Issue Nr. 017, Resizing Edit datasets

+ Status: Resolved in revision nr. 358
+ Priority: Low
+ Description: Resizing Edit datsets is not leading to desired results.
+ Notes:
  + if this is difficult to fix one might simply disable resizing


### Issue Nr. 018, Verticle scrollbar disappears

+ Status: Unresolved
+ Priority: Low
+ Description: Maximizing the window correcly reduces the verticle scrollbar, but redoing does not change the scrollbar.
+ Reproducible: Yes
  + maximize window, redo it
+ Notes:
  + Find out what gets triggered on maximization ( For resizing it is configure ) bind the on_resize function  from right_tree.py to it. 
  + resizing the window or similar actions allows to use the scrollbar once again
  + verticle scrollbar also allows to scroll very far to the right such that huge amount of white space appears


### Issue Nr. 019, Edit datasets window

+ Status: Resolved in revision nr. 358
+ Priority: Low
+ Description: Words left of the entry fields are partially centred and partially aligned to the left. 0.2cm (or so) space between the left and between the text and the entry fields would probably improve the window.


### Issue Nr. 020, Scrollbar datasets

+ Status: Resolved in Revision 352
+ Priority: Low
+ Description: It might be more intuitive to have the scrollbar for the datasets on the right side.


### Issue Nr. 021, Freezing of main window

+ Status: Partially resolved (note in documentation) in Revision 364 
+ Priority: Low
+ Description: The main window freezes if one opens a subwindow.
+ Reproducible: Yes
+ Notes:
  + This behavious is probably necessary
  + We might have to inform the user about it (maybe just in the documentation)


### Issue Nr. 022, No file type in save as

+ Status: Resolved in revision 366
+ Priority: Low
+ Description: Save as has no tile type.
+ Reproducible: Yes
+ Notes:
  + It would be nice to have file type csg
  + Having no file type causes an exception in the console when clicking on cancel
  + exception appears only once and it not reproducible later on


### Issue Nr. 023, Errors in readABF

+ Status: Resolved in revision 366
+ Priority: Low
+ Description: If reading an abf file causes, this is not handled by the GUI.
+ Reproducible: Yes
  + some datasets in ABF_Hentschke are not supported by readABF
  + loading them with the GUI leads to an error in the console
  + but the loading window is only partially created without reasonable feedback to the user
+ Notes:
  + closing the window allows to progress with the work in the GUI
  + a short error message would be nice, it does not have to be the message from readABF


### Issue Nr. 024, Colour in histogram plots

+ Status: Resolved in revision 366
+ Priority: Low
+ Description: If points are selected in the plot (blue colour), they are still in red in the histogram.
+ Reproducible: Yes
+ Notes:
  + use the same colour in the histogram

