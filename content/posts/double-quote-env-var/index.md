---
title: 通过环境变量加载配置
date: 2021-05-15T23:13:00+08:00  
category:
    - Programming
tags:
    - Linux
    - Python
--- 

启动时，程序读取配置有几种方法：

1) 把配置文件作为参数传给程序
2) 程序从配置服务器读取配置参数
3) 通过环境变量载入参数

第三种方法，由于简单方便，兼容性高，无需依赖其他基础设施，常作为中小型程序首选方法。本文分享几个使用环境变量的经验。

<!--more--> 

## 环境变量文件

通过设置环境变量，把配置项传递给程序的最简单用法如下：

```python
import os

# 读取环境变量A，如果读不到就打印0
print(os.environ.get("A", "0"))
```

测试一下

```bash-session
$ python your_program.py
0

$ A=1 python your_program.py
1
```

随着程序复杂度的升高，需要越来越多的环境变量配置程序行为。如果还是像上面这种用法，每次运行起来会格外的头疼：

```bash-session
$ A=1 B=2 C=3 D=4 E=5 AA=1 BA=2 CB=3 DC=4 EE=5 python your_program.py
```

因此，可以把所有的环境变量放入一个文件中.env（此处使用.env，也可以使用其它文件名，例如：.dot） 。文件内容如下：

```bash
export A=1
export B=2
export C=3
export D=4
export E=5
export AA=1
export BA=2
export CB=3
```

`export A=1` 会增加一个名字为A的环境变量同时赋值为1。有了这个文件，就可以这样操作了：

```bash-session
$ source .env && export && python your_program.py
declare -x A="1"
declare -x AA="1"
declare -x B="2"
declare -x BA="2"
declare -x C="3"
declare -x CB="3"
declare -x CLASSPATH=".:/usr/local/jdk/lib:/usr/local/jdk/jre/lib:/usr/local/jdk/lib/dt.jar:/usr/local/jdk/lib/tools.jar"
declare -x D="4"
declare -x E="5"
declare -x HOME="/home/hao"
...
declare -x WT_SESSION="63c4896d-7f36-473b-bc42-51ed14350db4"
declare -x XDG_DATA_DIRS="/usr/local/share:/usr/share:/var/lib/snapd/desktop"
1
```

通过export命令就能看到所有.env文件中的环境变量都已经声明复制，并在程序中被正确引用。不过严格的说， 我们写的`.env`不是真的`.env`环境变量文件，而是`shell`脚本。真正的环境变量文件应该长成这个样子：

```bash
A=1
B=2
C=3
D=4
E=5
AA=1
BA=2
CB=3
```

如果此时再次执行上面的那条命令（**请打开一个新terminal做这个测试，否则之前的环境变量依旧在Session中**）：

```bash-session
$ source .env && export && python your_program.py
declare -x CLASSPATH=".:/usr/local/jdk/lib:/usr/local/jdk/jre/lib:/usr/local/jdk/lib/dt.jar:/usr/local/jdk/lib/tools.jar"
declare -x HOME="/home/hao"
declare -x HOSTTYPE="x86_64"
declare -x JAVA_HOME="/usr/local/jdk"
declare -x JRE_HOME="/usr/local/jdk/jre"
...
declare -x WT_SESSION="ae8443cd-142b-4c66-96cb-15467fed0b4b"
declare -x XDG_DATA_DIRS="/usr/local/share:/usr/share:/var/lib/snapd/desktop"
0
```

因为source是执行脚本，而.env中并没有脚本命令，所以环境变量也就没有被声明和赋值。如果你希望用docker的--env-file或者docker-compose的 env_file指令加载环境变量文件，那就必须使用不含export命令的 **真** 环境变量文件。可这样一来，你就无法在terminal开发调试时，用source加载环境变量文件。当然可以写一段复杂的遍历语句来依次export环境变量。但更直接的方案是在程序中使用加载环境变量文件的库，读入环境变量文件。例如：

```python
from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("A"))
```

## 关于引号

在Linux环境下，如下两种环境变量是一样的：

```bash-session
$ cat .env
A=Hello
B="Hello"

$ echo $A
Hello

$ echo $B
Hello
```

然而docker的--env-file会将有双引号和没有双引号视为不同的内容。可以阅读[strange interpretation/parsing of .env file #3702](https://github.com/docker/compose/issues/3702)  

```bash-session
$ docker run --env-file=.env alpine sh -c 'echo $A'
Hello

$ docker run --env-file=.env alpine sh -c 'echo $B'
"Hello"
```

这个变化会造成什么影响呢？举个例子，假设你有个python文件要调用API，所依赖的库可能会去拿你传入URL的hostname：

```python
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

result = urlparse(os.getenv("U"))
print(result.hostname)
```

```bash-session
$ cat .env
U="https://www.baidu.com/a.mp4"

$ python url.py
www.baidu.com

$ docker run --env-file=.env -v $PWD:/opt python:3.8-alpine sh -c "pip install python-dotenv && python /opt/url.py"
None
```

如果在docker中调用API的程序去获取result.hostname，期待拿到www.baidu.com（在非docker环境下，也的确是这个值）。但实际得到None，因为传入urlparse的值是'"https://www.baidu.com/a.mp4"'，urlparse无法得到正确结果。因此，在环境变量中除非有空格，否则不要使用引号（双引号和单引号）。

可以阅读这篇文章再次加深以下印象[Don't Quote Environment Variables in Docker](https://dev.to/tvanantwerp/don-t-quote-environment-variables-in-docker-268h)。