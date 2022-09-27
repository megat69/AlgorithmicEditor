import os, platform
os.mkdir(os.path.join(os.path.dirname(__file__), "plugins"))

language = "fr" if input("Choose a language (EN/FR) : ")[:2].lower() == "fr" else "en"
translations = {
	'fr': {
		"pip_prefix": "Veuillez entrer votre préfixe PIP (pip, pip3, python -m pip, py -p pip...). Laissez vide pour 'pip'.",
		"requirements_install": "Installation des dépendances...",
		"install_plugin_repo": "Voulez-vous installer le plugin 'plugin_repo' et ses dépendances ? "
		                       "Il s'agit d'un excellent plugin pour vous aider à gérer et installer des plugins,"
		                       " en plus d'être un très bonne exemple pour apprendre à créer le vôtre. (o/n)",
		"setup_finished": "C'est tout bon ! Setup terminé."
	},
	'en': {
		"pip_prefix": "Please enter your PIP prefix (pip, pip3, python -m pip, py -p pip...). Leave blank for 'pip'.",
		"requirements_install": "Installing requirements...",
		"install_plugin_repo": "Do you want to install the 'plugin_repo' plugin and its requirements ? "
		                       "It is a great plugin to help you manage and install plugins, as well as being a great "
		                       "example on how to create your own. (y/n)",
		"setup_finished": "All done ! Setup complete."
	}
}

pip_prefix = input(translations[language]["pip_prefix"] + "\n")
if pip_prefix == "":
	pip_prefix = "pip"

print(translations[language]["requirements_install"])
if platform.system() == "Windows":
	os.system(f"{pip_prefix} install -r requirements-windows.txt")
else:
	os.system(f"{pip_prefix} install -r requirements.txt")

install_plugin_repo = input(translations[language]["install_plugin_repo"])[0].lower() != "n"
if install_plugin_repo:
	print(translations[language]["requirements_install"])
	os.system(f"{pip_prefix} install -r plugin_repo-requirements.txt")
	import requests
	r = requests.get("https://raw.githubusercontent.com/megat69/AlgorithmicEditor_Plugins/main/plugin_repo.py")
	if r.status_code != 200:
		with open(os.path.join(os.path.dirname(__file__), "plugins", "plugin_repo.py"), "w", encoding="utf-8") as f:
			f.write(r.text)
