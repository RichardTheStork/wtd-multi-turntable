# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform import Application
import sys
sys.path.append (r'W:\WG\Shotgun_Studio\install\core\python')

import os, sys, inspect
# realpath() will make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

# use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"subfolder")))
if cmd_subfolder not in sys.path:
	sys.path.insert(0, cmd_subfolder)


# import wtd.deadline as MDeadline

from python import turntable
# import turntable

reload(turntable)

shotName = None

class StgkTurntableApp(Application):
	"""
	The app entry point. This class is responsible for intializing and tearing down
	the application, handle menu registration etc.
	"""
	
	def init_app(self):
		"""
		Called as the application is being initialized
		"""
		if self.context.entity is None:
			raise tank.TankError("Cannot load the Set Frame Range application! "
								 "Your current context does not have an entity (e.g. "
								 "a current Shot, current Asset etc). This app requires "
								 "an entity as part of the context in order to work.")
		self.engine.register_command("TurntableTD", self.run_app)

	 
	def destroy_app(self):
		self.log_debug("Destroying StgkTurntableApp")

	def run_app(self):
		# turntable = self.import_module("turntable")
		
		turntable.ExecTurntable()
		# present a pyside dialog
		# lazy import so that this script still loads in batch mode
		"""
		message = " Turntable sent \n"
		from tank.platform.qt import QtCore, QtGui
		QtGui.QMessageBox.information(None,"TD Message", message)
		"""