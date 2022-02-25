---
title: 如何算一篇好的阐述并解决问题的博文？
date: 2020-02-10T00:02:00+08:00
category: 
    - Programming
tags:
    - Android
    - Flutter
---

最近在学习Flutter开发Android应用。新手搭环境难免遇到各种坑。一般都是边搜索边尝试，最终解决问题。因此“搜索”到别人的解法至关重要。我发现网上有大量的解法，但很多时候，要么“解法”缺斤短两，关键步骤缺失；要么知其然不知所以然，瞎猫碰死耗子解决问题，让读者无法借鉴。到底如何才算一篇合格的issue resolution博文，怎样才能帮到他人？

<!--more--> 

网上技术博客大致分为几类：

1. 一阶技术分享。所谓“一阶”即阐述具体知识和技术。比如： 上一篇[nohup]({{< ref "/posts/nohup" >}})讲*linux*命令的使用，还有[在Scrapy中使用cookie]({{< ref "/posts/scrapy-cookie" >}})则分析*scrapy*框架的使用技巧。
2. 二阶技术分享。所谓“二阶”即在“一阶”具体技术之上发挥创造。一般讲设计/模式/架构，讲思想，也可以讲如何把技术用到一个有趣的场景。比如：[Streaming Pipeline in Python 1]({{< ref "/posts/streaming-pipeline-in-python-1" >}}) 这篇讲的并不是*python*怎么用，甚至不是讲*expression generator*是什么，而是试图讲如何在*python*中实现一个流水线模式；还有我最喜欢的博主**Eric Lippert**的文章[An interesting list structure, part 1](https://ericlippert.com/2019/01/22/an-interesting-list-structure/)用c#来讲有趣的数据结构。
3. 三阶分享。到了三阶，与其说是技术分享，不如说是形而上的思维交流，比如：技术管理，技术商业化，技术人生，软技能，以及职业发展等等。例如：**Joe**的文章[Getting Things Done When You’re Only a Grunt](https://www.joelonsoftware.com/2001/12/25/getting-things-done-when-youre-only-a-grunt/)咋凭一己之力在团队里搞EE，讲的软技能（当然不排除大神带货之嫌，毕竟自家工具恰好解决他文章里说的那些问题）；再举Eric的文章[Work and success](https://ericlippert.com/2019/12/30/work-and-success/)成功的技术人生到底需不需要996状态工作（文章原话“working long hours”）？
4. 最后还有一类，和一阶分享类似，但不是介绍某个知识，技术和工具使用。而是在研发过程中，遇到了一些令人困惑的问题，经过长时间的搜索和尝试，最终解决。写成博客作为记录，同时分享给其他有可能遇到同样问题的伙伴。这种类型的分享和github的issues很像。

第2和3类博客有一定门槛，能写也愿意花精力去写的人少。最多的是1和4。程序员的日常就是和各种千奇百怪的“坑”做“斗争”，故第4类博客格外多，但质量良莠不齐，原因想必有几条：

1. 大部分博主仅是做个记录给自己看，无所谓别人能不能看懂。
2. “不识庐山真面目，只缘身在此山中”，很多博主虽然想让别人看懂，但是博主和读者理解的角度不同。有时候博主觉得已经写得很清楚了，但是读者看来缺少了一些关键细节，依旧不能理解。
3. 这类文章门槛低，基本属于中小学说明文范畴。大部分水平有限的同仁热衷产出此类文章，文笔和逻辑欠佳，难以保证质量。
4. 装逼。觉得写太细不是“专家”所为，专家应该只给思想定方向。这些简单的执行步骤，太low，写起来也麻烦。大家都自行搜索解决就好了。

这篇文章想借flutter环境搭建中遇到的问题，讲讲怎样才算一篇合格的issue resolution博客。

在Android Studio上安装flutter和dart开发应用。按[官方文档](https://flutter.dev/docs/get-started/install/linux)安装完毕后运行

```bash
$ flutter doctor

[-] Android toolchain - develop for Android devices
✗ Android license status unknown.
• Try re-installing or updating your Android SDK,
    visit https://flutter.dev/setup/#android-setup for detailed instructions.
```

出现了一个**Android license status unknown.**的错误。搜索后，找到一篇[关于升级Android SDK的文章](https://blog.csdn.net/weixin_41319450/article/details/90264627)，按文章所说许可证未知的情况下，应该升级sdkmanager，故执行

```bash
$ /home/Android/Sdk/tools/bin/sdkmanager --update

Exception in thread "main" java.lang.NoClassDefFoundError: javax/xml/bind/annotation/XmlSchema
    at com.android.repository.api.SchemaModule$SchemaModuleVersion.<init>(SchemaModule.java:156)
    at com.android.repository.api.SchemaModule.<init>(SchemaModule.java:75)
    at com.android.sdklib.repository.AndroidSdkHandler.<clinit>(AndroidSdkHandler.java:81)
    at com.android.sdklib.tool.sdkmanager.SdkManagerCli.main(SdkManagerCli.java:73)
    at com.android.sdklib.tool.sdkmanager.SdkManagerCli.main(SdkManagerCli.java:48)
Caused by: java.lang.ClassNotFoundException: javax.xml.bind.annotation.XmlSchema
    at java.base/jdk.internal.loader.BuiltinClassLoader.loadClass(BuiltinClassLoader.java:581)
    at java.base/jdk.internal.loader.ClassLoaders$AppClassLoader.loadClass(ClassLoaders.java:178)
    at java.base/java.lang.ClassLoader.loadClass(ClassLoader.java:521)
    ... 5 more
```

执行失败。用关键词*sdkmanager --update java.lang.NoClassDefFoundError: javax/xml/bind/annotation/XmlSchema*再一通搜索，发现很多讨论这个问题的博文，比如：

- [关于flutter sdk安装时候的xxxxx\SDK\tools\bin\sdkmanager --update快捷解法](https://blog.csdn.net/u011339184/article/details/103787959)和我遇到的问题细节略有不同（报错不一致），但基本可以辅助我得出一个结论：问题是*sdkmanager依赖的*java环境导致的。回头来看这篇文章本身，就属于“茶壶里煮饺子，有嘴倒不出”类型。博主应该是解决了自己的问题，但写出的文章囫囵吞枣，让其他新手无从下手。
- [运行sdkmanager --update报错java.lang.NoClassDefFoundError: javax/xml/bind/annotation/XmlSchema](https://blog.csdn.net/wwq614003946wwq/article/details/90673338)也说出了要点。可难道让大家重新装jdk吗？
- [sdkmanager --list 报错](https://www.jianshu.com/p/8f5238575601)的博主知其然不知其所以然。机器上想必已经装了java.se.ee啥的，所以加上一段配置项就work了，但为什么work估计还是一脸懵逼。
- [JDK11 使用 sdkmanager --update 报错解决](https://blog.csdn.net/u011339184/article/details/103787959) 是所有中文文章中，最靠谱的一篇：

  - 明确说明原因：JDK版本问题。环境中装了JDK 11，有些jar包已经剥离出去了。这些jar包在JDK 8中是存在的。博主完全理解了问题的本质原因，并清晰的阐述；
  - 降级到JDK 8太愚蠢。博主急人之所急，知道重装到JDK 8对于大部分人来说不是一个好的选择。同时给出了新方案：将缺少的几个jar包下载下来，并把这些jar包的位置添加到CLASSPATH这个环境变量中。这样sdkmanager就能使用这几个依赖包了。注意到博主明确给出了哪些jar包是缺失的（很赞）；
  - 遗憾的是博主可能假设所有人都是java高手，知道该去哪里找这些jar包，故没有给出jar包下载路径。全文离“完美”只差一步。

- 最后[Stack Overflow的答案](https://stackoverflow.com/questions/53076422/getting-android-sdkmanager-to-run-with-java-11)给出了正确的方案，并给出了下载地址。而且值得注意的是，国外的开发者喜欢用脚本和代码说话，甚至连“建子目录以及-O参数输出到子目录”这些细节都不放过。细到极致，跟着做不会出错。唯一的瑕疵：下载地址用到了 `http://central.maven.org`。http协议貌似已经不可访问，需要全部替换为 `https://repo.maven.apache.org`。

梳理一下终极解决方案。在Ubuntu 18.04 + Android Studio 3.5.1 + OpenJDK 11的组合上验证通过。

```bash
$ cd /home/Android/tools/bin

$ mkdir jaxb_lib

$ wget https://repo.maven.apache.org/maven2/javax/activation/activation/1.1.1/activation-1.1.1.jar -O jaxb_lib/activation.jar

$ wget https://repo.maven.apache.org/maven2/javax/xml/jaxb-impl/2.1/jaxb-impl-2.1.jar -O jaxb_lib/jaxb-impl.jar

$ wget https://repo.maven.apache.org/maven2/org/glassfish/jaxb/jaxb-xjc/2.3.2/jaxb-xjc-2.3.2.jar -O jaxb_lib/jaxb-xjc.jar

$ wget https://repo.maven.apache.org/maven2/org/glassfish/jaxb/jaxb-core/2.3.0.1/jaxb-core-2.3.0.1.jar -O jaxb_lib/jaxb-core.jar

$ wget hhttps://repo.maven.apache.org/maven2/org/glassfish/jaxb/jaxb-jxc/2.3.2/jaxb-jxc-2.3.2.jar -O jaxb_lib/jaxb-jxc.jar

$ wget https://repo.maven.apache.org/maven2/javax/xml/bind/jaxb-api/2.3.1/jaxb-api-2.3.1.jar -O jaxb_lib/jaxb-api.jar

$ vim sdkmanager
```

最后一步中，向脚本中增加几个jar路径到CLASSPATH环境变量

```bash
CLASSPATH=$CLASSPATH:$APP_HOME/bin/jaxb_lib/activation.jar:$APP_HOME/bin/jaxb_lib/jaxb-impl.jar:$APP_HOME/bin/jaxb_lib/jaxb-xjc.jar:$APP_HOME/bin/jaxb_lib/jaxb-core.jar:$APP_HOME/bin/jaxb_lib/jaxb-jxc.jar:$APP_HOME/bin/jaxb_lib/jaxb-api.jar
```

再试一下

```bash
$ /home/Android/Sdk/tools/bin/sdkmanager --update

WARNING: An illegal reflective access operation has occurred
WARNING: Illegal reflective access by com.sun.xml.bind.v2.runtime.reflect.opt.Injector$1 (file:/home/hao/Android/Sdk/tools/bin/jaxb_lib/jaxb-impl.jar) to method java.lang.ClassLoader.defineClass(java.lang.String,byte[],int,int)
WARNING: Please consider reporting this to the maintainers of com.sun.xml.bind.v2.runtime.reflect.opt.Injector$1
WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
WARNING: All illegal access operations will be denied in a future release
Warning: File /home/hao/.android/repositories.cfg could not be loaded.          
[=======================================] 100% Computing updates...             
------------------------------------------------------------    

$ flutter doctor

Doctor summary (to see all details, run flutter doctor -v):
[✓] Flutter (Channel beta, v1.14.6, on Linux, locale en_US.UTF-8)
[✓] Android toolchain - develop for Android devices (Android SDK version 29.0.2)
[✓] Android Studio (version 3.5)
[!] IntelliJ IDEA Community Edition (version 2019.2)
    ✗ Flutter plugin not installed; this adds Flutter specific functionality.
    ✗ Dart plugin not installed; this adds Dart specific functionality.
[!] VS Code (version 1.41.1)
    ✗ Flutter extension not installed; install from
    https://marketplace.visualstudio.com/items?itemName=Dart-Code.flutter
[✓] Connected device (1 available)

! Doctor found issues in 2 categories.
```

和Android Studio相关的flutter配置全部正常了！
