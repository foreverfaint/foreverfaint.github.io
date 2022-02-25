---
title: Streaming Pipeline in Python - 1
date: 2015-11-01T00:00:00+08:00
category:
    - Programming
tags:
    - Python
    - Design Pattern
---

最近用python 2.7做数据处理。数据说大不大，说小不小，千万级别。显然用Hadoop是大材小用。可由于每笔数据都是一个很大的json对象，处理起来很耗内存。单机加到8GB，依旧会出现OOM。不过还好此类问题有成熟的解决方案“流水线式的数据处理”：每次从文件读一笔记录数据，处理一笔数据，把处理结果持久化，相应的对象实例（内存）被回收。方案成熟易实现。先把代码列在下面，然后再解释其中遇到的坑。

<!--more--> 

首先我们有一个读取数据的方法，大致如下：

```python
def read_data(file_name):
    with open(file_name, mode='r') as f:
            for line in f.readlines():
                from json import loads
                yield loads(line, encoding='utf-8')
```


还要有一个将数据写入文件的方法：

```python
def write_to_text_file(items, output_file):
    from json import dumps
    i = 0
    with open(output_file, mode='w') as f:
        for item in items:
            i += 1
            f.write(dumps(item, encoding='utf-8'))
            f.write('\n')
            if i % 10000 == 0:
                print i
```

最后把代码串在一起，主流程代码如下：

```python
data = read_data('data.txt')
data = filter(lambda item: should_keep(item), data)
data = map(lambda item: convert_item(item), data)
write_to_text_file(items, 'processed_data.txt')
```

可当你执行该程序后，可能会吃惊的发现，内存使用量完全没有下降。问题出在下面这一行：

```python
for line in f.readlines():
```

阅读[readlines](https://docs.python.org/2/library/stdtypes.html?highlight=readlines#file.readlines)帮助文档之后，发现该函数如果不指定sizehint参数的话，会将文件内容全部读入内存，组成一个list。

> Read until EOF using **readline()** and return a list containing the lines thus read. If the optional sizehint argument is present, instead of reading up to EOF, whole lines totalling approximately sizehint bytes (possibly after rounding up to an internal buffer size) are read. Objects implementing a file-like interface may choose to ignore sizehint if it cannot be implemented, or cannot be implemented efficiently.

修改读文件代码如下：

```python
def read_data(file_name):
    with open(file_name, mode='r') as f:
        from json import loads
        while True:
            line = f.readline()
            if line:
                yield loads(line, encoding='utf-8')
            else:
                break
```

再次运行之后，再一次吃惊的发现内存依旧没有降下来。这回的问题出在map和filter方法上。Streaming依赖于 `yield` ，即generator expression（参看[PEP 0289](https://www.python.org/dev/peps/pep-0289/)）的使用。map和filter在python2.7中是不是基于generator expression实现的呢？我们验证一下：

```python
def mapped(n):
    print 'mapped %d' % n
    return n
    
def filtered(n):
    print 'filtered %d' % n
    return n > 0
```

如果map或者filter是generator expression实现的，很明显只有最后一步list(data)才会触发generator执行，这样mark1和mark2两个字符串会在filtered XXX和mapped XXX之前打印出来。可事实上，运行后的结果如下

```python
>>> data = [-1, 0, 1]
>>> data = map(mapped, data)
>>> print 'mark1'
mapped -1
mapped 0
mapped 1
mark1
>>> data = filter(filtered, data)
>>> print 'mark2'
>>> data = list(data)
filtered -1
filtered 0
filtered 1
mark2
```

这说明map和filter是立即执行，而非generator expression的实现。正是这个原因，导致数据依旧是全部读入内存中。阅读[map和filter的帮助文档](https://docs.python.org/2/library/functions.html#filter)后发现map和filter等价于list comprehension，是立即执行，而非generator expression。

> Note that filter(function, iterable) is equivalent to **[** item for item in iterable if function(item) **]** if function is not None and **[** item for item in iterable if item **]** if function is None.

将map和filter调整为generator expression的代码为：

```python
data = read_data('data.txt')
data = (item for item in data if should_keep(item)) 
data = (convert_item(item) for item in data)
write_to_text_file(items, 'processed_data.txt')
```

经过这次调整之后，内存再也不是问题。我们的Streaming Pipeline终于完工了。
