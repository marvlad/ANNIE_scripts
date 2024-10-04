#!/bin/bash
# Dummy test by M. Ascencio, Aug-2024
# mascenci@fnal.gov


# Check if no arguments are passed
if [ $# -eq 0 ]; then
    echo "###################################################################################################"
    echo "#  No arguments provided. Please provide at least one argument.                                   #"
    echo "#  Example:  './FastMakeClea [Toolchain_name]'                                                    #"
    echo "#  Use 'ln -s configfile/[toolchain_name]/ToolChainConfig [toolchain_name]' to generate the name. #"
    echo "###################################################################################################"
    exit 1
fi

# in case there is no symbolic

echo "###################################################################################################"
echo "Making the symbolic" 
ln -s configfiles/$1/ToolChainConfig $1

# default tools 
darray=("recoANNIE" "PlotWaveforms" "Factory")
farray=("PlotWaveforms")
uarray=("Unity_recoANNIE" "PlotWaveforms" "Factory")


# what files are you using?
# --------------------------------------------
# Store the elements into an array

tooschain="configfiles/$1/ToolsConfig"
array=($(grep -v '^#' $tooschain | awk '{print $2}'))
echo " "
echo "###################################################################################################"
echo "Tools: "
for element in "${array[@]}"; do
        echo "tool --->>  " $element
done
echo "###################################################################################################"

# --------------------------------------------
# modify temporaly the cpp to zpp 
cd UserTools
find . -type f -name "*.zpp" -exec rename .zpp .cpp {} +
find . -type f -name "*.cpp" -exec rename .cpp .zpp {} +

# --------------------------------------------
# Modify the Unity.h and the UserTools/Factory.cpp

echo " "
echo " "
echo "Making Unity.h in UserTools/"
echo "###################################################################################################"

# rm old Unity.h
rm Unity.h
# Def tools
for element in "${darray[@]}"; do
        cd $element
        find . -type f -name "*.zpp" -exec rename .zpp .cpp {} +
        cd ..
done

for element in "${uarray[@]}"; do
        echo "#include $element.h"
        echo "#include \"$element.h\"" >> Unity.h
done

# My tools
for element in "${array[@]}"; do
        echo "#include $element.h"
        cd $element
        find . -type f -name "*.zpp" -exec rename .zpp .cpp {} +
        cd ..
        echo "#include \"$element.h\"" >> Unity.h
done
echo "###################################################################################################"

# --------------------------------------------
# Create the Factory.cpp file
echo " "
echo " "
echo "Creating Factory.cpp in UserTools/Factory/"
echo "###################################################################################################"
cd Factory
rm Factory.cpp
cat <<EOF > Factory.cpp
#include "Factory.h"

Tool* Factory(std::string tool) {
    Tool* ret = 0;
EOF

# Loop through the array and add the conditional checks
for element in "${farray[@]}"; do
    echo "    if (tool==\"$element\") ret=new $element;" >> Factory.cpp
done

# Loop through the array and add the conditional checks
for element in "${array[@]}"; do
    echo "    if (tool==\"$element\") ret=new $element;" >> Factory.cpp
done

# Close the function in the file
cat <<EOF >> Factory.cpp

    return ret;
}
EOF
cat Factory.cpp
echo "###################################################################################################"
cd ../..
