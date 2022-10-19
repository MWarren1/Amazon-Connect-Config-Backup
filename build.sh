#!/bin/bash
############################################################
# Help                                                     #
############################################################
Help() {
    # Display Help
    echo "Add description of the script functions here."
    echo
    echo "Syntax: scriptTemplate [-h|-a|-f]"
    echo "options:"
    echo "a     Build all - no args"
    echo "f     Builds a specific package - pass <folder> arg to specify package. Folder must contain a requirements.txt file, even if the file empty"
    echo "Usage: $0 [-a] [-f folder]"
    echo
}

############################################################
# Build                                                    #
############################################################
Build() {

    # Only continue if there is a requirements.txt file
    FILE=src/requirements.txt
    LAYER_FILE=src/layer-requirements.txt
    if [ -f "$FILE" ];
    then
        # Clean up dist folder
        rm -r tmp || mkdir -p tmp
        # Copy src code to temp
        cp -r src/* tmp/
        echo "requirements.txt file exists - building package."
        # Install packages using requirements.txt
        cd tmp && pip3 install -t . -r requirements.txt
        # ZIP Enire /code directory
        echo "After zip pwd :$PWD"
        zip -r9 ../../../dist/$dir/$filename.zip ./
        # back to package folder
        cd ..
        # remove tmp contents
        rm -r tmp
        echo "Built $PWD"

    elif [ -f "$LAYER_FILE" ];
    then 

        # Clean up dist folder
        rm -r tmp/python/* || mkdir -p tmp/python
        # Copy src code to temp
        cp -r src/* tmp/python
        echo "layer-requirements.txt file exists - building Layer."
        # Install packages using requirements.txt
        cd tmp/python && pip3 install -t . -r layer-requirements.txt
        # back to python folder
        cd ..
        # ZIP Enire /code directory
        echo "After zip pwd :$PWD"
        zip -r9 ../../../dist/$dir/$filename.zip ./
        # back to package folder
        cd ..
        # remove tmp contents
        rm -r tmp
        echo "Built $PWD"     

    else
        echo "requirements.txt file does not exist - not building package."
    fi
    
}

############################################################
# BuildAll                                                 #
############################################################
BuildAll() {
    cd app-code/src
    echo "Buidling All Folders"
    for f in *; do 
        cd $f
        echo "Building in $f"
        filename=$f
        Build
        cd ../
    done
}

############################################################
############################################################
# Main program                                             #
############################################################
############################################################


############################################################
# Process the input options. Add options as needed.        #
############################################################
# Get the options
echo "$#"
while getopts ":haf:" option; do
    case $option in
    h) # display Help
        Help
        exit
        ;;
    a)
        # Build all folders
        BuildAll
        ;;

    f) # Build a specific folder
        filename=$OPTARG
        cd app-code/src/$filename
        Build
        ;;
    \?) # Invalid option
        echo "Error: Invalid option"
        exit
        ;;
    esac
done

echo "All Done"
