#
# Matthew Epstein
# global_vars.py
# This file contains the program's global variables.  All variables here are
# either constants or relate to the state of the program (eg. the expression
# currently being evaluated or whether a check-error or check-expect has been
# declared).  As a general rule, only information that I felt could be known by
# every other module in the program was allowed to be stored in a global
# variable.
# This file is at the lowest level of the program's file architecture.  It
# "includes" no other file, meaning that every file in p-scheme has access to
# the global variables
#


filename = None
ALL_TYPES = ["num", "bool", "nonetype", "str", "list"]
PRIMITIVES = ["it", "+", "-", "*", "/", "%", "^", "!", "v/", "int", "and", \
			  "or", "xor", "nand", "nor", "not", ">", "<", ">=", "<=", "=", \
			  "<>", "range", "rangeFrom", "today", "newList", "length", \
			  "null?", "append", "push", "get", "put", "init", "insert", \
			  "remove", "seven", "++", "num", "bool", "str", "list", \
			  "nonetype", "print", "input", "val", "check-error", \
			  "check-expect", "empty", "if", "ifTrue", "ifFalse", "while", \
			  "for", "claim", "define", "done", "wholesomeRemark", "exit", \
			  "random", "write", "getch", "clear_screen", "map", "fold", \
			  "filter", "all", "exists"]
VARIABLE_RESERVED_TERMS = ["error", "it", "val", "check-expect", \
                           "check-error", "if", "ifTrue", "ifFalse", "while", \
                           "empty", "for", "in", "define", "done"]
function_check = False
user_function = 0
curr_function = []
check_error = False
check_expect = False
curr_tree = []
function_error_check = False

def reset():
    global user_function, curr_function, check_error, check_expect, curr_tree
    user_function = 0
    curr_function = []
    check_error = False
    check_expect = False
    curr_tree = []
