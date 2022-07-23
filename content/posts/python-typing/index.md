---
title: "Python Typing"
date: 2022-07-23T17:05:00+08:00
category: 
    - Programming
tags: 
    - Python
---

最近看到有人在某乎上吐槽`Python`越来越卷，一个动态脚本语言开始用`typing`做静态类型检查。这个说法很哗众取宠。毕竟现在的`Python`已经不是十年前的`Python`，不只用于爬虫、运维和数据处理这些传统“脚本”类开发，也逐渐的在各种互联网软件、中间件和客户端开发中扮演重要角色（这部分开发过去是`Java`, `C#`，`C++`的地盘）。

<!--more--> 

业务需求增长会迫使架构增长；架构增长必然是模块数增加、交互复杂度变高； 伴随而来的是更长的产品生命周期（开发和维护的时间都会拉长）；这些增长都会触发团队膨胀；然而团队增长总是很难匹配业务/技术需求增长，毕竟人力成本会有天花板控制、招募和培训难以一朝一夕解决、市面上可匹配岗位的人员供给有限，以及沟通复杂度提升导致人效下降，这些因素最终都会导致团队质量下滑；一增一降的结果就是产品质量不增反降。

小型企业变为大中型企业要从“人治”变为“法治”。软件规模增长要想稳定住质量，也要从依赖“人员质量”的思想转变到“机制和流程改良”思想。更易于写出严谨接口（从而减少他人误用）、自动化生成高质量文档（知识查询和传承）、静态代码分析（将错误消灭在运行前），和代码可读性提升（提升理解、维护和改进成本）都是“机制和流程改良”的实操。显然有类型系统的静态语言在这些方面有天然优势。这也是在中等以上规模软件开发中，静态语言始终占据优势的原因之一。`Python`引入`typing`后，在类型系统方面得到提升。使得喜爱`Python`的开发者，在选择它进行中等规模软件开发时，又多了一个理由。

`Python`的`typing`覆盖了各种类型检查场景，符合一个工具要“简单场景简单上手，复杂场景也能支持”的理念。从我自身感受来说，常用的`typing`需求（例如：参数类型定义，返回值定义，回调函数定义等）可以被40% `typing`功能覆盖住；一些较少出现，但使用`typing`会极大减少错误的场景（例如：生成器，协程方法，泛函等）可以被另外40% `typing`功能覆盖；最后一些高级场景（如：函数Curry化，协程生成器/迭代器等，可以被最后20% `typing`覆盖。

本篇文章提要如下：

- 变量的`typing`比较简单，本文不再介绍。我们从函数`Callable`的`typing`讲起
- `Python`的**类**是一组变量（类变量和实例变量）和一组 *第一个参数是类实例`self`（或类本身）的函数* 构成，所以类的`typing`与函数的`typing`并无不同，我们也不单独介绍
- 函数之后，我们介绍泛型`typing`，也是本文中最难、篇幅最大的部分。讲泛型不得不讲协变（`covariance`）和逆变（`contravarance`），讲协变和逆变又不得不先讲`Subtype`，这些内容都集中在泛型这一节中讲解
- 最后会介绍装饰器（即高级函数变换）的`typing`

## typing的使用

在讲`typing`之前，我们先简要说明有了`typing`以后要怎么用起来，从而得到好处？

### 静态类型检查

首先可以用[`mypy`](https://mypy.readthedocs.io)通过`typing`进行类型检查

```bash-session
$ pip install mypy
Defaulting to user installation because normal site-packages is not writeable
Collecting mypy
  Downloading mypy-0.971-cp38-cp38-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_12_x86_64.manylinux2010_x86_64.whl (17.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 17.3/17.3 MB 12.1 MB/s eta 0:00:00
Collecting tomli>=1.1.0
  Using cached tomli-2.0.1-py3-none-any.whl (12 kB)
Collecting typing-extensions>=3.10
  Downloading typing_extensions-4.3.0-py3-none-any.whl (25 kB)
Collecting mypy-extensions>=0.4.3
  Using cached mypy_extensions-0.4.3-py2.py3-none-any.whl (4.5 kB)
Installing collected packages: mypy-extensions, typing-extensions, tomli, mypy
Successfully installed mypy-0.971 mypy-extensions-0.4.3 tomli-2.0.1 typing-extensions-4.3.0

$ mypy main.py  # 假设当前目录有main.py文件
main.py:32: error: Value of type variable "T" of "func" cannot be "int"
main.py:33: error: Value of type variable "S" of "func" cannot be "float"
Found 2 errors in 1 file (checked 1 source file)
```

`mypy`会输出所有和`typing`标注有冲突的代码。类似的工具还有[`pylint`](https://pylint.pycqa.org/en/latest/)

### 文档生成

如果使用`Visual Studio Code`，可以直接安装[`autoDocstring`](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring)。这个插件帮助开发者自动生成`docstring`，并且使用`typing`来推断参数类型。在任意函数下敲下“"""”后回车，即可得到如下自动生成的文档模板：

```Python
def func(a: int, b: str) -> float:
    """_summary_

    Args:
        a (int): _description_
        b (str): _description_

    Returns:
        float: _description_
    """
    return 1.0
```

然后使用[`mkgendocs`](hhttps://github.com/davidenunes/mkgendocs)或者[`pdoc3`](https://pdoc3.github.io/pdoc/)将`docstring`抽成`markdown`文件用于帮助文档渲染。


## Callable

```Python
def func(f):
    return f(1, "a")


print(func(lambda x, y: 1.0))  # 1.0
```

`func`函数使用`Callable`来定义对回调函数`f`的要求：

```Python
from typing import Callable


def func(f: Callable[[int, str], float]) -> float:
    return callback(1, "a")
```

如果允许回调函数`f`接收任何类型的参数，可以使用`Callable[[Any, Any], float]`来定义（有几个输入参数，就需要有几个`Any`占位），也可以使用`...`语法占据输入参数位置（可以代表任意多个输入参数）

```Python
from typing import Callable


def func(f: Callable[..., float]) -> float:
    return callback(1, "a")
```

### None or NoReturn?

如果函数没有`return`语言，运行时默认返回None值

```Python
def func():
    pass


print(func()) #  None
```

可以使用`-> None`来定义没有返回值的情况

```Python
def func() -> None:
    pass
```

如果函数**不应该**返回任何值，例如：

```Python
def func():
    raise NotImplementedError()
```

则应使用`NoReturn`

```Python
from typing import NoReturn


def func() -> NoReturn:
    raise NotImplementedError()
```

### Variable Arguments

函数使用可变参数的情况：

```Python
def func(a, *args, **kwargs):
    pass


func(1, "a", "b", c=1.1, d=1.2)
```

`*args`总会被解释为`Tuple`，`**kwargs`则总会被解释为`Dict`，因此使用`typing`时，只需指明`Tuple`的元素类型和`Dict`的`value`类型（`key`类型总是`str`），如：

```Python
def func(a: int, *args: str, **kwargs: float):
    pass


func(1, "a", "b", c=1.1, d=1.2)
```

但是如果`*args`和`**kwargs`由多种不同的类型组成，则应该使用`Any`或者`object`来做`typing`定义。

### 协程

协程由`async`修饰，可以`await`的函数：

```Python
async def func(a: int) -> str:
    return "hello"
```

`typing`是在`Callable`的返回值上增加`Awaitable`修饰：

```Python
from typing import Callable, Awaitable


c_func: Callable[[int], Awaitable[str]] = func

ret = await c_func(1)
```

### 函数重载

这部分内容引用自[Python Type Hints - How to Use @overload](https://adamj.eu/tech/2021/05/29/Python-type-hints-how-to-use-overload/)。

```Python
from __future__ import annotations

from collections.abc import Sequence


def double(input_: int | Sequence[int]) -> int | list[int]:
    if isinstance(input_, Sequence):
        return [i * 2 for i in input_]
    return input_ * 2


def print_int(a: int):
    print(a)


print_int(double(1))
```

这个函数的本意是：输入是`int`类型，则输出也是`int`类型；输入是`list`类型则输出类型也是`list`。但是代码中的`typing`无法正确表达约束（输入是`int`类型，输出是`list`类型的组合也满足现在的`typing`）。`print_int(double(1))`在静态类型检查时，报错`Argument 1 to "print_int" has incompatible type "Union[int, List[int]]"; expected "int"`。需要使用`overload`装饰器给静态类型检查更多的帮助：

```Python
from __future__ import annotations

from collections.abc import Sequence
from typing import overload


@overload
def double(input_: int) -> int:
    ...


@overload
def double(input_: Sequence[int]) -> list[int]:
    ...


def double(input_: int | Sequence[int]) -> int | list[int]:
    if isinstance(input_, Sequence):
        return [i * 2 for i in input_]
    return input_ * 2


def print_int(a: int):
    print(a)


print_int(double(1))
```

两个占位用的`overload`函数会被静态类型检查工具收集（`mypy`），但只有没有`overload`修饰的`double`函数会用做真正的实现（`import`阶段，最后`import`的符号定义会覆盖之前的符号定义）。如上改造后，`mypy`不会再报任何错误。

## 泛型

`Python`支持某种泛型范式很简单，如下这个函数对于所有支持`__add__`方法的类型都可以执行：

```Python
def func(a, b):
    return a + b


print(func(1, 2))  # 输出3
print(func([1, 2], [3]))  # 输出 [1, 2, 3]
print(func("Hello ", "World"))  # 输出 Hello World
```

### TypeVar

但如何告诉静态类型检查这是一个泛型函数？这时候就要使用`TypeVar`方法（类似于`C#`泛型中`type parameter`）：

```Python
from typing import TypeVar

T = TypeVar('T') 

def func(a: T, b: T) -> T: 
    return a + b


r = func(1, "a")  # 检查无法通过，因为形参a是int类型，b是str类型，不是typing提示的同一种类型
```

`TypeVar`还支持设置约束：

- 使用`T`作为类型的变量，必须是`Sequence`的subtype
- 使用`S`作为类型的变量，必须是`int`或者`list`

```Python
from typing import Sequence, TypeVar, List

T = TypeVar("T", bound=Sequence)
S = TypeVar("S", int, list)

def func(a: T, b: S) -> None:
    ...

func(1, 1)  # 检查无法通过，因为a的类型必须是Sequence的subtype
func([1, 2, 3], 1.0)  # 检查无法通过，因为b的类型必须是int或者list
func([1, 2, 3], [1, 2])
```

### Generic

定义泛型类则需要使用`Generic`：

```Python
from typing import TypeVar, Generic, List


T= TypeVar("T")


class SingleLinkedList(Generic[T]):
    def __init__(self, value: T, next: "SingleLinkedList") -> None:
        self.value = value
        self.next = next

    def __repr__(self) -> str:
        return f"{self.value} -> {self.next}"


def build_linked_list_from_int_list(data: List[int]) -> SingleLinkedList[int]:
    if not data:
        return None
    return SingleLinkedList(data[0], build_linked_list_from_int_list(data[1:]))


print(build_linked_list_from_int_list([1, 2]))
```

### Subtype Relationship

我们用符号`<:`来表示`is a subtype of`这个含义。当且仅当类型`A`和类型`B`满足如下条件时，我们说`B <: A`，`B`是`A`的子类型：

1. 所有 *`B`的实例* 是所有 *`A`的实例* 的子集，即：`isinstance(B(), A)`总是真，例如：`int`值总是`float`值；
2. 所有 *接收类型`A`作为参数的函数* 是所有 *接收类型`B`作为参数的函数* 的子集。这个表述略有些绕嘴，但它实际在说`Callable[[A], None]`是`Callable[[B], None]`这类函数的一个子集；

> 以上定义参见[PEP 483](https://peps.Python.org/pep-0483/#subtype-relationships)。

原文档中有一句话**The set of values becomes smaller in the process of subtyping, while the set of functions becomes larger.**很好的解释这个关系，即：在`subtyping`或者“子类化”的过程中，

- **类的实例集合变小了**，`Animal`的实例范围肯定大于`Dog`（`Dog`继承于`Animal`）。`Animal`可以包含`Cat`，`Dog`，`Tiger`等，但`Dog`不能包含`Cat`，实例范围缩小了；
- **函数集合变大了**，所有能够处理`Animal`的函数必然也能处理`Dog`，但是如果我们知道参数是`Dog`后，就可以给每一个接收`Animal`的函数再做一个针对`Dog`的优化函数，显然 *可以用`Dog`做参数的函数* 至少是 *用`Animal`做参数的函数* 总量的两倍，函数集合变大了；

当大家第一次接触`Subtype`这个概念时，可能会有一些疑惑（至少我是有的），记录在这里：

疑惑1： 满足第一个条件的类型对，难道不是自动满足第二个条件吗？有一个很好的反例：`List[int]`是不是`List[float]`的子类型？显然 *所有含有int的列表* 是 *所有含有float的列表* 的子集（我们可以用float列表保存一组int值），这说明第一个条件满足；我们来看第二个条件：*接收`List[float]`参数的函数* 是否是 *接收`List[int]`参数的函数* 子集，如果答案是“是”，则我们应该可以把`List[int]`作为参数传入`Callable[[List[float]], None]`，但请看下面这个例子（来自官方PEP 483的例子）：

```Python
def append_pi(lst: List[float]) -> None:
    lst += [3.14]

my_list = [1, 3, 5]  # type: List[int]

append_pi(my_list)   # 运行阶段可以把List[int]作为参数放入

my_list[-1] << 5     # ... 但是，my_list的使用者以为所有元素都是整数，所以会这么使用，3.14 << 5做位操作将会出错
```

可见问题 *接收`List[float]`参数的函数* 是否是 *接收`List[int]`参数的函数* 子集的答案是“否”。`List[int]`不是`List[float]`的子类型，满足条件1，但不满足条件2。

疑惑2：`Subtype`可以理解为**继承**吗？答案为“否”。`Subtype`是类型系统中的概念。实现类型系统的方案有两大类`Nominal Subtyping`和`Structural Subtyping`：

- `Nominal Subtyping`即通过“继承”方式来定义`Subtype`和`Supertype`
- `Structural Subtyping`即是所有动态类型语言（如`Python`和`Javascript`）中的`Duck type`，只要两个类型在结构上有共同点，你就可以将其中一个类型视作另一个类型的子类（看上去像鸭子，那它就是鸭子）

### Covariance and Contravariance

本部分内容改编自[Covariance, Contravariance, and Invariance — The Ultimate Python Guide](https://blog.daftcode.pl/covariance-contravariance-and-invariance-the-ultimate-Python-guide-8fabc0c24278)

```Python
class ParentClass:
    ...


class ChildClass(ParentClass):
    ...


def handle_parentClass(obj: ParentClass):
    pass


def handle_childClass(obj: ChildClass):
    pass
```

上面代码中，`ChildClass <: ParentClass`。那么`handle_parentClass`和`handle_childClass`是什么关系？作为函数，是否`handle_childClass <: handle_parentClass`关系成立？我们按照`<:`定义来看一下这个问题：

> 如果一个表达式能够赋值给一个变量，则说明右侧表达式结果的类型为左侧变量类型的子类型，即满足定义1

```Python
# 通过静态类型检查
parentClassObj: ParentClass = ChildClass()  

# mypy报错：error: Incompatible types in assignment (expression has type "ParentClass", variable has type "ChildClass")
childClassObj: ChildClass = ParentClass()  # 违反定义1：ParentClass()不是ChildClass实例的子集

# mypy报错：Incompatible types in assignment (expression has type "Callable[[ChildClass], Any]", variable has type "Callable[[ParentClass], None]")
f_handle_parentClass: Callable[[ParentClass], None] = handle_childClass  # 违反定义1：handle_childClass不是Callable[[ParentClass], None] 

# 通过静态类型检查
f_handle_childClass: Callable[[ChildClass], None] = handle_parentClass  
```

以上实验说明：`handle_childClass <: handle_parentClass`不成立，相反`handle_parentClass <: f_handle_childClass`成立，即`Callable[[ParentClass], None]`是`Callable[[ChildClass], None]`子类型。我们把以上这个示例用更形式化、更抽象的方式表达：

- `ParentClass`为`SuperType`，`ChildClass`为`SubType`，`Callable[[XX], None]`为`f(XX)`算子
- `SubType <: SuperType`和`f(SuperType) <: f(SubType)`成立，则`f`为 **逆变算子** `Contravariance`
- `SubType <: SuperType`和`f(SubType) <: f(SuperType)`成立，则`f`为 **协变算子** `Covariance`
- 如果以上两个关系都不成立，则`f`为`Invariance`

`f`可以是：

- `Type -> Tuple[Type, Tuple, ...]`，`Tuple`是一种协变算子，即：`Tuple[SubType1, SubType2, ...] <: Tuple[SuperType1, SuperType2, ...]`，例如：

```Python
# 通过静态类型检查，说明Tuple[SubType1, SubType2, ...] <: Tuple[SuperType1, SuperType2, ...]成立
tuple_parentClass: Tuple[ParentClass, ParentClass, float] = (ChildClass(), ChildClass(), 1)
```

- `Type -> Callable[[Type], None]`，`Callable`是逆变算子。更一般的，任何`Callable`对于作为输入参数的类型来说，是逆变算子。
- `Type -> Callable[..., Type]`，这种类型用于返回值的`Callable`是协变算子，例如：

```Python
def get_parent() -> ParentClass:
    ...


def get_child() -> ChildClass:
    ...


# mypy报错：error: Incompatible types in assignment (expression has type "Callable[[], ParentClass]", variable has type "Callable[[], ChildClass]")
f_get_child: Callable[[], ChildClass] = get_parent

# 通过类型检查，说明 Callable[..., SubType] <: Callable[..., SuperType]成立，是一种协变
f_get_parent: Callable[[], ParentClass] = get_child
```

更一般的，任何工厂类或者构造方法（只生成类实例，不改变类实例的方法）对于返回对象的类型来说，都是协变算子。

- `Type -> List[Type]`, `List`也是一种算子，同理`Iterable`，`Sequence`，`MutableSequence`这些容器类型都可以作为算子，他们是协变还是逆变？让我们已经用`mypy`来确认它们的类型

```Python
list_childClass: List[ChildClass]
list_parentClass: List[ParentClass]

# mypy报错：error: Incompatible types in assignment (expression has type "List[ParentClass]", variable has type "List[ChildClass]")
# List[SuperType] <: List[SubType]不成立，所以不是Contravariance
list_childClass = list_parentClass  # List[ChildClass] <- List[ParentClass]

# mypy报错：error: Incompatible types in assignment (expression has type "List[ChildClass]", variable has type "List[ParentClass]")
# List[SubType] <: List[SuperType]不成立，所以不是Covariance
list_parentClass = list_childClass  # List[ParentClass] <- List[ChildClass]
```

`List`即不是协变算子，也不是逆变算子，而是`Invariance`！`Tuple`和`List`都是序列类型，为什么一个是协变而另一个不是？这两个类型的区别是一个是“不可变容器”，另一个是“可变容器”。可变容器意味着可以向容器内增加或者删除元素，也可以修改其中某个元素，这将导致我们会将ParentClass类型添加到ChildClass类型的容器内，造成未来某个时刻的误用（上文中`append_pi`的例子）。

最后我们用`mypy`验证一下上面这个结论：可变容器是`Invariance`，而不可变容器是`Covariance`。

```Python
# Iterable不可变容器 是协变
iterable_childClass: Iterable[ChildClass]
iterable_parentClass: Iterable[ParentClass]
# mypy error: Incompatible types in assignment (expression has type "Iterable[ParentClass]", variable has type "Iterable[ChildClass]")
iterable_childClass = iterable_parentClass
iterable_parentClass = iterable_childClass

# Sequence不可变容器 是协变
seq_childClass: Sequence[ChildClass]
seq_parentClass: Sequence[ParentClass]
# mypy error: Incompatible types in assignment (expression has type "Sequence[ParentClass]", variable has type "Sequence[ChildClass]")
seq_childClass = seq_parentClass
seq_parentClass = seq_childClass

# MutableSequence可变容器 不是协变也不是逆变
mut_seq_childClass: MutableSequence[ChildClass]
mut_seq_parentClass: MutableSequence[ParentClass]
# mypy error: Incompatible types in assignment (expression has type "MutableSequence[ParentClass]", variable has type "MutableSequence[ChildClass]")
mut_seq_childClass = mut_seq_parentClass
# mypy error: Incompatible types in assignment (expression has type "MutableSequence[ChildClass]", variable has type "MutableSequence[ParentClass]")
mut_seq_parentClass = mut_seq_childClass
```

### Covariance and Controvariance Typing

现在我们来看一下为什么要在`typing`中引入协变和逆变。

```Python
from typing import TypeVar, Generic, Iterator


T = TypeVar("T")


class MyContainer(Generic[T]):
    def __init__(self):
        ...

    def __iter__(self) -> Iterator[T]:
        ...


def func(container: MyContainer[ParentClass]):
    for item in container:
        print(item)
```

在上面这段代码中，我们是否可以把`MyContainer[ChildClass]()`传入`func`中？代码逻辑上看，100%是没问题的。但是`mypy`却不这么认为，如果我们检查

```Python
# mypy error: Argument 1 to "func" has incompatible type "MyContainer[ChildClass]"; expected "MyContainer[ParentClass]"
func(MyContainer[ChildClass]())
```

该如何调整以上代码，使得`mypy`能验证通过呢？

`MyContainer[T]`是一个算子，`func`是另一个算子，两个算子嵌套形成新算子`Type -> Callable[[MyContainer[T]], None]`。只有当新算子`Callable[[MyContainer[ParentClass]], None] <: Callable[[MyContainer[ChildClass]], None]`成立时，即 *接收`ParentClass`为参数的函数* 是 *接收`ChildClass`为参数的函数* 的子集，即任何接收`ParentClass`的方法都可以接收`ChildClass`，才能让`func(MyContainer[ChildClass]())`通过静态类型检查。以上要求等同于要求`Type -> Callable[[MyContainer[T]], None]`是逆变算子。已知`Callable`是逆变算子，逆变算子嵌套协变算子才能产生新逆变算子，因此要求`MyContainer[T]`是一个协变算子。问题变为：如何让`MyContainer[T]`是一个协变算子？`TypeVar`提供了`covariant`设置：

```Python
T = TypeVar("T")  # 默认是invariant
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


class CoContainer(Generic[T_co]):
    def __init__(self):
        ...

    def __iter__(self) -> Iterator[T_co]:
        ...


class ContraContainer(Generic[T_contra]):
    def __init__(self):
        ...

    def __iter__(self) -> Iterator[T_contra]:
        ...
```

`Generic[T_co]`声明可以使`CoContainer[T_co]`成为和`Sequence`一样的协变算子，反之`ContraContainer[T_contra]`是逆变算子。我们测试一下：

```Python
def func_1(container: CoContainer[ParentClass]):
    for item in container:
        print(item)


def func_2(container: ContraContainer[ParentClass]):
    for item in container:
        print(item)


# 通过静态类型检查
func_1(CoContainer[ChildClass]())

# mypy error: Argument 1 to "func_2" has incompatible type "ContraContainer[ChildClass]"; expected "ContraContainer[ParentClass]"
func_2(ContraContainer[ChildClass]())
```

## ParamSpec和Concatenate

假设我们有一个装饰器如下，该如何用`typing`约束类型？

```Python
def add_logging(f):
  async def inner(*args, **kwargs):
    await log_to_database()
    return f(*args, **kwargs)
  return inner


@add_logging
def takes_int_str(x: int, y: str) -> int:
  return x + 7
```

使用前面讲过的`Callable`，应该是：

```Python
R = TypeVar("R")


def add_logging(f: Callable[..., R]) -> Callable[..., Awaitable[R]]:
  async def inner(*args: object, **kwargs: object) -> R:
    await log_to_database()
    return f(*args, **kwargs)
  return inner


@add_logging
def takes_int_str(x: int, y: str) -> int:
  return x + 7


await takes_int_str(1, "A")  # 通过静态类型检查
await takes_int_str("B", 2)  # 通过静态类型检查, 运行时报错 
```

`takes_int_str`满足`typing`：`Callable[..., R]`检查；同时`takes_int_str`变为`inner`后的参数类型为`object`，所以无论`inner(1, "A")`还是`inner("B", 2)`都满足类型检查。因此两条`takes_int_str`都会通过静态类型检查，但第二条语句会触发运行时错误。

为了解决以上问题，`Python`提供`ParamSpec`类型（见[PEP612](https://peps.Python.org/pep-0612/)）。`ParamSpec`将把参数类型的约束保留并传递给`inner`函数。`inner(x: int, y: str)`有了更明确的参数类型要求，`inner("B", 2)`语句也就无法通过静态分析。

```Python
P = ParamSpec("P")
R = TypeVar("R")


def add_logging(f: Callable[P, R]) -> Callable[P, Awaitable[R]]:
  async def inner(*args: P.args, **kwargs: P.kwargs) -> R:
    await log_to_database()
    return f(*args, **kwargs)
  return inner


@add_logging
def takes_int_str(x: int, y: str) -> int:
  return x + 7


await takes_int_str(1, "A") # Accepted
await takes_int_str("B", 2) # Correctly rejected by the type checker
```

与`ParamSpec`一起加入`typing`体系的还有`Concatenate`，可以很容易的向被修饰的函数中增加新的参数：

```Python
def with_request(f: Callable[Concatenate[Request, P], R]) -> Callable[P, R]:
  def inner(*args: P.args, **kwargs: P.kwargs) -> R:
    return f(Request(), *args, **kwargs)
  return inner


@with_request
def takes_int_str(request: Request, x: int, y: str) -> int:
  # use request
  return x + 7


takes_int_str(1, "A") # Accepted
takes_int_str("B", 2) # Correctly rejected by the type checker
```

