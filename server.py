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
    """Get the virtual environment's Python interpreter path."""
    # Check if already in venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return sys.executable
    
    # Look for venv in script directory
    script_dir = Path(__file__).parent
    venv_python = script_dir / "venv" / "bin" / "python"
    
    if venv_python.exists():
        return str(venv_python)
    
    # Try common venv names
    for venv_name in [".venv", "env"]:
        venv_path = script_dir / venv_name / "bin" / "python"
        if venv_path.exists():
            return str(venv_path)
    
    # Fallback to system Python with warning
    print(f"WARNING: Virtual environment not found, using system Python: {sys.executable}", 
          file=sys.stderr)
    return sys.executable


def verify_venv() -> dict:
    """Verify virtual environment status."""
    info = {
        "in_venv": False,
        "python_executable": sys.executable,
        "venv_python": get_venv_python(),
    }
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        info["in_venv"] = True
    
    return info


# Initialize venv paths
VENV_PYTHON = get_venv_python()
VENV_INFO = verify_venv()

# Startup logging
print(f"Python MCP Server Starting...", file=sys.stderr)
print(f"   Virtual Environment: {'YES' if VENV_INFO['in_venv'] else 'NO'}", file=sys.stderr)
print(f"   Python: {VENV_PYTHON}", file=sys.stderr)


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
            description=(
                "Execute Python code in a real system environment (non-sandboxed). Supports:\n"
                "- Full system access (file I/O, network, subprocess)\n"
                "- Package imports (numpy, pandas, requests, etc.)\n"
                "- Multi-line code execution\n"
                "- Returns stdout, stderr, and return value\n"
                "CAUTION: Code runs with user-level permissions"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Working directory for execution (optional, defaults to /tmp)"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Execution timeout in seconds (default: 30)"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="python_install",
            description=(
                "Install Python packages using pip in the virtual environment. "
                "Supports single or multiple package installations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "packages": {
                        "type": "string",
                        "description": "Package name(s) to install (space-separated, e.g., 'numpy pandas requests')"
                    },
                    "upgrade": {
                        "type": "boolean",
                        "description": "Upgrade if already installed (default: false)"
                    }
                },
                "required": ["packages"]
            }
        ),
        Tool(
            name="python_run_script",
            description=(
                "Run a Python script file from the filesystem. "
                "Executes with full system permissions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Absolute path to the Python script"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command-line arguments for the script"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Working directory (optional)"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Execution timeout in seconds (default: 60)"
                    }
                },
                "required": ["script_path"]
            }
        ),
        Tool(
            name="python_eval",
            description=(
                "Evaluate a Python expression and return the result. "
                "Quick evaluation for simple expressions (e.g., math calculations, data transformations)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Python expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        ),
        Tool(
            name="python_list_packages",
            description="List all installed Python packages in the virtual environment.",
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
    
    # Create temporary script
    script_path = Path(working_dir) / f"mcp_exec_{os.getpid()}.py"
    script_path.write_text(code)
    
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
