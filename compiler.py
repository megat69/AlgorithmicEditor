from typing import Union
# TODO : Interpreter


class Compiler:
	def __init__(self, instruction_names: Union[dict, tuple], var_types:dict, other_instructions:tuple, stdscr, translations: dict, translate_method, tab_char:str= "\t"):
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
		self.other_instructions = other_instructions

		# Compilation-related variables
		self.instructions_list = []  # The list of instructions to be compiled
		self.instructions_stack = []  # The stack of the instructions (indicates the number of tabs and the last instruction block's name)

		# Use variables
		self.stdscr = stdscr
		self.errored = False
		self.tab_char = tab_char
		self.translations = translations
		self.tranlate_method = translate_method


	def compile(self, instructions_list:list):
		"""
		Dispatches the compilation to the correct functions based on the instruction params.
		:param instructions_list: The list of instructions, a list of strings.
		"""
		# Calls the pre-compilation cleaning method
		self.prepare_new_compilation()

		# Keeps as an attribute the list of instructions
		self.instructions_list = instructions_list

		# Creates the instruction names
		instruction_names = self.instruction_names
		if isinstance(self.instruction_names, dict):
			instruction_names = instruction_names.keys()

		# Interprets each instruction one by one
		for i, line in enumerate(self.instructions_list):
			# Checks if no error occurred
			if self.errored: break

			line = line.split(' ')
			instruction_name = line[0]
			instruction_params = line[1:]

			# Based on the instruction's name, dispatches to the correct functions
			if instruction_name in (*instruction_names, *self.other_instructions):
				# Turns the fx_name into a callback function : The analyze_%name% method of this class.
				try: fx_name = getattr(self, f"analyze_{instruction_name}")
				except Exception: raise NotImplementedError(f"Function {instruction_name} not implemented")
				# Calls the callback function and gives it the instruction's name and params, along with the line number
				fx_name(instruction_name, instruction_params, i)

			# Defines a variable if wanted
			elif instruction_name in self.var_types:
				self.define_var(line, i)

			# Reassigns a variable if wanted
			elif len(instruction_params) != 0:
				if instruction_params[0].endswith("="):
					self.var_assignation(line, i)

			# Makes the final trimming to the line
			self.final_trim(instruction_name, i)

		# Also checks if an error occurred
		if self.errored:
			return None

		# Makes the final adjustments to each line and puts everything together
		final_compiled_code = self.final_touches()

		# Finally returns the compiled code
		return final_compiled_code


	def prepare_new_compilation(self):
		"""
		Gets called before compilation so the compiler can clean itself.
		"""
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


	def analyze_vars(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes local variables.
		"""
		pass


	def analyze_arr(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes local variables.
		"""
		pass


	def analyze_CODE_RETOUR(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the return code.
		"""
		pass


	def analyze_struct(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a structure.
		"""
		pass


	def analyze_init(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes a structure initialization.
		"""
		pass


	def final_trim(self, instruction_name:str, line_number:int):
		"""
		Makes the final trim to the line.
		"""
		pass


	def final_touches(self):
		"""
		Makes the final touches to the line.
		"""
		pass


	def define_var(self, instruction:list, line_number:int):
		"""
		Is called when a variable is defined.
		"""
		pass


	def var_assignation(self, instruction:list, line_number:int):
		"""
		Is called when a variable is defined.
		"""
		pass


	def error(self, message:str="Error."):
		"""
		Errors out to the user.
		"""
		self.stdscr.clear()
		self.stdscr.addstr(0, 0, message)
		self.stdscr.getch()
		self.errored = True
