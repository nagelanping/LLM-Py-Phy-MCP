# LLM-Py-Phy-MCP 服务器

**Linux 平台**下的一个为 LLM 提供**实体机 Python 执行能力**的模型上下文协议（MCP）服务器，包含多种 Python 库。
- 核心逻辑部分完全跨平台，**迁移到 Windows 需要调整路径处理和系统指令**
- **警告**：此 MCP 专为 LLM 在实体机执行 Python 代码而设计。在启用此服务器之前，请确保 LLM 代理是可信的，或通过客户端配置 MCP 工具执行前的权限。

## 功能特性

### 核心工具

1. **python_execute** - 执行 Python 代码，支持完整系统访问、包导入、多行代码，返回 stdout/stderr

2. **python_eval** - 快速求值 Python 表达式并返回结果

3. **python_install** - 使用 pip 安装 Python 包，支持单个或多个包

4. **python_run_script** - 运行 Python 脚本文件

5. **python_list_packages** - 列出所有已安装的 Python 包

**包含的 Python 库（参考 `requirements.txt` ）：**
```
# ============================================
# MCP Server Dependencies
# ============================================
mcp>=1.0.0

# ============================================
# 科学计算与数据分析核心库
# ============================================
numpy>=1.24.0              # 数值计算基础
pandas>=2.0.0              # 数据分析和处理
scipy>=1.10.0              # 科学计算（统计、优化、信号处理）
matplotlib>=3.7.0          # 数据可视化
seaborn>=0.12.0            # 统计数据可视化
plotly>=5.14.0             # 交互式可视化
scikit-learn>=1.3.0        # 机器学习
statsmodels>=0.14.0        # 统计建模

# ============================================
# 数据处理与存储
# ============================================
openpyxl>=3.1.0            # Excel 文件读写 (.xlsx)
xlrd>=2.0.1                # Excel 文件读取 (.xls)
xlsxwriter>=3.1.0          # Excel 文件写入（高级格式）
python-docx>=0.8.11        # Word 文档 (.docx) 处理
pypdf>=3.15.0              # PDF 读取和提取（替代PyPDF2）
pdfplumber>=0.9.0          # PDF 表格提取
reportlab>=4.0.0           # PDF 生成
pillow>=10.0.0             # 图像处理
python-pptx>=0.6.21        # PowerPoint 处理

# ============================================
# 文本处理与解析
# ============================================
beautifulsoup4>=4.12.0     # HTML/XML 解析
lxml>=4.9.0                # XML/HTML 处理（高性能）
markdown>=3.4.0            # Markdown 处理
pyyaml>=6.0                # YAML 文件处理
toml>=0.10.2               # TOML 文件处理
python-dotenv>=1.0.0       # .env 环境变量加载
jinja2>=3.1.0              # 模板引擎

# ============================================
# 网络请求与API
# ============================================
requests>=2.31.0           # HTTP 请求（同步）
httpx>=0.24.0              # HTTP 客户端（支持同步和异步）
urllib3>=2.0.0             # HTTP 连接池

# ============================================
# 数据库与持久化
# ============================================
sqlalchemy>=2.0.0          # SQL ORM 和数据库工具
pymongo>=4.4.0             # MongoDB 驱动
redis>=4.6.0               # Redis 客户端

# ============================================
# 日期时间处理
# ============================================
python-dateutil>=2.8.2     # 日期时间扩展
pytz>=2023.3               # 时区处理
arrow>=1.2.3               # 更友好的日期时间库

# ============================================
# 实用工具
# ============================================
tqdm>=4.65.0               # 进度条显示
colorama>=0.4.6            # 终端颜色输出
rich>=13.4.0               # 富文本终端输出
click>=8.1.0               # 命令行工具
loguru>=0.7.0              # 现代日志库

# ============================================
# 数据验证与序列化
# ============================================
pydantic>=2.0.0            # 数据验证
marshmallow>=3.19.0        # 对象序列化/反序列化
jsonschema>=4.18.0         # JSON Schema 验证

# ============================================
# 加密与安全
# ============================================
cryptography>=41.0.0       # 加密库
bcrypt>=4.0.0              # 密码哈希
pyjwt>=2.8.0               # JWT 令牌

# ============================================
# 数据格式转换
# ============================================
chardet>=5.1.0             # 字符编码检测
python-magic>=0.4.27       # 文件类型识别
tabulate>=0.9.0            # 表格格式化输出

```

## 安装

```bash
# 运行安装脚本
bash setup.sh

# 或手动安装
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 中文字体支持

该 MCP 服务器支持配置中文字体，Python 绘图常见字体示例：

- **Noto Sans CJK** (思源黑体)
- **Sarasa Gothic** (更纱黑体)
- **WenQuanYi Micro Hei** (文泉驿微米黑)

执行的Python代码会自动注入matplotlib字体配置，确保中文正常显示。

## 中文字体配置

使用 [`setup_chinese_fonts.py`](setup_chinese_fonts.py) 自动配置中文字体：

```bash
python setup_chinese_fonts.py
```

## MCP 配置

将以下配置添加到 MCP 客户端配置文件中（例如 `~/.cherrystudio/mcp/config.json`）：

```json
{
  "mcpServers": {
    "python": {
      "command": "/path/to/mcp/python/venv/bin/python",
      "args": [
        "/path/to/mcp/python/server.py"
      ],
      "env": {}
    }
  }
}
```

请将 `/path/to/mcp/python` 替换为 MCP Python 服务器目录的实际路径。

## 系统要求

- Python 3.8 或更高版本
- mcp 工具包

## 安全说明

- **代码以用户级权限执行**
- **无沙箱隔离 - 仅与可信的 LLM 代理一起使用**
- 工作目录默认为 /tmp

## 许可证

**0BSD LICENSE**