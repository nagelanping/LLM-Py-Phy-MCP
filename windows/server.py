#!/usr/bin/env python3
"""
LLM-Py-Phy-MCP - Windows Version
Python MCP Server - System-level Python Execution Environment
Provides Python code execution in isolated virtual environment with full system access
"""

import sys
import os
import asyncio
import subprocess
import traceback
import json
import tempfile
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
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    if in_venv:
        return sys.executable

    # 在脚本目录中查找虚拟环境（Windows 优先）
    script_dir = Path(__file__).parent
    venv_paths = [
        script_dir / "venv" / "Scripts" / "python.exe",
        script_dir / ".venv" / "Scripts" / "python.exe",
        script_dir / "venv" / "bin" / "python",
    ]

    for venv_python in venv_paths:
        if venv_python.is_file():
            return str(venv_python)

    # 回退到系统 Python
    return sys.executable


def is_in_venv() -> bool:
    """检查是否在虚拟环境中运行。"""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


# Initialize venv paths
VENV_PYTHON = get_venv_python()
VENV_INFO = {"in_venv": is_in_venv(), "python_path": VENV_PYTHON}

# Get system temp directory
TEMP_DIR = tempfile.gettempdir()


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
                    "code": {"type": "string", "description": "要执行的Python代码"},
                    "working_dir": {
                        "type": "string",
                        "description": f"工作目录(可选，默认{TEMP_DIR})",
                    },
                    "timeout": {"type": "number", "description": "超时秒数(默认30)"},
                },
                "required": ["code"],
            },
        ),
        Tool(
            name="python_install",
            description="使用pip安装Python包，支持单个或多个包",
            inputSchema={
                "type": "object",
                "properties": {
                    "packages": {
                        "type": "string",
                        "description": "包名(空格分隔，如'numpy pandas')",
                    },
                    "upgrade": {
                        "type": "boolean",
                        "description": "是否升级(默认false)",
                    },
                },
                "required": ["packages"],
            },
        ),
        Tool(
            name="python_run_script",
            description="运行Python脚本文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {"type": "string", "description": "脚本绝对路径"},
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "命令行参数",
                    },
                    "working_dir": {"type": "string", "description": "工作目录(可选)"},
                    "timeout": {"type": "number", "description": "超时秒数(默认60)"},
                },
                "required": ["script_path"],
            },
        ),
        Tool(
            name="python_eval",
            description="快速求值Python表达式并返回结果",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "要求值的表达式"}
                },
                "required": ["expression"],
            },
        ),
        Tool(
            name="python_list_packages",
            description="列出所有已安装的Python包",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
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
    working_dir = args.get("working_dir", TEMP_DIR)
    timeout = args.get("timeout", 30)

    # Create temporary script
    script_path = Path(working_dir) / f"mcp_exec_{os.getpid()}.py"
    script_path.write_text(code, encoding="utf-8")

    try:
        # CRITICAL FIX: stdin=DEVNULL prevents subprocess from inheriting MCP stdio
        process = await asyncio.create_subprocess_exec(
            VENV_PYTHON,
            str(script_path),
            cwd=working_dir,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return [
                TextContent(
                    type="text", text=f"Execution timed out after {timeout} seconds"
                )
            ]

        output = f"=== Execution Result ===\n"
        output += f"Exit Code: {process.returncode}\n\n"

        if stdout:
            output += f"=== STDOUT ===\n{stdout.decode('utf-8', errors='replace')}\n"

        if stderr:
            output += f"=== STDERR ===\n{stderr.decode('utf-8', errors='replace')}\n"

        if process.returncode == 0:
            output += "\n✓ Execution completed successfully"
        else:
            output += f"\n✗ Execution failed with exit code {process.returncode}"

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

    # CRITICAL FIX: stdin=DEVNULL prevents subprocess from inheriting MCP stdio
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        return [
            TextContent(
                type="text", text="Package installation timed out after 300 seconds"
            )
        ]

    output = f"=== Package Installation ===\n"
    output += f"Command: {' '.join(cmd)}\n\n"
    output += stdout.decode("utf-8", errors="replace")

    if stderr:
        output += f"\n=== STDERR ===\n{stderr.decode('utf-8', errors='replace')}"

    if process.returncode == 0:
        output += "\n\n✓ Installation completed successfully"
    else:
        output += f"\n\n✗ Installation failed with exit code {process.returncode}"

    return [TextContent(type="text", text=output)]


async def run_script(args: dict) -> list[TextContent]:
    """Run a Python script file."""
    script_path = args["script_path"]
    script_args = args.get("args", [])
    working_dir = args.get("working_dir", os.path.dirname(script_path))
    timeout = args.get("timeout", 60)

    if not os.path.isfile(script_path):
        return [
            TextContent(type="text", text=f"Error: Script not found: {script_path}")
        ]

    cmd = [VENV_PYTHON, script_path] + script_args

    # CRITICAL FIX: stdin=DEVNULL prevents subprocess from inheriting MCP stdio
    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=working_dir,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        return [
            TextContent(
                type="text", text=f"Script execution timed out after {timeout} seconds"
            )
        ]

    output = f"=== Script Execution ===\n"
    output += f"Script: {script_path}\n"
    output += f"Args: {script_args}\n"
    output += f"Exit Code: {process.returncode}\n\n"

    if stdout:
        output += f"=== STDOUT ===\n{stdout.decode('utf-8', errors='replace')}\n"

    if stderr:
        output += f"=== STDERR ===\n{stderr.decode('utf-8', errors='replace')}\n"

    if process.returncode == 0:
        output += "\n✓ Script completed successfully"
    else:
        output += f"\n✗ Script failed with exit code {process.returncode}"

    return [TextContent(type="text", text=output)]


async def eval_expression(args: dict) -> list[TextContent]:
    """Evaluate a Python expression."""
    expression = args["expression"]

    code = f"result = {expression}\nprint(result)\nprint(f'__TYPE__{{type(result).__name__}}')"

    script_path = Path(TEMP_DIR) / f"mcp_eval_{os.getpid()}.py"
    script_path.write_text(code, encoding="utf-8")

    try:
        # CRITICAL FIX: stdin=DEVNULL prevents subprocess from inheriting MCP stdio
        process = await asyncio.create_subprocess_exec(
            VENV_PYTHON,
            str(script_path),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return [
                TextContent(
                    type="text", text=f"Expression evaluation timed out: {expression}"
                )
            ]

        if process.returncode == 0:
            stdout_text = stdout.decode("utf-8", errors="replace").strip()
            lines = stdout_text.split("\n")
            value = "\n".join(lines[:-1]) if len(lines) > 1 else lines[0]
            type_info = lines[-1].replace("__TYPE__", "") if lines else "unknown"

            output = f"=== Expression Evaluation ===\n"
            output += f"Expression: {expression}\n"
            output += f"Result: {value}\n"
            output += f"Type: {type_info}"
        else:
            output = f"Error evaluating expression:\n{expression}\n\n"
            output += f"Error: {stderr.decode('utf-8', errors='replace')}\n"

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
    # CRITICAL FIX: stdin=DEVNULL prevents subprocess from inheriting MCP stdio
    process = await asyncio.create_subprocess_exec(
        VENV_PYTHON,
        "-m",
        "pip",
        "list",
        "--format=json",
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        packages = json.loads(stdout.decode("utf-8", errors="replace"))
        output = "=== Installed Python Packages ===\n\n"
        output += f"{'Package':<30} Version\n"
        output += "=" * 50 + "\n"

        for pkg in sorted(packages, key=lambda x: x["name"].lower()):
            output += f"{pkg['name']:<30} {pkg['version']}\n"

        output += f"\nTotal: {len(packages)} packages"
    else:
        output = f"Error listing packages:\n{stderr.decode('utf-8', errors='replace')}"

    return [TextContent(type="text", text=output)]


# ============================================================
# MAIN SERVER ENTRY POINT
# ============================================================


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    # Python 3.8+ 在 Windows 上默认使用 ProactorEventLoop，支持 subprocess
    asyncio.run(main())
