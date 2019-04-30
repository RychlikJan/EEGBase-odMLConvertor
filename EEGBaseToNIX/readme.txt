USER DOCUMENT
-----------------
INTRO
-----------------
The tool EEGBaseToNIX.py is a convertor Brain Vision data to NIX/odML file. The tool can parse and connect Brain Vision data with metadata at odML structure. 


INSTALL
-----------------
EEGBaseToNIX works on Python3, for succesful install all dependencies is needed pip(3).

- Clone or download the repository.

- Go to the folder EEGBaseToNIX.

- Run installLinux.sh for linux or installWin.bat for windows to download all dependencies.

- Run EEGBaseToNIX.py.


USE CASE
-----------------
DATA PACKAGE
-----------------
Data package is a working label for a folder with metadata and data to convert.

Data package structure:

The package has to contains a folder called "Data" with Brain Vision data inside (.eeg, .vhdr, .vmrk), and file metadata.xml. 
The file metadata have to contains data in odML format any version.

SCRIPT STARTUP
-----------------
The tool is runnable with one mandatory argument and one optional argument.

The mandatory argument is a path to the data package, where are "metadata" and folder "Data" and convert them to NIX/odML. If the path enters into a folder, which is not data package, check all folders inside. If the folders inside id a data package, try to convert the value of this folder. By this way, it is possible to convert more than one data package. The path has to be written without last separator.

Optional argument activates output of Info Logs. Log display is set by default to -off. To activate use "InfoLog=1".