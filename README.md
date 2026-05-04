# Hermes Stock Research 📊

基于同花顺问财API的A股深度研究报告自动生成器。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Hermes](https://img.shields.io/badge/Hermes-Agent-orange.svg)](https://github.com/NousResearch/hermes-agent)

## ✨ 功能特性

- 🚀 **一键生成**：输入股票代码和名称，自动采集数据并生成报告
- 📊 **9大模块**：覆盖财务、行业、估值、股东、机构、风险、资金、新闻
- 📈 **36个维度**：全方位数据分析
- 📝 **专业输出**：标准化Markdown格式研究报告
- 🔌 **多数据源**：集成同花顺问财 + 东方财富妙想API

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/imeiming/hermes-stock-research.git
cd hermes-stock-research
pip install pandas openpyxl httpx
```

### 配置API Key

```bash
export IWENCAI_API_KEY="your_iwencai_api_key"
export EM_API_KEY="your_eastmoney_api_key"  # 可选
```

### 生成报告

```bash
# 采集数据
python3 scripts/collector.py --stock-code 002156 --stock-name 通富微电

# 生成报告
python3 scripts/reporter.py --data-file output/002156_通富微电_*.json
```

## 📊 数据覆盖

| 模块 | 数据项 | 来源 |
|------|--------|------|
| 报告摘要 | 股价、市值、PE、PB、营收、利润 | hithink-finance-query |
| 宏观行业 | 行业分类、估值、资金流向、北向资金 | hithink-industry-query |
| 公司基本面 | 主营构成、盈利、偿债、营运、现金流 | hithink-business-query |
| 公司治理 | 实控人、股东、质押、管理层 | hithink-management-query |
| 机构持仓 | 机构持仓、研报评级、目标价 | hithink-insresearch-query |
| 估值分析 | PE/PB/PS、同行对比 | hithink-finance-query |
| 风险信息 | 诉讼、减持、重大合同 | hithink-management-query |
| 资金流向 | 主力资金、大单净买入 | hithink-sector-selector |
| 新闻资讯 | 公司新闻、行业动态 | news-search |

## 📝 报告示例

生成的报告包含：

- **报告摘要**：核心投资逻辑、风险提示、目标价位
- **深度分析**：宏观行业、基本面、估值、技术面、风险机会
- **投资建议**：入场策略、仓位建议、止损目标

详见 [examples/](examples/) 目录。

## 🔧 作为Hermes Agent技能使用

此项目可作为 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 的技能使用：

```bash
# 复制到Hermes技能目录
cp -r . ~/.hermes/skills/finance/hermes-stock-research

# 在Hermes中使用
hermes -q "分析通富微电"
```

## 📚 相关项目

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) - AI Agent框架
- [同花顺问财](https://www.iwencai.com/) - 金融数据API
- [东方财富妙想](https://www.eastmoney.com/) - 金融数据API

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)

## ⚠️ 免责声明

本工具生成的报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
