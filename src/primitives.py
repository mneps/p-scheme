# 
# Matthew Epstein
# primitives.py
# This file contains the defintions for all of p-schene's primitives functions.
# Whenever a user calls a primitive function, that function is evaluated by
# calling the appropriate function in this file.  This module heavily relies
# upon the definePrimitive() function in define_primitive.py.  (The function is
# not in this file because node.py uses it as well, but since this file
# "includes" node.py, node.py would not have access to the function if it were
# here.)
#
# It is also worth explaining how the type system works.  Each function has a
# type, which states the what types the arguments for that function must be as
# well as what type the function will produce.  Some arguments will be "linked"
# meaning that the arguments must be of the same type.  Takes the function that
# tests for equality, for example, which has type 'a * 'a -> bool.  It is
# unimportant whether or not the arguments are numbers, booleans, or some other
# type, but it is important that they are of the same type.  You cannot check
# for equality between, say, a string and a list (at least in p-scheme).
# Each function has a constraint list defined for itself, which contains the
# types that are valid for that function.  These contraint lists are of the
# form: [[[first_argument's_types]], [[second_argument's_types]], [[etc.]]]. At
# first glance, such list-nesting may seem wholly unnecessary, but it does serve
# an important purpose.  By creating the constraints list like this and then
# setting two arguments' respective constraints equal to each other, we can
# simulate the type-linking of arguments!  Say there is a function of type
# 'a *'a -> 'a, where 'a can be either a number or a string.  Setting up the
# constraint list would look like this:
#   arg_one_constraints = [["num", "str"]]
#   arg_two_constraints = arg_one_constraints
#   constraints = [arg_one_constraints, arg_two_constraints]
# Now, say that in solving the first argument, we realize that the first
# argument must be a number.  When we update arg_one_constraints to reflect
# this, arg_two_constraints will also be automatically updated, ensuring that
# the two arguments will always have the identical constraints.  This type of
# linking would not be possible without nesting the lists like so.  With one
# fewer layer of brackets, updating arg_one_constraints would update only
# arg_one_constraints, even if arg_one_constraints and arg_two_constraints
# had previsouly been set equal to each other.
#


import itertools
import math
import global_vars
from define_primitive import *
from expTree import *
from node import *
from env import *
from type_checking import *
from random import *
from list_string_handling import *
from makeTree import *


