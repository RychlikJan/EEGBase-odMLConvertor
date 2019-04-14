import platform
import sys
import os
import xml.etree.ElementTree as ET
from subprocess import Popen, PIPE, STDOUT


"""
dependencies
pip install odml nixio==1.5.0b3

pip install -i https://test.pypi.org/simple/ nixodmlconverter==0.0.4

https://web.gin.g-node.org/JiriVanek/DataConversionToNIX/mnetonix.py

chmod 777 mnetonix.py
chmod 777 convert.py


"""
path_spliter = ""
translater =""
def set_spliter():
    os_sys = platform.system()
    print(os_sys)
    global path_spliter
    global translater
    if "Linux" in os_sys:
        translater = "python3"
        path_spliter = "/"
    elif "Windows" in os_sys:
        translater = "python"
        path_spliter = "\\"
    else:
        path_spliter = ""
    print("[SET-SPLITER]" + path_spliter)




def iter_parent(tree):
    for parent in tree.iter():
        for child in parent:
            yield parent, child


def remove_one(root):
    for parent, child in iter_parent(root):
        if "http://www.g-node.org/guiml" in child.tag:
            parent.remove(child)


def get_name(path, end):
    new_xml_name_arr = path.split(path_spliter)
    file_name = new_xml_name_arr[-1]
    file_name_arr = file_name.split(".")
    file_name_arr[0] = file_name_arr[0] + end
    print("[GET-NAME] Return name: " + file_name_arr[0])
    return file_name_arr[0]


def get_path(path):
    print(path)
    path_arr = path.split(path_spliter)
    path = ""
    index = 0
    while index < len(path_arr)-2:
        path = path + path_arr[index]
        path = path + path_spliter
        index += 1
    path = path + "NewNIX"
    print("[GET-PATH] Final path is: " + path)
    print("[GET-PATH]", path_arr)
    return path


def make_dir(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        # directory already exists
        pass


def xml_parser(xml_name, path):
    print("[XML-Parser] Path:" +path)
    new_xml_name = get_name(path, ".xml")
    xml_file = ET.parse(xml_name)
    root = xml_file.getroot()

    i = 1
    while i == 1:
        remove_one(root)
        i = 0
        for child in root.iter():
            if "http://www.g-node.org/guiml" in child.tag:
                i = 1

    new_root = ET.Element("odML")
    version = ET.SubElement(new_root, "version")
    date = ET.SubElement(new_root, "date")
    section = ET.SubElement(new_root, "section")
    name = ET.SubElement(section, "name")
    typ = ET.SubElement(section, "type")

    new_root.set('version', '1')
    version.text = root.find('version').text
    date.text = root.find('date').text
    name.text = new_xml_name
    typ.text = "new"

    for element in root.findall('section'):
        section.append(element)

    path = get_path(path)
    tree = ET.ElementTree(new_root)
    make_dir(path)
    place = path+path_spliter+new_xml_name
    print(place)
    tree.write(place)
    print("[XML-Parser] Save to:" + place)
    print("[XML-Parser] Xml parse ends")
    return place


def file_exist(path):
    print("[FILE-EXIST] Path: "+ path)
    try:
        f = open(path)
        f.close()
    except IOError:
        return 0
    return 1


def point_split(array_path):
    print("[POINT-SPLIT]",array_path)
    arr_len = len(array_path)
    path = ""
    index = 0
    while index < arr_len-1:
        if index is not 0:
    	    path = path + "."
        path = path + array_path[index]
        index+=1
    print("[POINT-SPLIT] Path: " +path)
    return path



def all_vhdr_files(path):
    print("[ALL-VHDR-FILES] Actual entrance path: " +path)
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.vhdr' in file:
                files.append(os.path.join(r, file))
    index =0
    print("[ALL-VHDR-FILES] Tested all files", files)
    for f in files:
        path_egg = f.split(".")
        path_vmrk = f.split(".")
        eeg_p = point_split(path_egg) + ".eeg"
        vmrk_p = point_split(path_vmrk) + ".vmrk"
        exist_eeg = file_exist(eeg_p)
        exist_vmrk = file_exist(vmrk_p)
        if exist_eeg == 0 or exist_vmrk == 0:
            files.remove(f)
        index = index +1
    print(index)
    return files


def run_mne_to_nix_script(path):
    print("[MNE-TO-NIX] Mne to nix script started")
    print("[MNE-TO-NIX] Runs on file :" + path)
    pom = sys.path[0] + path_spliter + "mnetonix.py"
    print("[MNE-TO-NIX] Path script: " +pom)
    
    p = Popen([translater,pom, path], stdout=PIPE, stderr=STDOUT, bufsize=1)
    p.wait()
    print("[MNE-TO-NIX] Mne to nix ended")
    path_new_name = path.split()
    path = point_split(path_new_name) +".nix"
    result = file_exist(path)
    if result is 0:
        print("[MNE-TO-NIX] Mne to nix ended with errors")
        return "ErrorScript"
    else:
        print("[MNE-TO-NIX] Mne to nix ended successful")
        print("[MNE-TO-NIX] Saved to:" + path)
        return path


def copy_file(source_path, destination_path):
    print("[COPY-FILE] File copying started")
    new_dest_path_arr = destination_path.split(path_spliter)
    destination_path = ""
    index = 0
    while index < len(new_dest_path_arr)-1:
        destination_path = destination_path + new_dest_path_arr[index]
        destination_path = destination_path + path_spliter
        index += 1
    file_name = get_name(source_path, ".nix")
    os.rename(source_path, destination_path+file_name)
    print("[COPY-FILE] From:" + source_path)
    print("[COPY-FILE] To: " + destination_path + file_name)
    print("[COPY-FILE] File copying ended")


def nixodmlconverter_script(path):
    print("[NIX-ODML-CONVERTER-SCRIPT] Script started")
    p = Popen(["python3", "convert.py", path], stdout=PIPE, stderr=STDOUT, bufsize=1)
    p.wait()

    print("[NIX-ODML-CONVERTER-SCRIPT] Script ended successful")


def main():
    set_spliter()
    print("[EEG-BASE-TO-NIX] " + path_spliter)
    print("[EEG-BASE-TO-NIX] Script started")
    args = sys.argv
    if len(args) == 1:
        print("[EEG-BASE-TO-NIX] Use like an argument path into folder with measurement")
        sys.exit()
    if file_exist(args[1] + path_spliter+"metadata.xml") == 0:
        print("[EEG-BASE-TO-NIX] Metadata.xml file not found")
        sys.exit()
    vhdr_files = all_vhdr_files(args[1] + path_spliter+"Data")
    if not vhdr_files:
        print("[EEG-BASE-TO-NIX] No .vhdr files not found")
        sys.exit()
    print("[EEG-BASE-TO-NIX] Array vhdr files:",vhdr_files)
    path_to_metadata = xml_parser(args[1] + path_spliter+"metadata.xml", vhdr_files[0])
    path_to_nix = run_mne_to_nix_script(vhdr_files[0])
    if "ErrorScript" in path_to_nix:
        print("[EEG-BASE-TO-NIX] Script nnetonix.py failed")
        sys.exit()
    copy_file(path_to_nix, path_to_metadata)
    nixodmlconverter_script(path_to_metadata)
    print("[EEG-BASE-TO-NIX] Script ended")


if __name__ == '__main__':
    main()
