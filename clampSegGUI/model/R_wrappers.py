import sys
import warnings
from contextlib import contextmanager
from functools import wraps
from rpy2.robjects import r
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import IntVector
from rpy2.rinterface import NULL, RRuntimeWarning

import numpy as np

# from rpy2.rinterface import RRuntimeError
try:
    from rpy2.rinterface import RRuntimeError
except ImportError:
    from rpy2.rinterface_lib.embedded import RRuntimeError


@contextmanager
def RWarnings(level):
    """
    There are two levels: 'error' and 'ignore'. With 'error', R warnings are
    treated as R errors and can be caught as RRuntimeError. With 'ignore', they
    are ignored and not even printed. Beware that all Python warning filters
    will be reset after using this context manager.
    """
    new = {"error": 2, "ignore": -1}[level]
    old = r.getOption("warn")
    warnings.filterwarnings("ignore", category=RRuntimeWarning)
    r.options(warn=new)
    yield
    r.options(warn=old)
    warnings.resetwarnings()


# Historically, we were aiming for the following two-stage approach:

# try:
#    with RWarnings("error"):
#       pass # run some R code that might give warnings
# except RRuntimeError as e:
#   # show a message, let the user continue, if he choses to continue then do:
#   try:
#      with RWarnings("ignore"):
#         pass # run the same R code again
#   except RRuntimeError as e:
#      pass # show the ultimate error message

# However, it was found to be impractical: we don't get any warnings with our
# data. We either get errors or everything works fine. This means that we
# couldn't test the feature unless we craft an artificial dataset specifically
# for this purpose. We might do it in the future, but there is no urgent need.
# As for the warning that aren't data-related, we usually don't want the user
# to see them anyway, so we just use with RWarnings("ignore") everywhere.


# Checking whether the required R packages are installed and importing them:
with RWarnings("ignore"):
    try:
        importr("readABF")
    except RRuntimeError:
        sys.exit("Your R installation can't load readABF (maybe it isn't installed)")
    try:
        importr("clampSeg")
    except RRuntimeError:
        sys.exit("Your R installation can't load clampSeg (maybe it isn't installed)")


class ReadIntoRError(Exception):
    pass


class ClampSegError(Exception):
    pass


