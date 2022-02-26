---
title: Streaming Pipeline in Python - 2
date: 2015-11-20T00:00:00+08:00 
category: 
    - Python
tags:
    - Python
    - Design Pattern
---

除了[上一篇文章]({{< ref "/posts/streaming-pipeline-in-python-1" >}})中提到的几个问题，在使用Generator Expression的过程中，还遇到了一个bug。

<!--more--> 

pipeline中数据处理分为两步:

第一步，基于每一个旧数据生成一笔新数据，简要代码如下。请注意我们使用了生成器。

```python
def extend_old_data(items):
    for item in items:
        # generate a new item based on an old item
        new_item = Item()
        new_item['data'] = item['data'] + 1
        yield new_item
```

第二步，使用chain将新旧数据生成器混合在一起，关于[itertools](https://docs.python.org/2/library/itertools.html)

```python
from itertools import chain
old_data = read_data('data.txt')
new_data = extend_old_data(old_data)
all_data = chain(old_data, new_data)
```

当然最后要把数据写入文件

```python
write_to_text_file(all_data, 'processed_data.txt')
```

如果data.txt中内容为

```bash-session
1       
2
```

processed_data.txt中会是什么内容？我们可是期盼得到  

```bash-session
1          
2          
3        
4
```

可如果运行代码，我们得到是          

```bash-session
1              
2
```

Generator Expression是生成器，生成器的特点是所有数据都是on the fly，“用后即焚”。我们把代码按照运行的顺序从新排布一下：

```python
old_data = read_data('data.txt')
write_to_text_file(old_data, 'processed_data.txt')
write_to_text_file(extend_old_data(old_data), 'processed_data.txt')
```

看出来了吗？old_data被write_to_text_file先进行了“用后即焚”。到了extend_old_data(old_data)处，old_data已经空了，自然不会有新的item生成。如果不在意新item和旧item的排列顺序的话，为了正确实现合并新旧数据的意图，需要修改extend_old_data方法如下：

```python
def extend_old_data(items):
    for item in items:
        # generate a new item based on an old item
        new_item = Item()
        new_item['data'] = item['data'] + 1
        yield item
        yield new_item

old_data = read_data('data.txt')
all_data = extend_old_data(old_data)
```