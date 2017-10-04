#!/usr/bin/env python

import sys
import xmltodict
import os.path
import gzip

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
        print "INVALID URDF LOCATION"
        return
    if not os.path.isfile(installation_location):
        print "INVALID INSTALLATION LOCATION"
        return

    urdf_file = open(urdf_location)
    urdf_dict = xmltodict.parse(urdf_file.read())
    urdf_file.close()
    #print(xmltodict.unparse(urdf_dict, pretty=True))

    install_xml = installation_location[:installation_location.rindex(".")] + ".xml"
    inF = gzip.open(installation_location, 'rb')
    outF = open(install_xml, 'wb')
    outF.write( inF.read() )
    inF.close()
    outF.close()

    install_file = open(install_xml)
    install_dict = xmltodict.parse(install_file.read())
    install_file.close()
    safety_dict = getSafetySettings(install_dict["Installation"]["SafetySettings"])

if __name__ == '__main__':

    device = 'default'

    args = sys.argv[1:]

    if len(args) != 2:
        print('usage: update_urdf_from_installation.py <urdf_location> <installation_location>')
        sys.exit(2)

    update_urdf(args[0], args[1])
