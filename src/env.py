#
# Matthew Epstein
# env.py
# This file holds the Environment class for variables and functions.  Each
# environment instance is a dictionary (hash table) that can filled with
# variable names and values or functions with their defintions.  Functions are
# provided for the insertion and retrieval of values to and from the
# environment, respectively.
#


import time
import global_vars

class Environment:

    # Initializes the environment to an empty dictionary
    def __init__(self):
        self.env = dict()
        self.PMs = dict() # only necessary for the function environment

    # Returns True if a variable is in the environment and False otherwise
    def inEnv(self, var):
        try:
            tmp = self.env[var]
            return True
        except:
            return False

    # Returns True if a variable of the specified type is in the environment and
    # False otherwise
    def inEnvandType(self, var, varType):
        try:
            existing_var = self.env[var]
            for in_existing_var in existing_var:
                if in_existing_var[1] == varType:
                    return True
            return False
        except:
            return False

    # Binds a value to the "it" variable.  it-binding gets its own function
    # because the new value should always overwrite the previous one and if the
    # two previous values are of differing types, this would not occur with the
    # normal addBind() function.
    def addBindit(self, var, val):
        if self.__getType(val) == "variable":
            self.env[var] = self.env[val]
        else:
            self.env[var] = [(val, self.__getType(val))]


    # Adds a new variable (or function) to the environment.  There are three
    # possible cases for adding a variable to the environment, each of which is
    # handled separately.  If the new variable is completely new and has not
    # been previously declared, a new key is added to the dictionary and the
    # appropriate value is attached (Option A).  The second case is when
    # the new variable is already in the environment but the variable has not
    # yet been declared with the new value's type.  In this case, a new value
    # is appended to the variable's associated values (Option B).  The third
    # and final case is if the variable already is in the environment and the
    # variable has already been declared with the new value's type.  In this
    # case, the new value overwrites the previous value that was the same type
    # (Option C).
    def addBind(self, var, val, constraints=None):
        if self.__getType(val) == "variable":
            self.__addBindVar(var, val, constraints)
        else:
            if self.inEnv(var):
                existing_val = self.env[var]
                counter = 0
                for existing_var in self.env[var]:
                    if existing_var[1] == self.__getType(val):
                        # Option C
                        if self.__getType(val) == "function" and var not in global_vars.PRIMITIVES:
                            if val[1][0][0] == "|":
                                (self.env[var]).append((val, self.__getType(val)))
                        else:
                            self.env[var][counter] = (val, self.__getType(val))
                        break
                    counter += 1
                if counter == len(self.env[var]):
                    # Option B
                    (self.env[var]).append((val, self.__getType(val))) 
            else:
                # Option A
                self.env[var] = [(val, self.__getType(val))]


    # A private helper function to addBind.  This function is called if a
    # variable is assigned to the value(s) of another variable, instead of to a
    # literal value.
    def __addBindVar(self, var, val, constraints):
        cont = False
        if self.inEnv(var):
            for i in range(len(self.env[val])):
                if self.env[val][i][1] not in constraints[0]:
                    continue
                for j in range(len(self.env[var])):
                    if self.env[var][j][1] == self.env[val][i][1]:
                        self.env[var][j] = self.env[val][i]
                        cont = True
                        break
                if cont:
                    cont = False
                    continue
                self.env[var].append(self.env[val][i])
        else:
            newVar = []
            for i in range(len(self.env[val])):
                if self.env[val][i][1] in constraints[0]:
                    newVar.append((self.env[val][i][0], self.env[val][i][1]))
            self.env[var] = newVar


    # Returns the value of the variable that has type varType.
    def getVal(self, var, varType):
        for existing_var in self.env[var]:
            if existing_var[1] == varType:
                return existing_var[0]

    # Returns the type a variable was first declared as.  Necessary for when
    # two variables are of the same, multiple types.  The type chosen to use is
    # whatever type was declared first for the first variable in the expression.
    def getOrigType(self, var):
        if self.inEnv(var):
            return self.env[var][0][1]

    # Returns the types associated with the values of a variable.
    def getVarTypes(self, var):
        if self.inEnv(var):
            typeList = []
            for i in range(len(self.env[var])):
                typeList.append(self.env[var][i][1])
            return typeList
        return []

    # Clears an environment.
    def empty(self):
        self.env = dict()

    # Gets the arrity of a function.  Returns None if caled on a variable.
    def getArrity(self, var):
        try:
            if self.inEnv(var):
                return self.env[var][0][0][2]
        except:
            return None

    # Returns the number of functions a pattern-matching function contains
    def getNumFuncs(self, var):
        return len(self.env[var])

    # Returns all information pertaining to a function
    def getFunc(self, var):
        return self.env[var]

    # Adds a function-pattern matching entry to the PMs dictionary
    def addPM(self, name, pm):
        self.PMs[name] = pm

    # Returns the PM_Nums class associated with the given functions
    def getPM(self, name):
        return self.PMs[name]

    # Returns the type of a variable.  This is a private function, only intended
    # to be used by the bind functions.
    def __getType(self, arg):
        if arg == "true" or arg == "false" or arg == "maybe" \
                          or arg == True or arg == False:
            return "bool"
        if arg == "Nothing":
            return "nonetype"
        argStr = str(arg)
        if argStr == "" or (argStr[0] == "\"" and argStr[-1] == "\""):
            return "str"
        if argStr[0] == "[" and argStr[-1] == "]":
            return "list"
        try:
            if isinstance(float(arg), float):
                return "num"
        except:
            if self.inEnv(arg):
                return "variable"
            else:
                return "function"


    def printTest(self, var):
        print self.env[var], len(self.env[var])




