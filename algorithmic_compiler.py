"""
Uses the Compiler class to compile the project into Algorithmic code.
"""
from compiler import Compiler


class AlgorithmicCompiler(Compiler):
	def __init__(self, instruction_names:dict, var_types:dict, other_instructions:list, stdscr, translations, translate_method, tab_char:str="\t"):
		super().__init__(instruction_names, var_types, other_instructions, stdscr, translations, translate_method, tab_char)


	def analyze_const(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Constante : Nom : Paramètres """
		self.instructions_list[line_number] = f"{self.instruction_names['const']} : {self.var_types[instruction_params[0]]} : {' '.join(instruction_params[1:])}"


	def define_var(self, instruction:list, line_number:int):
		""" Noms, séparés, par, des, virgules : Type(s) """
		# Finding the type of the variable
		var_type = self.var_types[instruction[0]]

		# If the third argument is an equals ('=') sign, we use the shorthand for quick variable assignation
		if len(instruction) > 2 and instruction[2] == "=":
			# We save the name of the variable
			variable_name = instruction[1]

			# We remove the type of the variable from the instructions list
			instruction.pop(0)

			# We call the variable assignation method to generate an assignation string
			self.var_assignation(instruction, line_number)

			# We add to the current line the definition of the variable
			self.instructions_list[line_number] = f"{variable_name} : {var_type}\n" + \
					self.tab_char * (len(self.instructions_stack) + 1) + self.instructions_list[line_number]

		# Otherwise, we define all the variables quickly
		else:
			# Getting the names of each variable
			variable_names = ", ".join(instruction[1:])

			# Creating the string
			self.instructions_list[line_number] = f"{variable_names} : {var_type}"

			# Adds an 's' to the var type if multiple vars are declared
			if len(instruction[1:]) != 1 and instruction[0] != "string":
				self.instructions_list[line_number] += "s"


	def analyze_for(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Pour i allant de 0 à n avec un pas de 1 """
		self.instructions_stack.append("for")
		# Description of the for loop
		self.instructions_list[line_number] = f"Pour {instruction_params[0]} allant de {instruction_params[1]} à " \
		f"{instruction_params[2]} avec un pas de " \
		f"{1 if len(instruction_params) < 4 else instruction_params[3]}"


	def analyze_end(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Fin names[elem] """
		# Pops the element at the end of the stack and stores it in a variable
		last_elem = self.instructions_stack.pop()
		# If the last element is not "vars" (in the docstring), then we add "Fin names[elem]" to the line
		if last_elem != "vars":
			self.instructions_list[line_number] = f"Fin {self.instruction_names[last_elem]}"


	def analyze_while(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Tant Que condition """
		self.instructions_stack.append("while")
		# Rewrites the line
		self.instructions_list[line_number] = f"Tant Que {' '.join(instruction_params)}"


	def analyze_if(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Si condition """
		self.instructions_stack.append("if")
		# Rewrites the line
		self.instructions_list[line_number] = f"Si {' '.join(instruction_params)}"


	def analyze_else(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Sinon """
		# Rewrites the line
		self.instructions_list[line_number] = "Sinon"


	def analyze_elif(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Sinon Si condition """
		# Rewrites the line
		self.instructions_list[line_number] = f"Sinon Si {' '.join(instruction_params)}"


	def analyze_switch(self, instruction_name:str, instruction_params:list, line_number:int):
		""" SELON element """
		self.instructions_stack.append("switch")
		self.instructions_list[line_number] = f"SELON {' '.join(instruction_params)}"


	def analyze_case(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Cas element """
		# If there is no switch in the instruction stack, we error out to the user
		if "switch" not in self.instructions_stack:
			self.error(self.tranlate_method("compiler", "cpp", "errors", "case_outside_switch").format(
				line_number=line_number + 1
			))

		# If there is no error, we continue
		else:
			self.instructions_stack.append("case")
			self.instructions_list[line_number] = f"Cas {' '.join(instruction_params)}"


	def analyze_default(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Autrement : """
		# If there is no switch in the instruction stack, we error out to the user
		if "switch" not in self.instructions_stack:
			self.error(self.tranlate_method("compiler", "cpp", "errors", "default_outside_switch").format(
				line_number=line_number + 1
			))

		# If there is no error, we continue
		else:
			self.instructions_stack.append("default")
			self.instructions_list[line_number] = f"Autrement : {' '.join(instruction_params)}"


	def analyze_print(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Afficher(elements) """
		self.instructions_list[line_number] = f"Afficher({' '.join(instruction_params)})"


	def analyze_input(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Saisir(elements) """
		self.instructions_list[line_number] = f"Saisir({' '.join(instruction_params)})"


	def analyze_precond(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Préconditions : elements """
		self.instructions_list[line_number] = f"Préconditions : {' '.join(instruction_params)}"


	def analyze_data(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Données : elements """
		self.instructions_list[line_number] = f"Données : {' '.join(instruction_params)}"


	def analyze_datar(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Donnée/Résultat : elements """
		self.instructions_list[line_number] = f"Donnée/Résultat : {' '.join(instruction_params)}"


	def analyze_result(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Résultat : elements """
		self.instructions_list[line_number] = f"Résultat : {' '.join(instruction_params)}"


	def analyze_desc(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Description : elements """
		self.instructions_list[line_number] = f"Description : {' '.join(instruction_params)}"


	def analyze_return(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Retourner elements """
		# Checks we're not in a procedure
		if "proc" in self.instructions_stack:
			self.error(self.tranlate_method("compiler", "cpp", "errors", "return_in_procedure").format(
				line_number=line_number + 1
			))

		# Checks we're inside a function
		elif "fx" not in self.instructions_stack:
			self.error(self.tranlate_method("compiler", "cpp", "errors", "return_outside_function").format(
				line_number=line_number + 1
			))

		# Writes the line correctly
		else:
			self.instructions_list[line_number] = f"Retourner {' '.join(instruction_params)}"


	def analyze_fx_start(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Début : """
		# Removes 'vars' from the instruction stack if it is there
		if self.instructions_stack[-1] == "vars":
			self.instructions_stack.pop()

		# Rewrites the line
		self.instructions_list[line_number] = f"Début : {' '.join(instruction_params)}"


	def analyze_vars(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Variables locales : """
		self.instructions_list[line_number] = f"Variables locales : {' '.join(instruction_params)}"
		self.instructions_stack.append("vars")


	def analyze_arr(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Name : tableau [ size ] de type Type """
		try:
			# We construct the array size
			arr_sizes = ""
			for i in range(2, len(instruction_params)):
				arr_sizes += f"[ {instruction_params[i]} ]"

			# Getting the array type
			arr_type = self.var_types[instruction_params[0]].lower()

			# Building the final line
			self.instructions_list[line_number] = f"{instruction_params[1]} : tableau{arr_sizes} de type {arr_type}"

		# If the statement does not have all its parameters set
		except IndexError:
			self.error(self.tranlate_method("compiler", "cpp", "errors", "arr_missing_params").format(
				line_number=line_number + 1
			))

		# If the variable type doesn't exist
		except KeyError:
			self.error(self.tranlate_method("compiler", "cpp", "errors", "unrecognized_var_type").format(
				line_number=line_number + 1, type=instruction_params[0]
			))


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
				params.append(f"{instruction_params[i + 1]} : ")

				# Try block in case there is an IndexError
				try:
					# If the param is an array, we parse it correctly
					if instruction_params[i].startswith("arr"):
						params[-1] += f"Tableau[{']['.join(instruction_params[i].split('_')[2:])}] de " \
						              f"{self.var_types[instruction_params[i].split('_')[1]]}s"

					# If the param is a structure, we parse it correctly
					elif instruction_params[i].startswith("struct_"):
						params[-1] += f"Structure {instruction_params[i][7:]}"

					# If the param is NOT an array nor a structure
					else:
						# We add it to the params as the type, followed by the name, of whose we remove the
						# first char if it is '&' (no datar mode in algorithmic)
						params[-1] += self.var_types[instruction_params[i]][instruction_params[i][0] == '&':]

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
			# We write the line as a function
			self.instructions_list[line_number] = f"Fonction {instruction_params[1]} ({params}) : "

			# If the return type is not a structure
			if not instruction_params[0].startswith("struct_"):
				# We add the return type
				self.instructions_list[line_number] += self.var_types[instruction_params[0]]

			# If the return type is a structure
			else:
				# We add the structure message followed by the return type
				self.instructions_list[line_number] += "Structure " + instruction_params[0][7:]

		else:  # Procedure
			self.instructions_stack.append("proc")
			# We write the line as a procedure
			self.instructions_list[line_number] = f"Procédure {instruction_params[1]} ({params})"


	def analyze_struct(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Creates a function definition """
		# Prevents a crash when extra spaces are at the end of the line
		while instruction_params[-1] == "": instruction_params.pop()

		# Function to handle the parameters, whether they are arrays or standard variables
		def handle_params(instruction_params):
			# The list of parameters
			params = []

			# Fetches each parameter (going two by two, because each param goes <type> <name>)
			for i in range(1, len(instruction_params), 2):
				# Adds the parameter to the list of parameters
				try:
					params.append(f"{instruction_params[i + 1]} : ")
				except IndexError:
					self.error(self.tranlate_method("compiler", "algo", "errors", "structure_def_unnamed_param").format(
						line_number=line_number + 1
					))
					return []

				# Try block in case there is an IndexError
				try:
					# If the param is an array, we parse it correctly
					if instruction_params[i].startswith("arr"):
						try:
							vtype = self.var_types[instruction_params[i].split('_')[1]]
						except KeyError:
							vtype = instruction_params[i].split('_')[1]
						params[-1] += f"Tableau[{']['.join(instruction_params[i].split('_')[2:])}] de " \
						              f"{vtype}s"

					# If the param is a structure, we parse it correctly
					elif instruction_params[i].startswith("struct_"):
						params[-1] += f"Structure {instruction_params[i][7:]}"

					# If the param is NOT an array
					else:
						# We add it to the params as the type, followed by the name, of whose we remove the
						# first char if it is '&' (no datar mode in algorithmic)
						params[-1] += self.var_types[instruction_params[i]][instruction_params[i][0] == '&':]

				# If an IndexError is encountered, we remove the last param from the params list and continue
				except IndexError:
					params.pop()

			# We return the params
			return params

		# Getting the parameters string
		params = handle_params(instruction_params)

		# We write the line as a structure
		self.instructions_list[line_number] = f"Structure {instruction_params[0]}\n"
		for param in params:
			self.instructions_list[line_number] += self.tab_char * (len(self.instructions_stack) + 2) + param + "\n"
		self.instructions_list[line_number] += self.tab_char * (len(self.instructions_stack) + 1) + "Fin Structure"


	def analyze_CODE_RETOUR(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Analyzes the return code. """
		self.instructions_list[line_number] = ""


	def analyze_init(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Analyzes the structure initialization. """
		if len(instruction_params) < 2:  # Error for missing parameters
			self.error(self.tranlate_method("compiler", "algo", "errors", "struct_missing_args").format(
				line_number=line_number + 1
			))
		elif len(instruction_params) % 2 == 1:  # Error for missing parameters
			self.error(self.tranlate_method("compiler", "algo", "errors", "struct_args_not_even").format(
				line_number=line_number + 1
			))
		else:
			# Creates the structure initialization
			self.instructions_list[line_number] = f"{instruction_params[1]} : Structure {instruction_params[0]}"

			# Then for each extra couple of arguments, adds a initialization to this line
			for i in range(2, len(instruction_params), 2):
				self.instructions_list[line_number] += "\n" + self.tab_char * (len(self.instructions_stack) + 1)
				self.instructions_list[line_number] += f"{instruction_params[1]}.{instruction_params[i]} <- {instruction_params[i + 1]}"

	def var_assignation(self, instruction:list, line_number:int):
		"""
		Assigns/reassigns a variable.
		"""
		# Reassigns a value with an operator
		if instruction[1] != "=":
			instruction.insert(2, f"{instruction[0]} {instruction[1][:-1]}")
		# Assigns the value to the variable
		instruction[1] = "<-"
		self.instructions_list[line_number] = " ".join(instruction)

	def final_trim(self, instruction_name:str, line_number:int):
		""" Adds the line ends, transforms the function names, and adds the correct indentation """
		# Adds the end of line
		self.instructions_list[line_number] = self.instructions_list[line_number].replace("(ENDL)", "(FIN DE LIGNE)")

		# Adds the correct tabbing (amount of tabs is equal to amount of instructions in the instructions stack,
		# minus one if the current instruction is in the instruction names)
		tab_amount = len(self.instructions_stack)
		if instruction_name in (*self.instruction_names.keys(), "else", "elif", "fx_start", "vars"):
			tab_amount -= 1
		self.instructions_list[line_number] = self.tab_char * tab_amount + self.instructions_list[line_number]


	def final_touches(self):
		""" Concatenates everything into one string """
		return "Début\n" + "".join(self.tab_char + instruction + "\n" for instruction in self.instructions_list) + "Fin"
