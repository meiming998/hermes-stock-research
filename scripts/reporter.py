#!/usr/bin/env python3
"""
股票深度研究 - 报告生成脚本 v3

读取采集数据，按报告模版框架生成 Markdown 格式的深度研究报告。
自动提取关键字段，格式化为可读性强的报告。

v3 更新：集成行业估值、资金流向、新闻资讯数据

用法:
    python3 reporter.py --data-file output/600519_贵州茅台_20260504.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List


def safe_get(data: Dict, *keys, default=None):
    """安全获取嵌套字典数据"""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
    return current


def fmt_number(val, prefix="", suffix="", decimals=2) -> str:
    """格式化数字"""
    if val is None or val == "":
        return "N/A"
    try:
        num = float(val)
        if abs(num) >= 1e8:
            return f"{prefix}{num/1e8:.{decimals}f}亿{suffix}"
        elif abs(num) >= 1e4:
            return f"{prefix}{num/1e4:.{decimals}f}万{suffix}"
        else:
            return f"{prefix}{num:.{decimals}f}{suffix}"
    except:
        return str(val)


def fmt_pct(val) -> str:
    """格式化百分比"""
    if val is None or val == "":
        return "N/A"
    try:
        return f"{float(val):.2f}%"
    except:
        return str(val)


def get_field(item: Dict, *field_names, default="N/A") -> Any:
    """从数据项中获取字段，支持多个可能的字段名"""
    for name in field_names:
        val = item.get(name)
        if val is not None and val != "":
            return val
    return default


def generate_report(data: Dict) -> str:
    """根据采集数据生成研究报告"""
    meta = data.get("meta", {})
    sections = data.get("sections", {})
    stock_name = meta.get("stock_name", "未知")
    stock_code = meta.get("stock_code", "未知")
    collected_at = meta.get("collected_at", datetime.now().isoformat())
    
    # ========== 提取关键数据 ==========
    
    # 1. 报告摘要
    price_data = safe_get(sections, "1_报告摘要", "current_price", "datas", default=[{}])
    if isinstance(price_data, list) and price_data:
        price_data = price_data[0]
    else:
        price_data = {}
    
    fund_data = safe_get(sections, "1_报告摘要", "fundamentals_snapshot", "datas", default=[{}])
    if isinstance(fund_data, list) and fund_data:
        fund_data = fund_data[0]
    else:
        fund_data = {}
    
    current_price = get_field(price_data, "最新价", "收盘价[20260430]")
    pe_ttm = get_field(price_data, "市盈率(pe,ttm)[20260430]", "动态市盈率[20260430]")
    pb = get_field(price_data, "市净率[20260430]")
    total_mv = get_field(price_data, "总市值[20260430]")
    
    revenue = get_field(fund_data, "营业收入[20260331]")
    net_profit = get_field(fund_data, "归母净利润[20260331]")
    gross_margin = get_field(fund_data, "销售毛利率[20260331]")
    net_margin = get_field(fund_data, "销售净利率[20260331]")
    roe = get_field(fund_data, "净资产收益率[20260331]", "加权净资产收益率[20260331]")
    rev_growth = get_field(fund_data, "营业收入同比增长率[20260331]")
    profit_growth = get_field(fund_data, "归母净利润同比增长率[20260331]")
    
    # 2. 行业数据
    industry_data = safe_get(sections, "2_宏观与行业", "industry_basic", "datas", default=[{}])
    if isinstance(industry_data, list) and industry_data:
        industry_data = industry_data[0]
    else:
        industry_data = {}
    industry_name = get_field(industry_data, "所属同花顺行业", "所属同花顺二级行业")
    
    # 2.1 行业估值
    industry_val = safe_get(sections, "2_宏观与行业", "industry_valuation", "datas", default=[])
    
    # 2.2 行业资金流向
    sector_flow = safe_get(sections, "2_宏观与行业", "sector_capital_flow", "datas", default=[])
    
    # 2.3 北向资金
    northbound = safe_get(sections, "2_宏观与行业", "northbound_flow", "datas", default=[])
    
    # 3. 公司基本面
    biz_data = safe_get(sections, "3_公司基本面", "company_overview", "datas", default=[{}])
    if isinstance(biz_data, list) and biz_data:
        biz_data = biz_data[0]
    else:
        biz_data = {}
    main_product = get_field(biz_data, "主营产品")
    
    profit_detail = safe_get(sections, "3_公司基本面", "profitability", "datas", default=[{}])
    if isinstance(profit_detail, list) and profit_detail:
        profit_detail = profit_detail[0]
    else:
        profit_detail = {}
    
    cash_data = safe_get(sections, "3_公司基本面", "cash_flow", "datas", default=[{}])
    if isinstance(cash_data, list) and cash_data:
        cash_data = cash_data[0]
    else:
        cash_data = {}
    
    solvency_data = safe_get(sections, "3_公司基本面", "solvency", "datas", default=[{}])
    if isinstance(solvency_data, list) and solvency_data:
        solvency_data = solvency_data[0]
    else:
        solvency_data = {}
    
    efficiency_data = safe_get(sections, "3_公司基本面", "efficiency", "datas", default=[{}])
    if isinstance(efficiency_data, list) and efficiency_data:
        efficiency_data = efficiency_data[0]
    else:
        efficiency_data = {}
    
    # 4. 股东数据
    controller_data = safe_get(sections, "4_公司治理与股东", "controller", "datas", default=[{}])
    if isinstance(controller_data, list) and controller_data:
        controller_data = controller_data[0]
    else:
        controller_data = {}
    
    top10_data = safe_get(sections, "4_公司治理与股东", "top10_shareholders", "datas", default=[])
    
    # 5. 机构数据
    analyst_data = safe_get(sections, "5_机构持仓与市场情绪", "analyst_ratings", "datas", default=[])
    target_data = safe_get(sections, "5_机构持仓与市场情绪", "target_price", "datas", default=[])
    
    # 6. 估值数据
    valuation_data = safe_get(sections, "6_估值分析", "current_valuation", "datas", default=[{}])
    if isinstance(valuation_data, list) and valuation_data:
        valuation_data = valuation_data[0]
    else:
        valuation_data = {}
    
    peer_data = safe_get(sections, "6_估值分析", "peer_comparison", "datas", default=[])
    
    # 7. 风险数据
    litigation_data = safe_get(sections, "7_重大事件与风险", "litigation", "datas", default=[{}])
    if isinstance(litigation_data, list) and litigation_data:
        litigation_data = litigation_data[0]
    else:
        litigation_data = {}
    
    lockup_data = safe_get(sections, "7_重大事件与风险", "lockup", "datas", default=[{}])
    if isinstance(lockup_data, list) and lockup_data:
        lockup_data = lockup_data[0]
    else:
        lockup_data = {}
    
    # 8. 资金流向
    stock_flow = safe_get(sections, "8_资金流向", "stock_capital_flow", "datas", default=[{}])
    if isinstance(stock_flow, list) and stock_flow:
        stock_flow = stock_flow[0]
    else:
        stock_flow = {}
    
    big_order = safe_get(sections, "8_资金流向", "big_order_flow", "datas", default=[{}])
    if isinstance(big_order, list) and big_order:
        big_order = big_order[0]
    else:
        big_order = {}
    
    # 9. 新闻资讯
    company_news = safe_get(sections, "9_新闻资讯", "company_news", "datas", default=[])
    industry_news = safe_get(sections, "9_新闻资讯", "industry_news", "datas", default=[])
    macro_news = safe_get(sections, "9_新闻资讯", "macro_news", "datas", default=[])
    
    # ========== 生成报告 ==========
    
    report = f"""# {stock_name}({stock_code}) 深度研究报告

