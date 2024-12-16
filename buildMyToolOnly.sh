#!/bin/bash
# Dummy test by M. Ascencio, Dec-2024
# mascenci@fnal.gov

setBuild(){

        # Copy the main tools, scripts, etc
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        echo -e "\t ####### Preparing $1 "
        echo -e "\t ####### Making the $1 dir"
        mkdir -p build_$1/UserTools
        mkdir -p build_$1/configfiles

        echo -e "\t ####### Copy Makefile and Setup.sh to $1"
        cp Setup.sh build_$1/
        cp Makefile build_$1/
        cp -r DataModel build_$1/
        cp -r lib build_$1/
        cp -r src build_$1/
        cp -r include build_$1/
        cp linkdef* build_$1/

        darray=("recoANNIE" "PlotWaveforms" "Factory" "Examples")
        echo -e "\t ####### Copy the default Tools"
        for element in "${darray[@]}"; do
                echo -e "\t\t @@@@@@@@ Copy the $element"
                cp -r UserTools/$element build_$1/UserTools
        done
        echo -e "\t ####### Done with copy"

        echo -e "\t ####### Copy configfile/$1"
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

        echo -e "\t ####### Copy the extracted Tools"
        for element in "${array[@]}"; do
                cp -r UserTools/$element build_$1/UserTools
        done
        echo -e "\t ####### Copy done"

        cd build_$1

        echo -e "\t ####### Making the symbolic"
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

        cd ../build_$1
}

setBuild $1
