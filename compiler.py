"""
Compiler TODO :

Single class, two instances : Shared attributes
Possesses a main 'compile' function, which will call an 'analyze_line' method,
which will dispatch to the correct function based on the first argument in the line,
or if there is an equal sign
"""  # TODO : Interpreter


class Compiler:
	def __init__(self, instruction_names:dict, var_types:dict):
		"""
		Initializes a new compiler.
		:param instruction_names: Dictionaries containing the translation of the instructions
		:param var_types: Dictionaries containing the translation of the variable names
		"""
		# Dictionaries containing the translation of the variable names and the translation of the instructions
		self.instruction_names = instruction_names
		self.var_types = var_types

		# Compilation-related variables
		self.instructions_list = []  # The list of instructions to be compiled
		self.instructions_stack = []  # The stack of the instructions (indicates the number of tabs and the last instruction block's name)


	def compile(self, instructions_list:list):
		"""
		Dispatches the compilation to the correct functions based on the instruction params.
		:param instructions_list: The list of instructions, a list of strings.
		"""
		# Keeps as an attribute the list of instructions
		self.instructions_list = instructions_list

		# Interprets each instruction one by one
		for i, line in enumerate(self.instructions_list):
			line = line.split(' ')
			instruction_name = line[0]
			instruction_params = line[1:]

			# Based on the instruction's name, dispatches to the correct functions
			match instruction_name:
				case "":
					pass

				case _:  # Then checks for variables and stuff
					if instruction_name in self.var_types:
						pass
