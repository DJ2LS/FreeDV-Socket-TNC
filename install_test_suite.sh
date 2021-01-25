#/bin/bash


git clone --branch 002_HIGHSNR_PING_PONG https://github.com/DJ2LS/FreeDV-JATE.git 002_HIGHSNR_PING_PONG

cd 002_HIGHSNR_PING_PONG

rm -rf codec2
git clone --branch dr-packet https://github.com/drowe67/codec2.git
cd codec2 && mkdir build_linux && cd build_linux
cmake ../
make


cd ../..
ls

rm -rf LPCNet
git clone https://github.com/drowe67/LPCNet
cd LPCNet && mkdir build_linux && cd build_linux
cmake -DCODEC2_BUILD_DIR=../codec2/build_linux ../ 
make

cd ../..
ls

cd codec2/build_linux && rm -Rf *
cmake -DLPCNET_BUILD_DIR=../../LPCNet/build_linux ..
make
