# 中文字体配置说明

## 用途

此文件夹用于存放中文字体文件，使 Python 绘图工具（matplotlib）能够正确显示中文字符。

## 支持的字体格式
- `.ttf` - TrueType 字体
- `.otf` - OpenType 字体
- `.ttc` - TrueType Collection 字体集合

## 推荐的中文字体

### Linux 系统常用中文字体
```bash
# Ubuntu/Debian
sudo apt-get install fonts-wqy-zenhei fonts-wqy-microhei fonts-noto-cjk

# Fedora/RHEL
sudo dnf install google-noto-sans-cjk-fonts google-noto-serif-cjk-fonts

# Arch Linux
sudo pacman -S noto-fonts-cjk wqy-zenhei wqy-microhei
```

### 字体文件位置（系统自带）

- `/usr/share/fonts/truetype/wqy/` - 文泉驿字体
- `/usr/share/fonts/truetype/noto/` - Noto 字体
- `/usr/share/fonts/opentype/noto/` - Noto OpenType 字体

## 使用方法

### 方法1：复制字体文件到此文件夹
```bash
# 复制系统字体到 fonts 文件夹
cp /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc /home/Si/.cherrystudio/mcp/python/fonts/
cp /usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc /home/Si/.cherrystudio/mcp/python/fonts/
```

### 方法2：创建符号链接（推荐，节省空间）
```bash
# 创建符号链接到系统字体
ln -s /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc /home/Si/.cherrystudio/mcp/python/fonts/
ln -s /usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc /home/Si/.cherrystudio/mcp/python/fonts/
```


## 注意事项

1. 字体文件可能较大，建议使用符号链接
2. 修改字体后需要重启 MCP 服务器
3. 某些字体可能需要额外的配置文件
