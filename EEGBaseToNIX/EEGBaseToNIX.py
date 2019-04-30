import platform
import sys
import os
import xml.etree.ElementTree as ET
from subprocess import Popen, PIPE, STDOUT
from zipfile import ZipFile


"""
EEGBaseToNIX.py
Tool to convert experiments of University of West Bohemia egg base from BrainVision format to nix format.
Tool work wit two scripts of gnode. 1st one is mnetonix.py to parse brain vision format by mne libraries and create nix 
file and convert.py to conect nix file and odml data. 

Usage:
  python EEGBaseToNIX.py [-- Path to folder with metadata and data]||[--Path to folder with more experiments] <debug=1>

Dependencies
===================================
python3

pip install:
nixio==1.5.0b3
mne
odml
numpy
scipy 
matplotlib 
ipython 
jupyter 
pandas 
sympy 
nose
nixodmlconverter


chmod 777 mnetonix.py
chmod 777 convert.py


Implementation 
==================================
EEGBaseToNIX.py takes metadata, remove all informations about gui. After this runs mnetonix.py and parse .eeg .vhdr 
.vmrk files to nix files. Then runs convert.py script to conect metadata with ix file. 

If is program run with optional argument "debug=1" is possible to se how tool works with files. 

"""

"""Global variables
===================
path_spliter: Variable to split path on dependency with os
translater: Variable to split path on dependency with os
debug_mode: 
"""
path_spliter = ""
translater = ""
debug_mode = 0


def debug_print(log):
    """Method to print simply logs on console.
        Args:
            log (str): Log to print.
    """
    if debug_mode is 1:
        print(log)


def debug_print_arr(log, array):
    """Method to print array logs on console.
        Args:
            log (str): Log to print.
            array (array): Array to log
    """
    if debug_mode is 1:
        print(log, array)


def set_spliter():
    """
    Method to set global variables in dependency on OS System
    """
    os_sys = platform.system()
    debug_print("[OS-SYSTEM]"+os_sys)
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


def iter_parent(tree):
    """
    Method to goes trough xml and save parent of child element
    :param tree: xml tree

    """
    for parent in tree.iter():
        for child in parent:
            yield parent, child


def remove_one(root):
    """
    Remove specific element
    :param root:
    """
    for parent, child in iter_parent(root):
        if "http://www.g-node.org/guiml" in child.tag:
            parent.remove(child)


def get_name(path, end):
    """
    Method extract name from path and append new file ending
    :param path: Path to file-
    :param end: New file ending
    :return: Name of new file
    """
    new_xml_name_arr = path.split(path_spliter)
    file_name = new_xml_name_arr[-1]
    file_name_arr = file_name.split(".")
    file_name_arr[0] = file_name_arr[0] + end
    debug_print("[GET-NAME] Return name: " + file_name_arr[0])
    return file_name_arr[0]


def get_path(path):
    """
    Method add to target path new Way
    :param path: Actual path
    :return: New path
    """
    debug_print("[GET-PATH]" + path)
    path_arr = path.split(path_spliter)
    path = ""
    index = 0
    while index < len(path_arr)-2:
        path = path + path_arr[index]
        path = path + path_spliter
        index += 1
    path = path + "NewNIX"
    debug_print("[GET-PATH] Final path is: " + path)
    return path


def make_dir(path):
    """
    Method to create directory on specific path; if directory not exist
    :param path: Path
    """
    try:
        os.makedirs(path)
    except FileExistsError:
        # directory already exists
        pass


def xml_parser(xml_name, path):
    """
    Method to parse xml, remove gui tags and add new section, which is append to nix files
    :param xml_name: xml name
    :param path: path to xml
    """
    debug_print("[XML-PARSER] Path:" + path)
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
    tree.write(place)
    print("[XML-PARSER] Everything will be save on:" + place)
    debug_print("[XML-PARSER] Xml parse ends")
    return place


def file_exist(path):
    """
    Method tests the file exist.
    :param path: Path to file.
    :return: 0 - False/ 1-true
    """
    debug_print("[FILE-EXIST] Path: " + path)
    try:
        f = open(path)
        f.close()
    except IOError:
        return 0
    return 1


def point_split(array_path):
    """
    Method to split path array by point. Take everything before last point.
    :param array_path: array of parts of split path
    :return: path to array
    """
    debug_print_arr("[POINT-SPLIT]", array_path)
    arr_len = len(array_path)
    path = ""
    index = 0
    while index < arr_len-1:
        if index is not 0:
            path = path + "."
        path = path + array_path[index]
        index += 1
    debug_print("[POINT-SPLIT] Path: " + path)
    return path


def contains_zip(path):
    """
    Method to get and unzip files.
    :param path: path to target directory
    """
    zip_file = ""
    for root, dirs, file in os.walk(path):
        for f in file:
            if f.endswith(".zip"):
                zip_file = os.path.join(root, f)
    if zip_file is "":
        return
    debug_print(zip_file)
    with ZipFile(zip_file, 'r') as zipObj:
        zipObj.extractall(path)
        #os.remove(zip_file)  #uncomment to remove used zip files


