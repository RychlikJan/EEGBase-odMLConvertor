
import sys
import os
import xml.etree.ElementTree as ET
from xml.etree import ElementTree
import mne
import odml
import nixio as nix



def iterparent(tree):
    for parent in tree.iter():
        for child in parent:
            yield parent, child


def removeOne(root):
    for parent, child in iterparent(root):
        if "http://www.g-node.org/guiml" in child.tag:
            parent.remove(child)


def xmlParser(xmlName):
    xmlFile = ET.parse(xmlName)
    root = xmlFile.getroot()
    print("tested")
    i = 1
    while i == 1:
        removeOne(root)
        i = 0
        for child in root.iter():
            if "http://www.g-node.org/guiml" in child.tag:
                i = 1
    ElementTree.dump(root)


def fileExist(path):
    try:
        f = open(path)
        f.close()
    except IOError as e:
        return 0
    return 1


def allVhdrFiles(path):
    files=[]
    for r, d, f in os.walk(path):
        for file in f:
            if '.vhdr' in file:
                files.append(os.path.join(r, file))

    for f in files:
        pathEgg = f.split(".")
        pathVmrk = f.split(".")
        pathEgg[0] = pathEgg[0] + ".eeg"
        pathVmrk[0] = pathVmrk[0]+ ".vmrk"
        existEeg = fileExist(pathEgg[0])
        existVmrk = fileExist(pathVmrk[0])
        if existEeg == 0 or existVmrk == 0:
            files.remove(f)
    return files


def main():
    args = sys.argv
    if len(args) == 1:
        print("use like an argument path into folder with measurement")
        sys.exit()
    if fileExist(args[1]+"/metadata.xml") == 0:
        print("metadata.xml file not found")
        sys.exit()
    vhdrFiles = allVhdrFiles(args[1]+"/Data")
    if not vhdrFiles:
        print("No .vhdr files not found")
    xmlParser(args[1] + "/metadata.xml")


if __name__ == '__main__':
    main()
