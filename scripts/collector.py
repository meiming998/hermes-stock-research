#!/usr/bin/env python3
"""
股票深度研究 - 数据采集脚本 v2

整合同花顺问财 OpenAPI 多个技能，为专业级研究报告提供数据支撑。
严格遵循报告模版框架，自动采集所有可获取的数据。

技能整合：
- hithink-finance-query: 财务数据
- hithink-business-query: 经营数据
- hithink-industry-query: 行业数据
- hithink-insresearch-query: 机构研究
- hithink-management-query: 股东股本
- hithink-sector-selector: 行业估值+资金流向
- news-search: 新闻资讯

用法:
    python3 collector.py --stock-code 600519 --stock-name 贵州茅台
    python3 collector.py --stock-code 000858 --stock-name 五粮液 --output-dir /tmp/reports
"""

import argparse
import json
import os
import secrets
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# ============================================================================
# 配置
# ============================================================================

IWENCAI_API_URL = "https://openapi.iwencai.com/v1/query2data"
NEWS_API_URL = "https://openapi.iwencai.com/v1/comprehensive/search"

SKILLS = {
    "finance": {"skill_id": "hithink-finance-query", "version": "1.0.0"},
    "business": {"skill_id": "hithink-business-query", "version": "1.0.0"},
    "industry": {"skill_id": "hithink-industry-query", "version": "1.0.0"},
    "insresearch": {"skill_id": "hithink-insresearch-query", "version": "1.0.0"},
    "management": {"skill_id": "hithink-management-query", "version": "1.0.0"},
    "sector": {"skill_id": "hithink-sector-selector", "version": "1.0.0"},
}

# ============================================================================
# API 调用
# ============================================================================

def generate_trace_id() -> str:
    return secrets.token_hex(32)

def get_api_key() -> str:
    key = os.environ.get("IWENCAI_API_KEY", "")
    if not key:
        print("错误: IWENCAI_API_KEY 环境变量未设置", file=sys.stderr)
        sys.exit(1)
    return key

def query_iwencai(skill_type: str, query: str, limit: str = "10", page: str = "1") -> Dict:
    """调用问财 OpenAPI (数据查询)"""
    api_key = get_api_key()
    skill = SKILLS[skill_type]
    trace_id = generate_trace_id()
    
    payload = {
        "query": query,
        "page": page,
        "limit": limit,
        "is_cache": "1",
        "expand_index": "true",
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Claw-Call-Type": "normal",
        "X-Claw-Skill-Id": skill["skill_id"],
        "X-Claw-Skill-Version": skill["version"],
        "X-Claw-Plugin-Id": "none",
        "X-Claw-Plugin-Version": "none",
        "X-Claw-Trace-Id": trace_id,
    }
    
    request = urllib.request.Request(
        IWENCAI_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return {
                "success": True,
                "query": query,
                "datas": result.get("datas", []),
                "code_count": result.get("code_count", 0),
                "trace_id": trace_id,
            }
    except Exception as e:
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "trace_id": trace_id,
        }

def query_news(query: str) -> Dict:
    """调用问财新闻搜索 API"""
    api_key = get_api_key()
    trace_id = generate_trace_id()
    
    payload = {
        "channels": ["news"],
        "app_id": "AIME_SKILL",
        "query": query,
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Claw-Call-Type": "normal",
        "X-Claw-Skill-Id": "news-search",
        "X-Claw-Skill-Version": "1.0.0",
        "X-Claw-Plugin-Id": "none",
        "X-Claw-Plugin-Version": "none",
        "X-Claw-Trace-Id": trace_id,
    }
    
    request = urllib.request.Request(
        NEWS_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return {
                "success": True,
                "query": query,
                "datas": result.get("data", []),
                "trace_id": trace_id,
            }
    except Exception as e:
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "trace_id": trace_id,
        }

# ============================================================================
# 数据采集模块
# ============================================================================

