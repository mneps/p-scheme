#
# Matthew Epstein
# This file contains functions for the Ints class, which is used by
# pm_strings.py.  The class can be thought of as a representation of all the
# integers on the number line.  Intervals can be added to the number line but
# cannot be removed.
#

inf = float("inf")
ninf = float("-inf")


class Ints:

	# Initialize the class with an empty list that will hold information
	# regarding the numbers held in the interval.  The list will ultimately take
	# the form of
	# [(lower_bound1, upper_bound1), (lower_bound2, upper_bound2,), ...]
	# where upper_bound1 < lower_bound2, upper_bound2 < lower_bound3, etc.
	def __init__(self):
		self.interval = []


	# In addition to an instance of the Ints class, this function takes in a
	# lower bound and upper bound (both integers) as well as information
	# regarding which of those bounds are inclusive and which are exlcusive
	# (both booleans).  The function uses the __union() function as a helper
	# function.  This function should only be used when the lower bound and
	# upper bound are not equal to each other.  When this is not this case
	# (i.e. the interval to be added is a single number) the union_number()
	# function should be used.  Returns True if the bound could be successfully
	# inserted and False otherwise.
	def union_interval(self, lbound, ubound, lbound_inc, ubound_inc):
		for i in [lbound, ubound]:
			if type(i) not in [int, long] and i not in [ninf, inf]:
				return False

		if lbound >= ubound:
			return False

		if not lbound_inc and lbound != ninf:
			lbound + 1
		if not ubound and ubound != ninf:
			ubound_inc - 1

		return self.__union(lbound, ubound)


	# Adds a single number to the interval.  Uses the __union() function as a
	# helper function.  Returns True if the bound was successfully inserted and
	# False otherwise.
	def union_number(self, num):
		if type(num) not in [int, long]:
			return False

		return self.__union(num, num)


	# Inserts the new interval segment in the proper place in the self.interval
	# list (so that the order of the list is maintained).  Uses the
	# __validate_inteval() function as a helper function.  Returns True if the
	# interval could be inserted successfully and False otherwise.
	def __union(self, lbound, ubound):
		orig_interval = self.interval[:] # does a deep copy

		if self.interval == []:
			self.interval = [(lbound, ubound)]
		else:
			added = False
			elem = (lbound, ubound)
			for i in range(len(self.interval)):
				# lower bound is less than the current lower bound
				if lbound < self.interval[i][0]:
					continue
				# lower bound is greater than the next lower bound
				if i != len(self.interval)-1 and lbound > self.interval[i+1][0]:
					continue
				# lower bound is less than the next lower bound
				else:
					(self.interval).insert(i+1, elem)
					added = True
					break

			if not added:
				if lbound < self.interval[i][0]:
					(self.interval).insert(0, elem)

		if not self.__validate_interval():
			self.interval = orig_interval
			return False

		return True


	# Ensures that no number appears in the interval twice.  Returns True if the
	# inteval is valid and False otherwise.
	def __validate_interval(self):
		for i in range(1,len(self.interval)):
			if self.interval[i][0] <= self.interval[i-1][1]:
				return False

		return True


	# Returns True if every integer is contained within the interval and returns
	# False otherwise.  This function is used to determine if pattern matching
	# is exhaustive.
	def isComplete(self):
		if self.interval[0][0] != ninf:
			return False
		if self.interval[-1][1] != inf:
			return False

		for i in range(1, len(self.interval)):
			if (self.interval[i][0] - self.interval[i-1][1]) != 1:
				return False

		return True


	# Returns True if the specified number (num) is contained within the
	# interval and returns False otherwise.
	def inInterval(self, num):
		if type(num) != int and type(num) != long:
			return False

		for i in range(len(self.interval)):
			if num > self.interval[i][0] and num < self.interval[i][1]:
				return True
			if num == self.interval[i][0]:
				return True
			if num == self.interval[i][1]:
				return True

		return False




