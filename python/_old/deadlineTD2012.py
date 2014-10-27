'''
	Deadline module
	
	created by Sven Fraeys 2012
	
	documentation : Z:\WG_Code\wtd\common\doc\deadline.odt
	samples : Z:\WG_Code\wtd\common\samples\deadline
	
	
'''
import time
import os
import shutil
import shlex, subprocess
import code as WCode
import tabDocument as WTabDocument
import modo as WModo

OPTIONS_PATH = r"\\srv-deadline\Deadline6\settings\Options"
OPTIONS_PATH_MODO_BATCH = OPTIONS_PATH + "/modo_batch.txt"
OPTIONS_PATH_MODO_RENDER = OPTIONS_PATH + "/modo_render.txt"
OPTIONS_PATH_NUKE_RENDER = OPTIONS_PATH + "/nuke_render.txt"
OPTIONS_PATH_NUKE_BATCH = OPTIONS_PATH + "/nuke_batch.txt"
OPTIONS_PATH_TILE_ASSEMBLER_RENDER = OPTIONS_PATH + "/tileAssembler_render.txt"


def testFonction():
	print "test"

class deadlineBatch(object):
	debug = False
	popen = False
	DEADLINE_5 = r"C:\Program Files\Thinkbox\Deadline\bin\deadlinecommandbg.exe"
	DEADLINE_6 = "C:\\Program Files\\Thinkbox\\Deadline6\\bin\\deadlinecommandbg.exe"
	jobDependencies = []
	options = ["Plugin=MayaBatch","Frames=0"]
	pluginOptions = ["Version=2012","Build=None","ProjectPath=M:\\temp\\","StrictErrorChecking=True","ScriptJob=True","ScriptFilename=helloWorld.py"]
	arguments = []
	deadlineCommand = "C:\\Program Files\\Thinkbox\\Deadline6\\bin\\deadlinecommandbg.exe"
	# TEMPPATH = os.getenv("TEMP")
	TEMPPATH = "c:\\"
	jobId = None # id of the job of deadline
	id = None  # custom id that we give for saving and loading
	
	def loadOptions(self,path):
		if not os.path.exists(path):
			return False
		
		fs = open(path,'r')
		lines = fs.readlines()
		fs.close()
		for line in lines:
			lineStripped = line.strip()
			# print lineStripped
			lineStrippedSplitArray = lineStripped.split("=")
			key = lineStrippedSplitArray[0]
			value = None
			if len(lineStrippedSplitArray) > 0:
				value = lineStrippedSplitArray[1]
				
			if self.hasOption(key):
				self.deleteOption(key)
			
			self.setOption(key,value)
			
	def addJobDependency(self,job):
		self.jobDependencies.append(job)
	
	def getId(self):
		if self.id == None:
			self.id = "job_"+str(id(self))
		return self.id
	
	def setId(self,value):
		self.id = value
	
	def __init__(self):
		self.options = ["Plugin=MayaBatch","Frames=0"]
		self.pluginOptions = ["Version=2012","Build=None","ProjectPath=M:\\temp\\","StrictErrorChecking=True","ScriptJob=True","ScriptFilename=helloWorld.py"]
		self.arguments = []
		self.jobDependencies = []
		self.jobId = None
		self.deadlineCommand = deadlineBatch.DEADLINE_6
		# self.deadlineCommand = deadlineBatch.DEADLINE_6
		self.popen = False
	def unique_file(self,file_name):
		'''
			make a unique file
		'''
		counter = 1
		file_name_parts = os.path.splitext(file_name) # returns ('/path/file', '.ext')
		while os.path.isfile(file_name): 
			file_name = file_name_parts[0] + "" + str(counter) + file_name_parts[1]
			counter += 1
		return file_name
		
	def exportOptions(self, filepath):
		'''
			exports options to a file
		'''
		file = open(filepath, "w")
		for option in self.options:
			file.write(option+"\n")
		file.close()
		
	def exportPluginOptions(self, filepath):
		'''
			exports plugin to a file
		'''
		file = open(filepath, "w")
		for option in self.pluginOptions:
			file.write(option+"\n")
		file.close()
		
	def mergeOptions(self,options,pluginOptions=False):
		'''
			merges optionArray with current
		'''
		
		for option in options:
			nameAndValue = option.split("=")
			nameString = nameAndValue[0]
			valueString = nameAndValue[1]
			
			
			self.setOption(nameString,valueString,pluginOptions=pluginOptions)
		
	def getOption(self,name,pluginOptions=False):
		'''
			returns the value of that option
		'''
		options = self.options
		if pluginOptions == True:
			options = self.pluginOptions
			
		for option in options:
			nameAndValue = option.split("=")
			nameString = nameAndValue[0]
			if nameString == name:
				return nameAndValue[1]
		return None
		
	def hasOption(self,name,pluginOptions=False):
		'''
			returns True if the submitOption has the option
		'''
		options = self.options
		if pluginOptions == True:
			options = self.pluginOptions
		
		for option in options:
			nameAndValue = option.split("=")
			nameString = nameAndValue[0]
			if nameString == name:
				return True
		return False
	def deleteOption(self,name,pluginOptions=False):
		'''
			deletes option from options
		'''
		c = -1
		options = self.options
		if pluginOptions == True:
			options = self.pluginOptions
		for option in options:
			c += 1
			nameAndValue = option.split("=")
			nameString = nameAndValue[0]
			if nameString == name:
				del options[c]
		if pluginOptions == True:
			self.pluginOptions = options
		else:
			self.options = options
			
	def setOption(self,name,value,pluginOptions=False):
		'''
			adds and option in the submitoptions
		'''
		if self.hasOption(name,pluginOptions) == True:
			self.deleteOption(name,pluginOptions)
			
		if pluginOptions == True:
			self.pluginOptions.append(name+"="+str(value) )
		else:
			self.options.append(name+"="+str(value) )
			
	def getJobIdFromOutputfile(self,outputfile):
		'''
			get job id from the output file
		'''
		fs = open(outputfile,"r")
		lines = fs.readlines()
		fs.close()
		for line in lines:
			linePieces = line.split("=")
			if linePieces == None:
				continue
			if len(linePieces) == 2 :
				if linePieces[0] == "JobID":
					jobId = linePieces[1]
					jobId = jobId.replace("\n","")
					jobId = jobId.replace("\r","")
					return jobId 
		# return parser.get(outputfile,"JobID")
		return None
	
	def submitDependenciesToDeadline(self):
		'''
			submits the dependent jobs to deadline if needed
		'''
		returnIds = []
		for dependencyjob in self.jobDependencies:
			id = dependencyjob.jobId
			if id == None:
				id = dependencyjob.submitToDeadline()
			returnIds.append(id)
		return returnIds
		
	def submitToDeadline(self):
		'''
			submit the batch to deadline
		'''
		if self.jobId != None:
			return self.jobId
			
		dependencyIdArray = self.submitDependenciesToDeadline()
		currentDependencies = self.getOption("JobDependencies")
		if currentDependencies != None:
			currentDependencies = currentDependencies.split(",")
		else:
			currentDependencies = []
		
		allDepenencies = dependencyIdArray + currentDependencies
		

		
		newdependencyString = ""
		for dependencyId in allDepenencies:
			newdependencyString += dependencyId + ","
			
		self.setOption("JobDependencies",newdependencyString)
		
		if os.path.exists(self.TEMPPATH) == False:
			os.mkdir(self.TEMPPATH)
		pluginName = self.getOption("Plugin")
		# mayaSubmitInfo = self.unique_file(self.TEMPPATH + "/"+pluginName+"_submit_info.job")
		
		# self.setOption("DeleteOnComplete", "false")
		mayaSubmitInfo = (self.TEMPPATH + "/"+pluginName+"_submit_info.job")
		mayaPluginInfo = (self.TEMPPATH + "/"+pluginName+"_plugin_info.job")
		
		self.exportOptions(mayaSubmitInfo)
		self.exportPluginOptions(mayaPluginInfo)
		
		q = "\""
		
		outputFile = self.TEMPPATH + "\\output.txt"
		exitCodeFile = self.TEMPPATH + "\\exitcode.txt"
		args = ""
		for arg in self.arguments:
			args += arg.replace("\\","/") + " "
		
		sendToDeadlineCommand = q + self.deadlineCommand + q + " " + "-outputfiles " + outputFile + " " + exitCodeFile + " " + mayaSubmitInfo + " " + mayaPluginInfo + " "+ args
		if self.debug:
			print sendToDeadlineCommand
		
		subprocess.call(sendToDeadlineCommand,shell=True)
		
		jobId = self.getJobIdFromOutputfile(outputFile)
		self.jobId = jobId
		
		return jobId
		
	def submitToLocal(self):
		'''
			starts rendering localy
		'''
		return True
		
	def setFile(self,filepath):
		'''
			sets the workfile (for global use)
		'''
		
	def getFile(self):
		'''
			get the workfile (for global use)
		'''
		return ""
	
	def saveInTabNode(self,tabnode):
		deadlineNode = tabnode.addNode("deadline")
		deadlineNode.addNode(str(self.__class__.__name__))
		if self.deadlineCommand == self.DEADLINE_5:
			deadlineNode.addNode(str(5))
		else:
			deadlineNode.addNode(str(6))
		
		idsString = ""
		for jobDependency in self.jobDependencies:
			idsString += jobDependency.getId() + ","
			
		deadlineNode.addNode("jobDependencies="+str(idsString))
		
		submitInfoNode = tabnode.addNode("submit_info")
		pluginInfoNode = tabnode.addNode("plugin_info")
		
		for param in self.options:
			submitInfoNode.addNode(param)
		
		for param in self.pluginOptions:
			pluginInfoNode.addNode(param)
	
	def save(self,path):
		tabDoc = WTabDocument.tabDocument()
		saveInTabNode(tabDoc.root)
		tabDoc.save(path)
	
	def loadInTabNode(self,tabnode):
		deadlineNode = tabnode.getNode('deadline')
		if deadlineNode.nodes[1].value == '5':
			self.deadlineCommand = self.DEADLINE_5
		elif deadlineNode.nodes[1].value == '6':
			self.deadlineCommand = self.DEADLINE_6
		submitInfoNode = tabnode.getNode("submit_info")
		pluginInfoNode = tabnode.getNode("plugin_info")
		submitInfoArr = []
		pluginInfoArr = []
		
		for param in submitInfoNode.nodes:
			submitInfoArr.append(param.value)
		
		for param in pluginInfoNode.nodes:
			pluginInfoArr.append(param.value)
			
		self.pluginOptions = pluginInfoArr
		self.options = submitInfoArr
	
	def load(self,path):
		tabDoc = WTabDocument.tabDocument(path)
		self.loadInTabNode(tabDoc.root)
		
		
