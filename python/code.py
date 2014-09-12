import os


# --- CODE SETTINGS ---
RESOURCES = 'resources'
SCRIPTS = 'scripts'
FILE_TYPES = {SCRIPTS : ['python-lib', 'tools', 'scripts'], RESOURCES : ['resources']}
FILE_EXTENSIONS = {SCRIPTS : ['.py', '.mel'], RESOURCES : []}
# --- CODE SETTINGS ---


class codeManager:
	root = ''
	
	def __init__(self):		
		self.root = os.path.dirname(os.path.abspath(__file__))
		self.root = self.root.replace('\\', '/')
		self.root = self.root.split('/')
		self.root = self.root[ : -4]
		self.root = '/'.join(self.root)
		
	def __find_files_dir__(self, current, name, dir):
		res = []
		for d in os.listdir(dir):
			fi = dir + '/' + d
			if not os.path.isdir(fi):
				if current in d and len(name) == 0:
					res.append(fi)
			else:
				if current in d:
					if len(name) > 1:
						res += self.__find_files_dir__(name[0], name[ 1 : ], fi)
					elif len(name) == 0:
						res += self.__find_files_dir__('', [], fi)
					else:
						res += self.__find_files_dir__(name[0], [], fi)
						# pass
				else:
					res += self.__find_files_dir__(current, name, fi)
		return res
	
	def find_items(self, name, type='', local=True):
		name = name.replace('\\', '/')
		search_dir = self.root
		if local:
			search_dir = search_dir.replace('U:', 'C:')
			search_dir = search_dir.replace('Z:', 'C:')
		# print search_dir
		splitted_name = name.split('/')
		res = []
		if len(splitted_name) > 1:
			tmp = self.__find_files_dir__(splitted_name[0], splitted_name[ 1 : ], search_dir)
		else:
			tmp = self.__find_files_dir__(splitted_name[0], [], search_dir)
		if type == '':
			return tmp
		for t in tmp:
			for ty in FILE_TYPES[type]:
				if '/%s/' %ty in t.lower():
					if FILE_EXTENSIONS[type] == []:
						res.append(t)
					for ext in FILE_EXTENSIONS[type]:
						if t.lower().endswith(ext):
							res.append(t)
		return res
	
def find_items(name, type='', local=True):
	return codeManager().find_items(name, type, local=local)
	
def find_item(name, type='', local=True):
	res = find_items(name, type, local=local)
	if len(res) > 0:
		return res[0]
	else:
		return None
	
def find_resources(name, local=True):
	return find_items(name, type=RESOURCES, local=local)
	
def find_resource(name, local=True):
	res = find_resources(name, local=local)
	if len(res) > 0:
		return res[0]
	else:
		return None
	
def find_scripts(name, local=True):
	return find_items(name, type=SCRIPTS, local=local)
	
def find_script(name, local=True):
	res = find_scripts(name, local=local)
	if len(res) > 0:
		return res[0]
	else:
		return None

def find_in_scripts(name, script=''):
	# SLOW PROCESS, CAN BE SPED UP
	res = find_scripts(script)
	tmp = []
	for r in res:
		str = open(r, 'r')
		lines = str.readlines()
		for l in lines:
			if name in l:
				tmp.append(r)
				break
		str.close()
	return tmp
		
if __name__ == "__main__":
	# print codeManager().find_items('maya/renderPresets', type=SCRIPTS)
	# print codeManager().find_items('maya/pointcaches', type=SCRIPTS)
	print codeManager().find_items('renderPresets', type=SCRIPTS)
	# UI_FILE = find_items('ui/pipeline.ui', type=RESOURCES)
	# print UI_FILE
	# r = find_in_scripts('mayaSubmissionCmd')
	print len(r)
	print r
	