> 📅 报告生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}
> 📊 数据采集时间：{collected_at}
> 📖 数据来源：同花顺问财 OpenAPI

---

## 一、报告摘要（Executive Summary）

### 核心投资逻辑（Key Investment Thesis）

| 指标 | 数值 |
|------|------|
| 最新股价 | {fmt_number(current_price, "¥")} |
| 总市值 | {fmt_number(total_mv)} |
| 市盈率(PE-TTM) | {fmt_number(pe_ttm, decimals=2)} |
| 市净率(PB) | {fmt_number(pb, decimals=2)} |
| 营业收入 | {fmt_number(revenue)} |
| 归母净利润 | {fmt_number(net_profit)} |
| 毛利率 | {fmt_pct(gross_margin)} |
| 净利率 | {fmt_pct(net_margin)} |
| ROE | {fmt_pct(roe)} |
| 营收增长率 | {fmt_pct(rev_growth)} |
| 净利润增长率 | {fmt_pct(profit_growth)} |

### 核心风险提示（Key Risk Factors）
> ⚠️ **需关注的风险：**
> - 宏观经济下行风险
> - 行业竞争加剧风险
> - 公司经营不确定性
> - 估值回调风险
> - 政策变动风险

### 目标价位与周期（Target Price & Horizon）
"""
    
    # 添加目标价数据
    if target_data:
        report += "\n| 机构 | 目标价 | 评级 | 日期 |\n|------|--------|------|------|\n"
        for item in target_data[:5]:
            inst = get_field(item, "研究机构", default="N/A")
            tp = get_field(item, "目标价", default="N/A")
            rating = get_field(item, "原始评级", default="N/A")
            date = get_field(item, "公告日期", default="N/A")
            report += f"| {inst} | ¥{tp} | {rating} | {date} |\n"
    else:
        report += "\n> 📊 [目标价数据待补充]\n"
    
    report += f"""
