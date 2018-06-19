#
# Matthew Epstein
# intervals.py
# This file contains the header functions for the two interval classes, found in
# ints.py and reals.py.  The classes are polymorphic, and contain the same
# public methods.  When an interval class is first declared, the user must
# specify if they shall be dealing with all real numbers or exclusively with
# integers.  After that point though, the user does not have to worry about
# the difference between the two types of sets: all that implementation happens
# behind the scenes.  The big difference between the two is that when dealing
# with all real numbers it is necessary to specify if the bounds are inclusive
# or exclusive, while with integers it can be assumed that both bounds are
# always inclusive.  This class is used for pattern matching on numbers and
# strings.  (More information is contained in pm_nums.py and pm_strings.py).
#


from ints import *
from reals import *


REALS = 0
INTS = 1

class Intervals:

	# Initializes the class by creating an instance of the Reals class or the
	# Ints class, depending on the user's preference.
	def __init__(self, set_type):
		if set_type == REALS:
			self.interval = Reals()
		elif set_type == INTS:
			self.interval = Ints()


	# This function takes in a lower bound and an upper bound and performs a
	# union operation with that interval and the set that already exists.  The
	# function also takes in optional arguments to specify if lower and upper
	# bounds are inclusive or exclusive.  By default, the bounds are assumed to
	# be inclusive (and probably always should be inclusive if the set is
	# integers).  Returns True if the operation was successful and False
	# otherwise.
	def union_interval(self, lbound, ubound, lbound_inc=True, ubound_inc=True):
		return (self.interval).union_interval(lbound, ubound, lbound_inc, \
																	ubound_inc)

	# This function takes in a single number and performs a union operation with
	# that number and the existing set.  Returns True if the operation was
	# successful and False otherwise.
	def union_number(self, num):
		return (self.interval).union_number(num)


	# Returns True if every real number in the (-inf, inf) interval is contained
	# in the class's interval and the set is reals.  If the set is ints, then 
	# this function returns True if every integer in the (-inf, inf) interval is
	# contained in the class's interval.  Otherwise, it will return False.
	def isComplete(self):
		return (self.interval).isComplete()

	# Returns True if the number passed in is contained in the class's interval.
	# Returns False otherwise.
	def inInterval(self, num):
		return (self.interval).inInterval(num)






