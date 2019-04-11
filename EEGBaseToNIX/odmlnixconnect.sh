#!/bin/bash
if [ "$#" == 1 ] 
then
	echo "spoustim script"
	nixodmlconverter "$1"
else
	echo "malo arg"
fi
