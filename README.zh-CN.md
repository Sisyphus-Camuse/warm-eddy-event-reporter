# 暖涡事件报告器

[English](README.md) | [中文](README.zh-CN.md)

这是一个小型、干净、适合开源展示的 AI 辅助物理海洋学 demo。

本项目会生成一份完全合成的海表温度异常场，使用简单透明的算法检测暖涡事件，并导出 PNG 图件和 Markdown 报告。

这个仓库可以放心公开：

- 不包含私有研究代码。
- 不包含真实 NetCDF 数据。
- 不包含论文材料。
- 不包含本机路径。
- 只包含由脚本生成的合成演示数据。

## 项目动机

海洋科学研究经常需要把网格数据转化为图件、事件摘要和论文式描述。这个 demo 展示了一个最小但完整的工作流：

1. 生成合成演示数据。
2. 检测暖核涡旋。
3. 导出图件和可复现 Markdown 报告。
4. 准备用于未来 LLM 科研摘要生成的 prompt 模板。

未来如果获得 token 支持，可以用于 AI 辅助解释海洋事件、生成图注、比较多日期演化过程，以及辅助撰写可复现科研报告。当前开源版本不会调用任何模型 API。

## 快速开始

需要 Python 3.10 或更高版本。不需要第三方依赖。

```powershell
python generate_sample.py
python detect_eddy.py
python plot_report.py
```

生成文件：

- `data/synthetic_warm_eddy_sst_anomaly.csv`
- `data/synthetic_warm_eddy_metadata.json`
- `outputs/synthetic_warm_eddy_detection.json`
- `outputs/synthetic_warm_eddy_map.png`
- `outputs/synthetic_warm_eddy_report.md`

## 运行测试

```powershell
python -m unittest discover -s tests
```

测试使用临时合成数据，不需要联网，也不需要安装第三方包。

## 脚本说明

### `generate_sample.py`

生成一份合成海表温度异常场。该场包含一个高斯形暖核涡旋、弱背景梯度、平滑波动信号和少量确定性噪声。

### `detect_eddy.py`

寻找最暖网格点，用边界网格估计背景值，提取峰值附近超过半峰值阈值的连通暖区，并输出近似中心、强度、半径和面积。

### `plot_report.py`

生成无需第三方依赖的 PNG 热力图和 Markdown 报告。PNG 写入逻辑只使用 Python 标准库。

### `prompts/summary_prompt.md`

提供未来 LLM 科研叙事使用的 prompt 模板。它只是设计材料，当前脚本不会调用 API。

## 示例研究故事

这份合成暖涡数据可以展示 AI copilot 如何帮助研究者：

- 用自然语言解释涡旋检测指标；
- 草拟图注；
- 比较不同日期的事件属性；
- 把可复现诊断结果转化为简短科研报告。

## 安全说明

本项目生成的所有文件都来自合成演示数据。除非你明确想公开，否则不要把私有数据或未发表研究结果混入这个仓库。

