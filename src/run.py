#!/usr/bin/python

# 
# Matthew Epstein
# run.py
# This file is the foundation for all of p-scheme.  Contained within are
# functions to initialize the environments, parse the file, evaluate an
# expression, and handle errors.  Many of functions in this file are quite
# large, but since the purpose of this file is to accomplish tasks that only
# need to be done once (eg. initialize the environments, parse the file, etc.),
# breaking up the functions into smaller chuncks seemed unnecessary and may
# have even made the code more difficult to understand.  To compensate, I have
# written fairly detailed comments before each of the functions in question,
# explaining what that function does.
#


from __future__ import print_function #otherwise print cannot be in a lambda
import math
import re
import operator
import os
import sys
import time
import global_vars
from comments import *
from env import *
from error_handling import *
from expTree import *
from getch import *
from makeTree import *
from node import *
from list_string_handling import *
from primitives import *


# Creates the starting environments by adding all the primitive functions to
# the function environments and adding the "it" variable to the variable
# environment (and initializing it as Nothing).
def addPrimitives():
    varEnv = Environment()
    varEnv.addBind("it", "Nothing")

    funEnv = Environment()
    # arithmetic
    funEnv.addBind("+", (numArrityTwo, operator.add, 2))
    funEnv.addBind("-", (numArrityTwo, operator.sub, 2))
    funEnv.addBind("*", (numArrityTwo, operator.mul, 2))
    funEnv.addBind("/", (numArrityTwo, operator.div, 2))
    funEnv.addBind("%", (numArrityTwo, operator.mod, 2))
    funEnv.addBind("**", (numArrityTwo, operator.pow, 2))
    funEnv.addBind("random", (numArrityTwo, randint, 2))
    funEnv.addBind("!", (numArrityOne, math.factorial, 1))
    funEnv.addBind("v/", (numArrityOne, math.sqrt, 1))
    # booleans
    funEnv.addBind("and", (booleans, operator.and_, 2))
    funEnv.addBind("or", (booleans, operator.or_, 2))
    funEnv.addBind("xor", (booleans, operator.xor, 2))
    funEnv.addBind("nand", (booleans, (lambda x, y: not (x and y)), 2))
    funEnv.addBind("nor", (booleans, (lambda x, y: not (x or y)), 2))
    funEnv.addBind("not", (boolNot, operator.not_, 1))
    # comparison
    funEnv.addBind(">", (comparison, operator.gt, 2))
    funEnv.addBind("<", (comparison, operator.lt, 2))
    funEnv.addBind(">=", (comparison, operator.ge, 2))
    funEnv.addBind("<=", (comparison, operator.le, 2))
    funEnv.addBind("=", (equal_nequal, operator.eq, 2))
    funEnv.addBind("<>", (equal_nequal, operator.ne, 2))
    # range
    funEnv.addBind("range", (numArrityOne, (lambda x: range(x)), 1))
    funEnv.addBind("rangeFrom", (numArrityTwo, (lambda x, y: range(x,y)), 2))
    # lists
    funEnv.addBind("today", (arrityZero, (lambda: today()), 0))
    funEnv.addBind("newList", (arrityZero, (lambda: []), 0))
    funEnv.addBind("length", (listArrityOne, (lambda x: len(x)), 1))
    funEnv.addBind("null?", \
            (listArrityOne, (lambda x: "true" if len(x)==0 else "false"), 1))
    funEnv.addBind("append", (append_push, (lambda val, ds: ds.append(val)), 2))
    funEnv.addBind("push", (append_push, (lambda val, ds: ds.insert(0,val)), 2))
    funEnv.addBind("get", (listGet, (lambda pos, ds: ds[pos-today()]), 2))
    funEnv.addBind("put", (listPut, \
        (lambda val,pos,ds: ds[:pos-today()]+[val]+ds[pos+1-today():] \
                                if pos-today()+1!=0 \
                                else ds[:pos-today()]+[val]), 3))
    funEnv.addBind("init", (listInit, (lambda val, size: [val]*size), 2))
    funEnv.addBind("insert", \
            (listInsert, (lambda val,pos,ds: ds.insert(pos-today(),val)), 3))
    funEnv.addBind("remove", (listRemove,
        (lambda pos,ds: ds[:pos-today()]+ds[pos+1-today():] \
                                if pos-today()+1!=0 \
                                else ds[:pos-today()]), 2))
    # miscellaneous
    funEnv.addBind("seven", (arrityZero, (lambda: 7), 0))
    funEnv.addBind("clear_screen", \
                        (arrityZero, (lambda: print("\033[H\033[J")), 0))
    funEnv.addBind("exit", (arrityZero, (lambda: exit(0)), 0))
    funEnv.addBind("wholesomeRemark", (happy, None, 0))
    funEnv.addBind("++", (concat, operator.add, 2))
    # casting
    funEnv.addBind("int", (numArrityOne, (lambda x: int(x)), 1))
    funEnv.addBind("num", (castNum, \
                            (lambda x: int(float(x)) if int(float(x))==float(x)
                                                     else float(x)), 1))
    funEnv.addBind("bool", (castBool, None, 1))
    funEnv.addBind("str", (castStr, (lambda x: "\""+x+"\""), 1))
    funEnv.addBind("list", (castList, (lambda x: "["+str(x)+"]"), 1))
    funEnv.addBind("nonetype", (castNonetype, None, 1))
    # higher-order list functions
    funEnv.addBind("map", (listMap, None, 2))
    funEnv.addBind("fold", (listFold, None, 3))
    funEnv.addBind("filter", (listFilter, None, 2))
    funEnv.addBind("all", (listAll, None, 2))
    funEnv.addBind("exists", (listExists, None, 2))
    # basic operations
    funEnv.addBind("print", (printVar, (lambda x: print(x)), 1))
    funEnv.addBind("write", (printVar, (lambda x: sys.stdout.write(str(x))), 1))
    funEnv.addBind("input", (userInput, (lambda x: raw_input(x)), 1))
    funEnv.addBind("getch", (getChar, (lambda: getch()), 0))
    funEnv.addBind("val", (defineVar, None, 2))
    funEnv.addBind("check-error", (check_error, None, 1))
    funEnv.addBind("check-expect", (check_expect, None, 2))
    funEnv.addBind("empty", (empty, None, 0))
    funEnv.addBind("if", (conditional, None, 3))
    funEnv.addBind("ifTrue", (condArrityTwo, (lambda: True), 2))
    funEnv.addBind("ifFalse", (condArrityTwo, (lambda: False), 2))
    funEnv.addBind("while", (wloop, None, 2))
    funEnv.addBind("for", (floop, None, 4)) # second argument is the "in" keyword
    funEnv.addBind("claim", (claim, None, 1))

    return (varEnv, funEnv)


