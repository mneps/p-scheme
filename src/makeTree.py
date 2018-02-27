#
# Matthew Epstein
# makeTree.py
# This function is called by evaluate in run.py and by userFun in
# primitives.py.  It gets its own file because it can't go in run.py
# because then primitives.py wouldn't have access to it, but it doesn't really
# make sense for the function to go in primitives.py either.  The function
# takes in an expTree that has been initialized with only an expression and
# from the expression creates a tree of nodes.
#


from node import *

def makeTree(tree, funEnv, id_num, list_fun):
    val = tree.update_string()
    isRoot = tree.checkIfRoot()
    LIST_FUNCTIONS = ["fold", "map", "filter", "all", "exists"]

    if funEnv.inEnv(val) and not list_fun:
        if val in LIST_FUNCTIONS:
            list_fun = True
        node = Node(val, funEnv.getArrity(val), isRoot, tree.update_num_nodes())
        tree.updateNoneCount(funEnv.getArrity(val))
        for i in range(node.getNumChildren()):
            if i != 0 and list_fun:
                list_fun = False
            tree.updateNoneCount(-1)
            node.addChild(makeTree(tree, funEnv, tree.get_num_nodes(), \
                                                                  list_fun), i)
        return node
    else:
        if val == None:
            tree.updateNoneCount(1)
        return Node(val, -1, isRoot, tree.update_num_nodes())
