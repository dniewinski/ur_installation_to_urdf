#!/usr/bin/env python

import sys
import xmltodict
import os.path
import gzip
from shutil import copyfile

pi = 3.14159265359

joints = []
joints.append(("shoulder_pan_joint", "shoulder_pan_lower_limit", "shoulder_pan_upper_limit"))
joints.append(("shoulder_lift_joint", "shoulder_lift_lower_limit", "shoulder_lift_upper_limit"))
joints.append(("elbow_joint", "elbow_joint_lower_limit", "elbow_joint_upper_limit"))
joints.append(("wrist_1_joint", "wrist_1_lower_limit", "wrist_1_upper_limit"))
joints.append(("wrist_2_joint", "wrist_2_lower_limit", "wrist_2_upper_limit"))
joints.append(("wrist_3_joint", "wrist_3_lower_limit", "wrist_3_upper_limit"))

def getJointLimit(position, revolutions):
    return float(position) + float(revolutions) * pi * 2

def getList(data):
    data = data.replace("[", "")
    data = data.replace("]", "")
    return data.split(",")

def getSafetySettings(safetyData):
    splitData = safetyData.split("\n")

    strippedData = []
    for i in splitData:
        if i != "":
            string = i.strip().replace(" ", "")
            strippedData.append(string)

    dataDict = {}
    heading = ""
    for i in strippedData:
        if i.startswith("[") and i.endswith("]"):
            heading = i[1:-1]
        else:
            data = i.split("=")
            dataDict[heading + "." + data[0]] = data[1]

    return dataDict

def update_urdf_data(urdf_dict, install_dict, urdf_location, type):
    print "####################################"
    print "            " + type
    print "####################################"
    new_robot_params = "prefix joint_limited"
    max_force = install_dict["SafetyLimits" + type + "Values.maxForce"]
    maxJointSpeed = getList(install_dict["SafetyLimits" + type + "Joints.maxJointSpeed"])
    minJointPosition = getList(install_dict["SafetyLimits" + type + "Joints.minJointPosition"])
    maxJointPosition = getList(install_dict["SafetyLimits" + type + "Joints.maxJointPosition"])
    minJointRevolutions = getList(install_dict["SafetyLimits" + type + "Joints.minJointRevolutions"])
    maxJointRevolutions = getList(install_dict["SafetyLimits" + type + "Joints.maxJointRevolutions"])

    for macro in urdf_dict["robot"]["xacro:macro"]:
        if macro["@name"] == "ur10_robot" or macro["@name"] == "ur5_robot" or macro["@name"] == "ur3_robot":
            #print macro["@params"]
            for joint in macro["joint"]:
                try:
                    for i in range(len(joints)):
                        if joints[i][0] in joint["@name"]:
                            print ">>>>>>>>>>>>>>>>"
                            print str(i) + " - " + joint["@name"]
                            upperLimit = getJointLimit(maxJointPosition[i], maxJointRevolutions[i])
                            lowerLimit = getJointLimit(minJointPosition[i], minJointRevolutions[i])
                            speedLimit = maxJointSpeed[i]
                            forceLimit = max_force
                            print "lowerLimit = " + str(lowerLimit)
                            print "upperLimit = " + str(upperLimit)
                            print "speedLimit = " + str(speedLimit)
                            print "forceLimit = " + str(forceLimit)

                            new_robot_params = new_robot_params + " " + joints[i][1] + ":=" + str(lowerLimit)
                            new_robot_params = new_robot_params + " " + joints[i][2] + ":=" + str(upperLimit)
                            joint["xacro:if"]["limit"]["@effort"] = str(forceLimit)
                            joint["xacro:if"]["limit"]["@velocity"] = str(speedLimit)
                except:
                    pass
            macro["@params"] = new_robot_params

    out_file_name = urdf_location[:urdf_location.rindex(".urdf.xacro")] + "_" + type + ".urdf.xacro"
    print "SAVING TO " + out_file_name

    outFile = open(out_file_name, 'w')
    outFile.write(xmltodict.unparse(urdf_dict, pretty=True))
    outFile.close()
    
def update_urdf(urdf_location, installation_location):
    if not os.path.isfile(urdf_location):
        print "Invalid URDF Location"
        return
    if not os.path.isfile(installation_location):
        print "Invalid Installation Location"
        return

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

    try:
        urdf_file = open(urdf_location)
        urdf_dict = xmltodict.parse(urdf_file.read())
        urdf_file.close()
    except:
        print "Error Parsing URDF "
        return

    update_urdf_data(urdf_dict, safety_dict, urdf_location, "Normal")
    update_urdf_data(urdf_dict, safety_dict, urdf_location, "Reduced")

if __name__ == '__main__':

    device = 'default'

    args = sys.argv[1:]

    if len(args) != 2:
        print('usage: update_urdf_from_installation.py <urdf_location> <installation_location>')
        sys.exit(2)

    update_urdf(args[0], args[1])
