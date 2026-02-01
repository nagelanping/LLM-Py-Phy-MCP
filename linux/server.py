#!/usr/bin/env python3
"""
LLM-Py-Phy-MCP
Python MCP Server - System-level Python Execution Environment
Provides Python code execution in isolated virtual environment with full system access
"""

import sys
import os
import subprocess
import traceback
import json
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# ============================================================
# VIRTUAL ENVIRONMENT ENFORCEMENT
# ============================================================

def get_venv_python() -> str:
    """获取虚拟环境的 Python 解释器路径。"""
    # 检查是否已在虚拟环境中
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv:
        return sys.executable
    
    # 在脚本目录中查找虚拟环境
    script_dir = Path(__file__).parent
    venv_paths = [
        script_dir / "venv" / "bin" / "python",
        script_dir / ".venv" / "bin" / "python",
        script_dir / "venv" / "Scripts" / "python.exe",
    ]
    
    for venv_python in venv_paths:
        if venv_python.is_file():
            return str(venv_python)
    
    # 回退到系统 Python
    print(f"警告: 未找到虚拟环境，使用系统 Python: {sys.executable}", file=sys.stderr)
    return sys.executable


def is_in_venv() -> bool:
    """检查是否在虚拟环境中运行。"""
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )


# Initialize venv paths
VENV_PYTHON = get_venv_python()
VENV_INFO = {'in_venv': is_in_venv(), 'python_path': VENV_PYTHON}

# ============================================================
# FONT CONFIGURATION FOR CHINESE CHARACTERS
# ============================================================

# Get the fonts directory path
FONTS_DIR = Path(__file__).parent / "fonts"
FONTS_DIR.mkdir(exist_ok=True)

# Set environment variables for matplotlib to find Chinese fonts
os.environ["MPLCONFIGDIR"] = str(Path(__file__).parent / ".matplotlib")
os.environ["FONTCONFIG_PATH"] = str(FONTS_DIR)

# Startup logging
print(f"Python MCP Server Starting...", file=sys.stderr)
print(f"   Virtual Environment: {'YES' if VENV_INFO['in_venv'] else 'NO'}", file=sys.stderr)
print(f"   Python: {VENV_PYTHON}", file=sys.stderr)
print(f"   Fonts Directory: {FONTS_DIR}", file=sys.stderr)


# ============================================================
# MCP SERVER SETUP
# ============================================================

app = Server("python-executor")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Python execution tools."""
    return [
        Tool(
            name="python_execute",
            description="执行Python代码，支持完整系统访问、包导入、多行代码，返回stdout/stderr",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的Python代码(在一个代码块中完成所有操作)"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "工作目录(可选，默认/tmp)"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "超时秒数(默认30)"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="python_install",
            description="使用pip安装Python包，支持单个或多个包",
            inputSchema={
                "type": "object",
                "properties": {
                    "packages": {
                        "type": "string",
                        "description": "包名(空格分隔，如'numpy pandas')"
                    },
                    "upgrade": {
                        "type": "boolean",
                        "description": "是否升级(默认false)"
                    }
                },
                "required": ["packages"]
            }
        ),
        Tool(
            name="python_run_script",
            description="运行Python脚本文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "脚本绝对路径"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "命令行参数"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "工作目录(可选)"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "超时秒数(默认60)"
                    }
                },
                "required": ["script_path"]
            }
        ),
        Tool(
            name="python_eval",
            description="快速求值Python表达式并返回结果",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要求值的表达式"
                    }
                },
                "required": ["expression"]
            }
        ),
        Tool(
            name="python_list_packages",
            description="列出所有已安装的Python包",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution."""
    try:
        if name == "python_execute":
            return await execute_python(arguments)
        elif name == "python_install":
            return await install_packages(arguments)
        elif name == "python_run_script":
            return await run_script(arguments)
        elif name == "python_eval":
            return await eval_expression(arguments)
        elif name == "python_list_packages":
            return await list_packages()
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        error_msg = f"Error executing {name}:\n{traceback.format_exc()}"
        return [TextContent(type="text", text=error_msg)]


# ============================================================
# TOOL IMPLEMENTATIONS
# ============================================================

