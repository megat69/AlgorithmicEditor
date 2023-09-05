"""
Contains the Plugin base class, which allows developers to create their own plugins.
The Plugin class should be inherited from, rather than used as-is.
"""
import curses
from typing import Callable, Type, Any

# Imports the main.py file. If another file is used as top-level import, the program will crash.
import __main__

if hasattr(__main__, "App"):
	AppType = Type[__main__.App]
else:
	AppType = Any

class Plugin:
	_next_pair_number = 10

	def __init__(self, app: AppType):
		self.app: __main__.App = app  # An instance of the app
		self.plugin_name: str = ""  # The name of the plugin
		self.config: dict = {}  # The config data of the plugin
		self.translations: dict = {}  # The translations of your app
		self.was_initialized: bool = False  # Whether the init() method was called. If True, will not call the method. If False, will turn to True upon call of init().

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

	def on_crash(self):
		"""
		Gets called in case of a crash. Lets the plugin do some work in order to save necessary or important data.
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


	def add_command(self, character: str, function: Callable[[], Any], description: str, hidden: bool = False):
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


	def add_option(self, name: str, current_value: Callable[[], Any], callback: Callable[[], Any]):
		"""
		Adds a new option to the app that the user can access from the options command.
		:param name: The name of the config option (preferably translated), as indicative as possible.
		:param current_value: A callback function returning the current value of the config option, generally a lambda.
		:param callback: A function to be called when the user chooses to change the config for the new option.
		"""
		# If a command with the same prefix exists, it replaces it
		self.app.options_list.append((name, current_value, callback))


	def create_pair(self, fg: int, bg: int) -> int:
		"""
		Creates a new color pair with the given colors, and returns its ID.
		:param fg: A curses color.
		:param bg: A curses color.
		:return: The ID of the color pair.
		"""
		curses.init_pair(Plugin._next_pair_number, fg, bg)
		Plugin._next_pair_number += 1
		return Plugin._next_pair_number - 1


	def get_config(self, key: str, default: Any) -> Any:
		"""
		Returns the element of the config at the given key. If 'key' does not exist in config, sets the value of 'key' to the given 'default' and returns 'default'.
		:param key: The key of the config element you want to get.
		:param default: The value to assign to 'key' and return if 'key' is not in the config.
		:return: The value of the config at the given key, or the value of 'default' if 'key' is not in the config.
		"""
		if key not in self.config:
			self.config[key] = default
		return self.config[key]

