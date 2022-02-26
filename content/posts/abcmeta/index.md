---
title: Python的抽象类
date: 2016-04-16T13:59:34+08:00
category:
    - Programming
:tags:
    - Python
---

面向对象语言大都支持抽象类：比如C#中的abstract关键字，C++的类方法的=0语法。python也支持面向对象编程范式。如何在Python中创建一个抽象类呢？答案是 [ABCMeta](https://docs.python.org/2/library/abc.html)（ABC = Abstract Base Class）。

<!--more--> 

## Python中声明抽象基类

```python
import abc

class BaseCalculator(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def calculate(self, data):
        print 'i am base'
```

运行下述代码，会收到TypeError异常，可见BaseCalculator是一个无法初始化的抽象类。请注意：尽管calculate有一个完整的实现（没有抛出NotImplementedError异常），它依旧是一个抽象方法。

```bash-session
>>> a = BaseCalculator()
>>> a.calculate([])
TypeError: Can\'t instantiate abstract class BaseCalculator with abstract methods calculate
```

## 使用直接继承抽象基类，创建子类

和其他面向对象语言一样，子类继承抽象父类，并实现它的全部抽象方法即可：

```python
class DerivedCalculator2(BaseCalculator):
    def calculate(self, data):
        print 'i am dervied'
```

运行下述代码，则得到输出：

```bash-session
>>> print 'Subclass:', issubclass(DerivedCalculator2, BaseCalculator)
Subclass: True

>>> print 'Instance:', isinstance(DerivedCalculator2(), BaseCalculator)
Instance: True

>>> a = DerivedCalculator2()
>>> a.calculate([])
i am derived
```

issubclass和isinstance帮助我们验证了DerivedCalculator2的确是BaseCalculator子类。

## “注册”子类到抽象基类

除了“传统”的继承，Python中还允许“注册”一个子类到抽象基类：

```python
class DerivedCalculator1(object):
    def calculate(self, data):
        print 'i am derived'

BaseCalculator.register(DerivedCalculator1)
```

运行下述代码，我们得到完全一样的输出：

```bash-session
>>> print 'Subclass:', issubclass(DerivedCalculator1, BaseCalculator)
Subclass: True

>>> print 'Instance:', isinstance(DerivedCalculator1(), BaseCalculator)
Instance: True

>>> a = DerivedCalculator1()
>>> a.calculate([])
i am derived
```

不过如果调用抽象基类的`__subclasses__`，你会发现这个“注册”的子类并没有出现在subclass列表中。下面代码只输出**DerivedCalculator2**

```python
for sc in BaseCalculator.__subclasses__():
    print sc.__name__
```

## 部分实现子类

如果BaseCalculator中有两个抽象方法calculate和report。DerviedCalculator1和DerviedCalculator2都只实现了其中的calculate，称它们为部分实现子类。

```python
import abc

class BaseCalculator(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def calculate(self, data):
        print 'i am base'

    @abc.abstractmethod
    def report(self):
        print 'i am base'

class DerivedCalculator1(object):
    def calculate(self, data):
        print 'i am derived'

BaseCalculator.register(DerivedCalculator1)

class DerivedCalculator2(BaseCalculator):
    def calculate(self, data):
        print 'i am dervied'
```

运行下述代码，在最后一个print处会遇到TypeError异常 。用“注册”实现的部分子类，竟然通过了isinstance的检查！而直接继承的子类则未通过检查。考虑到子类的确不是一个“完整的”抽象父类之子类，我们可不希望直到调用“report”方法时程序才崩溃！基于防御性编程思想[Defensive Programming](https://en.wikipedia.org/wiki/Defensive_programming)，最好能在某个“很早的时刻”，通过Python运行时检查把问题及时暴露出来。所以使用直接继承声明子类，结合instance判断，不失为更好的选择。

```bash-session
>>> print 'Subclass:', issubclass(DerivedCalculator1, BaseCalculator)
Subclass: True

>>> print 'Instance:', isinstance(DerivedCalculator1(), BaseCalculator)
Instance: True

>>> print 'Subclass:', issubclass(DerivedCalculator2, BaseCalculator)
Subclass: True

>>> print 'Instance:', isinstance(DerivedCalculator2(), BaseCalculator)
TypeError: Can\'t instantiate abstract class DerivedCalculator2 with abstract methods report
```
    
本文所述内容参考自[https://pymotw.com/2/abc/](https://pymotw.com/2/abc/)
