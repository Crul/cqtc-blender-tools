import os.path
import pickle

def load_pickle(pickle_path):
	if os.path.isfile(pickle_path):
		return pickle.load(open(pickle_path, "rb"))
	
	return []


def save_pickle(pickle_path, data):
	pickle.dump(data, open(pickle_path, "wb"))
