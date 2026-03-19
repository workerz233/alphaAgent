"""
综合评分服务 - 多维度综合评分系统
"""
from typing import Dict, List, Optional
import pandas as pd
import numpy as np


class ComprehensiveScoringService:
    """综合评分服务"""

    def __init__(self):
        # 默认评分配置
        self.default_weights = {
            "return": 0.3,          # 收益率权重
            "risk": 0.25,            # 风险权重
            "efficiency": 0.2,       # 效率权重（夏普、IR等）
            "stability": 0.15,       # 稳定性权重
            "cost": 0.1,             # 成本权重（换手率）
        }

    def score_factor(
        self,
        factor_metrics: Dict,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict:
        """
        对因子进行综合评分

        Args:
            factor_metrics: 因子指标字典
                必须包含:
                - ic_mean: IC均值
                - ir: IR值
                - ic_std: IC标准差（可选）
                - stability_score: 稳定性得分（可选）
                - turnover: 换手率（可选）
            weights: 自定义权重

        Returns:
            评分结果
        """
        if weights is None:
            weights = {
                "ic": 0.35,
                "ir": 0.30,
                "stability": 0.20,
                "turnover": 0.15,
            }

        total_score = 0.0
        details = {}

        # 1. IC得分 (0-100)
        ic_mean = abs(factor_metrics.get("ic_mean", 0))
        ic_score = min(ic_mean * 400, 100)  # IC=0.25时满分
        total_score += weights["ic"] * ic_score
        details["ic_score"] = float(ic_score)

        # 2. IR得分 (0-100)
        ir = factor_metrics.get("ir", 0)
        ir_score = min(ir * 40, 100)  # IR=2.5时满分
        total_score += weights["ir"] * ir_score
        details["ir_score"] = float(ir_score)

        # 3. 稳定性得分 (0-100)
        stability = factor_metrics.get("stability_score", 0.8)
        stability_score = stability * 100
        total_score += weights["stability"] * stability_score
        details["stability_score"] = float(stability_score)

        # 4. 换手率得分 (0-100)
        turnover = factor_metrics.get("turnover", 0.3)
        # 换手率越低越好
        turnover_score = max(100 - turnover * 200, 0)
        total_score += weights["turnover"] * turnover_score
        details["turnover_score"] = float(turnover_score)

        # 评级
        grade = self._get_grade(total_score)

        return {
            "total_score": round(total_score, 2),
            "grade": grade,
            "details": details,
            "weights": weights,
        }

    def score_strategy(
        self,
        strategy_metrics: Dict,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict:
        """
        对策略进行综合评分

        Args:
            strategy_metrics: 策略指标字典
                必须包含:
                - annual_return: 年化收益率
                - volatility: 波动率
                - sharpe_ratio: 夏普比率
                - max_drawdown: 最大回撤
                - win_rate: 胜率（可选）
                - turnover: 换手率（可选）
            weights: 自定义权重

        Returns:
            评分结果
        """
        if weights is None:
            weights = self.default_weights

        total_score = 0.0
        details = {}

        # 1. 收益率得分 (0-100)
        annual_return = strategy_metrics.get("annual_return", 0)
        # 假设年化收益率目标为20%
        return_score = min(max(annual_return / 0.2 * 100, 0), 100)
        total_score += weights["return"] * return_score
        details["return_score"] = float(return_score)

        # 2. 风险得分 (0-100)
        max_drawdown = strategy_metrics.get("max_drawdown", 0.2)
        # 最大回撤越小越好，假设目标为10%
        drawdown_score = max(100 - abs(max_drawdown) / 0.1 * 100, 0)
        total_score += weights["risk"] * drawdown_score
        details["risk_score"] = float(drawdown_score)

        # 3. 效率得分 (0-100)
        sharpe_ratio = strategy_metrics.get("sharpe_ratio", 0)
        # 夏普比率目标为2.0
        sharpe_score = min(sharpe_ratio / 2.0 * 100, 100)
        total_score += weights["efficiency"] * sharpe_score
        details["efficiency_score"] = float(sharpe_score)

        # 4. 稳定性得分 (0-100)
        win_rate = strategy_metrics.get("win_rate", 0.5)
        win_rate_score = win_rate * 100
        total_score += weights["stability"] * win_rate_score
        details["stability_score"] = float(win_rate_score)

        # 5. 成本得分 (0-100)
        turnover = strategy_metrics.get("turnover", 0.5)
        # 换手率越低越好
        cost_score = max(100 - turnover * 100, 0)
        total_score += weights["cost"] * cost_score
        details["cost_score"] = float(cost_score)

        # 评级
        grade = self._get_grade(total_score)

        return {
            "total_score": round(total_score, 2),
            "grade": grade,
            "details": details,
            "weights": weights,
        }

    def score_portfolio(
        self,
        portfolio_metrics: Dict,
        benchmark_metrics: Optional[Dict] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict:
        """
        对投资组合进行综合评分

        Args:
            portfolio_metrics: 组合指标字典
            benchmark_metrics: 基准指标字典（可选）
            weights: 自定义权重

        Returns:
            评分结果
        """
        if weights is None:
            weights = {
                "return": 0.35,
                "risk": 0.30,
                "diversification": 0.2,
                "efficiency": 0.15,
            }

        total_score = 0.0
        details = {}

        # 1. 收益率得分
        annual_return = portfolio_metrics.get("annual_return", 0)
        return_score = min(max(annual_return / 0.15 * 100, 0), 100)

        # 如果有基准，计算超额收益
        if benchmark_metrics:
            benchmark_return = benchmark_metrics.get("annual_return", 0)
            excess_return = annual_return - benchmark_return
            return_score = min(max(excess_return / 0.05 * 100, 0), 100)

        total_score += weights["return"] * return_score
        details["return_score"] = float(return_score)

        # 2. 风险得分
        volatility = portfolio_metrics.get("volatility", 0.15)
        max_drawdown = portfolio_metrics.get("max_drawdown", 0.1)
        risk_score = max(100 - (volatility / 0.2 * 50 + max_drawdown / 0.15 * 50), 0)
        total_score += weights["risk"] * risk_score
        details["risk_score"] = float(risk_score)

        # 3. 分散化得分
        concentration = portfolio_metrics.get("herfindahl_index", 0.1)
        # Herfindahl指数越低越好
        diversification_score = max(100 - concentration * 100, 0)
        total_score += weights["diversification"] * diversification_score
        details["diversification_score"] = float(diversification_score)

        # 4. 效率得分
        sharpe_ratio = portfolio_metrics.get("sharpe_ratio", 1.0)
        sharpe_score = min(sharpe_ratio / 2.0 * 100, 100)
        total_score += weights["efficiency"] * sharpe_score
        details["efficiency_score"] = float(sharpe_score)

        # 评级
        grade = self._get_grade(total_score)

        return {
            "total_score": round(total_score, 2),
            "grade": grade,
            "details": details,
            "weights": weights,
        }

    def compare_and_rank(
        self,
        items: List[Dict],
        scoring_type: str = "strategy",
    ) -> List[Dict]:
        """
        对多个项目进行评分和排名

        Args:
            items: 项目列表，每个项目包含metrics和name
            scoring_type: 评分类型 ("factor", "strategy", "portfolio")

        Returns:
            排序后的项目列表
        """
        scored_items = []

        for item in items:
            metrics = item.get("metrics", {})
            name = item.get("name", "Unknown")

            # 根据类型选择评分方法
            if scoring_type == "factor":
                score_result = self.score_factor(metrics)
            elif scoring_type == "strategy":
                score_result = self.score_strategy(metrics)
            elif scoring_type == "portfolio":
                score_result = self.score_portfolio(metrics)
            else:
                raise ValueError(f"未知的评分类型: {scoring_type}")

            scored_items.append({
                "name": name,
                "score": score_result["total_score"],
                "grade": score_result["grade"],
                "details": score_result["details"],
            })

        # 按得分排序
        scored_items.sort(key=lambda x: x["score"], reverse=True)

        # 添加排名
        for i, item in enumerate(scored_items, 1):
            item["rank"] = i

        return scored_items

    def _get_grade(self, score: float) -> str:
        """
        根据得分返回评级

        Args:
            score: 得分 (0-100)

        Returns:
            评级
        """
        if score >= 95:
            return "S+"
        elif score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        else:
            return "D"

    def generate_scoring_report(self, score_result: Dict, name: str) -> str:
        """
        生成评分报告

        Args:
            score_result: 评分结果
            name: 项目名称

        Returns:
            报告文本
        """
        report = f"# {name} 评分报告\n\n"
        report += f"## 综合得分\n\n"
        report += f"**得分**: {score_result['total_score']:.2f}/100\n"
        report += f"**评级**: {score_result['grade']}\n\n"

        report += f"## 分项得分\n\n"

        details = score_result.get("details", {})
        weights = score_result.get("weights", {})

        for key, weight in weights.items():
            score = details.get(f"{key}_score", 0)
            report += f"- **{key.upper()}**: {score:.2f}/100 (权重 {weight:.0%})\n"

        return report


# 全局综合评分服务实例
comprehensive_scoring_service = ComprehensiveScoringService()
