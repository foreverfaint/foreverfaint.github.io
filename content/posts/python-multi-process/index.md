---
title: Python多进程开发
date: 2016-10-20T00:00:00+08:00 
category:
    - Programming
:tags:
    - Python
    - Concurrency Programming
---

用Python有一段时间了，但是延续其他语言开发经验，用线程较多。然而Python自身GIL机制导致计算密集型的运算用多线程反而低效。故专门研究了一下Python多进程的开发，在这里分享一些心得。

<!--more--> 

由于Python [GIL](https://wiki.python.org/moin/GlobalInterpreterLock)机制的存在，Python在多线程执行时，并无法充分利用多核CPU的优势。甚至多线程执行计算密集型操作时，甚至慢于单线程重复执行操作。所以在日常开发中，如果要并行的操作是计算密集型，应该尽量用多进程取代多线程。尽管Python的多线程和多进程库在API设计层面，设计成了一致方法签名，方便开发者快速将程序在多线程和多进程间切换，但其实两种调用方案间有不少细微的差别，值得我们关注。

## 多线程和多进程

下面是Python使用多线程的代码

```python
import os
import threading
import time


def foo(start, end):
    print('Process: {}, Thread: {}'.format(os.getpid(), threading.currentThread().name))


async_target = threading.Thread(target=foo, args=(0, 3, ))
async_target.start()
async_target.join()
```

代码输出中可以看到两个print命令在同一个进程13077，但不同的线程中完成。

```bash-session
Process: 13077, Thread: MainThread
Process: 13077, Thread: Thread-1
```

将该代码调整为多进程，十分简单：

```python
import multiprocessing
async_target = multiprocessing.Process(target=foo, args=(0, 3, ))
async_target.start()
async_target.join()
```

这次，两个print命令发生在不同的进程，分别是13077和13079，但均在各进程的主线程（MainThread）中完成

```bash-session
Process: 13077, Thread: MainThread
Process: 13079, Thread: MainThread
```

### 线程池

Python的线程和进程都支持Pool。如果你在Python 2.7中尝试如下代码

```python
from multiprocessing.pool import ThreadPool
pool = ThreadPool(3)
pool.map(foo, ((0, 3, ), (1, 4, ), (2, 5, )))
```

会得到如下错误

```bash-session
Process: 20254, Thread: MainThread
Traceback (most recent call last):
File "parallel.py", line 22, in <module>
    pool.map(foo, ((0, 3, ), (1, 4, ), (2, 5, )))
File "/usr/lib/python2.7/multiprocessing/pool.py", line 253, in map
    return self.map_async(func, iterable, chunksize).get()
File "/usr/lib/python2.7/multiprocessing/pool.py", line 572, in get
    raise self._value
TypeError: foo() takes exactly 2 arguments (1 given)
```

这是因为(0, 3, )没能自动unpack给foo，所以我们需要加一个workaround函数帮忙unpack一下。

```python
def unpack_foo(args):
    foo(*args)

from multiprocessing.pool import ThreadPool
pool = ThreadPool(3)
pool.map(unpack_foo, ((0, 3, ), (1, 4, ), (2, 5, )))
```

输出

```bash-session
Process: 20843, Thread: Thread-2
Process: 20843, Thread: Thread-3
Process: 20843, Thread: Thread-4
```

不过到了python 3.3，有了starmap方法，我们日子轻松很多

```python
from multiprocessing.pool import ThreadPool
pool = ThreadPool(3)
pool.starmap(foo, ((0, 3, ), (1, 4, ), (2, 5, )))
```

### 进程池

回到正题，如果使用进程池，代码只需做很小的改动，将ThreadPool改为multiprocessing.Pool，其他不用修改

```python
pool = multiprocessing.Pool(3)
pool.starmap(foo, ((0, 3, ), (1, 4, ), (2, 5, )))
```

可能你已经注意到了ThreadPool是放在multiprocessing.pool这个包内的。这是因为先有的进程池模式。而ThreadPool只是通过使用假进程multiprocessing.dummy复用进程池逻辑实现的。

## 计数问题

在多线程或者多进程环境下，如果同样的计数功能（多个线程或者多个进程同时修改一个计数器），代码是否也会很相似呢？先看多线程计数

```python
counter = 0

def increment():
    global counter
    counter += 1

pool = ThreadPool(3)
for i in range(5):
    pool.apply_async(increment)
pool.close()
pool.join()

print('counter={}'.format(counter))
```

程序运行会输出`counter=5`。请注意，我们使用了异步`apply_async`方法，从而实现并发执行5次`increment`方法。因此我们需要使用`pool.join()`方法防止子线程完成工作前，主线程就结束。然而只有在线程池已经关闭（即不再有新的线程进入池子）时，才能执行join。故在join之前，需要执行`pool.close()`

如果像之前一样，我们简单替换`ThreadPool`为`multiprocessing.Pool`，会发现执行后`counter=0`。因为counter并不能跨进程共享，所以每个进程都有自己的counter，并且自增1。而主进程没有执行这个操作，故counter依旧是0。跨进程完成计数需要依赖进程间共享数据，如：Value，Array，Manager等。

```python
shared_counter = None


def init(args):
    ''' store the counter for later use '''
    global shared_counter
    shared_counter = args


def increment():
    global shared_counter
    with shared_counter.get_lock():
        shared_counter.value += 1


init_shared_counter = multiprocessing.Value('i', 0)

pool = multiprocessing.Pool(3, initializer=init, initargs=(init_shared_counter, ))
for i in range(5):
    pool.apply_async(increment)
pool.close()    
pool.join()

print('counter={}'.format(init_shared_counter.value))
```

多进程版本和多线程版本差距较大，几个要关注的点：

1. 首先要创建一个`multiprocessing.Value`作为计数器。构造函数有两个变量，第一个i表明这是一个signed int类型，第二个0表示该变量的初始值。
2. 创建`multiprocessing.Pool`时，需要设置一个初始化函数`init`，并将计数器作为参数传入。该函数会在每个进程初始化时被调用，即`init_shared_counter`会传入每一个进程中，并赋值给进程内的全局变量`shared_counter`
3. 在`increment`函数中可以自增进程内的全局变量`shared_counter`，该操作会影响所有计数器　`init_shared_counter`，故需要加锁。

执行以上代码就会得到`counter=5`的结果。

## 关于回调

线程和进程结束时，可以调用启动时设置的回调函数。

```python
def running():
    print('Running Process: {}, Thread: {}'.format(os.getpid(), threading.currentThread().name))


def completed(res):
    print('Completed Process: {}, Thread: {}'.format(os.getpid(), threading.currentThread().name))


print('Main Process: {}, Thread: {}'.format(os.getpid(), threading.currentThread().name))
pool = ThreadPool(3)
for i in range(5):
    pool.apply_async(running, callback=completed)
pool.close()
pool.join()
```

输出

```bash-session
Main Process: 24321, Thread: MainThread
Running Process: 24028, Thread: Thread-24
Running Process: 24028, Thread: Thread-24
Running Process: 24028, Thread: Thread-24
Running Process: 24028, Thread: Thread-23
Running Process: 24028, Thread: Thread-25
Completed Process: 24028, Thread: Thread-28
Completed Process: 24028, Thread: Thread-28
Completed Process: 24028, Thread: Thread-28
Completed Process: 24028, Thread: Thread-28
Completed Process: 24028, Thread: Thread-28
```

所有的完成回调都发生在同一个进程的，同一个线程中，但不是主线程。所以请确保回调执行可以迅速完成，否则会造成回调堆积，回调线程出现阻塞。

再看一下多进程的回调结果。

```bash-session
Main Process: 24826, Thread: MainThread
Running Process: 24865, Thread: MainThread
Running Process: 24866, Thread: MainThread
Running Process: 24867, Thread: MainThread
Running Process: 24865, Thread: MainThread
Running Process: 24867, Thread: MainThread
Completed Process: 24826, Thread: Thread-31
Completed Process: 24826, Thread: Thread-31
Completed Process: 24826, Thread: Thread-31
Completed Process: 24826, Thread: Thread-31
Completed Process: 24826, Thread: Thread-31
```

所有的回调都发生在父进程，同一个线程中，但也不是主线程。

## 其它

如果使用`apply_async`放入很多线程或者进程等待Pool有资源处理，有可能出现OOM情况。所以当预期会有超大量等待执行的任务时，建议不要调用async，而是使用apply或者map，执行固定数量的任务；该彼此任务结束后，再循环执行下一个批次。
