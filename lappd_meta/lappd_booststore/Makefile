CC = g++
CFLAGS = -I /home/mascenci/Documents/annie-ana/annie101/boost/advanced/A5/include -I /home/mascenci/Documents/annie-ana/annie101/boost/Tools -I /opt/homebrew/Cellar/boost/1.89.0/include
LDFLAGS = -L /opt/homebrew/Cellar/boost/1.89.0/lib -lboost_date_time -lboost_serialization -lboost_iostreams
TARGET = Boost2MetadataCSV
SOURCES = $(TARGET).cpp /home/mascenci/Documents/annie-ana/annie101/boost/Tools/BoostStore.cpp /home/mascenci/Documents/annie-ana/annie101/boost/advanced/A5/src/PsecData.cpp
OBJECTS = $(SOURCES:.cpp=.o)
all: $(TARGET)
$(TARGET): $(OBJECTS)
        $(CC) $(OBJECTS) -o $(TARGET) $(LDFLAGS)
%.o: %.cpp
        $(CC) $(CFLAGS) -c $< -o $@
clean:
        rm -f $(OBJECTS) $(TARGET) *.bin *.data *.txt *.root src/*.o
.PHONY: all clean