class draftBatch(deadlineBatch):
	scriptFile = ""
	def __init__(self):
		super(draftBatch,self).__init__()
		self.options = ["Plugin=Draft","Frames=0"]
		self.pluginOptions = ["scriptFile="]
	
	def saveInTabNode(self,tabnode):
		deadlineBatch.saveInTabNode(self,tabnode)
		plugin = tabnode.addNode("plugin")
		plugin.addNode(self.scriptFile)
		
	def loadInTabNode(self,tabnode):
		deadlineBatch.loadInTabNode(self,tabnode)
		plugin = tabnode.getNode("plugin")
		self.scriptFile = plugin.nodes[0].value
	
	def submitToDeadline(self):	
		self.setOption("scriptFile",(self.scriptFile),True)
		jobId = deadlineBatch.submitToDeadline(self)
		return jobId

		
class tileAssemblerRender(deadlineBatch):
	def __init__(self):
		super(tileAssemblerRender,self).__init__()
		self.options = ["Plugin=TileAssembler","Frames=0"]
		self.pluginOptions = ["InputImages=","InputDirectory=","InputStartsWith=","InputPaddingSize=","InputExtension="]
	
	def saveInTabNode(self,tabnode):
		deadlineBatch.saveInTabNode(self,tabnode)
		plugin = tabnode.addNode("plugin")
		plugin.addNode(self.scriptFile)
		
	def loadInTabNode(self,tabnode):
		deadlineBatch.loadInTabNode(self,tabnode)
		plugin = tabnode.getNode("plugin")
		self.scriptFile = plugin.nodes[0].value
	
	def submitToDeadline(self):	
		jobId = deadlineBatch.submitToDeadline(self)
		return jobId
		
