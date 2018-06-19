#
# Matthew Epstein
# pm_nums.py
# This file handles pattern matching for numbers.  The PM_Nums class is similar
# to the PM_Bools, PM_Strings, and PM_Lists classes, which are located in
# pm_bools.py, pm_strings.py, and pm_lists.py, respectively.  All four classes
# hold the same three public functions: addPattern(), isComplete(), and
# matches().  Both this class and the PM_Strings class rely heavily on the
# Intervals class, found in intervals.py.
#


import global_vars
import re
from intervals import *
from type_checking import *

class PM_Nums:

    # Initializes the PM_Nums class.  self.interval is an instance of the real
    # numbers version of the Intervals class.  It keeps track of which numbers
    # have been used in a pattern and which have not.  Once self.interval is
    # equal to the (-inf, inf) interval, pattern matching is considered
    # complete.  Whereas self.interval can be thought of as the union of all the
    # different patterns, self.patterns, is a list of all the individual
    # patterns. The length of self.patterns will be equal to the number of
    # different patterns a function contains.  This is necessary for determining
    # which pattern a function matches once it is called.
    def __init__(self):
        self.interval = Intervals(REALS)
        self.patterns = []
        self.arg_name = None


    # This function takes in a pattern as a string which will be of the form
    # [number_literal][operator][variable_name][operator*][number_literal*].
    # The final two parts (denoted with an asterisk) are optional, but both must
    # be present if one is included.  "1.8=n" and "12<n<=15" are both valid
    # patterns, for example.  The one exception to the required pattern format
    # is if the pattern is a wild card, in which case the entire pattern will
    # simply be an underscore.  Using __verify_pattern() and __add_helper(),
    # this function verifies the pattern is in a proper format, and updates
    # self.interval and self.patterns.
    def addPattern(self, pattern):
        if pattern == "_":
            if not (self.interval).isComplete():
                all_reals = Intervals(REALS)
                all_reals.union_interval(ninf, inf, False, False)
                self.interval = all_reals
                (self.patterns).append(all_reals)
                return ("not_error", "good pattern")
            else:
                return ("error", "Error: Pattern matching is already exhaustive")

        (error, val) = self.__verify_pattern(pattern)
        if error == "error":
            return (error, val)
        (op, pattern) = val

        detect_eq = lambda x: True if "=" in x else False

        if op == "=":
            return self.__add_helper(pattern, pattern, True, True)
        elif op == "<>":
            first = self.__add_helper(ninf, pattern, False, False)
            if first[0] == "error":
                return first
            return self.__add_helper(pattern, inf, False, False, True)
        elif op == "<" or op == "<=":
            return self.__add_helper(pattern, inf, detect_eq(op), False)
        elif op == ">" or op == ">=":
            return self.__add_helper(ninf, pattern, False, detect_eq(op))
        else: # multiple ops (eg. a<n<b)
            return self.__add_helper(pattern[0], pattern[1], \
                                            detect_eq(op[0]), detect_eq(op[1]))


    # This function checks that the pattern is of a valid format.  If it is not,
    # this function will return the proper error.  Otherwise, it will return
    # the operator and the list literal that are expressed within the
    # pattern.  Since 7 can never be used in p-scheme, the correct way to
    # pattern match on the number 7 is not "7=n", for example, but "seven=n".
    # This function converts "seven" into 7.  This function uses __two_ops()
    # as a helper function when there are two operators contained in the
    # pattern.
    def __verify_pattern(self, pattern):
        ops = ["<=", ">=", "<>", "=", "<", ">"]
        op = None

        if bool(pattern.count("<") == 2) ^ bool(pattern.count(">") == 2):
            return self.__two_ops(pattern)

        for i in ops:
            if len(pattern.split(i)) == 2:
                op = i
                break

        if op == None:
            return ("error", "Error: Bad pattern")

        pattern_split = pattern.split(op)
        if pattern_split[0] == "7":
            return ("error", "Error: Argument is 7")
        if pattern_split[0] == "seven":
            pattern_split[0] = "7"
        elif not isNum(pattern_split[0]):
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


    # This function is similar to __verify_pattern, except it is called when
    # the pattern contains two operators.  It uses __verify_pattern() to verify
    # the first half of the pattern and then confirms the rest of the pattern
    # is of a good format itself.
    def __two_ops(self, pattern):
        if pattern.count("<") == 2:
            op = "<"
        else:
            op = ">"

        first_half_pattern = pattern[:pattern.find(op, pattern.find(op)+1)]
        pattern = pattern[pattern.find(op, pattern.find(op)+1)+1:]
        if pattern[0] == "=":
            pattern = pattern[1:]
            op = op + "="
        if pattern == "7":
            return ("error", "Error: Argument is 7")
        if pattern == "seven":
            bound = "7"
        elif not isNum(pattern):
            return ("error", "Error: Bad pattern")
        else:
            bound = pattern


        (error, val) = self.__verify_pattern(first_half_pattern)
        if error == "error":
            return (error, val)

        if "<>" in [op, val[0]]:
            return ("error", "Error: Bad Pattern")


        if "=" in val[0] and "=" in op:
            if "<" in op:
                if float(val[1]) > float(bound):
                    return ("error", "Error: Bad Pattern")
            else:
                if float(val[1]) < float(bound):
                    return ("error", "Error: Bad Pattern")
            return ("not_error", ([val[0], op], [val[1], bound]))
        else:
            if "<" in op:
                if float(val[1]) >= float(bound):
                    return ("error", "Error: Bad Pattern")
            else:
                if float(val[1]) <= float(bound):
                    return ("error", "Error: Bad Pattern")
            return ("not_error", ([op, val[0]], [bound, val[1]]))

 
    # This funciton updates self.interval and self.patterns.  It will return an
    # error if pattern matching proves to be over-exhaustive.
    def __add_helper(self, lbound, ubound, lbound_ie, ubound_ie, nequal=False):
        lbound = float(lbound)
        ubound = float(ubound)

        if lbound > ubound:
            (lbound, ubound) = (ubound, lbound)
            (lbound_ie, ubound_ie) = (ubound_ie, lbound_ie)

        new_pattern = Intervals(REALS)

        if lbound == ubound:
            if not (self.interval).union_number(lbound):
                return ("error", "Error: A value matches two patterns")
            new_pattern.union_number(lbound)

        elif not (self.interval).union_interval(lbound, ubound, \
                                                          lbound_ie, ubound_ie):
            return ("error", "Error: A value matches two patterns")
        else:
            new_pattern.union_interval(lbound, ubound, lbound_ie, ubound_ie)

        if nequal:
            (self.patterns[-1]).union_interval(lbound, ubound, \
                                                           lbound_ie, ubound_ie)
        else:
            (self.patterns).append(new_pattern)
        return ("not_error", "good pattern")


    # Returns True if pattern matching is complete and returns False otherwise.
    def isComplete(self):
        return (self.interval).isComplete()


    # Returns True if arg is contained in the i-th pattern and False otherwise.
    # arg will always be a number.
    def matches(self, arg, i):
        return (self.patterns[i]).inInterval(float(arg))



