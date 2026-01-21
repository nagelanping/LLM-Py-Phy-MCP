# 中文字体配置说明

## 用途

此文件夹用于存放中文字体文件，使 Python 绘图工具（matplotlib）能够正确显示中文字符。

## 支持的字体格式

`.ttf` - TrueType 字体
`.otf` - OpenType 字体
`.ttc` - TrueType Collection 字体集合

### 系统字体文件位置示例

`/usr/share/fonts/sarasa-gothic`  # 更纱黑体
`/usr/share/fonts/noto` # 思源黑体
`/usr/share/fonts/wqy` # 文泉驿

## 使用方法

### 方法0：使用安装脚本
```bash
python setup_chinese_fonts.py
```

### 方法1：复制字体文件到此文件夹
```bash
# 复制系统字体到 fonts 文件夹
cp /usr/share/fonts/path-to-font path-to-mcp/python/fonts/
```

### 方法2：创建符号链接（推荐，节省空间）
```bash
# 创建符号链接到系统字体
ln -s /usr/share/fonts/path-to-font path-to-mcp/python/fonts/
```


## 注意事项

- 字体文件可能较大，建议使用符号链接
- 修改字体后需要重启 MCP 服务器
- 某些字体可能需要额外的配置文件