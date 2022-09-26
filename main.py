import curses
import sys
import pyperclip
from functools import partial


class App:
	def __init__(self, command_symbol: str = ":", using_namespace_std: bool = False):
		self.current_text = ""
		self.stdscr = None
		self.rows, self.cols = 0, 0
		self.lines = 1
		self.current_index = 0
		self.commands = (
			("q", self.quit, "Quit"),
			("c", self.compile, "Compile"),
			("t", self.modify_tab_char, "Modify tab char"),
			("s", self.save, "Save"),
			("o", self.open, "Open"),
			("p", self.compile_to_cpp, "Compile to C++"),
			(command_symbol, partial(self.add_char_to_text, command_symbol), command_symbol)
		)
		self.instructions_list = []
		self.tab_char = "\t"
		self.command_symbol = command_symbol
		self.using_namespace_std = using_namespace_std


	def main(self, stdscr):
		self.stdscr = stdscr
		self.stdscr.clear()
		self.rows, self.cols = self.stdscr.getmaxyx()
		self.apply_stylings()
		self.stdscr.refresh()

		# Declaring color pairs, then saving them
		curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
		color_pairs = {
			"statement": 1,
			"function": 2,
			"variable": 3,
			"instruction": 4,
			"strings": 3
		}
		color_control_flow = {
			"statement": ("if", "else", "end", "elif", "for", "while"),
			"function": ("fx", "fx_start", "return"),
			"variable": ('int', 'float', 'string', 'bool', 'char'),
			"instruction": ("print", "input")
		}

		# App main loop
		while True:
			# Gets the current screen size
			self.rows, self.cols = self.stdscr.getmaxyx()

			# Key input
			key = self.stdscr.getkey()

			# If system key is pressed
			if key == self.command_symbol:
				self.stdscr.addstr(self.rows - 1, 0, self.command_symbol)
				key = self.stdscr.getkey()
				for key_name, function, name in self.commands:
					if key == key_name:
						self.stdscr.addstr(self.rows - 1, 1, key_name)
						self.stdscr.refresh()
						key = self.stdscr.getkey()
						if key == "\n":
							function()
				self.stdscr.addstr(self.rows - 1, 0, " " * 4)
			# If it is a regular key
			else:
				# Screen clearing
				self.stdscr.clear()

				# If the key IS a backspace character, we remove the last character from the text
				if key in ("\b", "\0") or key.startswith("KEY_"):
					if key == "\b":
						if self.current_index > 0:
							self.current_text = self.current_text[:self.current_index - 1] + self.current_text[self.current_index:]
							self.current_index -= 1
					elif key in ("KEY_UP", "KEY_DOWN"):
						text = self.current_text + "\n"
						indexes = tuple(index for index in range(len(text)) if text.startswith('\n', index))
						closest_index = min(indexes, key=lambda x:abs(x-self.current_index))
						closest_index = indexes.index(closest_index)
						closest_index = closest_index + (-1)**(key == "KEY_UP")
						try:
							if closest_index <= 0:
								self.current_index = 0
							else:
								self.current_index = indexes[closest_index]
						except IndexError: pass
					elif key == "KEY_LEFT":
						self.current_index -= 1
					elif key == "KEY_RIGHT":
						self.current_index += 1
				else:
					# If the key is NOT a backspace character, we add the new character to the text
					self.add_char_to_text(key)

				# Clamping the index
				self.current_index = max(min(self.current_index, len(self.current_text)), 0)

			# Displays the current text
			# TODO Longer lines
			idx = 0
			cur = tuple()
			for i, line in enumerate(self.current_text.split("\n")):
				# Getting the splitted line for syntax highlighting
				splitted_line = line.split(" ")

				# Getting the cursor position
				if idx + len(line) > self.current_index and idx <= self.current_index:
					cur = (i, len(str(self.lines)) + 1 + (self.current_index - idx), line[self.current_index - idx])
				elif idx + len(line) == self.current_index:
					cur = (i, len(str(self.lines)) + 1 + (self.current_index - idx), " ")

				# Writing the line to the screen
				if len(str(self.lines)) + 1 + len(line) < self.cols:
					self.stdscr.addstr(i, len(str(self.lines)) + 1, line)
				else:
					self.stdscr.addstr(i, len(str(self.lines)) + 1, line[:self.cols - (len(str(self.lines)) + 1)])

				# Updating the amount of characters in the line
				idx += len(line) + 1

				# Tests the beginning of the line to add a color, syntax highlighting
				start_statement = splitted_line[0]
				if start_statement in tuple(sum(color_control_flow.values(), tuple())):
					if start_statement in color_control_flow["statement"]:
						c_pair = "statement"
					elif start_statement in color_control_flow["function"]:
						c_pair = "function"
					elif start_statement in color_control_flow["instruction"]:
						c_pair = "instruction"
					else:
						c_pair = "variable"
					# Overwrites the beginning of the line with the given color if possible
					self.stdscr.addstr(i, len(str(self.lines)) + 1, start_statement, curses.color_pair(color_pairs[c_pair]))

				# Finds all strings between quotes (single or double) and highlights them green
				quotes_indexes = tuple(i for i, ltr in enumerate(line) if ltr == "\"")
				for j, index in enumerate(quotes_indexes):
					if j % 2 == 0:
						try:
							self.stdscr.addstr(
								i,
								len(str(self.lines)) + 1 + index, line[index:quotes_indexes[j + 1] + 1],
								curses.color_pair(color_pairs["strings"] if not "=" in splitted_line[1] else 5)
							)
						except IndexError:
							self.stdscr.addstr(
								i,
								len(str(self.lines)) + 1 + index, line[index:],
								curses.color_pair(color_pairs["strings"] if not "=" in splitted_line[1] else 5)
							)

				# Finds all equal signs to highlight them in statement color
				try:
					if "=" in splitted_line[1]:
						self.stdscr.addstr(
							i, len(str(self.lines)) + 2 + len(splitted_line[0]),
							splitted_line[1],
							curses.color_pair(color_pairs["statement"])
						)
				except IndexError: pass  # If there is no space in the line

				# Finds all '&' signs and gives them the statement color
				symbol_indexes = tuple(i for i, ltr in enumerate(line) if ltr == "&")
				for index in symbol_indexes:
					self.stdscr.addstr(
						i,
						len(str(self.lines)) + 1 + index, line[index],
						curses.color_pair(color_pairs["statement"])
					)

				# If the instruction is a function declaration, we highlight each types in the declaration
				if splitted_line[0] == "fx" and len(splitted_line) > 1:
					# Highlighting the function's return type; as statement if void or variable otherwise
					if splitted_line[1] in (*color_control_flow["variable"], "void"):
						self.stdscr.addstr(
							i, len(str(self.lines)) + 4,
							splitted_line[1],
							curses.color_pair(color_pairs["variable" if splitted_line[1] != "void" else "statement"])
						)

					# Highlighting each argument's type
					for j in range(3, len(splitted_line), 2):
						if splitted_line[j] in (*color_control_flow["variable"], "void"):
							self.stdscr.addstr(
								i, len(str(self.lines)) + 2 + len(" ".join(splitted_line[:j])),
								splitted_line[j], curses.color_pair(color_pairs["variable"])
							)

			# Placing cursor
			if cur != tuple():
				self.stdscr.addstr(*cur, curses.A_REVERSE)

			# Visual stylings, e.g. adds a full line over the input
			self.apply_stylings()

			# Screen refresh after input
			self.stdscr.refresh()


	def quit(self) -> None:
		"""
		Exits the app.
		"""
		sys.exit(0)


	def apply_stylings(self) -> None:
		"""
		Apply all the stylings to the screen.
		"""
		# Applies the bar at the bottom of the screen
		self.stdscr.addstr(self.rows - 3, 0, "▓" * self.cols)

		# Adds the commands list at the bottom of the screen
		cols = 0
		for key_name, function, name in self.commands:
			if key_name != self.command_symbol:
				generated_str = f"{self.command_symbol}{key_name} - {name}"
				self.stdscr.addstr(self.rows - 2, cols, generated_str, curses.A_REVERSE | curses.A_BOLD)
				cols += len(generated_str)
				self.stdscr.addstr(self.rows - 2, cols, " ")
				cols += 1
		self.stdscr.refresh()

		# Gets the amount of lines in the text
		self.calculate_line_numbers()
		# Puts the line numbers at the edge of the screen
		for i in range(self.lines):
			self.stdscr.addstr(i, 0, str(i + 1).zfill(len(str(self.lines))), curses.A_REVERSE)


	def calculate_line_numbers(self) -> int:
		"""
		Calculates the amount of lines in the text.
		Saves it into the correct variable and returns it.
		"""
		self.lines = self.current_text.count("\n") + 1
		return self.lines


	def modify_tab_char(self) -> None:
		"""
		Modifies the tab character.
		"""
		key = self.stdscr.getkey()
		final_str = ""
		while key != "\n":
			final_str += key
			self.stdscr.addstr(self.rows - 1, 3, final_str)
			key = self.stdscr.getkey()
		self.tab_char = final_str


	def add_char_to_text(self, key: str):
		"""
		Adds the given character at the end of the text.
		:param key: A character to add to the text.
		"""
		self.current_text = self.current_text[:self.current_index] + key + self.current_text[self.current_index:]
		self.current_index += 1


	def save(self):
		# compiled_str = self.compile(True)
		pyperclip.copy(self.current_text)
		# TODO : Save


	def open(self):
		self.current_text = pyperclip.paste()
		self.stdscr.clear()
		self.stdscr.refresh()
		self.apply_stylings()


	def compile(self, noshow:bool=False) -> None | str:
		"""
		Compiles the inputted text into algorithmic code.
		:param noshow: Whether not to show the compiled code.
		"""
		self.instructions_list = self.current_text.split("\n")
		instructions_stack = []
		names = {"for": "Pour", "if": "Si", "while": "Tant Que", "switch": "Selon",
		         "case": "Cas", "default": "Autrement", "fx": "Fonction", "proc": "Procédure"}
		var_types = {"int": "Entier", "float": "Réel", "string": "Chaîne de caractères", "bool": "Booléen",
		             "char": "Caractère"}
		for i, line in enumerate(self.instructions_list):
			line = line.split(" ")
			instruction_name = line[0]
			instruction_params = line[1:]

			if instruction_name in var_types.keys():
				var_type = var_types[instruction_name]
				self.instructions_list[i] = ", ".join(instruction_params) + " : " + var_type + \
				                            ("s" if len(instruction_params) != 1 and instruction_name != "string" else "")

			elif instruction_name == "for":
				instructions_stack.append("for")
				self.instructions_list[i] = f"Pour {instruction_params[0]} allant de {instruction_params[1]} à " \
				                            f"{instruction_params[2]} avec un pas de " \
				                            f"{1 if len(instruction_params) < 4 else instruction_params[3]}"

			elif instruction_name == "end":
				last_elem = instructions_stack.pop()
				self.instructions_list[i] = f"Fin {names[last_elem]}"

			elif instruction_name == "while":
				instructions_stack.append("while")
				self.instructions_list[i] = f"Tant Que {' '.join(instruction_params)}"

			elif instruction_name == "if":
				instructions_stack.append("if")
				self.instructions_list[i] = f"Si {' '.join(instruction_params)}"

			elif instruction_name == "else":
				self.instructions_list[i] = f"Sinon"

			elif instruction_name == "elif":
				self.instructions_list[i] = f"Sinon Si {' '.join(instruction_params)}"

			elif instruction_name == "switch":
				instructions_stack.append("switch")
				self.instructions_list[i] = f"SELON {' '.join(instruction_params)}"

			elif instruction_name == "case":
				instructions_stack.append("case")
				self.instructions_list[i] = f"Cas {' '.join(instruction_params)}"

			elif instruction_name == "default":
				instructions_stack.append("default")
				self.instructions_list[i] = f"Autrement : {' '.join(instruction_params)}"

			elif instruction_name == "print":
				self.instructions_list[i] = f"Afficher({' '.join(instruction_params)})"

			elif instruction_name == "input":
				self.instructions_list[i] = f"Saisir({' '.join(instruction_params)})"

			elif instruction_name == "fx":
				if instruction_params[0] != "void":
					instructions_stack.append("fx")
					params = tuple(f"{instruction_params[i+1]} : {var_types[instruction_params[i]]}" for i in range(2, len(instruction_params), 2))
					params = ", ".join(params)
					self.instructions_list[i] = f"Fonction {instruction_params[1]} ({params}) : {var_types[instruction_params[0]]}"
					del params
				else:
					instructions_stack.append("proc")
					params = tuple(f"{var_types[instruction_params[i]]} {instruction_params[i + 1]}" for i in
					               range(2, len(instruction_params), 2))
					params = ", ".join(params)
					self.instructions_list[i] = f"Procédure {instruction_params[1]} ({params})"
					del params


			elif instruction_name == "precond": self.instructions_list[i] = f"Préconditions : {' '.join(instruction_params)}"
			elif instruction_name == "data": self.instructions_list[i] = f"Données : {' '.join(instruction_params)}"
			elif instruction_name == "result": self.instructions_list[i] = f"Résultats : {' '.join(instruction_params)}"
			elif instruction_name == "desc": self.instructions_list[i] = f"Description : {' '.join(instruction_params)}"
			elif instruction_name == "vars": self.instructions_list[i] = f"Variables locales : {' '.join(instruction_params)}"
			elif instruction_name == "fx_start": self.instructions_list[i] = f"Début : {' '.join(instruction_params)}"
			elif instruction_name == "return": self.instructions_list[i] = f"Retourner {' '.join(instruction_params)}"

			elif len(instruction_params) != 0:
				if instruction_params[0] == "=":
					self.instructions_list[i] = f"{instruction_name} ← {' '.join(instruction_params[1:])}"

				elif instruction_params[0].endswith("="):
					self.instructions_list[i] = f"{instruction_name} ← {instruction_name} {instruction_params[0][:-1]} {' '.join(instruction_params[1:])}"

			self.instructions_list[i] = self.instructions_list[i].replace("(ENDL)", "(FIN DE LIGNE)")
			self.instructions_list[i] = self.tab_char * (len(instructions_stack) - (1 if instruction_name in (*names.keys(), "else", "elif", "fx_start") else 0)) + self.instructions_list[i]

		final_compiled_code = "Début\n" + "".join(self.tab_char + instruction + "\n" for instruction in self.instructions_list) + "Fin"
		if noshow is False:
			pyperclip.copy(final_compiled_code)
			self.stdscr.clear()
			self.stdscr.addstr(final_compiled_code)
			self.stdscr.refresh()
			self.stdscr.getch()
			self.stdscr.clear()
			self.apply_stylings()
			self.stdscr.refresh()
		else:
			return final_compiled_code


	def compile_to_cpp(self):
		"""
		Compiles everything to C++ code ; might not always work.
		"""
		self.instructions_list = self.current_text.split("\n")
		instructions_stack = []
		names = ('for', 'if', 'while', 'switch', 'case', 'default', 'else', 'elif')
		ifsanitize = lambda s: s.replace('ET', '&&').replace('OU', '||').replace('NON', '!')
		var_types = {"int": "int", "float": "float", "string": "std::string", "bool": "bool",
		             "char": "char"}
		fxtext = []
		last_elem = None

		for i, line in enumerate(self.instructions_list):
			line = line.split(" ")
			instruction_name = line[0]
			instruction_params = line[1:]

			if instruction_name in var_types.keys():
				var_type = var_types[instruction_name]
				self.instructions_list[i] = var_type + " " + ", ".join(instruction_params)

			elif instruction_name == "for":
				instructions_stack.append("for")
				self.instructions_list[i] = f"for ({instruction_params[0]} = {instruction_params[1]}; " \
				                            f"{instruction_params[0]} <= {instruction_params[2]}; " \
				                            f"{instruction_params[0]} += {1 if len(instruction_params) < 4 else instruction_params[3]})" + "{"

			elif instruction_name == "end":
				last_elem = instructions_stack.pop()
				if last_elem in ("case", "default"):
					self.instructions_list[i] = self.tab_char + "break;"
				else:
					self.instructions_list[i] = "}"

			elif instruction_name == "while":
				instructions_stack.append("while")
				self.instructions_list[i] = f"while ({ifsanitize(' '.join(instruction_params))}) " + "{"

			elif instruction_name == "if":
				instructions_stack.append("if")
				self.instructions_list[i] = f"if ({ifsanitize(' '.join(instruction_params))}) " + "{"

			elif instruction_name == "else":
				self.instructions_list[i] = "} else {"

			elif instruction_name == "elif":
				self.instructions_list[i] = "} " + f"else if ({ifsanitize(' '.join(instruction_params))}) " + " {"

			elif instruction_name == "switch":
				instructions_stack.append("switch")
				self.instructions_list[i] = f"switch ({' '.join(instruction_params)}) " + "{"

			elif instruction_name == "case":
				instructions_stack.append("case")
				self.instructions_list[i] = f"case {' '.join(instruction_params)}:"

			elif instruction_name == "default":
				instructions_stack.append("default")
				self.instructions_list[i] = "default:"

			elif instruction_name == "print":
				self.instructions_list[i] = f"std::cout << {' '.join(instruction_params).replace(' & ', ' << ')}"

			elif instruction_name == "input":
				self.instructions_list[i] = f"std::cout << std::endl;\n{self.tab_char * (len(instructions_stack) + 1)}std::cin >> {' '.join(instruction_params)}"

			elif instruction_name == "fx":
				instructions_stack.append("fx")
				params = tuple(f"{var_types[instruction_params[i]]} {instruction_params[i+1]}" for i in range(2, len(instruction_params), 2))
				params = ", ".join(params)
				if instruction_params[0] != "void":
					self.instructions_list[i] = f"{var_types[instruction_params[0]]} {instruction_params[1]}({params}) " + "{"
				else:
					self.instructions_list[i] = f"void {instruction_params[1]}({params}) " + "{"
				del params

			elif instruction_name == "precond": self.instructions_list[i] = f"// Préconditions : {' '.join(instruction_params)}"
			elif instruction_name == "data": self.instructions_list[i] = f"// Données : {' '.join(instruction_params)}"
			elif instruction_name == "result": self.instructions_list[i] = f"// Résultats : {' '.join(instruction_params)}"
			elif instruction_name == "desc": self.instructions_list[i] = f"// Description : {' '.join(instruction_params)}"
			elif instruction_name == "vars": self.instructions_list[i] = f"// Variables locales : {' '.join(instruction_params)}"
			elif instruction_name == "fx_start": self.instructions_list[i] = ""
			elif instruction_name == "return": self.instructions_list[i] = f"return {' '.join(instruction_params)}"

			elif len(instruction_params) != 0:
				if instruction_params[0].endswith("="):
					self.instructions_list[i] = f"{instruction_name} {' '.join(instruction_params)}"

			self.instructions_list[i] = self.instructions_list[i].replace("puissance(", "pow(").replace("racine(", "sqrt(")
			self.instructions_list[i] = self.instructions_list[i].replace("aleatoire(", "srand(time(NULL))")
			self.instructions_list[i] = self.instructions_list[i].replace("(ENDL)", "\\n")
			self.instructions_list[i] = self.tab_char * (len(instructions_stack) - (1 if instruction_name in (*names, "fx") else 0))\
			                            + self.instructions_list[i] + (";" if instruction_name not in
			                                (*names, "end", "fx", "fx_start", "precond", "data", "result", "desc", "vars", "//") else "")
			if self.using_namespace_std:
				self.instructions_list[i] = self.instructions_list[i].replace("std::", "")

			if "fx" in instructions_stack or (instruction_name == "end" and last_elem == "fx"):
				fxtext.append(self.instructions_list[i])
				if instruction_name == "end":
					fxtext[-1] += "\n"
				self.instructions_list[i] = ""

		final_compiled_code = "#include <iostream>\n" + ("using namespace std;\n" if self.using_namespace_std else "") + \
		                      ("#include <math.h>\n" if 'puissance(' in self.current_text or \
		                                                'racine(' in self.current_text else '')  \
		                      + ("#include <stdlib.h>\n#include <time.h>\n" if 'aleatoire(' in self.current_text else '') + "\n" +\
							  "\n".join(fxtext) + "\n\nint main() {\n" + "".join(
			self.tab_char + instruction + "\n" for instruction in self.instructions_list if instruction != ";" and instruction != "")\
		                      + self.tab_char + "return 0;\n}"
		pyperclip.copy(final_compiled_code)
		self.stdscr.clear()
		self.stdscr.addstr(final_compiled_code)
		self.stdscr.refresh()
		self.stdscr.getch()
		self.stdscr.clear()
		self.apply_stylings()
		self.stdscr.refresh()


if __name__ == "__main__":
	app = App(
		command_symbol=":" if "-command_symbol" not in sys.argv else sys.argv[sys.argv.index("--command_symbol") + 1],
		using_namespace_std=False if "--using_namespace_std" not in sys.argv else sys.argv[sys.argv.index("--using_namespace_std") + 1]
	)
	curses.wrapper(app.main)