> 📌 **投资周期建议：** 需根据个股特性确定（短期交易/中期波段/长期价值投资）

### 目标投资者画像（Target Investor Profile）
> 📌 需根据公司特性确定适合的投资者类型

---

## 二、深度分析（In-Depth Analysis）

### 1. 宏观环境与行业分析

#### 国内宏观环境
"""
    
    # 添加宏观新闻
    if macro_news:
        report += "\n**最新宏观动态：**\n"
        for item in macro_news[:3]:
            title = get_field(item, "title", default="")
            summary = get_field(item, "summary", default="")
            if title:
                report += f"- **{title}**\n"
                if summary:
                    report += f"  {summary[:100]}...\n"
    else:
        report += "\n> 📌 **当前宏观背景：** 需结合最新宏观经济数据填充\n"
    
    report += f"""
#### 国际宏观环境
> 📌 **国际环境影响：** 需结合国际经济形势填充

#### 行业基本信息
- **所属行业：** {industry_name}

#### 行业估值水平
"""
    
    # 添加行业估值数据
    if industry_val:
        report += "\n| 指标 | 数值 |\n|------|------|\n"
        for item in industry_val[:3]:
            for k, v in item.items():
                if v and "股票" not in k and "最新" not in k:
                    report += f"| {k} | {v} |\n"
    else:
        report += "\n> 📊 [行业估值数据待补充]\n"
    
    report += f"""
#### 行业资金流向
"""
    
    # 添加行业资金流向
    if sector_flow:
        report += "\n| 指标 | 数值 |\n|------|------|\n"
        for item in sector_flow[:3]:
            for k, v in item.items():
                if v and "股票" not in k and "最新" not in k:
                    report += f"| {k} | {v} |\n"
    else:
        report += "\n> 📊 [行业资金流向数据待补充]\n"
    
    report += f"""
#### 北向资金动态
"""
    
    # 添加北向资金
    if northbound:
        report += "\n| 指标 | 数值 |\n|------|------|\n"
        for item in northbound[:3]:
            for k, v in item.items():
                if v and "股票" not in k and "最新" not in k:
                    report += f"| {k} | {v} |\n"
    else:
        report += "\n> 📊 [北向资金数据待补充]\n"
    
    report += f"""
