"""
因子有效性分析服务
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from scipy.stats import pearsonr, spearmanr

logger = logging.getLogger(__name__)


class FactorEffectivenessService:
    """因子有效性分析服务类"""

    def __init__(self):
        pass

    def analyze_effectiveness(
        self,
        factor_data: Dict[str, pd.DataFrame],
        factor_name: str,
        future_periods: List[int] = [1, 5, 10, 20]
    ) -> Dict[str, Any]:
        """
        分析因子有效性

        Args:
            factor_data: 股票代码到因子数据的映射
            factor_name: 因子名称
            future_periods: 未来收益周期列表

        Returns:
            {
                "scatter_plot": {...},     # 散点图数据
                "ic_time_series": {...},   # IC时序分析
                "event_response": {...},   # 事件响应分析
                "decay_analysis": {...}    # 因子衰减曲线
            }
        """
        results = {}

        # 1. 因子-收益散点图
        results["scatter_plot"] = self._create_scatter_data(
            factor_data, factor_name
        )

        # 2. IC时序分析
        results["ic_time_series"] = self._calculate_ic_series(
            factor_data, factor_name
        )

        # 3. 事件响应分析（因子突破阈值后N日收益）
        results["event_response"] = self._analyze_event_response(
            factor_data, factor_name
        )

        # 4. 因子衰减曲线
        results["decay_analysis"] = self._analyze_decay(
            factor_data, factor_name, future_periods
        )

        return results

    def _create_scatter_data(
        self,
        factor_data: Dict[str, pd.DataFrame],
        factor_name: str
    ) -> Dict[str, Any]:
        """
        创建因子-收益散点图数据

        Returns:
            {
                "x": list,  # 因子值
                "y": list,  # 收益率
                "correlation": float,
                "correlation_pvalue": float
            }
        """
        factor_values = []
        returns = []

        for stock_code, df in factor_data.items():
            if factor_name in df.columns and "close" in df.columns:
                # 计算下一期收益率（正确的未来收益）
                df_copy = df.copy()
                df_copy["future_return"] = df_copy["close"].shift(-1) / df_copy["close"] - 1

                # 提取有效数据
                valid_data = df_copy[[factor_name, "future_return"]].dropna()

                # 过滤掉无穷值
                valid_data = valid_data[~np.isinf(valid_data["future_return"])]

                factor_values.extend(valid_data[factor_name].tolist())
                returns.extend(valid_data["future_return"].tolist())

        if len(factor_values) < 2:
            return {"error": "数据不足以计算相关性"}

        # 计算相关性
        correlation, p_value = pearsonr(factor_values, returns)

        return {
            "x": [float(v) for v in factor_values],
            "y": [float(v) for v in returns],
            "correlation": float(correlation),
            "correlation_pvalue": float(p_value),
            "count": len(factor_values)
        }

    def _calculate_ic_series(
        self,
        factor_data: Dict[str, pd.DataFrame],
        factor_name: str,
        window: int = 20
    ) -> Dict[str, Any]:
        """
        计算IC时序分析

        Returns:
            {
                "dates": list,
                "ic_values": list,
                "ic_mean": float,
                "ic_std": float,
                "ir": float,
                "ic_positive_ratio": float
            }
        """
        # 合并所有股票数据
        all_data = []
        for stock_code, df in factor_data.items():
            if factor_name in df.columns and "close" in df.columns:
                df_copy = df.copy()
                # 计算下一期收益率（正确的未来收益）
                df_copy["future_return"] = df_copy["close"].shift(-1) / df_copy["close"] - 1
                df_copy["stock_code"] = stock_code
                all_data.append(df_copy[[factor_name, "future_return", "stock_code"]])

        if not all_data:
            return {"error": "没有可用的数据"}

        merged_df = pd.concat(all_data, ignore_index=False)

        num_stocks = len(factor_data)

        # 单只股票：使用时间序列滚动IC
        if num_stocks == 1:
            return self._calculate_timeseries_ic(merged_df, factor_name, window)
        # 多只股票：使用横截面IC
        else:
            return self._calculate_cross_sectional_ic(merged_df, factor_name)

    def _calculate_timeseries_ic(
        self,
        df: pd.DataFrame,
        factor_name: str,
        window: int = 20
    ) -> Dict[str, Any]:
        """计算时间序列滚动IC（适用于单只股票）"""
        # 删除缺失值
        factor_vals = df[factor_name].dropna()
        return_vals = df["future_return"].dropna()

        # 对齐数据
        common_index = factor_vals.index.intersection(return_vals.index)
        if len(common_index) < window + 1:
            return {"error": f"数据不足，需要至少{window+1}个数据点，当前只有{len(common_index)}个"}

        factor_aligned = factor_vals.loc[common_index]
        return_aligned = return_vals.loc[common_index]

        # 计算滚动IC
        rolling_ic = factor_aligned.rolling(window=window, min_periods=10).corr(return_aligned)

        # 过滤无效值
        valid_ic = rolling_ic.dropna()
        valid_ic = valid_ic[~np.isinf(valid_ic)]

        if len(valid_ic) == 0:
            return {"error": "无法计算有效的IC序列（滚动窗口内所有值都无效）"}

        # 只取有IC值的日期和数值
        ic_values = valid_ic.tolist()
        dates = [str(d) for d in valid_ic.index]

        ic_series = pd.Series(ic_values)

        # 计算IC统计指标
        ic_mean = float(ic_series.mean())
        ic_std = float(ic_series.std())
        ir = ic_mean / ic_std if ic_std != 0 else 0.0
        ic_positive_ratio = float((ic_series > 0).mean())

        return {
            "dates": dates,
            "ic_values": [float(v) for v in ic_values],
            "ic_mean": ic_mean,
            "ic_std": ic_std,
            "ir": ir,
            "ic_positive_ratio": ic_positive_ratio
        }

    def _calculate_cross_sectional_ic(
        self,
        df: pd.DataFrame,
        factor_name: str
    ) -> Dict[str, Any]:
        """计算横截面IC（适用于多只股票）"""
        ic_values = []
        dates = []

        # 按日期分组
        grouped = df.groupby(level=0)

        for date, group in grouped:
            # 需要至少2只股票才能计算横截面相关性
            if len(group) < 2:
                continue

            factor_vals = group[factor_name].dropna()
            return_vals = group["future_return"].dropna()

            # 对齐数据
            common_index = factor_vals.index.intersection(return_vals.index)
            if len(common_index) < 2:
                continue

            # 计算横截面IC
            try:
                ic, _ = pearsonr(
                    factor_vals.loc[common_index],
                    return_vals.loc[common_index]
                )
                if not np.isnan(ic) and not np.isinf(ic):
                    ic_values.append(float(ic))
                    dates.append(str(date))
            except:
                continue

        if not ic_values:
            return {"error": "无法计算IC序列（横截面数据不足）"}

        ic_series = pd.Series(ic_values)

        # 计算IC统计指标
        ic_mean = float(ic_series.mean())
        ic_std = float(ic_series.std())
        ir = ic_mean / ic_std if ic_std != 0 else 0.0
        ic_positive_ratio = float((ic_series > 0).mean())

        return {
            "dates": dates,
            "ic_values": [float(v) for v in ic_values],
            "ic_mean": ic_mean,
            "ic_std": ic_std,
            "ir": ir,
            "ic_positive_ratio": ic_positive_ratio
        }

    def _analyze_event_response(
        self,
        factor_data: Dict[str, pd.DataFrame],
        factor_name: str,
        threshold_percentile: float = 0.8,
        holding_periods: List[int] = [1, 3, 5, 10]
    ) -> Dict[str, Any]:
        """
        事件响应分析 - 因子突破阈值后N日收益

        Args:
            factor_data: 股票代码到因子数据的映射
            factor_name: 因子名称
            threshold_percentile: 阈值分位数（0.8表示前20%高暴露）
            holding_periods: 持有周期列表

        Returns:
            {
                "threshold_value": float,
                "high_exposure_returns": {period: float},
                "low_exposure_returns": {period: float},
                "excess_returns": {period: float}
            }
        """
        # 合并所有数据
        all_data = []
        for stock_code, df in factor_data.items():
            if factor_name in df.columns and "close" in df.columns:
                all_data.append(df[[factor_name, "close"]].copy())

        if not all_data:
            return {"error": "没有可用的数据"}

        merged_df = pd.concat(all_data, ignore_index=False)

        # 计算因子阈值（高暴露阈值）
        factor_values = merged_df[factor_name].dropna()
        threshold_value = float(factor_values.quantile(threshold_percentile))

        # 分析高暴露和低暴露事件后的收益
        high_returns = {p: [] for p in holding_periods}
        low_returns = {p: [] for p in holding_periods}

        # 计算低暴露阈值（底部20%）
        low_threshold = float(factor_values.quantile(1 - threshold_percentile))

        # 找出高暴露和低暴露的时点
        for stock_code, df in factor_data.items():
            if factor_name not in df.columns or "close" not in df.columns:
                continue

            # 计算未来收益（正确的方式：未来N期的收益率）
            for period in holding_periods:
                # 未来period期的收益率 = (未来价格 - 当前价格) / 当前价格
                df[f"future_return_{period}"] = df["close"].shift(-period) / df["close"] - 1

            # 高暴露事件（因子值 > 高阈值）
            high_events = df[df[factor_name] > threshold_value].index
            for event_date in high_events:
                for period in holding_periods:
                    if event_date in df.index:
                        future_ret = df.loc[event_date, f"future_return_{period}"]
                        if pd.notna(future_ret) and not np.isinf(future_ret):
                            high_returns[period].append(future_ret)

            # 低暴露事件（因子值 < 低阈值，底部20%）
            low_events = df[df[factor_name] < low_threshold].index
            for event_date in low_events:
                for period in holding_periods:
                    if event_date in df.index:
                        future_ret = df.loc[event_date, f"future_return_{period}"]
                        if pd.notna(future_ret) and not np.isinf(future_ret):
                            low_returns[period].append(future_ret)

        # 计算平均收益
        high_avg = {}
        low_avg = {}
        excess = {}

        for period in holding_periods:
            if high_returns[period]:
                high_avg[period] = float(np.mean(high_returns[period]))
            else:
                high_avg[period] = 0.0

            if low_returns[period]:
                low_avg[period] = float(np.mean(low_returns[period]))
            else:
                low_avg[period] = 0.0

            excess[period] = high_avg[period] - low_avg[period]

        return {
            "threshold_value": threshold_value,
            "threshold_percentile": threshold_percentile,
            "high_exposure_returns": {f"{p}日": high_avg[p] for p in holding_periods},
            "low_exposure_returns": {f"{p}日": low_avg[p] for p in holding_periods},
            "excess_returns": {f"{p}日": excess[p] for p in holding_periods},
            "holding_periods": holding_periods
        }

    def _analyze_decay(
        self,
        factor_data: Dict[str, pd.DataFrame],
        factor_name: str,
        periods: List[int]
    ) -> Dict[str, Any]:
        """
        因子衰减分析 - 计算不同持有期的IC

        Returns:
            {
                "decay_curve": [
                    {"period": str, "period_days": int, "ic": float, "abs_ic": float}
                ]
            }
        """
        decay_data = []

        for period in periods:
            all_factor_values = []
            all_returns = []

            for stock_code, df in factor_data.items():
                if factor_name not in df.columns or "close" not in df.columns:
                    continue

                # 计算未来收益（未来period期的收益率）
                future_returns = df["close"].shift(-period) / df["close"] - 1

                # 获取有效数据
                factor_series = df[factor_name]
                valid_mask = factor_series.notna() & future_returns.notna()

                if valid_mask.sum() >= 5:  # 至少需要5个数据点
                    all_factor_values.extend(factor_series[valid_mask].tolist())
                    all_returns.extend(future_returns[valid_mask].tolist())

            # 计算该持有期的IC
            if len(all_factor_values) >= 10:
                try:
                    ic, _ = pearsonr(all_factor_values, all_returns)
                    if not np.isnan(ic) and not np.isinf(ic):
                        decay_data.append({
                            "period": f"{period}日",
                            "period_days": period,
                            "ic": float(ic),
                            "abs_ic": abs(float(ic))
                        })
                except:
                    pass

        if not decay_data:
            return {"error": "无法计算衰减曲线"}

        return {"decay_curve": decay_data}


# 全局服务实例
factor_effectiveness_service = FactorEffectivenessService()
