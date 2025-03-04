# 使用官方Python运行时作为父镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /apps

# 将当前目录内容复制到容器内的/app路径下
COPY . /apps

# 安装任何需要的包
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 确保应用可以访问外部世界
# （这一步可能不是必需的，取决于您的网络配置和应用需求）
# RUN apt-get update && apt-get install -y \
#     libpq-dev gcc && \
#     rm -rf /var/lib/apt/lists/*

# 暴露必要的端口（如果您的应用监听特定端口的话）
EXPOSE 5000

# 设置执行命令以运行应用
CMD ["python", "app.py"]