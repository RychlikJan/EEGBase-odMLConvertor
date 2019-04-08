
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

    # for element in root.findall('section'):
    #     element.tag = 'subsection'

    #element = root.find('date')
    #child = ET.SubElement(root, "section")

    "Nove xml, a prenaset jednotlive tagy pomoci depp section na webu navod"

    #https://stackoverflow.com/questions/49259985/addin-multiple-sub-elements-with-same-tag-to-en-xml-tree-with-python-elementtree
    #elem = ET.Element.makeelement('section')
    #element.insert(0,elem)
    #ET.SubElement(element,'section')
    #element.SubElement('section')
    # ElementTree.dump(root)
    print()
    print()
    newRoot = ET.Element("odML")
    version = ET.SubElement(newRoot, "version")
    date = ET.SubElement(newRoot, "date")
    version.text = root.find('version').text
    date.text = root.find('date').text
    section = ET.SubElement(newRoot, "section")
    name = ET.SubElement(section, "name")
    name.text = "Mereni"
    typ= ET.SubElement(section, "type")
    typ.text = "new"
    for element in root.findall('section'):
        section.append(element)

    # ET.SubElement(doc, "field1", name="blah").text = "some value1"
    # ET.SubElement(doc, "field2", name="asdfasd").text = "some vlaue2"
    # ElementTree.dump(newRoot)
    #tree = ET.ElementTree(newRoot)
    #tree.write("filename.xml")
    tree = ET.ElementTree(newRoot)
    tree.write("filename.xml")


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
