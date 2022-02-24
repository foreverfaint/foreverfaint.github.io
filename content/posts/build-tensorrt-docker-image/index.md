---
title: "制作tensorrt容器镜像"
date: 2022-02-24T17:12:22+08:00
categories: 
    - devops
tags:
    - docker
    - tensorrt
---

首先，NVIDIA NGC已经为每个TensorRT的版本提供了[docker镜像](https://docs.nvidia.com/deeplearning/tensorrt/container-release-notes/rel_21-07.html)。具体的镜像使用方法参见[NGC TensorRT页面](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/tensorrt) 。简单说，开发者pull官方镜像，然后作为base镜像，在上面build自己的环境镜像。

<!--more--> 

```bash{linenos=false}
$ docker run --gpus all -it --rm nvcr.io/nvidia/tensorrt:xx.xx-py3
```

**Hello World!** This is written in *Markdown*, a lightweight markup language.

:man_astronaut:
:star:
:woman_astronaut:

