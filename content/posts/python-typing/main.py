# def func(a, b):
#     return a + b


# print(func(1, 2))  # 输出3
# print(func([1, 2], [3]))  # 输出 [1, 2, 3]
# print(func("Hello ", "World"))  # 输出 Hello World


# from typing import TypeVar

# T = TypeVar('T') 

# def func(a: T, b: T) -> T: 
#     return a + b


# r: str = "r"
# r = func(1, 2)  # 检查无法通过
# r = func(1, "a")  # 检查无法通过


# from typing import Sequence, TypeVar, List

# T = TypeVar("T", bound=Sequence)
# S = TypeVar("S", int, list)

# def func(a: T, b: S) -> None:
#     ...

# func(1, 1)
# func([1, 2, 3], 1.0)
# func([1, 2, 3], [1, 2])


# def func(a: int, b: str) -> float:
#     """_summary_

#     Args:
#         a (int): _description_
#         b (str): _description_

#     Returns:
#         float: _description_
#     """
#     return 1.0


# from __future__ import annotations
# from collections.abc import Sequence


# def double(input_: int | Sequence[int]) -> int | list[int]:
#     if isinstance(input_, Sequence):
#         return [i * 2 for i in input_]
#     return input_ * 2


# def print_int(a: int):
#     print(a)


# print_int(double(1))


# from __future__ import annotations

# from collections.abc import Sequence
# from typing import overload


# @overload
# def double(input_: int) -> int:
#     ...


# @overload
# def double(input_: Sequence[int]) -> list[int]:
#     ...


# def double(input_: int | Sequence[int]) -> int | list[int]:
#     if isinstance(input_, Sequence):
#         return [i * 2 for i in input_]
#     return input_ * 2


# def print_int(a: int):
#     print(a)


# print_int(double(1))


# from typing import TypeVar, Generic,  List


# T= TypeVar("T")


# class SingleLinkedList(Generic[T]):
#     def __init__(self, value: T, next: "SingleLinkedList") -> None:
#         self.value = value
#         self.next = next

#     def __repr__(self) -> str:
#         return f"{self.value} -> {self.next}"


# def build_linked_list_from_int_list(data: List[int]) -> SingleLinkedList[int]:
#     if not data:
#         return None
#     return SingleLinkedList(data[0], build_linked_list_from_int_list(data[1:]))


# print(build_linked_list_from_int_list([1, 2]))


class ParentClass:
    def foo(self):
        pass


class ChildClass(ParentClass):
    def bar(self):
        pass


def handle_parentClass(obj: ParentClass):
    pass


def handle_childClass(obj: ChildClass):
    pass


from typing import Callable, Iterator, Tuple, List, Iterable, Sequence, MutableSequence, TypeVar, Generic
# parentClassObj: ParentClass = ChildClass()
# childClassObj: ChildClass = ParentClass()
# f_handle_parentClass: Callable[[ParentClass], None] = handle_childClass
# f_handle_childClass: Callable[[ChildClass], None] = handle_parentClass

# tuple_parentClass: Tuple[ParentClass, ParentClass, float] = (ChildClass(), ChildClass(), 1)


# def get_parent() -> ParentClass:
#     ...


# def get_child() -> ChildClass:
#     ...


# f_get_child: Callable[[], ChildClass] = get_parent
# f_get_parent: Callable[[], ParentClass] = get_child


# list_childClass: List[ChildClass]
# list_parentClass: List[ParentClass]

# # mypy报错：
# list_childClass = list_parentClass  # List[ChildClass] <- List[ParentClass]

# # mypy报错：error: List item 0 has incompatible type "ParentClass"; expected "ChildClass"
# list_parentClass = list_childClass  # List[ParentClass] <- List[ChildClass]

# # Iterable不可变容器 是协变
# iterable_childClass: Iterable[ChildClass]
# iterable_parentClass: Iterable[ParentClass]
# # mypy error: Incompatible types in assignment (expression has type "Iterable[ParentClass]", variable has type "Iterable[ChildClass]")
# iterable_childClass = iterable_parentClass
# iterable_parentClass = iterable_childClass

# # Sequence不可变容器 是协变
# seq_childClass: Sequence[ChildClass]
# seq_parentClass: Sequence[ParentClass]
# # mypy error: Incompatible types in assignment (expression has type "Sequence[ParentClass]", variable has type "Sequence[ChildClass]")
# seq_childClass = seq_parentClass
# seq_parentClass = seq_childClass

# # MutableSequence可变容器 不是协变也不是逆变
# mut_seq_childClass: MutableSequence[ChildClass]
# mut_seq_parentClass: MutableSequence[ParentClass]
# # mypy error: Incompatible types in assignment (expression has type "MutableSequence[ParentClass]", variable has type "MutableSequence[ChildClass]")
# mut_seq_childClass = mut_seq_parentClass
# # mypy error: Incompatible types in assignment (expression has type "MutableSequence[ChildClass]", variable has type "MutableSequence[ParentClass]")
# mut_seq_parentClass = mut_seq_childClass

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


def func_1(container: CoContainer[ParentClass]):
    for item in container:
        print(item)


def func_2(container: ContraContainer[ParentClass]):
    for item in container:
        print(item)


func_1(CoContainer[ChildClass]())
func_2(ContraContainer[ChildClass]())