# Returns the number day of the year it is today.  Jan 1 is 0; Dec 31 on a
# non-leap year is 364.
def today():
    return (time.localtime().tm_yday-1)


# Strips a line of code of comments and line continuations (<~).  The function
# returns the "stripped" line, as well as information regarding if the
# expression is finished or if it extends onto the next line of code as well.
def condense_lines(line, lines, lineCount, origLines, numLines, fullExp, \
                                                            comment_check=True):
    if comment_check:
        lines[line] = handle_comments(line, lines, lineCount, origLines)
    if lines[line] == "error":
        global_vars.function_check = False
        return ("error", "", 0, lines[line])

    lines[line] = (lines[line]).lstrip()
    if lines[line] == "" and numLines == 1:
        return ("continue", "", 1, lines[line])
    if lines[line] == "" and numLines != 1:
        return ("continue", fullExp, numLines+1, lines[line])
    if (lines[line])[:2] == "<~":
        fullExp = (lines[line])[2:] + ' ' + fullExp
        return ("continue", fullExp, numLines+1, lines[line])
    elif fullExp != "":
        fullExp = lines[line] + ' ' + fullExp
    else:
        fullExp = lines[line]

    if handle_strings(fullExp, lineCount, numLines, origLines) == "error":
        global_vars.function_check = False
        return ("error", "", 0, lines[line])

    return ("finished", fullExp, numLines, lines[line])



