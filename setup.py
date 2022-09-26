import os, platform
os.mkdir(os.path.join(os.path.dirname(__file__), "plugins"))

if platform.system() == "Windows":
	os.system("pip install -r requirements-windows.txt")
else:
	os.system("pip install -r requirements.txt")