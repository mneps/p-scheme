#
# Matthew Epstein
# pm_bools.py
# This file handles pattern matching for booleans.  Since there are only two
# possible patterns (true and false), booleans are the easiest type upton which
# to pattern match.  The PM_Bools class is similar to the PM_Nums, PM_Strings,
# and PM_Lists classes, which are located in pm_nums.py, pm_strings.py, and
# pm_lists.py, respectively.  All four classes hold the same three public
# functions: addPattern(), isComplete(), and matches().
#


import global_vars
import re
from type_checking import *

class PM_Bools:

    # Initializes the PM_Bools class.  self.interval is a list of length two
    # that indicates which booleans have been used thus far.  self.interval[0]
    # corresponds to true; self.interval[1] corresponds to false.  Once
    # self.interval is [True, True], pattern matching is considered complete.
    # Whereas self.interval can be thought of as the union of all the different
    # patterns, self.patterns, is a list of all the individual patterns.  The
    # length of self.patterns will be equal to the number of different patterns
    # a function contains.  This is necessary for determining which pattern a
    # function matches once it is called.
    def __init__(self):
        self.interval = [False, False]
        #self.wild_card = False
        self.patterns = []
        self.arg_name = None


    # This function takes in a pattern as a string which will be of the form
    # [boolean_literal][operator][variable_name].  "true=n" would be a valid
    # pattern, for example.  The boolean literal expressed in the pattern cannot
    # be maybe.  The one exception to the required pattern format is if the
    # pattern is a wild card, in which case the entire pattern will simply be an
    # underscore.  Using __verify_pattern() and __add_helper(), this function
    # verifies the pattern is in a proper format, and updates self.interval and
    # self.patterns.
    def addPattern(self, pattern):
        if pattern == "_":
            if not self.isComplete():
                self.interval = [True, True]
                #self.wild_card = True
                (self.patterns).append([True, True])
                return ("not_error", "good pattern")
            else:
                return ("error", "Error: Pattern matching is already exhaustive")

        (error, val) = self.__verify_pattern(pattern)
        if error == "error":
            return (error, val)
        (op, pattern) = val

        return self.__add_helper(pattern, op)


    # This function checks that the pattern is of a valid format.  If it is not,
    # this function will return the proper error.  Otherwise, it will return
    # the operator and the boolean literal that are expressed within the
    # pattern.
    def __verify_pattern(self, pattern):
        ops = ["<>", "="]
        op = None

        for i in ops:
            if len(pattern.split(i)) == 2:
                op = i
                break

        if op == None:
            return ("error", "Error: Bad pattern")

        pattern_split = pattern.split(op)
        if not isBool(pattern_split[0]) or pattern_split[0] == "maybe":
            return ("error", "Error: Bad pattern")

        if self.arg_name == None:
            self.arg_name = pattern_split[1]
        elif self.arg_name != pattern_split[1]:
            return ("error", "Error: Argument names do not match")

        if isLiteral(pattern_split[1]) or \
                    pattern_split[1] in global_vars.VARIABLE_RESERVED_TERMS:
            return ("error", "Error: Name is reserved")

        if re.sub('\W+', "", pattern_split[1]) != pattern_split[1]:
            return ("error", "Error: Name contains reserved symbol")

        return ("not_error", (op, pattern_split[0]))


    # This funciton updates self.interval and self.patterns.  It will return an
    # error if pattern matching proves to be over-exhaustive.
    def __add_helper(self, pattern, op):
        if (pattern == "true" and op == "=") or \
                                        (pattern == "false" and op == "<>"):
            if self.interval[0]:
                return ("error", "Error: A value matches two patterns")
            self.interval[0] = True
            (self.patterns).append([True, False])
        else:
            if self.interval[1]:
                return ("error", "Error: A value matches two patterns")
            self.interval[1] = True
            (self.patterns).append([False, True])

        return ("not_error", "good pattern")


    # Returns True if pattern matching is complete and returns False otherwise.
    def isComplete(self):
        return (self.interval[0] and self.interval[1])

    
    # Returns True if arg is contained in the i-th pattern and False otherwise.
    # arg will always be either true or false.  The maybe case is handled in
    # node.py.
    def matches(self, arg, i):
        if arg == "true":
            index = 0
        elif arg == "false":
            index = 1

        return self.patterns[i][index]

