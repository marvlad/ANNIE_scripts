#!/bin/bash
# Dummy test by M. Ascencio, Dec-2024
# mascenci@fnal.gov

setBuild(){

        # Copy the main tools, scripts, etc
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        echo -e "\t ####################################################"
        echo -e "\t ############# Preparing $(echo "$1" | tr ',' '_') "
        echo -e "\t ####################################################"
        echo -e "\t ####### Making the $(echo "$1" | tr ',' '_') dir"
        cd ../ # Because I am script dir now
        DIR_NAME="build_$(echo "$1" | tr ',' '_')"
        IFS=',' read -r -a tools <<< "$1"

        if [ -d $DIR_NAME ]; then
           echo -e "\t Ha! Directory '$DIR_NAME' exists. Removing it..."
           rm -rf $DIR_NAME
           echo -e "\t Directory '$DIR_NAME' removed."
        fi

        mkdir -p $DIR_NAME/UserTools
        mkdir -p $DIR_NAME/configfiles

        echo -e "\t ####### Copying Makefile, DataModel, lib, src, include, linkdef* and Setup.sh to $DIR_NAME"
        cp Setup.sh $DIR_NAME/
        cp Makefile $DIR_NAME/
        cp -r DataModel $DIR_NAME/
        cp -r lib $DIR_NAME/
        cp -r src $DIR_NAME/
        cp -r include $DIR_NAME/
        cp linkdef* $DIR_NAME/

        darray=("recoANNIE" "PlotWaveforms" "Factory" "Examples")
        echo -e "\t ####### Copying the default Tools"
        for element in "${darray[@]}"; do
                echo -e "\t\t @@@@@@@@ Copying $element"
                cp -r UserTools/$element $DIR_NAME/UserTools
        done

        for tool in "${tools[@]}"; do
            echo -e "\t ####### Copying configfile/$tool"
        done
        cp -r configfiles/LoadGeometry $DIR_NAME/configfiles

        array=()
        for tool in "${tools[@]}"; do
            cp -r configfiles/$tool $DIR_NAME/configfiles
            toolschain="configfiles/$tool/ToolsConfig"
            array+=($(grep -v '^#' $toolschain | awk '{print $2}'))
        done
        echo -e "\t ####################################################"
        echo -e "\t \t Extracted tools : "
        for element in "${array[@]}"; do
                echo -e "\t \t \t \t tool ---->  " $element
        done
        echo -e "\t ####################################################"
        echo -e "\t ####### Copying the extracted Tools"
        for element in "${array[@]}"; do
                cp -r UserTools/$element $DIR_NAME/UserTools
        done

        cd $DIR_NAME

        echo -e "\t ####### Making the symbolic links"
        for tool in "${tools[@]}"; do
            ln -s configfiles/$tool/ToolChainConfig $tool
        done
        ln -s /ToolAnalysis/ToolDAQ ToolDAQ

        # Making the Unity.h
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        echo -e "\t ####### Making Unity.h"
        uarray=("Unity_recoANNIE" "PlotWaveforms" "Factory")
        farray=("PlotWaveforms")

        # Spe. tools
        #echo -e "\t #include DummyTool.h"
        echo "#include \"DummyTool.h\"" >> UserTools/Unity.h

        for element in "${uarray[@]}"; do
                #echo -e "\t #include $element.h"
                echo "#include \"$element.h\"" >> UserTools/Unity.h
        done

        # My tools
        for element in "${array[@]}"; do
                #echo -e "\t #include $element.h"
                echo "#include \"$element.h\"" >> UserTools/Unity.h
        done

        # making Factory.cpp
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        rm UserTools/Factory/Factory.cpp
        echo -e "\t ####### Making Factory/Factory.cpp"
        echo "#include \"Factory.h\"" >> UserTools/Factory/Factory.cpp
        echo "Tool* Factory(std::string tool)  {" >> UserTools/Factory/Factory.cpp
        echo "    Tool* ret = 0;" >> UserTools/Factory/Factory.cpp
        echo "    if (tool==\"DummyTool\") ret=new DummyTool;" >> UserTools/Factory/Factory.cpp

        # Loop through the array and add the conditional checks
        for element in "${farray[@]}"; do
            echo "    if (tool==\"$element\") ret=new $element;" >> UserTools/Factory/Factory.cpp
        done

        # Loop through the array and add the conditional checks
        for element in "${array[@]}"; do
            echo "    if (tool==\"$element\") ret=new $element;" >> UserTools/Factory/Factory.cpp
        done
        echo "return ret;" >> UserTools/Factory/Factory.cpp
        echo "}" >> UserTools/Factory/Factory.cpp

        echo -e "\t DONE!"
        echo -e "\t Now go to ../$DIR_NAME, execute the container and compile it. Use cd ../$DIR_NAME; source Setup.sh; make clean; make"
}
# Check the arguments
if [ $# -eq 0 ]; then
    echo "###################################################################################################"
    echo "#  No arguments provided. Please provide at least one argument.                                    "
    echo "#  Usage: '$0 [Toolchain_name]' or"
    echo "#         '$0 \"Tool1,Tool2,...\"' or"
    echo "#         '$0 [Toolchain_name] clean'                             "
    echo "###################################################################################################"
    exit 1
fi

DIR_NAME="build_$(echo "$1" | tr ',' '_')"
CONFIG_DIR="../configfiles/"
IFS=',' read -r -a tools <<< "$1"

if [ $# -eq 1 ]; then
    for tool in "${tools[@]}"; do
       if [ ! -d "$CONFIG_DIR/$tool" ]; then
          echo "ERROR: Directory 'configfiles/$tool' does not exist."
          exit 1
       fi
    done
    setBuild $1
elif [ $# -eq 2 ] && [ "$2" == "clean" ]; then
    rm -rf ../$DIR_NAME
else
    echo "Invalid argument. Usage: '$0 [Toolchain_name]' or '$0 \"Tool1,Tool2,...\" or '$0 [Toolchain_name] clean'"
    exit 1
fi
