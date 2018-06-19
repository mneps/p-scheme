# 
# Matthew Epstein
# comments.py
# This file is responsible for handling comment sanitization and for raising
# errors if a comment or a string is entered in an incorrect format.  The
# handle_comments() function is admittedly difficult to read, and I apologize
# for that.  I ran into a number of issues accounting for the various edge-cases
# and the function kept growing and growing.
#


import global_vars
from error_handling import *

comment = False
comment_start_line = None
C_START = "!@"
C_END = "#$"
QUOTE = "\""


# Ensures that comments are of the correct format
def handle_strings(expression, lineCount, numLines, origLines):
    if expression.count("\"") % 2 == 0:
        return
    val = "Error: It never ends"
    return origLines.RaiseException(lineCount, numLines, val)



# Sanitizes comments from a line of code
def handle_comments(line, lines, lineCount, origLines):
    loop = True
    origLine = lines[line]
    currLine = lines[line]
    
    toReplace = "q"
    while toReplace in lines[line]:
        toReplace = toReplace + "q"
    markerA = toReplace + '1'
    markerB = toReplace + '2'

    global comment, comment_start_line, C_START, C_END, QUOTE
    while loop:
        loop = False
        # deals with the end of block comments and the case of !@\n"#$"
        if C_END in currLine and comment:
            comment = False
            currLine = currLine[currLine.find(C_END)+2:]
            loop = True       
        #deals with the middle of block comments
        if comment and C_END not in currLine and currLine != "":
            currLine = ""
            loop = True
        # deals with the start of block comments and checks for the "!@" case
        if C_START in currLine and C_END not in currLine:
            if currLine[:currLine.find(C_START)].count(QUOTE) % 2  == 1:
                currLine = currLine[:currLine.find(C_START)] + markerA + \
                           currLine[currLine.find(C_START)+2:]
                loop = True
            else:
                comment_start_line = lineCount
                comment = True
                currLine = currLine[:currLine.find(C_START)]
                loop = False
        # deals with comments that are contained on one line, comments that end
        # without starting, and checks for the "#$" case
        if currLine.find(C_START) < currLine.find(C_END) and not comment:
            if currLine.find(C_START) == -1:
                if currLine[:currLine.find(C_END)].count(QUOTE) % 2  == 1:
                    currLine = currLine[:currLine.find(C_END)] + markerB \
                             + currLine[currLine.find(C_END)+2:]
                    loop = True
                elif not comment:
                    val = "Error: Comment ends without starting"
                    comment = False
                    return origLines.RaiseException(lineCount, 1, val)
                else:
                    loop = True
            else:
                if currLine[:currLine.find(C_START)].count(QUOTE) % 2  == 1:
                    currLine = currLine[:currLine.find(C_START)] \
                            + markerA + currLine[currLine.find(C_START)+2:]
                    loop = True
                else:
                    currLine = currLine[:currLine.find(C_START)] + \
                                  currLine[currLine.find(C_END)+2:]
                    loop = True
        # deals with the invalid case of comments in the #$___!@ format when
        # there is no comment currently being written
        elif currLine.find(C_START) > currLine.find(C_END) and not comment:
            if currLine[:currLine.find(C_END)].count(QUOTE) % 2  == 1:
                currLine = currLine[:currLine.find(C_END)] \
                 + markerB + currLine[currLine.find(C_END)+2:]
                loop = True
            elif currLine[:currLine.find(C_START)].count(QUOTE) % 2  == 1:
                currLine = currLine[:currLine.find(C_START)] \
                 + markerA + currLine[currLine.find(C_START)+2:]
                loop = True
            else:
                val = "Error: Comment ends without starting"
                comment = False
                return origLines.RaiseException(lineCount, 1, val)
    if lineCount == len(lines) and comment \
                                    and not global_vars.function_error_check:
        val = "Error: It never ends"
        comment = False
        origLines.RaiseException(comment_start_line, 1, val, 3)

    return currLine.replace(markerA, "!@").replace(markerB, "#$")


