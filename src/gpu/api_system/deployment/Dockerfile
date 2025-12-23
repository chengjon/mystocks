# MyStocks API模式GPU加速系统 - Docker镜像
# 基于Ubuntu 22.04，包含GPU加速功能

FROM ubuntu:22.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/conda/bin:$PATH"

# 设置工作目录
WORKDIR /opt/mystocks_gpu_api

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    htop \
    tmux \
    vim \
    net-tools \
    dnsutils \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-tk \
    libssl-dev \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装Anaconda
RUN wget -O /tmp/Anaconda3-2024.10-1-Linux-x86_64.sh https://repo.anaconda.com/archive/Anaconda3-2024.10-1-Linux-x86_64.sh \
    && bash /tmp/Anaconda3-2024.10-1-Linux-x86_64.sh -b -p /opt/conda \
    && rm /tmp/Anaconda3-2024.10-1-Linux-x86_64.sh

# 初始化conda
RUN /opt/conda/bin/conda init bash

# 安装CUDA 12.1
RUN wget -O cuda-repo-ubuntu2204-12-1-local_12.1.1-520.61.05-1_amd64.deb https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda-repo-ubuntu2204-12-1-local_12.1.1-520.61.05-1_amd64.deb \
    && dpkg -i cuda-repo-ubuntu2204-12-1-local_12.1.1-520.61.05-1_amd64.deb \
    && cp /var/cuda-repo-ubuntu2204-12-1-local/cuda-*-keyring.gpg /usr/share/keyrings/ \
    && apt-get update \
    && apt-get -y install cuda-toolkit-12-1 \
    && rm -f cuda-repo-ubuntu2204-12-1-local_12.1.1-520.61.05-1_amd64.deb

# 设置环境变量
ENV CUDA_HOME=/usr/local/cuda-12.1
ENV LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH
ENV PATH=/usr/local/cuda-12.1/bin:$PATH

# 创建Python虚拟环境
RUN /opt/conda/bin/conda create -n mystocks python=3.10 -y

# 激活虚拟环境并安装Python依赖
RUN /opt/conda/envs/mystocks/bin/pip install --no-cache-dir --upgrade pip

# 安装关键Python库
RUN /opt/conda/envs/mystocks/bin/pip install --no-cache-dir \
    numpy \
    pandas \
    pyyaml \
    psycopg2-binary \
    taospy \
    akshare \
    yfinance \
    requests \
    aiohttp \
    asyncio \
    grpcio \
    grpcio-tools \
    protobuf \
    redis \
    celery \
    flower \
    prometheus-client \
    psutil \
    pydantic \
    fastapi \
    uvicorn \
    websockets \
    sqlalchemy \
    alembic \
    jinja2 \
    click \
    loguru \
    schedule \
    python-dotenv \
    python-multipart \
    bcrypt \
    jwt \
    cryptography \
    paramiko \
    fabric \
    gitpython \
    tqdm \
    matplotlib \
    seaborn \
    plotly \
    scikit-learn \
    xgboost \
    lightgbm \
    catboost \
    tensorflow \
    torch \
    torch-geometric \
    transformers \
    datasets \
    accelerate \
    bitsandbytes \
    peft \
    trl \
    wandb \
    tensorboard \
    mlflow \
    optuna \
    hyperopt \
    ray \
    dask \
    numba \
    cython \
    pybind11 \
    cmake \
    make \
    g++ \
    && rm -rf /root/.cache/pip

# 安装RAPIDS
RUN /opt/conda/envs/mystocks/bin/conda install -c rapidsai -c conda-forge -c nvidia \
    cudf=24.02 cuml=24.02 python=3.10 -y

# 安装VectorBT
RUN /opt/conda/envs/mystocks/bin/pip install --no-cache-dir vectorbt

# 创建非root用户
RUN useradd -m -s /bin/bash mystocks && \
    mkdir -p /opt/mystocks_gpu_api && \
    chown -R mystocks:mystocks /opt/mystocks_gpu_api

# 复制项目文件
COPY . /opt/mystocks_gpu_api/

# 设置权限
RUN chown -R mystocks:mystocks /opt/mystocks_gpu_api

# 创建必要的目录
RUN mkdir -p /opt/mystocks_gpu_api/{logs,backups,cache} && \
    chown -R mystocks:mystocks /opt/mystocks_gpu_api/{logs,backups,cache}

# 创建启动脚本
COPY deployment/entrypoint.sh /opt/mystocks_gpu_api/entrypoint.sh
RUN chmod +x /opt/mystocks_gpu_api/entrypoint.sh

# 设置入口点
ENTRYPOINT ["/opt/mystocks_gpu_api/entrypoint.sh"]

# 切换到非root用户
USER mystocks

# 暴露端口
EXPOSE 50051 50052 50053 8000

# 默认命令
CMD ["python", "services/gpu_api_server.py"]