# Does an initial scan of the document passed in and uses the condense_lines()
# function to modify the lines that are to be evaluated in the evaluate()
# function.  Specifically, the function strips the file of comments and adds
# user-defined functions to the function environment.  After a user-defined
# function has been added, that function definition is erased from the file,
# evaluate() would otherwise evaluate the function definition, which is
# obviously incorrect: a function should only be evaluated when it is actually
# called.
def function_check(lines_to_evaluate, origLines, funEnv):
    global_vars.function_check = True
    lineCount = 0
    fullExp = ""
    numLines = 1
    function_definition = False

    # need to make a copy otherwise it will modify the lines array that will be
    # passed to evaluate() 
    lines = []
    for line in lines_to_evaluate:
        lines.append(line)

    for line in range(len(lines)):
        lineCount += 1

        (status, fullExp, numLines, single_line) = \
            condense_lines(line, lines, lineCount, origLines, numLines, fullExp)
        lines_to_evaluate[line] = single_line
        if status == "error":
            if line+1 == len(lines):
                continue
            return
        if status == "continue":
            lines[line] = ""
            continue
        if status == "finished":
            lines[line] = fullExp
            fullExp = ""
            expLength = numLines

        expression = handleQuotesAndBrackets(lines[line])
        if isinstance(expression, int):
            global_vars.function_check = False
            if lines[line][-11:] == "check-error":
                continue
            else:
                return
        expression.reverse()

        if expression[0] == "define":
            if function_definition:
                val = "Error: Can't define a function within a function"
                origLines.RaiseException(lineCount, numLines, val, 3)
            else:
                if len(expression) != 3:
                    val = "Error: Incorrect number of arguments"
                    origLines.RaiseException(lineCount, numLines, val, 3)
                constraints = [[["list"]]]

                if isList(expression[2]) and string_check(expression[2]) != None:
                    (error, val) = string_check(expression[2])
                    origLines.RaiseException(lineCount, numLines, val, 3)

                empty = Environment()
                (toAppend, constraints[0][0]) = \
                        general_type(expression[2], constraints[0], empty, empty)
                if toAppend[0] == "error":
                    origLines.RaiseException(lineCount, numLines, toAppend[1], 3)
                val_list = [toAppend]

                if var_check(string_to_list(expression[2])):
                    val = "Error: Word is reserved"
                    origLines.RaiseException(lineCount, numLines, val, 3)

                reserved_terms = global_vars.PRIMITIVES + ["it", "in", "done"]
                reserved_symbols = ["\"", "[", "]", "<~", ".", "<'>", "//"]

                if isLiteral(expression[1]) or expression[1] in reserved_terms:
                    val = "Error: Word is reserved"
                    origLines.RaiseException(lineCount, numLines, val, 3)
                for i in reserved_symbols:
                    if i in expression[1]:
                        val = "Error: Name contains reserved symbol"
                        origLines.RaiseException(lineCount, numLines, val, 3)

                val_list[0] = string_to_list(val_list[0])

                function_definition = True
                function_lineCount = lineCount
                function_numLines = numLines
                name = expression[1]
                arrity = len(val_list[0]) 
                function_body = [expression]
                for i in range(line-numLines, line+1):
                    lines_to_evaluate[i] = ""
                continue
        elif function_definition:
            if expression == ["done"]:
                function_definition = False
                funEnv.addBind(name, \
                    (userFun, function_body, arrity, [function_lineCount, line]))
                for i in range(line-numLines, line+1):
                    lines_to_evaluate[i] = ""
            else:
                function_body.append(expression)
                for i in range(line-numLines, line+1):
                    lines_to_evaluate[i] = ""
        else:
            if expression == ["done"]:
                val = "Error: No function definition in progress"
                origLines.RaiseException(lineCount, numLines, val, 3)
        numLines = 1

    if function_definition:
        val = "Error: It never ends"
        origLines.RaiseException(function_lineCount, function_numLines, val, 3)
    global_vars.function_check = False




# If an error is raised within a function, the error message should point to
# the line within the function where the error occurs.  This function ensures
# that that happens.
def getErrorLine(funEnv, origLines, error):
    global_vars.function_error_check = True
    fun_start = funEnv.getVal(global_vars.curr_function[-1], "function")[3][0]
    fun_stop = funEnv.getVal(global_vars.curr_function[-1], "function")[3][1]
    error_num = int(error.split("@")[1])+1

    lines = []
    for i in range(fun_start+1, fun_stop+1):
        lines.append(origLines.getLine(i-1))

    lineCount = fun_start - 1
    fullExp = ""
    numLines = 1
    trueLineCount = 0

    for line in range(len(lines)):
        lineCount += 1
        (status, fullExp, numLines, _) = \
            condense_lines(line, lines, lineCount, origLines, numLines, fullExp)
        if status == "error":
            return (lineCount, numLines)
        if status == "continue":
            continue
        if status == "finished":
            trueLineCount += 1
            if trueLineCount == error_num:
                return (lineCount+1, numLines)
            lines[line] = fullExp
            fullExp = ""
            expLength = numLines
            numLines = 1



