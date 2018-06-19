#
# Matthew Epstein
# list_string_handling.py
# This file deals with a lot of the annoying work of turning strings into lists
# and lists into strings.  (The code is read in as a string but in order to
# perform list operations, it's necessary to turn those string representations
# of lists into actual lists).  This file also handles error checking for
# erroneous quotes and brackets in the parsing porition of the program.
#

import re
import global_vars
from type_checking import *


# Handles parsing duties related to quotes and brackets.  This function is
# necessary for a number of reasons.  Without it, the evaluator would treat
# certain keywords and functions as code that should be executed, even if the
# text was within quotes.  Secondly, it allows for strings and lists to be
# within lists, and recognizes bad input.  And finally, without this function,
# the parser would divide up a list of n elements into n different parts,
# instead of interpreting it as a single entity.  The function returns either
# the parsed expression if there is no error, or an integer value that
# represents the type of error that was raised.
def handleQuotesAndBrackets(origExp):
    toReturn = 0

    noQuotes = re.sub('"[^"]*"', "\"\"", origExp) #remove quotes
    noQuotes = ' '.join(noQuotes.split()) #combine whitespace

    if "<'>" in noQuotes:
        toReturn = 3
    expression = ""

    regex = re.compile('[()]')
    noQuotes = regex.sub("", noQuotes)

    nestedCount = 0
    for i in range(len(noQuotes)):
        if nestedCount == 0:
            expression = expression + noQuotes[i]
        if noQuotes[i] == "[":
            if getMatchingBracket(noQuotes[i:]) != -1:
                nestedCount += 1
            else:
                toReturn = 2
                break
        elif noQuotes[i] == "]":
            nestedCount -=1
            if nestedCount == 0:
                expression = expression + noQuotes[i]
            if nestedCount < 0:
                toReturn = 1
                break

    if toReturn != 0:
        expression = noQuotes

    expression = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', expression)

    if expression[-1] == "check-error" and not global_vars.function_check:
        global_vars.check_error = True
    if expression[-1] == "check-expect" and not global_vars.function_check:
        global_vars.check_expect = True
    if toReturn != 0:
        return toReturn

    # adds brackets back in
    for i in range(len(expression)):
        start = 0
        while expression[i].find("[", start) != -1:
            temp = expression[i][:expression[i].find("[", start)] + \
                    noQuotes[noQuotes.find("["):getMatchingBracket(noQuotes)]
            expression[i] = temp + \
                            expression[i][expression[i].find("[", start)+2:]
            start = len(temp)
            noQuotes = noQuotes[getMatchingBracket(noQuotes):]

    # adds quotes back in
    temp = origExp
    for i in range(len(expression)):
        start = 0
        while expression[i].find("\"", start) != -1:
            if temp.find("\"") == temp.find("\"\""):
                temp = temp[(temp.find("\"\""))+2:]
                start = expression[i].find("\"\"", start)+2
                continue
            expression[i] = expression[i][:expression[i].find("\"", start)] + \
                            temp[temp.find("\""):
                            (temp.find("\"", (temp.find("\""))+2))+1] + \
                            expression[i][(expression[i].find("\"", start))+2:]
            temp = temp[(temp.find("\""))+1:]
            start = expression[i].find("\"", start)+1
            temp = temp[(temp.find("\""))+1:]
            start = expression[i].find("\"", start)+1

    return expression


# Removes the information inside brackets from an expression
# (eg. the line of code "[1, 2, 3] 4 insert" would turn into "[] 4 insert").
# This function is used by the string_to_list() function, which allows it to
# treat a list as a single entity, as opposed to many different elements.
def remove_brackets(noQuotes):
    expression = ""
    nestedCount = 0
    for i in noQuotes:
        if nestedCount == 0:
            expression = expression + i
        if i == "[":
            nestedCount += 1
        elif i == "]":
            nestedCount -=1
            if nestedCount == 0:
                expression = expression + i
    return expression


# Returns the location of the closing bracket that corresponds to the first
# opening bracket.  Helpful for when brackets are nested
def getMatchingBracket(noQuotes):
    nestedCount = 0
    for i in range(len(noQuotes)):
        if noQuotes[i] == "[":
            nestedCount += 1
        elif noQuotes[i] == "]":
            nestedCount -=1
            if nestedCount == 0:
                return i+1
    return -1


# If a list is hard-coded in as [1.0, 2.0, 3.0], for example, this function will
# turn that list into [1, 2, 3]
def int_float_handling(arg):
    if float(arg) == int(float(arg)):
         return int(float(arg))
    else:
        return float(arg)


