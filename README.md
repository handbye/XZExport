# 先知社区文章导出工具

一个用于将阿里云先知社区（xz.aliyun.com）文章导出为Markdown格式的Python工具，支持命令行和图形界面两种使用方式。

## 功能特点

- 📄 将先知社区文章完整导出为Markdown格式
- 🖼️ 自动下载并本地化文章中的图片
- 🖥️ 支持命令行和图形界面两种操作方式
- 🛡️ 绕过网站WAF保护机制
- 🔄 支持动态内容加载
- 📁 自动创建图片目录并管理图片文件
- 📋 保留文章原始格式和结构
- 🎯 支持多种文章标题和内容提取方式

## 安装依赖

确保已安装Python 3.6+，然后安装所需依赖：

```bash
pip install -r requirements.txt
```

如果没有requirements.txt文件，可以手动安装：

```bash
pip install requests beautifulsoup4 markdownify selenium webdriver-manager
```

## 使用方法

### 1. 命令行方式

```bash
python export_xz.py <文章URL> -o <输出目录>
```

#### 示例

```bash
python export_xz.py https://xz.aliyun.com/t/12345 -o ./output
```

### 2. 图形界面方式

运行GUI应用程序：

```bash
python gui_app.py
```

在界面中：
1. 输入文章URL
2. 选择输出目录（默认当前目录）
3. 点击"Export Article"按钮开始导出

## 项目结构

```
XZExport/
├── export_xz.py     # 核心导出功能模块
├── gui_app.py       # 图形界面程序
├── build_app.sh     # 应用程序打包脚本
├── requirements.txt # 依赖库列表
└── README.md        # 项目说明文档
```

## 构建独立应用程序

如果需要创建独立可执行文件（无需Python环境），可以使用提供的构建脚本：

```bash
chmod +x build_app.sh
./build_app.sh
```

构建完成后，独立应用程序将位于 `dist/XZExporter.app` 目录中（macOS）。

**构建依赖**: 需要安装PyInstaller

```bash
pip install pyinstaller
```

## 技术实现

- **Web 驱动**: Selenium + ChromeDriver (headless模式)
- **HTML解析**: BeautifulSoup4
- **HTML转Markdown**: markdownify
- **网络请求**: requests
- **GUI框架**: Tkinter
- **图片处理**: 自动下载并保存到images目录

## 注意事项

1. 确保已安装Chrome浏览器
2. 首次运行时会自动下载ChromeDriver
3. 文章URL必须以`https://xz.aliyun.com/`开头
4. 导出过程中请勿关闭命令行窗口或GUI界面
5. 图片将保存在输出目录下的`images`子目录中
6. 大型文章可能需要较长处理时间

## 常见问题

### Q: 导出失败提示"Error initializing driver"
A: 请确保Chrome浏览器已正确安装，或检查网络连接是否正常。

### Q: 文章内容为空或不完整
A: 可能是网站结构更新导致选择器失效，请检查最新的网页结构。

### Q: 图片下载失败
A: 检查网络连接，或确认图片URL是否可访问。

## License

MIT License

## 更新日志

### v1.0
- 初始版本发布
- 支持命令行和GUI两种方式
- 实现文章内容和图片导出功能
- 支持动态内容加载和WAF绕过