#
# Matthew Epstein
# This file contains functions for the Reals class, which is used by pm_nums.py.
# The class can be thought of as a representation of all the real numbers on the
# number line.  Intervals can be added to the number line but cannot be removed.
#

inf = float("inf")
ninf = float("-inf")


class Reals:

	# Initialize the class with an empty list that will hold information
	# regarding the numbers held in the interval.  The list will ultimately take
	# the form of
	# [(lower_bound1, upper_bound1, lower_bound1_inc, upper_bound1_inc),
	#  (lower_bound2, upper_bound2, lower_bound2_inc, upper_bound2_inc), ...]
	# where the first two elements of the list are numbers such
	# upper_bound1 <= lower_bound2, upper_bound2 <= lower_bound3, etc. and the
	# third and fourth elements of the list are boolean values that reflect
	# if the corresponding bound is inclusive (True) or exclusive (False).
	# As an example, the following set:
	# 	[-5,0) U (3,4) U [3.6, 8.2]
	# would be represented as such:
	# 	[(-5, 0, True, False), (3, 4, False, False),  3.6, 8.2, True, True)]
	def __init__(self):
		self.interval = []


	# In addition to an instance of the Reals class, this function takes in a
	# lower bound and upper bound (both integers) as well as information
	# regarding which of those bounds are inclusive and which are exlcusive
	# (both booleans).  The function uses the __union() function as a helper
	# function.  This function should only be used when the lower bound and
	# upper bound are not equal to each other.  When this is not this case
	# (i.e. the interval to be added is a single number) the union_number()
	# function should be used.  Returns True if the bound could be successfully
	# inserted and False otherwise.
	def union_interval(self, lbound, ubound, lbound_ie, ubound_ie):
		for i in [lbound, ubound]:
			if type(i) not in [int, float, long]:
				return False

		if lbound >= ubound:
			return False

		for i in [lbound_ie, ubound_ie]:
			if not isinstance(i, bool):
				return False

		return self.__union(lbound, ubound, lbound_ie, ubound_ie)


	# Adds a single number to the interval.  Uses the __union() function as a
	# helper function.  Returns True if the bound was successfully inserted and
	# False otherwise.
	def union_number(self, num):
		if type(num) not in [int, float, long]:
			return False

		return self.__union(num, num, True, True)


	# Inserts the new interval segment in the proper place in the self.interval
	# list (so that the order of the list is maintained).  Uses the
	# __validate_inteval() function as a helper function.  Returns True if the
	# interval could be inserted successfully and False otherwise.
	def __union(self, lbound, ubound, lbound_ie, ubound_ie):
		orig_interval = self.interval[:] # does a deep copy

		if self.interval == []:
			self.interval = [(lbound, ubound, lbound_ie, ubound_ie)]
		else:
			added = False
			elem = (lbound, ubound, lbound_ie, ubound_ie)
			for i in range(len(self.interval)):
				# lower bound is less than the current lower bound
				if lbound < self.interval[i][0]:
					continue
				# lower bound is greater than the next lower bound
				if i != len(self.interval)-1 and lbound > self.interval[i+1][0]:
					continue
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
	# inteval is valid and False otherwise.  This function also ensures that an
	# interval like this:
	#	[a,b) U [b,b] U (b, c]
	# is in the correct format.  If the [b,b] interval is not in the middle, the
	# interval will not validate.
	def __validate_interval(self):
		for i in range(len(self.interval)):
			if self.interval[i][0] == self.interval[i][1]:
				if i >= 2 and self.interval[i-2][1] == self.interval[i][0] \
						  and self.interval[i-1][0] == self.interval[i][0]:
					temp = self.interval[i]
					self.interval[i] = self.interval[i-1]
					self.interval[i-1] = temp
				elif (len(self.interval) - i) >= 3 \
							and self.interval[i+1][1] == self.interval[i][0] \
							and	self.interval[i-2][0] == self.interval[i][0]:
					temp = self.interval[i]
					self.interval[i] = self.interval[i+1]
					self.interval[i+1] = temp


		for i in range(1,len(self.interval)):
			if self.interval[i][0] < self.interval[i-1][1]:
				return False
			if self.interval[i][0] == self.interval[i-1][1] and \
								self.interval[i][2] and self.interval[i-1][3]:
				return False

		return True


	# Returns True if every real number is contained within the interval and
	# returns False otherwise.  This function is used to determine if pattern
	# matching is exhaustive.
	def isComplete(self):
		if self.interval[0][0] != ninf:
			return False
		if self.interval[-1][1] != inf:
			return False

		for i in range(1, len(self.interval)):
			if self.interval[i][0] != self.interval[i-1][1]:
				return False
			if not (self.interval[i][2] ^ self.interval[i-1][3]):
				return False

		return True


	# Returns True if the specified number (num) is contained within the
	# interval and returns False otherwise.
	def inInterval(self, num):
		if type(num) not in [int, float, long]:
			return False

		for i in range(len(self.interval)):
			if num > self.interval[i][0] and num < self.interval[i][1]:
				return True
			if num == self.interval[i][0] and self.interval[i][2]:
				return True
			if num == self.interval[i][1] and self.interval[i][3]:
				return True

		return False





