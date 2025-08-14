# Dell 服务器信息批量采集爬虫

本项目使用 **Python + Playwright + Google Chrome 浏览器** 批量访问 Dell 官方支持页面，获取服务器的关键信息，包括：

- 服务标签（Service Tag）
- 快速服务码（Express Service Code）
- 出货日期
- 国家/地区
- 状态
- 当前计划（保修计划）
- 开始日期
- 结束日期

采集到的数据会保存为 CSV 文件，方便进一步处理或导入 CMDB 系统。

---

## 目录

- [运行环境](#运行环境)
- [安装步骤](#安装步骤)
- [准备数据](#准备数据)
- [运行爬虫](#运行爬虫)
- [输出结果](#输出结果)
- [注意事项](#注意事项)
- [常见问题](#常见问题)

---

## 运行环境

- **Python**：3.9 及以上
- **Google Chrome**：已安装桌面版
- **操作系统**：Windows / macOS / Linux（建议 Windows 运行）
- **虚拟环境**（venv）：推荐使用

---

## 安装步骤

1. **克隆项目或下载代码**
   ```bash
   git clone https://github.com/yourname/dell-server-crawler.git
   cd dell-server-crawler
   ```

2. **创建虚拟环境并激活**
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\activate

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **安装 Playwright（虽然本项目用系统 Chrome，但建议执行一次）**
   ```bash
   playwright install
   ```

---

## 准备数据

在项目根目录创建一个 `service_tags.txt` 文件，**每行一个 Service Tag**，示例：

```txt
3HYSL73
ABC1234
XYZ5678
```

---

## 运行爬虫

激活虚拟环境后，执行：

```bash
python crawler.py
```

程序会自动：

- 打开 Google Chrome（非无头模式）
- 访问 Dell 中文支持页面
- 点击“管理服务”按钮加载保修信息
- 提取所需字段
- 保存结果到 `dell_assets.csv`

---

## 输出结果

生成的 `dell_assets.csv` 包含以下列：

| 输入标签 | 服务标签 | 快速服务码 | 出货日期 | 国家/地区 | 状态 | 当前计划 | 开始日期 | 结束日期 |
|----------|----------|------------|----------|-----------|------|----------|----------|----------|
---

## 注意事项

1. **必须安装系统 Google Chrome**，Playwright 会调用系统 Chrome，而不是内置 Chromium。
2. 建议批量运行时添加代理或控制速率，避免 Dell 限流。
3. 页面加载较慢时，代码会自动刷新一次以防止卡在加载圈。
4. 中文页面已通过 `Accept-Language` 和 `locale="zh-CN"` 强制设置，不需要手动映射状态字段。

---

## 常见问题

### 1. 为什么爬虫打开的还是日文页面？
请确保：
- `URL` 已使用 `zh-cn` 版本
- 在 `browser.new_context` 中设置：
  ```python
  locale="zh-CN",
  extra_http_headers={"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.5"},
  ```
- 每次访问前清除 Cookie：`await context.clear_cookies()`

### 2. Playwright 提示找不到 Chrome？
请确保本地安装了最新版 Google Chrome，并且在命令行执行：
```bash
chrome --version
```
能正常显示版本。

### 3. 如何控制爬取速度？
可以修改 `crawler.py` 中：
```python
await page.wait_for_timeout(400 + random.randint(0, 600))
```
来调整每次访问的间隔时间。

---

## 作者

- **K3**
- 适用于 IDC 环境批量资产信息采集
