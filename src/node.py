#
# Matthew Epstein
# node.py
# This file holds the node class.  The two most important methods in this
# class--which also are two of the most parts of p-scheme as a whole--are the
# evaluate() function, which recursively evaluates a node and its subtree in
# order to produce a result, as well as the epsteinCheck() function, which is a 
# tree-rebalancing algorithm named after...well, me.  Both functions are
# explained in more detail below.
#

import sys
import global_vars
from define_primitive import *
from list_string_handling import *
from type_checking import *



class Node:
    # Initializes the class.  For functions, numChildren will be equal to the
    # arrity of that function while for variables and literals, numChildren will
    # equal to -1.
    def __init__(self, val, numChildren, root, id_num):
        self.val = val
        self.numChildren = numChildren
        self.children = [None] * self.numChildren #[None]*-1 = []
        self.root = root # will be a boolean value
        self.id_num = id_num
        if numChildren == -1:
            self.result = val
        else:
            self.result = None

    # The four functions below are all fairly self-explanatory.
    def getChild(self, i):
        return self.children[i]

    def getVal(self):
        return self.val

    def getNumChildren(self):
        return self.numChildren

    def addChild(self, newChild, i):
        self.children[i] = newChild


    # This function takes in a node expression tree and evaluates it by 
    # recursively calling this function on that node's children.  Along the way,
    # the function checks to make sure it is not evaluating the "useless" branch
    # an if-statement or the body of a loop that has already terminated.  This
    # is important because functions that update values and are in the garbage
    # part of a conditional or loop would be evaluated without this check.  A
    # A consequence of this method is that if there is an error in the garbage
    # part of the conditional or loop, the evaluator will not find it (although
    # this is not necessarily a bad thing).  This function also calls the
    # __pattern_matching() function.
    def evaluate(self, varEnv, funEnv, locEnv):
        checks = ["check-error", "check-expect"]
        if self.val in checks and global_vars.user_function > 0:
            return ("error", "Error: Can't check within a function")

        if self.root and self.val != None and self.numChildren == -1:
            val_list = definePrimitive([self.val], [[global_vars.ALL_TYPES]], \
                                                            varEnv, locEnv[-1])
            if val_list[0] == "error":
                return val_list
            return ("not_error", str(val_list[0]))

        if self.numChildren != -1:
            conds_and_loops = ["if", "ifTrue", "ifFalse", "while", "for"]
            if self.val not in conds_and_loops:
                for i in range(self.numChildren):
                    self.children[i].result = \
                            (self.children[i]).evaluate(varEnv, funEnv, locEnv)
                #self.children = [(a,b) for (a,b) in self.children if b != None]
                for i in range(len(self.children)):
                    if self.children[i].result[0] == "not_error":
                        self.children[i].result = self.children[i].result[1]
                    else:
                        return self.children[i].result
        else:
            return ("not_error", self.val)

        args = reduce(lambda acc, x: acc+[x.result], self.children, [])
        args = filter(lambda x: x != None, args)

        if self.val not in global_vars.PRIMITIVES:
            global_vars.curr_function.append(self.val)

        if funEnv.getNumFuncs(self.val) == 1:
            (fun, op) = funEnv.getVal(self.val, "function")[:2]
            try:
                (error, val) = fun(args, varEnv, locEnv, funEnv, op, self.id_num)
            # otherwise when the user uses the exit() function the "Recursion 
            # too deep" error will print
            except SystemExit:
                exit(0)
            except:
                return ("error", "Error: Recursion too deep")
        else:
            return self.__pattern_matching(funEnv, varEnv, locEnv, args)

        return (error, str(val))


    # This function serves as a helper function for the evaluate() function.  It
    # checks to make sure the input to the function is valid and then checks the
    # input against the function's patterns to find the correct version of
    # the function to call.
    def __pattern_matching(self, funEnv, varEnv, locEnv, args):
        param = funEnv.getFunc(self.val)[0][0][1][0][-1][1:-1]
        vals = []
        for i in range(len(args)):
            literal_type = get_pattern_type(self.val, funEnv, i)
            (result, constraint) = \
              general_type(args[i], [[literal_type[1]]], varEnv, locEnv[-1])
            if result[0] == "error":
                return result
            (error, val) = ("not_error", result)
            if not isLiteral(val):
                val = getValofType(val, constraint, varEnv, locEnv[-1])
            if isString(val) and len(val) > 52 and \
                                    val[0] == "\"" and val[-1] == "\"":
                return ("error", "Error: String is too long to match against")
            vals.append(val)

        vals = map(lambda x: x if x!="maybe" else "true" \
                                    if randint(0,1)==0 else "false", vals)
        for i in range(funEnv.getNumFuncs(self.val)):
            if reduce(lambda acc, x: \
                    (funEnv.getPM(self.val)).matches(x, i) and acc, vals, True):
                (fun, body) = funEnv.getFunc(self.val)[i][0][:2]
                try:
                    return fun(args, varEnv, locEnv, funEnv, body, self.id_num, i)
                except SystemExit: # see comment in lines 96-97
                    exit(0)
                except:
                    return ("error", "Error: Recursion too deep")
            if i == funEnv.getNumFuncs(self.val)-1:
                return ("error", "Error: Input matches no patterns")


    # Detailing exactly how this algorithm works would be far too complicated,
    # for a comment, so instead I will simply explain the issue this algorithm
    # solves.  I intend to give a full description of how this algorithm works
    # in the completed p-scheme documentation (although that will not be
    # finished for some time).
    # The issue at hand is that because there are separate environments for
    # functions and variables, it only makes sense that a function and a
    # variable ought to be able to share the same name.  If this were not the,
    # case, the environments could not be said to be truly separate.  Now, say
    # that a user declares the plus sign (+) to be equal to 1.  This does not
    # override the addition operation, because the environments are separate.
    # Now, futher imagine that this pesky user writes the following line of
    # code:
    #   + + +
    # This code should evaluate to 2, since the first two +'s should be
    # recognized as variables with values equal to 1, while the final + is the
    # primitive addition operator.  The corresponding evaluation tree would look
    # like this:
    #                               + 
    #                              / \
    #                             +   +
    # However, the above tree is not the one that will be created by the
    # makeTree() function.  The actual tree will be created will look like this:
    #                               + 
    #                              / \
    #                             +   
    #                            / \
    #                           +
    #                          / \
    # Obviously, this is incorrect.  Evaluating the above tree will result in an
    # "Incorrect number of arguments" error--not 2.  The algorithm below is
    # capable of recognizing when a tree is incorrectly formatted and will
    # correctly rebalance it.
    def epsteinCheck(self, varEnv, funEnv, tree, locEnv):
        if tree.getNoneCount() == 0:
            return
        none_check = lambda x: x.val==None
        # if-statement below handles cases like (+ print), (true (1 \\- val) val)
        if self.numChildren != -1 and \
           all(self.children[i].val == None for i in range(self.numChildren)):
            if locEnv[-1].inEnv(self.val) or varEnv.inEnv(self.val):
                tree.updateNoneCount(-self.numChildren)
                if funEnv.getArrity(self.val) != 0:
                    self.numChildren = -1
            else:
                return
        if self.numChildren != -1 and filter(none_check, self.children) != []:
            if self.children[0].val == None:
                return
            (status, node) = (self.children[0]).__findSubtree(varEnv, funEnv, \
                                                               tree, locEnv[-1])
            if status == "yes":
                for i in range((len(self.children)-1), -1, -1):
                    if self.children[i].val == None:
                        tree.updateNoneCount(-1)
                        self.addChild(node, i)
                        # if-statement below handles cases like (7 (5 - val) +)
                        # where - has already been declaraed as a variable
                        if self.children[i].numChildren != -1:
                            if all(self.children[i].children[j].val == None \
                                   for j in range(self.children[i].numChildren)):
                                tree.updateNoneCount(-self.children[i].numChildren)
                                if funEnv.getArrity(self.children[i].val) != 0:
                                    self.children[i].numChildren = -1
                            break
            else: #status == "maybe"
                return
        elif self.numChildren != -1:
            for i in range(self.numChildren):
                self.children[i].epsteinCheck(varEnv, funEnv, tree, locEnv)
            return
            if self.root:
                return
        else: # node value is a variable/literal
            return
        return self.epsteinCheck(varEnv, funEnv, tree, locEnv)


    # This is a private helper function to epsteinCheck()
    def __findSubtree(self, varEnv, funEnv, tree, locEnv):
        # Don't need to check if a literal since literals can't have children
        var = locEnv.inEnv(self.val) or varEnv.inEnv(self.val)
        fun = funEnv.inEnv(self.val) and (funEnv.getArrity(self.val) == 0)
        left = False

        # Variables/literals and functions of arrity zero will both always be
        # leaves and are therefore treated the same
        found = False
        if self.numChildren > 0:
            for i in range((len(self.children)-1), -1, -1):
                if self.children[i].val != None:
                    for j in range(i-1, -1, -1):
                        left = self.children[j].__backInTime(varEnv, funEnv, \
                                                                         locEnv)
                        if left:
                            break
                    subtreeRoot = self.children[i].__findSubtree(varEnv, \
                                                           funEnv, tree, locEnv)
                    found = True
                    break
            if not found:
                return ("maybe", self)
        else:
            return ("maybe", self)

        if subtreeRoot[0] == "yes":
            return subtreeRoot
        if subtreeRoot[0] == "maybe":
            if var or fun or left:
                for i in range(self.numChildren):
                    if self.children[i] == subtreeRoot[1]:
                        self.addChild(Node(None, -1, False, -1), i)
                        tree.updateNoneCount(1)
                if all(self.children[i].val == None \
                                            for i in range(self.numChildren)):
                    tree.updateNoneCount(-self.numChildren)
                    self.numChildren = -1
                return ("yes", subtreeRoot[1])

        return ("maybe", self) # occurs if var is false


    # This is a private helper function to epsteinCheck().  Without it, code
    # like the following:
    # 5 //rangeFrom val
    # true false false nor 9 v/ 3 4 - 1 2 * + rangeFrom + 4 = if check-expect
    # would give an "Incorrect number of arguments" error.
    def __backInTime(self, varEnv, funEnv, locEnv):
        var = locEnv.inEnv(self.val) or varEnv.inEnv(self.val)
        fun = funEnv.inEnv(self.val) and (funEnv.getArrity(self.val) == 0)
        if self.numChildren > 0 and (var or fun):
            return True

        for i in range(self.numChildren):
            if (self.children[i].__backInTime(varEnv, funEnv, locEnv)):
                return True
        return False


    # This function ensures that the number 7 is not at the leaf-level of a tree
    # either as a number or as an element in a list.  The function returns True
    # if the number 7 is present and False otherwise.  It also ensures that
    # there are no top-level functions in a node other than at the root of the
    # tree. 
    def seven_and_checkCheck (self):
        top_level_functions = ["check-error", "check-expect", "define", "done"]
        if not self.root and self.val in top_level_functions:
            global_vars.check_error = False
            global_vars.check_expect = False
            return ("error", "Error: Function is top-level")

        if self.numChildren != -1:
            for i in range(self.numChildren):
                result = self.children[i].seven_and_checkCheck()
                if result[0] == "error":
                    return result
        elif isNum(self.val) and int(float(self.val)) == 7:
            return ("error", "Error: Argument is 7")
        if isList(self.val):
            result = handle_seven(self.val)
            if result == ("error", "Error: Argument is 7"):
                return result
            else:
                self.val = result

        return ("not_error", "all good")


    # Returns the node with the specified ID number
    def get_node(self, desired_id):
        if self.id_num == desired_id:
            return self

        for i in range(self.numChildren):
            if (self.children[i]).get_node(desired_id) != None:
                return (self.children[i]).get_node(desired_id)


    # For testing purposes only
    def printTree(self):
        print self.val, self.numChildren#, self.id_num
        if self.numChildren != -1:
            for i in range(self.numChildren):
                self.children[i].printTree()

