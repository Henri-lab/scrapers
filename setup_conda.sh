#!/bin/bash

# 检查conda是否已安装
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到conda命令，请确保已安装Anaconda或Miniconda"
    exit 1
fi

# 创建conda环境
echo "创建jobs-scraper conda环境..."
conda create -n jobs-scraper python=3.10 -y

# 激活环境并安装依赖
echo "激活环境并安装依赖..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate jobs-scraper

# 安装依赖
pip install -r requirements.txt

echo "conda环境设置完成！"
echo "使用命令激活环境: conda activate jobs-scraper"