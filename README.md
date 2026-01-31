# LLM-Py-Phy-MCP 服务器

一个为 LLM 提供实体机 Python 执行能力的模型上下文协议（MCP）服务器，支持 Linux 和 Windows 平台，包含多种 Python 库。

**警告**：此 MCP 专为 LLM 在实体机执行 Python 代码而设计。在启用此服务器之前，请确保 LLM 代理是可信的，或通过客户端配置 MCP 工具执行前的权限。

## 功能特性

### 核心工具

1. **python_execute** - 执行 Python 代码，支持完整系统访问、包导入、多行代码，返回 stdout/stderr

2. **python_eval** - 快速求值 Python 表达式并返回结果

3. **python_install** - 使用 pip 安装 Python 包，支持单个或多个包

4. **python_run_script** - 运行 Python 脚本文件

5. **python_list_packages** - 列出所有已安装的 Python 包

### 包含的 Python 库

参考 `requirements.txt`，包含以下主要类别：

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

### Linux 平台

```bash
# 运行安装脚本
bash setup.sh

# 或手动安装
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows 平台

在命令提示符或 PowerShell 中运行：

```batch
setup.bat
```

该脚本会自动创建虚拟环境、升级 pip 并安装所有依赖包。

#### Windows 手动安装

```batch
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 中文字体支持

### Linux 平台

Linux 版本支持配置中文字体，Python 绘图常见字体示例：

- **Noto Sans CJK** (思源黑体)
- **Sarasa Gothic** (更纱黑体)
- **WenQuanYi Micro Hei** (文泉驿微米黑)

执行的 Python 代码会自动注入 matplotlib 字体配置，确保中文正常显示。

#### 配置中文字体

使用 `setup_chinese_fonts.py` 自动配置中文字体：

```bash
python setup_chinese_fonts.py
```

### Windows 平台

Windows 版本暂时不包含中文字体配置。如需在 matplotlib 中使用特定中文字体，请在代码中手动配置或优化 prompt 让 llm 主动使用对应字体。

## MCP 配置

### Linux 平台

将以下配置添加到 MCP 客户端配置文件中（例如 `~/.cherrystudio/mcp/config.json` 或 Claude Desktop 的配置文件）：

```json
{
  "mcpServers": {
    "python": {
      "command": "/path/to/LLM-Py-Phy-MCP/linux/venv/bin/python",
      "args": [
        "/path/to/LLM-Py-Phy-MCP/linux/server.py"
      ],
      "env": {}
    }
  }
}
```

请将 `/path/to/LLM-Py-Phy-MCP` 替换为 MCP Python 服务器目录的实际路径。

### Windows 平台

编辑配置文件，使用绝对路径并注意使用双反斜杠 `\\` 或单正斜杠 `/`：

```json
{
  "mcpServers": {
    "python": {
      "command": "X:\\path\\to\\LLM-Py-Phy-MCP\\windows\\venv\\Scripts\\python.exe",
      "args": [
        "X:\\path\\to\\LLM-Py-Phy-MCP\\windows\\server.py"
      ],
      "env": {}
    }
  }
}
```

替换路径、配置完成后，重启 MCP 客户端以加载新配置。

## 系统要求

- **Linux**: 任何主流发行版
- **Windows**: Windows 10/11
- **Python**: 3.8 或更高版本
- **磁盘空间**: 至少 1GB 可用空间
- **MCP**: mcp 工具包

## 安全说明

- 代码以用户级权限执行
- 无沙箱隔离 - 仅与可信的 LLM 代理一起使用
- Linux 工作目录默认为 /tmp
- Windows 工作目录默认为系统临时目录

## 技术说明

### Linux 版本特性

- 虚拟环境路径：`venv/bin/python`
- 临时目录：`/tmp`
- 自动注入中文字体配置到执行的 Python 代码
- 动态加载 `fonts/` 目录中的字体文件

### Windows 版本特性

- 虚拟环境路径：`venv\Scripts\python.exe`
- 临时目录：使用 `tempfile.gettempdir()` 获取系统临时目录
- 文件操作使用 UTF-8 编码，错误时使用替换模式
- 使用异步 subprocess 执行，防止继承 MCP stdio

## 故障排除

### 虚拟环境创建失败

确保 Python 已正确安装并添加到 PATH 环境变量中。

### 依赖安装失败

某些包可能需要 C++ 编译器：

- **Linux**: 安装 `build-essential` 和 `python3-dev`
- **Windows**: 安装 Visual Studio Build Tools 或使用预编译的 wheel 文件

### MCP 客户端无法连接

1. 检查配置文件中的路径是否正确
2. 确保使用绝对路径
3. 检查虚拟环境是否正确创建
4. 查看 MCP 客户端的日志输出

## 许可证

**0BSD LICENSE**