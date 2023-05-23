# ChatGPT coding Rubik's Cube

## MacOS

```
python3 --version 
// Python 3.9.13

pip --version
// pip 22.1.1 from /usr/local/lib/python3.9/site-packages/pip (python 3.9)

python3 -m pip install --upgrade pip
// 升级pip 到最近版

pip3 install pipenv  
// 安装 pipenv

pipenv run python src/rubik_cube.py
// 调试运行

cd tests & pipenv run python xxx
// 测试
```

## Windows

```
python --version 
// Python 3.6.8

pip --version
// pip 21.3.1 from c:\users\sun_ao\appdata\local\programs\python\python36\lib\site-packages\pip (python 3.6)

python -m pip install --upgrade pip
// 升级pip 到最近版

pip install pipenv  
// 安装 pipenv

pipenv run python src/rubik_cube.py
// 调试运行

cd tests & pipenv run python xxx
// 测试
```

## 接口服务

```
pipenv run python src/app.py

// 接口请求示例 anno-rubik/tests/http/process_images.http
```
