from time import sleep
from typing import Iterable, Iterator


class MyIterator(Iterator[int]):
    def __init__(self, n: int) -> None:
        super().__init__()
        self._i = n

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        if self._i == 0:
            raise StopIteration()
        self._i -= 1
        return self._i


class MyIterable(Iterable[int]):
    def __init__(self, n: int) -> None:
        super().__init__()
        self._n = n

    def __iter__(self) -> Iterator[int]:
        return MyIterator(self._n)


# my_iterable = [3, 2, 1]

# my_iter_1 = iter(my_iterable)
# print(next(my_iter_1))

# my_iter_2 = iter(my_iterable)
# print(next(my_iter_2))

# my_iter_3 = iter(my_iter_2)
# print(next(my_iter_3))


# def generator():
#     yield 3
#     yield 2
#     yield 1


# my_iter_4 = generator()
# print(my_iter_4)
# print(next(my_iter_4))

# my_iter_5 = generator()
# print(next(my_iter_5))

# my_iter_6 = iter(my_iter_5)
# print(next(my_iter_6))


# def full_gen(a):
#     b = yield a
#     c = yield a + b
#     yield a + b + c


# g = full_gen(1)
# print(next(g))  # 激活迭代器到yield a这句，得到返回值1
# print(g.send(2))   # 传递b = 2，得到yield a + b = 1 + 2 = 3
# print(g.send(3))   # 传递c = 3，得到yield c + a + b = 1 + 2 + 3 = 6
# print(g.send(4))   # 没有更多的yield语句，return触发StopIteration



def autostart(func):
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        g.send(None)
        return g
    return start


@autostart
def full_gen():
    try:
        a = yield
        print(a)
        b = yield
        print(b)
    except ValueError as e:
        print(str(e))
    except GeneratorExit:
        print("close")


# g_1 = full_gen()
# g_1.send(1)
# g_1.throw(ValueError(2))

# g_2 = full_gen()
# g_2.send(2)
# g_2.close()

def produce():
    yield 3
    yield 2
    raise ValueError(1)


def consume(n):
    print(n)


# producer = produce()
# for i in producer:
#     consume(i)


# def consume():
#     while True:
#         n = yield
#         print(n)


# consumer = consume()
# consumer.send(3)
# consumer.send(2)
# consumer.throw(ValueError(1))  # or consumer.close()

import asyncio


async def produce():  # 这里用了[PEP 525]的Async Generator
    yield "Hello"
    await asyncio.sleep(1)
    yield "World"


async def consume():
    async for r in produce():  # 这里用了[PEP 525]的async for
        print(r)


f_1 = consume()
print(f_1)
asyncio.run(f_1)


# def produce():
#     sleep(1)
#     yield "Hello"


# def consume():
#     while True:
#         n = yield
#         print(n)


# def schedule():
#     p_1 = produce()
#     print(p_1)
#     c_1 = consume()
#     print(c_1)
#     c_1.send(None)

#     while True:
#         try:
#             n = p_1.send(None)
#         except StopIteration:
#             c_1.close()
#             break
#         else:
#             c_1.send(n)


# schedule()

    

