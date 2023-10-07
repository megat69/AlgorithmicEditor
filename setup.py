import os, platform
import sys

def associate_file_type():
	# Writes the bat file launching the file
	with open("AlgoEditorOpen.bat", "w", encoding="utf-8") as f:
		f.write(f"MODE con:cols=197 lines=45\ncmd /k python \"{os.getcwd()}/main.py\" --file \"%1\"")

	# Runs the commands to create the default extension
	os.system(f"ftype AlgoEditorFile=\"{os.getcwd()}/AlgoEditorOpen.bat\" %1")
	os.system("assoc .algo=AlgoEditorFile")


os.chdir(os.path.dirname(__file__))
if len(sys.argv) >= 2 and sys.argv[1] == "--filetype":
	try:
		from pyuac import isUserAdmin, runAsAdmin
	except ImportError:
		os.system("pip install pyuac")
		os.system("python setup.py --filetype")
		sys.exit(1)
	else:
		if isUserAdmin():
			associate_file_type()
			sys.exit(0)
		else:
			sys.exit(3 + runAsAdmin([sys.executable, "--filetype"]))

PLUGINS_STARTER_PACK = (
	("autocomplete", {"fr": "Ajoute de l'autocomplétion", "en": "Adds autocompletion"}),
	("copy", {"fr": "Permet de copier", "en": "Enables copying"}),
	("paste", {"fr": "Permet de coller", "en": "Enables pasting"}),
	("docstring", {"fr": "Rend la création de documentation plus simple", "en": "Makes documentation creation easier"}),
	("file_index", {"fr": "Ajoute un index de fichiers dans l'éditeur", "en": "Adds a file index in the editor"}),
	("tabs", {"fr": "Ajoute la possibilité d'avoir plusieurs onglets ouverts", "en": "Enables you to open multiple tabs at once"}),
)

# Asks the user their age
language = "fr" if input("Choose a language (EN/FR) : ")[:2].lower() == "fr" else "en"

# Creates the plugins folder if it doesn't exist
try:
	os.mkdir("plugins")
except FileExistsError: pass

# Creates the plugins config
if not os.path.exists("plugins_config.json"):
	with open("plugins_config.json", "w", encoding="utf-8") as f:
		f.write(
			'{\n\t"BASE_CONFIG": {\n\t\t"default_save_location": "%%",\n\t\t"language": "%%"\n\t}\n}'.replace(
				"%%", os.path.normpath(os.path.join(os.path.dirname(__file__), "../")).replace(
					"\\", "/"
				), 1
			).replace("%%", language, 1)
		)

# Creates all the translations for the setup in the file
translations = {
	'fr': {
		"pip_prefix": "Veuillez entrer votre préfixe PIP (pip, pip3, python -m pip, py -p pip...). Laissez vide pour 'pip'.",
		"requirements_install": "Installation des dépendances...",
		"install_plugin_repo": "Voulez-vous installer le plugin 'plugin_repo' et ses dépendances ? "
		                       "Il s'agit d'un excellent plugin pour vous aider à gérer et installer des plugins,"
		                       " en plus d'être un très bonne exemple pour apprendre à créer le vôtre. (o/n)",
		"install_starter_pack": "Voulez-vous installer un starter pack de plugins ? Ils sont faits pour rendre "
		                        "votre vie plus facile, et son développés en même temps que le projet lui-même.\n"
		                        "Une bonne partie des fonctionnalités de l'éditeur sont implémentées par leur biais.\n"
		                        "Le starter pack de plugins inclut :"
		                        "{}"
		                        "Voulez-vous les installer ? (o/n)",
		"setup_finished": "C'est tout bon ! Setup terminé.",
		"error_occured": "Une erreur s'est produite durant le téléchargement du plugin_repo.",
		"associate_filetype": "Voulez-vous associer l'extension '.algo' avec ce logiciel ? (o/n) "
	},
	'en': {
		"pip_prefix": "Please enter your PIP prefix (pip, pip3, python -m pip, py -p pip...). Leave blank for 'pip'.",
		"requirements_install": "Installing requirements...",
		"install_plugin_repo": "Do you want to install the 'plugin_repo' plugin and its requirements ? "
		                       "It is a great plugin to help you manage and install plugins, as well as being a great "
		                       "example on how to create your own. (y/n)",
		"install_starter_pack": "Do you want to install a starter pack of plugins ? They are intended to make "
		                        "your life easier, and are developed alongside the project itself. A lot of "
		                        "editor features are implemented through those. The plugins include :"
		                        "{}"
		                        "Do you want to install them ? (y/n)",
		"setup_finished": "All done ! Setup complete.",
		"error_occured": "An error occurred while trying to download the plugin_repo.",
		"associate_filetype": "Do you want to associate the extension '.algo' with this software ? (y/n) "
	}
}

# Asks the user their PIP prefix
pip_prefix = input(translations[language]["pip_prefix"] + "\n")
if pip_prefix == "":
	pip_prefix = f"\"{sys.executable}\" -m pip"

# Installs the requirements
print(translations[language]["requirements_install"])
if platform.system() == "Windows":
	os.system(f"{pip_prefix} install -r requirements-windows.txt")
	from pyuac import isUserAdmin, runAsAdmin
else:
	os.system(f"{pip_prefix} install -r requirements.txt")

# Asks the user if they want to install the plugin repo
install_plugin_repo = input("\n"*2 + translations[language]["install_plugin_repo"])[0].lower() != "n"
if install_plugin_repo:
	# Installs the plugin repo requirements
	print(translations[language]["requirements_install"])
	os.system(f"{pip_prefix} install -r plugin_repo-requirements.txt")

	# Using requests, downloads the plugin repo
	import requests
	def download_plugin(name: str):
		r = requests.get(f"https://raw.githubusercontent.com/megat69/AlgorithmicEditor_Plugins/main/{name}.py")
		if r.status_code == 200:
			with open(os.path.join(os.path.dirname(__file__), "plugins", f"{name}.py"), "w", encoding="utf-8") as f:
				f.write(r.text)
		# If an error happened (connection, server error...), it is printed out to the user and the
		# plugin download is aborted
		else:
			print(translations[language]["error_occured"])

	# Downloads the plugin repo
	download_plugin("plugin_repo")

	# Asking the user if they want to install the starter pack plugin
	install_starter_pack = input("\n"*2 + translations[language]["install_starter_pack"].format(
		''.join([
			f"\n- '{name}' : {description[language]}"
			for name, description in PLUGINS_STARTER_PACK
		])
	))[0].lower() != "n"

	# Installs the whole starter pack if the user said yes
	if install_starter_pack:
		for name, _ in PLUGINS_STARTER_PACK:
			print(f"Downloading {name}...")
			download_plugin(name)
			print(f"Installed {name} !")
		print("Starter pack installed !")

# If the user is on Windows, we ask them if they want to associate the '.algo' filetype with the editor
# This action needs setup.py to be run as administrator to function.
if platform.system() == "Windows":
	associate_filetypes = input("\n" * 2 + translations[language]["associate_filetype"]) != "n"
	if associate_filetypes:
		if not isUserAdmin():
			runAsAdmin(cmdLine=[sys.executable, "--filetype"])
		else:
			associate_file_type()

# Prints the line saying the setup finished
print(translations[language]["setup_finished"])
