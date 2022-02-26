---
title: Python测试开发2 - mock
date: 2021-10-10T13:55:00+08:00 
category:
    - Programming
:tags:
    - Python
    - Test
---

上篇文章介绍了`python`测试开发的第一大神器`fixture`， 本篇则聚焦另一神器`mock`。

<!--more--> 

## 关于mock

业务逻辑会依赖第三方API，或者特定数据库内容。如果单元测试把这些依赖都囊括进来，逻辑将会十分复杂。运行测试也会消耗大量时间和计算资源。这种情况下，使用[unittest.mock](https://docs.python.org/3/library/unittest.mock.html)模拟外部依赖，提供“设计”好的结果给测试逻辑用，会起到事半功倍的效果。

好的系统设计层次分明，每层都将细节封装，抽象出一组API供上层逻辑调用。因此，下层API都可以视作上层逻辑的“外部依赖”。对上层逻辑进行测试时，可使用`mock`模拟下层API的返回值。这样做优点有三：

- 首要优点涉及“分层系统测试原则”，即：分层系统测试，每一层的测试重点应该放在**当前层的逻辑（如何调用各下层API，并将结果组装为本层结果）；而不应该分散精力测试下层API对错 (下层API对错应由下层API的单元测试保证，无需在当前层重复验证)**。使用`mock`模拟下层API是上述测试原则的体现。
- 其次，系统分层的目的就是隐藏细节，防止底层细节变化对上层逻辑造成冲击。单元测试在验证上层逻辑时，也应该遵循同样的思想：**避免依赖底层“细节”准备测试数据**。否则底层细节一旦变化，测试用例不得不调整。
- 最后，无需每层测试都从底层开始准备测试数据，减少单元测试的复杂度。

举个例子，假设系统有两层：数据层`MySQLProvider`和`CacheCombinedDataProvider`。

```python
class MySQLProvider:
    _data = []

    def insert(self, item):
        if item >= 2:
            MySQLProvider._data.append(item)

    def select(self):
        return MySQLProvider._data

    def delete(self, item):
        MySQLProvider._data.remove(item)

class CacheCombinedDataProvider:
    def __init__(self):
        self._db = MySQLProvider()

    def get_data(self):
        data = self._db.select()
        first = data[0]
        remained = data[1:]
        return [x for x in remained if 1 < first + x < 5]
```

不用`mock`，则测试用例如下：

```python
def test_mysql_provider():
    # 底层API测试用例
    target = MySQLProvider()
    try:
        # 准备测试数据
        target.insert(1)
        target.insert(2)
        # 测试
        assert 1 == len(target.select())
    finally:
        # 清理数据
        target.delete(2)


def test_cache_combined_data_provider():
    # 底层API测试用例
    target = MySQLProvider()
    try:
        # 准备测试数据
        target.insert(2)
        target.insert(2.5)
        target.insert(5)
        # 测试
        assert 1 == len(CacheCombinedDataProvider().get_data())
        assert CacheCombinedDataProvider().get_data()[0] == 2.5
    finally:
        # 清理数据
        target.delete(2)
        target.delete(2.5)
        target.delete(5)
```

上述测试有几个问题：

- 为了测试`get_data`，不得不在`test_cache_combined_data_provider`中重复`test_mysql_provider`做过的准备工作。
-`test_cache_combined_data_provider`失败的原因应该是`CacheCombinedDataProvider().get_data()`逻辑有缺陷。然而当前的测试方法下，`insert`或者`select`有错误，也会导致测试失败。这就违反了前文所述第一原则，当前测试不仅在测试当前层，还分散了精力重复测试底层（即`test_mysql_provider`应该保证的内容）
- 为了能测试`get_data`，我们不得不理解`insert`逻辑，插入满足测试需要的数据；一旦`insert`逻辑发生变化，`test_cache_combined_data_provider`相关代码也不得不调整。何其无辜！`get_data`的逻辑并没有任何变化呀！

如果我们使用`mock`，则代码变为：

```python
def test_cache_combined_data_provider_2():
    with mock.patch.object(MySQLProvider, "select") as mock_select:
        mock_select.return_value = [2, 2.5, 5]
        actual = CacheCombinedDataProvider().get_data()
        assert 1 == len(actual)
        assert actual[0] == 2.5
```

测试代码清爽许多。更重要的是，只要`select`接口不变，`test_cache_combined_data_provider_2`就无需修改。一旦`test_cache_combined_data_provider_2`测试失败，毫无疑问`get_data`出了`bug`（而不是`MySQLProvider`有`bug`）。

### 使用mock测试的缺点

有好必有坏， 使用`mock`进行单元测试的诟病之一就是：单元测试不再是针对API输入输出的测试，而是“利用（耦合）”当前层的实现细节（`mock`实现细节中的某些依赖）。因此两种情况下，应避免使用`mock`：

- 使用`mock`带来的复杂度不比准备测试数据低多少，甚至更高时，不妨直接准备测试数据。
- 不希望单元测试太“白盒”的时候，每层逻辑都按照API定义的输入输出严格做黑盒测试，不需要`mock`细节。

### mock类实例方法

`mock`类的实例方法有多种方法，例如：

-`mock`类的实例方法（见：`test_call_take_1`）。
-`mock`类本身，将生成的类实例替换为`mock.MagicMock`（见：`test_call_take_2`）。

```python
class Lower:
    def take(self, item):
        print(self)

def call_take(a):
    Lower().take(a)

def test_call_take_1():
    with mock.patch.object(Lower, "take") as take_func:
        call_take(1)
        take_func.assert_called_once_with(1)

def test_call_take_2():
    with mock.patch(__name__ + ".Lower") as Lower_class:
        Lower_class.return_value = mock.MagicMock()
        call_take(1)
        Lower_class.return_value.take.assert_called_once_with(1)
```

但是你会意识到，无论哪一种方法，在调用`take`时，都“忽略”了`self`参数。

`Python`中有`bound method`和`unbound method`的区别。`bound method`就是类的实例方法，方法中第一个参数为`self`；`unbound method`就是类的静态方法。当`mock`类实例方法时，无形中把`bound method`变为了`unbound method`（`patch`和`patch.object`隐藏了`self`）。

大部分时候，这样的“忽略”对测试目标没有影响。不过如果你的确需要测试`bound method`， 比如下面这种情况：你需要确认`take`函数接收到的`self`的`a`已经赋值（这属于要验证的`call_take`的逻辑部分）。

```python
class Lower:
    def __init__(self, default_a):
        self.a = default_a

    def take(self, new_a):
        self.a = new_a

def call_take(a):
    default_a = fetch_default_a_via_remove_config_server()
    Lower(default_a).take(a)
```

可以使用`mock.patch.object`的[autospec=True](https://docs.python.org/3.6/library/unittest.mock.html#unittest.mock.patch.object)设置，将`mock`出的方法的签名改为和原始方法一致（即：变为`bound method`，调用时传入`self`作为第一个参数）

```python {hl_lines=2}
def test_call_take_1():
    with mock.patch.object(Lower, "take", autospec=True) as take_func:
        call_take(1)
        take_func.assert_called_once_with(1)
```

执行起来，`take_func.assert_called_once_with(1)`测试失败，因为`take_func`收到的第一个参数是`self`而不是`1`。

```bash-session
E           AssertionError: expected call not found.
E           Expected: take(1)
E           Actual: take(<test.Lower object at 0x7f661e83c760>, 1)
E
E           pytest introspection follows:
E
E           Args:
E           assert (<test.Lower object at 0x7f661e83c760>, 1) == (1,)
E             At index 0 diff: <test.Lower object at 0x7f661e83c760> != 1
E             Left contains one more item: 1
E             Full diff:
E             - (1,)
E             + (<test.Lower object at 0x7f661e83c760>, 1) 
```

正确的测试如下：

```python
def test_call_take_1():
    default_a = 10
    with mock.patch.object(Lower, "take", autospec=True) as take_func, \
        mock.patch(__name__ + ".fetch_default_a_via_remove_config_server", return_value=default_a):
        call_take(1)
        take_func.assert_called_once()
        args, _ = take_func.call_args
        assert args[0].a == default_a  # 验证self.a已经被赋值
        assert args[1] == 1
```

通过获取`mock`对象的`call_args`，拿到第一个参数（即`self`），检查是否和`default_a`一致。

### mock类的property

假设类定义如下：

```python
class A:
    @property
    def f(self):
        return "a"

    def foo(self):
        return "aa"
```

如果希望`mock`属性`f`， 可否直接将`f`换为`mock.Mock`? 毕竟`property`本质上是一个方法，如果`foo`可以直接被替换，理论上`f`也应该可以。

```python
def test_property():
    a = A()
    a.foo = mock.Mock(return_value="bb")
    assert a.foo() == "bb"
    a.f = mock.Mock(return_value="b")
    assert a.f == "b"
```

很遗憾`foo`的替换成功了，但是`f`的替换由于`f`是个只读属性失败了（`AttributeError: can't set attribute`）。那是不是把`f`改为写属性就可以了？

```python
class A:
    @property
    def f(self):
        return "a"

    @f.setter
    def f(self, v):
        pass

def test_property():
    a = A()
    a.f = mock.Mock(return_value="b")
    assert a.f == "b"
```

依旧行不通。`mock.Mock`被当作值`v`被赋值给`A`的实例，而并没有替换整个函数`f`。正确的做法是通过`mock.patch`将`f`替换为一个`mock.Mock`使用。下面是正确的测试代码：

```python
def test_property2():
    with mock.patch(__name__ + ".A.f", new_callable=mock.Mock(return_value="b")):
        assert A().f == "b"
```

### mock asyncio

介绍`mock asyncio`之前，需要提一下`pytest`不能直接测试`asyncio`代码。需要安装插件`pytest-asyncio <https://github.com/pytest-dev/pytest-asyncio>`_。`pytest-asyncio`的具体使用，可参看相关文档。下面是一段最基础的`async`函数测试示例：

```python
# -*- encoding: utf-8 -*-
import asyncio
import pytest

async def async_foo():
    await asyncio.sleep(0.1)
    return "a"

@pytest.mark.asyncio
async def test_mock_foo():
    res = await async_foo()
    assert "a" == res
```

`Python 3.8`之后，`unittest.mock`提供了`AsyncMock`对象，让`mock``async`方法和普通方法几乎一样：

```python
@pytest.mark.asyncio
async def test_mock_foo():
    with mock.patch(__name__ + ".async_foo", side_effect=mock.AsyncMock(return_value="b")):
        res = await async_foo()
        assert "b" == res
```

对于老版本的`Python`， 可以安装`asyncmock`包使用`AsyncMock`。