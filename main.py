import curses, _curses
import string
import sys
import pyperclip
from functools import partial
import os
import importlib
import json
from typing import Union, Optional, Callable, Any
from configparser import ConfigParser
from collections import deque
from traceback import print_exception
import re

from algorithmic_compiler import AlgorithmicCompiler
from cpp_compiler import CppCompiler
from utils import display_menu, input_text, get_screen_middle_coords, browse_files


# Constants
CRASH_FILE_NAME = ".crash"


class App:
	__singleton = None


	def __new__(cls, *args, **kwargs):
		"""
		Creates a singleton of the class.
		"""
		if cls.__singleton is None:
			cls.__singleton = super().__new__(cls)
		return cls.__singleton


	def __init__(self):
		# Loads the config
		with open("plugins_config.json", "r", encoding="utf-8") as f:
			self.plugins_config = json.load(f)  # The configuration of the plugins

		# Loads the translations
		self.translations = {}  # Contains all the translations in all the translation files
		self.language = self.plugins_config["BASE_CONFIG"]["language"]  # Contains the language code of the chosen language (e.g. 'en' or 'fr').
		for translation_file in os.listdir("translations/"):
			with open(f"translations/{translation_file}", "r", encoding="utf8") as f:
				# Loads the translations as dictionaries,
				# e.g. translation_file = 'translations_en.json', self.translations['en'] = {...}
				self.translations[translation_file[13:15]] = json.load(f)

		self.current_text = ""  # The text being displayed in the window
		self.stdscr: Optional[_curses.window] = None  # The standard screen (see curses library)
		self.rows, self.cols = 0, 0  # The number of rows and columns in the window
		self.lines = 1  # The number of lines containing text in the window
		self.current_index = 0  # The current index of the cursor
		self.command_symbol = ":"  # The symbol triggering a command
		self.commands = {
			"q": (self.quit, self.get_translation("commands", "q"), False),
			"q!": (partial(self.quit, True), self.get_translation("commands", "q!"), True),
			"qs!": (partial(self.quit, True, True), self.get_translation("commands", "qs!"), True),
			"s": (self.save, self.get_translation("commands", "s"), False),
			"qs": (partial(self.save, quick_save=True), self.get_translation("commands", "qs"), False),
			"o": (self.open, self.get_translation("commands", "o"), False),
			"c": (self.compile, self.get_translation("commands", "c"), False),
			"p": (self.compile_to_cpp, self.get_translation("commands", "p"), False),
			"op": (self.options, self.get_translation("commands", "op"), False),
			"h": (self.display_commands, self.get_translation("commands", "h"), False),
			"z": (self.undo, self.get_translation("commands", "z"), False),
			"a": (self.repeat_last_command, self.get_translation("commands", "a"), False),
			# "t": (self.modify_tab_char, self.get_translation("commands", "t"), True),
			# "j": (self.toggle_std_use, self.get_translation("commands", "j"), True),
			# "st": (self.toggle_struct_use, self.get_translation("commands", "st"), True),
			"cl": (self.clear_text, self.get_translation("commands", "cl"), True),
			"is": (self.insert_text, self.get_translation("commands", "is"), True),
			"rlt": (self.reload_theme, self.get_translation("commands", "rlt"), True),
			"m": (self.mark_line, self.get_translation("commands", "m"), True),
			# To add the command symbol to the text
			self.command_symbol: (partial(self.add_char_to_text, self.command_symbol), self.command_symbol, True)
		}  # A dictionary of all the commands, either built-in or plugin-defined.
		self.last_used_command: Optional[str] = None  # The prefix of the last command used
		self.instructions_list = []  # The list of instructions for compilation, is only used by the compilation functions
		self.tab_char = "\t"  # The tab character
		self.using_namespace_std = False  # Whether to use the std namespace during the C++ compilation
		self.use_struct_keyword = False  # Whether to use the struct keyword in the functions' return type during the C++ compilation
		self.logs = True  # Whether to log
		self.min_display_line = 0  # The minimum line displayed on the window (scroll)
		self.cur = tuple()  # The cursor
		self.min_display_char = 0  # Useless at the moment
		self.last_save_action = "clipboard"  # What the user did the last time he saved some code from the editor ; can be 'clipboard' or the pah to a file.
		self.compilers = {}  # A dictionary of compilers for the editor
		self.undo_actions = deque([], maxlen=21)  # All the actions that can be used to undo
		self.is_crash_reboot = False  # Whether the editor has been rebooted from a crash. Can only be used through a plugin's init() method, will always be False otherwise.
		self.marked_lines = []  # Which lines are currently marked by the user
		self.left_placement_shift = 0  # By how many columns the line numbers should be shifted to the right
		self.top_placement_shift = 0  # By how many lines the top of the code should be shifted from the top
		self.input_locked = False  # If True, will disable all keyboard input except for commands and plugins

		# Changes the class variable of browse_files to be the config's class variable
		if self.plugins_config["BASE_CONFIG"]["default_save_location"] != "":
			browse_files.last_browsed_path = self.plugins_config["BASE_CONFIG"]["default_save_location"]
		else:
			browse_files.last_browsed_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../"))

		# Changes the namespace std use based on its setting last time
		if "using_namespace_std" in self.plugins_config["BASE_CONFIG"].keys():
			self.using_namespace_std = self.plugins_config["BASE_CONFIG"]["using_namespace_std"]
		else:
			self.plugins_config["BASE_CONFIG"]["using_namespace_std"] = False

		# Changes the namespace std use based on its setting last time
		if "use_struct_keyword" in self.plugins_config["BASE_CONFIG"].keys():
			self.use_struct_keyword = self.plugins_config["BASE_CONFIG"]["use_struct_keyword"]
		else:
			self.plugins_config["BASE_CONFIG"]["use_struct_keyword"] = False

		# Changes the tab character based on its setting last time
		if "tab_char" in self.plugins_config["BASE_CONFIG"].keys():
			self.tab_char = self.plugins_config["BASE_CONFIG"]["tab_char"]
		else:
			self.plugins_config["BASE_CONFIG"]["tab_char"] = self.tab_char

		# Creates a maximum length for the queue of the undo actions based on the config
		if "max_undo_size" in self.plugins_config["BASE_CONFIG"].keys():
			self.undo_actions = deque([], maxlen=self.plugins_config["BASE_CONFIG"]["max_undo_size"] + 1)
		else:
			self.plugins_config["BASE_CONFIG"]["max_undo_size"] = self.undo_actions.maxlen - 1

		# Generates the list of options the user has access to
		self.options_list = [
			(self.get_translation('commands', 'std_use'), lambda: self.using_namespace_std, self.toggle_std_use),
			(self.get_translation('commands', 'struct_use'), lambda: self.use_struct_keyword, self.use_struct_keyword),
			(self.get_translation('commands', 'modify_tab_char'), lambda: repr(self.tab_char), self.modify_tab_char),
			(self.get_translation('language', 'language'), lambda: self.language, self.change_language),
			(self.get_translation('change_max_undo_size', 'max_undo'),
			 lambda: self.plugins_config['BASE_CONFIG']['max_undo_size'], self.change_max_undo_size),
		]  # The list of options the user has access to ; Follows the scheme <name> <current_state> <callback_trigger>


		# Getting the theme
		self._theme_parser = ConfigParser()
		self._theme_parser.read("theme.ini")

		# Preparing the color pairs
		self.color_pairs = {
			pair_name: self._theme_parser["PAIRS"].getint(pair_name, fallback_value)
			for pair_name, fallback_value in (
				("statement", 1),
				("function", 2),
				("variable", 3),
				("instruction", 4),
				("strings", 3),
				("special_string", 5)
			)
		}  # The number of the color pairs
		self.color_control_flow = {
			"statement": ("if", "else", "end", "elif", "for", "while", "switch", "case", "default", "const"),
			"function": ("fx", "fx_start", "return", "CODE_RETOUR", "struct"),
			"variable": ('int', 'float', 'string', 'bool', 'char'),
			"instruction": ("print", "input", "arr", "init")
		}  # What each type of statement corresponds to
		self.theme_scheme = self._theme_parser["SCHEME"].get("scheme", "DARK")
		self.default_bg = curses.COLOR_BLACK
		self.default_fg = curses.COLOR_WHITE

		# Loads all the plugins
		self.plugins = self.load_plugins()  # A dict containing all the plugins as list of [module, instance]


	def main(self, stdscr: _curses.window):
		"""
		The main function, wrapped around by curses.
		"""
		# Curses initialization
		self.stdscr: _curses.window = stdscr
		self.stdscr.clear()
		self.rows, self.cols = self.stdscr.getmaxyx()

		# If a .crash file exists, we show a message asking if they want their data to be recovered,
		# then we set current_text to its contents and delete it
		if CRASH_FILE_NAME in os.listdir(os.path.dirname(__file__)) and "--file" not in sys.argv:
			self._on_crash_recover()

		# Declaring the color pairs
		self._declare_color_pairs()

		# Initializes the compilers
		self._load_compilers()

		# Initializes each plugin, if they have an init function
		self._init_plugins()

		# If the app had not previously crashed, we display the welcome page
		if self.is_crash_reboot is False:
			self.show_welcome_page()

		# Displays the text
		self.display_text()
		self.apply_stylings()
		self.stdscr.refresh()

		# App main loop
		while True:
			# Gets the current screen size
			self.rows, self.cols = self.stdscr.getmaxyx()

			# Key input
			key = self.stdscr.getkey()

			# If the undo is full, dumping the earliest element of queue
			if len(self.undo_actions) == self.undo_actions.maxlen:
				self.undo_actions.popleft()

			# If system key is pressed
			if key == self.command_symbol:
				self.handle_command_key()

			# If it is a regular key
			else:
				# Screen clearing
				self.stdscr.clear()

				# Handles the input as regular keys
				if not self.input_locked:
					self.handle_regular_key(key)

				# Calls the plugins update_on_keypress function
				for plugin in self.plugins.values():
					if hasattr(plugin[1], "update_on_keypress"):
						plugin[1].update_on_keypress(key)

				# Clamping the index
				self.current_index = max(min(self.current_index, len(self.current_text)), 0)

			# Displays the current text
			# TODO Longer lines
			self.display_text()

			# Visual stylings, e.g. adds a full line over the input
			self.apply_stylings()

			# Screen refresh after input
			self.stdscr.refresh()


	def handle_regular_key(self, key: str):
		"""
		Handles the regular input.
		:param key: The key pressed by the user.
		"""
		# If the key IS a backspace character, we remove the last character from the text
		if key in ("\b", "\0") or key.startswith("KEY_") or key.startswith("CTL_") or len(key) != 1:
			if key in ("KEY_BACKSPACE", "\b", "\0"):
				if self.current_index > 0:
					# Makes the action undoable
					self.undo_actions.append(
						{
							"action_type": "removed_char",
							"char": self.current_text[self.current_index - 1],
							"index": self.current_index - 1,
							"adder": 0
						}
					)
					# Removes the character from the text
					self.current_text = self.current_text[:self.current_index - 1] + self.current_text[
					                                                                 self.current_index:]
					self.current_index -= 1
			elif key == "KEY_DC":  # Delete key
				if self.current_index < len(self.current_text):
					# Makes the action undoable
					self.undo_actions.append(
						{
							"action_type": "removed_char",
							"char": self.current_text[self.current_index],
							"index": self.current_index,
							"adder": 0
						}
					)
					# Removes the character from the text
					self.current_text = self.current_text[:self.current_index] + self.current_text[
					                                                             self.current_index + 1:]
			elif key in ("KEY_UP", "KEY_DOWN"):
				text = self.current_text + "\n"
				indexes = tuple(index for index in range(len(text)) if text.startswith('\n', index))
				closest_index = min(indexes, key=lambda x: abs(x - self.current_index))
				closest_index = indexes.index(closest_index)
				closest_index = closest_index + (-1) ** (key == "KEY_UP")
				try:
					if closest_index <= 0:
						if "\n" in self.current_text:
							self.current_index = self.current_text.index("\n")
						else:
							self.current_index = len(self.current_text)
					else:
						self.current_index = indexes[closest_index]
				except IndexError:
					pass
			elif key == "KEY_LEFT":
				self.current_index -= 1
			elif key == "KEY_RIGHT":
				self.current_index += 1
			elif key == "CTL_LEFT":
				self.current_index -= 1
				while self.current_index >= 0 and self.current_text[self.current_index] in string.ascii_letters:
					self.current_index -= 1
			elif key == "CTL_RIGHT":
				self.current_index += 1
				while self.current_index < len(self.current_text) and self.current_text[
					self.current_index] in string.ascii_letters:
					self.current_index += 1
			elif key == "KEY_NPAGE":
				self.min_display_line -= 1
				if self.min_display_line < 0:
					self.min_display_line = 0
			elif key == "KEY_PPAGE":
				self.min_display_line += 1
				if self.min_display_line > self.lines - 1:
					self.min_display_line = self.lines - 1
			elif key == "KEY_F(1)":
				self.commands["h"][0]()
			elif key == "KEY_F(4)":
				self.commands["q"][0]()
			elif key == "KEY_SEND":  # The key used to type '<', for some reason
				self.add_char_to_text("<")
			elif key == "CTL_END":  # The key used to type '>', for some reason
				self.add_char_to_text(">")
			elif key == "SHF_PADSLASH":  # The key used to type '!', for some reason
				self.add_char_to_text("!")
			"""elif key == "KEY_HOME":
				self.min_display_char -= 1
				if self.min_display_char < 0:
					self.min_display_char = 0
			elif key == "KEY_END":
				self.min_display_char += 1"""
		else:
			# If the key is NOT a backspace character, we add the new character to the text
			self.add_char_to_text(key)


	def handle_command_key(self):
		"""
		Handles a command.
		"""
		# Writes the command symbol to the command area row
		self.stdscr.addstr(self.rows - 1, 0, self.command_symbol)
		# Awaits the user's full command
		key = input_text(self.stdscr, 1, self.rows - 1)
		# Gets the repeat count (e.g. ":5z" will repeat ":z" 5 times)
		repeat_count = 1
		if key != "" and key[0].isdigit():
			# Finds the number before the command
			repeat_count_str = re.search(r'\d+', key).group()
			repeat_count = int(repeat_count_str)

			# Removes the number from the command name so we can actually find the correct command
			key = key[len(repeat_count_str):]
		# If the command exists
		if key in self.commands.keys():
			# We get the command information
			key_name, (function, name, hidden) = key, self.commands[key]

			# We add the full command name to the command area row
			self.stdscr.addstr(self.rows - 1, 1, key_name)

			# We launch the command as many times as needed
			for _ in range(repeat_count):
				self.execute_command(function, key)

		# Add a few spaces to clear the command name
		self.stdscr.addstr(self.rows - 1, 0, " " * 4)


	def execute_command(self, function: Callable[[], Any], key: str):
		"""
		Executes the given command.
		:param function: A function to call (a command).
		:param key: The prefix of the command.
		"""
		try:
			# Remembering the current state of the text so the command can be undone
			# However, not doing this if this is the undo command
			if key != "z":
				self.undo_actions.append(
					{
						"action_type": "command",
						"current_text": self.current_text,
						"current_index": self.current_index
					}
				)

			# Actually launching the command
			function()

			# Keeps in mind the key used as being the last command
			if key != "a":
				self.last_used_command = key

		# If a curses error happens, we warn the user and log the error
		except curses.error as e:
			self.stdscr.addstr(self.rows - 1, 5, self.get_translation("errors", "unknown"))
			self.log(e)
			print_exception(e)
			# We also undo the action just in case
			if key != "z":
				self.undo()


	def _init_plugins(self):
		"""
		Inits once every plugin that was loaded.
		"""
		msg_string = self.get_translation("loaded_plugin", plugin_name="{}")
		for i, (plugin_name, plugin) in enumerate(self.plugins.items()):
			if hasattr(plugin[1], "init"):
				if not plugin[1].was_initialized:
					plugin[1].init()
					plugin[1].was_initialized = True
			# Writes a message to the screen showing all imported plugins
			self.stdscr.addstr(
				self.rows - 4 - i,
				self.cols - (len(msg_string.format(plugin_name)) + 2),
				msg_string.format(plugin_name)
			)
			# Highlights the plugin name
			self.stdscr.addstr(
				self.rows - 4 - i,
				self.cols - (len(msg_string.format(plugin_name)) - msg_string.find("{") + 2),
				plugin_name,
				curses.color_pair(self.color_pairs["instruction"])
			)
		msg_string = self.get_translation("loaded_n_plugins")
		self.stdscr.addstr(
			self.rows - 4 - len(self.plugins.keys()),
			self.cols - (len(msg_string.format(len(self.plugins.keys()))) + 2),
			msg_string.format(len(self.plugins.keys())), curses.color_pair(3)
		)

	def _load_compilers(self):
		"""
		Loads the base compilers.
		"""
		self.compilers["algorithmic"] = AlgorithmicCompiler(
			{
				"for": "Pour",
				"if": "Si",
				"while": "Tant Que",
				"switch": "Selon",
				"arr": "Tableau",
				"case": "Cas",
				"default": "Autrement",
				"fx": "Fonction",
				"proc": "Procédure",
				"const": "Constante"
			},
			{
				"int": "Entier",
				"float": "Réel",
				"string": "Chaîne de caractères",
				"bool": "Booléen",
				"char": "Caractère"
			},
			["print", "input", "end", "elif", "else", "fx_start", "vars", "precond", "data", "datar", "result",
			 "return", "desc", "CODE_RETOUR", "init", "struct", "const"],
			self.stdscr,
			self.translations,
			self.get_translation,
			self.tab_char
		)
		self.compilers["C++"] = CppCompiler(
			('for', 'if', 'while', 'switch', 'arr', 'case', 'default', 'fx', 'proc', 'struct'),
			{
				"int": "int",
				"float": "float",
				"string": "std::string",
				"bool": "bool",
				"char": "char"
			},
			["print", "input", "end", "elif", "else", "fx_start", "vars", "precond", "data", "datar", "result",
			 "return", "desc", "CODE_RETOUR", "init", "const"],
			self.stdscr,
			self
		)

	def _on_crash_recover(self):
		"""
		If a crash file exists, asks the user if they want to recover.
		"""
		def recover_crash_data():
			with open(os.path.join(os.path.dirname(__file__), CRASH_FILE_NAME), "r", encoding="utf-8") as f:
				self.current_text = f.read()
			self.display_text()
			self.is_crash_reboot = True

		display_menu(
			self.stdscr,
			(
				("Yes", recover_crash_data),
				("No", lambda: None)
			),
			label=self.get_translation("crash_recovery"),
			clear=False
		)
		os.remove(os.path.join(os.path.dirname(__file__), CRASH_FILE_NAME))


	def _declare_color_pairs(self):
		"""
		Declares all the curses color pairs based on the theme.
		"""
		# Sets the default colors
		if hasattr(curses, f"COLOR_{self._theme_parser['SCHEME'].get('default_bg', 'BLACK')}"):
			self.default_bg = getattr(curses, f"COLOR_{self._theme_parser['SCHEME'].get('default_bg', 'BLACK')}")
		else:
			self.default_bg = curses.COLOR_BLACK
		if hasattr(curses, f"COLOR_{self._theme_parser['SCHEME'].get('default_fg', 'WHITE')}"):
			self.default_fg = getattr(curses, f"COLOR_{self._theme_parser['SCHEME'].get('default_fg', 'WHITE')}")
		else:
			self.default_fg = curses.COLOR_WHITE
		curses.init_pair(255, self.default_fg, self.default_bg)
		self.stdscr.attron(curses.color_pair(255))

		# Fetches all the possible color pair numbers in the theme
		for i in range(1, 9):
			# Finds each pair of colors in the theme
			current_pair = self._theme_parser["COLORS"].get(f"pair_{i}")

			# If the current pair is defined in the theme
			if current_pair is not None:
				# We turn it into an actual pair by separating the values on the comma
				current_pair = current_pair.split(",")

				# We check that this is indeed a pair, otherwise raise an error
				if len(current_pair) != 2:
					raise KeyError(self.get_translation(
						"errors", "color_pair_creation_error", i=i, current_pair=current_pair
					))

				# Then we sanitize the values by stripping them from whitespaces and putting them in uppercase
				for j in range(2):
					current_pair[j] = current_pair[j].strip().upper()

					# If it is the default color, we define it as such
					if current_pair[j].lower().startswith("def"):
						if j == 0:  # Foreground
							current_pair[j] = self._theme_parser['SCHEME'].get('default_fg', 'WHITE')
						if j == 1:  # Background
							current_pair[j] = self._theme_parser['SCHEME'].get('default_bg', 'BLACK')

					# We also check if this color exists in curses, and otherwise raise an exception
					elif not hasattr(curses, f"COLOR_{current_pair[j]}"):
						raise KeyError(self.get_translation(
							"errors", "not_curses_color",
							i=i, color=j, current_pair_element=current_pair[j]
						))

				# We then initialize the pair by finding the corresponding curses color
				curses.init_pair(
					i,
					getattr(curses, f"COLOR_{current_pair[0]}"),
					getattr(curses, f"COLOR_{current_pair[1]}")
				)

		# Sets the background color
		self.stdscr.bkgd(' ', curses.color_pair(255))


	def get_translation(self, *keys: str, language: str = None, **format_keys) -> str:
		"""
		Returns the translation of the given string.
		:param keys: Every key, in order, towards the translation.
		:param language: The language in which to translate in. If None (by default), the value of self.language is used.
		:param format_keys: Parameters that would be used in the str.format() method.
		:return: The translation.
		"""
		# Tries to reach the correct translation
		try:
			# Loads the translation in the given language
			string = self.translations[self.language if language is None else language]

			# Loads, key by key, the contents of the translation
			for key in keys:
				string = string[key]

		# If anything happens, we fall back to english.
		except KeyError:
			if language != "en":
				string = self.get_translation(*keys, language="en")
			else:
				raise KeyError(f"Translation for {keys} not found !")


		# We format the string based on the given format_keys
		if format_keys:
			string = string.format(**format_keys)

		# We return the given string
		return string


	def undo(self):
		"""
		Undoes the last action.
		"""
		# Checks if there are actions that can be undone, otherwise just leaves there
		if len(self.undo_actions) == 0: return None

		# Looks at the last action while removing it from the queue
		last_action = self.undo_actions.pop()

		# Remembers if an action was undone for later
		undone_action = False

		# If the last action is a character addition
		if last_action["action_type"] == "added_char":
			self.current_text = self.current_text[:last_action["index"]] + \
									self.current_text[last_action["index"] + len(last_action["char"]):]
			# Also refreshes the screen
			undone_action = True

		# If the last action was to remove a character, we add it back
		elif last_action["action_type"] == "removed_char":
			# Inserting the character back into the text
			current_text = list(self.current_text)
			current_text.insert(
				last_action["index"], last_action["char"]
			)
			current_text = "".join(current_text)
			self.current_text = current_text

			# Putting the cursor back to where the character was
			self.current_index = last_action["index"] + last_action["adder"]

			# Refreshes the screen
			undone_action = True

		# If the last action was a command launch
		elif last_action["action_type"] == "command":
			# Resetting the current text and current index
			self.current_text = last_action["current_text"]
			self.current_index = last_action["current_index"]

			# Refreshes the screen
			undone_action = True

		# If unknown, logs the action and recursively calls the function
		else:
			self.log(f"Unknown action : {last_action}")
			# Tries to undo another action
			self.undo()

		# Refreshes the screen
		if undone_action:
			self.stdscr.clear()
			self.display_text()


	def quit(self, force_quit: bool = False, auto_quicksave: bool = False) -> None:
		"""
		Exits the app.
		:param force_quit: If set to True, will automatically quit without saving. Default is False.
		:param auto_quicksave: If set to True, will automatically quicksave. Default is False.
		"""
		def quit():
			# Saves the plugin config, after saving the base config
			if self.plugins_config["BASE_CONFIG"]["default_save_location"] != "":
				self.plugins_config["BASE_CONFIG"]["default_save_location"] = browse_files.last_browsed_path
			with open("plugins_config.json", "w", encoding="utf-8") as f:
				json.dump(self.plugins_config, f, indent=2)

			# Exits the app
			sys.exit(0)
		def save_and_quit():
			self.save()
			quit()
		def cancel():
			pass


		# If we have been asked to, we quicksave
		if auto_quicksave:
			self.save(quick_save=True)


		# Provides the option to save and quit, quit without saving, or cancel quitting.
		if force_quit is False:
			display_menu(
				self.stdscr,
				(
					(self.get_translation("quit", "quit_without_save"), quit),
					(self.get_translation("quit", "save_and_quit"), save_and_quit),
					(self.get_translation("quit", "cancel"), cancel)
				),
				1, self.get_translation("quit", "quit_message"),
				space_out_last_option = True
			)

		# If we have been asked to force quit, we just quit without asking the user
		else:
			quit()


	def get_lineno_length(self) -> int:
		"""
		Returns the space taken by the line numbers?
		"""
		return len(str(self.lines)) + 1 + self.left_placement_shift


	def display_text(self):
		"""
		Displays the text in current_text.
		"""
		# Calculates the size of the line numbers
		self.calculate_line_numbers()

		# Gets the position of the cursor on the window
		self.cur = (
			self.current_text[:self.current_index].count('\n') - self.min_display_line + self.top_placement_shift,
			self.current_index - (self.current_text[:self.current_index].rfind('\n')) + self.get_lineno_length() - 1,
			self.current_text[self.current_index]
				if
					self.current_index < len(self.current_text)  # If the current index is after the end of the text
					and self.current_text[self.current_index].isprintable()  # Or if the character is not printable
				else
			" "
		)
		for i, line in enumerate(
				self.current_text.split("\n")[self.min_display_line:self.min_display_line + (self.rows - 3) - self.top_placement_shift]
		):
			line = line[self.min_display_char:]
			# Getting the splitted line for syntax highlighting
			splitted_line = line.split(" ")

			# Writing the line to the screen
			if self.get_lineno_length() + len(line) < self.cols - self.left_placement_shift - 1:  # -1 is for the scrollbar
				# If the line's length does not overflow off the screen, we write it entirely
				self.stdscr.addstr(i + self.top_placement_shift, self.get_lineno_length(), line)
			else:
				# If the line's length overflows off the screen, we write only the part that stays in the screen
				self.stdscr.addstr(i + self.top_placement_shift, self.get_lineno_length(), line[:self.cols - self.get_lineno_length() - self.left_placement_shift])

			# Tests the beginning of the line to add a color, syntax highlighting
			self.syntax_highlighting(line, splitted_line, i)

			# Calls the plugins update_on_syntax_highlight function
			for plugin_name, plugin in tuple(self.plugins.items()):
				if len(plugin) > 1:
					if hasattr(plugin[1], "update_on_syntax_highlight"):
						plugin[1].update_on_syntax_highlight(line, splitted_line, i)
				else:
					del self.plugins[plugin_name]

		# Placing cursor
		if 0 <= self.cur[1] < self.cols and 0 <= self.cur[0] < self.rows - 3:
			try:
				self.stdscr.addstr(*self.cur, curses.A_REVERSE)
			except curses.error:
				pass


	def apply_stylings(self) -> None:
		"""
		Apply all the stylings to the screen.
		"""
		# Applies the bar at the bottom of the screen
		try:
			self.stdscr.addstr(self.rows - 3, 0, "▓" * self.cols)
		except curses.error: pass

		# Adds the commands list at the bottom of the screen
		self.display_commands_list()

		# Calculates the scrollbar
		self.calculate_scrollbar()

		# Gets the amount of lines in the text
		self.calculate_line_numbers()
		# Puts the line numbers at the edge of the screen
		for i in range(self.min_display_line, min(self.lines, self.min_display_line + (self.rows - 3) - self.top_placement_shift)):
			style = curses.A_REVERSE
			if i in self.marked_lines:  # Gives the line a different color if it marked
				style |= curses.color_pair(self.color_pairs["statement"])
			self.stdscr.addstr(i - self.min_display_line + self.top_placement_shift, self.left_placement_shift, str(i + 1).zfill(len(str(self.lines))), style)

		self.stdscr.refresh()


	def calculate_scrollbar(self):
		"""
		Calculate and display the scrollbar.
		"""
		total_lines_of_code = self.current_text.count("\n")
		scrollbar_max_height = self.rows - 3 - self.top_placement_shift
		if total_lines_of_code > scrollbar_max_height:
			scrollbar_height = int(scrollbar_max_height / total_lines_of_code * scrollbar_max_height)
			scrollbar_pos = self.top_placement_shift + int(
				self.min_display_line / total_lines_of_code * scrollbar_max_height)
			for i in range(scrollbar_height):
				if scrollbar_pos + i < self.rows - 3:
					self.stdscr.addstr(
						scrollbar_pos + i,
						self.cols - 1,
						" ",
						curses.A_REVERSE
					)

	def display_commands_list(self):
		"""
		Displays the list of commands at the bottom of the window.
		"""
		cols = 0
		for key_name, (function, name, hidden) in self.commands.items():
			if key_name != self.command_symbol and hidden is False:
				generated_str = f"{self.command_symbol}{key_name} - {name}"

				# If printing this text would overflow off the screen, we break out of the loop
				if cols + len(generated_str) >= self.cols - 4:
					try:
						self.stdscr.addstr(self.rows - 2, cols, "...", curses.A_REVERSE)
					except curses.error:
						pass
					# We also display "..." beforehand.
					break

				try:
					# Adds the generated string at the right place of the screen
					self.stdscr.addstr(self.rows - 2, cols, generated_str, curses.A_REVERSE)
					# Keeping in mind the x coordinates of the next generated string
					cols += len(generated_str)
					# Followed by a space
					self.stdscr.addstr(self.rows - 2, cols, " ")
				except curses.error:
					self.log(f"Could not display command {self.command_symbol}{key_name} - {name}")
				cols += 1

			# Adds a spacing between built-in and plugin commands
			elif key_name == self.command_symbol:
				cols += 3

	def reload_theme(self):
		"""
		Reloads the theme.
		"""
		self._theme_parser.read("theme.ini")
		self.color_pairs = {
			pair_name: self._theme_parser["PAIRS"].getint(pair_name, fallback_value)
			for pair_name, fallback_value in self.color_pairs.items()
		}
		self._declare_color_pairs()
		# Adds a message at the bottom to warn the theme was reloaded
		self.stdscr.addstr(self.rows - 1, 4, self.get_translation("theme_reloaded"))


	def load_plugins(self):
		"""
		Loads all the plugins.
		"""
		from plugin import Plugin  # Note : A bit dirty to put an import here, but required for it to work
		# Creating the plugins folder if it does not exist
		if not os.path.exists(os.path.join(os.path.dirname(__file__), "plugins")):
			os.mkdir(os.path.join(os.path.dirname(__file__), "plugins"))

		# Initializing the plugins var
		plugins = {}

		# Lists all the plugin files inside the plugins folder
		for plugin in os.listdir(os.path.join(os.path.dirname(__file__), "plugins")):
			if plugin.startswith("__") or os.path.isdir(os.path.join(os.path.dirname(__file__), "plugins", plugin)) \
					or not plugin.endswith(".py"):
				continue  # Python folders/files

			# Cleaning the name
			plugin = plugin.replace(".py", "")

			# Importing the plugin and storing it in the variable
			try:
				plugins[plugin] = [importlib.import_module(f"plugins.{plugin}")]
			except Exception as e:
				self.log(f"Failed to load plugin {plugin} :\n{e}")
				continue

			# Initializes the plugins init function
			try:
				# Appends a new plugin to the list of plugins, by initializing the given plugin
				plugins[plugin].append(plugins[plugin][0].init(self))
				# Checks if we correctly received a plugin
				if not isinstance(plugins[plugin][-1], Plugin):
					raise TypeError(f"Plugin '{plugin}' init method did not return a Plugin subclass.")
				# Stores the plugin name
				plugins[plugin][-1].plugin_name = plugin
				# If the plugin does not have a config, creates one
				if plugin not in self.plugins_config.keys():
					self.plugins_config[plugin] = {}
				# Grants the plugin its config
				plugins[plugin][-1].config = self.plugins_config[plugin]

			# If an error occurred during plugin loading, we unimport the plugin and log the error
			except Exception as e:
				del plugins[plugin]
				self.log(f"An error occurred while importing the plugin '{plugin}' :\n{e}")

		# Returning the dict of plugins
		return plugins


	def calculate_line_numbers(self) -> int:
		"""
		Calculates the amount of lines in the text.
		Saves it into the correct variable and returns it.
		"""
		self.lines = self.current_text.count("\n") + 1
		return self.lines


	def modify_tab_char(self) -> None:
		"""
		Modifies the tab character.
		"""
		self.tab_char = input_text(self.stdscr, position_x=3)
		self.plugins_config["BASE_CONFIG"]["tab_char"] = self.tab_char


	def clear_text(self):
		"""
		Clears the current text in the editor.
		"""
		def _clear_text():
			self.current_text = ""
			self.current_index = 0

		display_menu(self.stdscr, (
			(self.get_translation("yes"), _clear_text),
			(self.get_translation("no"), lambda: None)
		),
		             label=self.get_translation("editor_clear_confirm"))


	def insert_text(self):
		"""
		Inserts the text from the given file into the editor
		"""
		filename = browse_files(self.stdscr, can_create_files=False)()
		if filename != "":
			with open(filename, "r", encoding="utf-8") as f:
				self.add_char_to_text(f.read())


	def add_char_to_text(self, key: str):
		"""
		Adds the given character at the end of the text.
		:param key: A character to add to the text.
		"""
		# Remembers the action as an undoable action
		self.undo_actions.append(
			{
				"action_type": "added_char",
				"char": key,
				"index": self.current_index
			}
		)

		# Adds the given character to the text
		self.current_text = self.current_text[:self.current_index] + key + self.current_text[self.current_index:]
		self.current_index += len(key)


	def display_commands(self):
		"""
		Displays all the commands at the center of the screen.
		"""
		# Gets the middle screen coordinates
		middle_y, middle_x = get_screen_middle_coords(self.stdscr)

		# Creates the label
		generated_str = f"----- {self.get_translation('commands_list', 'commands_list')} -----"
		self.stdscr.addstr(
			middle_y - len(self.commands) // 2 - 1,
			middle_x - len(generated_str) // 2,
			generated_str, curses.color_pair(1) | curses.A_REVERSE
		)

		# Remembering whether we're into the plugins section
		in_plugins_section = False

		# Displays each command
		for i, (key_name, (function, name, hidden)) in enumerate(self.commands.items()):
			if key_name != self.command_symbol:
				generated_str = f"{self.command_symbol}{key_name} - {name}"
			else:
				generated_str = f"---- {self.get_translation('commands_list', 'plugin_commands')} : ----"
				in_plugins_section = True

			self.stdscr.addstr(
				(middle_y - len(self.commands) // 2 + i + in_plugins_section) % (self.rows - 3),
				middle_x - len(generated_str) // 2,
				generated_str, (curses.A_REVERSE if i % 2 == 0 else curses.A_NORMAL) \
					if key_name != self.command_symbol else curses.color_pair(1) | curses.A_REVERSE
			)

			if middle_y - len(self.commands) // 2 + i + in_plugins_section == self.rows - 4:
				self.stdscr.getch()
				self.stdscr.clear()

		self.stdscr.getch()
		self.stdscr.clear()


	def syntax_highlighting(self, line, splitted_line, i):
		"""
		Creates a syntax highlighting for the given line.
		:param line: The line to use for parsing.
		:param splitted_line: A split version of the line (split on spaces)
		:param i: The index of the line in the window.
		"""
		# Caches the amount of needed spaces on the left side of the screen
		minlen = self.get_lineno_length()
		mintop = i + self.top_placement_shift

		# Colors the statement
		start_statement = splitted_line[0]
		if start_statement in tuple(sum(self.color_control_flow.values(), tuple())):
			if start_statement in self.color_control_flow["statement"]:
				c_pair = "statement"
			elif start_statement in self.color_control_flow["function"]:
				c_pair = "function"
			elif start_statement in self.color_control_flow["instruction"]:
				c_pair = "instruction"
			else:
				c_pair = "variable"
			# Overwrites the beginning of the line with the given color if possible
			self.stdscr.addstr(mintop, minlen, start_statement, curses.color_pair(self.color_pairs[c_pair]))

		# Finds all '[' and ']' signs and gives them the statement color
		for current_symbol in '[]':
			symbol_indexes = tuple(i for i, ltr in enumerate(line) if ltr == current_symbol)
			for index in symbol_indexes:
				self.stdscr.addstr(
					mintop,
					minlen + index, line[index],
					curses.color_pair(self.color_pairs["statement"])
				)

		# Finds all strings between quotes (single or double) and highlights them green
		quotes_indexes = tuple(i for i, ltr in enumerate(line) if ltr == "\"")
		for j, index in enumerate(quotes_indexes):
			if j % 2 == 0:
				try:
					self.stdscr.addstr(
						mintop,
						minlen + index, line[index:quotes_indexes[j + 1] + 1],
						curses.color_pair(self.color_pairs["strings"] if "=" not in splitted_line[1] else 5)
					)
				except IndexError:
					if len(splitted_line) > 1:
						self.stdscr.addstr(
							mintop,
							minlen + index, line[index:],
							curses.color_pair(self.color_pairs["strings"] if "=" not in splitted_line[1] else 5)
						)

		# Finds all equal signs to highlight them in statement color
		try:
			if "=" in splitted_line[1]:
				self.stdscr.addstr(
					mintop, minlen + 1 + len(splitted_line[0]),
					splitted_line[1],
					curses.color_pair(self.color_pairs["statement"])
				)

			elif splitted_line[0] in self.color_control_flow["variable"] and splitted_line[2] == "=":
				self.stdscr.addstr(
					mintop, minlen + sum(len(e) + 1 for e in splitted_line[:2]),
					"=",
					curses.color_pair(self.color_pairs["statement"])
				)

		except IndexError:
			pass  # If there is no space in the line

		# Finds all '&' signs and gives them the statement color
		symbol_indexes = tuple(i for i, ltr in enumerate(line) if ltr == "&")
		for index in symbol_indexes:
			self.stdscr.addstr(
				mintop,
				minlen + index, line[index],
				curses.color_pair(self.color_pairs["statement"])
			)


		# Function to find all the instances of a substring in a string
		def find_all(full_string: str, search: str):
			"""
			Finds all instances of a substring in a string.
			:param full_string: The string to search into.
			:param search: The string of whom to find all the instances.
			:return: A generator containing all the indexes of the substring.
			"""
			start = 0
			while True:
				start = full_string.find(search, start)
				if start == -1: return
				yield start
				start += len(search)


		# Finds all instances of built-in functions to color them green
		for builtin_function in ("puissance", "racine", "aleatoire", "alea", "len"):
			for builtin_function_index in find_all(line, f"{builtin_function}("):
				self.stdscr.addstr(
					mintop, minlen + builtin_function_index,
					builtin_function,
					curses.color_pair(self.color_pairs["special_string"])
				)


		# If the instruction is a function declaration, we highlight each types in the declaration
		if splitted_line[0] == "fx" and len(splitted_line) > 1:
			# Highlighting the function's return type; as statement if void or variable otherwise
			if splitted_line[1] in (*self.color_control_flow["variable"], "void"):
				self.stdscr.addstr(
					mintop, minlen + 3,
					splitted_line[1],
					curses.color_pair(self.color_pairs["variable" if splitted_line[1] != "void" else "statement"])
				)

			# Or if it is a structure
			elif splitted_line[1].startswith("struct"):
				self.stdscr.addstr(
					mintop, minlen + 3,
					"struct",
					curses.color_pair(self.color_pairs["instruction"])
				)
				self.stdscr.addstr(
					mintop, minlen + 10,
					splitted_line[1][7:],
					curses.color_pair(self.color_pairs["special_string"])
				)

			# Highlighting each argument's type
			for j in range(3, len(splitted_line), 2):
				if splitted_line[j] in (*self.color_control_flow["variable"], "void"):
					self.stdscr.addstr(
						mintop, minlen + 1 + len(" ".join(splitted_line[:j])),
						splitted_line[j], curses.color_pair(self.color_pairs["variable"])
					)

				# If the argument's type is array
				elif splitted_line[j].startswith("arr"):
					# Highlighting the array type in red
					self.stdscr.addstr(
						mintop, minlen + 1 + len(" ".join(splitted_line[:j])),
						"arr", curses.color_pair(self.color_pairs["statement"])
					)
					# Highlighting the underscore
					self.stdscr.addstr(
						mintop, minlen + 1 + len(" ".join(splitted_line[:j])) + 3,
						"_", curses.color_pair(self.color_pairs["function"])
					)
					# Highlighting the var type in yellow
					try:
						self.stdscr.addstr(
							mintop, minlen + 1 + len(" ".join(splitted_line[:j])) + 4,
							splitted_line[j][4:4 + len(splitted_line[j].split("_")[1])], curses.color_pair(self.color_pairs["variable"])
						)
					except IndexError: pass
					# Highlighting the underscore
					try:
						self.stdscr.addstr(
							mintop, minlen + 1 + len(" ".join(splitted_line[:j])) + 4 + len(splitted_line[j].split("_")[1]),
							"_", curses.color_pair(self.color_pairs["function"])
						)
					except IndexError: pass

				# If the argument is a structure
				elif splitted_line[j].startswith("struct"):
					self.stdscr.addstr(
						mintop, minlen + 1 + len(" ".join(splitted_line[:j])),
						"struct", curses.color_pair(self.color_pairs["instruction"])
					)
					self.stdscr.addstr(
						mintop, minlen + 8 + len(" ".join(splitted_line[:j])),
						splitted_line[j][7:],
						curses.color_pair(self.color_pairs["special_string"])
					)


		# If the instruction is an array, we highlight the array's type and its size
		elif splitted_line[0] == "arr" and len(splitted_line) > 1:
			if splitted_line[1] in self.color_control_flow["variable"]:
				self.stdscr.addstr(
					mintop, minlen + 4,
					splitted_line[1],
					curses.color_pair(self.color_pairs["variable"])
				)

			if len(splitted_line) > 3:
				for j in range(3, len(splitted_line)):
					if splitted_line[j].isdigit():
						self.stdscr.addstr(
							mintop, minlen + len(" ".join(splitted_line[:j])) + 1,
							splitted_line[j],
							curses.color_pair(self.color_pairs["special_string"])
						)

		# If the instruction is a constant
		elif splitted_line[0] == "const" and len(splitted_line) > 1:
			if splitted_line[1] in self.color_control_flow["variable"]:
				self.stdscr.addstr(
					mintop, minlen + 6,
					splitted_line[1],
					curses.color_pair(self.color_pairs["variable"])
				)

			if len(splitted_line) > 3 and "=" in splitted_line[3]:
				self.stdscr.addstr(
					mintop, minlen + len(" ".join(splitted_line[:3])) + 1,
					splitted_line[3],
					curses.color_pair(self.color_pairs["statement"])
				)# If the instruction is a function declaration, we highlight each types in the declaration

		# If the instruction is a structure
		elif splitted_line[0] == "struct" and len(splitted_line) > 1:
			# Highlighting the structure's name
			self.stdscr.addstr(
				mintop, minlen + 7,
				splitted_line[1],
				curses.color_pair(self.color_pairs["special_string"])
			)

			# Highlighting each argument's type
			for j in range(2, len(splitted_line), 2):
				if splitted_line[j] in self.color_control_flow["variable"]:
					self.stdscr.addstr(
						mintop, minlen + 1 + len(" ".join(splitted_line[:j])),
						splitted_line[j], curses.color_pair(self.color_pairs["variable"])
					)

				# If the argument's type is array
				elif splitted_line[j].startswith("arr"):
					# Highlighting the array type in red
					self.stdscr.addstr(
						mintop, minlen + 1 + len(" ".join(splitted_line[:j])),
						"arr", curses.color_pair(self.color_pairs["statement"])
					)
					# Highlighting the underscore
					self.stdscr.addstr(
						mintop, minlen + 1 + len(" ".join(splitted_line[:j])) + 3,
						"_", curses.color_pair(self.color_pairs["function"])
					)
					# Highlighting the var type in yellow
					try:
						self.stdscr.addstr(
							mintop, minlen + 1 + len(" ".join(splitted_line[:j])) + 4,
							splitted_line[j][4:4 + len(splitted_line[j].split("_")[1])], curses.color_pair(self.color_pairs["variable"])
						)
					except IndexError: pass
					# Highlighting the underscore
					try:
						self.stdscr.addstr(
							mintop, minlen + 1 + len(" ".join(splitted_line[:j])) + 4 + len(splitted_line[j].split("_")[1]),
							"_", curses.color_pair(self.color_pairs["function"])
						)
					except IndexError: pass


		# If the instruction is a structure initialization
		elif splitted_line[0] == "init" and len(splitted_line) > 1:
			# Highlighting the structure type
			self.stdscr.addstr(
				mintop, minlen + 5,
				splitted_line[1],
				curses.color_pair(self.color_pairs["special_string"])
			)

			# Highlighting each of the arguments if they correspond to a field of the structure, or a number
			for j in range(3, len(splitted_line)):
				# Defining a default flag as being... Well, normal.
				flag = curses.A_NORMAL

				# Highlighting if the argument is a field of the structure (thus if its index is odd)
				if j % 2 == 1:
					# Highlighting as variable
					flag = curses.color_pair(self.color_pairs["variable"])

				# Highlighting the argument as a statement if it is a number
				elif splitted_line[j].isdigit():
					flag = curses.color_pair(self.color_pairs["statement"])

				# Highlighting as a special string if the argument is a string
				elif len(splitted_line[j]) > 0 and splitted_line[j][0] in "\"'":
					flag = curses.color_pair(self.color_pairs["special_string"])

				# Overwrites the text
				self.stdscr.addstr(
					mintop, minlen + 5 + sum(len(e) + 1 for e in splitted_line[1:j]),
					splitted_line[j],
					flag
				)


	def toggle_std_use(self):
		"""
		Toggles the use of the std namespace in the C++ compilation.
		"""
		self.using_namespace_std = not self.using_namespace_std
		self.stdscr.addstr(self.rows - 1, 4, self.get_translation(
			"toggle_namespace_std", state=self.using_namespace_std
		))
		self.plugins_config["BASE_CONFIG"]["using_namespace_std"] = self.using_namespace_std


	def toggle_struct_use(self):
		"""
		Toggles the use of the struct keyword in the function's return type during the C++ compilation.
		"""
		self.use_struct_keyword = not self.use_struct_keyword
		self.stdscr.addstr(self.rows - 1, 4, self.get_translation(
			"toggle_struct_use", state=self.use_struct_keyword
		))
		self.plugins_config["BASE_CONFIG"]["use_struct_keyword"] = self.use_struct_keyword


	def log(self, *args, **kwargs):
		"""
		Prints the given arguments if logs are enabled.
		"""
		if self.logs: print(*args, **kwargs)


	def save(self, text_to_save:str=None, quick_save:bool=False):
		"""
		Saves the code into a file or the clipboard, depending on what's chosen by the user.
		:param text_to_save: The text to save. If None, the contents of the editor. None by default.
		:param quick_save: Whether to quicksave (do the last save action). False by default.
		"""
		def save_to_clipboard():
			"""
			Saves the code to the clipboard.
			"""
			if remember_quicksave:
				self.last_save_action = "clipboard"
			pyperclip.copy(text_to_save)

		def save_to_file():
			"""
			Saves the code to a file.
			"""
			# Creates and displays a few messages to the user
			msg = tuple(elem.format(command_symbol=self.command_symbol) for elem in
			            self.get_translation("save", "save_browse_msg"))
			for i in range(len(msg)):
				self.stdscr.addstr(self.rows // 2 + i, self.cols // 2 - len(msg[i]) // 2, msg[i])

			# Asks for the filename
			filename = input_text(self.stdscr, self.cols // 10, self.rows // 2 + len(msg))

			# If the filename is empty, we don't go inside the if statement (thus cancelling the save)
			if filename != "":
				# If the filename is equals to the command symbol + v (e.g. ':v'), we make it what is currently inside the clipboard
				if filename == self.command_symbol + "v":
					filename = pyperclip.paste()
				# If the filename is equals to the command symbol + b (e.g. ':b"), we open the file browser.
				if filename == self.command_symbol + "b":
					filename = browse_files(self.stdscr, can_create_files=True)()
					if filename == "": return None

				# If the path already exists, we ask the user to confirm the decision of overwriting the file
				if os.path.exists(filename):
					confirm = None
					def set_confirm(b:bool):
						"""
						Sets the value of confirm.
						"""
						nonlocal confirm
						confirm = b
					display_menu(self.stdscr, (
						(self.get_translation("yes"), partial(set_confirm, True)),
						(self.get_translation("no"), partial(set_confirm, False))
					), label =self.get_translation("save", "overwrite_file"))
					# If the user didn't confirm, we don't save.
					if confirm is False:
						return

				# If the filename is a valid path, we dump the code into the requested file
				with open(filename, "w", encoding="utf-8") as f:
					f.write(text_to_save)

				# Saving this save mode as quick action
				if remember_quicksave:
					self.last_save_action = filename

		remember_quicksave = text_to_save is None
		if text_to_save is None:
			text_to_save = self.current_text

		# If this is a regular save, we deploy the menu
		if quick_save is False:
			display_menu(
				self.stdscr,
				(
					(self.get_translation("save", "save_to_clipboard"), save_to_clipboard),
					(self.get_translation("save", "save_to_file"), save_to_file),
					(self.get_translation("cancel"), lambda: None)
				), label =self.get_translation("save", "save_menu"),
				space_out_last_option = True
			)
			self.stdscr.clear()

		# If it is a quicksave :
		else:
			# We paste the code into the clipboard if the last save method was as so
			if self.last_save_action == "clipboard":
				save_to_clipboard()

			# Or we dump the code in the last file it was saved to
			else:
				with open(self.last_save_action, "w", encoding="utf-8") as f:
					f.write(text_to_save)

			self.stdscr.addstr(self.rows - 1, 4, self.get_translation(
				"save", "quicksaved",
				destination=self.last_save_action \
					if self.last_save_action != "clipboard" else \
					self.get_translation("save", "clipboard")
			))


	def open(self, filename: str = None):
		"""
		Opens a code session.
		"""
		opened_code = False
		def open_from_clipboard():
			"""
			Saves the code to the clipboard.
			"""
			self.current_text = pyperclip.paste()
			nonlocal opened_code
			opened_code = True

		def open_from_file(filename: str = None):
			"""
			Saves the code to a file.
			"""
			if filename is None:
				msg = tuple(
					elem.format(command_symbol=self.command_symbol) for elem in
					self.get_translation("open", "open_browse_msg")
				)
				for i in range(len(msg)):
					self.stdscr.addstr(self.rows // 2 + i, self.cols // 2 - len(msg[i]) // 2, msg[i])
				filename = input_text(self.stdscr, self.cols // 10, self.rows // 2 + len(msg))
			if filename != "":
				if filename == self.command_symbol + "v":
					filename = pyperclip.paste()
				if filename == self.command_symbol + "b":
					filename = browse_files(self.stdscr, can_create_files=False)()
				if os.path.exists(filename):
					with open(filename, "r", encoding="utf-8") as f:
						self.current_text = f.read()
						nonlocal opened_code
						opened_code = True
				else:
					msg = self.get_translation("open", "nonexistent_file")
					self.stdscr.addstr(self.rows // 2, self.cols // 2 - len(msg), msg)

		if filename is None:
			display_menu(
				self.stdscr,
				(
					(self.get_translation("open", "open_from_clipboard"), open_from_clipboard),
					(self.get_translation("open", "open_from_file"), partial(open_from_file, None)),
					(self.get_translation("cancel"), lambda: None)
				), label =self.get_translation("open", "open_menu"),
				space_out_last_option = True
			)
		else:
			open_from_file(filename)

		self.stdscr.clear()
		if opened_code:
			self.current_index = 0
			self.stdscr.refresh()
			self.apply_stylings()


	def change_max_undo_size(self):
		"""
		Changes the maximum depth of the undo method.
		"""
		# Requests user input for a size
		self.stdscr.addstr(self.rows - 2, 0, self.get_translation("change_max_undo_size", "input"))
		given_size = input_text(self.stdscr)

		# Tests if the input is a valid number
		if given_size.isdigit():
			# Converts the input to a number, saves it into the config, then regenerates the undo stack
			new_size = int(given_size)
			self.undo_actions = deque(self.undo_actions, maxlen=new_size + 1)
			self.plugins_config["BASE_CONFIG"]["max_undo_size"] = new_size


		# Warns the user it is not a valid number
		else:
			self.stdscr.clear()
			self.stdscr.addstr(self.rows - 2, 0, self.get_translation("change_max_undo_size", "not_a_number").format(
				given_size=given_size
			))
			self.stdscr.getch()


	def show_welcome_page(self):
		"""
		Simply shows a message to the user welcoming him to the app.
		"""
		for i, line in enumerate(self.get_translation("welcome_page")):
			self.stdscr.addstr(
				5 + i,
				self.cols // 2 - len(line) // 2,
				line.format(help_key=f"{self.command_symbol}h", command_symbol=self.command_symbol),
				(curses.A_REVERSE | curses.color_pair(self.color_pairs["instruction"])) * (i == 0)
			)
			if "{help_key}" in line:
				self.stdscr.addstr(
					5 + i,
					self.cols // 2 - len(line) // 2 + line.find("{"),
					f"{self.command_symbol}h",
					curses.color_pair(self.color_pairs["variable"])
				)
			if "{command_symbol}" in line:
				self.stdscr.addstr(
					5 + i,
					self.cols // 2 - len(line) // 2 + line.find("{"),
					self.command_symbol,
					curses.color_pair(self.color_pairs["statement"])
				)



	def change_language(self):
		"""
		Allows the user to change language.
		"""
		def select_language(lang: str):
			# Changes the language to the given one
			self.plugins_config["BASE_CONFIG"]["language"] = lang
			self.language = self.plugins_config["BASE_CONFIG"]["language"]

		# Asks the user to choose a language between all the available languages.
		display_menu(
			self.stdscr,
			tuple(
				[(translation_file[13:15].capitalize(), partial(select_language, translation_file[13:15]))
				for translation_file in os.listdir("translations/")]
				+ [(self.get_translation("quit", "cancel"), lambda: None)]
			),
			label = f"-- {self.get_translation('language', 'label')} --",
			space_out_last_option = True
		)


	def options(self):
		"""
		Allows the user to set some options.
		"""
		do_loop = True
		def end_loop():
			nonlocal do_loop
			do_loop = False

		while do_loop:
			display_menu(
				self.stdscr,
				(
					*[  # Renders the text for each option
						(f"{option[0]} : {option[1]()}", option[2])
						for option in self.options_list
					],
					(self.get_translation("quit", "save_and_quit"), end_loop),
				),
				label = "-- Options --",
				space_out_last_option = True,
				allow_key_input = True
			)



	def mark_line(self):
		"""
		Allows the user to mark a line.
		"""
		# Finds the index of the current line
		current_line_index = self.current_text[:self.current_index].count('\n')

		# Toggles the mark on this line
		if current_line_index in self.marked_lines:
			self.marked_lines.remove(current_line_index)
		else:
			self.marked_lines.append(current_line_index)


	def repeat_last_command(self):
		"""
		Repeats the last command.
		"""
		if self.last_used_command is not None:
			self.execute_command(self.commands[self.last_used_command][0], self.last_used_command)


	def compile(self, noshow:bool=False) -> Union[None, str]:
		"""
		Compiles the inputted text into algorithmic code.
		:param noshow: Whether not to show the compiled code.
		"""
		# Creates a list if instructions by splitting the text into lines
		self.instructions_list = self.current_text.split("\n")

		# Updates the compiler's tab char
		self.compilers["algorithmic"].tab_char = self.tab_char

		# Compiles the code through the Compiler class's compile method
		final_compiled_code = self.compilers["algorithmic"].compile(self.instructions_list)

		if noshow is False:
			if final_compiled_code is not None:
				# Shows the compilation result to the user
				self.stdscr.clear()
				try:
					self.stdscr.addstr(0, 0, final_compiled_code)

					# Calls each plugins' update_on_compilation method
					for plugin in self.plugins.values():
						if hasattr(plugin[1], "update_on_compilation"):
							plugin[1].update_on_compilation(final_compiled_code, "algo")

					# Refreshes the screen and awaits user input (pause)
					self.stdscr.refresh()
					self.stdscr.getch()
				except curses.error: pass

				# Saves the compiled code based on the user's choice
				self.save(final_compiled_code)

			# Clears the screen and reapplies each stylings
			self.stdscr.clear()
			self.apply_stylings()
			self.stdscr.refresh()
		else:
			return final_compiled_code


	def compile_to_cpp(self):
		"""
		Compiles everything to C++ code ; might not always work.
		"""
		# Creates a list if instructions by splitting the text into lines
		self.instructions_list = self.current_text.split("\n")

		# Modifies the std::string use of std:: based on its use
		self.compilers["C++"].var_types["string"] = ("std::" if self.using_namespace_std is False else "") + "string"
		self.compilers["C++"].use_struct_keyword = self.use_struct_keyword

		# Compiles the code through the Compiler class's compile method
		final_compiled_code = self.compilers["C++"].compile(self.instructions_list)

		# Only does this part if no error was raised (if final_compiled_code is not None)
		if final_compiled_code is not None:
			# Shows the compilation result to the user
			self.stdscr.clear()
			self.stdscr.refresh()
			try:
				self.stdscr.addstr(0, 0, final_compiled_code)
			except curses.error: pass

			# Calls each plugins' update_on_compilation method
			for plugin in self.plugins.values():
				if hasattr(plugin[1], "update_on_compilation"):
					plugin[1].update_on_compilation(final_compiled_code, "cpp")

			# Adds a pause
			self.stdscr.getch()

			# Saves the compiled code based on the user's choice
			self.save(final_compiled_code)

		# Clears the screen and reapplies each stylings
		self.stdscr.clear()
		self.apply_stylings()
		self.stdscr.refresh()



def generate_crash_file(app:App, *args):
	"""
	Generates a .crash file.
	:param app: The application instance.
	"""
	# Saves a crash file with the contents of the current code
	with open(os.path.join(os.path.dirname(__file__), CRASH_FILE_NAME), "w", encoding="utf-8") as f:
		f.write(app.current_text)

	# If the app has loaded plugins, we call their on_crash function
	if hasattr(app, "plugins"):
		for plugin_name, (_, plugin_instance) in app.plugins.items():
			plugin_instance.on_crash()


if __name__ == "__main__":
	# Selects the current working directory as the directory of this file
	os.chdir(os.path.dirname(__file__))

	try:
		# Instantiates the app
		app = App()

		# Sets up the command symbol
		if "--command_symbol" in sys.argv:
			app.command_symbol = sys.argv[sys.argv.index("--command_symbol") + 1]

		# Defines whether to display logs
		if "--nologs" in sys.argv:
			app.logs = False

		# Setting the use for the std namespace if there was an argument for it
		if "--using_namespace_std" in sys.argv:
			app.using_namespace_std = sys.argv[sys.argv.index("--using_namespace_std") + 1]

		# If a file was specified as argument
		if "--file" in sys.argv:
			filename = sys.argv[sys.argv.index("--file") + 1]
			# We read the file contents and store it as the app's current text
			with open(filename, "r", encoding="utf-8") as f:
				app.current_text = f.read()
			# We make it so the quicksave will automatically save to this file
			app.last_save_action = filename

		# Detects console closing and creates a .crash file, depending on the OS
		import platform
		if platform.system() == "Windows":
			import win32api
			win32api.SetConsoleCtrlHandler(partial(generate_crash_file, app), True)
		else:
			import signal
			signal.signal(signal.SIGHUP, partial(generate_crash_file, app))

		# We launch the app
		curses.wrapper(app.main)

	# If a crash occurs, generates a .crash file
	except Exception as e:
		# In the event of a crash, saves the current_text to a .crash file
		try:
			generate_crash_file(app)
		except NameError: pass
		# Then raises the exception again
		raise e