# Turns a string into a list.  I'm not entirely sure why the lstrip()s are
# necessary, but sometimes leading spaces pop up unexpectedly.
def string_to_list(string):
    if string == "[]":
        return []
    elif type(string) == list:
        return string
    else:
        string = string[1:-1]

    new_list = []
    noQuotes = re.sub('"[^"]*"', "\"\"", string)
    expression = remove_brackets(noQuotes)

    if expression.find(",") == -1:
        if isNum(string):
            new_list.append(int_float_handling(string))
        else:
            new_list.append(string)
        return new_list

    while expression != "":
        expression = expression.lstrip()
        if expression[0] == "\"":
            new_list.append((string[:string[1:].find("\"")+2]).lstrip())
            expression = expression[(expression[1:].find("\""))+4:]
            string = string[(string[1:].find("\""))+4:]
        elif expression[0] == "[":
            new_list.append((string[:getMatchingBracket(string)]).lstrip())
            expression = expression[(expression[1:].find("]"))+3:]
            string = string[getMatchingBracket(string)+2:]
        else:
            if expression.find(",") != -1:
                if isNum(expression[:expression.find(",")]):
                    new_list.append(\
                        int_float_handling(expression[:expression.find(",")]))
                else:
                    new_list.append((expression[:expression.find(",")]).lstrip())
                expression = expression[(expression.find(","))+2:]
                string = string[(string.find(","))+2:]
            else:
                if isNum(expression):
                    new_list.append(int_float_handling(expression))
                else:
                    new_list.append(expression.lstrip())
                expression = ""

    return new_list


# Turns a list into a string.  Uses the stringify() function as a helper
# function.
def list_to_string(my_list):
    if my_list == []:
        return "[]"

    new_string = "[" + stringify(my_list[0], "")
    my_list = my_list[1:]

    for x in my_list:
        new_string = new_string + ", " + stringify(x, "")
    new_string += "]"

    return new_string


# This function handles the potentially recursive nature of turning a list into
# a string.  If the original list contains elements that are lists than those
# lists will need to be turned into strings as well.
def stringify(elem, string):
    if type(elem) == list:
        if elem == []:
            return "[]"

        string = "[" + stringify(elem[0], string)
        elem = elem[1:]
        for x in elem:
            string = string + ", " + stringify(x, string)
        return string + "]"        
    elif type(elem) == str:
        return elem
    else:
        return str(elem)


# If a list has a maybe value in it, this function turns that maybe into either
# a true or false.
def handle_maybe(string):
    my_list = string_to_list(string)
    helper = lambda x: handle_maybe(x) if isList(x) else \
                                x if not x=="maybe" else \
                                "true" if randint(0,1)==0 else "false"
    new_string = map(helper, my_list)
    return list_to_string(new_string)


# If a list has a 7 value in it, this function returns an error.  If the list
# has seven in it, this function turns the seven into 7.  This function uses
# the scan_for_7s() and replace_sevens() functions as helper functions.
def handle_seven(string):
    if string_check(string) != None:
        return string

    if scan_for_7s(string):
        return True

    if string != "[]":
        a = string_to_list(string)
    return list_to_string(replace_sevens(string))


# Ensure that a list contains no 7s.  Return True if a 7 is present and False
# otherwise.
def scan_for_7s(string):
    my_list = string_to_list(string)
    helper = lambda x: scan_for_7s(x) if isList(x) else True if x==7 else False
    return reduce(lambda acc, x: acc or helper(x), my_list, False)


# Replaces the seven function with the number 7 and returns the updated list.
# If no sevens are present, the original list is returned.
def replace_sevens(string):
    my_list = string_to_list(string)
    helper = lambda x: replace_sevens(x) if isList(x) \
                                         else 7 if x=="seven" else x
    return map(helper, my_list)


# Ensures that all elements of a list are valid (eg. variables are defined,
# types are correct, etc.)
def list_check(string, varEnv, locEnv):
    list_arg = string_to_list(string)
    for i in list_arg:
        (error, val) = \
                general_type(str(i), [global_vars.ALL_TYPES], varEnv, locEnv)
        if error != "" and error[0] == "error":
            return error


# Ensures a list that's hardcoded in is of the data-comma-space-data format
def string_check(string):
    noQuotes = re.sub('"[^"]*"', "\"\"", string)
    for i in range(len(noQuotes)):
        try:
            if (noQuotes[i] == " " and \
                    (noQuotes[i-1] != "," or noQuotes[i+1] == "]")) or \
               (noQuotes[i] == "," and \
                    (noQuotes[i+1] != " " or noQuotes[i-1] == "[")):
                return ("error", "Error: Bad list format")
        except:
            return ("error", "Error: Bad list format")


# Ensures no element of a list is a literal (called in the function_check()
# function in the pscm file).  If there are four quotes in the argument the
# format will be checked in the string pattern matching class.
def var_check(a_list):
    isNon_numLiteral = lambda x: isBool(x) or \
              (isString(x) and x.count("\"") != 4) or isList(x) or isNothing(x)
    return reduce(lambda acc, x: (acc or isNon_numLiteral(x)), a_list, False)

