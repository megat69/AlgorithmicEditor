"""
A collection of utility functions for the editor.
"""
import curses
import os
from functools import partial
from math import ceil


def display_menu(stdscr, commands: tuple, default_selected_element: int = 0, label: str = None, clear: bool = True, space_out_last_option: bool = False, allow_key_input: bool = False):
	"""
	Displays a menu at the center of the screen, with every option chosen by the user.
	:param stdscr: The standard screen.
	:param commands: A tuple of commands.
	:param default_selected_element: The menu element selected by default. 0 by default. It is composed of tuples of 2 elements : the command name, and the function to call upon selection.
	:param label: Displays a title above the menu. None by default.
	:param clear: Whether to clear the screen before creating the menu. True by default.
	:param space_out_last_option: Adds a newline before the last option of the menu.
	:param allow_key_input: If true, allows the user to type in a string. The menu will only show the elements containing the string.
	"""
	# Gets the middle of the screen coordinates
	screen_middle_y, screen_middle_x = get_screen_middle_coords(stdscr)

	# Selects an element
	selected_element = default_selected_element

	# Gets the amount of given commands, and stores it into a variable, for optimization purposes.
	cmd_len = len(commands)

	# Clears the contents of the screen
	if clear:
		stdscr.clear()

	# Gets the rows and columns
	rows, cols = stdscr.getmaxyx()

	# Keeps in mind the amount of pages and the current page
	max_items_per_page = rows - 5 - allow_key_input
	current_page = 0
	total_pages = ceil(cmd_len / max_items_per_page)

	# Initializing the key
	key = ""

	# Initializing the string to search for
	string_to_search_for = ""

	# Function returning only the elements of the list that contain the given substring
	def return_list_with_substrings(lst: tuple, substring: str, enabled: bool) -> tuple:
		if not enabled : return lst
		else:
			new_lst = []
			for element in lst:
				if substring in element[0]:
					new_lst.append(element)
			return tuple(new_lst)

	# Looping until the user selects an item
	while key not in ("\n", "\t"):
		# Displays the menu title
		if label is not None:
			# Checking for the horizontal size
			if len(label) > cols - 5:
				label = label[:cols - 5] + "..."
			# Displaying label
			stdscr.addstr(
				screen_middle_y - min(max_items_per_page, cmd_len) // 2 - 2,
				screen_middle_x - len(label) // 2,
				label
			)
		# Displays the current string
		if allow_key_input:
			# Checking for the horizontal size
			if len(repr(string_to_search_for)) > cols - 5:
				string_to_search_for = string_to_search_for[:cols - 5] + "..."
			# Displaying label
			stdscr.addstr(
				screen_middle_y - min(max_items_per_page, cmd_len) // 2 - 1,
				screen_middle_x - len(repr(string_to_search_for)) // 2,
				repr(string_to_search_for)
			)

		# Remembering the length of the selected slice
		current_command_len = lambda: len(
			return_list_with_substrings(commands, string_to_search_for, allow_key_input)[max_items_per_page * current_page : max_items_per_page * (current_page + 1)]
		)

		# Displays the menu
		for i, command in enumerate(
			# Only displays the menu elements from the current page
			return_list_with_substrings(commands, string_to_search_for, allow_key_input)[max_items_per_page * current_page : max_items_per_page * (current_page + 1)]
		):
			# Checking for the horizontal size
			if len(command[0]) > cols - 5:
				command[0] = command[0][:cols - 5] + "..."
			# Displays the menu item
			stdscr.addstr(
				screen_middle_y - min(max_items_per_page, cmd_len) // 2 + i + \
				((max_items_per_page * current_page + i == len(return_list_with_substrings(commands, string_to_search_for, allow_key_input)) - 1) * space_out_last_option) + allow_key_input,
				screen_middle_x - len(command[0]) // 2,
				command[0],
				curses.A_NORMAL if i != selected_element else curses.A_REVERSE  # Reverses the color if the item is selected
			)

		# Displays at the bottom right how many pages are available
		if total_pages > 1:
			page_left_str = f"Page {current_page + 1}/{total_pages}"
			stdscr.addstr(rows - 3, cols - len(page_left_str) - 3, page_left_str, curses.A_REVERSE)

		# Fetches a key
		key = stdscr.getkey()

		# Selects another item
		if key == "KEY_UP":
			selected_element -= 1
		elif key == "KEY_DOWN":
			selected_element += 1
		elif key == "KEY_LEFT":
			# If this is the first page, we get to the last one
			if current_page == 0:
				current_page = total_pages - 1
				# Putting the cursor at the end if there are fewer elements on this page
				if selected_element >= current_command_len():
					selected_element = current_command_len() - 1
			# Otherwise, we get to the previous
			else:
				current_page -= 1
			stdscr.clear()
		elif key == "KEY_RIGHT":
			# If this is the last page, we get to the first one
			if current_page == total_pages - 1:
				current_page = 0
			# Otherwise, we get to the next
			else:
				current_page += 1
				# Putting the cursor at the end if there are fewer elements on this page
				if selected_element >= current_command_len():
					selected_element = current_command_len() - 1
			stdscr.clear()

		elif key in ("\n", "\t"): pass

		elif allow_key_input:
			if key == "\b":
				if string_to_search_for != "":
					string_to_search_for = string_to_search_for[:-1]
			else:
				string_to_search_for += key
			selected_element = 0
			stdscr.clear()

		# Wrap-around
		if selected_element < 0:
			selected_element = current_command_len() - 1
		elif selected_element >= current_command_len():
			selected_element = 0

	# Clears the screen
	stdscr.clear()

	# Calls the function from the appropriate item
	try:
		return return_list_with_substrings(commands, string_to_search_for, allow_key_input)[selected_element + current_page * max_items_per_page][1]()
	except IndexError:
		return 0



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
		if key in ("KEY_BACKSPACE", "\b", "\0"):
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


class browse_files:
	last_browsed_path = ""
	def __init__(self, stdscr, given_path:str=None, can_create_files:bool=True):
		"""
		Browse files to find one, returns a path to this file.
		:param stdscr: The standard screen.
		:return: A path to the selected file.
		"""
		self.path = browse_files.last_browsed_path if given_path is None else os.path.normpath(given_path)
		self.stdscr = stdscr
		self.can_create_files = can_create_files


	def __call__(self, stdscr=None, given_path:str=None) -> str:
		self.path = browse_files.last_browsed_path if given_path is None else os.path.normpath(given_path)
		if self.path == "":
			self.path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../"))
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


		menu_items = [("📁 ../", partial(self, self.stdscr, os.path.join(self.path, "../")))]
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

		browse_files.last_browsed_path = os.path.dirname(self.path)
		return self.path


	def create_new_file(self, position_y:int):
		"""
		Asks the user to input a name for a file and creates it, then sets the path to this file.
		"""
		filename = input_text(self.stdscr, 30, position_y)
		self.path = os.path.normpath(os.path.join(self.path, filename))