class StockResearchCollector:
    """股票深度研究数据采集器"""
    
    def __init__(self, stock_code: str, stock_name: str):
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.data = {
            "meta": {
                "stock_code": stock_code,
                "stock_name": stock_name,
                "collected_at": datetime.now().isoformat(),
                "collector_version": "2.0.0",
            },
            "sections": {}
        }
    
    def _add_section(self, section_name: str, data: Dict):
        """添加数据段"""
        self.data["sections"][section_name] = data
    
    # ----------------------------------------------------------------
    # 1. 报告摘要相关数据
    # ----------------------------------------------------------------
    def collect_summary_data(self):
        """采集报告摘要所需的核心数据"""
        print(f"📊 采集报告摘要数据...")
        section = {}
        
        section["current_price"] = query_iwencai("finance", 
            f"{self.stock_name} 最新股价 涨跌幅 市盈率 市净率", limit="1")
        
        section["fundamentals_snapshot"] = query_iwencai("finance",
            f"{self.stock_name} 营业收入 净利润 毛利率 净利率 ROE", limit="1")
        
        self._add_section("1_报告摘要", section)
    
    # ----------------------------------------------------------------
    # 2. 宏观与行业分析
    # ----------------------------------------------------------------
    def collect_macro_industry_data(self):
        """采集宏观与行业分析数据"""
        print(f"🌍 采集宏观与行业数据...")
        section = {}
        
        # 行业基本信息
        section["industry_basic"] = query_iwencai("industry",
            f"{self.stock_name} 所属行业 行业地位", limit="5")
        
        # 行业规模与增速
        section["industry_scale"] = query_iwencai("industry",
            f"{self.stock_name}所属行业 市场规模 行业增速", limit="5")
        
        # 行业竞争格局
        section["competitive_landscape"] = query_iwencai("industry",
            f"{self.stock_name} 行业竞争对手 市场份额", limit="10")
        
        # 行业政策
        section["industry_policy"] = query_iwencai("industry",
            f"{self.stock_name}所属行业 产业政策 监管", limit="5")
        
        # 行业估值（使用 sector-selector）
        section["industry_valuation"] = query_iwencai("sector",
            f"{self.stock_name}所属行业 行业PE 行业PB 估值分位", limit="5")
        
        # 行业资金流向（使用 sector-selector）
        section["sector_capital_flow"] = query_iwencai("sector",
            f"{self.stock_name}所属行业 资金流向 主力资金净流入", limit="5")
        
        # 北向资金流向
        section["northbound_flow"] = query_iwencai("sector",
            f"{self.stock_name}所属行业 北向资金 净买入", limit="5")
        
        self._add_section("2_宏观与行业", section)
    
    # ----------------------------------------------------------------
    # 3. 公司基本面分析
    # ----------------------------------------------------------------
    def collect_fundamental_data(self):
        """采集公司基本面数据"""
        print(f"📈 采集公司基本面数据...")
        section = {}
        
        # --- 公司概况 ---
        section["company_overview"] = query_iwencai("business",
            f"{self.stock_name} 主营业务 核心产品", limit="5")
        
        # 主营构成
        section["revenue_composition"] = query_iwencai("business",
            f"{self.stock_name} 主营构成 收入构成", limit="10")
        
        # --- 财务数据 ---
        section["profitability"] = query_iwencai("finance",
            f"{self.stock_name} 营业收入 净利润 毛利率 净利率 ROE ROA 最新", limit="5")
        
        section["growth"] = query_iwencai("finance",
            f"{self.stock_name} 营业收入增长率 净利润增长率 近三年", limit="5")
        
        section["solvency"] = query_iwencai("finance",
            f"{self.stock_name} 资产负债率 流动比率 速动比率", limit="1")
        
        section["efficiency"] = query_iwencai("finance",
            f"{self.stock_name} 应收账款周转率 存货周转率 总资产周转率", limit="1")
        
        section["cash_flow"] = query_iwencai("finance",
            f"{self.stock_name} 经营现金流 自由现金流 现金流量", limit="1")
        
        self._add_section("3_公司基本面", section)
    
    # ----------------------------------------------------------------
    # 4. 公司治理与股东
    # ----------------------------------------------------------------
    def collect_governance_data(self):
        """采集公司治理与股东数据"""
        print(f"👔 采集公司治理数据...")
        section = {}
        
        section["controller"] = query_iwencai("management",
            f"{self.stock_name} 实际控制人 控股股东", limit="5")
        
        section["top10_shareholders"] = query_iwencai("management",
            f"{self.stock_name} 前十大股东 持股比例", limit="10")
        
        section["shareholder_count"] = query_iwencai("management",
            f"{self.stock_name} 股东户数 变化趋势", limit="5")
        
        section["pledge"] = query_iwencai("management",
            f"{self.stock_name} 股权质押", limit="5")
        
        section["management_team"] = query_iwencai("management",
            f"{self.stock_name} 高管 董事会 管理层", limit="10")
        
        self._add_section("4_公司治理与股东", section)
    
    # ----------------------------------------------------------------
    # 5. 机构持仓与市场情绪
    # ----------------------------------------------------------------
    def collect_institutional_data(self):
        """采集机构持仓与分析师评级数据"""
        print(f"🏦 采集机构持仓数据...")
        section = {}
        
        section["institutional_holdings"] = query_iwencai("management",
            f"{self.stock_name} 机构持仓 基金持仓 持股比例", limit="10")
        
        section["analyst_ratings"] = query_iwencai("insresearch",
            f"{self.stock_name} 研报评级 券商评级", limit="10")
        
        section["earnings_forecast"] = query_iwencai("insresearch",
            f"{self.stock_name} 业绩预测 盈利预测", limit="10")
        
        section["target_price"] = query_iwencai("insresearch",
            f"{self.stock_name} 目标价 研报目标价", limit="10")
        
        self._add_section("5_机构持仓与市场情绪", section)
    
    # ----------------------------------------------------------------
    # 6. 估值分析
    # ----------------------------------------------------------------
    def collect_valuation_data(self):
        """采集估值分析数据"""
        print(f"💰 采集估值数据...")
        section = {}
        
        section["current_valuation"] = query_iwencai("finance",
            f"{self.stock_name} 市盈率PE 市净率PB 市销率PS 股息率", limit="1")
        
        section["historical_valuation"] = query_iwencai("finance",
            f"{self.stock_name} 历史市盈率 估值区间 近5年", limit="5")
        
        section["peer_comparison"] = query_iwencai("finance",
            f"{self.stock_name} 同行业 市盈率 市净率 对比", limit="10")
        
        self._add_section("6_估值分析", section)
    
    # ----------------------------------------------------------------
    # 7. 重大事件与风险
    # ----------------------------------------------------------------
    def collect_risk_data(self):
        """采集风险与机会数据"""
        print(f"⚠️ 采集风险与机会数据...")
        section = {}
        
        section["litigation"] = query_iwencai("management",
            f"{self.stock_name} 诉讼 处罚 违规", limit="5")
        
        section["lockup"] = query_iwencai("management",
            f"{self.stock_name} 限售解禁 减持", limit="5")
        
        section["major_contracts"] = query_iwencai("business",
            f"{self.stock_name} 重大合同 项目 订单", limit="5")
        
        self._add_section("7_重大事件与风险", section)
    
    # ----------------------------------------------------------------
    # 8. 资金流向（个股）
    # ----------------------------------------------------------------
    def collect_capital_flow_data(self):
        """采集个股资金流向数据"""
        print(f"💸 采集资金流向数据...")
        section = {}
        
        # 个股资金流向
        section["stock_capital_flow"] = query_iwencai("sector",
            f"{self.stock_name} 主力资金净流入 资金流向", limit="5")
        
        # 大单资金
        section["big_order_flow"] = query_iwencai("sector",
            f"{self.stock_name} 大单净流入 超大单", limit="5")
        
        self._add_section("8_资金流向", section)
    
    # ----------------------------------------------------------------
    # 9. 新闻资讯
    # ----------------------------------------------------------------
    def collect_news_data(self):
        """采集新闻资讯数据"""
        print(f"📰 采集新闻资讯...")
        section = {}
        
        # 公司新闻
        section["company_news"] = query_news(f"{self.stock_name} 最新消息")
        
        # 行业新闻（从行业名获取）
        industry_result = query_iwencai("industry",
            f"{self.stock_name} 所属行业", limit="1")
        industry_name = ""
        if industry_result.get("success") and industry_result.get("datas"):
            industry_name = industry_result["datas"][0].get("所属同花顺行业", "")
            if isinstance(industry_name, list):
                industry_name = industry_name[0] if industry_name else ""
        
        if industry_name:
            section["industry_news"] = query_news(f"{industry_name} 行业动态")
        else:
            section["industry_news"] = {"success": False, "query": "", "datas": []}
        
        # 宏观新闻
        section["macro_news"] = query_news("宏观经济 货币政策 财政政策")
        
        self._add_section("9_新闻资讯", section)
    
    # ----------------------------------------------------------------
    # 主采集流程
    # ----------------------------------------------------------------
    def collect_all(self) -> Dict:
        """执行全部数据采集"""
        print(f"\n{'='*60}")
        print(f"🔬 开始采集 {self.stock_name}({self.stock_code}) 深度研究数据")
        print(f"{'='*60}\n")
        
        self.collect_summary_data()
        self.collect_macro_industry_data()
        self.collect_fundamental_data()
        self.collect_governance_data()
        self.collect_institutional_data()
        self.collect_valuation_data()
        self.collect_risk_data()
        self.collect_capital_flow_data()
        self.collect_news_data()
        
        print(f"\n{'='*60}")
        print(f"✅ 数据采集完成！共采集 {len(self.data['sections'])} 个数据模块")
        print(f"{'='*60}\n")
        
        return self.data
    
    def save(self, output_path: str):
        """保存采集数据"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"💾 数据已保存到: {output_path}")

# ============================================================================
# CLI 入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="股票深度研究 - 数据采集脚本 v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 collector.py --stock-code 600519 --stock-name 贵州茅台
  python3 collector.py --stock-code 000858 --stock-name 五粮液 --output-dir /tmp/reports
        """
    )
    
    parser.add_argument("--stock-code", "-c", required=True, help="股票代码（如 600519）")
    parser.add_argument("--stock-name", "-n", required=True, help="股票名称（如 贵州茅台）")
    parser.add_argument("--output-dir", "-o", default=None, help="输出目录")
    
    args = parser.parse_args()
    
    output_dir = args.output_dir or os.path.expanduser("~/.hermes/scripts/stock-research/output")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{args.stock_code}_{args.stock_name}_{timestamp}.json")
    
    collector = StockResearchCollector(args.stock_code, args.stock_name)
    data = collector.collect_all()
    collector.save(output_file)
    
    # 输出摘要
    print(f"\n📋 数据摘要:")
    for section_name, section_data in data["sections"].items():
        success_count = sum(1 for v in section_data.values() if isinstance(v, dict) and v.get("success"))
        total_count = len(section_data)
        print(f"  • {section_name}: {success_count}/{total_count} 查询成功")
    
    print(f"\n📄 完整数据文件: {output_file}")

if __name__ == "__main__":
    main()
