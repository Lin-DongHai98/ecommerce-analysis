# -*- coding: utf-8 -*-
"""
把 orders_data.csv 一键导入 MySQL。

前置条件：
    1. 已安装依赖：pip install -r requirements.txt
    2. 已创建数据库：CREATE DATABASE order_analysis CHARACTER SET utf8mb4;
    3. 已配置 .env（可直接 cp .env.example .env 后修改）

用法：
    python init_db.py
"""

import os
import sys

import pandas as pd
from sqlalchemy import create_engine

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print('[WARN] 未安装 python-dotenv，将只读取系统环境变量')

# ---- 读取配置 ----
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'order_analysis')
DB_TABLE = os.getenv('DB_TABLE', 'orders_detail')
CSV_PATH = os.getenv('CSV_PATH', 'orders_data.csv')

missing = [k for k, v in {
    'DB_USER': DB_USER, 'DB_PASSWORD': DB_PASSWORD,
    'DB_HOST': DB_HOST, 'DB_NAME': DB_NAME}.items() if not v]
if missing:
    sys.exit(f'[ERROR] .env 中缺少必填变量：{missing}\n'
             f'        请执行 cp .env.example .env 后填写自己的 MySQL 连接信息。')

if not os.path.exists(CSV_PATH):
    sys.exit(f'[ERROR] 找不到数据文件：{CSV_PATH}\n'
             f'        请确认 CSV_PATH 配置正确，或把 orders_data.csv 放在项目根目录。')

# ---- 读取 CSV ----
df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
print(f'[INFO] 读取 {CSV_PATH}：{len(df)} 行 × {len(df.columns)} 列')

# ---- 写入 MySQL ----
url = (f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}'
       f'/{DB_NAME}?charset=utf8mb4')

try:
    engine = create_engine(url)
    with engine.connect() as conn:
        pass
except Exception as err:
    sys.exit(f'[ERROR] MySQL 连接失败：{err}\n'
             f'        请确认 .env 配置正确，且已执行：'
             f'CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4;')

df.to_sql(DB_TABLE, engine, if_exists='replace', index=False)
print(f'[OK] 导入完成：{len(df)} 行 → {DB_NAME}.{DB_TABLE}')
