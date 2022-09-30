from typing import Callable


class Plugin:
	def __init__(self, app):
		self.app = app
		self.created_commands = {}

	def init(self):
		"""
		Called when loading the plugin.
		"""
		pass

	def update_on_syntax_highlight(self, line:str, splitted_line:list, i:int):
		"""
		Gets called every frame, right after the syntax highlighting of the current line is complete.
		Gets called n times each frame, where n is the amount of lines in the program.
		"""
		pass

	def update_on_keypress(self, key:str):
		"""
		Gets called right after the user presses a non-command/non-special key.
		:param key: The key pressed by the user.
		"""
		pass

	def update_on_compilation(self, final_compiled_code:str, compilation_type:str):
		"""
		Gets called at the end of a compilation.
		:param final_compiled_code: The compiled code.
		:param compilation_type: The language in which the code was compiled. Can be either "cpp" or "algo".
		"""
		pass

	def add_command(self, character:str, function:Callable, description:str, hidden:bool = False):
		"""
		Adds a command to the app.
		:param character: The character triggering the command.
		:param function: The function called on command trigger.
		:param description: A very short description of the command shown to the user (less than 20 characters).
		"""
		if len(character) != 1:
			raise Exception(f"Command character length must be one character, not {len(character)} ('{character}').")
		else:
			# If a command with the same prefix exists, and if so, replaces it
			self.app.commands[character] = (function, description, hidden)

