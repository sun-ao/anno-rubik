# 使用 Python 3.11 slim 镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 配置 Debian 使用阿里云镜像源
RUN sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|http://security.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources

# 设置工作目录
WORKDIR /app

# 先安装系统依赖（利用 Docker 缓存）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1-mesa-dev \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt ./

# 安装 Python 依赖
RUN pip install --index-url https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 复制应用代码
COPY . /app

# 暴露端口
EXPOSE 5000

# 运行应用
CMD ["python", "run.py"]
