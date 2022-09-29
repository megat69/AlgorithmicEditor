"""
A collection of utility functions for the editor.
"""
import curses
import os
from functools import partial


def display_menu(stdscr, commands: tuple, default_selected_element: int = 0, label: str = None):
	"""
	Displays a menu at the center of the screen, with every option chosen by the user.
	:param stdscr: The standard screen.
	:param commands: A tuple of commands.
	:param default_selected_element: The menu element selected by default. 0 by default.
	It is composed of tuples of 2 elements : the command name, and the function to call upon selection.
	:param label: Displays a title above the menu. None by default.
	"""
	# Gets the middle of the screen coordinates
	screen_middle_y, screen_middle_x = get_screen_middle_coords(stdscr)

	# Selects an element
	selected_element = default_selected_element

	# Gets the amount of given commands, and stores it into a variable, for omptimization purposes.
	cmd_len = len(commands)

	# Clears the contents of the screen
	stdscr.clear()

	# Initializing the key
	key = ""

	# Looping until the user selects an item
	while key not in ("\n", "\t"):
		# Displays the menu title
		if label is not None:
			stdscr.addstr(
				screen_middle_y - cmd_len // 2 - 2,
				screen_middle_x - len(label) // 2,
				label
			)

		# Displays the menu
		for i, command in enumerate(commands):
			# Displays the menu item
			stdscr.addstr(
				screen_middle_y - cmd_len // 2 + i,
				screen_middle_x - len(command[0]) // 2,
				command[0],
				curses.A_NORMAL if i != selected_element else curses.A_REVERSE  # Reverses the color if the item is selected
			)

		# Fetches a key
		key = stdscr.getkey()

		# Selects another item
		if key == "KEY_UP":
			selected_element -= 1
		elif key == "KEY_DOWN":
			selected_element += 1
		# Wrap-around
		if selected_element < 0:
			selected_element = cmd_len - 1
		elif selected_element > cmd_len - 1:
			selected_element = 0

	# Clears the screen
	stdscr.clear()

	# Calls the function from the appropriate item
	return commands[selected_element][1]()



def get_screen_middle_coords(stdscr) -> tuple[int, int]:
	"""
	Returns the middle coordinates of the screen.
	:param stdscr: The standard screen.
	:return: A tuple of 2 integers : the middle coordinates of the screen, as (rows, cols).
	"""
	screen_y_size, screen_x_size = stdscr.getmaxyx()
	return screen_y_size // 2, screen_x_size // 2


def input_text(stdscr, position_x: int = 0, position_y: int = None) -> str:
	"""
	Asks the user for input and then returns the given text.
	:param stdscr: The standard screen.
	:param position_x: The x coordinates of the input. Default is to the left of the screen.
	:param position_y: The y coordinates of the input. Default is to the bottom of the screen.
	:return: Returns the string inputted by the user.
	"""
	# Initializing vars
	key = ""
	final_text = ""
	if position_y is None: position_y = stdscr.getmaxyx()[0] - 1

	# Loops until the user presses Enter
	while key != "\n":
		# Awaits for a keypress
		key = stdscr.getkey()

		# Sanitizes the input
		if key == "\b":
			# If the character is a backspace, we remove the last character from the final text
			final_text = final_text[:-1]
			# Removes the character from the screen
			stdscr.addstr(position_y, position_x + len(final_text), " ")

		elif key.startswith("KEY_") or (key.startswith("^") and key != "^") or key == "\n":
			# Does nothing if it is a special key
			pass

		else:
			# Adds the key to the input
			final_text += key

		# Shows the final text at the bottom
		stdscr.addstr(position_y, position_x, final_text)

	# Writes the full length of the final text as spaces where it was written
	stdscr.addstr(position_y, position_x, " " * len(final_text))

	# Returns the final text
	return final_text


last_browsed_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../"))
class browse_files:
	def __init__(self, stdscr, given_path:str=None, can_create_files:bool=True):
		"""
		Browse files to find one, returns a path to this file.
		:param stdscr: The standard screen.
		:return: A path to the selected file.
		"""
		self.path = last_browsed_path if given_path is None else os.path.normpath(given_path)
		self.stdscr = stdscr
		self.can_create_files = can_create_files


	def __call__(self, stdscr=None, given_path:str=None) -> str:
		global last_browsed_path
		self.path = last_browsed_path if given_path is None else os.path.normpath(given_path)
		if stdscr is not None:
			self.stdscr = stdscr
		folders_list = []
		files_list = []
		for element in os.listdir(self.path):
			if os.path.isdir(os.path.join(self.path, element)):
				folders_list.append(element)
			else:
				files_list.append(element)


		def set_new_path(new_path:str):
			self.path = new_path


		menu_items = [(f"📁 ../", partial(self, self.stdscr, os.path.join(self.path, "../")))]
		menu_items.extend([
			(f"📁 {name}", partial(self, self.stdscr, os.path.join(self.path, name))) \
			for name in folders_list
		])
		menu_items.extend([
			(f"📄 {name}", partial(set_new_path, os.path.normpath(os.path.join(self.path, name)))) \
			for name in files_list
		])
		menu_items.extend([
			("Cancel", partial(set_new_path, ""))
		])
		if self.can_create_files:
			menu_items.extend([
				("New file :", partial(self.create_new_file, len(menu_items) + 1))
			])
		menu_items = tuple(menu_items)

		display_menu(
			self.stdscr,
			menu_items,
			label=self.path
		)

		last_browsed_path = os.path.dirname(self.path)
		return self.path


	def create_new_file(self, position_y:int):
		"""
		Asks the user to input a name for a file and creates it, then sets the path to this file.
		"""
		filename = input_text(self.stdscr, 30, position_y)
		self.path = os.path.normpath(os.path.join(self.path, filename))
