import shutil, sys
import os, datetime
import subprocess
import ssl
import sys
sys.path.append (r'W:/WG/Shotgun_Studio/install/core/python')
import sgtk

import tank
from tank import Hook
from tank import TankError

SERVER_PATH = 'https://rts.shotgunstudio.com'
SCRIPT_USER = 'AutomateStatus_TD'
SCRIPT_KEY = '8119086c65905c39a5fd8bb2ad872a9887a60bb955550a8d23ca6c01a4d649fb'

# sg = Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
sg = sgtk.api.shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)


# wtd_fw = self.load_framework("tk-framework-wtd_v0.x.x")
# ffmpeg = wtd_fw.import_module("pipeline.ffmpeg")


FFMPEG_env = os.environ.get('FFMPEG_PATH')
ffmpegPath = str(FFMPEG_env)+"/ffmpeg"

ffmpegPathNew = os.path.normpath(ffmpegPath)

print FFMPEG_env
print ffmpegPathNew

value = subprocess.call('%s -f lavfi -i color=c=black:s="%s" -vframes 1 "%s"' %(ffmpegPathNew,"1280x720","W:/RTS/People/Tdelbergue/test.png"))


def ffmpegMakingSlates(inputFilePath, outputFilePath, audioPath = "", topleft = "", topmiddle = "", topright = "", bottomleft = "", bottommiddle = "", bottomright = "", ffmpegPath = ffmpegPathNew, font = "arial.ttf", font_size = 16, font_color = "white", slate_height = 21, slate_color = "black@1.0", overwrite = True, logLevel = "verbose"):
	
	top = "%s/5.0" %slate_height
	bottom = "h-(%s-%s/5.0-1)" %(slate_height, slate_height)
	if overwrite:
		overwrite = "-y"
	else:
		overwrite = ""
	
	logLevel = "-loglevel %s " %logLevel
	
	command_line_arguments = '{ffmpeg} {logLevel}-f image2 -i "{input}" -vf "drawbox=x=-{slate_height}:y=0:w=20000:h=0:color={slate_color}:t={slate_height},\
	drawtext=fontsize={font_size}:fontfile={font}: text={topleft}: x={left}: y={top}: fontcolor={font_color},\
	drawtext=fontsize={font_size}:fontfile={font}:text={topmiddle}: x={middle}: y={top}: fontcolor={font_color},\
	drawtext=fontsize={font_size}:fontfile={font}:text={topright}: x={right}: y={top}: fontcolor={font_color},\
	drawtext=fontsize={font_size}:fontfile={font}:text={bottomleft}: x={left}: y={bottom}: fontcolor={font_color},\
	drawtext=fontsize={font_size}:fontfile={font}:text={bottommiddle}: x={middle}: y={bottom}: fontcolor={font_color},\
	drawtext=fontsize={font_size}:fontfile={font}:text={bottomright}: x={right}: y={bottom}: fontcolor={font_color}"\
	"{output}" {overwrite}'.format(
		ffmpeg=ffmpegPath, input=inputFilePath, output=outputFilePath, 
		topleft=topleft, topmiddle=topmiddle, topright=topright ,bottomleft=bottomleft, bottommiddle=bottommiddle, bottomright=bottomright, 
		left= "5",middle= "(w-tw)/2", right= "(w-tw)-5", top="%s/5.0" %slate_height, bottom="h-(%s-%s/5.0-1)" %(slate_height, slate_height), 
		font=font, font_size=font_size, font_color=font_color, 
		slate_height=slate_height, slate_color=slate_color, overwrite = overwrite, logLevel = logLevel
		)
	value = subprocess.call(command_line_arguments, creationflags=CREATE_NO_WINDOW, shell=False)
	return value




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

# -----	
#SLATES 
#------	
Film = "Richard the Stork"
#GET CURRENT DATE
today = datetime.date.today()
todaystr = today.isoformat()
#Get USER
# USER = sgtk.util.get_current_user(tk)	
	


for i in FrameRangeGlobal:
	DigitsFormat="%04d"%i
	ffmpegMakingSlates(inputFilePath= path+name+"."+str(DigitsFormat)+ext	, outputFilePath= path+name+"."+str(DigitsFormat)+ext	, topleft = name, topmiddle = Film, topright = str(FrameRangeGlobal[0])+"-"+str(DigitsFormat)+"-"+str(FrameRangeGlobal[-1]), bottomleft = EntType, bottommiddle = "", bottomright = todaystr , ffmpegPath =ffmpegPathNew, font = "arial.ttf"  )

	
# CONVERSION FFMPEG MOV
if os.path.isfile(RndOutMov):
	os.remove(RndOutMov)
	
try:
	os.system('%s -i "%s" -vcodec libx264 -pix_fmt yuv420p -r 25 "%s"' %(ffmpegPath,RndInMov,RndOutMov ))
	# os.system('%s -f image2 -i "%s" -vcodec libx264 -pix_fmt yuv420p -r 25 "%s"' %(ffmpegPath,RndInMov,RndOutMov ))
	# os.system('%s -f image2 -i "%s" -vcodec libx264 -pix_fmt yuv720p -r 25 "%s"' %(ffmpegPath,RndInMov,RndOutMov ))
except:
	pass

	
	
# ----------------------------------------------
# UPLOAD QUICKTIME
# ----------------------------------------------

'''

# quicktime = 'C:/Users/tdelbergue/Desktop/claudius_mod_v000_turntable.mov'


data = {'project': {'type':'Project','id':66},
		'entity': {'type':'Asset', 'id':int(IDAsset)},
		'code': str(name),
		'sg_path_to_frames':RndInMov,
		'sg_path_to_movie':RndOutMov
		}

	 
result = sg.create('Version', data)
executed = sg.upload("Version",result['id'],RndOutMov,'sg_uploaded_movie')
print executed
'''