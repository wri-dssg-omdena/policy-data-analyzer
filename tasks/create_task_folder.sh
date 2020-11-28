#!/bin/bash


FOLDERS_TO_CREATE="input output src"

for i in "$@"
do
case $i in
    -n=*|--name=*)
    FOLDER_NAME="${i#*=}"
    mkdir ${FOLDER_NAME}
    cd ${FOLDER_NAME}
    for folder in $FOLDERS_TO_CREATE; do
        mkdir $folder
        cd $folder
        touch .gitkeep
	cd ..
    done
    shift # past argument=value
    ;;
    -a=*|--add_notebook=*)
    ADD_NOTEBOOK="${i#*=}"
    if [[ $ADD_NOTEBOOK == "True" ]]; then
	mkdir notebooks
	cd notebooks
	touch .gitkeep
	cd .. 
    fi	
    ;;
esac
done


