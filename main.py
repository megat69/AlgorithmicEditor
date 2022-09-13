import curses
import sys


class App:
	def __init__(self):
		self.current_text = ""
		self.stdscr = None
		self.rows, self.cols = 0, 0


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
				if key != "\b":
					self.current_text += key
				# If the key IS a backspace character, we remove the last character from the text
				else:
					self.current_text = self.current_text[:-1]

			# Displays the current text
			self.stdscr.addstr(0, 0, self.current_text)

			# Visual stylings, e.g. adds a full line over the input
			self.apply_stylings()

			# Screen refresh after input
			self.stdscr.refresh()


	def quit(self):
		sys.exit(0)


	def apply_stylings(self):
		self.stdscr.addstr(self.rows - 2, 0, "▓" * self.cols)


if __name__ == "__main__":
	app = App()
	curses.wrapper(app.main)