# Checks to make sure the result of a conditional or a loop (both of which 
# evaluate subtrees) can be translated into a value.
def verifyResult(val, varEnv, locEnv):
    if val[0] != "not_error":
        return val
    constraints = [[global_vars.ALL_TYPES]]
    val_list = definePrimitive([val[1]], constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list
    val_list = map(lambda x: x if not isinstance(x, bool) else "true" \
                                            if x else "false", val_list)
    return ("not_error", val_list[0])


# This function takes in an argument and verifies that the argument is a
# function.  Used by higher-order list functions, which take a function as an
# argument
def valid_function_check(arg, varEnv, locEnv, funEnv):
    if isLiteral(arg):
        return ("error", "Error: Bad type")
    if not funEnv.inEnv(arg):
        if not varEnv.inEnv(arg) and not locEnv.inEnv(arg):
            return ("error", "Error: Argument does not exist")
        else:
            return ("error", "Error: Bad type")
    return ("not_error", arg)

# Function called when both arguments must be numbers.
def numArrityTwo(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[["num"]], [["num"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list
    try:
        result = op(val_list[0], val_list[1])
        if op == operator.div:
            result = op(float(val_list[0]), float(val_list[1]))
        if not isinstance(result, list): #range returns a list
            if int(result) == result:
                result = int(result)
        return ("not_error", result)
    except:
        if op == randint:
            if val_list[0] > val_list[1]:
                return ("error", "Error: Argument out of range")
            else:
                return ("error", "Error: Arguments must be integers")    
        elif op == operator.div or op == operator.mod:
            return ("error", "Error: Cannot divide or modulo by 0")
        else:
            return ("error", "Error: Argument must be an integer")

# String concatenation
def concat(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[["str"]], [["str"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list
    for i in range(len(val_list)):
        if isString(val_list[i]):
            val_list[i] = val_list[i][1:-1]
    return ("not_error", "\""+op(val_list[0], val_list[1])+"\"")


# Function called when both arguments must be numbers.
def numArrityOne(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[["num"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    # ! will raise an error if arg is non-integral or negative
    # v/ will raise an error if arg is negative
    # range will return an error if a non-int is passed in
    # int will never raise an error
    try:
        if op == math.sqrt:
            result = op(val_list[0])
            if int(result) == result:
                result = int(result)
            return ("not_error", result)
        return ("not_error", op(val_list[0]))
    except:
        return ("error", "Error: Argument out of range")


# eg. and, or, xor, etc.
def booleans(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[["bool"]], [["bool"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list
    return ("not_error", "true" if op(val_list[0], val_list[1]) else "false")

# The not function
def boolNot(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[["bool"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list
    return ("not_error", "true" if op(val_list[0]) else "false")

# eg. <. <=, =>, >
# Both numbers and strings (think alphabetical sorting) can be compared to each
# other
def comparison(args, varEnv, locEnv, funEnv, op, id_num):
    constB = [["num", "str"]]
    constA = constB
    constraints = [constA, constB] #link the arguments
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list
    return ("not_error", "true" if op(val_list[0], val_list[1]) else "false")


# = and <>
def equal_nequal(args, varEnv, locEnv, funEnv, op, id_num):
    constB = [global_vars.ALL_TYPES]
    constA = constB
    constraints = [constA, constB]

    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    return ("not_error", "true" if op(val_list[0], val_list[1]) else "false")


# Printing (prints with a new line character at the end) and writing (no new
# line character)
def printVar(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[global_vars.ALL_TYPES]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if isinstance(val_list[0], bool):
        if val_list[0]:
            val_list[0] = "true"
        else:
            val_list[0] = "false"

    if isString(val_list[0]):
        val_list[0] = val_list[0][1:-1].replace("<'>", "\"")
        op(val_list[0])
    else:
        op(val_list[0])
    return ("not_error", "Nothing")

# The user is prompted to enter input.  The input can either be a number or a
# string but there is obviously no reason the user should know about the
# representations of booleans, lists, or nonetype objects.
def userInput(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[global_vars.ALL_TYPES]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if isinstance(val_list[0], bool):
        if val_list[0]:
            val_list[0] = "true"
        else:
            val_list[0] = "false"

    if isString(val_list[0]):
        val_list[0] = val_list[0][1:-1]
    input_val = op(val_list[0])
    if not isNum(input_val):
        input_val = "\"" + input_val + "\""
    return ("not_error", input_val)


# Functions that take in no arguments.
def arrityZero(args, varEnv, locEnv, funEnv, op, id_num):
    if args != []:
        return ("error", "Error: Incorrect number of arguments")
    return ("not_error", op())


# Similar to the userInput() function, except the user may only enter a single
# character. 
def getChar(args, varEnv, locEnv, funEnv, op, id_num):
    if args != []:
        return ("error", "Error: Incorrect number of arguments")
    val = op()
    if isNum(val):
        return ("not_error", int(val))
    else:
        return ("not_error", "\""+val+"\"")


# Simply prints an encouraging message to the user.
def happy(args, varEnv, locEnv, funEnv, op, id_num):
    if args != []:
        return ("error", "Error: Incorrect number of arguments")
    compliments = ["You're doing great!", "You can do it!", "Don't stop now!", \
                   "This is really great code!", "You're a smart cookie!", \
                   "Keep up the good work!", "You're perfect!", \
                   "On a scale of 1 to 10, you're an 11.", \
                   "Your hair looks stunning today!", "You're inspiring!", \
                   "You would surve a zombie apocalypse.", \
                   "There's ordinary, and then there's you.", \
                   "You're really something special!", \
                   "You're a gift to those around you.", \
                   "You're someone's reason to smile :)", \
                   "Is that your picture next to \"charming\" in the dictionary?", \
                   "Your inside is even more beautiful than your outside.", \
                   "Being around you makes everything better!", \
                   "Jokes are funnier when you tell them!", \
                   "Our community is better because you're in it!",
                   "I bet you do crossword puzzles in ink.", \
                   "You're a winner winner chicken dinner!",
                   "You just light up the room!", "You have the best laugh!", \
                   "You bring out the best in people!", \
                   "We are all better people for having known you.",
                   "The world needs more people like you in it!", \
                   "You deserve love and happiness.", "You have the best ideas!", \
                   "You have a gift for making people comfortable."]
    print compliments[randint(0,29)]
    return ("not_error", "Nothing")


# Functions that take in a single list (eg. length() and null?)
def listArrityOne(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[["list"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    val_list[0] = string_to_list(val_list[0])
    return ("not_error", op(val_list[0]))

# Appending or pushing an argument to a list
def append_push(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[global_vars.ALL_TYPES], [["list"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    val_list[1] = string_to_list(val_list[1])
    if isBool(args[0]):
        val_list[0] = args[0]

    op(val_list[0], val_list[1])
    val_list[1] = list_to_string(val_list[1])
    val_list[1] = handle_maybe(val_list[1])
    return ("not_error", val_list[1])

# Get an element of a list, from its position in the list
def listGet(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[["num"]], [["list"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    val_list[1] = string_to_list(val_list[1])

    try:
        toReturn = str(op(val_list[0], val_list[1]))
        if toReturn == "maybe":
            if randint(0,1) == 0:
                toReturn = "true"
            else:
                toReturn = "false"
    except:
        return ("error", "Error: Position does not exist in list")

    return ("not_error", toReturn)


# Puts an element in a list at the specified position
def listPut(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[global_vars.ALL_TYPES], [["num"]], [["list"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list
    val_list[2] = string_to_list(val_list[2])

    if isBool(args[0]):
        val_list[0] = args[0]

    if abs(val_list[1]-time.localtime().tm_yday+1) > len(val_list[2])-1 and \
        (val_list[1]-time.localtime().tm_yday+1) * (-1) != len(val_list[2]):
        return ("error", "Error: Position does not exist in list")
    val_list[2] = op(val_list[0], val_list[1], val_list[2])

    val_list[2] = list_to_string(val_list[2])
    val_list[2] = handle_maybe(val_list[2])
    return ("not_error", val_list[2])


# Inserts a value into a list at the specified position
def listInsert(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[global_vars.ALL_TYPES], [["num"]], [["list"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list
    val_list[2] = string_to_list(val_list[2])


    if isBool(args[0]):
        val_list[0] = args[0]

    if abs(val_list[1]-time.localtime().tm_yday+1) > len(val_list[2]):
        val_list[1]-time.localtime().tm_yday+1
        return ("error", "Error: No element there")
    op(val_list[0], val_list[1], val_list[2])

    val_list[2] = list_to_string(val_list[2])
    val_list[2] = handle_maybe(val_list[2])
    return ("not_error", val_list[2])

# Removes an element from the specified position of the list
def listRemove(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[["num"]], [["list"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if val_list[1] == "[]":
        return ("errorDec", "DeclarationOfIndependence")
    val_list[1] = string_to_list(val_list[1])

    if abs(val_list[0]-time.localtime().tm_yday+1) > len(val_list[1])-1 and \
        (val_list[0]-time.localtime().tm_yday+1) * (-1) != len(val_list[1]):
        return ("error", "Error: No element to remove")

    if len(val_list[1]) == 1:
        val_list[1] = []
    else:
        val_list[1] = op(val_list[0], val_list[1])

    val_list[1] = list_to_string(val_list[1])
    val_list[1] = handle_maybe(val_list[1])
    return ("not_error", val_list[1])


# Initializes a new list of the specified length where each element is the
# specified value
def listInit(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[global_vars.ALL_TYPES], [["num"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if isBool(args[0]):
        val_list[0] = args[0]

    if val_list[1] == 0:
        new_list = "[]"
    elif val_list[1] < 0:
        return ("error", "Error: Invalid list size")
    else:
        new_list = op(val_list[0], val_list[1])
        new_list = list_to_string(new_list)
        new_list = handle_maybe(new_list)
    return ("not_error", new_list)


# Executes a mapping function.  Since the first argument is a function it is
# handled separately.
def listMap(args, varEnv, locEnv, funEnv, op, id_num):
    if len(args) != 2:
        return ("error", "Error: Incorrect number of arguments")

    (error, val) = valid_function_check(args[0], varEnv, locEnv[-1], funEnv)
    if error == "error":
        return (error, val)
    args[0] = val

    constraints = [[["list"]]]
    val_list = definePrimitive([args[1]], constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    new_list = "[]"
    (fun, op) = funEnv.getVal(args[0], "function")[:2]
    (append_fun, append_op) = funEnv.getVal("append", "function")[:2]

    val_list[0] = string_to_list(val_list[0])
    for i in val_list[0]:
        if args[0] not in global_vars.PRIMITIVES:
            global_vars.curr_function.append(args[0])
        if isinstance(i, list):
            i = list_to_string(i)
        else:
            i = str(i)

        (error, val) = fun([i], varEnv, locEnv, funEnv, op, id_num)
        if error == "error":
            return (error, val)
        (error, new_list) = append_fun([str(val), new_list], varEnv, locEnv, \
                                                      funEnv, append_op, id_num)
        if error == "error":
            return (error, new_list)

    return ("not_error", new_list)


# Executes a mapping function.  Since the first argument is a function it is
# handled separately.
def listFold(args, varEnv, locEnv, funEnv, op, id_num):
    if len(args) != 3:
        return ("error", "Error: Incorrect number of arguments")

    (error, val) = valid_function_check(args[0], varEnv, locEnv[-1], funEnv)
    if error == "error":
        return (error, val)
    args[0] = val

    constraints = [[global_vars.ALL_TYPES], [["list"]]]
    val_list = definePrimitive(args[1:], constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    (fun, op) = funEnv.getVal(args[0], "function")[:2]

    val_list[1] = string_to_list(val_list[1])
    val = val_list[0]

    for i in val_list[1]:
        if args[0] not in global_vars.PRIMITIVES:
            global_vars.curr_function.append(args[0])
        if isinstance(i, list):
            i = list_to_string(i)
        else:
            i = str(i)
        if isinstance(val_list[0], list):
            val_list[0] = list_to_string(val_list[0])
        if isinstance(val_list[0], bool):
            if val_list[0]:
                val_list[0] = "true"
            else:
                val_list[0] = "false"
        else:
            val_list[0] = str(val_list[0])

        (error, val) = fun([i, val_list[0]], varEnv, locEnv, funEnv, op, id_num)
        if error == "error":
            return (error, val)
        val_list[0] = val
    return ("not_error", val)


# Executes a filtering function.  Since the first argument is a function it is
# handled separately.
def listFilter(args, varEnv, locEnv, funEnv, op, id_num):
    if len(args) != 2:
        return ("error", "Error: Incorrect number of arguments")

    (error, val) = valid_function_check(args[0], varEnv, locEnv[-1], funEnv)
    if error == "error":
        return (error, val)
    args[0] = val

    constraints = [[["list"]]]
    val_list = definePrimitive([args[1]], constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    new_list = "[]"
    (fun, op) = funEnv.getVal(args[0], "function")[:2]
    (append_fun, append_op) = funEnv.getVal("append", "function")[:2]

    val_list[0] = string_to_list(val_list[0])
    for i in val_list[0]:
        if args[0] not in global_vars.PRIMITIVES:
            global_vars.curr_function.append(args[0])
        if isinstance(i, list):
            i = list_to_string(i)
        else:
            i = str(i)

        (error, val) = fun([i], varEnv, locEnv, funEnv, op, id_num)
        if error == "error":
            return (error, val)
        if val == "true":
            (error, new_list) = append_fun([str(i), new_list], varEnv, \
                                              locEnv, funEnv, append_op, id_num)
        elif val != "false":
            return ("error", "Error: Bad type")
        if error == "error":
            return (error, new_list)

    return ("not_error", new_list)


# Uses the listFilter function to defermine if all the elements in the list when
# passed in as an argument to a given function return true.
def listAll(args, varEnv, locEnv, funEnv, op, id_num):
    (error, val) = listFilter(args, varEnv, locEnv, funEnv, op, id_num)
    if error == "error":
        return (error, val)

    constraints = [[["list"]]]
    val_list = definePrimitive([args[1]], constraints, varEnv, locEnv[-1])

    if len(string_to_list(val_list[0])) == len(string_to_list(val)):
        return ("not_error", "true")
    else:
        return ("not_error", "false")

# Uses the listFilter function to defermine if any element in a list when passed
# in as an argument to a given function return true.
def listExists(args, varEnv, locEnv, funEnv, op, id_num):
    (error, val) = listFilter(args, varEnv, locEnv, funEnv, op, id_num)
    if error == "error":
        return (error, val)

    if len(string_to_list(val)) > 0:
        return ("not_error", "true")
    else:
        return ("not_error", "false")


# For the casting functions below, only certain types can be cast to other
# types.  A list can be cast to another type, but only if it is a singleton
# list (eg. [1] num will produce 1 but [1, 2] num will produce an error).
# Cast to a number.  Only numbers, strigs, and lists can be

# Casts to a number.
def castNum(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[["num", "str", "list"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if isList(val_list[0]):
        if len(string_to_list(val_list[0])) == 1:
            arg = string_to_list(val_list[0])[0]
            constraints = [[["num"]]]
            val_list = definePrimitive([str(arg)], constraints, varEnv, \
                                                                    locEnv[-1])
            if val_list[0] == "error":
                return ("error", "Error: Argument cannot be a num")
        else:
            return ("error", "Error: Argument cannot be a num")
    if isString(val_list[0]):
         val_list[0] = val_list[0][1:-1]
    try:
        return ("not_error", op(val_list[0]))
    except:
        return ("error", "Error: Argument cannot be a num")

# Casts to a boolean.
def castBool(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[["bool", "str", "list"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if isList(val_list[0]):
        if len(string_to_list(val_list[0])) == 1:
            arg = string_to_list(val_list[0])[0]
            constraints = [[["bool"]]]
            val_list = definePrimitive([str(arg)], constraints, varEnv, \
                                                                    locEnv[-1])
            if val_list[0] == "error":
                return ("error", "Error: Argument cannot be a bool")
        else:
            return ("error", "Error: Argument cannot be a bool")
    if isString(val_list[0]):
        if isBool(val_list[0][1:-1]):
            return ("not_error", val_list[0][1:-1])
        else:
            return ("error", "Error: Argument cannot be a bool")
    if isinstance(val_list[0], bool):
         return ("not_error", "true" if val_list[0] else "false")


# Casts to a string.
def castStr(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[global_vars.ALL_TYPES]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if isinstance(val_list[0], bool):
        return ("not_error", op("true") if val_list[0] else op("false"))
    if val_list[0] == "Nothing":
        return ("not_error", op("Nothing"))

    if isNum(val_list[0]):
        return ("not_error", op(str(val_list[0])))
    if isList(val_list[0]):
        temp = handle_maybe(val_list[0])
        temp = str(temp)
        temp = temp.replace("\"", "<'>")
        return ("not_error", op(temp))
    return ("not_error", val_list[0])


# Casts to a list.
def castList(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[global_vars.ALL_TYPES]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if isList(val_list[0]):
        return ("not_error", val_list[0])
    if isinstance(val_list[0], bool):
        return ("not_error", "[true]" if val_list[0] else "[false]")
    return ("not_error", op(val_list[0]))


# Casts to a nonetype.
def castNonetype(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[["str", "list", "nonetype"]]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if isList(val_list[0]):
        if len(string_to_list(val_list[0])) == 1:
            arg = string_to_list(val_list[0])[0]
            constraints = [[["nonetype"]]]
            val_list = definePrimitive([str(arg)], constraints, varEnv, \
                                                                    locEnv[-1])
            if val_list[0] == "error":
                return ("error", "Error: Argument cannot be a nonetype")
        else:
            return ("error", "Error: Argument cannot be a nonetype")
    if isNothing(val_list[0]):
        return ("not_error", "Nothing")
    if isString(val_list[0]):
        if isNothing(val_list[0][1:-1]):
            return ("not_error", val_list[0][1:-1])
        else:
            return ("error", "Error: Argument cannot be a nonetype")


# Variable assignment.  This function is one of the more lengthy ones, mainly
# because of the necssary error-checking and because it is specialized
# enought that definePrimitive() can't really be called.
def defineVar(args, varEnv, locEnv, funEnv, op, id_num=None):
    if len(args) != 2:
        return ("error", "Error: Incorrect number of arguments")
    constraints = [[global_vars.ALL_TYPES]]

    for arg in args:
       if isList(arg) and string_check(arg) != None:
            return string_check(arg)

    val_list = []
    (toAppend, constraints[0][0]) = general_type(args[1], constraints[0], \
                                                            varEnv, locEnv[-1])
    if toAppend[0] == "error":
        return toAppend
    val_list.append(toAppend)

    if isLiteral(args[0]) or args[0] in global_vars.VARIABLE_RESERVED_TERMS:
        return ("error", "Error: Name is reserved")
    if "//" in args[0][2:] or args[0][:-2] == "_g":
        return ("error", "Error: Name contains reserved symbol")

    if len(args[0]) > 2: #avoids the necessity of a try-except
        if args[0][:2] == "//" and funEnv.inEnv(args[0][2:]):
            args[0] = args[0][2:]
        elif args[0][:2] == "//" and not funEnv.inEnv(args[0][2:]):
            return ("error", "Argument is not a function")

    if re.sub('\W+', "", args[0]) != args[0]:
        return ("error", "Error: Name contains reserved symbol")

    if isNum(val_list[0]):
        if float(val_list[0]) == int(float(val_list[0])):
             val_list[0] = str(int(float(val_list[0]))) #eg. "3.0"->3.0->3->"3"
        else:
            val_list[0] = str(float(val_list[0]))

    if isList(val_list[0]) and \
                        list_check(val_list[0], varEnv, locEnv[-1]) != None:
        return list_check(val_list[0], varEnv, locEnv[-1])

    if global_vars.user_function > 0 and args[0][-2:] != "_g":
        locEnv[-1].addBind(args[0], val_list[0], constraints[0])
    else:
        if args[0][-2:] == "_g":
            args[0] = args[0][:-2]
        varEnv.addBind(args[0], val_list[0], constraints[0])
    return ("not_error", args[0]) 

# Check-expect
def check_expect (args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[global_vars.ALL_TYPES], [global_vars.ALL_TYPES]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    val_list = map(lambda x: x if not isinstance(x, bool) else "true" \
                                                if x else "false", val_list)

    for i in range(len(val_list)):
        try:
            val_list[i] = val_list[i].replace("<'>", "\"")
        except:
            pass

    if val_list[0] == val_list[1]:
        return ("not_error", "Check was " + str(val_list[0]) + ", as expected")
    else:
        return ("error", "Error: Result was supposed to be " + \
                    str(val_list[1]) + ", but was actually " + str(val_list[0]))

# Check-error
def check_error (args, varEnv, locEnv, funEnv, op, id_num):
    if len(args) != 1:
        global_vars.check_error = False
        return ("error", "Error: Incorrect number of arguments")
    constraints = [[global_vars.ALL_TYPES]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])

    global_vars.check_error = False
    if val_list[0] == "error":
        return ("not_error", "Expression failed, as expected")
    else:
        return ("error", "Error: Expression did not fail")

# Empties a function environment--the local environment if within a function;
# the variable environment if not.
def empty(args, varEnv, locEnv, funEnv, op, id_num):
    if global_vars.user_function > 0:
        locEnv.empty()
    else:
        varEnv.empty()
    return ("not_error", "Nothing")


# The conditional and loop functions below work in a similar manner.  Evaluating
# an expression overwrites the original expression with that expression's
# result.  This presents a problem for conditionals--because it's possible that
# we will not want to evaluate to body of the conditional and normal evaluation
# will automatically evaluate the entirety of an expression--and also for
# loops--both for the reason stated above, but also because a loop that runs
# more than one time will need to be evaluated again, but the portion of the
# tree that needs to be evaluated will have already been overwritten by
# evaluating the first iteration of the loop.  The solution is to pass the
# function the id number of the conditional or loop in the tree, so that the
# function can get the node of the tree in question.  Then, once it has that
# node, the appropriate branches of the subtree can be evaluated.  For a
# conditional, the first expression is evaluated and based on the result, either
# the true or false branch is evaluated with the other ignored.  This means
# that an error in the non-evaluated branch will not be found (this is not
# necessarily a bad thing).  For a loop, a similar process occurs, but after
# each iteration of the tree is evaluated, the resulting value is saved and the
# loop function then calls itself, repeating the process until the loop's 
# conditional statement evaluates to false and a final result has been has
# found.


# It should be noted that conditionals and loops both must be a single
# expression.

# For if-statements with both a true and a false branch
def conditional(args, varEnv, locEnv, funEnv, op, id_num):
    tree_section = global_vars.curr_tree[-1].get_node(id_num)
    for i in range(3):
        if (tree_section.getChild(i)).getVal() == None:
            return ("error", "Error: Incorrect number of arguments")

    conditional = (tree_section.getChild(0)).evaluate(varEnv, funEnv, locEnv)
    if conditional[0] == "error":
         return conditional

    constraints = [[["bool"]]]
    val_list = definePrimitive([conditional[1]], constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if isinstance(val_list[0], bool):
        if val_list[0]:
            body = (tree_section.getChild(1)).evaluate(varEnv, funEnv, locEnv)
        else:
            body = (tree_section.getChild(2)).evaluate(varEnv, funEnv, locEnv)
        if body[0] == "error":
            return body
        return verifyResult(body, varEnv, locEnv)
    else:
        return ("error", "Error: Bad type")


# For if statements with only one branch (ifTrue and ifFalse)
def condArrityTwo(args, varEnv, locEnv, funEnv, op, id_num):
    tree_section = global_vars.curr_tree[-1].get_node(id_num)
    for i in range(2):
        if (tree_section.getChild(i)).getVal() == None:
            return ("error", "Error: Incorrect number of arguments")

    conditional = (tree_section.getChild(0)).evaluate(varEnv, funEnv, locEnv)
    if conditional[0] == "error":
         return conditional

    constraints = [[["bool"]]]
    val_list = definePrimitive([conditional[1]], constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if isinstance(val_list[0], bool):
        if val_list[0] == op():
            body = (tree_section.getChild(1)).evaluate(varEnv, funEnv, locEnv)
            if body[0] == "error":
                return body
            return verifyResult(body, varEnv, locEnv)
        else:
            return ("not_error", "Nothing")
    else:
        return ("error", "Error: Bad type")


# While loops
def wloop(args, varEnv, locEnv, funEnv, op, id_num, prev_val="Nothing"):
    tree_section = global_vars.curr_tree[-1].get_node(id_num)
    if (tree_section.getChild(0)).getVal() == None or \
       (tree_section.getChild(1)).getVal() == None:
       return ("error", "Error: Incorrect number of arguments")

    conditional = (tree_section.getChild(0)).evaluate(varEnv, funEnv, locEnv)
    if conditional[0] == "error":
        return conditional

    if isBool(conditional[1]):
        if getBoolVal(conditional[1]):
            body = (tree_section.getChild(1)).evaluate(varEnv, funEnv, locEnv)
            if body[0] == "error":
                return body
            try:
                return wloop([], varEnv, locEnv, funEnv, op, id_num, body[1])
            except:
                return ("error", "Error: Infinite loop")
        else:
            prev_val = ("not_error", prev_val)
            return verifyResult(prev_val, varEnv, locEnv)
    else:
        return ("error", "Error: Bad type")


# For loops
def floop(args, varEnv, locEnv, funEnv, op, id_num, prev_val="Nothing", \
                                                                   iteration=0):
    tree_section = global_vars.curr_tree[-1].get_node(id_num)
    for i in range(4):
        if (tree_section.getChild(i)).getVal() == None:
            return ("error", "Error: Incorrect number of arguments")
    if (tree_section.getChild(1)).getVal() != "in":
        return ("error", "Error: \"in\" keyword is missing")

    constraints = [[["list"]]]
    list_arg = (tree_section.getChild(2)).evaluate(varEnv, funEnv, locEnv)
    if list_arg[0] == "error":
        return list_arg
    list_val = definePrimitive([list_arg[1]], constraints, varEnv, locEnv[-1])
    if list_val[0] == "error":
        return list_val
    if list_val[0] == "[]":
        list_val = []
        iterator_val = defineVar([args[0], "Nothing"], varEnv, locEnv, funEnv, \
                                                                           None)
        if iterator_val[0] == "error":
            return iterator_val
    else:
        list_val = string_to_list(list_val[0])

    if len(list_val) > iteration:
        var_arg = (tree_section.getChild(0)).evaluate(varEnv, funEnv, locEnv)
        if var_arg[0] == "error":
            return var_arg
        arg_list = [var_arg[1], str(list_val[iteration])]
        iterator_val = defineVar(arg_list, varEnv, locEnv, funEnv, None)
        if iterator_val[0] == "error":
            return iterator_val
        body = (tree_section.getChild(3)).evaluate(varEnv, funEnv, locEnv)
        if body[0] == "error":
            return body
        return floop([], varEnv, locEnv, funEnv, op, id_num, body[1], \
                                                                    iteration+1)
    else:
        prev_val = ("not_error", prev_val)
        return verifyResult(prev_val, varEnv, locEnv)


# Claims (assertions)
def claim(args, varEnv, locEnv, funEnv, op, id_num):
    constraints = [[global_vars.ALL_TYPES]]
    val_list = definePrimitive(args, constraints, varEnv, locEnv[-1])
    if val_list[0] == "error":
        return val_list

    if isinstance(val_list[0], bool):
        return (("not_error", "Nothing") \
                if val_list[0] \
                else ("claim_failed", "Claim failed: Claim not as expected"))
    return ("error", "Error: Claim can't be verified or disproven")


# Determines whether or not the parameter in the function header is simply a
# variable (eg. "n") or is part of a pattern (eg. "1=n").  It returns the name
# of the parameter.
def __parse_parameter(param):
    suffixes = ["<=", ">=", "<>", "=", "<", ">"]
    first_cut = reduce(lambda acc, x: min(acc, \
                            float("inf") if param.find(x)==-1 \
                                         else param.find(x)), \
                                                        suffixes, float("inf"))

    param = param[first_cut+1:]
    if reduce(lambda acc, x: acc or param[0] == x, [">", "<", "="], False):
        param = param[1:]

    for j in suffixes:
        if j in param:
            param = param[:param.find(j)]

    return param

# User-defined functions are evaluated similarly to evaluate() in run.py.  Each
# user-defined function has the entire function definition stored in the
# function environment.  When a user-defined function needs to be evaluated, the
# body of the function is retrieved and the code is executed, line-by-line, just
# as it would be ordinarily.  The local variable environments are represented as
# a stack of environments.  Whenever a function is called, a new environment is
# pushed onto the stack and initialized with the function's parameters.  When
# a function returns, its variable environment is popped off the stack.  The
# value returned from a function is simply the value of the last expression that
# was evaluated within a function.
def userFun(args, varEnv, locEnv, funEnv, body, id_num, pm=0):
    params = string_to_list(funEnv.getFunc(global_vars.curr_function[-1])[pm][0][1][0][2])

    if funEnv.getNumFuncs(global_vars.curr_function[-1]) != 1:
        for i in range(len(params)):
            if params[i] != "_" and \
                reduce(lambda acc, x: acc or x in params[i], \
                                                [">", "<", "="], False):
                params[i] = __parse_parameter(params[i])

    if len(params) != len(args):
        return ("error", "Error: Incorrect number of arguments")

    global_vars.user_function += 1
    locEnv.append(Environment())
    for i in range(len(args)):
        args[i] = ("not_error", args[i])
        arg = str(verifyResult(args[i], varEnv, locEnv[:-1])[1])

        if not isNum(params[i]) and params[i] != "_":
            result = defineVar([params[i], arg], varEnv, locEnv, funEnv, None)
            if result[0] == "error":
                return result

    expressions = body[1:]
    for i in range(len(expressions)):
        emptyTree = ExpressionTree(expressions[i])
        expTree = makeTree(emptyTree, funEnv, 0, False)
        expTree.epsteinCheck(varEnv, funEnv, emptyTree, locEnv)
        global_vars.curr_tree.append(expTree)

        if emptyTree.get_string_length() == 0:
            result = expTree.seven_and_checkCheck()
            if result[0] == "error":
                return ("error@"+str(i)+";"+str(pm), result[1])
            else:
                (error, val) = expTree.evaluate(varEnv, funEnv, locEnv)
                if error != "not_error":
                    if "@" in error:
                        return (error, val)
                    else:
                        return (error+"@"+str(i)+";"+str(pm), val)
                val = val.replace("<'>", "\"")
                varEnv.addBindit("it", val)
        else:
            return ("error@"+str(i)+";"+str(pm), "Error: Incorrect number of arguments")
        global_vars.curr_tree.pop()

    locEnv.pop()
    global_vars.curr_function.pop()
    global_vars.user_function -= 1
    return (error, handle_bool(val))


# This short function is necessary because if a function wishes to simply return
# a boolean value, the evaluator will "evaluate" the p-scheme boolean and turn
# it into a python boolean before casting it to a string.  This will ultimately
# lead to an "argument does not exist" error because python booleans will not
# be interpreted as p-scheme literals
def handle_bool(val):
    if val == "True":
        return "true"
    if val == "False":
        return "false"
    return val


