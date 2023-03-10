"""
Contains the Plugin base class, which allows developers to create their own plugins.
The Plugin class should be inherited from, rather than used as-is.
"""
from typing import Callable
import json

# Imports the main.py file. If another file is used as top-level import, the program will crash.
import __main__


class Plugin:
	def __init__(self, app: __main__.App):
		self.app: __main__.App = app  # An instance of the app
		self.plugin_name: str = ""  # The name of the plugin
		self.config: dict = {}  # The config data of the plugin
		self.translations: dict = {}  # The translations of your app

	def init(self):
		"""
		Called when loading the plugin.
		"""
		pass

	def update_on_syntax_highlight(self, line: str, splitted_line: list, i: int):
		"""
		Gets called every frame, right after the syntax highlighting of the current line is complete.
		Gets called n times each frame, where n is the amount of lines in the program.
		"""
		pass

	def update_on_keypress(self, key: str):
		"""
		Gets called right after the user presses a non-command/non-special key.
		:param key: The key pressed by the user.
		"""
		pass

	def update_on_compilation(self, final_compiled_code: str, compilation_type: str):
		"""
		Gets called at the end of a compilation.
		:param final_compiled_code: The compiled code.
		:param compilation_type: The language in which the code was compiled. Can be either "cpp" or "algo".
		"""
		pass


	def translate(self, *keys: str, language: str = None, **format_keys) -> str:
		"""
		Gives you the translation of the string found at the key with the given language.
		If language is None, the app's language will be used.
		:param keys: The keys to the translation.
		:param language: The language to be used to translate. If None (default), the app's language.
		:param format_keys: Parameters that would be used in the str.format() method.
		:return: The translated string.
		"""
		# Tries to reach the correct translation
		try:
			# Loads the translation in the given language
			string = self.translations[self.app.language if language is None else language]

			# Loads, key by key, the contents of the translation
			for key in keys:
				string = string[key]

		# If anything happens, we fall back to english.
		except KeyError:
			if language != "en":
				string = self.translate(*keys, language="en")
			else:
				raise KeyError(f"Translation for {keys} not found !")

		# We format the string based on the given format_keys
		if format_keys:
			string = string.format(**format_keys)

		# We return the given string
		return string


	def add_command(self, character: str, function: Callable, description: str, hidden: bool = False):
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