class commandScriptBatch(deadlineBatch):
	'''
		command line script batch
	'''
	command = ""
	def __init__(self):
		super(commandScriptBatch,self).__init__()
		self.options = ["Plugin=CommandScript","Frames=0"]
		
		self.pluginOptions = ["StartupDirectory=C:\\Program Files\\Thinkbox\\Deadline6\\bin\\"]
		
	def exportCommandsFile(self,filepath):
		'''
			saves commandsfile
		'''
		file = open(filepath, "w")
		file.write( self.command )
		file.close()
		
	def submitToDeadline(self):
		'''
			submit deadline
		'''
		pluginName = self.getOption("Plugin")
		# (self.TEMPPATH + "/"+pluginName+"_commandscriptBatch.txt")
		commandsFile = (self.TEMPPATH + "/"+pluginName+"_commandscriptBatch.txt")
		# commandsFile = deadlineBatch.unique_file(self, "C:\\temp\\commandscriptBatch.txt")
		self.exportCommandsFile(commandsFile)
		self.arguments.append(commandsFile)
		
		
		jobId = deadlineBatch.submitToDeadline(self)
		return jobId
		
class pythonBatch(deadlineBatch):
	scriptFile = ""
	PYTHON_EXE = r"C:/Python27/python.exe"
	def saveInTabNode(self,tabnode):
		deadlineBatch.saveInTabNode(self,tabnode)
		plugin = tabnode.addNode("plugin")
		plugin.addNode(self.scriptFile)
		
	def loadInTabNode(self,tabnode):
		deadlineBatch.loadInTabNode(self,tabnode)
		plugin = tabnode.getNode("plugin")
		self.scriptFile = plugin.nodes[0].value
		
	def __init__(self):
		super(pythonBatch,self).__init__()
		self.options = ["Plugin=Python","Frames=0"]
		self.pluginOptions = ["Arguments=","Version=2.7"]
		
	def submitToDeadline(self):	
		self.setOption("ScriptFile",(self.scriptFile),True)
		jobId = deadlineBatch.submitToDeadline(self)
		return jobId
	def getLocalCommandline(self):
		args = self.getOption("Arguments",True)
		pythonCommandline = self.PYTHON_EXE + " " +self.scriptFile + " " + args
		return pythonCommandline
	def submitToLocal(self):
		pythonCommandline = self.getLocalCommandline()
		subprocess.call(pythonCommandline)
		
class deadlineJobBatch(pythonBatch):
	scriptFile = ""
	jobFile = ""
	
	def __init__(self):
		super(deadlineJobBatch,self).__init__()
		self.scriptFile = WCode.find_script("deadline/submitDeadlineSaveFile.py")
		self.jobFile = ""
		
	def submitToDeadline(self):	
		jobFile = self.jobFile.replace("\\","/")
		self.setOption("Arguments","\""+(jobFile)+"\"",True)
		jobId = pythonBatch.submitToDeadline(self)
		return jobId	
	
