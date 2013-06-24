#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2012 Francisco Pina Martins <f.pinamartins@gmail.com>
# This file is part of Radeon-tray.
# Radeon-tray is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Radeon-tray is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Radeon-tray.  If not, see <http://www.gnu.org/licenses/>.

import sys
from os import path, getegid
from PyQt4 import QtGui, QtCore
import zmq

PORT = "5556"
CONTEXT = None
SOCKET = None

PROFILE_PATH = path.join(path.dirname(__file__), "last_power_profile")
METHOD_PATH = path.join(path.dirname(__file__), "last_power_method")
HIGHPATH = path.join(path.dirname(__file__), "high.svg")
MIDPATH = path.join(path.dirname(__file__), "mid.svg")
LOWPATH = path.join(path.dirname(__file__), "low.svg")
AUTOPATH = path.join(path.dirname(__file__), "auto.svg")
DYNPMPATH = path.join(path.dirname(__file__), "dynpm.svg")
DEFAULTPATH = path.join(path.dirname(__file__), "default.svg")
NOPERM = """"You don't have the permission to write card's
settings, check the official site for information!"""

class SystemTrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, icon, parent, method, profile, cards, temp_path):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)

        self.setToolTip("Radeon-Tray")
        self.method = method
        self.profile = profile
        self.cards = cards

        menu = QtGui.QMenu(parent)

        self.temp_path = temp_path

        if method == "dynpm":
            current_methodAction = menu.addAction(QtGui.QIcon("dynpm.svg"), "Current power method: " + method)
        else:
            current_methodAction = menu.addAction(QtGui.QIcon(profile + ".svg"), "Current power method: " + method)
        current_methodAction.setStatusTip("Click to toggle between profile and dynpm modes.")

        current_methodAction.triggered.connect(lambda: current_methodAction.setIcon(QtGui.QIcon(profile + ".svg")) if current_methodAction.text() == "Current power method: dynpm" else current_methodAction.setIcon(QtGui.QIcon("dynpm.svg")))
        current_methodAction.triggered.connect(lambda: power_method_set("profile", cards) if current_methodAction.text() == "Current power method: dynpm" else power_method_set("dynpm", cards))
        current_methodAction.triggered.connect(lambda: self.setIcon(QtGui.QIcon(profile + ".svg")) if current_methodAction.text() == "Current power method: dynpm" else self.setIcon(QtGui.QIcon("dynpm.svg")))
        current_methodAction.triggered.connect(lambda: current_methodAction.setText("Current power method: profile") if current_methodAction.text() == "Current power method: dynpm" else current_methodAction.setText("Current power method: dynpm"))

        sep0 = menu.addSeparator()

        self.high_action = menu.addAction(QtGui.QIcon(HIGHPATH), "High Power")
        self.high_action.triggered.connect(self.activate_high)

        self.mid_action = menu.addAction(QtGui.QIcon(MIDPATH), "Mid Power")
        self.mid_action.triggered.connect(self.activate_mid)

        self.lowAction = menu.addAction(QtGui.QIcon(LOWPATH), "Low Power")
        self.lowAction.triggered.connect(self.activate_low)

        self.autoAction = menu.addAction(QtGui.QIcon(AUTOPATH), "Auto")
        self.autoAction.triggered.connect(self.activate_auto)

        self.dynpmAction = menu.addAction(QtGui.QIcon(DYNPMPATH), "Dynpm")
        self.dynpmAction.triggered.connect(self.activate_dynpm)

        sep1 = menu.addSeparator()

        self.temp_label = menu.addAction(temp_checker(temp_path))

        sep2 = menu.addSeparator()

        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.checkStatus()

        self.setContextMenu(menu)

        # Connect object to activated signal to grab single click
        # on tray icon
        QtCore.QObject.connect(
            self,
            QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"),
            self.show_status)

    def activate_high(self):
        """Activate high profile
        """
        if not power_method_set("profile", self.cards) or\
            not power_profile_set("high", self.cards):
                self.showMessage("Error",
                    NOPERM, self.Critical, 10000)
                return
        self.setIcon(QtGui.QIcon(HIGHPATH))
        self.lowAction.setEnabled(True)
        self.mid_action.setEnabled(True)
        self.high_action.setEnabled(False)
        self.autoAction.setEnabled(True)
        self.dynpmAction.setEnabled(True)

    def activate_mid(self):
        """Activate mid profile
        """
        if not power_method_set("profile", self.cards) or\
            not power_profile_set("mid", self.cards):
                self.showMessage("Error",
                    NOPERM, self.Critical, 10000)
                return
        self.setIcon(QtGui.QIcon(MIDPATH))
        self.lowAction.setEnabled(True)
        self.mid_action.setEnabled(False)
        self.high_action.setEnabled(True)
        self.autoAction.setEnabled(True)
        self.dynpmAction.setEnabled(True)

    def activate_low(self):
        """Activate low profile
        """
        if not power_method_set("profile", self.cards) or\
            not power_profile_set("low", self.cards):
                self.showMessage("Error",
                    NOPERM, self.Critical, 10000)
                return
        self.setIcon(QtGui.QIcon(LOWPATH))
        self.lowAction.setEnabled(False)
        self.mid_action.setEnabled(True)
        self.high_action.setEnabled(True)
        self.autoAction.setEnabled(True)
        self.dynpmAction.setEnabled(True)

    def activate_auto(self):
        """Activate auto profile
        """
        if not power_method_set("profile", self.cards) or\
            not power_profile_set("auto", self.cards):
                self.showMessage("Error",
                    NOPERM, self.Critical, 10000)
                return
        self.setIcon(QtGui.QIcon(AUTOPATH))
        self.lowAction.setEnabled(True)
        self.mid_action.setEnabled(True)
        self.high_action.setEnabled(True)
        self.autoAction.setEnabled(False)
        self.dynpmAction.setEnabled(True)

    def activate_dynpm(self):
        """Activate dynpm method with default profile
        """
        if not power_profile_set("default", self.cards) or\
            not power_method_set("dynpm", self.cards):
                self.showMessage("Error",
                    NOPERM, self.Critical, 10000)
                return
        self.setIcon(QtGui.QIcon(DYNPMPATH))
        self.lowAction.setEnabled(True)
        self.mid_action.setEnabled(True)
        self.high_action.setEnabled(True)
        self.autoAction.setEnabled(True)
        self.dynpmAction.setEnabled(False)

    def checkStatus(self):
        if self.profile == "low":
            self.lowAction.setEnabled(False)
            self.setIcon(QtGui.QIcon(LOWPATH))
        if self.profile == "mid":
            self.mid_action.setEnabled(False)
            self.setIcon(QtGui.QIcon(MIDPATH))
        if self.profile == "high":
            self.high_action.setEnabled(False)
            self.setIcon(QtGui.QIcon(HIGHPATH))
        if self.profile == "auto":
            self.autoAction.setEnabled(False)
            self.setIcon(QtGui.QIcon(AUTOPATH))
        if self.method == "dynpm":
            self.dynpmAction.setEnabled(False)
            self.setIcon(QtGui.QIcon(DYNPMPATH))


    def show_status(self, act_reas):
        """Show current card status

        Reasons:
            0: unknown reason
            1: request for the context menu
            2: double clicked
            3: one click
            4: click with the middle button

        Icons:
            NoIcon, Information, Warning, Critical
        """
        if act_reas == 3:
            self.showMessage("Radeon-INFO",
                radeon_info_get(), self.Information, 10000)



        self.activated.connect(self.click_trap)

    def click_trap(self, val):
        if val == 1:
            t = temp_checker(self.temp_path)
            self.temp_label.setText(t)