async def execute_python(args: dict) -> list[TextContent]:
    """Execute Python code in virtual environment."""
    code = args["code"]
    working_dir = args.get("working_dir", "/tmp")
    timeout = args.get("timeout", 30)

    # Prepend matplotlib font configuration for Chinese characters
    # 使用绝对路径确保字体正确加载
    fonts_dir_abs = str(FONTS_DIR.resolve())
    mpl_config_dir_abs = str((Path(__file__).parent / ".matplotlib").resolve())
    
    font_config = f"""
# Auto-injected: Chinese font configuration
import os
import re
from pathlib import Path

def extract_font_family(filename):
    \"\"\"从文件名提取字体家族名称\"\"\"
    # 移除扩展名
    name = Path(filename).stem
    # 移除字重后缀
    name = re.sub(r'-(Bold|Regular|Light|Medium|Thin|ExtraLight|SemiBold|Black|Heavy|Italic|BoldItalic|LightItalic|SemiBoldItalic|ExtraLightItalic)+$', '', name, flags=re.IGNORECASE)
    # 在驼峰命名处添加空格
    name = re.sub(r'([a-z])([A-Z])', r'\\1 \\2', name)
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\\1 \\2', name)
    return name.strip()

# 使用绝对路径（从 server.py 传入）
fonts_dir = Path(r"{fonts_dir_abs}")
os.environ["MPLCONFIGDIR"] = r"{mpl_config_dir_abs}"

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    # 动态加载 fonts/ 目录中的所有字体文件，并从文件名提取字体家族
    font_families = set()
    if fonts_dir.exists():
        for ext in ["*.ttf", "*.otf", "*.ttc"]:
            for font_file in fonts_dir.glob(ext):
                try:
                    # 使用绝对路径添加字体到 matplotlib
                    font_path_abs = str(font_file.resolve())
                    fm.fontManager.addfont(font_path_abs)
                    # 从文件名提取字体家族名称
                    family = extract_font_family(font_file.name)
                    font_families.add(family)
                except Exception:
                    pass
    
    # 使用提取的字体家族配置 matplotlib
    if font_families:
        plt.rcParams['font.sans-serif'] = list(font_families) + ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
except ImportError:
    pass
except Exception:
    # 确保字体配置失败不会影响代码执行
    pass
"""

    # Create temporary script
    script_path = Path(working_dir) / f"mcp_exec_{os.getpid()}.py"
    script_path.write_text(font_config + "\n" + code)
    
    try:
        result = subprocess.run(
            [VENV_PYTHON, str(script_path)],
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = f"=== Execution Result ===\n"
        output += f"Exit Code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"=== STDOUT ===\n{result.stdout}\n"
        
        if result.stderr:
            output += f"=== STDERR ===\n{result.stderr}\n"
        
        if result.returncode == 0:
            output += "\n✓ Execution completed successfully"
        else:
            output += f"\n✗ Execution failed with exit code {result.returncode}"
        
        return [TextContent(type="text", text=output)]
    
    finally:
        if script_path.exists():
            script_path.unlink()


async def install_packages(args: dict) -> list[TextContent]:
    """Install Python packages using pip."""
    packages = args["packages"].strip()
    upgrade = args.get("upgrade", False)
    
    cmd = [VENV_PYTHON, "-m", "pip", "install"]
    if upgrade:
        cmd.append("--upgrade")
    cmd.extend(packages.split())
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300
    )
    
    output = f"=== Package Installation ===\n"
    output += f"Command: {' '.join(cmd)}\n\n"
    output += result.stdout
    
    if result.stderr:
        output += f"\n=== STDERR ===\n{result.stderr}"
    
    if result.returncode == 0:
        output += "\n\n✓ Installation completed successfully"
    else:
        output += f"\n\n✗ Installation failed with exit code {result.returncode}"
    
    return [TextContent(type="text", text=output)]


async def run_script(args: dict) -> list[TextContent]:
    """Run a Python script file."""
    script_path = args["script_path"]
    script_args = args.get("args", [])
    working_dir = args.get("working_dir", os.path.dirname(script_path))
    timeout = args.get("timeout", 60)
    
    if not os.path.isfile(script_path):
        return [TextContent(type="text", text=f"Error: Script not found: {script_path}")]
    
    cmd = [VENV_PYTHON, script_path] + script_args
    
    result = subprocess.run(
        cmd,
        cwd=working_dir,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    output = f"=== Script Execution ===\n"
    output += f"Script: {script_path}\n"
    output += f"Args: {script_args}\n"
    output += f"Exit Code: {result.returncode}\n\n"
    
    if result.stdout:
        output += f"=== STDOUT ===\n{result.stdout}\n"
    
    if result.stderr:
        output += f"=== STDERR ===\n{result.stderr}\n"
    
    if result.returncode == 0:
        output += "\n✓ Script completed successfully"
    else:
        output += f"\n✗ Script failed with exit code {result.returncode}"
    
    return [TextContent(type="text", text=output)]


async def eval_expression(args: dict) -> list[TextContent]:
    """Evaluate a Python expression."""
    expression = args["expression"]
    
    code = f"result = {expression}\nprint(result)\nprint(f'__TYPE__{{type(result).__name__}}')"
    
    script_path = Path("/tmp") / f"mcp_eval_{os.getpid()}.py"
    script_path.write_text(code)
    
    try:
        result = subprocess.run(
            [VENV_PYTHON, str(script_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            value = '\n'.join(lines[:-1]) if len(lines) > 1 else lines[0]
            type_info = lines[-1].replace('__TYPE__', '') if lines else 'unknown'
            
            output = f"=== Expression Evaluation ===\n"
            output += f"Expression: {expression}\n"
            output += f"Result: {value}\n"
            output += f"Type: {type_info}"
        else:
            output = f"Error evaluating expression:\n{expression}\n\n"
            output += f"Error: {result.stderr}\n"
        
        return [TextContent(type="text", text=output)]
    
    except Exception as e:
        error_msg = f"Error evaluating expression:\n{expression}\n\n"
        error_msg += f"Error: {str(e)}\n"
        error_msg += traceback.format_exc()
        return [TextContent(type="text", text=error_msg)]
    
    finally:
        if script_path.exists():
            script_path.unlink()


async def list_packages() -> list[TextContent]:
    """List installed Python packages."""
    result = subprocess.run(
        [VENV_PYTHON, "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        packages = json.loads(result.stdout)
        output = "=== Installed Python Packages ===\n\n"
        output += f"{'Package':<30} Version\n"
        output += "=" * 50 + "\n"
        
        for pkg in sorted(packages, key=lambda x: x["name"].lower()):
            output += f"{pkg['name']:<30} {pkg['version']}\n"
        
        output += f"\nTotal: {len(packages)} packages"
    else:
        output = f"Error listing packages:\n{result.stderr}"
    
    return [TextContent(type="text", text=output)]


# ============================================================
# MAIN SERVER ENTRY POINT
# ============================================================

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
