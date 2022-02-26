---
title: sealed keyword in Kotlin
date: 2020-03-22T00:00:00+08:00 
category: 
    - Programming
tags: 
    - Android
    - Kotlin
---

`sealed`关键字在`C#`中用来修饰类。`sealed`这个词“人如其名”，显而易见的表明：它使得被它修饰的类或者方法被封闭，不允许被继承(sealed class)，或者被重写（sealed method）。Kotlin中也有`sealed`关键字，但它的含义与C#中的含义有巨大的不同。

<!--more--> 

在很多语言中都有`sealed`关键字。比如在`C#`中

```csharp
sealed class A {
    public void foo() {
    }
}

class B: A {
}
```

上面这个`C#`类被用`sealed`修饰，因此如果我们试图声明一个新类`class B`继承自`class A`就会编译失败。当然在`C#`中也可以将`sealed`应用到方法上，从而禁止任何子类重写该方法。详情参见[C# reference](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/sealed)。

事实上，`java`也有类似功能的关键字`final`，同样可以实现禁止一个类被继承。`Kotlin`是一款JVM，也有`sealed`关键词。但该关键词的含义却与`C#`中的含义相差巨大，这里做一些简要介绍。

## enum class

`Kotlin`中有很多不同的类，其中一种类叫`enum class`。与其他语言中的枚举类型是一个意思，但是是以类的形式出现，也多了一些类的特性。

```kotlin
enum class Fruit {
    Apple, Peach, Unknown
}

fun main() {
    val fruit = Fruit.Apple
    print("$fruit")
}
```

通常用到`enum`我们都希望语言最好能支持：

1. 给`enum`的字面值赋予数字值
2. 给`enum`增加一些好用的方法

`Kotlin`作为现代化的语言自然会给予支持：

```kotlin
enum class Fruit(val num: Int, val unitWeight: Float) {
    Apple(1, 1.0f) {
        override fun eat() = Peach
    },

    Peach(2, 2.0f) {
        override fun eat() = Unknown
    },

    Unknown(3, 3.0f) {
        override fun eat() = Apple
    };

    abstract fun eat(): Fruit
}

fun main() {
    val fruit = Fruit.Apple
    println("$fruit")
    println("${fruit.eat()}")
    println("${fruit.num}")
    println("${fruit.unitWeight}")
}
```

以上示例很好的描述了`Kotlin`中`enum`的各种灵活语法。`enum`的实例`Apple`,`Peach`,`Unknown`都只能有一个。如果你希望多几个`Apple`，`enum class`是不支持的。比如我可能需要`num`是2代表两个苹果；我甚至需要`Peach`的`num`也是2，表示两个桃子，然而这些都不是`enum class`能做，甚至该做的。这时候就轮到`sealed class`出场了。

## sealed class

在`Kotlin`语言中，`sealed class`依旧可以有自己的子类。但是要求子类必须和`sealed class`在同一个kt文件内。和`C#`中的`sealed class`做个对比：

1.`Kotlin`中的`sealed class`是个抽象类，不能实例化。`C#`中的`sealed class`恰好相反，必须是一个可以实例化的类。
2.`Kotlin`中的`sealed class`可以被继承，但仅限在同一个文件内的子类继承。`C#`中的`sealed class`无论在哪个文件里也不能被继承。

这是我不喜欢`Kotlin`的原因之一。`sealed`到底是`sealed`啥？ 既不是包级别的`sealed`，也不是类级别的`sealed`，　搞出一个不伦不类的 *文件*`sealed`。按[官方说法](https://kotlinlang.org/docs/reference/sealed-classes.html) 这是一个`enum class`的增强，即一个支持内部状态的`enum`类型。`enum`真的需要增强吗？特别是 **用增加一个新语法的方式** 来增强？有性价比吗？Ugly不？

暂且接受这一切。既然`sealed class`是`enum class`的一种增强，那我们就先用`sealed class`实现一下同样的Fruit继承体系。

```kotlin
sealed class Fruit(val num: Int, val unitWeight: Float) {
    object Apple: Fruit(1, 1.0f) {
        override fun eat(): Fruit {
            return Fruit.Peach
        }
    }

    object Peach: Fruit(2, 2.0f) {
        override fun eat(): Fruit {
            return Fruit.Unknown
        }
    }

    object Unknown: Fruit(3, 3.0f) {
        override fun eat(): Fruit {
            return Fruit.Apple
        }
    }

    abstract fun eat(): Fruit
}

fun main() {
    val fruit = Fruit.Apple
    println("$fruit")
    println("${fruit.eat()}")
    println("${fruit.num}")
    println("${fruit.unitWeight}")
    println("${Fruit.Apple.eat() is Fruit.Peach}")
}
```

`fruit`和`fruit.eat()`输出的都是`object`,故实际打印结果类似**xyz.dev66.Fruit$Apple@3a03464**。`sealed class`这么用就失去它的意义了。它与`enum class`最大的不同就是它可以实例化多个“水果”：

```kotlin
sealed class Fruit(val num: Int, val unitWeight: Float) {
    class Apple(num: Int, unitWeight: Float): Fruit(num, unitWeight) {
        override fun eat(): Fruit {
            return Fruit.Peach(2, 2.0f)
        }
    }

    class Peach(num: Int, unitWeight: Float): Fruit(num, unitWeight) {
        override fun eat(): Fruit {
            return Fruit.Unknown(3, 3.0f)
        }
    }

    class Unknown(num: Int, unitWeight: Float): Fruit(num, unitWeight) {
        override fun eat(): Fruit {
            return Fruit.Apple(1, 1.0f)
        }
    }

    abstract fun eat(): Fruit
}

fun main() {
    val fruit = Fruit.Apple(2, 1.0f)
    println("$fruit")
    println("${fruit.eat()}")
    println("${fruit.num}")
    println("${fruit.unitWeight}")
    println("${Fruit.Apple(1, 1.0f) == Fruit.Unknown(3, 3.0f).eat()}")
}
```

将`object`改为`class`，就能初始化多个苹果和桃子了。特别最后一个`println`提醒我们尽管`Fruit.Unknown(3, 3.0f).eat()`返回了`Fruit.Apple(1, 1.0f)`，但是它和`==`左侧的苹果实例并不是一个。

`sealed`限制了只有`Fruit`所在文件的维护者可以增加水果的类型。任何其他没有该文件修改权限的开发者，无法创建更多的水果。但是其他开发者可以在其他文件中创建苹果的子类，或者桃子的子类。所以到底`sealed`的意义在哪里？

官方提供了一个`sealed class`使用的方法，与`when`结合，避免使用`else`，从而使代码更健壮。我理解因为不使用`else`，当增加了新的`sealed class`子类之后，编译器会警告开发者补全`when`的分支。

```kotlin
fun printlnFruit(fruit: Fruit) {
    when (fruit) {
        is Fruit.Apple -> println("apple ${fruit.num}")
        is Fruit.Peach -> println("peach ${fruit.num}")
        is Fruit.Unknown -> println("unknown ${fruit.num}")
    }
}
```

用一句话解释`sealed class`，一个支持多实例（有内部状态）的`enum class`。
