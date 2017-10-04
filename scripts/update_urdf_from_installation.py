#!/usr/bin/env python

import sys
import xmltodict
import os.path
import gzip
from shutil import copyfile

joints = []
joints.append("shoulder_pan_joint")
joints.append("shoulder_lift_joint")
joints.append("elbow_joint")
joints.append("wrist_1_joint")
joints.append("wrist_2_joint")
joints.append("wrist_3_joint")

def getList(data):
    data = data.replace("[", "")
    data = data.replace("]", "")
    return data.split(",")

def getSafetySettings(safetyData):
    splitData = safetyData.split("\n")

    strippedData = []
    for i in splitData:
        if i != "":
            strippedData.append(i.replace(" ", ""))

    dataDict = {}
    heading = ""
    for i in strippedData:
        if i.startswith("[") and i.endswith("]"):
            heading = i[1:-1]
        else:
            data = i.split("=")
            dataDict[heading + "." + data[0]] = data[1]

    return dataDict

def update_urdf(urdf_location, installation_location):
    if not os.path.isfile(urdf_location):
        print "Invalid URDF Location"
        return
    if not os.path.isfile(installation_location):
        print "Invalid Installation Location"
        return

    #try:
    urdf_file = open(urdf_location)
    urdf_dict = xmltodict.parse(urdf_file.read())
    urdf_file.close()

    for macro in urdf_dict["robot"]["xacro:macro"]:
        if macro["@name"] == "ur10_robot" or macro["@name"] == "ur5_robot" or macro["@name"] == "ur3_robot":
            for joint in macro["joint"]:
                try:
                    for i in range(len(joints)):
                        if joints[i] in joint["@name"]:
                            print str(i) + " - " + joint["@name"]
                except:
                    pass
    #except:
    #    print "Error Parsing URDF "
#        return

    try:
        install_xml = installation_location[:installation_location.rindex(".")] + ".xml"
        inF = gzip.open(installation_location, 'rb')
        outF = open(install_xml, 'wb')
        outF.write( inF.read() )
        inF.close()
        outF.close()
    except:
        print "Error Extracting Installation File"
        return

    try:
        install_file = open(install_xml)
        install_dict = xmltodict.parse(install_file.read())
        install_file.close()
    except:
        print "Error Parsing Installation"
        return

    safety_dict = getSafetySettings(install_dict["Installation"]["SafetySettings"])

    copyfile(urdf_location, urdf_location + ".BKP")

if __name__ == '__main__':

    device = 'default'

    args = sys.argv[1:]

    if len(args) != 2:
        print('usage: update_urdf_from_installation.py <urdf_location> <installation_location>')
        sys.exit(2)

    update_urdf(args[0], args[1])
