#!/bin/bash
# Dummy test by M. Ascencio, Dec-2024
# mascenci@fnal.gov

setBuild(){

        # Copy the main tools, scripts, etc
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        echo -e "\t ####################################################"
        echo -e "\t ############# Preparing $1 "
        echo -e "\t ####################################################"
        echo -e "\t ####### Making the $1 dir"
        cd ../ # Because I am script dir now
        mkdir -p build_$1/UserTools
        mkdir -p build_$1/configfiles

        echo -e "\t ####### Copying Makefile, DataModel, lib, src, include, linkdef* and Setup.sh to $1"
        cp Setup.sh build_$1/
        cp Makefile build_$1/
        cp -r DataModel build_$1/
        cp -r lib build_$1/
        cp -r src build_$1/
        cp -r include build_$1/
        cp linkdef* build_$1/

        darray=("recoANNIE" "PlotWaveforms" "Factory" "Examples")
        echo -e "\t ####### Copying the default Tools"
        for element in "${darray[@]}"; do
                echo -e "\t\t @@@@@@@@ Copying $element"
                cp -r UserTools/$element build_$1/UserTools
        done

        echo -e "\t ####### Copying configfile/$1"
        cp -r configfiles/$1 build_$1/configfiles
        cp -r configfiles/LoadGeometry build_$1/configfiles
        toolschain="configfiles/$1/ToolsConfig"
        echo -e "\t ####### Extracting the tools used in $toolschain"
        array=($(grep -v '^#' $toolschain | awk '{print $2}'))
        echo -e " "
        echo -e "\t ####################################################"
        echo -e "\t \t Extracted tools : "
        for element in "${array[@]}"; do
                echo -e "\t \t \t \t tool ---->  " $element
        done
        echo -e "\t ####################################################"

        echo -e "\t ####### Copying the extracted Tools"
        for element in "${array[@]}"; do
                cp -r UserTools/$element build_$1/UserTools
        done

        cd build_$1

        echo -e "\t ####### Making the symbolic links"
        ln -s configfiles/$1/ToolChainConfig $1
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
        
        echo -e "DONE!"
        echo -e "Now go to ../build_$1, execute the container and compile it. User make clean; make"
}

if [ $# -eq 0 ]; then
    echo "###################################################################################################"
    echo "#  No arguments provided. Please provide at least one argument.                                   #"
    echo "#  Usage: '$0 [Toolchain_name]' or '$0 [Toolchain_name] clean'                               #"
    echo "###################################################################################################"
    exit 1
fi

TOOLCHAIN_NAME=$1
CONFIG_DIR="../configfiles/${TOOLCHAIN_NAME}"

if [ $# -eq 1 ]; then
    if [ ! -d "$CONFIG_DIR" ]; then
        echo "Error: Toolchain '$TOOLCHAIN_NAME' does not exist in 'configfiles/'."
        exit 1
    fi
    setBuild $TOOLCHAIN_NAME
elif [ $# -eq 2 ] && [ "$2" == "clean" ]; then
    rm -rf ../build_$TOOLCHAIN_NAME
else
    echo "Invalid argument. Usage: '$0 [Toolchain_name]' or '$0 [Toolchain_name] clean'"
    exit 1
fi
