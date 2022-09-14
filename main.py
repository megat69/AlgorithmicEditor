import curses
import sys


class App:
	def __init__(self):
		self.current_text = ""
		self.stdscr = None
		self.rows, self.cols = 0, 0
		self.lines = 1


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
				if self.stdscr.getkey() == "q":
					self.stdscr.addstr(self.rows - 1, 1, "q")
					self.stdscr.refresh()
					self.stdscr.getch()
					self.quit()
			# If it is a regular key
			else:
				# Screen clearing
				self.stdscr.clear()

				# If the key is NOT a backspace character, we add the new character to the text
				if key not in ("\b", "KEY_UP", "KEY_DOWN", "KEY_LEFT", "KEY_RIGHT"):
					self.current_text += key
				# If the key IS a backspace character, we remove the last character from the text
				else:
					self.current_text = self.current_text[:-1]

			# Displays the current text
			for i, line in enumerate(self.current_text.split("\n")):
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
		self.stdscr.addstr(self.rows - 2, 0, "▓" * self.cols)

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


if __name__ == "__main__":
	app = App()
	curses.wrapper(app.main)
