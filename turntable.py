# -*- coding: utf-8 -*-
import sys
sys.path.append (r'Z:\Shotgun_Studio\install\core\python')
import sgtk
from sgtk.platform import Application
import maya.cmds as cmds
from pymel.core import *
import math
import wtd.deadline as MDeadline
import os
import inspect
shotName = None

#==============================================================
# SHOTGUN GET INFORMATIONS
#==============================================================

ScenePath= cmds.file (q=True, sn=True)
PathWithoutFileName = os.path.split(ScenePath)[0]
tk = sgtk.sgtk_from_path(ScenePath)
tk.reload_templates()

ContextFromPath = tk.context_from_path(ScenePath)
AssetIdNumber = ContextFromPath.entity.get('id') 

TemplateFromPath = tk.template_from_path(ScenePath)
TemplateFields = TemplateFromPath.get_fields(ScenePath)

AssetType = TemplateFields.get('sg_asset_type')
AssetName = TemplateFields.get('Asset')
StepName = TemplateFields.get('Step')
# format the version with 3 digits
# VersionScene = '%0*d' % (03, TemplateFields.get('version'))
VersionScene = TemplateFields.get('version')

VersionKey = TemplateFromPath.keys['version']
VersionKeyFormated= VersionKey.str_from_value(VersionScene)

AssetRenderTemplate = tk.templates['maya_asset_render']
AssetRenderFullPath = AssetRenderTemplate.apply_fields(TemplateFields)
AssetRenderPath = AssetRenderFullPath.split('.')[0]

#==============================================================
#RENDER TURNTABLE TD V0.02
#==============================================================
"""
def TEST():
	print "hello"
"""

def SaveChanges(): 
	# check if there are unsaved changes
	fileCheckState = cmds.file(q=True, modified=True)
	if fileCheckState:
		print 'Need to save.'
		# This is maya's native call to save, with dialogs, etc.
		# No need to write your own.
		cmds.SaveScene()
		pass
	else:
		print 'No new changes, proceed.'
		pass


def ExecTurntable(turntableScene):
	'''
	#GET INFORMATIONS BY SCENE PATH
	FullPath= cmds.file (q=True, sn=True)
	PathWithoutFileName = os.path.split(FullPath)[0]
	AssetType = FullPath.split("/")[3]
	AssetName = FullPath.split("/")[4]
	StepName = FullPath.split("/")[5]
	VersionScene = FullPath.split("_v")[1][:3]
	'''
	#NUMBER OF GROUPS IN SCENE VERIFICATION
	curentSel = cmds.ls(g=True, an= True, l=True )

	list_grps = []
	for theString in curentSel:
		theSplitAr = theString.split(":")
		if theSplitAr [1][:-1] in list_grps:
			None
		else:
			list_grps.append(theSplitAr [1][:-1])

	if len(list_grps)!= 1:
		cmds.warning("-program need 1 group named: " + AssetName)
	elif AssetName not in list_grps :
		cmds.warning("-program need 1 group named: " + AssetName)
	else:
		#print ("1 groupe = OK")
		GroupName = list_grps [0] 

		#PATHS AND TYPE FILE
		#turntableScenePath = 'C:/Users/tdelbergue/Desktop/'
		#turntableScenePath = "W:/RTS/Experimental/People/TDelbergue/"
		turntableScenePath = "W:/RTS/_Library/Presets/Maya/"
		turntableSceneName= 'scene_turntable_07.ma'
		# turntableSceneName= turntableScene

		LibraryPath = "W:/RTS/_Library"
		RendersPath = "W:/RTS/Renders/_Library/mod"
		WorkMayaPath = "work/maya"
		PublishMayaPath = "publish/maya"

		# CurrentMayaPath = LibraryPath +"/"+AssetType +"/"+ AssetName+ "/" + StepName +"/"+ WorkMayaPath +"/"
		CurrentMayaPath = PathWithoutFileName+"/"
		# AssetRenderPath = LibraryPath +"/"+AssetType +"/"+ AssetName+ "/" + StepName +"/"+ PublishMayaPath +"/"
		# AssetRenderPath = RendersPath+"/"+AssetType +"/"+ AssetName+ "/" 
		#OUPUT PATH
		if not os.path.exists(AssetRenderPath):
			os.makedirs(AssetRenderPath)
		
		ExportGeoFilePath = CurrentMayaPath
		ExportGeoFileName = AssetName

		fileType = "fbx"

		geometry = cmds.ls(geometry=True)
		cmds.select(geometry, r=True)

		#export FBX file
		cmds.file(ExportGeoFilePath+ExportGeoFileName+".fbx",pr=1,typ="FBX export",es=1, op="groups=0; ptgroups=0; materials=0; smoothing=0; normals=0")

		# SaveChanges()

		#open sceneturntable
		sceneturntableFullpath = os.path.join(turntableScenePath,turntableSceneName)
		#print sceneturntableFullpath
		cmds.file( sceneturntableFullpath, o=True )

		#import file
		#cmds.file -import -type "OBJ" -ra true -mergeNamespacesOnClash false -namespace "kiki" -options "mo=1"  -pr -loadReferenceDepth "all" "C:/Users/tdelbergue/Desktop/kiki.obj"

		# files = cmds.getFileList(folder=CurrentMayaPath, filespec=GroupName+'.'+fileType)
		files = cmds.getFileList(folder=CurrentMayaPath, filespec=AssetName+'.'+fileType)
		if len(files) == 0:
			#print files
			cmds.warning("No files found")
		else:
			for f in files:
				#print f
				test = cmds.file(ExportGeoFilePath + f, i=True, pn= True)  
				# cmds.parent( GroupName, 'locator_fix' )
				cmds.parent( AssetName, 'locator_fix' )
				
		SceneTurnOutputName = AssetName+"_"+StepName+"_v"+str(VersionKeyFormated)+'_turn'		
		
		cmds.file(rename =CurrentMayaPath+SceneTurnOutputName)
		cmds.file(save=True)

		# ZOOM ON GEOMETRY
		geometry = cmds.ls(geometry=True)
		cmds.select(geometry, r=True)

		## Gather our world bounding box and store it in a variable called b
		#b = general.exactWorldBoundingBox()
		b = cmds.exactWorldBoundingBox()

		## b now contains min and max XYZ world coords
		## Name our temporary locators

		locName = "tempLoc"
		## Create a locator at each min and max point to form a fake bounding box

		positions = [[0,1,2], [0,4,2], [0,4,5], [3,4,5], [3,1,5], [3,4,2], [3,1,2], [0,1,5]]

		ratioHautMoitie = b[4]-((b[4]-b[1])/2)
		heightBoundBox = (b[4]-b[1])
		widthBoundBox = (b[3]-b[0])
		depthBoundBox = (b[5]-b[2])

		heightBoundBoxMin= 2.193*heightBoundBox
		widthBoundBoxMin= 1.425* widthBoundBox

		for position in positions:
			#print position
			cmds.spaceLocator(p=(b[position[0]],b[position[1]],b[position[2]]), name=locName)

		## Once we create the locators, frame locators, delete
		cmds.setAttr( "camWide.translateY", ratioHautMoitie )

		if heightBoundBoxMin >=  widthBoundBoxMin:
			cmds.setAttr( "camWide.translateZ",heightBoundBoxMin)
		if heightBoundBoxMin <=  widthBoundBoxMin:
			cmds.setAttr( "camWide.translateZ",widthBoundBoxMin)

			
		# EYES MESH IN SCENE VERIFICATION
		eyeList = []
			
		allObjects = cmds.ls(l=False, typ= 'mesh' )

		for obj in allObjects:
			if "eye" in obj.lower():
				EyesTrsX = cmds.objectCenter(obj,x=True)
				EyesTrsY = cmds.objectCenter(obj,y=True)
				EyesTrsZ = cmds.objectCenter(obj,z=True)
				eyeList.append(obj)
		
		#WARNING MESSAGES IF MISSING EYES OR GROUP PROBLEMS
		if not eyeList:
			cmds.warning("no object with name 'eye' was found, please rename or create one")	
			
		sumX = []
		sumY = []
		sumZ = []
		#print eyeList
		if eyeList:
			for obj in eyeList:
				EyesTrsX = cmds.objectCenter(obj,x=True)
				EyesTrsY = cmds.objectCenter(obj,y=True)
				EyesTrsZ = cmds.objectCenter(obj,z=True)
				sumX.append(EyesTrsX)
				sumY.append(EyesTrsY)
				sumZ.append(EyesTrsZ)    

		EyesTrsX = sum(sumX)/len(sumX)
		EyesTrsY = sum(sumY)/len(sumY)
		EyesTrsZ = sum(sumZ)/len(sumZ)

		cmds.spaceLocator(p=(EyesTrsX,EyesTrsY,EyesTrsZ), name="pivot_head")
		cmds.parent( "pivot_head", eyeList[0][:-5] )
			
		heightToptoEyes = (b[4]-EyesTrsY) 

		cmds.setAttr( "pivot_camCloseUp.translateX", EyesTrsX )
		cmds.setAttr( "pivot_camCloseUp.translateY", EyesTrsY )
		cmds.setAttr( "pivot_camCloseUp.translateZ", EyesTrsZ ) 

		cmds.parent( "pivot_camCloseUp", "pivot_head" )

		#cmds.setAttr( "camCloseUp.translateY", EyesTrsY )
		cmds.setAttr( "camCloseUp.translateZ", 7*heightToptoEyes+ b[5] )

		CAM1Z =getAttr( "camWide.translateZ" )
		CAM2Z =getAttr( "camCloseUp.translateZ" )
		CAM3Z = CAM1Z - ((CAM1Z-CAM2Z)/2)

		cmds.setAttr( "camMiddle.translateZ", 2*heightBoundBox )

		cmds.setAttr("camMiddle.translateY",(ratioHautMoitie+EyesTrsY)/2)

		tempLocators = select("tempLoc*", r=1)

		delete()

		#SCENE PARAMETERS
		#HD720
		cmds.setAttr ("defaultResolution.width", 1280)
		cmds.setAttr ("defaultResolution.height", 720)
		cmds.setAttr("defaultResolution.deviceAspectRatio",1.777)
		cmds.setAttr ("defaultResolution.pixelAspect", 1)

		#LIGHTING TRANSFORMS
		KeyShapeIntensity = cmds.getAttr( "KeyShape.intensity")
		RimShapeIntensity = cmds.getAttr( "RimShape.intensity")
		FillShapeIntensity = cmds.getAttr( "FillShape.intensity")
		'''
		KeyShapeIntensity = 10000.0
		RimShapeIntensity = 2600.0
		FillShapeIntensity =250.0
		'''

		HeighRichardReference = 15

		ScaleFactor= heightBoundBox/HeighRichardReference

		LightCompensation=ScaleFactor*math.sqrt(ScaleFactor)

		cmds.setAttr("LOC_Lights.scaleX",ScaleFactor)
		cmds.setAttr("LOC_Lights.scaleY",ScaleFactor)
		cmds.setAttr("LOC_Lights.scaleZ",ScaleFactor)

		NewKeyShapeIntensity = cmds.setAttr( "KeyShape.intensity",KeyShapeIntensity*LightCompensation)
		NewRimShapeIntensity = cmds.setAttr( "RimShape.intensity",RimShapeIntensity*LightCompensation)
		NewFillShapeIntensity = cmds.setAttr( "FillShape.intensity",FillShapeIntensity*LightCompensation)

		cmds.file(q=True, modified=True)
		cmds.file(q=True, modified=True)
		cmds.file(q=True, modified=True)
		
		#OUTPUT FRAMES NAME
		cmds.setAttr("defaultRenderGlobals.imageFilePrefix", SceneTurnOutputName,type="string")

		#CREATE_SCENES_AND_CAMS
		cmds.file(rename = CurrentMayaPath+SceneTurnOutputName+'CloseUp')
		cmds.file(save=True)

		cameraObj = "camCloseUp"
		cmds.lockNode(cameraObj+".renderable", lock=False)
		cmds.setAttr(cameraObj+".renderable",0)
		cameraObj = "camWide"
		cmds.lockNode(cameraObj+".renderable", lock=False)
		cmds.setAttr(cameraObj+".renderable",1)
		#save wide
		cmds.file(rename = CurrentMayaPath+SceneTurnOutputName+'Wide')
		cmds.file(save=True)

		cameraObj = "camWide"
		cmds.lockNode(cameraObj+".renderable", lock=False)
		cmds.setAttr(cameraObj+".renderable",0)
		cameraObj = "camMiddle"
		cmds.lockNode(cameraObj+".renderable", lock=False)
		cmds.setAttr(cameraObj+".renderable",1)
		#save mid
		cmds.file(rename = CurrentMayaPath+SceneTurnOutputName+'Middle')
		cmds.file(save=True)

		#save close
		cmds.file( q=True, ex=True )
		
		#==============================================================
		#DEADLINE POST_PROCESS = COMPLETE IMAGE RANGE CHILD SCRIPT
		#==============================================================
		"""
		infile = open('W:/RTS\Experimental/People/TDelbergue/images_range_copy03RESEAU.py')
		outfile = open('C:/Users/tdelbergue/Desktop/testRange.py', 'w+')

		replacements = {'path=""':'path=', 'name=""':'name="claudius_mod_v000_turntable."'}

		for line in infile:
			for src, target in replacements.iteritems():
				line = line.replace(src, target)
			outfile.write(line)
		infile.close()
		outfile.close()
		"""
		#==============================================================
		#DEADLINE SUBMIT
		#==============================================================

		def submitturntable (CharName, CameraName, frameRangeInput ):
			#print "Render turntable v1.0"
			#print "Note : your maya scene must be a .MA (maya ascii format)"
			#print 60*"-"
			scenePath = CurrentMayaPath+CharName+"/"
			if not os.path.exists(scenePath):
				os.makedirs(scenePath)    
			#shot = "claudius_turntable_00.ma"
			mr = MDeadline.mayaRender()
			mr.ProjectPath = PathWithoutFileName
			mr.outputFilePath = AssetRenderPath
			mr.sceneFile = PathWithoutFileName+"/"+SceneTurnOutputName+CameraName+".ma"
			mr.setOption("Priority","50")
			mr.setOption("Name",CharName + "_v_"+VersionKeyFormated+ " -" + "turntable" + "- " + CameraName )
			frameRange = frameRangeInput
			frameRangeString = frameRangeInput
			mr.setOption("Frames",frameRangeString)
			mr.setOption("Pool","maya_2013")
			mr.setOption("MachineLimit","1")
			
			deadlineID = mr.submitToDeadline()
			print deadlineID
			return deadlineID

		ID1 = submitturntable (AssetName,"Wide", "0-159" )
		ID2 = submitturntable (AssetName,"Middle", "160-319x10" )
		ID3 = submitturntable (AssetName,"CloseUp", "320-479x20" )
		tempDep = "%s,%s,%s" %(ID1, ID2, ID3)

		childJob =  MDeadline.create_pythonBatch()
		childJob.setOption("Name",AssetName+" Child Job - Make complete sequence ")

		# ADDING ONE JOB AS A DEPENDENCY
		childJob.setOption("JobDependencies", tempDep)
		childJob.scriptFile = r"W:/RTS/Experimental/People/TDelbergue/FillMissingFiles03.py"
		childJob.setOption("Arguments", 'pathArg='+str(AssetRenderPath+"/")+' '+'nameArg='+str(SceneTurnOutputName)+' '+'IDAssetArg='+str(AssetIdNumber),True)

		#SUBMITTING
		childId = childJob.submitToDeadline()