def all_vhdr_files(path):
    """
    Method to get names and paths to all .vhdr files ant paths to tehm
    :param path: path to target irectory
    """
    debug_print("[ALL-VHDR-FILES] Actual entrance path: " + path)
    files = []
    contains_zip(path)
    for r, d, f in os.walk(path):
        for file in f:
            if '.vhdr' in file:
                files.append(os.path.join(r, file))
    index = 0
    debug_print_arr("[ALL-VHDR-FILES] Tested all files", files)
    while index < len(files):
        f = files[index]
        path_egg = f.split(".")
        path_vmrk = f.split(".")
        eeg_p = point_split(path_egg) + ".eeg"
        vmrk_p = point_split(path_vmrk) + ".vmrk"
        exist_eeg = file_exist(eeg_p)
        exist_vmrk = file_exist(vmrk_p)
        if exist_eeg == 0 or exist_vmrk == 0:
            files.remove(f)
            index = index-1
        index = index + 1
    return files


def run_mne_to_nix_script(path):
    """
    Runs script to parse mne and make nix file
    :param path: Path to .vhdr, .eeg and .vmrk file
    :return: Result of mntetonix.py script
    """
    debug_print("[MNE-TO-NIX] Mne to nix script started")
    print("[MNE-TO-NIX] Starts runs on file :" + path)
    pom = sys.path[0] + path_spliter + "mnetonix.py"
    debug_print("[MNE-TO-NIX] Path script: " + pom)
    
    p = Popen([translater, pom, path], stdout=PIPE, stderr=STDOUT, bufsize=1)
    p.wait()
    debug_print("[MNE-TO-NIX] Mne to nix ended")
    path_new_name = path.split(".")
    path = point_split(path_new_name) + ".nix"
    result = file_exist(path)
    if result is 0:
        print("[MNE-TO-NIX] Mne to nix ended with errors")
        return "ErrorScript"
    else:
        debug_print("[MNE-TO-NIX] Mne to nix ended successful")
        debug_print("[MNE-TO-NIX] Saved to:" + path)
        return path


def copy_file(source_path, destination_path):
    """
    Method to move file between directories.
    :param source_path: Source path.
    :param destination_path: Destination path.
    """
    debug_print("[COPY-FILE] File copying started")
    new_dest_path_arr = destination_path.split(path_spliter)
    destination_path = ""
    index = 0
    while index < len(new_dest_path_arr)-1:
        destination_path = destination_path + new_dest_path_arr[index]
        destination_path = destination_path + path_spliter
        index += 1
    file_name = get_name(source_path, ".nix")
    os.rename(source_path, destination_path+file_name)
    debug_print("[COPY-FILE] From:" + source_path)
    debug_print("[COPY-FILE] To: " + destination_path + file_name)
    debug_print("[COPY-FILE] File copying ended")


def nixodmlconverter_script(path):
    """
    Runs convrty.py to connect xml a .nix file.
    :param path: path to directory with nix and xml(odml) file
    """
    debug_print("[NIX-ODML-CONVERTER-SCRIPT] Script started")
    pom = sys.path[0] + path_spliter + "convert.py"
    p = Popen([translater, pom, path], stdout=PIPE, stderr=STDOUT, bufsize=1)
    p.wait()
    debug_print("[NIX-ODML-CONVERTER-SCRIPT] Script ended successful")


def convert(path):
    """
    Method drives conversion between BarainVision and nix file.
    :param path: Path to target directory
    """
    print("[CONVERT-FILE] Working with target file: " + path)
    if file_exist(path + path_spliter+"metadata.xml") == 0:
        print("[CONVERT-FILE] Metadata.xml file not found")
        return
    vhdr_files = all_vhdr_files(path + path_spliter+"Data")
    if not vhdr_files:
        print("[CONVERT-FILE] No completely .vhdr files found")
        return
    debug_print_arr("[CONVERT-FILE] Array vhdr files:", vhdr_files)
    path_to_metadata = xml_parser(path + path_spliter+"metadata.xml", vhdr_files[0])
    path_to_nix = run_mne_to_nix_script(vhdr_files[0])
    if "ErrorScript" in path_to_nix:
        debug_print("[CONVERT-FILE] Script Mnetonix.py failed")
        return
    copy_file(path_to_nix, path_to_metadata)
    nixodmlconverter_script(path_to_metadata)
    print("[CONVERT-FILE] Converting file ended")


def main():
    """
    Main method.
    :return:
    """
    set_spliter()
    debug_print("[EEG-BASE-TO-NIX] Script started")
    args = sys.argv
    if len(args) == 1:
        print("[EEG-BASE-TO-NIX] Use path to a folder with measurement as an argument")
        sys.exit()

    global debug_mode
    if len(args) == 3:
        if "1" in args[2]:
            debug_mode = 1
    print(args[1])
    try:
        directories = next(os.walk(args[1]))[1]
    except:
        print("[EEG-BASE-TO-NIX] Use path to a folder with measurement as an argument")
        return 0

    if "Data" in directories:
        convert(args[1])
    else:
        for d in directories:
            convert(args[1] + path_spliter + d)
    debug_print("[EEG-BASE-TO-NIX] Script ended")


if __name__ == '__main__':
    main()
