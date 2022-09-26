from typing import Callable

class Plugin:
	def __init__(self, cls):
		self.cls = cls

	def init(self):
		"""
		Called when loading the plugin.
		"""
		pass

	def add_command(self, character:str, function:Callable, description:str):
		"""
		Adds a command to the app.
		:param character: The character triggering the command.
		:param function: The function called on command trigger.
		:param description: A very short description of the command shown to the user (less than 20 characters).
		"""
		if len(character) != 1:
			raise Exception(f"Command character length must be one character, not {len(character)} ('{character}').")
		else:
			self.cls.commands.append((character, function, description))