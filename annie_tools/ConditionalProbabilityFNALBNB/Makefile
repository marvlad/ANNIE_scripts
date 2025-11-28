# g++ -std=c++17 main.cpp -o testcode `root-config --cflags --libs`
CXX = g++
CXXFLAGS = -std=c++17 -O2 `root-config --cflags`
LDFLAGS = `root-config --libs`
INC = -I include/

# Target name
TARGET = testcode
SRC = main.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET) $(LDFLAGS) $(INC)

clean:
	rm -f $(TARGET)

.PHONY: all clean

