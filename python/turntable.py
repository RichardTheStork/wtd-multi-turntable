# -*- coding: utf-8 -*-
import sys
sys.path.append (r'W:\WG\Shotgun_Studio\install\core\python')
sys.path.append("//srv-deadline2/DeadlineRepository6/api/python/Deadline")
import os
import sgtk
from sgtk.platform import Application
import maya.cmds as cmds
from pymel.core import *
import math
import DeadlineConnect as Connect
import inspect
shotName = None

import getpass
UserName = getpass.getuser()
ComputerName = os.environ['COMPUTERNAME']



def SaveChanges(): 
	# check if there are unsaved changes
	fileCheckState = cmds.file(q=True, modified=True)
	if fileCheckState:
		cmds.warning("Before continuing, save your scene")


def ExecTurntable():
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
	AssetRenderPathAndFileBase = AssetRenderFullPath.split('.')[0]
	AssetRenderPath = AssetRenderFullPath.rsplit('\\', 1)[0]
	AssetRenderFile = AssetRenderFullPath.split('\\')[-1]

	#GET PATH OF LAST VERSION OF TURNTABLE SCENE
	fields = ['id', 'code', 'sg_status_list']
	filters = [
		['project','is',{'type':'Project','id':66}],
		['id','is',1022]
		]
	asset= tk.shotgun.find_one("Asset",filters,fields)
	PublishTemplate = tk.templates['maya_asset_publish']
	listscenerender= []
	PublishsScenesPaths = tk.paths_from_template(PublishTemplate, asset)
	for PublishScene in PublishsScenesPaths:
		if "turntableCharacter" in PublishScene:
			listscenerender.append(PublishScene)
	listscenerender.sort()
	LastTurntablePath = listscenerender[-1]

	#==============================================================
	#RENDER TURNTABLE TD V0.02
	#==============================================================

	CurrentFolder = os.path.dirname(os.path.realpath(__file__))
	SaveChanges()
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

		CurrentMayaPath = PathWithoutFileName+"/"

		#OPEN SCENETURNTABLE
		cmds.file( LastTurntablePath, o=True )
		
		ImportPreviousScene = cmds.file(ScenePath, i=True, pn= True)  	
		cmds.parent( AssetName, 'locator_fix' )
		
		SceneTurnOutputName = AssetRenderFile.split('.')[0]+'_turn'
		cmds.file(rename =CurrentMayaPath+SceneTurnOutputName)
		cmds.file(save=True)

		#BOUNDING BOX CREATION
		
		locFixSel = cmds.listRelatives("locator_fix", allDescendents=True, noIntermediate=True, s=False, f=True)
		mySel =cmds.select(locFixSel)
		Isel = cmds.ls( selection=True,s=False )

		XMIN=[]
		YMIN=[]
		ZMIN=[]
		XMAX=[]
		YMAX=[]
		ZMAX=[]

		for i in Isel:
			if "Shape" in i:
				None
			else:
				IselBBox = cmds.xform(i, q=True ,bb=True )
				XMIN.append(IselBBox[0])
				YMIN.append(IselBBox[1])
				ZMIN.append(IselBBox[2])
				XMAX.append(IselBBox[3])
				YMAX.append(IselBBox[4])
				ZMAX.append(IselBBox[5])

		Xwidth =(max(XMAX)- min(XMIN))
		Ywidth =(max(YMAX)- min(YMIN))
		Zwidth =(max(ZMAX)- min(ZMIN))
		
		ratioHautMoitie = Ywidth/2

		heightBoundBoxMin= 2.193*Ywidth
		widthBoundBoxMin= 1.425* Xwidth
		
		if heightBoundBoxMin >=  widthBoundBoxMin:
			cmds.setAttr( "camWide.translateZ",heightBoundBoxMin)
		if heightBoundBoxMin <=  widthBoundBoxMin:
			cmds.setAttr( "camWide.translateZ",widthBoundBoxMin)
		
		cmds.setAttr( "camWide.translateY", ratioHautMoitie )
			
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
			
		heightToptoEyes = (max(YMAX)-EyesTrsY) 

		cmds.setAttr( "pivot_camCloseUp.translateX", EyesTrsX )
		cmds.setAttr( "pivot_camCloseUp.translateY", EyesTrsY )
		cmds.setAttr( "pivot_camCloseUp.translateZ", EyesTrsZ ) 

		cmds.parent( "pivot_camCloseUp", "pivot_head" )

		#cmds.setAttr( "camCloseUp.translateY", EyesTrsY )
		cmds.setAttr( "camCloseUp.translateZ", 7*heightToptoEyes- min(ZMIN) )
		#eyes one third from the top:
		# cmds.setAttr( "camCloseUp.translateY", EyesTrsY+ ((heightToptoEyes/3)*2))
		Zwide =getAttr( "camWide.translateZ" )
		Zcloseup =getAttr( "camCloseUp.translateZ" )
		CAM3Z = Zwide - ((Zwide-Zcloseup)/2)

		# cmds.setAttr( "camMiddle.translateZ", 2*Ywidth )
		cmds.setAttr( "camMiddle.translateZ", CAM3Z)

		cmds.setAttr("camMiddle.translateY",(ratioHautMoitie+EyesTrsY)/2)
		
		#CHECK IF CAM ORDER (FAR > NEAR IS OKAY, INVERT IF NOT )
		if Zwide < Zcloseup:
			cmds.setAttr("camWide.translateZ",Zcloseup)
			cmds.setAttr("camCloseUp.translateZ",Zwide)
			
		#SMOOTH MESHES under locator_fix
		locator_fix_ChildMeshes = cmds.listRelatives( 'locator_fix', ad=True, typ='mesh' )
		cmds.select( locator_fix_ChildMeshes )
		cmds.displaySmoothness( du=3, dv=3, pw=16, ps=4,po=3 )

		#SCENE PARAMETERS
		#HD720
		cmds.setAttr ("defaultResolution.width", 1280)
		cmds.setAttr ("defaultResolution.height", 720)
		cmds.setAttr ("defaultResolution.deviceAspectRatio",1.777)
		cmds.setAttr ("defaultResolution.pixelAspect", 1)

		#OUTPUT FRAMES NAME
		cmds.setAttr("defaultRenderGlobals.imageFilePrefix", AssetRenderFile.split('.')[0],type="string")

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
		#DEADLINE SUBMIT
		#==============================================================
		def submitturntable (CharName, CameraName, frameRangeInput ):
			# scenePath = CurrentMayaPath+CharName+"/"
			if not os.path.exists(AssetRenderPath):
				os.makedirs(AssetRenderPath)
			
			Deadline = Connect.DeadlineCon('srv-deadline2', 8080 )

			JobInfo = {
				"Name" : CharName + "_v_"+VersionKeyFormated+ " -" + "turntable" + "- " + CameraName,
				"UserName" : UserName,
				"Frames" : frameRangeInput,
				"Pool" : "maya",
				"Plugin" : "MayaCmd",
				"MachineName": ComputerName

				}
				
			PluginInfo = {
				"Version":"2013",
				"Build":"None",
				"StrictErrorChecking":"True",
				"LocalRendering":"False",
				"MaxProcessors":"0",
				"CommandLineOptions":"",
				"UseOnlyCommandLineOptions":"0",
				"IgnoreError211":"False",
				"SceneFile":PathWithoutFileName+"/"+SceneTurnOutputName+CameraName+".ma",
				"OutputFilePath":AssetRenderPath+"/",
				"Renderer":"MentalRay",
				"Priority":"50"

				}
				
			newJob = Deadline.Jobs.SubmitJob(JobInfo, PluginInfo,idOnly=False)
			print newJob["_id"]
			return newJob["_id"]

		JobID1 = submitturntable (AssetName,"Wide", "0-159" )
		JobID2 = submitturntable (AssetName,"Middle", "160-319x10" )
		JobID3 = submitturntable (AssetName,"CloseUp", "320-479x20" )
		JobsDepId = "%s,%s,%s" %(JobID1, JobID2, JobID3)

		# -------------------------------------------------------------------------------------------------
		# ADDING ONE JOB AS A DEPENDENCY
		# -------------------------------------------------------------------------------------------------
		
		def submitTurnChildJob ():
			Deadline = Connect.DeadlineCon('srv-deadline2', 8080 )
			JobInfo = {
				"Name" : AssetName+" Child Job - Make complete sequence ",
				"UserName" : UserName,
				"Frames" : 0,
				"Pool" : "small_tasks",
				"Plugin" : "Python",
				"MachineName": ComputerName,
				"JobDependencies": JobsDepId
			}

			PluginInfo = {
				"Version":2.7,
				"ScriptFile": os.path.abspath(CurrentFolder+"/FillMissingFiles03.py"),
				"Arguments":
				'entityTypeArg='+str(AssetType)+' '+
				'pathArg='+str(AssetRenderPath+"/")+' '+
				'nameArg='+str(AssetRenderFile.split('.')[0])+' '+
				'VersionArg='+str(VersionKeyFormated)+' '+
				'IDAssetArg='+str(AssetIdNumber)
			}

			newJob = Deadline.Jobs.SubmitJob(JobInfo, PluginInfo,idOnly=False)
			print newJob["_id"]
		
		childJob = submitTurnChildJob()