def may_raise(exception_cls):
    """
    Silences the exceptions specified.
    """

    def silencer(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                with RWarnings("ignore"):
                    return f(*args, **kwargs)
            except RRuntimeError as e:
                raise exception_cls(e.args[0])

        return wrapper

    return silencer


r("""
readATF <- function (path) {
   read.table(path, skip=9, header=T, sep="\t") # expected structure: Time.s, Im.pA, Vm.mV
}

adaptATF <- function (y, channels, unit) { # nS is nanoSiemens
   # the `channels` argument behaves like its counterpart in ABF
   result <- data.frame(y[,1])
   colnames(result) <- "Time [s]"
   if (length(channels) == 1) {
      i <- channels[1]
      data <- y[,i]
   } else if (length(channels) == 2) {
      i <- channels[1]
      j <- channels[2]
      data <- y[,i]/y[,j]
   } else {
      stop('argument "channels" should be of length 1 or 2')
   }
   result[[paste0("Data [", unit, "]")]] <- data
   result
}
""")


class ATF:
    @may_raise(ReadIntoRError)
    def __init__(self, path):
        """
        Short initialisation of the ATF class. Reads the dataset from a path.
        """
        self._atf = r.readATF(path)
        self.names = list(self._atf.names)
        self.path = path

    @may_raise(ReadIntoRError)
    def as_data_frame(self, channels, unit):
        """
        Preferred use of the ATF class. Outputs the dataset as a dataframe for further computation.
        """
        unit = NULL if unit is None else unit
        channels = IntVector(channels)
        return r["adaptATF"](self._atf,
                             channels=channels,
                             unit=unit)


class ABF:

    @may_raise(ReadIntoRError)
    def __init__(self, path):
        """
        Short initialisation of the ABF class. Reads the dataset from a path.
        """
        self._abf = r.readABF(path)

    @property
    def path(self):
        """
        Short access to the path variable.
        """
        # Yes, the notation for accessing a field in a ListVector is that long.
        # [0] because we want a normal Python str, not an rpy2 StrVector.
        return self._abf[self._abf.names.index("path")][0]

    def names1(self):
        """
        Short access to the path variable.
        """
        # Yes, the notation for accessing a field in a ListVector is that long.
        # [0] because we want a normal Python str, not an rpy2 StrVector.

        return list(self._abf[self._abf.names.index("channelNames")])

    def units1(self):
        return list(self._abf[self._abf.names.index("channelUnits")])

    @may_raise(ReadIntoRError)
    def as_data_frame(self, sweep, channels, unit):
        """
        Preferred use of the ABF class. Outputs the dataset as a dataframe for further computation.
        """
        # the only supported `type` argument to `as.data.frame` is "one"
        # this is intended, we never need other types in our GUI
        sweep = NULL if sweep is None else sweep
        unit = NULL if unit is None else unit
        channels = IntVector(channels)

        return r["as.data.frame"](self._abf, sweep=sweep,
                                  type="one",
                                  channels=channels,
                                  unit=unit)


fit_to_xy = r("""
function (input) {
   # simplified, from plot.stepblock in stepR:
   xl <- input$idealization$leftEnd
   xr <- input$idealization$rightEnd
   ys <- input$idealization$value
   q  <- input$q
   list(ys = ys, q=q, xl=xl, xr=xr)
}
""")


class Fit:
    def __init__(self, fit):
        """
        Reads the fit from the R environment and saves them to a python environment.
        """
        xy = fit_to_xy(fit)
        self.xl = xy[xy.names.index("xl")]
        self.xr = xy[xy.names.index("xr")]
        self.y = xy[xy.names.index("ys")]
        self.q = xy[xy.names.index("q")]



FILTER_TEMPLATE = """
clampSeg::lowpassFilter(type = {filter_type!r},
                        param = list(pole = {pole},
                                       cutoff = {cutoff}/{sampling_rate}),
                        len = 11L, sr = {sampling_rate})
"""

DEFAULT_OPTIONS1 = """
list(simulation = "vector",
     save = list(workspace = c("vector"), fileSystem = c("vector")),
     load = list(workspace = c("vector"), fileSystem = c("vector")))
"""

DEFAULT_OPTIONS2 = """
list(simulation = "matrix",
     save = list(workspace = c("matrix"), fileSystem = c("matrix")),
     load = list(workspace = c("matrix"), fileSystem = c("matrix")))
"""


@may_raise(ClampSegError)
def calculate_JULES_HOMOGENEOUS(data, params, messages):
    """
    Calculates the fit and quantile, if necessary. 
    First sets up all the variables.
    Then starts the quantile calculation.
    Afterwards starts the fit calculation.
    If any of this fails, returns None to signal failure.
    """
    # Method:JULES HOMOGENEOUS
    filter_type, pole, cutoff, sampling_rate = params[0:4]
    filter = r(FILTER_TEMPLATE.format(filter_type=filter_type,
                                      pole=pole,
                                      cutoff=cutoff,
                                      sampling_rate=sampling_rate))

    quantile, alpha, repetitions = params[4:]
    # alpha is significance level
    quantile = NULL if quantile is None else float(quantile)
    # quantile = NULL means: has to be computed from alpha and repetitions
    alpha = NULL if alpha is None else alpha
    repetitions = NULL if repetitions is None else repetitions
    options1 = r(DEFAULT_OPTIONS1)

    with RWarnings("ignore"):
        try:
            if quantile == NULL:
                messages(-1, repetitions, 1)  ## Setting up the calculate_wait_window
                quantile = r("clampSeg::getCritVal")(n=len(data), filter=filter,
                                                     alpha=alpha,
                                                     r=repetitions, messages=messages,
                                                     options=options1)
            messages(-2, repetitions, 1)  ## Setting up the calculate_wait_window
            fit = r("clampSeg::jules")(data, filter, q=quantile, output="eachStep")
            return Fit(fit)
        except RRuntimeError:
            print("User Interrupt Of Monte Carlo Simulations")
        return None


@may_raise(ClampSegError)
def calculate_JSMURF_HOMOGENEOUS(data, params, messages):
    """
    Calculates the fit and quantile, if necessary.
    First sets up all the variables.
    Then starts the quantile calculation.
    Afterwards starts the fit calculation.
    If any of this fails, returns None to signal failure.
    """
    # Method:JSMURF HOMOGENEOUS
    filter_type, pole, cutoff, sampling_rate = params[0:4]
    filter = r(FILTER_TEMPLATE.format(filter_type=filter_type,
                                      pole=pole,
                                      cutoff=cutoff,
                                      sampling_rate=sampling_rate))

    quantile, alpha, repetitions = params[4:]
    # alpha is significance level
    quantile = NULL if quantile is None else float(quantile)
    # quantile = NULL means: has to be computed from alpha and repetitions
    alpha = NULL if alpha is None else alpha
    repetitions = NULL if repetitions is None else repetitions
    options1 = r(DEFAULT_OPTIONS1)
    with RWarnings("ignore"):
        try:
            if quantile == NULL:
                messages(-1, repetitions, 1)  ## Setting up the calculate_wait_window
                quantile = r("clampSeg::getCritVal")(n=len(data), filter=filter,
                                                     family="jsmurfPS",
                                                     alpha=alpha,
                                                     r=repetitions, messages=messages,
                                                     options=options1)

            messages(-2, repetitions, 1)  ## Setting up the calculate_wait_window
            fit = r("clampSeg::jsmurf")(data, filter, q=quantile, output="eachStep", family="jsmurfPS")
            return Fit(fit)
        except RRuntimeError:
            print("User Interrupt Of Monte Carlo Simulations")
        return None


@may_raise(ClampSegError)
def calculate_JSMURF_HETEROGENEOUS(data, params, messages):
    """
    Calculates the fit and quantile, if necessary.
    First sets up all the variables.
    Then starts the quantile calculation.
    Afterwards starts the fit calculation.
    If any of this fails, returns None to signal failure.
    """
    # Method:JSMURF HETEROGENEOUS
    filter_type, pole, cutoff, sampling_rate = params[0:4]
    filter = r(FILTER_TEMPLATE.format(filter_type=filter_type,
                                      pole=pole,
                                      cutoff=cutoff,
                                      sampling_rate=sampling_rate))

    quantile, alpha, repetitions = params[4:]
    # alpha is significance level
    quantile = NULL if quantile is None else float(quantile)
    # quantile = NULL means: has to be computed from alpha and repetitions
    alpha = NULL if alpha is None else alpha
    repetitions = NULL if repetitions is None else repetitions
    options2 = r(DEFAULT_OPTIONS2)
    with RWarnings("ignore"):
        try:
            if quantile == NULL:
                messages(-1, repetitions, 1)  ## Setting up the calculate_wait_window
                quantile = r("clampSeg::getCritVal")(n=len(data), filter=filter,
                                                     family="hjsmurf",
                                                     alpha=alpha,
                                                     r=repetitions, messages=messages,
                                                     options=options2)

            messages(-2, repetitions, 1)  ## Setting up the calculate_wait_window

            fit = r("clampSeg::jsmurf")(data, filter, q=quantile, output="eachStep", family="hjsmurf")

            return Fit(fit)
        except RRuntimeError:
            print("User Interrupt Of Monte Carlo Simulations")
        return None


@may_raise(ClampSegError)
def calculate_HILDE_HETEROGENEOUS(data, params, messages):
    """
    Calculates the fit and quantile, if necessary.
    First sets up all the variables.
    Then starts the quantile calculation.
    Afterwards starts the fit calculation.
    If any of this fails, returns None to signal failure.
    """
    # Method:HILDE HETEROGEEOUS
    filter_type, pole, cutoff, sampling_rate = params[0:4]
    filter = r(FILTER_TEMPLATE.format(filter_type=filter_type,
                                      pole=pole,
                                      cutoff=cutoff,
                                      sampling_rate=sampling_rate))

    quantile1, quantile2, alpha1, alpha2, repetitions = params[4:]
    # alpha is significance level
    quantile1 = NULL if quantile1 is None else float(quantile1)
    # quantile = NULL means: has to be computed from alpha and repetitions
    quantile2 = NULL if quantile2 is None else float(quantile2)
    alpha1 = NULL if alpha1 is None else alpha1
    alpha2 = NULL if alpha2 is None else alpha2
    repetitions = NULL if repetitions is None else repetitions
    options2 = r(DEFAULT_OPTIONS2)
    with RWarnings("ignore"):
        try:
            if quantile1 == NULL:
                messages(-1, repetitions, 1)  ## Setting up the calculate_wait_window
                quantile1 = r("clampSeg::getCritVal")(n=len(data), filter=filter,
                                                      family="hjsmurf",
                                                      alpha=alpha1,
                                                      r=repetitions, messages=messages,
                                                      options=options2)
            if quantile2 == NULL:
                messages(-1, repetitions, 1)  ## Setting up the calculate_wait_window
                quantile2 = r("clampSeg::getCritVal")(n=len(data), filter=filter,
                                                      family="2Param",
                                                      alpha=alpha2,
                                                      r=repetitions, messages=messages,
                                                      options=options2)

            messages(-2, repetitions, 1)  ## Setting up the calculate_wait_window
            fit = r("clampSeg::hilde")(data, filter, q1=quantile1, family="hjsmurf", q2=quantile2, output="eachStep", method="2Param")

            return Fit(fit)
        except RRuntimeError:
            print("User Interrupt Of Monte Carlo Simulations")
        return None


@may_raise(ClampSegError)
def calculate_HILDE_HOMOGENEOUS(data, params, messages):
    """
    Calculates the fit and quantile, if necessary.
    First sets up all the variables.
    Then starts the quantile calculation.
    Afterwards starts the fit calculation.
    If any of this fails, returns None to signal failure.
    """
    # Method:HILDE HOMOGENEOUS
    filter_type, pole, cutoff, sampling_rate = params[0:4]
    filter = r(FILTER_TEMPLATE.format(filter_type=filter_type,
                                      pole=pole,
                                      cutoff=cutoff,
                                      sampling_rate=sampling_rate))

    quantile1, quantile2, alpha1, alpha2, repetitions = params[4:]
    # alpha is significance level
    quantile1 = NULL if quantile1 is None else float(quantile1)
    # quantile = NULL means: has to be computed from alpha and repetitions
    quantile2 = NULL if quantile2 is None else float(quantile2)
    alpha1 = NULL if alpha1 is None else alpha1
    alpha2 = NULL if alpha2 is None else alpha2
    repetitions = NULL if repetitions is None else repetitions
    options2 = r(DEFAULT_OPTIONS2)
    options1 = r(DEFAULT_OPTIONS1)
    with RWarnings("ignore"):
        try:
            if quantile1 == NULL:
                messages(-1, repetitions, 1)  ## Setting up the calculate_wait_window
                quantile1 = r("clampSeg::getCritVal")(n=len(data), filter=filter,
                                                      family="jsmurfPS",
                                                      alpha=alpha1,
                                                      r=repetitions, messages=messages,
                                                      options=options1)
            if quantile2 == NULL:
                messages(-1, repetitions, 1)  ## Setting up the calculate_wait_window
                quantile2 = r("clampSeg::getCritVal")(n=len(data), filter=filter,
                                                      family="LR",
                                                      alpha=alpha2,
                                                      r=repetitions, messages=messages,
                                                      options=options2)

            messages(-2, repetitions, 1)  ## Setting up the calculate_wait_window

            fit = r("clampSeg::hilde")(data, filter, q1=quantile1, family="jsmurfPS", q2=quantile2, output="eachStep", method="LR")


            return Fit(fit)
        except RRuntimeError:
            print("User Interrupt Of Monte Carlo Simulations")
        return None
