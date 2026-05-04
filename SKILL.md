---
name: hermes-stock-research
description: 基于同花顺问财API的A股深度研究报告自动生成器。支持财务、行业、估值、股东等多维度分析，自动生成专业级Markdown报告。当用户需要分析A股股票、生成研究报告、进行股票深度研究时使用此技能。
version: 1.0.0
author: imeiming
license: MIT
metadata:
  hermes:
    tags: [finance, stock, research, report, a-share, 同花顺, 问财, 深度研究]
    related_skills: [hithink-finance-query, hithink-business-query, hithink-industry-query, hithink-insresearch-query, hithink-management-query, hithink-sector-selector, mx-finance-data, mx-macro-data, mx-finance-search]
---

# Hermes Stock Research 📊

基于同花顺问财 OpenAPI 的A股深度研究报告自动生成工具。

## 功能特性

- **9大数据模块**：报告摘要、宏观行业、公司基本面、公司治理、机构持仓、估值分析、风险信息、资金流向、新闻资讯
- **36个查询维度**：全面覆盖股票分析所需数据
- **标准化输出**：自动生成Markdown格式专业研究报告
- **多数据源支持**：集成问财API + 东方财富妙想API

## 快速开始

### 一键生成报告

```bash
# 1. 采集数据（约60秒）
python3 scripts/collector.py --stock-code 002156 --stock-name 通富微电

# 2. 生成报告
python3 scripts/reporter.py --data-file output/002156_通富微电_*.json
```

### 示例

```bash
# 分析贵州茅台
python3 scripts/collector.py --stock-code 600519 --stock-name 贵州茅台
python3 scripts/reporter.py --data-file output/600519_贵州茅台_*.json

# 分析五粮液
python3 scripts/collector.py --stock-code 000858 --stock-name 五粮液
```

## 数据覆盖度

### 通过问财API获取的数据

| 模块 | 数据项 | 数据源技能 |
|------|--------|-----------|
| **1. 报告摘要** | 股价、市值、PE、PB、营收、利润、毛利率、ROE | hithink-finance-query |
| **2. 宏观与行业** | 行业分类、行业估值、资金流向、北向资金、竞争对手 | hithink-industry-query + hithink-sector-selector |
| **3. 公司基本面** | 主营构成、盈利能力、偿债能力、营运能力、现金流 | hithink-finance-query + hithink-business-query |
| **4. 公司治理** | 实控人、前十大股东、股东户数、股权质押、管理层 | hithink-management-query |
| **5. 机构持仓** | 机构持仓、研报评级、业绩预测、目标价 | hithink-insresearch-query |
| **6. 估值分析** | PE/PB/PS/股息率、同行可比公司对比 | hithink-finance-query |
| **7. 风险信息** | 诉讼处罚、解禁减持、重大合同 | hithink-management-query + hithink-business-query |
| **8. 资金流向** | 个股主力资金流向、大单净买入、特大单净买入 | hithink-sector-selector |
| **9. 新闻资讯** | 公司新闻、行业动态、宏观政策新闻 | news-search |

### 通过妙想API补充的数据

| 数据项 | 数据源技能 | 查询示例 |
|--------|-----------|---------|
| **技术面数据** | mx-finance-data | `"XX股票 近20日K线数据 MACD RSI KDJ"` |
| **历史估值区间** | mx-finance-data | `"XX股票 近5年市盈率PE最高最低平均"` |
| **行业规模数据** | mx-finance-data | `"XX行业市场规模 行业增速"` |
| **宏观数据** | mx-macro-data | `"中国GDP增速 近5年"` |
| **金融资讯** | mx-finance-search | `"XX股票 最新研报与公告"` |

## 报告结构

生成的报告遵循专业研究报告框架：

```
一、报告摘要（Executive Summary）
  - 核心投资逻辑（Key Investment Thesis）
  - 核心风险提示（Key Risk Factors）
  - 目标价位与周期（Target Price & Horizon）
  - 目标投资者画像（Target Investor Profile）

二、深度分析（In-Depth Analysis）
  1. 宏观环境与行业分析（国内和国际分开）
  2. 公司基本面分析
     - 公司概况与商业模式
     - 财务健康状况（盈利/营运/偿债/成长/现金流）
     - 公司治理与股东情况
     - 机构持仓与市场情绪
  3. 估值分析（绝对估值+相对估值）
  4. 技术面分析（日线/周线/趋势/形态/指标/量价）
  5. 风险与机会综合评估

三、明确的投资建议与操作策略
  - 入场策略/仓位建议/止损策略/目标价位

数据来源与时效性说明
```

## 环境要求

### 必需

- Python 3.8+
- 同花顺问财 OpenAPI Key（设置环境变量 `IWENCAI_API_KEY`）

### 可选（用于补充数据）

- 东方财富妙想 API Key（设置环境变量 `EM_API_KEY`）
- pandas, openpyxl（用于读取xlsx文件）

```bash
# 安装可选依赖
pip3 install pandas openpyxl httpx
```

## 配置

### 设置API Key

```bash
# 在 ~/.hermes/.env 中添加
IWENCAI_API_KEY=your_iwencai_api_key
EM_API_KEY=your_eastmoney_api_key
```

### 或通过环境变量

```bash
export IWENCAI_API_KEY="your_key"
export EM_API_KEY="your_key"
```

## 文件结构

```
hermes-stock-research/
├── SKILL.md                 # 技能说明文档
├── README.md                # 项目说明
├── LICENSE                  # MIT License
├── scripts/
│   ├── collector.py         # 数据采集脚本（9大模块，36个查询）
│   └── reporter.py          # 报告生成脚本
├── examples/
│   └── 600519_贵州茅台_report.md  # 示例报告
└── output/                  # 报告输出目录（git忽略）
```

## 常见问题

### 1. API Key 错误

确保 `IWENCAI_API_KEY` 环境变量已正确设置。

### 2. 数据采集失败

- 检查网络连接
- 确认API Key有效
- 查看错误日志

### 3. 报告生成失败

确保数据采集成功完成，JSON文件存在于output目录。

## 开发说明

### 添加新的数据模块

在 `collector.py` 中添加新的采集方法：

```python
def collect_new_module(self):
    """采集新模块数据"""
    section = {}
    section["new_data"] = query_iwencai("finance", 
        f"{self.stock_name} 新查询内容", limit="10")
    self._add_section("新模块名称", section)
```

在 `reporter.py` 中添加对应的报告生成逻辑。

### 修改报告模板

编辑 `reporter.py` 中的 `generate_report()` 函数，调整Markdown模板。

## License

MIT License - 可自由使用、修改和分发。

## 致谢

- 同花顺问财 OpenAPI
- 东方财富妙想API
- Hermes Agent Framework
