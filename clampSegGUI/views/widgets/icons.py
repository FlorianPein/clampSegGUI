"""
Don't import this module at the beginning of a file, rather import it right
where you need it. The reason is the following: tkinter.PhotoImage raises
RuntimeError if Tk isn't initialized yet.
Python modules act as singletons, so you don't have to worry about multiple
initialization attempts.
"""

import os
from tkinter import PhotoImage, TkVersion

icons = {}
keys = ("new_project", "load_project", "save_project", "save_project_as",
            "add_datasets", "remove_datasets", "edit_datasets",
            "export_fit_as_CSV", "create_plots", "calculate")

package_path = os.path.dirname(__file__)
icons_path = os.path.join(package_path, "..", "icons")
png_supported = TkVersion >= 8.6
if png_supported:
   ext=".png"
else:
   ext=".gif"
for name in keys:
   key=os.path.join(icons_path, name+ext)
   # loading, converting from 128x128 to 64x64, storing so it won't get GCd:
   icons[name] = PhotoImage(file=key).subsample(2)
