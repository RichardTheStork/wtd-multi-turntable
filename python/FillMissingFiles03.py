import shutil, sys
import os
import subprocess
import ssl
import sys
from sys import platform as _platform
sys.path.append (r'W:/WG/Shotgun_Studio/install/core/python')
import sgtk


tempVars = sys.argv

# ----------------------------------
# -----------FILL SEQUENCE ---------
# ----------------------------------
EntType = tempVars[1]
EntType = EntType.replace('entityType=','')

path= tempVars[2]
path = path.replace('pathArg=','')
#path = "C:/Users/tdelbergue/Desktop/mini_turn/"

name = tempVars[3]
name = name.replace('nameArg=','')
#name = "claudius_mod_v000_turntable."

versionScene = tempVars[4]
versionScene = versionScene.replace('VersionArg=','')

IDAsset = tempVars[5]
IDAsset = IDAsset.replace('IDAssetArg=','')



# print "EntType"
# print EntType
# print "name"
# print name


ext= ".png"

step01 = 10
step02 = 20

liststep01 = range(160,319,step01)
liststep02 = range(320,479,step02)

def FillMissingFiles(path,name,ext,liststep,step):      
	for i in liststep:
		for u in range(1,step):
			#DigitsFormat= '%04d' i
			DigitsFormat="%04d"%i
			CopiesNum = (i+u)
			shutil.copy(path+name+"."+str(DigitsFormat)+ext, path+name+"."+str("%04d"%CopiesNum)+ext)
		
FillMissingFiles(path,name,ext,liststep01,step01)
FillMissingFiles(path,name,ext,liststep02,step02)

#ICONVERT EXR SCANLINE

# path ="C:/Users/tdelbergue/Desktop/ball/"
# path ="C:/Users/tdelbergue/Desktop/ALL_TURN_480/"
# name = "mvmt_ball00_"
# name = "claudius_mod_v000_turntable"

# RndIn = path+name+".%04d.exr"
# RndIn = path+name+".0001.exr"

# folderClean = "EXR_IMG"
folderClean = ""
RndIn = path+name
RndOut = path+folderClean+"/"+name

# RndInMov = path+folderClean+"/"+name+".%04d"+ext
RndInMov = os.path.join(path, name+".%04d"+ext)
RndInMov = os.path.normpath(RndInMov)

# RndOutMov = path+folderClean+"/"+name+".mov"
RndOutMov = os.path.join(path,name+".mov")
RndOutMov = os.path.normpath(RndOutMov)

print 50*"-"
print RndInMov
print RndOutMov
print 50*"-"

iconvertPath = r"W:/WG/WTD_Code/trunk/wtd/pipeline/resources/OpenImageIO_bin/iconvert.exe"

FrameRangeGlobal = range (0,479)

if not os.path.exists(path+folderClean):
    os.makedirs(path+folderClean)
	
# CONVERSION FFMPEG MOV
if os.path.isfile(RndOutMov):
    os.remove(RndOutMov)
	
ffmpegPath = ""
try:
	ffmpegPath = r'%s/ffmpeg.exe' %os.environ["FFMPEG_PATH"] 
except:
	ffmpegPath = r'ffmpeg.exe'
	
try:
	subprocess.call('%s -i "%s" -vcodec libx264 -pix_fmt yuv420p -r 25 "%s"' %(ffmpegPath,RndInMov,RndOutMov ))
	# os.system('%s -f image2 -i "%s" -vcodec libx264 -pix_fmt yuv420p -r 25 "%s"' %(ffmpegPath,RndInMov,RndOutMov ))
	# os.system('%s -f image2 -i "%s" -vcodec libx264 -pix_fmt yuv720p -r 25 "%s"' %(ffmpegPath,RndInMov,RndOutMov ))
except:
	pass
"""
if not os.path.exists(RndOutMov):
	# IF FILE MOV DOESN'T EXIST: CONVERSION EXR to EXR (tiled to scanline) , THEN RECONVERT
	for i in FrameRangeGlobal:
		DigitsFormat="%04d"%i
		RndInConv = RndIn+"."+DigitsFormat+".exr"
		RndOutConv = RndOut+"."+DigitsFormat+".exr"
		subprocess.call('%s -v --scanline "%s" "%s"' %(iconvertPath,RndInConv,RndOutConv )) 
	os.system('%s -f image2 -i "%s" -vcodec libx264 -pix_fmt yuv420p -r 25 "%s"' %(ffmpegPath,RndInMov,RndOutMov )) 
"""	
	
	
# ----------------------------------------------
# UPLOAD QUICKTIME
# ----------------------------------------------	
	
if _platform == "win32":
	ProjectPath= "W:\WG\Shotgun_Configs\RTS_Master"
	
elif _platform == "linux" or _platform == "linux2":
    ProjectPath="/srv/projects/rts/WG/Shotgun_Configs/RTS_Master"
	
else:
	ProjectPath= "W:\WG\Shotgun_Configs\RTS_Master"

tk = sgtk.sgtk_from_path(ProjectPath)

'''
filters = [ ['project','is', {'type':'Project','id':66}],
         ['entity','is',{'type':'Asset','id':831}]]
		 
task = tk.shotgun.find_one('Task',filters)
'''
data = {'project': {'type':'Project','id':66},
		'entity': {'type':'Asset', 'id':int(IDAsset)},
		'code': str(name),
		'sg_path_to_frames':RndInMov,
		'sg_path_to_movie':RndOutMov
		}

	 
result = tk.shotgun.create('Version', data)
executed = tk.shotgun.upload("Version",result['id'],RndOutMov,'sg_uploaded_movie')
print executed