class mayaBatch(deadlineBatch):
	sceneFile = ""
	scriptFile = ""
	submitMayaSceneFile = False
	def __init__(self):
		super(mayaBatch,self).__init__()
		self.options = ["Plugin=MayaBatch","Frames=0","TaskTimeoutMinutes=0","EnableAutoTimeout=False","ConcurrentTasks=1","LimitConcurrentTasksToNumberOfCpus=True","ChunkSize=1"]
		self.pluginOptions = ["Version=2012","Build=None","ProjectPath=M:\\temp\\","StrictErrorChecking=True","ScriptJob=True","ScriptFilename=helloWorld.py"]
	
	def saveInTabNode(self,tabnode):
		deadlineBatch.saveInTabNode(self,tabnode)
		plugin = tabnode.addNode("plugin")
		plugin.addNode(self.sceneFile)
		plugin.addNode(self.scriptFile)
		
		
	def loadInTabNode(self,tabnode):
		deadlineBatch.loadInTabNode(self,tabnode)
		plugin = tabnode.getNode("plugin")
		self.sceneFile = plugin.nodes[0].value
		self.scriptFile = plugin.nodes[1].value
	
	def submitToDeadline(self):
		'''
			submits to deadline
		'''
		self.arguments = [self.scriptFile] + self.arguments
		if self.submitMayaSceneFile == False:
			self.setOption("SceneFile",(self.sceneFile),True)
		else:
			self.arguments = [self.sceneFile] + self.arguments
			# self.arguments.append(self.sceneFile)
			# print self.arguments
		
		self.setOption("ScriptFilename",os.path.basename(self.getCleanUpScriptFile() ),True)
		jobId = deadlineBatch.submitToDeadline(self)
		return jobId
	def setFile(self,filepath):
		'''
			sets the workfile (for global use)
		'''
		self.sceneFile = filepath
	def getFile(self):
		'''
			get the workfile (for global use)
		'''	
		return self.sceneFile
	def getCleanUpScriptFile(self):
		'''
			cleanup script file
		'''
		cleanupScriptsPath = self.scriptFile.replace("\\","/")
		return cleanupScriptsPath
	def getCommand(self):
		'''
			returns the command
		'''
		pythonCommand = "execfile('"+self.getCleanUpScriptFile() +"');"
		pythonString = pythonCommand.replace("\"","\\\\\\\"")
		
		pythonString = "\"python \\\""+pythonString+"\\\" \""
		return pythonString
		
	def getLocalCommandline(self):
		'''
			get the local command line
		'''
		mayaExecuteLine = ""
		mayaExe = r"C:\Program Files\Autodesk\Maya2012\bin\mayabatch.exe"
		mayaExecuteLine += "\""+mayaExe+"\"" + " "
		mayaExecuteLine += "" + " "
		mayaExecuteLine += "-file " + self.sceneFile + " "
		mayaExecuteLine += "-command " + self.getCommand() + " "
		return mayaExecuteLine
		
	def submitToLocal(self):
		'''
			submit local
		'''
		mayaExecuteLine = self.getLocalCommandline()
		subprocess.call(mayaExecuteLine)

class mayaCommandScriptBatch(mayaBatch):
	mayaCommandScriptBatchSystemCommandsFile = ""
	scriptArguments = []
	def __init__(self):
		self.mayaCommandScriptBatchSystemCommandsFile = WCode.find_resource(r"deadline/mayaCommanScriptBatchCommandsFile.txt")
		super(mayaCommandScriptBatch,self).__init__()
	
	def submitToDeadline(self):
		'''
			submit to deadline
		'''
		command = self.getLocalCommandline()
		cmdBatch = commandScriptBatch()
		cmdBatch.command = command
		# cmdBatch.options = self.options
				
		origCopyCommandOptions = cmdBatch.options
		origCommandOptions = []
		for option in origCopyCommandOptions:
			origCommandOptions.append(option)
		
		cmdBatch.mergeOptions(self.options)
		
		cmdBatch.mergeOptions(origCommandOptions)
		
		jobId = cmdBatch.submitToDeadline()
		return jobId
	
class mayaRender(deadlineBatch):
	sceneFile = ""
	outputFilePath = ""
	renderer="MentalRay"
	preRenderScript = None
	
	def __init__(self):
		super(mayaRender,self).__init__()
		self.pluginOptions = ["Version=2012","Build=None","ProjectPath=M:\\temp\\","StrictErrorChecking=True","LocalRendering=False","MaxProcessors=0","OutputFilePath=M:\temp\animation\renders","Renderer=File","CommandLineOptions=","UseOnlyCommandLineOptions=0","IgnoreError211=False"]
		self.options = ["Plugin=MayaCmd","Frames=0","TaskTimeoutMinutes=0","EnableAutoTimeout=False","ConcurrentTasks=1","LimitConcurrentTasksToNumberOfCpus=True","ChunkSize=1"]
		
		
	def saveInTabNode(self,tabnode):
		deadlineBatch.saveInTabNode(self,tabnode)
		plugin = tabnode.addNode("plugin")
		plugin.addNode(self.sceneFile)
		plugin.addNode(self.outputFilePath)
		plugin.addNode(self.renderer)
		plugin.addNode(self.preRenderScript)
		
	def loadInTabNode(self,tabnode):
		deadlineBatch.loadInTabNode(self,tabnode)
		plugin = tabnode.getNode("plugin")
		self.sceneFile = plugin.nodes[0].value
		self.outputFilePath = plugin.nodes[1].value
		self.renderer = plugin.nodes[2].value
		self.preRenderScript = plugin.nodes[3].value
		
	def getCleanUpScriptFile(self):
		'''
			cleanup script file
		'''
		cleanupScriptsPath = self.preRenderScript.replace("\\","/")
		return cleanupScriptsPath
	def getCommand(self):
		'''
			returns the command
		'''
		pythonCommand = "execfile(\""+self.getCleanUpScriptFile() +"\")"
		pythonString = pythonCommand.replace("\"","\\\\\\\"")
		
		pythonString = "\"python \\\""+pythonString+"\\\" \""
		return pythonString
	def submitToDeadline(self):
		'''
			submit to deadline
		'''
		self.setOption("SceneFile",(self.sceneFile),True)
		self.setOption("OutputFilePath",(self.outputFilePath),True)
		self.setOption("Renderer",(self.renderer),True)
		
		if self.preRenderScript != None:
			preRenderScript = self.preRenderScript.replace("\\","/")
			preRenderString = ""
			pythonCommand = "execfile(\""+self.preRenderScript+"\")"
			pythonString = pythonCommand.replace("\"","\\\\\\\"")
			
			pythonString = "-preRender \"python \\\""+pythonString+"\\\" \""
			# print pythonString
			self.setOption("CommandLineOptions",(pythonString),True)
			
		
		# print pythonString
		# return None
		jobId = deadlineBatch.submitToDeadline(self)
		return jobId
		
	def submitToLocal(self):
		'''
			submit local
		'''
		mayaExecuteLine = ""
		mayaExe = r"C:\Program Files\Autodesk\Maya2012\bin\mayabatch.exe"
		mayaExecuteLine += "\""+mayaExe+"\"" + " "
		# mayaExecuteLine += "-batch" + " "
		mayaExecuteLine += "-file " + self.sceneFile + " "
		mayaExecuteLine += "-command " + self.getCommand() + " "
		mayaExecuteLine += "-proj " + "c:/" + " "
		
		# mayaExecuteLine += self.commandLineOptions
		# print mayaExecuteLine
		# print mayaExecuteLine
		subprocess.call(mayaExecuteLine)
	
	
