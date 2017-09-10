import sys
import os

current_path = os.path.dirname(__file__)
sys.path.append(current_path)
sys.path.append(os.path.join(current_path, "../src"))

addons = ["cqtc_super_effects", "cqtc_tools"]
for addon in addons:
	sys.path.append(os.path.join(current_path, os.path.join("../src", addon)))
