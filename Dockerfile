# 基于 Python 官方镜像创建一个新的镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 复制 Pipfile 和 Pipfile.lock 到容器中
COPY Pipfile Pipfile.lock /app/

# 安装依赖包（方案一）
RUN apt-get update && \
    apt-get install -y libgl1-mesa-dev && \
    pip install pipenv && \
    pipenv install --system --deploy

# 安装依赖包（方案二）
# RUN pip install pipenv && \
#     pipenv install --system --deploy && \
#     pipenv uninstall opencv-python && \
#     pipenv install opencv-python-headless

# 复制整个项目到容器中
COPY . /app

# 暴露应用程序的端口（如果需要的话）
EXPOSE 5000

# 运行应用程序（方案一）
CMD ["python", "src/app.py"]

# 运行应用程序（方案二）
# CMD ["pipenv", "run", "python", "src/app.py"]
