#!/bin/bash
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_23.1.0-1-Linux-x86_64.sh
chmod -x Miniconda3-py39_23.1.0-1-Linux-x86_64.sh
bash Miniconda3-py39_23.1.0-1-Linux-x86_64.sh -b
conda create -y -n sdiff_env python==3.9.16
conda init bash
