#
# Matthew Epstein
# intervals.py
# This file contains the header functions for the four pattern matching classes,
# found in pm_nums.py, pm_bools.py, pm_strings.py, and pm_lists.py.  The classes
# are polymorphic and contain the same three public methods.  When a pattern
# matching class is first declared, the client must specify the type of data
# they will be dealing with.  After that point though, the client does not have
# to worry about the difference between the four types: the different
# implementations happen behind the scenes.
#


from pm_bools import *
from pm_lists import *
from pm_nums import *
from pm_strings import *


class PatternMatching:

	# Initializes the class by creating an instance of the correct type of
	# pattern matching class.
	def __init__(self, pm_type):
		if pm_type == "num":
			self.pm_class = PM_Nums()
		elif pm_type == "bool":
			self.pm_class = PM_Bools()
		elif pm_type == "str":
			self.pm_class = PM_Strings()
		elif pm_type == "list":
			self.pm_class = PM_Lists()


	# This function adds a pattern.  It will return an error message if
	# something goes wrong.
	def addPattern(self, pattern):
		return (self.pm_class).addPattern(pattern)


	# Returns True if pattern matching is complete and returns False otherwise.
	def isComplete(self):
		return (self.pm_class).isComplete()


	# Returns True if arg is contained in the i-th pattern and False otherwise.
	def matches(self, arg, i):
		return (self.pm_class).matches(arg, i)