#### 行业规模与增速
> 📌 需补充行业市场规模、历史复合增长率及未来3-5年预测增速

#### 政策导向
> 📌 需分析与公司相关的国家层面产业政策、监管环境变化

#### 产业链地位
> 📌 需分析公司在产业链中的位置（上游/中游/下游），议价能力

#### 竞争格局分析
"""
    
    # 添加竞争对手数据
    competitive_data = safe_get(sections, "2_宏观与行业", "competitive_landscape", "datas", default=[])
    if competitive_data:
        report += "\n| 股票代码 | 市场占比 |\n|----------|----------|\n"
        for item in competitive_data[:5]:
            code = get_field(item, "股票代码", default="N/A")
            share = get_field(item, "市场占比", default="N/A")
            report += f"| {code} | {share} |\n"
    else:
        report += "\n> 📊 [竞争格局数据待补充]\n"
    
    report += f"""
---

### 2. 公司基本面分析

#### 公司概况与商业模式
- **主营产品：** {main_product}

#### 财务健康状况深度剖析

**盈利能力（最新期）：**
| 指标 | 数值 |
|------|------|
| 营业收入 | {fmt_number(revenue)} |
| 归母净利润 | {fmt_number(net_profit)} |
| 销售毛利率 | {fmt_pct(gross_margin)} |
| 销售净利率 | {fmt_pct(net_margin)} |
| 净资产收益率(ROE) | {fmt_pct(roe)} |
| 总资产报酬率(ROA) | {fmt_pct(get_field(profit_detail, '总资产报酬率[20260331]'))} |
| 营收增长率 | {fmt_pct(rev_growth)} |
| 净利润增长率 | {fmt_pct(profit_growth)} |

**偿债能力：**
| 指标 | 数值 |
|------|------|
| 资产负债率 | {fmt_pct(get_field(solvency_data, '资产负债率[20260331]'))} |
| 流动比率 | {get_field(solvency_data, '流动比率[20260331]')} |
| 速动比率 | {get_field(solvency_data, '速动比率[20260331]')} |

**营运能力：**
| 指标 | 数值 |
|------|------|
| 应收账款周转率 | {get_field(efficiency_data, '应收账款周转率[20260331]')} |
| 存货周转率 | {get_field(efficiency_data, '存货周转率[20260331]')} |
| 总资产周转率 | {get_field(efficiency_data, '总资产周转率[20260331]')} |

**现金流量：**
| 指标 | 数值 |
|------|------|
| 经营活动现金流净额 | {fmt_number(get_field(cash_data, '经营活动产生的现金流量净额[20260331]'))} |
| 企业自由现金流 | {fmt_number(get_field(cash_data, '企业自由现金流量[20260331]'))} |
| 总现金 | {fmt_number(get_field(cash_data, '总现金[20260331]'))} |

> 📌 **盈利质量分析：** 经营现金流/净利润 = {fmt_number(get_field(cash_data, '经营活动产生的现金流量净额[20260331]'))} / {fmt_number(net_profit)}

#### 公司治理与股东情况

**实际控制人：**
- **实际控制人：** {get_field(controller_data, '实际控制人')}
- **控股股东：** {get_field(controller_data, '股东名称')}
- **持股比例：** {fmt_pct(get_field(controller_data, '持股占流通股比例[20260331]'))}
- **持股市值：** {fmt_number(get_field(controller_data, '持股市值[20260331]'))}