class nukeBatch(deadlineBatch):
	sceneFile = ""
	scriptFile = ""
	exe = r"C:\Program Files\Nuke7.0v8\Nuke7.0.exe"
	
	def __init__(self):
		super(nukeBatch,self).__init__()
		self.sceneFile = ""
		self.scriptFile = ""
		self.options = ["Plugin=CommandScript","Frames=0"]
		self.pluginOptions = ["StartupDirectory=C:\\python27"]
		
	def getCommandline(self):
		exe = self.exe
		resourcePath = WCode.find_resource(r"deadline\nuke.py")
		resourcePath = self.modoBatchSystemScript = resourcePath.replace("U:","Z:")
		command = "\"%s\" -t %s %s %s" % (exe, resourcePath, self.sceneFile, self.scriptFile)
		return command
	def submitToLocal(self):
		'''
			starts rendering localy
		'''
		command = (self.getCommandline())
		# print command
		subprocess.call(command)
	

	def exportCommandsFile(self,filepath):
		'''
			saves commandsfile
		'''
		file = open(filepath, "w")
		file.write( self.getCommandline() )
		file.close()
		
	def submitToDeadline(self):
		'''
			submit deadline
		'''
		# commandsFile = deadlineBatch.unique_file(self, "C:\\temp\\commandsFile.txt")
		pluginName = self.getOption("Plugin")
		commandsFile = (self.TEMPPATH + "/"+pluginName+"NukeBatch_commandsFile.txt")
		self.exportCommandsFile(commandsFile)
		
		self.arguments.append(commandsFile)
		
		self.setOption("SceneFile",(self.sceneFile),True)
		self.setOption("ScriptFilename",os.path.basename(self.scriptFile),True)
		jobId = deadlineBatch.submitToDeadline(self)
		
		return jobId
		
class nukeRender(deadlineBatch):
	options = ["Plugin=Nuke","Frames=1"]
	pluginOptions = ["Version=7.0","Threads=0","RamUse=0","Build=64bit","BatchMode=False","NukeX=False","ContinueOnError=False"]
	nukeFile = ""
	sceneFile = ""
	
	exe = r"C:\Program Files\Nuke7.0v4\Nuke7.0.exe"
	def __init__(self):
		super(nukeRender,self).__init__()
		self.options = ["Plugin=Nuke","Frames=1"]
		self.pluginOptions = ["Version=7.0","Threads=0","RamUse=0","Build=64bit","BatchMode=False","NukeX=False","ContinueOnError=False"]
		self.sceneFile = ""
		self.nukeFile = ""
	def submitToDeadline(self):
		self.arguments = [self.getFile()] + self.arguments
		self.setOption("SceneFile",(self.getFile()),True)
		jobId = deadlineBatch.submitToDeadline(self)
		return jobId
	def submitToLocal(self):
		'''
			starts rendering localy
		'''
		exe = self.exe
		args = "-t -x"
		q = "\""
		command = q + exe + q + " " + args + " " +q + self.getFile() + q + ""
		print command
		subprocess.call(command)
	def setFile(self,filepath):
		'''
			sets the workfile (for global use)
		'''
		self.sceneFile = filepath
		self.nukeFile = filepath	
	def getFile(self):
		'''
			get the workfile (for global use)
		'''	
		sceneFile = self.sceneFile
		if sceneFile == "" or sceneFile == None:
			sceneFile = self.nukeFile
		return sceneFile

