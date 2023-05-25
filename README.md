# ChatGPT coding Rubik's Cube

## MacOS

```
python3 --version 
// Python 3.9.13

pip3 --version
// pip 23.1.2 from /usr/local/lib/python3.9/site-packages/pip (python 3.9)

python3 -m pip install --upgrade pip
// 升级pip 到最近版

pip3 install pipenv  
// 安装 pipenv

pipenv install   
// 安装依赖

cd tests 
// 测试

pipenv run python cube.py
// 调试运行
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

pipenv install   
// 安装依赖

cd tests 
// 测试

pipenv run python cube.py
// 调试运行
```

## 接口服务

切换到根目录

```
pipenv run python src/app.py

// 接口请求示例 anno-rubik/http/process_images.http
```

## Docker  

`问题`: ImportError: libGL.so.1: cannot open shared object file: No such file or directory  
`原因`：python镜像没有GUI环境（ cv2.imshow() 依赖）  
`解决`：apt-get update && apt-get install -y libgl1-mesa-dev  或者  opencv-python → opencv-python-headless   

```
docker build -t anno-rubik:latest .
docker run -d -p 5000:5000 anno-rubik:latest
```