def temp_location():
    """
    Tests a few paths for card temperature
    """
    path_list = ["/sys/class/drm/card0/device/hwmon/hwmon1/temp1_input"]
    temp_path = ""
    for paths in path_list:
        if path.exists(paths):
            temp_path = paths

    return temp_path

def temp_checker(temp_path):
    if temp_path == "":
        return "No temperature info"
    temperature = open(temp_path,'r').read()
    temp = str(int(temperature) / 1000) + "ºC"
    return temp

def main():
    #Main function
    cards = verifier()
    init_method, init_profile = power_status_get()
    temp_path = temp_location()
    l_method, l_profile = last_power_status_get()

    # Check if is lost the last configuration
    if l_method != init_method and l_profile != init_profile:
        power_profile_set(l_profile, cards)
        power_method_set(l_method, cards)

    init_method, init_profile = power_status_get()

    if init_method == "dynpm":
        icon = DYNPMPATH
    else:
        icon = DEFAULTPATH

    app = QtGui.QApplication(sys.argv)

    w = QtGui.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon(icon), w, init_method, init_profile, cards, temp_path)

    trayIcon.show()
    sys.exit(app.exec_())

def verifier():
    #First we verify how many cards we are dealing with, if any. Quit if none
    #are found.
    if SOCKET is not None:
        SOCKET.send("verifier")
        message = SOCKET.recv()
        return int(message)

    cards = 0
    if path.isdir("/sys/class/drm/card0"):
        cards += 1
    if path.isdir("/sys/class/drm/card1"):
        cards += 1
    if cards == 0:
        sys.exit("No suitable cards found.\nAre you using the OSS Radeon \
drivers?\nExiting the program.")
    return cards