class modoRender(deadlineBatch):
	sceneFile = ""
	outputFilename = ""
	outputFormat = None
	passGroup = ""
	readVersion = False
	tileAssemblerRender = None
	OUTPUTFORMAT_OPENEXR = "openexr"
	
	# tile rendering
	outputFolder = None
	tileJob = False
	regionFrame = 1
	tileJobTilesInX = 2
	tileJobTilesInY = 2
	outputFilePrefix = None
	regionFormat = None
	def __init__(self):
		super(modoRender,self).__init__()
		self.options = ["Plugin=Modo","Frames=1"]
		self.pluginOptions = ["Version=6xx","Build=64bit","Threads=0","PassGroup=","SceneFile="]
		self.sceneFile = None
		self.outputFilename = None
		self.outputFormat = None
		self.readVersion = False
		self.outputFolder = None
		self.outputFilePrefix = None
		self.tileJob = False
		self.regionFrame = 1
		self.tileJobTilesInX = 2
		self.tileJobTilesInY = 2
		self.regionFormat = None
		self.tileAssemblerRender = None
		
	def addTileRenderingRegionOptions(self,tileIndex,left,right,top,bottom,filename):
		tileIndex = str(tileIndex)
		# print tileIndex, left, right, top, bottom, filename
		self.setOption("RegionLeft%s"%tileIndex,left,True)
		self.setOption("RegionRight%s" % tileIndex,right,True)
		self.setOption("RegionTop%s" % tileIndex,top,True)
		self.setOption("RegionBottom%s" % tileIndex,bottom,True)
		self.setOption("RegionFilename%s" % tileIndex,filename,True)
		
		
	def setTileRenderingOptions(self):
		if self.tileJob:
			self.setOption("TileJob",True)
			self.setOption("TileJobFrame",self.regionFrame)
			self.setOption("TileJobTilesInX",self.tileJobTilesInX)
			self.setOption("TileJobTilesInY",self.tileJobTilesInY)
			self.setOption("RegionFormat",self.regionFormat,True)
			self.setOption("RegionJob",True,True)
			self.setOption("RegionFrame",self.regionFrame,True)
			i = -1
			width = 100.0 / float(self.tileJobTilesInX)
			height = 100.0 / float(self.tileJobTilesInY)
			
			self.setOption("Frames","0-%s" % str((self.tileJobTilesInX * self.tileJobTilesInY) - 1))
			
			for x in range(self.tileJobTilesInX):
				left = (float(x) / float(self.tileJobTilesInX) ) * 100
				right = left + width
				for y in range(self.tileJobTilesInY):
					i += 1
					top = ( float(y) / float(self.tileJobTilesInY) ) * 100
					bottom = top + height
					
					prefix = self.outputFilePrefix
					if prefix == None:
						prefix = ""
						
					filepath = self.outputFolder + prefix + "_tile_%sx%s_%sx%s_" % (str(x + 1),str(y + 1),str(self.tileJobTilesInX), str(self.tileJobTilesInY))
					self.addTileRenderingRegionOptions(i,left,right,top,bottom,filepath)
					
			if self.tileAssemblerRender != None:
				prefix = self.outputFilePrefix
				if prefix == None:
					prefix = ""
				filepath = self.outputFolder + prefix + "_tile_%sx%s_%sx%s_0000.exr" % (str(0),str(0),str(self.tileJobTilesInX), str(self.tileJobTilesInY))
				# mr.setOption("InputImages",r"M:\Film\_USERS\SFraeys\tiles\render\tiles__tile_0x0_8x4_0000.exr",True)
				
				dirname = self.outputFolder
				if prefix == "":
					dirname = os.path.dirname(self.outputFolder)
				self.tileAssemblerRender.setOption("InputDirectory",dirname,True)
				
				
				realprefix = ""
				if self.outputFilePrefix == None:
					outputFolder = self.outputFolder.replace("/","\\")
					realprefix = outputFolder.split("\\")[-1]
				else:
					realprefix = self.outputFilePrefix
					
				
				self.tileAssemblerRender.setOption("InputImages",filepath,True)
				# mr.setOption("InputStartsWith",r"tiles__tile_1x1_8x4_",True)
				
				self.tileAssemblerRender.setOption("InputStartsWith",realprefix + "_tile_1x1_%sx%s_" % (self.tileJobTilesInX, self.tileJobTilesInY),True)
				
				self.tileAssemblerRender.setOption("InputPaddingSize",4,True)
				self.tileAssemblerRender.setOption("InputExtension","exr",True)
				
				self.tileAssemblerRender.setOption("NotCropped",True,True)
				self.tileAssemblerRender.setOption("IgnoreOverlap",True,True)
				
	def submitToDeadline(self):
	
		if self.readVersion and self.sceneFile != None:
			isModo6 = WModo.is_modo601_file(self.sceneFile)
			if isModo6:
				self.setOption("Version","6xx",True)
			else:
				self.setOption("Version","7xx",True)
	
		# self.arguments = [self.sceneFile] + self.arguments
		self.setOption("SceneFile",(self.sceneFile),True)
		
		if self.outputFilename != None and self.tileJob == False:
			self.setOption("OutputFilename",(self.outputFilename),True)
			
		if self.outputFormat != None and self.tileJob == False:	
			self.setOption("OutputFormat",(self.outputFormat),True)
		
		if self.passGroup != None:
			self.setOption("PassGroup",(self.passGroup),True)
			
		if self.outputFolder != None and self.tileJob == False:
			self.setOption("OutputFilename",(self.outputFolder + self.outputFilePrefix),True)
			
		if self.tileJob:
			self.setTileRenderingOptions()
			
		jobId = deadlineBatch.submitToDeadline(self)
		
		if self.tileAssemblerRender != None:
			self.tileAssemblerRender.setOption("JobDependencies",jobId)
			self.tileAssemblerRender.submitToDeadline()
		
		return jobId


