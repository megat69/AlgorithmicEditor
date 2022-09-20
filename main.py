import curses
import sys
import pyperclip


class App:
	def __init__(self, command_symbol: str = ":"):
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
			("p", self.compile_to_cpp, "Compile to C++")
		)
		self.instructions_list = []
		self.tab_char = "\t"
		self.command_symbol = command_symbol


	def main(self, stdscr):
		self.stdscr = stdscr
		self.stdscr.clear()
		self.rows, self.cols = self.stdscr.getmaxyx()
		self.apply_stylings()
		self.stdscr.refresh()

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
					elif key == "KEY_UP":
						pass
					elif key == "KEY_DOWN":
						pass
					elif key == "KEY_LEFT":
						self.current_index -= 1
					elif key == "KEY_RIGHT":
						self.current_index += 1
				else:
					# If the key is NOT a backspace character, we add the new character to the text
					self.current_text = self.current_text[:self.current_index] + key + self.current_text[self.current_index:]
					self.current_index += 1

				# Clamping the index
				self.current_index = max(min(self.current_index, len(self.current_text)), 0)

			# Displays the current text
			idx = 0
			cur = tuple()
			for i, line in enumerate(self.current_text.split("\n")):
				# TODO : Cursor placement
				if idx + len(line) > self.current_index and idx <= self.current_index:
					# The cursor must be on this line
					self.stdscr.addstr(i, len(str(self.lines)) + 1, line)
					cur = (i, len(str(self.lines)) + 1 + (self.current_index - idx), line[self.current_index - idx])
				elif idx + len(line) == self.current_index:
					self.stdscr.addstr(i, len(str(self.lines)) + 1, line)
					cur = (i, len(str(self.lines)) + 1 + (self.current_index - idx), " ")
				else:
					self.stdscr.addstr(i, len(str(self.lines)) + 1, line)
				idx += len(line) + 1
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
		cols = 0
		for key_name, function, name in self.commands:
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


	def save(self):
		#compiled_str = self.compile(True)
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
		         "case": "Cas", "default": "Autrement"}
		for i, line in enumerate(self.instructions_list):
			line = line.split(" ")
			instruction_name = line[0]
			instruction_params = line[1:]

			if instruction_name in ("int", "float", "string", "bool", "char"):
				var_type = ""
				if instruction_name == "int":
					var_type = "Entier"
				elif instruction_name == "float":
					var_type = "Réel"
				elif instruction_name == "string":
					var_type = "Chaîne de caractères"
				elif instruction_name == "bool":
					var_type = "Booléen"
				elif instruction_name == "char":
					var_type = "Caractère"
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

			elif len(instruction_params) != 0:
				if instruction_params[0] == "=":
					self.instructions_list[i] = f"{instruction_name} ← {' '.join(instruction_params[1:])}"

				elif instruction_params[0].endswith("="):
					self.instructions_list[i] = f"{instruction_name} ← {instruction_name} {instruction_params[0][:-1]} {' '.join(instruction_params[1:])}"

			self.instructions_list[i] = self.tab_char * (len(instructions_stack) - (1 if instruction_name in (*names.keys(), "else", "elif") else 0)) + self.instructions_list[i]

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

		for i, line in enumerate(self.instructions_list):
			line = line.split(" ")
			instruction_name = line[0]
			instruction_params = line[1:]

			if instruction_name in ("int", "float", "string", "bool", "char"):
				var_type = ""
				if instruction_name == "int":
					var_type = "int"
				elif instruction_name == "float":
					var_type = "float"
				elif instruction_name == "string":
					var_type = "std::string"
				elif instruction_name == "bool":
					var_type = "bool"
				elif instruction_name == "char":
					var_type = "char"
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
				self.instructions_list[i] = f"std::cout << {' '.join(instruction_params)}"

			elif instruction_name == "input":
				self.instructions_list[i] = f"std::cout << std::endl;\n{self.tab_char * (len(instructions_stack) + 1)}std::cin >> {' '.join(instruction_params)}"

			elif len(instruction_params) != 0:
				if instruction_params[0].endswith("="):
					self.instructions_list[i] = f"{instruction_name} {' '.join(instruction_params)}"

			self.instructions_list[i] = self.tab_char * (len(instructions_stack) - (1 if instruction_name in names else 0)) + self.instructions_list[i] + (";" if instruction_name not in (*names, "end") else "")

		final_compiled_code = "#include <iostream>\n\nint main() {\n" + "".join(
			self.tab_char + instruction + "\n" for instruction in self.instructions_list if instruction != ";") + self.tab_char + "return 0;\n}"
		pyperclip.copy(final_compiled_code)
		self.stdscr.clear()
		self.stdscr.addstr(final_compiled_code)
		self.stdscr.refresh()
		self.stdscr.getch()
		self.stdscr.clear()
		self.apply_stylings()
		self.stdscr.refresh()

# TODO : Addstr the text up to the index, get the cursor position, keep using addstr, and then move the cursor back to the saved position

if __name__ == "__main__":
	app = App(command_symbol=":" if "-command_symbol" not in sys.argv else sys.argv[sys.argv.index("-command_symbol") + 1])
	curses.wrapper(app.main)
