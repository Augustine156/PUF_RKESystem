
# PUF_RKESystem

## Project Overview
The PUF_RKESystem project implements a secure Remote Keyless Entry (RKE) System using Physically Unclonable Functions (PUFs). This approach aims to enhance the security of wireless communication systems by exploiting the unique, unclonable nature of PUFs.

## Features
- Implementation of a PUF-based system for RKE.
- Scripts for simulation and analysis of the system.
- Demonstrates enhanced security in wireless communications.

## Getting Started
These instructions will help you get the project up and running on your local machine for development and testing.

### Prerequisites
- #### HackRF One Environment Build
We run HackRF One on PC with Windows and Raspberry Pi. You can follow the instruction to complete the installation: [HackRf One Installation Guide](https://hackrf.readthedocs.io/en/latest/installing_hackrf_software.html?fbclid=IwAR3pvwzfmRGtWe3UFUfrN1YL7KmpVvhETajoP_9MeSHRMS5668RgjFfzu2I)
- #### Machine Learning Environment Build
1. We recommend any developers to use Virtual Environment for the convinience of managing and installing packages whithin various versions: [Anaconda Installation on Linux](https://docs.anaconda.com/free/anaconda/install/linux/)
2. Tensorflow users should follow the installtion below: [Tensorflow Installation on Linux](https://www.tensorflow.org/lite/guide/python?fbclid=IwAR1atvxRhZ50hvUqw4LsZ7c6DscRYJ4AO43Y9VnlP6mlmXhv3hnYTFDXGpE)
3. Developers who use Nvidia Graphic Cards should install the Cuda and cudnn toolkit first:
[Cuda](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)
[cudnn](https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html)
4. Developers who use Mac with M series need differnet way to install metal and tensorflow packages
- #### Raspberry Pi Environment Build
In addition to the Raspberry Pi OS installation, to run LoRa Transceiver on Raspberry Pi, you should follow the instruction below: [Blinka](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi?fbclid=IwAR1B2d9Qf-4O9lRhFzS0N-B4NCXTMicfNOJ8ytc9hmf_QhU1tzEYn_HYqrg) [LoRa-Transceiver](https://learn.adafruit.com/adafruit-radio-bonnets/rfm9x-raspberry-pi-setup?fbclid=IwAR2l9JohbWHMphtdv4GU2kKuiA9427leZGG_OUh2MvQEcf4FuPfyeQ0Om9M)
- #### Additional Python libraries 
You can install these libraries through pip or Virtual Environment:
- json
- numpy
- random
- pypuf
- time
- hashlib
- busio
- board
- digitalio
- pickle
- adafruit_rfm9x
- zlib
- time
- digitalio
- adafruit_ssd1306
- subprocess
- os
- pydub
- tflite_runtime
- librosa

## Machine Learning Hardware Environment
- **OS:** Ubuntu 23.04 LTS
- **CPU:** Intel-7700
- **Motherboard:** Asus Z270 Prime AR
- **Memory:** 50GB
- **GPU:** MSI RTX 4090 SUPRIMX 24G
- **Power Supply:** NZXT C1200W

## Usage
1. Use HackRF One to record signals of legal keys and other noise.
2. Trim all signals from step one to reduce hardware load.
3. Train a machine learning model using the recorded legitimate signals and other noise.
4. Install this model in the car.
5. Conduct interactive testing with both the legitimate key and an attacker to verify the smooth operation of machine learning and Physical Unclonable Function (PUF).


## Contributing
Contributions are welcome! Please read [CONTRIBUTING.md](#) for details on submitting pull requests.

## References
This project uses insights from:
- Nils Wisiol et al. (2023). pypuf: A Python Library for PUF Simulation and Analysis. GitHub repository. [https://github.com/nils-wisiol/pypuf](https://github.com/nils-wisiol/pypuf)

## License
This project is licensed under [LICENSE.md](LICENSE.md).