class modoBatch(deadlineBatch):
	'''
		modo Batch system
	'''
	sceneFile = ""
	scriptFile = ""
	MODO_601_SP5_CL = r"c:\Program Files\Luxology\modo\601_sp5\modo_cl.exe"
	MODO_601_SP5_UI = r"c:\Program Files\Luxology\modo\601_sp5\modo.exe"
	MODO_701_SP1 = r"c:\Program Files\Luxology\modo\701_sp1\modo_cl.exe"
	MODO_701_SP3 = r"c:\Program Files\Luxology\modo\701_sp3\modo_cl.exe"
	modoExecutable = r"c:\Program Files\Luxology\modo\601_sp5\modo_cl.exe"
	assetPath = r"M:\Film\_LIBRARY\Modo_Content\Assets"
	dblog = None
	debug = None
	readVersion = False
	modoBatchSystemScript = None
	modoBatchSystemCommandsFile = None
	
	def toString(self):
		n = "\n"
		t = "\t"
		returnStr = "modoBatch" + n
		returnStr = t + self.sceneFile + n
		returnStr = t + self.scriptFile + n
		returnStr = t + self.modoExecutable + n
		returnStr = t + self.assetPath + n
	
	def saveInTabNode(self,tabnode):
		deadlineBatch.saveInTabNode(self,tabnode)
		plugin = tabnode.addNode("plugin")
		plugin.addNode(self.sceneFile)
		plugin.addNode(self.scriptFile)
		plugin.addNode(self.modoExecutable)
		plugin.addNode(self.assetPath)
		
	def loadInTabNode(self,tabnode):
		deadlineBatch.loadInTabNode(self,tabnode)
		plugin = tabnode.getNode("plugin")
		self.sceneFile = plugin.nodes[0].value
		self.scriptFile = plugin.nodes[1].value
		self.modoExecutable = plugin.nodes[2].value
		self.assetPath = plugin.nodes[3].value
	
	def __init__(self):
		super(modoBatch,self).__init__()
		self.modoExecutable = self.MODO_601_SP5_CL
		self.readVersion = False
		self.options = ["Plugin=CommandScript","Frames=0"]
		self.pluginOptions = ["StartupDirectory=C:\\python27"]
		resourcePath = WCode.find_resource(r"deadline\modo.py")
		self.modoBatchSystemScript = resourcePath.replace("U:","Z:")
		self.modoBatchSystemCommandsFile = WCode.find_resource(r"deadline\modoCommandsFile.txt")
		self.dblog = None
		self.debug = None
		# print "----"
		# print WCode.find_resource(r"deadline\modoCommandsFile.txt")
		# print "----"
	def cleanupString(self,value):
		value = value.replace("\\","/")
		return value
	def getCommandline(self):
		if self.readVersion and self.sceneFile != None:
			isModo6 = WModo.is_modo601_file(self.sceneFile)
			if isModo6:
				self.modoExecutable = self.MODO_601_SP5_CL
			else:
				self.modoExecutable = self.MODO_701_SP1
				
		templateFileStream = open(self.modoBatchSystemCommandsFile,"r")
		templateLine = templateFileStream.read()
		templateFileStream.close()
		
		templateLine = templateLine.replace("%exe%",self.cleanupString(self.modoExecutable))
		templateLine = templateLine.replace("%modo%",self.cleanupString(self.sceneFile))
		templateLine = templateLine.replace("%script%",self.cleanupString(self.modoBatchSystemScript))
		templateLine = templateLine.replace("%param1%",self.cleanupString(self.scriptFile))
		templateLine = templateLine.replace("%asset%",self.cleanupString(self.assetPath))
		if self.dblog != None:
			templateLine += " -dblog:%s" % self.dblog
			
		if self.debug != None:
			templateLine += " -debug:%s" % self.debug
			
		return templateLine
		
	def exportCommandsFile(self,filepath):
		'''
			saves commandsfile
		'''
		file = open(filepath, "w")
		file.write( self.getCommandline() )
		file.close()
		
	def submitToDeadline(self):
		'''
			submit deadline
		'''
		# commandsFile = deadlineBatch.unique_file(self, "C:\\temp\\commandsFile.txt")
		pluginName = self.getOption("Plugin")
		commandsFile = (self.TEMPPATH + "/"+pluginName+"_commandsFile.txt")
		self.exportCommandsFile(commandsFile)
		
		self.arguments.append(commandsFile)
		
		self.setOption("SceneFile",(self.sceneFile),True)
		self.setOption("ScriptFilename",os.path.basename(self.scriptFile),True)
		
		
		
		jobId = deadlineBatch.submitToDeadline(self)
		
		return jobId
		
	def submitToLocal(self):
		'''
			submit proces localy
		'''
		# print self.getCommandline()
		cl = self.getCommandline()
		# print cl
		if self.popen:
			subprocess.Popen(cl)
		else:
			subprocess.call(cl)
			
	def setFile(self,filepath):
		'''
			sets the workfile (for global use)
		'''
		self.sceneFile = filepath
	def getFile(self):
		'''
			get the workfile (for global use)
		'''	
		return self.sceneFile	
		
	
class mdcModoBatch(modoBatch):
	'''
		modo job for mdc project
	'''
	def submitToDeadline(self):
		self.setOption("Pool","small_tasks")
		return modoBatch.submitToDeadline(self)
		
class mdcMayaBatch(mayaBatch):
	'''
		maya job for mdc project
	'''
	def submitToDeadline(self):
		self.setOption("Pool","small_tasks")
		return mayaBatch.submitToDeadline(self)

def save(jobs,path):
	
	tabDoc = WTabDocument.tabDocument()
	
	for job in jobs:
		jobNode = tabDoc.root.addNode(job.getId())
		job.saveInTabNode(jobNode)
	tabDoc.save(path)

def submit(path,name=None, deadline5=False):
	dj = create_deadlineJobBatch()
	if deadline5:
		dj.deadlineCommand = deadlineBatch.DEADLINE_5
	if name != None:
		dj.setOption("Name",name)
	dj.jobFile = path
	return dj.submitToDeadline()
	