def temp_location():
    """Tests a few paths for card temperatur
    """
    paths_list = ["/sys/class/drm/card0/device/hwmon/hwmon1/temp1_input"]
    temp_path = ""
    for tpath in paths_list:
        if path.exists(tpath):
            temp_path = tpath

    return temp_path

def temp_checker(temp_path):
    if temp_path == "":
        return "No temperature info"
    with open(temp_path, "r") as f:
        temperature = f.read()
    temp = str(int(temperature) / 1000) + "°C"
    return temp

def radeon_info_get():
    """Get the power info
    """
    if SOCKET is not None:
        SOCKET.send("info")
        message = SOCKET.recv()
        return message

    cards = verifier()
    radeon_info = ""
    for xx in range(cards):
        radeon_info += "----- Card%d -----\n" % xx
        radeon_info += "Power method: %s\nPower profile: %s\n" % power_status_get(xx)
        radeon_info += temp_checker(temp_location()) + "\n"
        try:
            with open("/sys/kernel/debug/dri/"+str(xx)+"/radeon_pm_info","r") as ff:
                radeon_info += ff.read().strip()
        except IOError:
            radeon_info += "\nYou need root privileges\nfor more information"
        radeon_info += "\n---------------"
    return radeon_info


def power_status_get(num=0):
    """Get the power status. Uses with to close the file immediatelly
    """
    if SOCKET is not None:
        SOCKET.send("powerstatus")
        message = SOCKET.recv()
        return message.split(",")
    with open("/sys/class/drm/card"+str(num)+"/device/power_method","r") as f:
        power_method = f.readline().strip()
    with open("/sys/class/drm/card"+str(num)+"/device/power_profile","r") as f:
        power_profile = f.readline().strip()
    return power_method, power_profile

def last_power_status_get():
    """Get the last power status
    """
    if SOCKET is not None:
        SOCKET.send("lastpowerstatus")
        message = SOCKET.recv()
        return message.split(",")
    with open(METHOD_PATH, "r") as f:
        power_method = f.readline().strip()
    with open(PROFILE_PATH, "r") as f:
        power_profile = f.readline().strip()
    return power_method, power_profile

def power_profile_set(new_power_profile, cards):
    """Change the power profile
    """
    if SOCKET is not None:
        SOCKET.send("setprofile:"+new_power_profile)
        message = SOCKET.recv()
        return bool(message)
    try:
        for i in range(cards):
            with open("/sys/class/drm/card"+str(i)+"/device/power_profile","w") as f:
                f.write(new_power_profile)
        with open(PROFILE_PATH, "w") as fs:
            fs.write(new_power_profile)
    except IOError:
        return False
    return True


def power_method_set(new_power_method, cards):
    """Change the power method
    """
    if SOCKET is not None:
        SOCKET.send("setmethod:"+new_power_method)
        message = SOCKET.recv()
        return bool(message)
    try:
        for i in range(cards):
            with open("/sys/class/drm/card"+str(i)+"/device/power_method","w") as f:
                f.write(new_power_method)
        with open(METHOD_PATH, "w") as fs:
            fs.write(new_power_method)
    except IOError:
        return False
    return True



if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "client":
            CONTEXT = zmq.Context()
            SOCKET = CONTEXT.socket(zmq.REQ)
            SOCKET.connect("tcp://localhost:%s" % PORT)
    main()