**前十大股东：**
"""
    
    # 添加前十大股东
    if top10_data:
        report += "\n| 股东名称 | 持股比例 | 持股数量 |\n|----------|----------|----------|\n"
        for item in top10_data[:10]:
            name = get_field(item, "大股东名称", "股东名称", default="N/A")
            ratio = get_field(item, "持股比例[20260331]", "持股占流通股比例[20260331]", default="N/A")
            shares = get_field(item, "持股数量[20260331]", default="N/A")
            if shares != "N/A":
                shares = fmt_number(shares)
            report += f"| {name} | {fmt_pct(ratio) if ratio != 'N/A' else ratio} | {shares} |\n"
    else:
        report += "\n> 📊 [股东数据待补充]\n"
    
    report += f"""
#### 机构持仓与市场情绪

**分析师评级汇总：**
"""
    
    # 添加分析师评级
    if analyst_data:
        report += "\n| 机构 | 评级 | 研报标题 | 日期 |\n|------|------|----------|------|\n"
        for item in analyst_data[:5]:
            inst = get_field(item, "研究机构", default="N/A")
            rating = get_field(item, "原始评级", default="N/A")
            title = get_field(item, "研报", default="N/A")
            date = get_field(item, "公告日期", default="N/A")
            if len(str(title)) > 20:
                title = str(title)[:20] + "..."
            report += f"| {inst} | {rating} | {title} | {date} |\n"
    else:
        report += "\n> 📊 [分析师评级数据待补充]\n"
    
    report += f"""
---

### 3. 估值分析

**当前估值水平：**
| 指标 | 数值 |
|------|------|
| 市盈率(PE-TTM) | {fmt_number(pe_ttm, decimals=2)} |
| 动态市盈率 | {fmt_number(get_field(valuation_data, '动态市盈率[20260430]'), decimals=2)} |
| 市净率(PB) | {fmt_number(pb, decimals=2)} |
| 市销率(PS) | {fmt_number(get_field(valuation_data, '市销率[20260430]'), decimals=2)} |
| 股息率 | {fmt_pct(get_field(valuation_data, '股息率[20260430]'))} |

**同行可比公司对比：**
"""
    
    # 添加同行对比
    if peer_data:
        report += "\n| 股票代码 | 股票简称 | 最新价 | 涨跌幅 |\n|----------|----------|--------|--------|\n"
        for item in peer_data[:8]:
            code = get_field(item, "股票代码", default="N/A")
            name = get_field(item, "股票简称", default="N/A")
            price = get_field(item, "最新价", default="N/A")
            change = get_field(item, "最新涨跌幅", default="N/A")
            report += f"| {code} | {name} | ¥{price} | {fmt_pct(change)} |\n"
    else:
        report += "\n> 📊 [同行对比数据待补充]\n"
    
    report += f"""
**估值结论：**
> 📌 需综合判断：公司当前股价处于低估/合理/高估状态

---

### 4. 技术面分析

> ⚠️ **技术面数据需要额外数据源支持：**
> - 日线/周线K线数据
> - MACD、RSI、KDJ等技术指标
> - 成交量与资金流向数据
> - 支撑位与阻力位分析

---

### 5. 资金流向分析

**个股资金流向：**
"""
    
    # 添加个股资金流向
    if stock_flow and isinstance(stock_flow, dict):
        report += "\n| 指标 | 数值 |\n|------|------|\n"
        for k, v in stock_flow.items():
            if v and "股票" not in k and "最新" not in k:
                report += f"| {k} | {v} |\n"
    elif stock_flow and isinstance(stock_flow, list) and stock_flow:
        report += "\n| 指标 | 数值 |\n|------|------|\n"
        for k, v in stock_flow[0].items():
            if v and "股票" not in k and "最新" not in k:
                report += f"| {k} | {v} |\n"
    else:
        report += "\n> 📊 [个股资金流向数据待补充]\n"
    
    report += f"""
**大单资金动向：**
"""
    
    # 添加大单资金
    if big_order and isinstance(big_order, dict):
        report += "\n| 指标 | 数值 |\n|------|------|\n"
        for k, v in big_order.items():
            if v and "股票" not in k and "最新" not in k:
                report += f"| {k} | {v} |\n"
    elif big_order and isinstance(big_order, list) and big_order:
        report += "\n| 指标 | 数值 |\n|------|------|\n"
        for k, v in big_order[0].items():
            if v and "股票" not in k and "最新" not in k:
                report += f"| {k} | {v} |\n"
    else:
        report += "\n> 📊 [大单资金数据待补充]\n"
    
    report += f"""
