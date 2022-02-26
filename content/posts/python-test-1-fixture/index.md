---
title: Python测试开发1 - fixture
date: 2021-10-07T22:03:00+08:00 
category: 
    - Programming
tags: 
    - Python
    - Test
---

资深开发者实际时间分配有可能是4分调研+设计，3分编码，3分测试。且越是老鸟，测试比重越高。测试下功夫了，质量就到位了，返工次数少，调试难度低，工效KPI也就高了。本文分享`Python`测试开发中的一些心得。

<!--more--> 

`Python`测试开发通常以“单元测试”的形式体现。常用的单元测试框架有`unittest`、`nose`和`pytest`。其中 [pytest](https://github.com/pytest-dev/pytest)功能丰富、成熟度高、普及度高，且社区始终维护更新。 

`pytest`通过[pytest-mock](https://github.com/pytest-dev/pytest-mock/tree/main/src/pytest_mock)提供了`mocker fixture`模拟外部依赖。`pytest-mock`底层用的是`unittest.mock`（见[代码](https://github.com/pytest-dev/pytest-mock/blob/main/src/pytest_mock/plugin.py>)）。因此，我选用`pytest`+ 原生`unittest.mock`作为测试开发组合。此外，还会用[tox](https://tox.wiki/en/latest/)作为单元测试驱动框架。

单元测试工具并不复杂，就不详细介绍了。本系列文章重点放在两大神器`fixture`和`mock`上。

> 单元测试工具不复杂，不代表单元测试不复杂。单元测试的复杂性更多体现在：测试用例设计、测试数据设计和准备、如何减少测试代码对外部系统的依赖，以及降低待测部分持续变化对测试代码的冲击，等“设计”层面问题。

## 关于fixture

单元测试传递**同样**的输入到目标代码，预期目标代码输出**同样**的结果，从而判断测试通过与否。为了达到“**同样**的输入”这个目标，通常需要测试执行前（后），执行**同样**的初始化（清理）逻辑。被抽离封装后的初始化和清理逻辑，可称为`fixture`。`pytest`中使用[fixture](https://docs.pytest.org/en/6.2.x/fixture.html)十分简单，可参考帮助文档。下文只讲几个不关注就掉坑的问题。


### fixture被执行几次？

在下面的代码中，`foo2`和`foo3`都引用了`foo1`， 当`pytest`执行该测试模块时，到底`foo1`被执行几次？

```python
# -*- encoding: utf-8 -*-
import pytest

@pytest.fixture
def foo1():
    print("foo1")

@pytest.fixture
def foo2(foo1):
    print("foo2")

@pytest.fixture
def foo3(foo1):
    print("foo3")

def test_foo(foo2, foo3):
    assert True

def test_foo2(foo2):
    assert True

def test_foo3(foo3):
    assert True
```

试一下：

```bash-session
$ pytest ./test.py  ; 假设测试模块名为test.py
...

test.py::test_foo2
foo1
foo2
PASSED

test.py::test_foo3
foo1
foo3
PASSED

test.py::test_foo
foo1
foo2
foo3
PASSED
```

观察输出会有如下结论：

1. 每个`test_*`都会执行一次`foo1`。因此不用担心一个测试修改了`fixture`，而污染另一个测试的问题。
2. 对于同一个`test_*`，即使`foo1`被引用多次，也只会执行一次。**之后的引用，都会得到第一次执行结果的缓存** 。所以务必小心：在不得不多次引用时，一旦某个引用改变了`fixture`， 则所有引用都会改变（因为大家用的是同一个对象）。


### fixture在何时执行？

毫无疑问，`fixture`在每个测试前才会被执行。没有被用到的`fixture`不会被执行。依旧使用`test.py`中的`fixture`， 但测试方法调整为：

```python
def test_foo1(foo1):
    assert True

def test_foo3(foo3):
    assert True
```

执行时，先打印了测试方法名称，然后才打印出`fixture`中的内容；同时`foo2`没有引用，没有打印，说明没有执行：

```bash-session
test.py::test_foo3
foo1
foo3
PASSED

test.py::test_foo1
foo1
PASSED
```

### scope和autouse

上文提到`fixture`每个测试前都执行，其实这不是全部真相。毕竟有些`fixture`是重量级的，每个方法执行一次开销太大，得不偿失。`fixture`有两个重要参数`scope`和`autouse`， 结合使用可以控制`fixture`执行的时机和次数。

`autouse`不言自明。设置`autouse`为`True`的`fixture`即使没有被测试方法引用，也会执行。例如：每个测试都用到了数据库。为了避免测试相互干扰，执行每个测试前，需要清理数据库。每个方法签名上增加`cleaned_db`的`fixture`固然可以，但更好的方法是设置`autouse=True`，一劳永逸的避免漏加`cleaned_db`造成测试脏数据遗留的风险。

```python
# -*- encoding: utf-8 -*-
import pytest

@pytest.fixture(autouse=True)
def foo1():
    print("foo1")

@pytest.fixture
def foo2():
    print("foo2")

def test_foo1():
    assert True

def test_foo1_2():
    assert True
```

验证一下：可以看到`foo1`的`fixture`没有显式引用，也被执行了；而`foo2`则没有执行。

> 注意：即使加了`autouse=True`之后，`foo1`依旧每个测试执行一次。另外，请不要误会：给`fixture`增加了`autouse=True`，不代表可以在任何测试方法里直接使用这个`fixture`。如果要使用这个`fixture`， 必须将其显式添加到待测方法的函数签名中。

```bash-session
test.py::test_foo1_2
foo1
PASSED

test.py::test_foo1
foo1
PASSED
```

使用`scope`则可以调整`fixture`执行的范围，如：

-`scope`默认值为`function`： 每个测试都执行一次
-`class`： 一个测试类只执行一次
-`module`： 一个`.py`文件执行一次
-`package`：`test.py`所在包（当前包含`__init__.py`目录）及其子包（当前目录包含`__init__.py`的子目录）执行一次
-`session`：`pytest`所执行的进程中，只执行一次

```python
# -*- encoding: utf-8 -*-
import pytest

@pytest.fixture(autouse=True)
def foo1():
    print("foo1")

@pytest.fixture(autouse=True, scope="module")
def foo2():
    print("foo2")

def test_foo1():
    assert True

def test_foo1_2():
    assert True
```

`foo1`的`scope`为`function`，故两个测试触发两次执行；`foo2`的`scope`为`module`，整个文件只执行一次。

> 同时注意：`fixture`会在`scope`指定范围内，第一个测试运行时，才会执行。

```bash-session
test.py::test_foo1_2
foo2
foo1
PASSED

test.py::test_foo1
foo1
PASSED
```

### yield

`fixture`可以用`return`或者`yield`返回对象给测试方法使用。如果使用`yield`则可以实现`tearDown`功能。例如：

```python
# -*- encoding: utf-8 -*-
import pytest


@pytest.fixture
def foo1():
    print("foo1 start")
    yield "a"
    print("foo1 end")

@pytest.fixture
def foo2(foo1):
    print("foo2 start")
    yield "b"
    raise ValueError("foo2")

def test_foo1(foo2):
    print("test_foo1")
    assert True
```

`test_foo1`执行会调用`foo2`，`foo2`调用`foo1`。当`test_foo1`执行完毕，则执行`yield "b"`之后的清理代码。即使遇到异常清理失败（`ValueError`），`foo1`的`yield "a"`之后的清理代码依旧会被继续执行。

> 注意：`test_foo1`测试结果是`PASSED`，不会因为`fixture`清理失败而失败。

```bash-session
test.py::test_foo1 
foo1 start
foo2 start
test_foo1
PASSED
foo2 end    
foo1 end

test.py::test_foo1 ERROR
```
