#!/usr/bin/env python3
"""
中文字体配置辅助脚本
用于自动检测和配置系统中的中文字体
"""

import os
import sys
from pathlib import Path
import shutil

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
FONTS_DIR = SCRIPT_DIR / "fonts"
FONTS_DIR.mkdir(exist_ok=True)

# Python 绘图最常用的中文字体路径
SYSTEM_FONT_PATHS = [
    "/usr/share/fonts/truetype/wqy",      # 文泉驿
    "/usr/share/fonts/truetype/noto",     # 思源黑体
    "/usr/share/fonts/opentype/noto",     # 思源黑体
    "/System/Library/Fonts",              # macOS
    "/Library/Fonts",                     # macOS
    "C:/Windows/Fonts",                   # Windows
]

# 最常用的中文字体（按优先级排序）
CHINESE_FONT_PATTERNS = [
    "Noto",           # Noto Sans CJK SC (思源黑体) - 最通用
    "wqy",            # WenQuanYi Micro Hei (文泉驿微米黑) - Linux 常见
    "SimHei",         # 黑体 - Windows 常见
    "msyh",           # Microsoft YaHei (微软雅黑) - Windows 常见
]


def find_chinese_fonts():
    """查找系统中的常用中文字体"""
    found_fonts = []
    
    for font_dir in SYSTEM_FONT_PATHS:
        font_path = Path(font_dir)
        if not font_path.exists():
            continue
        
        for ext in ["*.ttf", "*.otf", "*.ttc"]:
            for font_file in font_path.rglob(ext):
                if font_file.is_file() and any(p.lower() in font_file.name.lower() for p in CHINESE_FONT_PATTERNS):
                    found_fonts.append(font_file)
    
    return sorted(set(found_fonts))


def link_fonts(font_files):
    """创建字体文件的符号链接"""
    linked = []
    for font_file in font_files:
        target = FONTS_DIR / font_file.name
        try:
            if target.exists() or target.is_symlink():
                target.unlink()
            os.symlink(font_file, target)
            linked.append(target)
            print(f"✓ 已链接: {font_file.name}")
        except Exception as e:
            print(f"✗ 链接失败 {font_file.name}: {e}")
    return linked


def copy_fonts(font_files):
    """复制字体文件"""
    copied = []
    for font_file in font_files:
        target = FONTS_DIR / font_file.name
        try:
            if target.exists():
                target.unlink()
            shutil.copy2(font_file, target)
            copied.append(target)
            print(f"✓ 已复制: {font_file.name}")
        except Exception as e:
            print(f"✗ 复制失败 {font_file.name}: {e}")
    return copied


def list_current_fonts():
    """列出当前 fonts 文件夹中的字体"""
    fonts = []
    for ext in ["*.ttf", "*.otf", "*.ttc"]:
        fonts.extend(FONTS_DIR.glob(ext))
    return sorted(fonts)


def link_directory(source_dir):
    """链接整个字体目录"""
    source_path = Path(source_dir)
    if not source_path.exists() or not source_path.is_dir():
        print(f"✗ 目录不存在: {source_dir}")
        return []
    
    font_files = []
    for ext in ["*.ttf", "*.otf", "*.ttc"]:
        font_files.extend(source_path.rglob(ext))
    
    if not font_files:
        print("✗ 未找到字体文件")
        return []
    
    print(f"✓ 找到 {len(font_files)} 个字体文件")
    return link_fonts(font_files)


def print_usage():
    """打印使用说明"""
    print("""
中文字体配置工具
==================================================

用法:
  python setup_chinese_fonts.py [命令] [参数]

命令:
  (无参数)      交互式模式，自动查找系统字体
  auto          自动模式：查找并链接系统字体
  link <目录>   链接整个字体目录到 fonts 文件夹
  list          列出当前 fonts 文件夹中的字体

示例:
  python setup_chinese_fonts.py
  python setup_chinese_fonts.py auto
  python setup_chinese_fonts.py link /usr/share/fonts/truetype/wqy
  python setup_chinese_fonts.py list
""")


def main():
    args = sys.argv[1:]
    
    # 显示帮助
    if "-h" in args or "--help" in args or "help" in args:
        print_usage()
        return
    
    # 列出当前字体
    if "list" in args:
        print("=" * 50)
        print("当前 fonts 文件夹中的字体")
        print("=" * 50)
        current_fonts = list_current_fonts()
        if not current_fonts:
            print("✗ fonts 文件夹中没有字体文件")
        else:
            print(f"共 {len(current_fonts)} 个字体文件:\n")
            for font in current_fonts:
                size = font.stat().st_size / 1024
                print(f"  - {font.name} ({size:.1f} KB)")
        return
    
    # 链接目录
    if len(args) >= 2 and args[0] == "link":
        print("=" * 50)
        print("链接字体目录")
        print("=" * 50)
        linked = link_directory(args[1])
        print(f"\n✓ 成功链接 {len(linked)} 个字体文件")
        print("\n下一步: 重启 MCP 服务器\n")
        return
    
    # 自动模式或交互式模式
    print("=" * 50)
    print("中文字体配置工具")
    print("=" * 50)
    
    # 列出当前字体
    current_fonts = list_current_fonts()
    print(f"\n当前 fonts 文件夹中的字体 ({len(current_fonts)} 个):")
    for font in current_fonts:
        print(f"  - {font.name}")
    
    # 查找系统字体
    print("\n正在查找常用中文字体...")
    system_fonts = find_chinese_fonts()
    
    if not system_fonts:
        print("✗ 未找到常用中文字体")
        print("\n建议操作:")
        print("  1. 安装常用中文字体包:")
        print("     sudo apt-get install fonts-wqy-microhei fonts-noto-cjk")
        print("  2. 使用 link 命令链接字体目录:")
        print("     python setup_chinese_fonts.py link <字体目录>")
        return
    
    print(f"✓ 找到 {len(system_fonts)} 个常用中文字体:")
    for i, font in enumerate(system_fonts[:10], 1):  # 只显示前10个
        size = font.stat().st_size / 1024
        print(f"  {i}. {font.name} ({size:.1f} KB)")
    if len(system_fonts) > 10:
        print(f"  ... 还有 {len(system_fonts) - 10} 个字体")
    
    # 自动模式直接链接
    if "auto" in args:
        print("\n正在创建符号链接...")
        linked = link_fonts(system_fonts)
        print(f"\n✓ 成功链接 {len(linked)} 个字体文件")
        print("\n下一步: 重启 MCP 服务器\n")
        return
    
    # 交互式模式
    print("\n请选择操作:")
    print("  1. 创建符号链接 (推荐，节省空间)")
    print("  2. 复制字体文件")
    print("  3. 仅显示信息，不操作")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        print("\n正在创建符号链接...")
        linked = link_fonts(system_fonts)
        print(f"\n✓ 成功链接 {len(linked)} 个字体文件")
    elif choice == "2":
        print("\n正在复制字体文件...")
        copied = copy_fonts(system_fonts)
        print(f"\n✓ 成功复制 {len(copied)} 个字体文件")
    else:
        print("\n未执行任何操作")
    
    print("\n下一步: 重启 MCP 服务器\n")


if __name__ == "__main__":
    main()
