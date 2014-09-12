import shutil, sys
import os
import subprocess
import ssl
import sys
sys.path.append (r'W:\WG\Shotgun_Studio\install\core\python')
import sgtk


tempVars = sys.argv

# ----------------------------------
# -----------FILL SEQUENCE ---------
# ----------------------------------

# path= tempVars[1]
# path = path.replace('pathArg=','')
path = "W:/RTS/Renders/_Library/mod/Character/claudius/publish/maya/v000/claudius_mod_v000/"
# name = tempVars[2]
# name = name.replace('nameArg=','')
name = "claudius_mod_v000_turn"

# IDAsset = tempVars[3]
# IDAsset = IDAsset.replace('IDAssetArg=','')

IDAsset = 852

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

folderClean = "EXR_IMG"
RndIn = path+name
RndOut = path+folderClean+"/"+name

RndInMov = path+folderClean+"/"+name+".%04d"+ext
RndOutMov = path+folderClean+"/"+name+".mov"

iconvertPath = r"W:/WG/WTD_Code/trunk/wtd/pipeline/resources/OpenImageIO_bin/iconvert.exe"

FrameRangeGlobal = range (0,479)

if not os.path.exists(path+folderClean):
    os.makedirs(path+folderClean)
	
# CONVERSION FFMPEG MOV
ffmpegPath = r"W:/WG/WTD_Code/trunk/wtd/pipeline/resources/ffmpeg/bin/ffmpeg.exe" 
try:
	os.system('%s -f image2 -i "%s" -vcodec libx264 -pix_fmt yuv420p -r 25 "%s"' %(ffmpegPath,RndIn,RndOutMov ))
except:
	pass

if not os.path.exists(RndOutMov):
	# IF FILE MOV DOESN'T EXIST: CONVERSION EXR to EXR (tiled to scanline) , THEN RECONVERT
	for i in FrameRangeGlobal:
		DigitsFormat="%04d"%i
		RndInConv = RndIn+"."+DigitsFormat+".exr"
		RndOutConv = RndOut+"."+DigitsFormat+".exr"
		subprocess.call('%s -v --scanline "%s" "%s"' %(iconvertPath,RndInConv,RndOutConv )) 
	os.system('%s -f image2 -i "%s" -vcodec libx264 -pix_fmt yuv420p -r 25 "%s"' %(ffmpegPath,RndInMov,RndOutMov )) 
	
	
	
# ----------------------------------------------
# UPLOAD QUICKTIME
# ----------------------------------------------	
	
SERVER_PATH = 'https://rts.shotgunstudio.com'
SCRIPT_USER = 'AutomateStatus_TD'
SCRIPT_KEY = '8119086c65905c39a5fd8bb2ad872a9887a60bb955550a8d23ca6c01a4d649fb'

# sg = Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
sg = sgtk.api.shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

# quicktime = 'C:/Users/tdelbergue/Desktop/claudius_mod_v000_turntable.mov'

'''
filters = [ ['project','is', {'type':'Project','id':66}],
         ['entity','is',{'type':'Asset','id':831}]]
		 
task = sg.find_one('Task',filters)
'''
data = {'project': {'type':'Project','id':66},
         'entity': {'type':'Asset', 'id':int(IDAsset)}}
	 
result = sg.create('Version', data)
executed = sg.upload("Version",result['id'],RndOutMov,'sg_uploaded_movie')
print executed
