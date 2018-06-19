#
# Matthew Epstein
# pm_strings.py
# This file handles pattern matching for strings.  The PM_Strings class is
# similar to the PM_Nums, PM_Bools, and PM_Lists classes, which are located in
# pm_nums.py, pm_bools.py, and pm_lists.py, respectively.  All four classes
# hold the same three public functions: addPattern(), isComplete(), and
# matches().  Both this class and the PM_Nums class rely heavily on the
# Intervals class, found in intervals.py.  This class works by converting every
# string into an integer and then essentially doing pattern matching on
# integers.  Strings must be 50 characters or less.
#


import global_vars
import re
from intervals import *
from type_checking import *


# Pattern matching cannot be performed on strings longer than 50 characters.
# MAX_STR is the 50-character string with the largest numerical representation
# while MAX_NUM is that number.
MAX_STR = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
MAX_NUM = 769449752767133292742943790958350921451790972423891374406296339660826788531267084181308746337890624


class PM_Strings:

    # Initializes the PM_Strings class.  self.interval is an instance of the
    # integers version of the Intervals class.  It keeps track of which numbers
    # (strings) have been used in a pattern and which have not.  Once
    # self.interval is equal to the (-inf, inf) interval, pattern matching is
    # considered complete.  The 0-minimum/50-maximum string length means that
    # there are many integers that cannot correspond to any string (the shortest
    # possible string is the empty string with a corresponding value of -1).
    # Upon initialization of the class, we therefore add two "dummy" patterns:
    # all values less than the smallest string and all values greater than the
    # largest string.  This allows us to use the isComplete() method in the
    # Intervals class.  These two dummy patterns will always be the last two
    # patterns in self.patterns.  Otherwise, the indexing argument in the
    # matches() function would be off, since clients to this class should not
    # need to think about adjusting for the extra two patterns.  Whereas
    # self.interval can be thought of as the union of all the different
    # patterns, self.patterns, is a list of each individual patterns.  The
    # length of self.patterns will be equal to the number of different patterns
    # a function contains plus two (for the dummy patterns).  This is necessary
    # for determining which pattern a function matches once it is called.
    # self.arg_name is set to None twice because calling addPattern() will set
    # self.arg_name to "n".  If it were not reset to None, the user could only
    # do pattern matching on strings if the name of their parameter is n.
    def __init__(self):
        self.interval = Intervals(INTS)
        self.patterns = []
        self.arg_name = None

        self.addPattern("\"\">n", True) #"" is -1
        self.addPattern("\""+MAX_STR+"\"<n", True)
        self.arg_name = None


    # This function takes in a pattern as a string which will be of the form
    # [string_literal][operator][variable_name][operator*][string_literal*].
    # The final two parts (denoted with an asterisk) are optional, but both must
    # be present if one is included.  ""hello"=n" and ""hi"<n<="bye"" are both
    # valid patterns, for example.  The one exception to the required pattern
    # format is if the pattern is a wild card, in which case the entire pattern
    # will simply be an underscore.  The init flag is necessary because adding
    # the dummy patterns is slightly different.  init will only be set to True
    # when those two patterns are being added.  This function uses 
    # __verify_pattern() and __add_helper(), to verify the pattern is in a
    # proper format, and update self.interval and self.patterns, respectively.
    def addPattern(self, pattern, init=False):
        if pattern == "_":
            if not (self.interval).isComplete():
                all_ints = Intervals(INTS)
                all_ints.union_interval(ninf, inf)
                self.interval = all_ints
                # this ensures the -1>n and MAX_STR<n patterns will always be
                # the final two patterns
                self.patterns = self.patterns[:-2] + [all_ints] + \
                                                            self.patterns[-2:]
                return ("not_error", "good pattern")
            else:
                return ("error", "Error: Pattern matching is already exhaustive")
        
        (error, val) = self.__verify_pattern(pattern)
        if error == "error":
            return (error, val)
        (ops, patterns) = val


        if init:
            if ops[0] == ">":
                ops.append(">")
                patterns.append(ninf)
            else: #ops[0] == "<"
                ops.append("<")
                patterns.append(inf)
        else:
            if len(ops) == 1 and (ops[0] == ">" or ops[0] == ">="):
                ops.append(">=")
                patterns.append(-1)
            elif len(ops) == 1 and (ops[0] == "<" or ops[0] == "<="):
                ops.append("<=")
                patterns.append(MAX_NUM)

        if len(ops) == 1:
            if ops[0] == "=":
                return self.__add_helper(patterns[0], patterns[0], init)
            elif ops[0] == "<>":
                first = self.__add_helper(-1, patterns[0]-1, init)
                if first[0] == "error":
                    return first
                return self.__add_helper(patterns[0]+1, MAX_NUM, init, True)
        else:
            offset_first_num = lambda op,val: val-1 if op==">" else val+1
            offset_second_num = lambda op,val: val+1 if op==">" else val-1
            if "=" not in ops[0]:
                patterns[0] = offset_first_num(ops[0], patterns[0])
            if "=" not in ops[1]:
                patterns[1] = offset_second_num(ops[1], patterns[1])

            return self.__add_helper(min(patterns), max(patterns), init)

        return ("not_error", "good pattern")


    # This function checks that the pattern is of a valid format.  If it is not,
    # this function will return the proper error.  Otherwise, it will return
    # the operator and the string literal that are expressed within the
    # pattern.  This function uses the __op_parsing() function to appropriately
    # split up the pattern and the __encode() and __convert() functions to turn
    # strings into their corresponding integral values.
    def __verify_pattern(self, pattern):
        if pattern[0] != "\"":
            return ("error", "Error: Bad pattern")
        pattern = pattern[1:]

        for i in range(len(pattern)):
            if pattern[i] != "\"":
                continue
            word1 = pattern[:i]
            pattern = pattern[i+1:]
            break

        (error, base95) = self.__encode(word1)
        if error == "error":
            return (error, base95)
        val1 = self.__convert(base95)

        (error, val) = self.__op_parsing(pattern)
        if error == "error":
            return (error, val)
        (op1, pattern) = val

        ops = ["=", "<", ">"]
        for i in range(len(pattern)):
            if pattern[i] not in ops:
                if i == len(pattern)-1:
                    var = pattern
                    pattern = ""
                continue
            var = pattern[:i]
            pattern = pattern[i:]
            break

        if self.arg_name == None:
            self.arg_name = var
        elif self.arg_name != var:
            return ("error", "Error: Argument names do not match")

        if isLiteral(var) or var in global_vars.VARIABLE_RESERVED_TERMS:
            return ("error", "Error: Name is reserved")

        if re.sub('\W+', "", var) != var:
            return ("error", "Error: Name contains reserved symbol")

        if pattern == "":
            return ("not_error", ([op1], [val1]))

        (error, val) = self.__op_parsing(pattern)
        if error == "error":
            return (error, val)
        (op2, pattern) = val
        if not isString(pattern):
            return ("error", "Error: Bad pattern")

        if "<>" in [op1, op2]:
            return ("error", "Error: Bad pattern")

        word2 = pattern[1:-1]
        (error, base95) = self.__encode(word2)
        if error == "error":
            return (error, base95)
        val2 = self.__convert(base95)
        return ("not_error", ([op1, op2], [val1, val2]))


    # This funciton updates self.interval and self.patterns.  It will return an
    # error if pattern matching proves to be over-exhaustive.
    def __add_helper(self, lbound, ubound, init, nequal=False):
        if lbound > ubound:
            (lbound, ubound) = (ubound, lbound)

        new_pattern = Intervals(INTS)

        if lbound == ubound:
            if not (self.interval).union_number(lbound):
                return ("error", "Error: A value matches two patterns")
            new_pattern.union_number(lbound)

        elif not (self.interval).union_interval(lbound, ubound):
            return ("error", "Error: A value matches two patterns")
        else:
            new_pattern.union_interval(lbound, ubound)

        if init:
            (self.patterns).append(new_pattern)
        elif nequal:
            (self.patterns[-3]).union_interval(lbound, ubound)
        else:
            # see comment on lines 79-80
            self.patterns = self.patterns[:-2] + [new_pattern] + \
                                                            self.patterns[-2:]
        return ("not_error", "good pattern")


    # This function splits a pattern at the operator and checks to make sure the
    # operator is in a valid format.  If it is, the function returns what was on
    # either side of the operator.  Otherwise, it returns an error.
    def __op_parsing(self, pattern):
        ops = ["<", ">", "="]
        if pattern[0] not in ops:
            return ("error", "Error: Bad pattern")
        if (pattern[0] == "<" and (pattern[1] == "=" or pattern[1] == ">")) or \
                                    (pattern[0] == ">" and pattern[1] == "="):
            return ("not_error", (pattern[:2], pattern[2:]))
        else:
            return ("not_error", (pattern[:1], pattern[1:]))

    
    # There are 95 ASCII values that can be printed on a screen.  On a typical
    # ASCII chart, these would be values 32 (a space) through 126 (the ~
    # character).  To convert a string to an integral, value, we first rewrite
    # the word in base 95, where a space is 0, a ! is 1, and so on and so forth
    # until we reach ~, which is 94.  This function takes in a word and converts
    # it to base 95.  For example, if the input is "Hello!", the corresponding
    # ASCII values are 72, 101, 108, 108, 111, 33.  Written in base 95 (and we
    # use the word "written" here loosely), this word would be
    # [40, 69, 76, 76, 79, 1], which is the list that this function returns.
    # The value for the empty string in base 95 is -1.
    def __encode(self, word):
        if word == "":
            return ("not_error", [-1])
        try:
            encoded = map(lambda x: ord(x)-32, list(word))
            error = "not_error"
        except:
            error = "error"
            encoded = "Error: Non-ASCII value detected"

        return (error, encoded)


    # This function takes in a list of numbers that represent a word written in
    # base 95 and converts the number from base 95 to base 10.  In the example
    # above where the word is "Hello!", the base 10 equivalent for
    # [40, 69, 76, 76, 79, 1] would be 315198322031.
    def __convert(self, base95):
        power = 0
        base10 = 0
        while len(base95) != 0:
            base10 += base95[-1] * (95 ** power)
            power += 1
            base95 = base95[:-1]

        return base10


    # Returns True if pattern matching is complete and returns False otherwise.
    def isComplete(self):
        return (self.interval).isComplete()

    # Returns True if arg is contained in the i-th pattern and False otherwise.
    # Also will return False if the argument is longer that 50 characters.  arg
    # will always be a string.
    def matches(self, arg, i):
        if len(arg[1:-1]) > 50:
            return False
        arg = self.__convert(self.__encode(arg[1:-1])[1])
        return (self.patterns[i]).inInterval(arg)


