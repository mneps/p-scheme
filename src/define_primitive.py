#
# Matthew Epstein
# define_primitive.py
# This file holds the definePrimitive() function, which checks that the user
# has passed a function the correct number of arguments, that the arguments are
# of the correct type, and--if these two specifications were satisfied--gets the
# values that those arguments represent (eg. if x=3 and the argument passed to
# the function is x, then x will be the argument and 3 the associated value).
# The function gets its own file because it is used by both primitives.py and
# node.py.  It can't go in primitives.py because then node.py wouldn't have
# access to it, but it doesn't make much sense for the function to go in
# node.py either.
#

from list_string_handling import *
from type_checking import *


# See the comment at the top of the file for this function's purpose.
def definePrimitive(args, constraints, varEnv, locEnv):
    #print args
    if len(args) != len(constraints):
        return ("error", "Error: Incorrect number of arguments")

    cleanArgs = [] # strips dot from argument name
    for i in range(len(args)):
        if isList(args[i]) and string_check(args[i]) != None:
            return string_check(args[i])
        (toAppend, constraints[i][0]) = \
                        general_type(args[i], constraints[i], varEnv, locEnv)
        if toAppend != "" and toAppend[0] == "error":
            return toAppend
        cleanArgs.append(toAppend)

    constraints[0][0] = \
                constraintCheck(cleanArgs[0], constraints[0], varEnv, locEnv)
    val_list = [] # values with correct type
    for i in range(len(cleanArgs)):
        val_list.append(getValofType(cleanArgs[i], constraints[i][0], varEnv, \
                                                                        locEnv))
        if isinstance(val_list[i], tuple) and val_list[i][0] == "error":
            return val_list[i]

    for i in val_list:
        if isList(i) and list_check(i, varEnv, locEnv) != None:
            return list_check(i, varEnv, locEnv)

    for i in range(len(val_list)):
        try:
            if val_list[i][:2] == "//" and varEnv.inEnv(val_list[i][2:]):
                val_list[i] = val_list[i][2:]
            elif val_list[i][:2] == "//" and not funEnv.inEnv(val_list[i][2:]):
                return ("error", "Function does not exist")
        except:
            pass

    return val_list