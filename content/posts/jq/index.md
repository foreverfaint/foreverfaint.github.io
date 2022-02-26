---
title: jq
date: 2019-10-10T00:00:00+08:00 
category:
    - DevOps
tags: 
    - Linux
---

JSON格式的字符串是Web API最常见的返回格式。在使用API时，我们经常使用`curl`或者`wget`快速方便的调试API。如果API返回的是JSON，输出到控制台里会像下面这样。没有格式，很难阅读：

<!--more--> 

```bash-session
$ curl https://localhost/v1/stores/00138 -H Authorization:MyAuthCode
{"data":{"results":[{"create_datetime":"2019-09-27T11:34:26","delete_datetime":null,"id":1,"is_delete":false,"name":"00138","setting":{"update_datetime":"2019-09-27T11:34:38"},"store_id":"00138","update_datetime":"2019-09-27T11:34:26"}],"total":1}}
```

`jq`是一款Linux工具，可以将JSON字符串格式化后输出到控制台上。在Ubuntu上安装十分简单`apt-get install jq`。安装成功后，再次使用`curl`测试API，同时用管道连接到`jq`：

```bash-session
$ curl https://localhost/v1/stores/00138 -H Authorization:MyAuthCode | jq .
{
    "data": {
        "results": [
        {
            "create_datetime": "2019-09-27T11:34:26",
            "delete_datetime": null,
            "id": 1,
            "is_delete": false,
            "name": "00138",
            "setting": {
                "update_datetime": "2019-09-27T11:34:38"
            },
            "store_id": "00138",
            "update_datetime": "2019-09-27T11:34:26"
        }
        ],
        "total": 1
    }
}
```

是不是世界立刻清爽了？`jq`的强大远不止于此。如果只想查看results数组内的内容：

```bash-session
$ curl https://localhost/v1/stores/00138 -H Authorization:MyAuthCode | jq -r 'data.results'
[
    {
        "create_datetime": "2019-09-27T11:34:26",
        "delete_datetime": null,
        "id": 1,
        "is_delete": false,
        "name": "00138",
        "setting": {
            "update_datetime": "2019-09-27T11:34:38"
        },
        "store_id": "00138",
        "update_datetime": "2019-09-27T11:34:26"
    }
]
```

results是个数组，如果只想查看数组中第1个元素：

```bash-session
$ curl https://localhost/v1/stores/00138 -H Authorization:MyAuthCode | jq -r 'data.results[0]'
{
    "create_datetime": "2019-09-27T11:34:26",
    "delete_datetime": null,
    "id": 1,
    "is_delete": false,
    "name": "00138",
    "setting": {
        "update_datetime": "2019-09-27T11:34:38"
    },
    "store_id": "00138",
    "update_datetime": "2019-09-27T11:34:26"
}
```

请注意上面的输出不再有**[ ]**。如果只想输出数组中每个元素的id和name属性：

```bash-session
$ curl https://localhost/v1/stores/00138 -H Authorization:MyAuthCode | jq -r 'data.results[]|.id,.name'
1
00138
```

将每个元素的id和name按顺序依次输出。每个属性单占一行。由于实例中results数组只有一个元素，故只输出了两行，分别对应id（1）和name（00138）。如果想将数组中每个元素转换为另一个字典输出，比如将id和name的属性值交换位置：

```bash-session
$ curl https://localhost/v1/stores/00138 -H Authorization:MyAuthCode | jq -r 'data.results[]|{id:.name,name:.id}'
{
    "id": "00138",
    "name": 1
}
```

有了`jq`这款利器，我们开发的工具输出结果到控制台时，也可以用JSON格式。搭配`jq`可以漂亮展示结果，方便观察和调试。再无需操心如何用print到控制台才能看起来方便些。不过务必注意，工具输出时要格式化为 **JSON字符串** ，而不是像下面这样：

```python
def foo():
    json_obj = dict(a=1, b=1)
    print(json_obj)
```

运行上述代码：

```bash-session
$ python foo.py
{'a': 1, 'b': 2}

$ python foo.py | jq .
parse error: Invalid numeric literal at line 1, column 5
```

因为`{'a': 1, 'b': 2}`不是一个合法的Json字符串。正确做法：

```python
def foo():
    json_obj = dict(a=1, b=1)
    print(json.dumps(json_obj))
```

再次运行：

```bash-session
$ python foo.py
{"a": 1, "b": 2}

$ python foo.py | jq .
{
    "a": 1,
    "b": 2
}
```


此外，如果有从网页上拷贝下来的大JSON想用jq格式化一下，有两个方法：

- 保存在一个临时文件json.txt，然后`jq . json.txt`。
- 也可以直接在控制台上输入`echo '{"a": 1, "b": 2}' | jq .`
