# Myshell
A terminal running on a web page

myshell文件夹被打包成一个模块，运行时直接python -m myshell

文件目录如下
```
├── myshell
    ├── app.py
    ├── __init__.py
    ├── __main__.py
    ├── static
    │   ├── shell.css
    │   └── shell.js
    └── templates
        └── index.html
```

前端代码在static、templates文件夹下，主要是网页模板和布局，以及与后端通信的一些逻辑
服务端代码在app.py文件中，主要是启动服务，使用pty模拟终端，并与前端通信（接收输入的命令，传递相应的输出信息）