---

### 6. 风险与机会综合评估

#### 风险矩阵

**公司特有风险：**
"""
    
    # 添加风险数据
    has_litigation = get_field(litigation_data, "诉讼", "处罚", "违规", default=None)
    if has_litigation:
        report += f"- {has_litigation}\n"
    else:
        report += "- 暂无重大诉讼/处罚记录\n"
    
    has_lockup = get_field(lockup_data, "限售解禁", "减持", default=None)
    if has_lockup:
        report += f"- {has_lockup}\n"
    else:
        report += "- 暂无大规模解禁减持压力\n"
    
    report += f"""
#### 潜在催化剂（Catalysts）
> 📌 **未来6-12个月潜在催化剂：**
> - 新产品发布/技术突破
> - 重大合同签订
> - 业绩超预期
> - 行业政策利好
> - 资产重组

---

### 7. 新闻资讯

#### 公司最新动态
"""
    
    # 添加公司新闻
    if company_news:
        for item in company_news[:5]:
            title = get_field(item, "title", default="")
            summary = get_field(item, "summary", default="")
            url = get_field(item, "url", default="")
            if title:
                report += f"\n**{title}**\n"
                if summary:
                    report += f"{summary[:150]}...\n"
                if url:
                    report += f"🔗 {url}\n"
    else:
        report += "\n> 📊 [公司新闻待补充]\n"
    
    report += f"""
#### 行业动态
"""
    
    # 添加行业新闻
    if industry_news:
        for item in industry_news[:3]:
            title = get_field(item, "title", default="")
            summary = get_field(item, "summary", default="")
            if title:
                report += f"\n**{title}**\n"
                if summary:
                    report += f"{summary[:150]}...\n"
    else:
        report += "\n> 📊 [行业新闻待补充]\n"
    
    report += f"""
---

## 三、明确的投资建议与操作策略

### 投资评级
> 📌 **需根据分析结论确定：** 强烈买入 / 增持 / 中性 / 减持 / 卖出

### 操作策略

**入场策略：** 📌 需明确理想买入价位或触发条件
**仓位建议：** 📌 需建议总资金的配置比例
**止损策略：** 📌 需设定明确的止损位
**目标价位：** 📌 需说明对应市盈率或其他估值基准

---

## 数据来源与时效性

| 数据类型 | 来源 | 时效性 |
|---------|------|--------|
| 财务数据 | 同花顺问财 | 最新财报 |
| 行业数据 | 同花顺问财 | 最新统计 |
| 行业估值 | 同花顺问财 | 实时 |
| 资金流向 | 同花顺问财 | 实时 |
| 机构评级 | 同花顺问财 | 近3个月 |
| 股东数据 | 同花顺问财 | 最新季报 |
| 新闻资讯 | 同花顺问财 | 实时 |

> **免责声明：** 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
> 报告中的数据来源于同花顺问财 OpenAPI，数据准确性以官方披露为准。
"""
    
    return report


def main():
    parser = argparse.ArgumentParser(description="股票深度研究 - 报告生成脚本 v3")
    parser.add_argument("--data-file", "-d", required=True, help="采集数据JSON文件路径")
    parser.add_argument("--output", "-o", default=None, help="输出报告文件路径")
    
    args = parser.parse_args()
    
    with open(args.data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    report = generate_report(data)
    
    if args.output:
        output_path = args.output
    else:
        base = os.path.splitext(args.data_file)[0]
        output_path = f"{base}_report.md"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ 报告已生成: {output_path}")
    print(f"📄 报告长度: {len(report)} 字符")


if __name__ == "__main__":
    main()
