from typing import Callable

class Plugin:
	def __init__(self, cls):
		self.cls = cls

	def add_command(self, character:str, function:Callable, description:str):
		if len(character) != 1:
			raise Exception(f"Command character length must be one character, not {len(character)} ('{character}').")
		else:
			self.cls.commands.append((character, function, description))