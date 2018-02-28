#
# Matthew Epstein
# type_checking.py
# As the filename implies, this file is responsible for most of the
# type-handling in p-scheme.  The general_type() function is called by
# definePrimitive().  It solves each variable's types, returns an updated
# constraint list, and decides if a type-error should be raised.  This file
# also includes a number of smaller functions (isNum(), isLiteral(), etc.) that
# are employed by a wide range of functions throughout the program.
#


import operator
import global_vars
from env import *
from random import *

# The eight functions below are all fairly self-explanatory.
def isNum(x):
    try:
        isinstance(float(x), float)
        return True
    except:
        return False

def isBool(x):
    return (x == "true" or x == "false" or x == "maybe")


def isString(x):
    # calling isString() on a number would otherwise return an error since
    # numbers don't have the [] property
    if isNum(x):
        return False
    
    x = x.replace("<'>", "\"")

    if x == "":
        return True

    return (x[0] == "\"" and x[-1] == "\"")   #if x is of the "___" format

def isList(x):
    if x == "" or isNum(x): #"object has no attribute __getitem__" error
        return False

    return (x[0] == "[" and x[-1] == "]")   #if x is of the [___] format

def isNothing(x):
    return (x == "Nothing")


def isLiteral(x):
    return (isNum(x) or isBool(x) or isString(x) or isList(x) or isNothing(x))

# must update as more types are added
def isValidType(x):
    return (x in global_vars.ALL_TYPES)

def getLiteralType(x):
    if isNum(x):
        return "num"
    if isBool(x):
        return "bool"
    if isString(x):
        return "str"
    if isList(x):
        return "list"
    if isNothing(x):
        return "nonetype"
    return ("error", "Error: Bad type")  


# Desired_type is a list of types that are valid.  This function is used to
# detect type-errors in the general_type() function
def isUndesirableType(x, desired_types):
    f = lambda y: False if (x!=y or y in desired_types) else True
    return reduce((lambda acc, a: operator.or_ (acc, f(a))), \
                                                global_vars.ALL_TYPES, False)


# Ensures that a literal matches its constraint
def check_expected_literal_type(arg, constraint):
    if isNum(arg) and constraint == "num":
        return arg
    if isBool(arg) and constraint == "bool":
        return arg
    if isString(arg) and constraint == "str":
        return arg
    if isList(arg) and constraint == "list":
        return arg
    if isNothing(arg) and constraint == "nonetype":
        return arg
    return ("error", "Error: Bad type")


# This comment strips the dot from an argument (eg. x.int) and uses the
# information from the dot (if it was present) as well as the constraint to
# solve the argument's type.
def general_type(arg, constraints, varEnv, locEnv):
    if not isLiteral(arg):
        arg_split = arg.split(".")
    else:
        arg_split = [arg]

    if len(arg_split[0]) > 2:
        if arg_split[0][:2] == "//" and \
           (locEnv.inEnv(arg_split[0][2:]) or varEnv.inEnv(arg_split[0][2:])):
            arg = arg_split[0][2:]
            arg_split[0] = arg_split[0][2:]

    if arg_split[0] != arg: #if var contains a dot
        env_fun = lambda acc, x: acc or x.inEnvandType(arg_split[0], arg_split[1])
        if reduce(env_fun, [locEnv, varEnv], False) and \
                                                 arg_split[1] in constraints[0]:
            arg = arg_split[0]
            constraints = [arg_split[1]]
        elif isLiteral(arg_split[0]):
            return (("error", "Error: Argument does not support dot operation"), \
                                                                    constraints)
        elif arg_split[1] not in global_vars.ALL_TYPES:
            return (("error", "Error: Argument type does not exist"), constraints)
        elif arg_split[1] not in constraints[0]:
            return (("error", "Error: Bad type"), constraints)
        elif not varEnv.inEnv(arg_split[0]) and not varEnv.inEnv(arg_split[0]):
            return (("error", "Error: Argument does not exist"), constraints)
        elif isUndesirableType(arg_split[1], locEnv.getVarTypes(arg_split[0])) and \
           isUndesirableType(arg_split[1], varEnv.getVarTypes(arg_split[0])):
            return (("error", "Error: Bad type"), constraints)
    else: #if var is a literal
        env_fun = lambda acc, x: acc or x.inEnv(arg_split[0])
        if reduce(env_fun, [locEnv, varEnv], False):
            for env in [locEnv, varEnv]:
                typesOfArg = env.getVarTypes(arg)
                intersection = [x for x in typesOfArg if x in constraints[0]]
                if intersection == []:
                    if env == varEnv:
                        return (("error", "Error: Bad type"), constraints)
                else:
                    constraints = intersection
                    break
        elif isLiteral(arg):
            for i in range(len(constraints[0])):
                errorTest = check_expected_literal_type(arg, constraints[0][i])
                if errorTest == "" or errorTest[0] != "error":
                    arg = errorTest
                    constraints = [getLiteralType(arg)]
                    break
                elif i == len(constraints[0])-1:
                    return (errorTest, constraints)
        else:
            return (("error", "Error: Argument does not exist"), constraints)
    return (arg, constraints)


# If input is two variables with identical and multiple types, constraints will
# not be a singleton list so we need to find the constraint we want.  By the
# time this function is called, we should know that the intersection between the
# argument's types and the constraints is not empty
def constraintCheck(arg, constraints, varEnv, locEnv):
    if len(constraints[0]) == 1:
        return constraints[0]

    for env in [locEnv, varEnv]:
        typesOfArg = env.getVarTypes(arg)
        intersection = [x for x in typesOfArg if x in constraints[0]]
        if intersection == []:
            continue
        constraints = [intersection[0]]
        break
    return constraints

# All arguments are originally entered as a string.  This function "casts" the
# argument to its actual value.
def casted(arg):
    if isNum(arg):
        try:
            if float(arg) == int(float(arg)):
                return int(float(arg))
        except:
            return ("error", "Error: To infinity and beyond")
        return float(arg)
    if isBool(arg):
        return getBoolVal(arg)
    if isString(arg):
        return str(arg)
    if isList(arg):
        return arg
    if isNothing(arg):
        return str(arg)


# Translates p-scheme booleans into python booleans
def getBoolVal(arg):
    if arg == "maybe":
        if randint(0,1) == 0:
            return True
        else:
            return False
    elif arg == "true":
        return True
    return False


# By the time this function is called, all potential errors should have been
# handled so arg will either be a literal or a variable of type constraint
def getValofType(arg, constraint, varEnv, locEnv):
    for env in [locEnv, varEnv]:
        if env.inEnvandType(arg, constraint[0]):
            return casted(env.getVal(arg, constraint[0]))
        else:
            continue

    return casted(arg) #if arg is not a variable, it must be a literal
