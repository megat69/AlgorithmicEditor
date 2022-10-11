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
			Keys : ('for', 'if', 'while', 'switch', 'arr', 'case', 'default', 'fx', 'proc', 'const')
		:param var_types: Dictionaries containing the translation of the variable names
			Keys : ('int', 'float', 'string', 'bool', 'char')
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
			if instruction_name in self.instruction_names.keys():
				# Turns the fx_name into a callback function : The analyze_%name% method of this class.
				try: fx_name = getattr(self, f"analyze_{instruction_name}")
				except Exception: raise NotImplementedError(f"Function {instruction_name} not implemented")
				# Calls the callback function and gives it the instruction's name and params, along with the line number
				fx_name(instruction_name, instruction_params, i)

			elif instruction_name in self.var_types:
				pass


	def analyze_const(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_for(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_end(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_while(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_if(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_else(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_elif(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_switch(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_case(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_default(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_print(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_input(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_fx(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_precond(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_data(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_datar(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_result(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_return(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_desc(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass


	def analyze_fx_start(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a constant.
		"""
		pass
