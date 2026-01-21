#!/usr/bin/env python3
"""
中文字体配置辅助脚本
动态扫描系统字体，无需预设字体列表
"""

import os
import sys
from pathlib import Path
import shutil

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
FONTS_DIR = SCRIPT_DIR / "fonts"
FONTS_DIR.mkdir(exist_ok=True)


def scan_font_directories():
    """扫描系统字体目录，按文件夹分组返回所有字体家族"""
    # 通用搜索路径
    search_paths = [
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path.home() / ".fonts",
        Path.home() / ".local/share/fonts",
    ]
    
    families = {}
    
    for base_path in search_paths:
        if not base_path.exists():
            continue
        
        # 遍历所有子目录
        for font_dir in base_path.iterdir():
            if not font_dir.is_dir():
                continue
            
            # 收集该目录下的所有字体文件
            font_files = []
            for ext in ["*.ttf", "*.otf", "*.ttc"]:
                font_files.extend(font_dir.rglob(ext))
            
            if font_files:
                # 使用目录名作为家族标识
                family_key = f"{font_dir.parent.name}/{font_dir.name}"
                if family_key not in families:
                    families[family_key] = []
                families[family_key].extend([f for f in font_files if f.is_file()])
    
    # 去重并排序
    for key in families:
        families[key] = sorted(set(families[key]))
    
    return families


def display_font_families(families):
    """显示字体家族列表"""
    print("\n找到以下字体家族:")
    family_list = []
    
    for idx, (family_key, fonts) in enumerate(sorted(families.items()), 1):
        print(f"  {idx}. {family_key} - {len(fonts)}个字体")
        family_list.append(family_key)
    
    return family_list


def select_families_interactive(families):
    """交互式选择字体家族"""
    family_list = display_font_families(families)
    
    while True:
        choice = input("\n请输入要链接的字体家族编号 (多选用逗号分隔, 如: 1,3): ").strip()
        
        if not choice:
            print("✗ 未选择任何字体家族")
            return []
        
        try:
            indices = [int(x.strip()) for x in choice.split(",")]
            selected = []
            for idx in indices:
                if 1 <= idx <= len(family_list):
                    selected.append(family_list[idx - 1])
                else:
                    print(f"✗ 无效的编号: {idx}")
                    return None
            return selected
        except ValueError:
            print("✗ 输入格式错误，请输入数字")
            return None


def get_fonts_from_families(families, selected_family_keys):
    """从选中的字体家族中获取所有字体文件"""
    fonts = []
    for key in selected_family_keys:
        if key in families:
            fonts.extend(families[key])
    return fonts


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
  (无参数)           交互式模式，选择字体家族
  auto               自动模式：链接第一个可用字体家族
  link <目录>        链接整个字体目录到 fonts 文件夹
  list               列出当前 fonts 文件夹中的字体

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
    
    # 查找系统字体（按家族分组）
    print("\n正在扫描系统字体目录...")
    font_families = scan_font_directories()
    
    if not font_families:
        print("✗ 未找到字体")
        print("\n建议操作:")
        print("  使用 link 命令链接字体目录:")
        print("     python setup_chinese_fonts.py link <字体目录>")
        return
    
    print(f"✓ 找到 {len(font_families)} 个字体家族")
    
    # 自动模式：链接第一个字体家族
    if "auto" in args:
        first_family = list(font_families.keys())[0]
        print(f"\n自动选择字体家族: {first_family}")
        fonts_to_link = font_families[first_family]
        print(f"找到 {len(fonts_to_link)} 个字体文件")
        print("\n正在创建符号链接...")
        linked = link_fonts(fonts_to_link)
        print(f"\n✓ 成功链接 {len(linked)} 个字体文件")
        print("\n下一步: 重启 MCP 服务器\n")
        return
    
    # 交互式模式：显示字体家族供用户选择
    selected_families = None
    while selected_families is None:
        selected_families = select_families_interactive(font_families)
        if selected_families is None:
            retry = input("是否重新输入? (y/n): ").strip().lower()
            if retry != 'y':
                print("\n未执行任何操作")
                return
    
    if not selected_families:
        print("\n未执行任何操作")
        return
    
    # 获取选中家族的所有字体
    fonts_to_link = get_fonts_from_families(font_families, selected_families)
    print(f"\n选中的字体家族: {', '.join(selected_families)}")
    print(f"共 {len(fonts_to_link)} 个字体文件")
    
    # 询问操作方式
    print("\n请选择操作:")
    print("  1. 创建符号链接 (推荐，节省空间)")
    print("  2. 复制字体文件")
    print("  3. 取消")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        print("\n正在创建符号链接...")
        linked = link_fonts(fonts_to_link)
        print(f"\n✓ 成功链接 {len(linked)} 个字体文件")
    elif choice == "2":
        print("\n正在复制字体文件...")
        copied = copy_fonts(fonts_to_link)
        print(f"\n✓ 成功复制 {len(copied)} 个字体文件")
    else:
        print("\n未执行任何操作")
        return
    
    print("\n下一步: 重启 MCP 服务器\n")


if __name__ == "__main__":
    main()
