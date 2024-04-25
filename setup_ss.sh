#!/bin/bash

git clone https://github.com/InteractiveComputerGraphics/SPlisHSPlasH.git
cd SPlisHSPlasH
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DUSE_PYTHON_BINDINGS=Off ..
make -j 4
