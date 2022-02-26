---
title: 在循环中使用lambda
date: 2016-01-02T20:45:29+08:00
category:
    - Programming
tags:
    - Python
---

谈到函数式编程，必然会提到lambda。lambda使得高阶函数运算用起来得心应手。而谈到lambda就要提到闭包。闭包将lambda和它运行时依赖“环境”连接在一起。用一个简单python代码来描述lambda和闭包：

<!--more--> 

```python
threshold = 10000

is_high_salary = lambda x: x < threshold

for salary in filter(is_high_salary, [90, 10000, 10001, 1002]):
    print salary
```

对python和lambda稍有了解的朋友都知道上面的程序将输出90和1002。虽然threshold这个变量并没有显示的传入lambda表达式，但是它已经悄然由编译器通过闭包与is_high_salary绑在一起。所以当执行filter时，is_high_salary能够正确得到threshold的值10000。

问题来了，threshold这个值是什么时候和is_high_salary这个表达式绑定起来的呢？在声明is_high_salary时？验证一下：

```python
threshold = 10000

is_high_salary = lambda x: x < threshold

threshold = 10001

for salary in filter(is_high_salary, [90, 10000, 10001, 1002]):
    print salary
```

结果是90, 10000, 1002。显然，threshold是在执行is_high_salary时完成的绑定。有了基本概念后，再出一个有些迷惑性的题目：

```python
steps = [lambda x: x < 5, lambda x: x > 1]

nums = [0, 1, 2, 3, 4, 5, 6]

for step in steps:
    nums = (num for num in nums if step(num))

for num in nums:
    print num
```

这里除了lambda表达式列表，还有一个generator expression（本质上也是一种lambda表达式）。在上面的代码中generator expression使用闭包绑定了循环变量step，而step本身又是一个lambda表达式。结果会是什么？答案是2, 3, 4, 5, 6。并不是想象中的2, 3, 4 (大于1且小于5)。

首先，generator expression的执行是在倒数第二行遍历nums时才触发的。这意味着闭包绑定也是在那时完成的。我们在来看一下steps循环中到底绑定了什么，绑定了几次：

- 因为steps里面有两个元素，两个元素依次赋给step变量循环两次
- 循环执行两次，有两个generator expression生成，两个的闭包都绑定到step上
- 当nums循环开始执行时，step值为lambda x: x > 1，故两个generator expression都绑定到这个lambda表达式上

自然只筛选出了大于1的元素。一种正确的实现（还有好多种其他方案）：

```python
def wrap(f):
    return (num for num in nums if f(num))

steps = [lambda x: x < 5, lambda x: x > 1]

nums = [0, 1, 2, 3, 4, 5, 6]

for step in steps:
    nums = wrap(step)

for num in nums:
    print num
```

将generator expression绑定到一个局部变量上，这里我们通过构造一个包装函数，完成了局部变量创建。这样每个generator expression都绑定到了唯一的一个变量上。

