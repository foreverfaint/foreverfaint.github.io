---
title: nohup
date: 2020-01-19T00:00:00+08:00
category:
    - DevOps
tags: 
    - Linux
---

nohup是一个POSIX命令。人如其名“NO”+“HUP（hangup）”，“HUP”是挂起信号，“NOHUP”就是忽略挂起信号。

<!--more--> 

## 实用版说明

### NOHUP

```bash-session
$ nohup ping www.baidu.com > log.txt
```

执行该命令后，当前`ping`命令会保持在**前台**运行，即我们没法继续在当前terminal执行其它命令。如果我们开启一个新的terminal，然后执行：

```bash-session
$ wc -l log.txt
24 log.txt

$ wc -l log.txt
28 log.txt
```

会看到`wc`输出的数字在持续增长中。现在关闭运行`nohup`命令的terminal（即发出了SIGHUP信号）。在第二个terminal（运行`wc`命令的那个），再次执行：

```bash-session
$ wc -l log.txt
32 log.txt

$ wc -l log.txt
35 log.txt
```

就能看到log.txt文件的行数依旧在持续增长，这说明`ping`命令并没有因为SIGHUP信号而终止。

### 关于&符号

```bash-session
$ nohup ping www.baidu.com > log.txt &
```

执行该命令后，`ping`会在后台运行（即，我们可以在当前terminal内执行其他命令）。如果我们查看log.txt文件，就会看到文件在持续变大。`nohup`和`＆`的组合确保了命令可以永久在**后台**执行。

### 关于重定向操作符

```bash-session
$ nohup ping www.baidu.com > log.txt 2>&1 &
```

- `>`操作符右侧接一个文件。如果文件不存在，则创建新文件，并将左侧命令输出**覆盖**到文件中
- `>>`操作符右侧同样接一个文件。如果文件不存在，则创建新文件，并将左侧命令输出**追加**到文件中
- 0是标准输入（stdin），1是标准输出（stdout），2是标准错误输出（stderr）。**2>&1**是将标准错误重定向到标准输出。最后**> log.txt**再将标准输出重定向到文件log.txt

## 理论版说明

为了讲清楚NOHUP的机制，必须要先介绍一些概念：

### 进程组

一个进程及其子进程形成一个**进程组**。**进程组**中的第一个进程，称为**进程组领导者**（process group leader）。每个进程有一个ID（PID）。进程的父进程的ID叫PPID。进程组ID（PGID）用**进程组领导者**的PID。举个例子：

```bash-session
$ nohup ping www.baidu.com | less
```

会产生一个**进程组**。**进程组**会包含至少三个进程`nohup``ping``less`。 

### 会话

一个**会话**会由多个**进程组**组成。创建**会话**的进程称为**会话领导者**（session leader）。每个**会话**有一个ID（SID），为**会话领导者**进程ID。

### 终端（terminal）

过去**终端**是一个真实的物理设备，支持输入（键盘）和显示输出（显示器），用来操作主机。现在当我们提到**终端**，是一个抽象的概念，通常是指操作系统的一个应用。我们通过**终端**应用向会话输入信号，并将会话的内容显示出来。

### Shell

当我们在Linux系统中，启动一个**终端**，实际上启动了一个**进程**，该进程执行**shell**应用，解释和处理各种命令。这个进程作为**会话领导者**形成了一个新**会话**。当然隐含着也创建了一个**进程组**。如果我们打开两个**终端**，那就开启了两个会话。举个例子：

先启动一个**终端**，执行

```bash-session
$ nohup www.bing.com &

$ ping www.baidu.com
```

再启动一个**终端**，执行

```bash-session
$ nohup www.google.com &
```

然后让我们用`ps j`看看这几个进程和会话：

```bash-session
===== ===== ===== ===== ===== ====================
PPID  PID   PGID  SID   TPGID COMMAND
===== ===== ===== ===== ===== ====================
 6133 12708  5693  5693 5693  SecureCRT
12708 12720 12720 12720 18176 -zsh
12708 12786 12786 12786 18191 -zsh
12720 18165 18165 12720 18176 ping www.bing.com
12720 18176 18176 12720 18176 ping www.baidu.com
12786 18184 18184 12786 18191 ping www.google.com
12786 18191 18191 12786 18191 ps j
===== ===== ===== ===== ===== ====================
```

可看到几个事情：  

- `www.bing.com`和`www.baidu.com`的SID是一样的，在同一个会话中
- `www.google.com`则在另一个会话中
- `www.bing.com`和`www.baidu.com`是两个命令，故在两个不同的**进程组**，PGID不同；两个命令的PPID相同，同属于`zsh`创建的子进程组　（本示例中，我的**shell**是zsh）
- `www.google.com`的PPID也指向一个`zsh`。而这两个`zsh`最终都指向`SecureCRT`所在进程。

此外每个会话会对应一个**前台进程组**（TPGID, tty process group id），其他进程组都属于**后台进程组**。　会话中只有**前台进程组**可以接收**终端**的输入和信号。 启动时，**会话领导者**是**终端**的**控制进程**（通常就是**Shell**进程）。随着控制**终端**的进程变化，**终端**会修改**前台进程组**。从上面的表格即可看出，**终端**中当前正在执行的进程所在进程组被设置为TPG。**控制进程组**永远是**会话领导者**所在组；**前台进程组**则根据当前哪个进程正在执行来变化。

- 第二行的`-zsh`，`ping www.bing.com`，`ping www.baidu.com`的TPGID均为正在终端前台运行的`ping www.baidu.com`所在进程ID。
- 第三行的`-zsh`,`ping www.google.com`，`ps j`的TPGID则是正在运行的`ps j`所在进程ID

### SIGHUP

当关闭**终端**时，系统发送SIGHUP信号给**控制进程**。当**控制进程**退出时，会将SIGHUP发给所在进程组中每一个进程。然后向**前台进程组**发信号。如果不希望自己的进程退出，就应该使用`nohup`和`&`组合将进程放到后台且忽略SIGHUP信号。

关闭**终端**　后，使用`ps j`会发现本应继续运行的进程不见了。难道是被杀掉了？不是说好的nohup吗？请用`ps -aux`试一下，是不是又找到那些后台进程了？**x**确保`ps`命令显示所有进程，而不是按**终端**来显示。