def load(path):
	tabDoc = WTabDocument.tabDocument(path)
	jobs = []
	
	for jobNode in tabDoc.root.nodes:
		# job = deadlineBatch()
		# print jobNode
		
		jobClass = jobNode.getNode("deadline").nodes[0].value
		jobDependenciesStringIdArray = jobNode.getNode("deadline").nodes[2].value.split("=")[1].split(",")
		jobDependenciesStringIdArray.remove("")
		job = eval(jobClass+"()")
		id = jobNode.getName()
		job.setId(id)
		job.loadInTabNode(jobNode)
		job.jobDependenciesStringIdArray = jobDependenciesStringIdArray
		
		jobs.append(job)
		
	# linking the jobdependencies
	for job in jobs:
		jobDependencies = []
		for jobString in job.jobDependenciesStringIdArray:
			for jobB in jobs:
				if jobB.getId() == jobString:
					jobDependencies.append(jobB)
		job.jobDependencies = jobDependencies
		
	return jobs

def create_modoBatch():
	mb = modoBatch()
	mb.setOption("Pool","small_tasks")
	mb.setOption("Name","untitled modoBatch")
	mb.setOption("Priority","99")
	mb.loadOptions(OPTIONS_PATH_MODO_BATCH)
	return mb

def create_deadlineJobBatch():
	djb = deadlineJobBatch()
	djb.setOption("Name","Untitled Submitter")
	djb.setOption("Pool","submitter")
	return djb
	
def create_mayaBatch():
	mb = mayaBatch()
	mb.setOption("Name","Untitled mayaBatch" )
	mb.setOption("Pool","maya")
	return mb
	
def create_mayaRender():
	mb = mayaRender()
	mb.setOption("Name","Untitled mayaRender" )
	mb.setOption("Pool","maya")
	return mb
	
def create_modoRender():
	mr = modoRender()
	mr.setOption("Name","Untitled modoRender" )
	mr.setOption("Pool","modo")
	mr.setOption("Priority","99")
	mr.loadOptions(OPTIONS_PATH_MODO_RENDER)
	return mr

def create_modoBatch_mdc():
	mb = create_modoBatch()
	mb.modoBatchSystemScript = "mdcDeadline"
	mb.loadOptions(OPTIONS_PATH_MODO_BATCH)
	return mb
	
def create_pythonBatch():
	pb = pythonBatch()
	pb.setOption("Name","Untitled pythonBatch" )
	pb.setOption("Pool","small_tasks")
	return pb
	
def create_nukeRender():
	nr = nukeRender()
	nr.setOption("Name","Untitled nukeRender" )
	nr.setOption("Pool","nuke")
	nr.loadOptions(OPTIONS_PATH_NUKE_RENDER)
	return nr
	
def create_nukeBatch():
	nukeBatchObject = nukeBatch()
	nukeBatchObject.setOption("Name","Untitled nukeBatch" )
	nukeBatchObject.setOption("Pool","small_tasks")
	nukeBatchObject.loadOptions(OPTIONS_PATH_NUKE_BATCH)
	return nukeBatchObject
	
def create_tileAssemblerRender():
	tileAssemblerObject = tileAssemblerRender()
	tileAssemblerObject.setOption("Name","Untitled tileAssembler" )
	tileAssemblerObject.setOption("Pool","small_tasks")
	tileAssemblerObject.loadOptions(OPTIONS_PATH_TILE_ASSEMBLER_RENDER)
	return tileAssemblerObject
	
if __name__ == "__main__":
	pass
	mr = modoRender()
	mr.sceneFile = r"C:\Users\sfraeys\Desktop\chan.lxo"
	# mr.tileJob = True
	# mr.outputFolder = "c:/"
	# mr.outputFilePrefix = "pref"
	# mr.regionFormat = "openexr_tiled32"
	# mr.submitToDeadline()
	
	# mr = create_tileAssemblerRender()
	# mr.setOption("InputImages",r"M:\Film\_USERS\SFraeys\tiles\render\tiles__tile_0x0_2x2_0000.exr",True)
	# mr.setOption("InputDirectory",r"M:\Film\_USERS\SFraeys\tiles\render",True)
	# mr.setOption("InputStartsWith",r"tiles__tile_1x1_8x4_",True)
	# mr.setOption("InputPaddingSize",4,True)
	# mr.setOption("InputExtension","exr",True)
	
	# self.pluginOptions = ["InputImages=","InputDirectory=","InputStartsWith=","InputPaddingSize=","InputExtension="]
	print mr.submitToDeadline()
	
	# mb = create_modoBatch()
	# mb.sceneFile = r"C:\broken.lxo"
	# mb.scriptFile = r'U:\WG_Code\mdc\modo\scripts\helloworld.py'
	# mb.dblog = "c:/error.txt"
	# mb.debug = "normal"
	# mb.submitToLocal()
	
	# nb = create_nukeBatch()
	# nb.sceneFile = r"M:\Film\q012\s006\Scenes\Compositing\q012_s006_cmp_v010.nk"
	# nb.scriptFile = r"C:\Users\sfraeys\Desktop\work.py"
	# nb.submitToLocal()
	
	# nr = create_nukeBatch()
	# nr.sceneFile = r"M:\Film\q012\s001\Scenes\Compositing\q012_s001_cmp_v017.nk"
	# nr.scriptFile = "c:/dd"
	# id = nr.submitToDeadline()
	
	# nr = create_nukeRender()
	# nr.setOption("Priority","0")
	# nr.loadOptions("c:/renderData.txt")
	# nr.nukeFile = r"M:\Film\q012\s001\Scenes\Compositing\q012_s001_cmp_v999.nk"
	# nr.setOption("JobDependencies",str(id))
	# print nr.submitToDeadline()
	
	# nr = create_nukeBatch()
	# nr.nukeFile = r"M:\Film\q012\s006\Scenes\Compositing\q012_s006_cmp_v011.nk"
	# nr.scriptFile = r"c:/temp.py"
	# print nr.submitToDeadline()
	