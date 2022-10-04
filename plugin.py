from typing import Callable
import json


class Plugin:
	def __init__(self, app):
		self.app = app

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
		:param character: The character triggering the command. It is highly recommended to make it no more than one character.
		:param function: The function called on command trigger.
		:param description: A very short description of the command shown to the user (less than 20 characters).
		:param hidden: Whether the command should be hidden (only displayed in the commands list, and not the bottom of
			the screen). False by default.
		"""
		# If a command with the same prefix exists, it replaces it
		self.app.commands[character] = (function, description, hidden)

