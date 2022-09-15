import curses
import sys
import pyperclip


class App:
	def __init__(self):
		self.current_text = ""
		self.stdscr = None
		self.rows, self.cols = 0, 0
		self.lines = 1
		self.current_index = 0
		self.commands = (
			("q", self.quit, "Quit"),
			("c", self.compile, "Compile"),
			("t", self.modify_tab_char, "Modify tab char")
		)
		self.instructions_list = []
		self.tab_char = "\t"


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
			if key == ":":
				self.stdscr.addstr(self.rows - 1, 0, ":")
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

				# If the key is NOT a backspace character, we add the new character to the text
				if key == "\b" or key.startswith("KEY_"):
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
				# If the key IS a backspace character, we remove the last character from the text
				else:
					self.current_text = self.current_text[:self.current_index] + key + self.current_text[self.current_index:]
					self.current_index += 1

				# Clamping the index
				self.current_index = max(min(self.current_index, len(self.current_text)), 0)

			# Displays the current text
			for i, line in enumerate(self.current_text.split("\n")):
				# TODO : Cursor placement
				self.stdscr.addstr(i, len(str(self.lines)) + 1, line)

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
			generated_str = f":{key_name} - {name}"
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


	def modify_tab_char(self):
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


	def compile(self) -> None:
		"""
		Compiles the inputted text into algorithmic code.
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

			self.instructions_list[i] = self.tab_char * (len(instructions_stack) - (1 if instruction_name in names.keys() else 0)) + self.instructions_list[i]

		final_compiled_code = "Début\n" + "".join(self.tab_char + instruction + "\n" for instruction in self.instructions_list) + "Fin"
		pyperclip.copy(final_compiled_code)
		self.stdscr.clear()
		self.stdscr.addstr(final_compiled_code)
		self.stdscr.refresh()
		self.stdscr.getch()
		self.stdscr.clear()
		self.apply_stylings()
		self.stdscr.refresh()


if __name__ == "__main__":
	app = App()
	curses.wrapper(app.main)
