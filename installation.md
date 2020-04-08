# Installation guide

## Introduction

Please note that so far we have only tested the program systematically on a Linux system, but further support for other operating systems is planned.

To use clampSegGUI, unzip the zip file and ensure that you have the dependencies explained below. Start the GUI by running the file `run.pyw`. From the top level directory of the program, where `run.pyw` is, you have to type:

    python run.pyw

Here, `python` should refer to at least Python 3.5.3 If there are multiple installations of Python on your system, your command might need to be more specific, e.g. `python3 run.pyw` or `python3.5 run.pyw`.

## Dependencies

Before running clampSegGUI, check whether you have the following requirements and install them if necessary (the program also performs checks on startup):

1. Python 3.5.3 or later

    You can check this by typing 'python' (or a more specific command as explained above) in the command line. For further support, in particular how to install python please visit [https://www.python.org/](https://www.python.org/).

2. This Python version can import `tkinter`
    This is almost always the case unless you've built Python manually. You can test this by starting Python and typing

        import tkinter

    You should get no message. If this fails, the solution is highly system-dependent. On a Debian-based system like Ubuntu you might want to do `sudo apt-get install tk-dev`, then rebuild Python with `make`. A much more easier solution would be to use pre-compiled Python binaries. The probability is high that they are already in your system's official repository, but alternatives exist as well (including commercial ones [ActivePython](https://www.activestate.com/products/activepython/)).

3. This Python version has the packages `numpy` (version 1.11.0 or later), `matplotlib` (version 1.5.1 or later) and `rpy2` (version 2.9.4 or later).

    You can check this by starting this python version (check it especially carefully if you have multiple Python versions on your system) and typing

        import numpy
        import matplotlib
        import rpy2

    You should get no message. To check their versions type:

        numpy.__version__
        matplotlib.__version__
        rpy2.__version__
    
    If this fails, please see [NumPy docs](https://docs.scipy.org/doc/numpy/user/install.html), [Matplotlib docs](https://matplotlib.org/users/installing.html) or [rpy2 docs](http://rpy.sourceforge.net/rpy2/doc-dev/html/overview.html#installation), respectively.

4. Statistical programming language R 3.2.0 or later

    You can check this by typing 'R' in the command line. For further support, in particular how to install R, please visit [https://www.r-project.org/](https://www.r-project.org/).

5. R packages `clampSeg` and `readABF`

    You can check this (they will not be installed, unless you used them before) by starting R (type R in the command line) and typing

        library(clampSeg)
        library(readABF)

    You can install these packages by typing

        install.packages(c('clampSeg', 'readABF'))

    For further help how to install R packages, please visit [https://www.r-project.org/](https://www.r-project.org/).

6. Your `rpy2` installation works correctly with the R version you have. Type into your Python interpreter:

        from rpy2.robjects.packages import importr
        readABF = importr("readABF")
        readABF.__version__

It should return `'1.0.1'` or later. If there are problems with that, they are, sadly, non-trivial to fix. Carefully reinstalling rpy2 is an option. [rpy2 docs](http://rpy.sourceforge.net/rpy2/doc-dev/html/overview.html#installation) might be helpful.

### License

```
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

