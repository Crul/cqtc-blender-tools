import os.path
import pickle

def load_pickle(path):
	if os.path.isfile(path):
		return pickle.load(open(path, "rb"))
	
	return []


def save_pickle(path, data):
	pickle.dump(data, open(path, "wb"))
