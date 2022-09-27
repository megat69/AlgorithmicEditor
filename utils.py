"""
A collection of utility functions for the editor.
"""
import curses
from typing import Tuple, Callable


def display_menu(stdscr, commands: Tuple[Tuple[str, Callable]], default_selected_element: int = 0) -> None:
	"""
	Displays a menu at the center of the screen, with every option chosen by the user.
	:param stdscr: The standard screen.
	:param commands: A tuple of commands.
	:param default_selected_element: The menu element selected by default. 0 by default.
	It is composed of tuples of 2 elements : the command name, and the function to call upon selection.
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
		stdscr.addstr(
			screen_middle_y - cmd_len // 2 - 2,
			screen_middle_x - len(" -- MENU --") // 2,
			"-- MENU --"
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
	commands[selected_element][1]()



def get_screen_middle_coords(stdscr) -> tuple[int, int]:
	"""
	Returns the middle coordinates of the screen.
	:param stdscr: The standard screen.
	:return: A tuple of 2 integers : the middle coordinates of the screen, as (rows, cols).
	"""
	screen_y_size, screen_x_size = stdscr.getmaxyx()
	return screen_y_size // 2, screen_x_size // 2
