"""
Uses the Compiler class to compile the project into C++.
"""
from compiler import Compiler


def ifsanitize(string:str) -> str:
	"""
	Transforms all ET into &&, etc.
	:param string: The string to sanitize.
	:return: The sanitized string.
	"""
	return string.replace('ET', '&&').replace('OU', '||').replace('NON', '!')


class CppCompiler(Compiler):
	def __init__(self, instruction_names:tuple, var_types:dict, other_instructions:tuple, stdscr, app,
	                use_struct_keyword:bool=True):
		super().__init__(instruction_names, var_types, other_instructions, stdscr, app.translations, app.get_translation, app.tab_char)

		# Creates a list of constants
		self.constants = []
		# Creates a list of function lines
		self.fxtext = []
		# Creates the return code
		self.return_code = "0"

		# Chooses whether we use the struct keyword in the functions' return type and arguments
		self.use_struct_keyword = use_struct_keyword

		# Creates some use variables
		self.app = app


	def prepare_new_compilation(self):
		"""
		Resets everything before compilation.
		"""
		self.constants.clear()
		self.fxtext.clear()
		self.return_code = "0"


	def analyze_const(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Constante : Nom : Paramètres """
		# Adds a constant to the list of constants
		self.constants.append(f"const {' '.join(instruction_params)}")

		# Empties the line
		self.instructions_list[line_number] = ""


	def define_var(self, instruction:list, line_number:int):
		""" Noms, séparés, par, des, virgules : Type(s) """
		# Finding the type of the variable
		var_type = self.var_types[instruction[0]]

		# If the third argument is an equals ('=') sign, we use the shorthand for quick variable assignation
		if len(instruction) > 2 and instruction[2] == "=":
			# We remove the type of the variable from the instructions list
			instruction.pop(0)

			# We call the variable assignation method to generate an assignation string
			self.var_assignation(instruction, line_number)

		# Otherwise, we define all the variables quickly
		else:
			# Getting the names of each variable
			variable_names = ", ".join(instruction[1:])

			# Creating the string
			self.instructions_list[line_number] = var_type + " " + variable_names


	def analyze_for(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Pour i allant de 0 à n avec un pas de 1 """
		self.instructions_stack.append("for")
		# Creates the for loop's body
		self.instructions_list[line_number] = f"for ({instruction_params[0]} = {instruction_params[1]}; " \
		f"{instruction_params[0]} <= {instruction_params[2]}; " \
		f"{instruction_params[0]} += {1 if len(instruction_params) < 4 else instruction_params[3]}) " + "{"


	def analyze_end(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Fin names[elem] """
		# Pops the element at the end of the stack and stores it in a variable
		last_elem = self.instructions_stack.pop()

		# If the last element is a case or default statement, we replace the end with a break statement
		if last_elem in ("case", "default"):
			self.instructions_list[line_number] = self.tab_char + "break;"

		elif last_elem == "fx":
			self.fxtext.append("}")
			self.instructions_list[line_number] = ""

		# Otherwise it's just a curly bracket
		else:
			self.instructions_list[line_number] = "}"


	def analyze_while(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Tant Que condition """
		self.instructions_stack.append("while")
		# Rewrites the line for the while loop
		self.instructions_list[line_number] = f"while ({ifsanitize(' '.join(instruction_params))}) " + "{"


	def analyze_if(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Si condition """
		self.instructions_stack.append("if")
		# Rewrites the line
		self.instructions_list[line_number] = f"if ({ifsanitize(' '.join(instruction_params))}) " + "{"


	def analyze_else(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Sinon """
		# Rewrites the line
		self.instructions_list[line_number] = "} else {"


	def analyze_elif(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Sinon Si condition """
		# Rewrites the line
		self.instructions_list[line_number] = "} " + f"else if ({ifsanitize(' '.join(instruction_params))}) " + " {"


	def analyze_switch(self, instruction_name:str, instruction_params:list, line_number:int):
		""" SELON element """
		self.instructions_stack.append("switch")
		# Rewrites the line
		self.instructions_list[line_number] = f"switch ({' '.join(instruction_params)}) " + "{"


	def analyze_case(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Cas element """
		# If there is no switch in the instruction stack, we error out to the user
		if "switch" not in self.instructions_stack:
			self.error(self.tranlate_method("compilers", "cpp", "errors", "case_outside_switch").format(
				line_number=(line_number + 1)
			))

		# If there is no error, we continue
		else:
			self.instructions_stack.append("case")
			self.instructions_list[line_number] = f"case {' '.join(instruction_params)}:"


	def analyze_default(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Autrement : """
		# If there is no switch in the instruction stack, we error out to the user
		if "switch" not in self.instructions_stack:
			self.error(self.tranlate_method("compilers", "cpp", "errors", "default_outside_switch").format(
				line_number=(line_number + 1)
			))

		# If there is no error, we continue
		else:
			self.instructions_stack.append("default")
			self.instructions_list[line_number] = "default:"


	def analyze_print(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Afficher(elements) """
		# Creates the string to print
		string_to_print = ' '.join(instruction_params)

		# Turns all & into <<
		string_to_print = string_to_print.replace(' & ', ' << ')

		# Rewrites the string
		self.instructions_list[line_number] = f"std::cout << {string_to_print}"


	def analyze_input(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Saisir(elements) """
		self.instructions_list[line_number] = f"std::cin >> {' '.join(instruction_params)}"


	def analyze_precond(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Préconditions : elements """
		self.instructions_list[line_number] = f"// Préconditions : {' '.join(instruction_params)}"


	def analyze_data(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Données : elements """
		self.instructions_list[line_number] = f"// Données : {' '.join(instruction_params)}"


	def analyze_datar(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Donnée/Résultat : elements """
		self.instructions_list[line_number] = f"// Donnée/Résultat : {' '.join(instruction_params)}"


	def analyze_result(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Résultat : elements """
		self.instructions_list[line_number] = f"// Résultat : {' '.join(instruction_params)}"


	def analyze_desc(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Description : elements """
		self.instructions_list[line_number] = f"// Description : {' '.join(instruction_params)}"


	def analyze_return(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Retourner elements """
		# Checks we're not in a procedure
		if "proc" in self.instructions_stack:
			self.error(self.tranlate_method("compilers", "cpp", "errors", "return_in_procedure").format(
				line_number=(line_number + 1)
			))

		# Checks we're inside a function
		elif "fx" not in self.instructions_stack:
			self.error(self.tranlate_method("compilers", "cpp", "errors", "return_outside_function").format(
				line_number=(line_number + 1)
			))

		# Writes the line correctly
		else:
			self.instructions_list[line_number] = f"return {' '.join(instruction_params)}"


	def analyze_vars(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Variables locales : """
		self.instructions_list[line_number] = f"// Variables locales : {' '.join(instruction_params)}"


	def analyze_fx_start(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Début : """
		# Empties the line
		self.instructions_list[line_number] = ""


	def analyze_arr(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Name : tableau [ size ] de type Type """
		try:
			# We construct the array size
			arr_sizes = ""
			for i in range(2, len(instruction_params)):
				arr_sizes += f"[{instruction_params[i]}]"

			# Building the final line
			self.instructions_list[line_number] = f"{self.var_types[instruction_params[0]]} {instruction_params[1]}{arr_sizes}"

		# If the statement does not have all its parameters set
		except IndexError:
			self.error(self.tranlate_method("compilers", "cpp", "errors", "arr_missing_params").format(
				line_number=(line_number + 1)
			))

		# If the variable type doesn't exist
		except KeyError:
			self.error(self.tranlate_method("compilers", "cpp", "errors", "unrecognized_var_type").format(
				line_number=(line_number + 1), type=instruction_params[0]
			))


	def analyze_init(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Analyzes the structure initialization. """

		if len(instruction_params) < 2:  # Error for missing parameters
			self.error(self.tranlate_method("compilers", "cpp", "errors", "struct_missing_args").format(
				line_number=(line_number + 1), param_amount=len(instruction_params)
			))
		elif len(instruction_params) % 2 == 1:  # Error for missing parameters
			self.error(self.tranlate_method("compilers", "cpp", "errors", "struct_args_not_even").format(
				line_number=(line_number + 1), param_amount=len(instruction_params)
			))
		else:
			# Creates the structure initialization
			self.instructions_list[line_number] = f"struct {instruction_params[0]} {instruction_params[1]};"

			# Then for each extra couple of arguments, adds a initialization to this line
			for i in range(2, len(instruction_params), 2):
				self.instructions_list[line_number] += "\n" + self.tab_char * (len(self.instructions_stack) + 1)
				self.instructions_list[line_number] += f"{instruction_params[1]}.{instruction_params[i]} = {instruction_params[i + 1]};"
			self.instructions_list[line_number] = self.instructions_list[line_number][:-1]


	def analyze_fx(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Creates a function definition """
		# Prevents a crash when extra spaces are at the end of the line
		while instruction_params[-1] == "": instruction_params.pop()

		# Function to handle the parameters, whether they are arrays or standard variables
		def handle_params(instruction_params):
			# The list of parameters
			params = []

			# Fetches each parameter (going two by two, because each param goes <type> <name>)
			for i in range(2, len(instruction_params), 2):
				# Adds the parameter to the list of parameters
				params.append("")

				# Try block in case there is an IndexError
				try:
					# If the param is an array, we parse it correctly
					if instruction_params[i].startswith("arr"):
						current_array_param = instruction_params[i].split("_")
						params[-1] += f"{self.var_types[current_array_param[1]]} {current_array_param[2]}[{']['.join(current_array_param[2:])}]"

					# If the param is a structure, we parse it correctly
					elif instruction_params[i].startswith("struct_"):
						params[-1] += "struct " * self.use_struct_keyword + f"{instruction_params[i][7:]} {instruction_params[i + 1]}"

					# If the param is NOT an array
					else:
						# We add it to the params as the type, followed by the name, of whose we remove the
						# first char if it is '&' (no datar mode in algorithmic)
						params[-1] += self.var_types[instruction_params[i]] + " " + instruction_params[i + 1][instruction_params[i][0] == '&':]

				# If an IndexError is encountered, we remove the last param from the params list and continue
				except IndexError:
					params.pop()

			# We merge back the params and return them
			params = ", ".join(params)
			return params

		# Getting the parameters string
		params = handle_params(instruction_params)

		# Branching on whether it is a procedure or a function
		if instruction_params[0] != "void":
			self.instructions_stack.append("fx")

			# If the return type is not a structure
			if not instruction_params[0].startswith("struct_"):
				# We add the return type
				self.instructions_list[line_number] = self.var_types[instruction_params[0]]

			# If the return type is a structure
			else:
				# We add the structure message followed by the return type
				self.instructions_list[line_number] = "struct " * self.use_struct_keyword + instruction_params[0][7:]

			# We write the line as a function
			self.instructions_list[line_number] += f" {instruction_params[1]}({params}) " + "{"

		else:  # Procedure
			self.instructions_stack.append("proc")
			# We write the line as a procedure
			self.instructions_list[line_number] = f"void {instruction_params[1]}({params}) " + "{"

		# If the name of the function/procedure is 'main', we error out
		if instruction_params[1] == "main":
			self.error(f"Error on line {line_number + 1} : Cannot name function/procedure 'main'.")



	def analyze_struct(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Creates a structure definition """
		# Prevents a crash when extra spaces are at the end of the line
		while instruction_params[-1] == "": instruction_params.pop()

		# Function to handle the parameters, whether they are arrays or standard variables
		def handle_params(instruction_params):
			# The list of parameters
			params = []

			# Fetches each parameter (going two by two, because each param goes <type> <name>)
			for i in range(1, len(instruction_params), 2):
				# Adds the parameter to the list of parameters
				params.append("")

				# Try block in case there is an IndexError
				try:
					# If the param is an array, we parse it correctly
					if instruction_params[i].startswith("arr"):
						current_array_param = instruction_params[i].split("_")
						params[-1] += f"{self.var_types[current_array_param[1]]} {current_array_param[2]}[{']['.join(current_array_param[2:])}]"

					# If the param is a structure, we parse it correctly
					elif instruction_params[i].startswith("struct_"):
						params[-1] += "struct " * self.use_struct_keyword + f"{instruction_params[i][7:]} {instruction_params[i + 1]}"

					# If the param is NOT an array
					else:
						# We add it to the params as the type, followed by the name, of whose we remove the
						# first char if it is '&' (no datar mode in algorithmic)
						params[-1] += self.var_types[instruction_params[i]] + " " + instruction_params[i + 1][instruction_params[i][0] == '&':]

				# If an IndexError is encountered, we remove the last param from the params list and continue
				except IndexError:
					params.pop()

			# We return back the parameters
			return params

		# Getting the parameters string
		params = handle_params(instruction_params)

		# Branching on whether it is a procedure or a function
		# We write the line as a structure
		self.constants.append("")
		self.constants[-1] += f"struct {instruction_params[0]}" + " {\n"
		for param in params:
			self.constants[-1] += self.tab_char * (len(self.instructions_stack) + 1) + param + ";\n"
		self.constants[-1] += self.tab_char * len(self.instructions_stack) + "};"
		self.instructions_list[line_number] = ""


	def analyze_CODE_RETOUR(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Changes the return code at the end of the function. """
		self.instructions_list[line_number] = ""
		self.return_code = " ".join(instruction_params)


	def final_trim(self, instruction_name:str, line_number:int):
		""" Adds the line ends, transforms the function names, and adds the correct indentation """
		# Adds the end of line
		self.instructions_list[line_number] = self.instructions_list[line_number].replace("(ENDL)", "\\n")

		# Adds the power, sqrt, and rand functions
		for algo_function, cpp_function in (
				("puissance(", "pow("),
				("racine(", "sqrt("),
				("aleatoire(", "rand("),
				("alea(", "rand(")
		):
			self.instructions_list[line_number] = self.instructions_list[line_number].replace(algo_function, cpp_function)

		# Function to find all the instances of a substring in a string
		def find_all(full_string: str, search: str):
			"""
			Finds all instances of a substring in a string.
			:param full_string: The string to search into.
			:param search: The string of whom to find all the instances.
			:return: A generator containing all the indexes of the substring.
			"""
			start = 0
			while True:
				start = full_string.find(search, start)
				if start == -1: return
				yield start
				start += len(search)

		# Adds the len function
		if "len(" in self.instructions_list[line_number]:
			for index in find_all(self.instructions_list[line_number], "len("):
				var_name = self.instructions_list[line_number][
		           index + 4 :
		           index + 4 + self.instructions_list[line_number][index + 4:].find(")")
		        ]
				self.instructions_list[line_number] = self.instructions_list[line_number].replace(
					f"len({var_name})",
					f"(sizeof({var_name})/sizeof({var_name}[0]))",
					1
				)


		# Adds the correct tabbing (amount of tabs is equal to amount of instructions in the instructions stack,
		# minus one if the current instruction is in the instruction names)
		tab_amount = len(self.instructions_stack)
		if instruction_name in (*self.instruction_names, "else", "elif"):
			tab_amount -= 1

		# Adds a semicolon if necessary
		if not (
				self.instructions_list[line_number].startswith("//") or
				self.instructions_list[line_number].endswith("}") or
				instruction_name in (*self.instruction_names, "else", "elif")
		):
			self.instructions_list[line_number] += ";"

		# Writes the line
		self.instructions_list[line_number] = self.app.tab_char * tab_amount + self.instructions_list[line_number]

		# Removes the std:: if we use the std namespace
		if self.app.using_namespace_std:
			self.instructions_list[line_number] = self.instructions_list[line_number].replace("std::", "")

		# Adds it to fxtext if necessary
		if len(self.instructions_stack) != 0 and (
			"fx" in self.instructions_stack or
			(instruction_name == "end" and self.instructions_stack[-1] == "fx")
		):
			self.fxtext.append(self.instructions_list[line_number])
			if instruction_name == "end":
				self.fxtext[-1] += "\n"
			self.instructions_list[line_number] = ""


	def final_touches(self):
		""" Concatenates everything into one string """
		# Initializes the final compiled code
		final_compiled_code = "#include <iostream>\n"

		# We import math.h if we use power or sqrt in the code
		if "puissance(" in self.app.current_text or "racine(" in self.app.current_text:
			final_compiled_code += "#include <math.h>\n"

		# If we use random in the code, we import stdlib.h and time.h
		if 'aleatoire(' in self.app.current_text or 'alea(' in self.app.current_text:
			final_compiled_code += "#include <stdlib.h>\n#include <time.h>\n"

		# If we use len in the code, we import stdlib.h
		if 'len(' in self.app.current_text:
			final_compiled_code += "#include <stdlib.h>\n"

		# If we use the std namespace, we put it there
		if self.app.using_namespace_std:
			final_compiled_code += "using namespace std;\n"

		# We add a simple blank line
		final_compiled_code += "\n"

		# We add the constants text to the final_compiled_code
		final_compiled_code += "\n".join(self.constants)
		# We also add another newline if there are constants declared
		if len(self.constants) != 0:
			final_compiled_code += "\n\n"

		# We then add the function's text
		final_compiled_code += "\n".join(text for text in self.fxtext if text.replace(self.tab_char, "") != ";")

		# We start to add the main function
		final_compiled_code += "\n\nint main() {\n"

		# We add the srand(time(NULL)) statement if we are using random
		if "aleatoire(" in self.app.current_text or "alea(" in self.app.current_text:
			final_compiled_code += self.tab_char + "srand(time(NULL));\n"

		# We then add each instruction along with a tab
		for instruction in self.instructions_list:
			if instruction.replace(self.tab_char, "") != ";" and instruction != "":
				final_compiled_code += self.tab_char + instruction + "\n"

		# We complete the compilation
		final_compiled_code += self.tab_char + f"return {self.return_code};\n" + "}"

		return final_compiled_code
