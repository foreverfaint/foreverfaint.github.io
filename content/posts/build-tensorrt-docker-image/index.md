---
title: "TensorRT容器镜像"
date: 2022-02-24T17:12:22+08:00
categories: 
    - DevOps
tags:
    - Docker
    - TensorRT
---

首先，NVIDIA NGC为每个TensorRT的版本提供了[docker镜像](https://docs.nvidia.com/deeplearning/tensorrt/container-release-notes/rel_22-01.html)。具体的镜像使用方法参见[NGC TensorRT页面](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/tensorrt) 。简单说，开发者基于官方镜像build自己的镜像。

<!--more--> 

## 使用官方镜像

例如运行**22.01**版本的tensorrt镜像：

```bash-session
$ docker run --gpus all --rm nvcr.io/nvidia/tensorrt:22.01-py3 nvidia-smi

=====================
== NVIDIA TensorRT ==
=====================

NVIDIA Release 22.01 (build 30856447)
NVIDIA TensorRT Version 8.2.2
Copyright (c) 2016-2022, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

Container image Copyright (c) 2022, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

https://developer.nvidia.com/tensorrt

Various files include modifications (c) NVIDIA CORPORATION & AFFILIATES.  All rights reserved.

This container image and its contents are governed by the NVIDIA Deep Learning Container License.
By pulling and using the container, you accept the terms and conditions of this license:
https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license

To install Python sample dependencies, run /opt/tensorrt/python/python_setup.sh

To install the open-source samples corresponding to this TensorRT release version
run /opt/tensorrt/install_opensource.sh.  To build the open source parsers,
plugins, and samples for current top-of-tree on master or a different branch,
run /opt/tensorrt/install_opensource.sh -b <branch>
See https://github.com/NVIDIA/TensorRT for more information.

Fri Feb 25 07:22:53 2022       
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 510.54       Driver Version: 510.54       CUDA Version: 11.6     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  Tesla T4            Off  | 00000000:02:00.0 Off |                    0 |
| N/A   51C    P0    29W /  70W |   1861MiB / 15360MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
                                                                               
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|    0   N/A  N/A      1671      G                                      14MiB |
|    0   N/A  N/A    624052      G                                      14MiB |
|    0   N/A  N/A   1306910      C                                    1829MiB |
+-----------------------------------------------------------------------------+
```

> **22.01**为镜像版本号，而非tensorrt版本号。

查看不同版本镜像中安装了哪些软件，可查看[TensorRT发布页面](https://docs.nvidia.com/deeplearning/tensorrt/container-release-notes/rel_22-01.html)。**22.01**安装了：

- Ubuntu 20.04, Note: Container image 22.01-py3 contains Python 3.8. 
- NVIDIA CUDA 11.6.0
- **TensorRT 8.2.2**
- cuBLAS 11.8.1.74
- NVIDIA cuDNN 8.3.2
- NVIDIA NCCL 2.11.4 (optimized for NVLink™ ), Note: Although NCCL is packaged in the container, it does not affect TensorRT nor inferencing in any way.
- rdma-core 36.0
- NVIDIA HPC-X 2.10
- OpenMPI 4.1.2rc4+
- OpenUCX 1.12.0
- GDRCopy 2.3
- Nsight Systems 2021.5.2.53

## 构建自定义镜像

但如果是某些特殊原因，比如：

- 需要一个更小的镜像（NVIDIA的官方镜像在6+GB），例如：不想安装`Nsight Systems`到镜像中
- 需要一个官方没有提供的版本组合，例如：`ubuntu 18.04 + python 3.6 + cuda 11.6 + tensorrt 7.1`

可以从`ubuntu`的容器镜像，或者从NVIDIA的`cuda`容器镜像开始构建自己的镜像。从`ubuntu`开始构建，最终镜像大概在4GB左右。从`cuda`开始，最终镜像会在4.6GB左右。如果没有特殊的需求，建议从`cuda`开始，调试精力和构建一次的时间都会节省一些。以下以`cuda`为例，说明过程。

## 基础镜像选择

NVIDIA将`cuda`镜像发布到了[`docker hub`](https://hub.docker.com/r/nvidia/cuda)上，先根据对操作系统类型和`cuda`版本选择基础镜像。每一类版本镜像又分为三种：

- `base`，仅包含`cuda runtime`（cudart）。
- `runtime`，基于`base`，还包含[CUDA math libraries](https://developer.nvidia.com/gpu-accelerated-libraries)、[NCCL](https://developer.nvidia.com/nccl)，和[cuDNN](https://developer.nvidia.com/cudnn)。
- `devel`，基于`runtime`，还包含开发库和开发工具。如果需要使用镜像基于`cuda`做进一步编译和开发，应该使用该镜像。


我们以[`nvidia/cuda:11.6.0-runtime-ubuntu20.04`](https://hub.docker.com/layers/nvidia/cuda/11.6.0-runtime-ubuntu20.04)作为基础镜像。

## 创建Dockerfile

### 进行Ubuntu配置

使用`dockerfile:1`的语法，可以按多stage方法进行构建。

```dockerfile
# syntax=docker/dockerfile:1
FROM nvidia/cuda:11.6.0-runtime-ubuntu20.04 AS Base
```

`./sources-focal.list`是一个自定义的apt源。比如使用国内（中国大陆）的apt源替换默认的海外apt源，可以大大提供安装速度和稳定性。

```dockerfile
COPY ./sources-focal.list /etc/apt/sources.list
```

设置`DEBIAN_FRONTEND=noninteractive`防止安装过程中，出现`prompt`提示进行某项配置（例如：时区和键盘layout）。不过貌似从`cuda`镜像开始安装，这些配置已经进行过设置，所以可以跳过这些步骤。

```dockerfile
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && \
    ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    apt-get install -y --no-install-recommends tzdata keyboard-configuration software-properties-common
```

### 安装Python

基础镜像中并没有安装`docker`，所以第二步可以选择python版本进行安装。本文以`python 3.8`为例：

```dockerfile
RUN apt-get -y install curl wget autoconf automake libtool python3.8 python3.8-dev python3.8-distutils ffmpeg && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py && \
    pip install -U pip setuptools -i https://mirrors.aliyun.com/pypi/simple && \
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple  
```

其中：

- `update-alternatives`将`python`和`python3`命令指向`python3.8`
- `python3 get-pip.py`安装的`pip`，会放到`/usr/local/bin/pip`这个位置，而不是`/usr/bin/pip`
- `pip config set global.index-url https://mirrors.aliyun.com/pypi/simple`设置一个国内（中国大陆）更快的`pip`源

### 安装TensorRT

安装过程参考[Nvidia TensorRT Installation](https://docs.nvidia.com/deeplearning/tensorrt/install-guide/index.html#installing)。特别是在[4.1. Debian Installation](https://docs.nvidia.com/deeplearning/tensorrt/install-guide/index.html#installing-debian)一节有一句重要的提示，重要中的重要我进行了加粗。我们正是在用包含了`cuda`和`cudnn`的基础镜像安装！如果没看到这句话，各种下载和配置尝试会耽误不少时间 :smile:

> For advanced users who are already familiar with TensorRT and want to get their application running quickly, are **using an NVIDIA CUDA container with cuDNN included**, or want to setup automation, follow the network repo installation instructions (see Using [The NVIDIA CUDA Network Repo For Debian Installation](https://docs.nvidia.com/deeplearning/tensorrt/install-guide/index.html#maclearn-net-repo-install)). 

在[4.1.1 Using The NVIDIA CUDA Network Repo For Debian Installation](https://docs.nvidia.com/deeplearning/tensorrt/install-guide/index.html#maclearn-net-repo-install)这一节，同样最重要的一句：

> Note: If you are using a CUDA container with cuDNN included, then the NVIDIA CUDA network repository will already be set up and you can skip step 1. 

这一节一共3步，如上第1步可以忽略了，而第3步只有在安装*非最新版本TensorRT*的时候才用得上。因此我们只需要关注第2步。我们的镜像是作为运行时镜像使用，不用于开发，所以只安装 *For only running TensorRT C++ applications* 和 *For running TensorRT Python applications*

```dockerfile
RUN apt-get -y install libnvinfer8 libnvonnxparsers8 libnvparsers8 libnvinfer-plugin8 && \
    pip install numpy && \
    apt-get -y install python3-libnvinfer
```

以上即为自定义TensorRT镜像的制作过程。

