""" Module logging
Functionality for logging and a logger shell.
"""

import sys, os, time
import code
import iep
iep.status = None

# todo: enable logging to a file?

# Define prompts
try:
    sys.ps1
except AttributeError:
    sys.ps1 = ">>> "
try:
    sys.ps2
except AttributeError:
    sys.ps2 = "... "

    
original_print = print
def print(*args, **kwargs):
    # Obtain time string
    t = time.localtime()
    preamble = "{:02g}-{:02g}-{:04g} {:02g}:{:02g}:{:02g}: "
    preamble = preamble.format( t.tm_mday, t.tm_mon, t.tm_year, 
                                t.tm_hour, t.tm_min, t.tm_sec)
    # Prepend to args and print
    args = [preamble] + list(args)
    original_print(*tuple(args),**kwargs)
    
    

def splitConsole(stdoutFun=None, stderrFun=None):
    """ splitConsole(stdoutFun=None, stderrFun=None)
    Splits the stdout and stderr streams. On each call
    to their write methods, in addition to the original
    write method being called, will call the given 
    functions.
    Returns the history of the console (combined stdout 
    and stderr).
    Used by the logger shell.
    """
    
    # Split stdout and stderr
    sys.stdout = OutputStreamSplitter(sys.stdout)
    sys.stderr = OutputStreamSplitter(sys.stderr)
    
    # Make them share their history
    sys.stderr._history = sys.stdout._history
    
    # Set defer functions
    if stdoutFun:
        sys.stdout._deferFunction = stdoutFun
    if stderrFun:
        sys.stderr._deferFunction = stderrFun
    
    # Return history 
    return ''.join(sys.stdout._history)


class OutputStreamSplitter:
    """ This class is used to replace stdout and stderr output
    streams. It defers the stream to the original and to
    a function that can be registered.
    Used by the logger shell.
    """
    
    def __init__(self, fileObject):
        
        # Init, copy properties if it was already a splitter
        if isinstance(fileObject, OutputStreamSplitter):
            self._original = fileObject._original
            self._history = fileObject._history
            self._deferFunction = fileObject._deferFunction
        else:
            self._original = fileObject
            self._history = []
            self._deferFunction = self.dummyDeferFunction
    
    def dummyDeferFunction(self, text):
        pass
    
    def write(self, text):
        """ Write method. """
        self._original.write(text)
        self._history.append(text)
        self._deferFunction(text)
        # Show in statusbar
        if iep.status and len(text)>1:
            iep.status.showMessage(text, 5000)
    
    
    def flush(self):
        return self._original.flush()
    
    def closed(self):
        return self._original.closed()
    
    def close(self):
        return self._original.close()
    
    def encoding(self):
        return self._original.encoding()

# Split now, with no defering
splitConsole()

