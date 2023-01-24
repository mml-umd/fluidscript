import json

def readJSON(file):	#Reads JSON data from file
	f = open(file)
	try:
		data = json.load(f)
	except Exception as e:
		print(file, " couldn't be read, defaulting to empty contents")
		data = json.loads("{}")

	f.close()
	return data

def writeJSON(data, file):	#Writes JSON data to file
	f = open(file, "w")
	json.dump(data, f, indent=2)
	f.close()