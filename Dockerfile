FROM python:3.11-slim
WORKDIR /app

# 升级 pip 并安装运行依赖
RUN python -m pip install --upgrade pip
RUN pip install "mcp[cli]>=1.13.1"

# 复制项目文件并设置启动命令
COPY . .
EXPOSE 8000
CMD ["python", "hello.py"]