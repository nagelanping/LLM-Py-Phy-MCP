#!/usr/bin/env python3
"""
中文字体配置辅助脚本
用于自动检测和配置系统中的中文字体
"""

import os
import sys
from pathlib import Path
import subprocess

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
FONTS_DIR = SCRIPT_DIR / "fonts"
FONTS_DIR.mkdir(exist_ok=True)

# 常见的中文字体路径
SYSTEM_FONT_PATHS = [
    # Linux
    "/usr/share/fonts/truetype/wqy",
    "/usr/share/fonts/truetype/noto",
    "/usr/share/fonts/truetype/arphic",
    "/usr/share/fonts/opentype/noto",
    "/usr/share/fonts/cjk",
    # macOS
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti.ttc",
    "/Library/Fonts",
    # Windows (通过 Wine)
    "/usr/share/fonts/wine",
]

# 常见的中文字体文件名
CHINESE_FONT_PATTERNS = [
    "wqy-zenhei",
    "wqy-microhei",
    "NotoSansCJK",
    "NotoSerifCJK",
    "SimHei",
    "SimSun",
    "PingFang",
    "STHeiti",
    "ARPL",
    "gbsn",
    "gkai",
]


def find_chinese_fonts():
    """查找系统中的中文字体文件"""
    found_fonts = []

    for font_dir in SYSTEM_FONT_PATHS:
        font_path = Path(font_dir)
        if not font_path.exists():
            continue

        # 查找匹配的字体文件
        for pattern in CHINESE_FONT_PATTERNS:
            for ext in ["*.ttf", "*.otf", "*.ttc"]:
                for font_file in font_path.glob(f"*{pattern}*{ext}"):
                    if font_file.is_file():
                        found_fonts.append(font_file)

    # 去重
    found_fonts = list(set(found_fonts))
    return sorted(found_fonts)


def link_fonts(font_files):
    """创建字体文件的符号链接"""
    linked = []
    for font_file in font_files:
        target = FONTS_DIR / font_file.name
        try:
            # 如果已存在，先删除
            if target.exists() or target.is_symlink():
                target.unlink()

            # 创建符号链接
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
            # 如果已存在，先删除
            if target.exists():
                target.unlink()

            # 复制文件
            import shutil
            shutil.copy2(font_file, target)
            copied.append(target)
            print(f"✓ 已复制: {font_file.name}")
        except Exception as e:
            print(f"✗ 复制失败 {font_file.name}: {e}")

    return copied


def list_current_fonts():
    """列出当前 fonts 文件夹中的字体"""
    fonts = list(FONTS_DIR.glob("*.ttf")) + list(FONTS_DIR.glob("*.otf")) + list(FONTS_DIR.glob("*.ttc"))
    return fonts


def main():
    print("=" * 60)
    print("中文字体配置工具")
    print("=" * 60)
    print()

    # 1. 列出当前字体
    current_fonts = list_current_fonts()
    print(f"当前 fonts 文件夹中的字体 ({len(current_fonts)} 个):")
    for font in current_fonts:
        size = font.stat().st_size / 1024
        print(f"  - {font.name} ({size:.1f} KB)")
    print()

    # 2. 查找系统字体
    print("正在查找系统中的中文字体...")
    system_fonts = find_chinese_fonts()

    if not system_fonts:
        print("✗ 未找到系统中的中文字体")
        print()
        print("建议操作:")
        print("  1. 安装中文字体包:")
        print("     sudo apt-get install fonts-wqy-zenhei fonts-noto-cjk")
        print("  2. 手动下载字体文件并放入 fonts 文件夹")
        return

    print(f"✓ 找到 {len(system_fonts)} 个中文字体:")
    for i, font in enumerate(system_fonts, 1):
        size = font.stat().st_size / 1024
        print(f"  {i}. {font.name} ({size:.1f} KB) - {font.parent}")
    print()

    # 3. 询问操作
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("请选择操作:")
        print("  1. 创建符号链接 (推荐，节省空间)")
        print("  2. 复制字体文件")
        print("  3. 仅显示信息，不操作")
        print()

        choice = input("请输入选项 (1/2/3): ").strip()
        mode = {"1": "link", "2": "copy", "3": "info"}.get(choice, "info")

    if mode == "link":
        print("\n正在创建符号链接...")
        linked = link_fonts(system_fonts)
        print(f"\n✓ 成功链接 {len(linked)} 个字体文件")

    elif mode == "copy":
        print("\n正在复制字体文件...")
        copied = copy_fonts(system_fonts)
        print(f"\n✓ 成功复制 {len(copied)} 个字体文件")

    else:
        print("\n未执行任何操作")

    print()
    print("=" * 60)
    print("配置完成！")
    print("=" * 60)
    print()
    print("下一步:")
    print("  1. 重启 MCP 服务器")
    print("  2. 运行测试代码验证中文字体是否生效")
    print()


if __name__ == "__main__":
    main()
