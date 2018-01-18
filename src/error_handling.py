#
# Matthew Epstein
# exceptions.py
# This file holds the OriginalLines class, which holds a copy of the original
# code that was entered, before it was santized for comments.  This is
# necessary so that error messages can print the original code that erred, as
# opposed to the altered version that the evaluator reads.  Since this class
# already has access to the original code, it makes sense for the function that
# prints errors to be here too.
#

import sys
import global_vars

class OriginalLines:

    # Initializes the class.  Important to note that self.lines gets a deep
    # copy of lines, so that it will not change as lines does.
    def __init__(self, lines):
        self.lines = lines[:]
        self.handle_error = False
        self.error_lineNumber = 0

    # Used for check-error.  If handle_error is set to True, it means that
    # the current function is under the umbrella of a check-error.  It is up
    # to the user to ensure that RaiseException() is not called when this is
    # the case.
    def toggleErrorCheck(self):
    	self.handle_error = not self.handle_error

    # The two functions below are fairly self-explanatory.  getLine() is more
    # complicated than it probably needs to be, but doing it this way accounts
    # for some line-counting confusion.
    def handleError(self):
    	return self.handle_error

    def getLine(self, lineNum):
        try:
            return self.lines[lineNum]
        except:
            return self.lines[lineNum-1]


    # There are a four different "types" of errors that can be raised.  For the
    # default method, the "special" variable is set to 0.  When the error
    # message is the Declaration of Independence, special=1.  When special=2,
    # a claim failed, which isn't quite the same as an error being raised, but
    # still functions very similarly and is thus handled in this function as
    # well.  Finally, in the case where special=3, it means there was an error
    # in a function definition.  In this case the function simply returns and
    # allows the code to run until that error eventually manifests itself once
    # that function is actually called.
    def RaiseException(self, lineNum, numLines, error, special=0):
        if global_vars.function_check and special != 3:
            return "error"
        if global_vars.check_error and special != 2:
            return ("not_error", "Check failed, as expected")

        lines = ""
        for i in range(numLines,0,-1):
            lines = lines + self.getLine(lineNum-i) + "\n"
            if i != 1:
                lines += "      "

        if numLines != 1:
            lineStr = "lines " + str(lineNum-numLines+1) +  "-" + str(lineNum)
        else:
            lineStr = "line " + str(lineNum)

        if special == 1:
            open("dec.txt", 'r')
            decOfInd = [line.rstrip('\n') for line in open("dec.txt")]
            sys.stdout.write("  File {}; {}\n    {}"\
                                .format(global_vars.filename, lineStr, lines))
            for line in decOfInd:
                print line
        else:
            print("  File {}; {}\n    {}{}"\
                    .format(global_vars.filename, lineStr, lines, error))
        exit(0)

