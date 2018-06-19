#
# Matthew Epstein
# pm_lists.py
# This file handles pattern matching for lists.  The PM_Lists class is similar
# to the PM_Nums, PM_Bools, and PM_Strings classes, which are located in
# pm_nums.py, pm_strings.py, and pm_lists.py, respectively.  All four classes
# hold the same three public functions: addPattern(), isComplete(), and
# matches().
#


import global_vars
import re
from type_checking import *
from list_string_handling import *

class PM_Lists:

    # Initializes the PM_Lists class.  Unlike the other three pattern matching
    # classes, PM_Lists does not contain a self.interval variable.  In the other
    # classes, self.interval essentially keeps track of what portion of the
    # total number of possible patterns have already been used.  For lists,
    # however, there is no efficient way to do this.  Therefore, we simply keep
    # track of the patterns that have been used.  For numbers and strings, we
    # can use the isComplete() function in the Intervals class to determine if
    # pattern matching is exhaustive.  Booleans are simple enough that testing
    # for completeness is not an issue.  For lists, we know a pattern matching
    # is exhaustive when either:
    #   a) the wild card pattern is used
    #   b) a function has only two patterns where one pattern is of the format
    #      [some_list]=n and the other is of the format [some_list]<>n
    # When one of these conditions is met, the self.complete flag will be set to
    # True. self.patterns, is a list of all the individual patterns.  The length
    # of self.patterns will be equal to the number of different patterns a
    # function contains.  This is necessary for determining which pattern a
    # function matches once it is called.
    def __init__(self):
        #self.wild_card = False
        self.patterns = []
        self.arg_name = None
        self.complete = False


    # This function takes in a pattern as a string which will be of the form
    # [list_literal][operator][variable_name].  "[1, [], "abc"]=n" would be a
    # valid pattern, for example.  In addition, individual elements of a list
    # can be set to the wild card character, so a pattern like "[1, _, "abc"]=n"
    # would also be considered acceptable.  This pattern would match with all
    # lists whose first and third elements are 1 and "abc", respectively.  The
    # one exception to the required pattern format is if the pattern is a wild
    # card, in which case the entire pattern will simply be an underscore.
    # Using __verify_pattern() and __add_helper(), this function verifies the
    # pattern is in a proper format, and updates self.patterns.
    def addPattern(self, pattern):
        if pattern == "_":
            if not self.isComplete():
                # self.wild_card = True
                self.complete = True
                (self.patterns).append(("_", "="))
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
    # the operator and the list literal that are expressed within the
    # pattern.  If there any sevens within the list, this function will also
    # convert those sevens to 7s.
    def __verify_pattern(self, pattern):
        (op, var) = (None, None)

        for i in range(len(pattern)-1,-1,-1):
            if pattern[i] == "=":
                op = "="
                var = pattern[i+1:]
                pattern = pattern[:i]
                break
            elif pattern[i] == ">":
                if i != 0 and pattern[i-1] == "<":
                    op = "<>"
                    var = pattern[i+1:]
                    pattern = pattern[:i-1]
                    break

        if op == None or var == None:
            return ("error", "Error: Bad pattern")

        if not isList(pattern):
            return ("error", "Error: Bad pattern")

        seven_test = handle_seven(pattern)
        if seven_test == True:
            return ("error", "Error: Argument is 7")
        else:
            pattern = seven_test


        list_format = string_check(pattern)
        if list_format != None:
            return list_format

        if self.arg_name == None:
            self.arg_name = var
        elif self.arg_name != var:
            return ("error", "Error: Argument names do not match")

        if isLiteral(var) or var in global_vars.VARIABLE_RESERVED_TERMS:
            return ("error", "Error: Name is reserved")

        if re.sub('\W+', "", var) != var:
            return ("error", "Error: Name contains reserved symbol")

        return ("not_error", (op, string_to_list(pattern)))


    # This funciton updates self.patterns.  It will return an error if pattern
    # matching proves to be over-exhaustive.  For lists, over-exhaustion is a
    # bit tricky.  If there are two patterns one which is [1, _, 3] and the
    # other which is [_, 2, _], that will be considered as over-exhaustive since
    # [1, 2, 3] will match both patterns.
    def __add_helper(self, pattern, op):
        if op == "<>":
            if len(self.patterns) > 1:
                return ("error", "Error: A value matches two patterns")
            elif len(self.patterns) == 1:
                if self.patterns[0][0] == pattern and \
                                                    self.patterns[0][1] == "=":
                    (self.patterns).append((pattern, op))
                    self.complete = True
                else:
                    return ("error", "Error: A value matches two patterns")
            else:
                self.patterns = [(pattern, op)]
            return ("not_error", "good pattern")

        if len(self.patterns) == 1 and self.patterns[0][1] == "<>":
            if self.patterns[0][0] == pattern:
                (self.patterns).append((pattern, op))
                self.complete = True
                return ("not_error", "good pattern")
            else:
                return ("error", "Error: A value matches two patterns")

        for i in range(len(self.patterns)):
            same = False
            if len(self.patterns[i][0]) == len(pattern):
                for j in range(len(pattern)):
                    if self.patterns[i][0][j] == "_" or pattern[j] == "_":
                        continue
                    elif self.patterns[i][0][j] == pattern[j]:
                        continue
                    else:
                        same = False
                        break
            if same:
                return ("error", "Error: A value matches two patterns")

        (self.patterns).append((pattern, op))
        return ("not_error", "good pattern")


    # Returns True if pattern matching is complete and returns False otherwise.
    def isComplete(self):
        return self.complete


    # Returns True if arg is contained in the i-th pattern and False otherwise.
    # arg will always be a list.  This function uses __matches_helper().
    def matches(self, arg, i):
        arg = string_to_list(arg)

        if self.patterns[i][0] == "_":
            return True
        elif self.patterns[i][1] == "<>":
            return self.__matches_helper(arg, i, True)
        else:
            return self.__matches_helper(arg, i, False)


    # This function compares the list in the i-th pattern to the list given as
    # an argument and tests to see if the two patterns match.
    def __matches_helper(self, arg, i, truth_value):
        if len(self.patterns[i][0]) != len(arg):
            return truth_value
        for j in range(len(arg)):
            if self.patterns[i][0][j] == "_" or arg[j] == "_":
                continue
            elif self.patterns[i][0][j] != arg[j]:
                return truth_value
        return not truth_value