# This function goes line by through a file, parsing each line of code, forming
# the expression's abstract syntax tree, evaluating the expression, and
# handling the result, as necessary.  
def evaluate(lines, origLines, varEnv, funEnv):
    beginCheck = False
    fullExp = ""
    numLines = 1 #number of lines a multiline expression is

    lineCount = 0
    for line in range(len(lines)):
        lineCount += 1

        (status, fullExp, numLines, _) = \
                        condense_lines(line, lines, lineCount, origLines, \
                                                    numLines, fullExp, False)
        if status == "continue":
            lines[line] = ""
            continue
        if status == "finished":
            lines[line] = fullExp
            fullExp = ""
            expLength = numLines

        if not beginCheck:
            if lines[line] != "Ready to go":
                val = "Error: Missing the header"
                origLines.RaiseException(lineCount, numLines, val)
            else:
                beginCheck = True
                continue


        expression = handleQuotesAndBrackets(lines[line])

        if isinstance(expression, int):
            if global_vars.check_error:
                global_vars.check_error = False
                val = "Expression failed, as expected"
                print("-->", val)
                numLines = 1
                continue
            else:
                if expression == 1:
                    val = "Error: Inconsistent brackets"
                if expression == 2:
                    val = "Error: It never ends"
                if expression == 3:
                    val = "Error: Escaping when no escape is necessary"
                origLines.RaiseException(lineCount, numLines, val)
        expression.reverse()

        locEnv = Environment()
        emptyTree = ExpressionTree(expression)
        expTree = makeTree(emptyTree, funEnv, 0, False)
        expTree.epsteinCheck(varEnv, funEnv, emptyTree, [locEnv])
        global_vars.curr_tree.append(expTree)

        if emptyTree.get_string_length() == 0:
            if expTree.sevenCheck():
                (error, val) = ("error", "Error: Argument is 7")
            else:
                (error, val) = expTree.evaluate(varEnv, funEnv, [locEnv])
                val = val.replace("<'>", "\"")
        else:
            (error, val) = ("error", "Error: Incorrect number of arguments")

        if not global_vars.check_error and len(global_vars.curr_function) != 0 \
           and global_vars.curr_function[-1] not in global_vars.PRIMITIVES and \
           "@" in error:
           (lineCount, numLines) = getErrorLine(funEnv, origLines, error)
           origLines.RaiseException(lineCount, numLines, val)

        if "errorDec" in error: #could be errorDec or errorDec@_
            (error, val) = origLines.RaiseException(lineCount, numLines, val, 1)
        if "claim_failed" in error:
            (error, val) = origLines.RaiseException(lineCount, numLines, val, 2)
        if error != "not_error" and "error" in error:
            (error, val) = origLines.RaiseException(lineCount, numLines, val)

        if global_vars.check_error or global_vars.check_expect:
            print("-->", val)

        if global_vars.check_error or global_vars.check_expect:
            varEnv.addBindit("it", "\"" + val + "\"")
        else:
            varEnv.addBindit("it", val)
        numLines = 1
        global_vars.reset()

    if fullExp != "":
        val = "Error: Incorrect number of arguments"
        origLines.RaiseException(lineCount, numLines, val)


def main():
    open(global_vars.filename, 'r')
    if os.stat(global_vars.filename).st_size == 0: #file is empty
        print("  File {}; {}\n    {}{}".format(global_vars.filename, \
                                            "line 1", "\n", "Error: No code"))
        exit(0)

    lines = [line.rstrip('\n') for line in open(global_vars.filename)]
    origLines = OriginalLines(lines)
    (varEnv, funEnv) = addPrimitives()
    function_check(lines, origLines, funEnv)
    evaluate(lines, origLines, varEnv, funEnv)
    

if __name__ == '__main__':
    assert (len(sys.argv) == 2)
    if sys.argv[1][-5:] != ".pscm":
        print ("Error: unrecognizable file extension")
        exit(1)
    global_vars.filename = sys.argv[1]
    main()
    

