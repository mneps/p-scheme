#
# Matthew Epstein
# expTree.py
# This file holds the ExpressionTree class, which has the very specific purpose
# of taking in a line of code and turning that line into an abstract syntax
# tree.  The tree is comprised of a collection of nodes (see node.py for the
# Node class), where each function, variable, and literal is represented by a
# single node.  A function with arrity n expects to have n children.  In order
# to differentiate between a function with arrity 0 and variables and literals,
# the former is said to have 0 children while the latter is said to have -1
# children.  In addition to the tree itself, the class holds the expression
# as a string and  counters for the number of nodes in the tree (used to
# determine each node's ID number while the tree is being built) and the number
# of available spots in the tree (used for the tree rebalancing algorithm
# discussed in node.py).
#



class ExpressionTree:
    # Initializes the class with starting values.
    def __init__(self, string):
        self.tree = None
        self.origString = string
        self.string = string
        self.noneCount = 0
        self.num_nodes = 0

    # Returns the first value of the expression (whether it be function,
    # variable or literal) and updates the string so that the first value
    # is no longer in the expression
    def update_string(self):
        try:
            first = self.string[0]
            self.string = self.string[1:]
        except:
            first = None
        return first

    # The six remaining functions below are all fairly self-explanatory.
    def checkIfRoot(self):
        if len(self.origString) == len(self.string)+1:
            return True
        return False

    def updateNoneCount(self, new_children):
        self.noneCount = self.noneCount + new_children

    def getNoneCount(self):
        return self.noneCount

    def get_string_length(self):
        return len(self.string)

    def update_num_nodes(self):
        self.num_nodes += 1
        return self.num_nodes

    def get_num_nodes(self):
        return self.num_nodes




