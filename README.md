# 邮件分类助手 (Mail Sorter)

基于规则的智能 QQ 邮件分类系统。

## 功能特性

- **智能分类**: 自动将邮件分为简历类、报告类、广告类、通知类、验证码类
- **精美界面**: LaTeX Paper 论文排版风格
- **跨平台**: 支持 Windows EXE 和 Android APK
- **隐私优先**: 凭据本地存储，不上传任何信息

## 分类规则

| 分类 | 关键词 | 发件人特征 |
|------|--------|-----------|
| 简历类 | 简历、求职、应聘、offer、面试 | job、zhaopin、career |
| 报告类 | 报告、分析、报表、月报、周报 | report、analytics |
| 广告类 | 促销、优惠、折扣、限时 | marketing、promotion |
| 通知类 | 通知、提醒、公告、系统消息 | official、support |
| 验证码类 | 验证码、注册、登录、token | noreply、security |

## 快速开始

### 1. 获取 QQ 邮箱授权码

1. 登录 [QQ 邮箱](https://mail.qq.com)
2. 进入设置 → 账户
3. 开启 IMAP/SMTP 服务
4. 生成授权码并妥善保存

### 2. 运行应用

```bash
# 安装依赖
pip install flet

# 运行
python main.py
```

### 3. 配置与使用

1. 输入邮箱地址和授权码
2. 点击"连接"
3. 点击"开始分类"

## 开发

### 环境要求

- Python 3.10+
- flet 0.21+

### 项目结构

```
mail-sorter/
├── src/
│   ├── core/
│   │   ├── classifier.py    # 分类引擎
│   │   └── imap_client.py  # IMAP 客户端
│   ├── ui/
│   │   └── main_app.py     # 主界面
│   └── utils/
│       └── config.py       # 配置管理
├── main.py                 # 入口
├── requirements.txt
└── pyproject.toml
```

## 构建

### Windows EXE

使用 PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --name "MailSorter" main.py
```

### Android APK

使用 Flet 构建:

```bash
flet build apk
```

## 许可证

MIT License
