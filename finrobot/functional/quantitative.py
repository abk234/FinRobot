import os
import json
import importlib
import yfinance as yf
import backtrader as bt
from backtrader.strategies import SMA_CrossOver
from typing import Annotated, List, Tuple, Dict
from matplotlib import pyplot as plt
from pprint import pformat
from IPython import get_ipython
import pandas as pd
import numpy as np


class DeployedCapitalAnalyzer(bt.Analyzer):
    def start(self):
        self.deployed_capital = []
        self.initial_cash = self.strategy.broker.get_cash()  # Initial cash in account

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.deployed_capital.append(order.executed.price * order.executed.size)
            elif order.issell():
                self.deployed_capital.append(order.executed.price * order.executed.size)

    def stop(self):
        total_deployed = sum(self.deployed_capital)
        final_cash = self.strategy.broker.get_value()
        net_profit = final_cash - self.initial_cash
        if total_deployed > 0:
            self.retn = net_profit / total_deployed
        else:
            self.retn = 0

    def get_analysis(self):
        return {"return_on_deployed_capital": self.retn}


class BackTraderUtils:

    def back_test(
        ticker_symbol: Annotated[
            str, "Ticker symbol of the stock (e.g., 'AAPL' for Apple)"
        ],
        start_date: Annotated[
            str, "Start date of the historical data in 'YYYY-MM-DD' format"
        ],
        end_date: Annotated[
            str, "End date of the historical data in 'YYYY-MM-DD' format"
        ],
        strategy: Annotated[
            str,
            "BackTrader Strategy class to be backtested. Can be pre-defined or custom. Pre-defined options: 'SMA_CrossOver'. If custom, provide module path and class name as a string like 'my_module:TestStrategy'.",
        ],
        strategy_params: Annotated[
            str,
            "Additional parameters to be passed to the strategy class formatted as json string. E.g. {'fast': 10, 'slow': 30} for SMACross.",
        ] = "",
        sizer: Annotated[
            int | str | None,
            "Sizer used for backtesting. Can be a fixed number or a custom Sizer class. If input is integer, a corresponding fixed sizer will be applied. If custom, provide module path and class name as a string like 'my_module:TestSizer'.",
        ] = None,
        sizer_params: Annotated[
            str,
            "Additional parameters to be passed to the sizer class formatted as json string.",
        ] = "",
        indicator: Annotated[
            str | None,
            "Custom indicator class added to strategy. Provide module path and class name as a string like 'my_module:TestIndicator'.",
        ] = None,
        indicator_params: Annotated[
            str,
            "Additional parameters to be passed to the indicator class formatted as json string.",
        ] = "",
        cash: Annotated[
            float, "Initial cash amount for the backtest. Default to 10000.0"
        ] = 10000.0,
        save_fig: Annotated[
            str | None, "Path to save the plot of backtest results. Default to None."
        ] = None,
    ) -> str:
        """
        Use the Backtrader library to backtest a trading strategy on historical stock data.
        """
        cerebro = bt.Cerebro()

        if strategy == "SMA_CrossOver":
            strategy_class = SMA_CrossOver
        else:
            assert (
                ":" in strategy
            ), "Custom strategy should be module path and class name separated by a colon."
            module_path, class_name = strategy.split(":")
            module = importlib.import_module(module_path)
            strategy_class = getattr(module, class_name)

        strategy_params = json.loads(strategy_params) if strategy_params else {}
        cerebro.addstrategy(strategy_class, **strategy_params)

        # Create a data feed
        data = bt.feeds.PandasData(
            dataname=yf.download(ticker_symbol, start_date, end_date, auto_adjust=True)
        )
        cerebro.adddata(data)  # Add the data feed
        # Set our desired cash start
        cerebro.broker.setcash(cash)

        # Set the size of the trades
        if sizer is not None:
            if isinstance(sizer, int):
                cerebro.addsizer(bt.sizers.FixedSize, stake=sizer)
            else:
                assert (
                    ":" in sizer
                ), "Custom sizer should be module path and class name separated by a colon."
                module_path, class_name = sizer.split(":")
                module = importlib.import_module(module_path)
                sizer_class = getattr(module, class_name)
                sizer_params = json.loads(sizer_params) if sizer_params else {}
                cerebro.addsizer(sizer_class, **sizer_params)

        # Set additional indicator
        if indicator is not None:
            assert (
                ":" in indicator
            ), "Custom indicator should be module path and class name separated by a colon."
            module_path, class_name = indicator.split(":")
            module = importlib.import_module(module_path)
            indicator_class = getattr(module, class_name)
            indicator_params = json.loads(indicator_params) if indicator_params else {}
            cerebro.addindicator(indicator_class, **indicator_params)

        # Attach analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe_ratio")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="draw_down")
        cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trade_analyzer")
        # cerebro.addanalyzer(DeployedCapitalAnalyzer, _name="deployed_capital")

        stats_dict = {"Starting Portfolio Value:": cerebro.broker.getvalue()}

        results = cerebro.run()  # run it all
        first_strategy = results[0]

        # Access analysis results
        stats_dict["Final Portfolio Value"] = cerebro.broker.getvalue()
        # stats_dict["Deployed Capital"] = pformat(
        #     first_strategy.analyzers.deployed_capital.get_analysis(), indent=4
        # )
        stats_dict["Sharpe Ratio"] = (
            first_strategy.analyzers.sharpe_ratio.get_analysis()
        )
        stats_dict["Drawdown"] = first_strategy.analyzers.draw_down.get_analysis()
        stats_dict["Returns"] = first_strategy.analyzers.returns.get_analysis()
        stats_dict["Trade Analysis"] = (
            first_strategy.analyzers.trade_analyzer.get_analysis()
        )

        if save_fig:
            directory = os.path.dirname(save_fig)
            if directory:
                os.makedirs(directory, exist_ok=True)
            plt.figure(figsize=(12, 8))
            cerebro.plot()
            plt.savefig(save_fig)
            plt.close()

        return "Back Test Finished. Results: \n" + pformat(stats_dict, indent=2)


class TradingStrategyAnalyzer:
    """
    Analyzes trading opportunities and calculates entry price, stop loss, target price, and optimal entry timing.
    """

    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range (ATR) for volatility-based stop loss."""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr

    @staticmethod
    def calculate_support_resistance(data: pd.DataFrame, window: int = 20) -> Dict[str, float]:
        """Calculate support and resistance levels using local minima and maxima."""
        close = data['Close']
        high = data['High']
        low = data['Low']
        
        # Find local minima (support) and maxima (resistance)
        support_levels = []
        resistance_levels = []
        
        for i in range(window, len(data) - window):
            # Support: local minimum
            if low.iloc[i] == low.iloc[i-window:i+window+1].min():
                support_levels.append(low.iloc[i])
            # Resistance: local maximum
            if high.iloc[i] == high.iloc[i-window:i+window+1].max():
                resistance_levels.append(high.iloc[i])
        
        current_price = close.iloc[-1]
        
        # Find nearest support and resistance
        support_below = [s for s in support_levels if s < current_price]
        resistance_above = [r for r in resistance_levels if r > current_price]
        
        nearest_support = max(support_below) if support_below else current_price * 0.95
        nearest_resistance = min(resistance_above) if resistance_above else current_price * 1.05
        
        return {
            'support': nearest_support,
            'resistance': nearest_resistance,
            'current_price': current_price
        }

    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI) for entry timing."""
        close = data['Close']
        delta = close.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    @staticmethod
    def calculate_moving_averages(data: pd.DataFrame, short_period: int = 20, long_period: int = 50) -> Dict[str, pd.Series]:
        """Calculate short and long term moving averages."""
        close = data['Close']
        return {
            'sma_short': close.rolling(window=short_period).mean(),
            'sma_long': close.rolling(window=long_period).mean(),
            'ema_short': close.ewm(span=short_period, adjust=False).mean(),
            'ema_long': close.ewm(span=long_period, adjust=False).mean()
        }

    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence) indicator."""
        close = data['Close']
        ema_fast = close.ewm(span=fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=slow_period, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, num_std: float = 2.0) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands indicator."""
        close = data['Close']
        sma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        middle_band = sma
        
        # Calculate %B (position within bands)
        percent_b = (close - lower_band) / (upper_band - lower_band)
        
        return {
            'upper': upper_band,
            'middle': middle_band,
            'lower': lower_band,
            'percent_b': percent_b,
            'bandwidth': (upper_band - lower_band) / middle_band
        }

    @staticmethod
    def analyze_trading_opportunity(
        ticker_symbol: Annotated[
            str, "Ticker symbol of the stock (e.g., 'AAPL' for Apple)"
        ],
        period: Annotated[
            str, "Time period for analysis: '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'"
        ] = "6mo",
        risk_reward_ratio: Annotated[
            float, "Risk-reward ratio for target price calculation (e.g., 2.0 means target is 2x the risk). Default is 2.0"
        ] = 2.0,
        stop_loss_method: Annotated[
            str, "Method for stop loss: 'atr' (Average True Range), 'percentage' (fixed %), 'support' (nearest support level). Default is 'atr'"
        ] = "atr",
        stop_loss_percentage: Annotated[
            float, "Percentage for stop loss if method is 'percentage' (e.g., 2.0 for 2%). Default is 2.0"
        ] = 2.0,
        atr_multiplier: Annotated[
            float, "Multiplier for ATR-based stop loss (e.g., 2.0 means stop loss is 2x ATR). Default is 2.0"
        ] = 2.0,
        use_advanced_indicators: Annotated[
            bool, "Whether to use MACD and Bollinger Bands for enhanced analysis. Default is True"
        ] = True,
    ) -> str:
        """
        Analyze a stock and provide trading recommendations including:
        - Entry price (current price or pullback level)
        - Stop loss level
        - Target price
        - Optimal entry timing based on technical indicators
        """
        try:
            # Fetch stock data
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return f"Error: No data available for {ticker_symbol}"
            
            # Calculate technical indicators
            current_price = data['Close'].iloc[-1]
            atr = TradingStrategyAnalyzer.calculate_atr(data)
            current_atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else current_price * 0.02
            
            support_resistance = TradingStrategyAnalyzer.calculate_support_resistance(data)
            rsi = TradingStrategyAnalyzer.calculate_rsi(data)
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            ma = TradingStrategyAnalyzer.calculate_moving_averages(data)
            sma_short = ma['sma_short'].iloc[-1]
            sma_long = ma['sma_long'].iloc[-1]
            ema_short = ma['ema_short'].iloc[-1]
            ema_long = ma['ema_long'].iloc[-1]
            
            # Calculate advanced indicators if enabled
            macd_data = None
            bb_data = None
            if use_advanced_indicators:
                macd_data = TradingStrategyAnalyzer.calculate_macd(data)
                bb_data = TradingStrategyAnalyzer.calculate_bollinger_bands(data)
            
            # Determine trend with multiple confirmations
            ma_bullish = sma_short > sma_long and ema_short > ema_long
            trend = "BULLISH" if ma_bullish else "BEARISH"
            
            # MACD confirmation
            macd_signal = None
            if macd_data is not None:
                current_macd = macd_data['macd'].iloc[-1]
                current_signal = macd_data['signal'].iloc[-1]
                current_histogram = macd_data['histogram'].iloc[-1]
                prev_histogram = macd_data['histogram'].iloc[-2] if len(macd_data['histogram']) > 1 else 0
                
                # MACD bullish: MACD line above signal line and histogram increasing
                macd_bullish = current_macd > current_signal and current_histogram > prev_histogram
                macd_signal = "BULLISH" if macd_bullish else "BEARISH"
            
            # Bollinger Bands analysis
            bb_signal = None
            bb_position = None
            if bb_data is not None:
                current_price = data['Close'].iloc[-1]
                upper_bb = bb_data['upper'].iloc[-1]
                lower_bb = bb_data['lower'].iloc[-1]
                middle_bb = bb_data['middle'].iloc[-1]
                percent_b = bb_data['percent_b'].iloc[-1]
                
                if current_price < lower_bb:
                    bb_signal = "OVERSOLD"
                    bb_position = "Below Lower Band"
                elif current_price > upper_bb:
                    bb_signal = "OVERBOUGHT"
                    bb_position = "Above Upper Band"
                elif current_price > middle_bb:
                    bb_signal = "NEUTRAL-BULLISH"
                    bb_position = "Upper Half"
                else:
                    bb_signal = "NEUTRAL-BEARISH"
                    bb_position = "Lower Half"
            
            # Calculate entry price with advanced indicator confirmation
            bullish_signals = 0
            bearish_signals = 0
            
            if ma_bullish:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            if macd_signal == "BULLISH":
                bullish_signals += 1
            elif macd_signal == "BEARISH":
                bearish_signals += 1
            
            if bb_signal in ["NEUTRAL-BULLISH", "OVERSOLD"]:
                bullish_signals += 1
            elif bb_signal == "OVERBOUGHT":
                bearish_signals += 1
            
            # Enhanced entry logic
            if bullish_signals >= 2:
                # Strong bullish setup
                if bb_signal == "OVERSOLD":
                    entry_price = lower_bb if bb_data is not None else support_resistance['support']
                    entry_recommendation = "BUY: Oversold condition with bullish momentum"
                else:
                    entry_price = min(current_price, max(support_resistance['support'], sma_short))
                    entry_recommendation = "BUY: Multiple bullish signals confirmed"
            elif bearish_signals >= 2:
                entry_price = current_price
                entry_recommendation = "CAUTION: Multiple bearish signals. Wait for reversal or avoid."
            elif trend == "BULLISH":
                entry_price = min(current_price, max(support_resistance['support'], sma_short))
                entry_recommendation = "BUY on pullback to support or moving average"
            else:
                entry_price = current_price
                entry_recommendation = "CAUTION: Bearish trend detected. Consider waiting for trend reversal."
            
            # Calculate stop loss
            if stop_loss_method == "atr":
                stop_loss = entry_price - (atr_multiplier * current_atr)
            elif stop_loss_method == "percentage":
                stop_loss = entry_price * (1 - stop_loss_percentage / 100)
            elif stop_loss_method == "support":
                stop_loss = support_resistance['support'] * 0.98  # Slightly below support
            else:
                stop_loss = entry_price * 0.98  # Default 2% stop loss
            
            # Ensure stop loss is reasonable
            if stop_loss > entry_price * 0.95:  # Not more than 5% below entry
                stop_loss = entry_price * 0.97
            
            # Calculate target price based on risk-reward ratio
            risk = entry_price - stop_loss
            target_price = entry_price + (risk * risk_reward_ratio)
            
            # Also consider resistance level
            if target_price > support_resistance['resistance']:
                target_price = support_resistance['resistance'] * 0.99  # Slightly below resistance
            
            # Determine optimal entry timing with advanced indicators
            entry_timing = []
            signal_strength = "MODERATE"
            
            # RSI-based timing
            if current_rsi < 30:
                entry_timing.append("RSI indicates OVERSOLD - Good entry opportunity")
                signal_strength = "STRONG" if bullish_signals >= 2 else signal_strength
            elif current_rsi > 70:
                entry_timing.append("RSI indicates OVERBOUGHT - Wait for pullback")
            elif 30 <= current_rsi <= 50:
                entry_timing.append("RSI in neutral zone - Good entry zone")
            
            # Moving average crossover
            if ema_short > ema_long and sma_short > sma_long:
                entry_timing.append("Moving averages show BULLISH momentum")
            elif ema_short < ema_long and sma_short < sma_long:
                entry_timing.append("Moving averages show BEARISH momentum - Wait for reversal")
            
            # MACD signals
            if macd_data is not None:
                if macd_signal == "BULLISH":
                    entry_timing.append("MACD shows BULLISH crossover - Momentum building")
                    signal_strength = "STRONG" if bullish_signals >= 2 else signal_strength
                elif macd_signal == "BEARISH":
                    entry_timing.append("MACD shows BEARISH signal - Wait for reversal")
            
            # Bollinger Bands signals
            if bb_data is not None:
                if bb_signal == "OVERSOLD":
                    entry_timing.append(f"Bollinger Bands: OVERSOLD ({bb_position}) - Potential bounce")
                    signal_strength = "STRONG"
                elif bb_signal == "OVERBOUGHT":
                    entry_timing.append(f"Bollinger Bands: OVERBOUGHT ({bb_position}) - Wait for pullback")
                else:
                    entry_timing.append(f"Bollinger Bands: {bb_position} - {bb_signal}")
            
            # Price position
            if current_price < sma_short:
                entry_timing.append("Price below short MA - Potential pullback entry")
            elif current_price > sma_short:
                entry_timing.append("Price above short MA - Momentum entry")
            
            # Overall signal strength
            if bullish_signals >= 2:
                signal_strength = "STRONG"
                entry_timing.append(f"✅ STRONG BUY SIGNAL: {bullish_signals} bullish confirmations")
            elif bearish_signals >= 2:
                signal_strength = "WEAK"
                entry_timing.append(f"⚠️ WEAK SIGNAL: {bearish_signals} bearish signals detected")
            
            # Compile results
            result = {
                "Ticker": ticker_symbol,
                "Current Price": f"${current_price:.2f}",
                "Trend": trend,
                "Signal Strength": signal_strength,
                "Entry Price": f"${entry_price:.2f}",
                "Entry Recommendation": entry_recommendation,
                "Stop Loss": f"${stop_loss:.2f} ({((stop_loss/entry_price - 1) * 100):.2f}%)",
                "Target Price": f"${target_price:.2f} ({((target_price/entry_price - 1) * 100):.2f}%)",
                "Risk-Reward Ratio": f"{risk_reward_ratio:.1f}:1",
                "Risk Amount": f"${risk:.2f} per share",
                "Potential Reward": f"${(target_price - entry_price):.2f} per share",
                "Support Level": f"${support_resistance['support']:.2f}",
                "Resistance Level": f"${support_resistance['resistance']:.2f}",
                "Current RSI": f"{current_rsi:.2f}",
                "Short MA (20)": f"${sma_short:.2f}",
                "Long MA (50)": f"${sma_long:.2f}",
            }
            
            # Add advanced indicators if enabled
            if macd_data is not None:
                result["MACD"] = f"{macd_data['macd'].iloc[-1]:.4f}"
                result["MACD Signal"] = f"{macd_data['signal'].iloc[-1]:.4f}"
                result["MACD Histogram"] = f"{macd_data['histogram'].iloc[-1]:.4f}"
                result["MACD Signal Type"] = macd_signal
            
            if bb_data is not None:
                result["Bollinger Upper"] = f"${bb_data['upper'].iloc[-1]:.2f}"
                result["Bollinger Middle"] = f"${bb_data['middle'].iloc[-1]:.2f}"
                result["Bollinger Lower"] = f"${bb_data['lower'].iloc[-1]:.2f}"
                result["Bollinger %B"] = f"{bb_data['percent_b'].iloc[-1]:.2f}"
                result["Bollinger Position"] = bb_position
            
            result["Optimal Entry Timing"] = "\n".join(f"  • {timing}" for timing in entry_timing)
            
            # Format output with explanations
            output = f"""
╔══════════════════════════════════════════════════════════════╗
║          TRADING STRATEGY ANALYSIS - {ticker_symbol:^10}          ║
╚══════════════════════════════════════════════════════════════╝

📊 CURRENT MARKET DATA:
   Current Price: {result['Current Price']}
   Trend: {result['Trend']} ({'Price is generally moving UP' if trend == 'BULLISH' else 'Price is generally moving DOWN'})
   Signal Strength: {result['Signal Strength']} ({'Multiple indicators agree - Higher confidence' if signal_strength == 'STRONG' else 'Mixed signals - Proceed with caution' if signal_strength == 'MODERATE' else 'Indicators disagree - Wait for better setup'})
   
   📈 Moving Averages (Shows price trend over time):
   • Short MA (20 days): {result['Short MA (20)']} - Recent average price
   • Long MA (50 days): {result['Long MA (50)']} - Longer-term average price
   • Interpretation: {'Short MA above Long MA = BULLISH trend (price likely to continue up)' if ma_bullish else 'Short MA below Long MA = BEARISH trend (price likely to continue down)'}
   
   📊 RSI (Relative Strength Index): {result['Current RSI']}
   • What it means: {'OVERSOLD (below 30) - Stock may bounce back up - Good BUY opportunity' if current_rsi < 30 else 'OVERBOUGHT (above 70) - Stock may pull back - Consider SELLING or waiting' if current_rsi > 70 else 'Neutral (30-70) - Stock moving at healthy pace'}
   • Simple explanation: Like a speedometer - too fast (overbought) or too slow (oversold)"""
            
            # Add MACD info if available
            if macd_data is not None:
                macd_explanation = "BULLISH - MACD above Signal = Momentum building (like green traffic light)" if macd_signal == "BULLISH" else "BEARISH - MACD below Signal = Momentum slowing (like red traffic light)"
                hist_trend = ""
                if len(macd_data['histogram']) > 1:
                    prev_hist = macd_data['histogram'].iloc[-2]
                    hist_trend = "Increasing = Strong momentum" if current_histogram > prev_hist else "Decreasing = Momentum weakening"
                else:
                    hist_trend = "Initial reading"
                
                output += f"""
   
📈 MACD INDICATOR (Shows momentum changes):
   MACD Line: {result['MACD']}
   Signal Line: {result['MACD Signal']}
   Histogram: {result['MACD Histogram']} ({hist_trend})
   Signal: {result['MACD Signal Type']} - {macd_explanation}
   • Simple explanation: Like a traffic light - green (bullish) when MACD crosses above Signal, red (bearish) when it crosses below"""
            
            # Add Bollinger Bands info if available
            if bb_data is not None:
                bb_explanation = ""
                if bb_signal == "OVERSOLD":
                    bb_explanation = "Price at LOWER band = OVERSOLD - May bounce up (potential BUY signal)"
                elif bb_signal == "OVERBOUGHT":
                    bb_explanation = "Price at UPPER band = OVERBOUGHT - May pull back (potential SELL signal)"
                elif bb_signal == "NEUTRAL-BULLISH":
                    bb_explanation = "Price in upper half of bands - Slightly bullish"
                else:
                    bb_explanation = "Price in lower half of bands - Slightly bearish"
                
                output += f"""
   
📊 BOLLINGER BANDS (Shows price boundaries and volatility):
   Upper Band: {result['Bollinger Upper']} (Like a ceiling - price rarely goes above)
   Middle Band: {result['Bollinger Middle']} (Average price - center of the band)
   Lower Band: {result['Bollinger Lower']} (Like a floor - price rarely goes below)
   %B: {result['Bollinger %B']} ({'0 = at lower band, 1 = at upper band, 0.5 = at middle'})
   Position: {result['Bollinger Position']}
   • Interpretation: {bb_explanation}
   • Simple explanation: Like a rubber band - when price touches edges, it often bounces back toward middle"""
            
            output += f"""

🎯 TRADING RECOMMENDATIONS:
   Entry Price: {result['Entry Price']}
   Entry Strategy: {result['Entry Recommendation']}
   
   🛡️ Stop Loss: {result['Stop Loss']}
   • What it means: Maximum price you're willing to lose per share
   • Why it matters: Protects you from big losses - automatically sell if price drops to this level
   • Simple explanation: Like a safety net - if trade goes wrong, you exit here to limit losses
   
   🎯 Target Price: {result['Target Price']}
   • What it means: Price level where you should consider taking profit
   • Why it matters: Helps you know when to sell and lock in gains
   • Simple explanation: Like a finish line - when price reaches here, consider selling to take profit
   
   💰 Risk-Reward: {result['Risk-Reward Ratio']}
   • What it means: {f'You risk ${risk:.2f} to potentially make ${(target_price - entry_price):.2f}'}
   • Why it matters: {'Good ratio - potential reward is greater than risk' if risk_reward_ratio >= 2.0 else 'Consider improving ratio - reward should be at least 2x the risk'}
   • Simple explanation: Like betting odds - {f'Risk $1 to make ${risk_reward_ratio:.1f}'} - Only take trades where reward > risk
   
   Risk per Share: {result['Risk Amount']}
   Potential Reward: {result['Potential Reward']}

📈 TECHNICAL LEVELS (Historical price boundaries):
   Support: {result['Support Level']}
   • What it means: Price level where buyers often step in (like a floor)
   • How to use: Good place to buy, set stop loss just below this level
   • Simple explanation: Like a safety net - price often bounces up from here
   
   Resistance: {result['Resistance Level']}
   • What it means: Price level where sellers often step in (like a ceiling)
   • How to use: Good place to sell, set target price near this level
   • Simple explanation: Like a ceiling - price often bounces down from here

⏰ OPTIMAL ENTRY TIMING:
{result['Optimal Entry Timing']}

⚠️  RISK DISCLAIMER:
   This analysis is for informational purposes only and should not be
   considered as financial advice. Always do your own research and
   consider your risk tolerance before making any trading decisions.
"""
            
            return output
            
        except Exception as e:
            return f"Error analyzing {ticker_symbol}: {str(e)}"

    @staticmethod
    def backtest_strategy_recommendations(
        ticker_symbol: Annotated[
            str, "Ticker symbol of the stock (e.g., 'AAPL' for Apple)"
        ],
        start_date: Annotated[
            str, "Start date for backtesting in 'YYYY-MM-DD' format"
        ],
        end_date: Annotated[
            str, "End date for backtesting in 'YYYY-MM-DD' format"
        ],
        entry_price: Annotated[
            float, "Entry price for the strategy"
        ],
        stop_loss: Annotated[
            float, "Stop loss price"
        ],
        target_price: Annotated[
            float, "Target price for taking profit"
        ],
        use_advanced_indicators: Annotated[
            bool, "Whether to use MACD and Bollinger Bands for entry/exit signals"
        ] = True,
    ) -> str:
        """
        Backtest a trading strategy based on the recommended entry, stop loss, and target prices.
        Returns performance metrics and trade statistics.
        """
        try:
            # Fetch historical data
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                return f"Error: No data available for {ticker_symbol} from {start_date} to {end_date}"
            
            # Initialize tracking variables
            position = None  # None, 'long', or 'short'
            entry_date = None
            entry_price_actual = None
            trades = []
            wins = 0
            losses = 0
            total_profit = 0.0
            
            # Calculate indicators
            if use_advanced_indicators:
                macd_data = TradingStrategyAnalyzer.calculate_macd(data)
                bb_data = TradingStrategyAnalyzer.calculate_bollinger_bands(data)
            
            ma = TradingStrategyAnalyzer.calculate_moving_averages(data)
            rsi = TradingStrategyAnalyzer.calculate_rsi(data)
            
            # Simulate trading
            for i in range(50, len(data)):  # Start after enough data for indicators
                current_price = data['Close'].iloc[i]
                current_date = data.index[i]
                
                # Check if we have a position
                if position is None:
                    # Look for entry signal
                    sma_short = ma['sma_short'].iloc[i]
                    sma_long = ma['sma_long'].iloc[i]
                    current_rsi = rsi.iloc[i] if not pd.isna(rsi.iloc[i]) else 50
                    
                    # Entry conditions
                    ma_bullish = sma_short > sma_long
                    rsi_ok = current_rsi < 70  # Not overbought
                    price_near_entry = abs(current_price - entry_price) / entry_price < 0.02  # Within 2%
                    
                    # Advanced indicator confirmation
                    macd_ok = True
                    bb_ok = True
                    if use_advanced_indicators:
                        if macd_data is not None:
                            current_macd = macd_data['macd'].iloc[i]
                            current_signal = macd_data['signal'].iloc[i]
                            macd_ok = current_macd > current_signal
                        
                        if bb_data is not None:
                            lower_bb = bb_data['lower'].iloc[i]
                            bb_ok = current_price >= lower_bb  # Not too oversold
                    
                    # Enter long position
                    if ma_bullish and rsi_ok and price_near_entry and macd_ok and bb_ok:
                        position = 'long'
                        entry_date = current_date
                        entry_price_actual = current_price
                
                elif position == 'long':
                    # Check exit conditions
                    exit_reason = None
                    exit_price = None
                    
                    # Stop loss hit
                    if current_price <= stop_loss:
                        exit_reason = "Stop Loss"
                        exit_price = stop_loss
                    # Target hit
                    elif current_price >= target_price:
                        exit_reason = "Target Reached"
                        exit_price = target_price
                    # Trailing stop (if price moves significantly above entry)
                    elif current_price > entry_price_actual * 1.1:  # 10% profit
                        # Trailing stop at 5% below peak
                        trailing_stop = current_price * 0.95
                        if current_price < trailing_stop:
                            exit_reason = "Trailing Stop"
                            exit_price = trailing_stop
                    
                    # Exit signal from indicators
                    if exit_reason is None and use_advanced_indicators:
                        sma_short = ma['sma_short'].iloc[i]
                        sma_long = ma['sma_long'].iloc[i]
                        current_rsi = rsi.iloc[i] if not pd.isna(rsi.iloc[i]) else 50
                        
                        # Bearish reversal
                        if sma_short < sma_long:
                            exit_reason = "Bearish Reversal"
                            exit_price = current_price
                        
                        # RSI overbought
                        if current_rsi > 70:
                            exit_reason = "RSI Overbought"
                            exit_price = current_price
                        
                        # MACD bearish
                        if macd_data is not None:
                            current_macd = macd_data['macd'].iloc[i]
                            current_signal = macd_data['signal'].iloc[i]
                            if current_macd < current_signal:
                                exit_reason = "MACD Bearish"
                                exit_price = current_price
                        
                        # Bollinger Bands overbought
                        if bb_data is not None:
                            upper_bb = bb_data['upper'].iloc[i]
                            if current_price > upper_bb:
                                exit_reason = "Bollinger Overbought"
                                exit_price = current_price
                    
                    # Execute exit
                    if exit_reason:
                        profit = exit_price - entry_price_actual
                        profit_pct = (profit / entry_price_actual) * 100
                        
                        trades.append({
                            'entry_date': entry_date,
                            'exit_date': current_date,
                            'entry_price': entry_price_actual,
                            'exit_price': exit_price,
                            'profit': profit,
                            'profit_pct': profit_pct,
                            'exit_reason': exit_reason
                        })
                        
                        if profit > 0:
                            wins += 1
                        else:
                            losses += 1
                        
                        total_profit += profit
                        position = None
                        entry_date = None
                        entry_price_actual = None
                
                # Force exit at end of data
                if i == len(data) - 1 and position == 'long':
                    exit_price = current_price
                    profit = exit_price - entry_price_actual
                    profit_pct = (profit / entry_price_actual) * 100
                    
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': current_date,
                        'entry_price': entry_price_actual,
                        'exit_price': exit_price,
                        'profit': profit,
                        'profit_pct': profit_pct,
                        'exit_reason': "End of Period"
                    })
                    
                    if profit > 0:
                        wins += 1
                    else:
                        losses += 1
                    
                    total_profit += profit
            
            # Calculate statistics
            total_trades = len(trades)
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            avg_profit = total_profit / total_trades if total_trades > 0 else 0
            avg_win = sum(t['profit'] for t in trades if t['profit'] > 0) / wins if wins > 0 else 0
            avg_loss = sum(t['profit'] for t in trades if t['profit'] < 0) / losses if losses > 0 else 0
            
            # Format results
            result = f"""
╔══════════════════════════════════════════════════════════════╗
║        BACKTEST RESULTS - {ticker_symbol:^10}                    ║
╚══════════════════════════════════════════════════════════════╝

📅 BACKTEST PERIOD:
   Start: {start_date}
   End: {end_date}

📊 STRATEGY PARAMETERS:
   Entry Price: ${entry_price:.2f}
   Stop Loss: ${stop_loss:.2f}
   Target Price: ${target_price:.2f}
   Risk-Reward: {((target_price - entry_price) / (entry_price - stop_loss)):.2f}:1

📈 PERFORMANCE METRICS:
   Total Trades: {total_trades}
   Winning Trades: {wins}
   Losing Trades: {losses}
   Win Rate: {win_rate:.2f}%
   Total Profit/Loss: ${total_profit:.2f}
   Average Profit per Trade: ${avg_profit:.2f}
   Average Win: ${avg_win:.2f}
   Average Loss: ${avg_loss:.2f}

📋 TRADE DETAILS:
"""
            for i, trade in enumerate(trades, 1):
                result += f"""
   Trade #{i}:
   • Entry: {trade['entry_date'].strftime('%Y-%m-%d')} @ ${trade['entry_price']:.2f}
   • Exit: {trade['exit_date'].strftime('%Y-%m-%d')} @ ${trade['exit_price']:.2f}
   • P/L: ${trade['profit']:.2f} ({trade['profit_pct']:.2f}%)
   • Reason: {trade['exit_reason']}
"""
            
            if total_trades == 0:
                result += "\n   No trades executed during this period.\n"
            
            return result
            
        except Exception as e:
            return f"Error backtesting {ticker_symbol}: {str(e)}"

    @staticmethod
    def calculate_position_size(
        account_value: float,
        entry_price: float,
        stop_loss: float,
        risk_per_trade_pct: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate how many shares to buy based on risk management.
        
        Args:
            account_value: Total account value
            entry_price: Entry price per share
            stop_loss: Stop loss price per share
            risk_per_trade_pct: Percentage of account to risk per trade (default 1%)
        
        Returns:
            Dictionary with position sizing details
        """
        risk_per_share = entry_price - stop_loss
        if risk_per_share <= 0:
            risk_per_share = entry_price * 0.02  # Default 2% risk
        
        total_risk_amount = account_value * (risk_per_trade_pct / 100)
        num_shares = int(total_risk_amount / risk_per_share)
        
        total_cost = num_shares * entry_price
        max_loss = num_shares * risk_per_share
        
        return {
            'num_shares': num_shares,
            'total_cost': total_cost,
            'max_loss': max_loss,
            'risk_per_share': risk_per_share,
            'risk_percentage': risk_per_trade_pct
        }

    @staticmethod
    def comprehensive_analysis(
        ticker_symbol: Annotated[
            str, "Ticker symbol of the stock (e.g., 'AAPL' for Apple)"
        ],
        period: Annotated[
            str, "Time period for analysis: '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'"
        ] = "6mo",
        risk_reward_ratio: Annotated[
            float, "Risk-reward ratio for target price calculation (e.g., 2.0 means target is 2x the risk). Default is 2.0"
        ] = 2.0,
        stop_loss_method: Annotated[
            str, "Method for stop loss: 'atr' (Average True Range), 'percentage' (fixed %), 'support' (nearest support level). Default is 'atr'"
        ] = "atr",
        stop_loss_percentage: Annotated[
            float, "Percentage for stop loss if method is 'percentage' (e.g., 2.0 for 2%). Default is 2.0"
        ] = 2.0,
        account_value: Annotated[
            float, "Total account value for position sizing. Default is 10000"
        ] = 10000.0,
        risk_per_trade_pct: Annotated[
            float, "Percentage of account to risk per trade. Default is 1.0%"
        ] = 1.0,
        company_research: Annotated[
            str | None, "Company research text from AI analysis. If None, will be skipped."
        ] = None,
    ) -> str:
        """
        Comprehensive analysis combining technical analysis, position sizing, and company research.
        Provides kid-friendly recommendations and forecasts.
        """
        try:
            # Get technical analysis
            technical_result = TradingStrategyAnalyzer.analyze_trading_opportunity(
                ticker_symbol=ticker_symbol,
                period=period,
                risk_reward_ratio=risk_reward_ratio,
                stop_loss_method=stop_loss_method,
                stop_loss_percentage=stop_loss_percentage,
                atr_multiplier=2.0,
                use_advanced_indicators=True
            )
            
            # Extract key values from technical analysis
            import re
            entry_match = re.search(r'Entry Price: \$([\d.]+)', technical_result)
            stop_match = re.search(r'Stop Loss: \$([\d.]+)', technical_result)
            target_match = re.search(r'Target Price: \$([\d.]+)', technical_result)
            current_price_match = re.search(r'Current Price: \$([\d.]+)', technical_result)
            trend_match = re.search(r'Trend: (\w+)', technical_result)
            signal_strength_match = re.search(r'Signal Strength: (\w+)', technical_result)
            
            if not all([entry_match, stop_match, target_match, current_price_match]):
                return f"Error: Could not parse technical analysis results.\n\n{technical_result}"
            
            entry_price = float(entry_match.group(1))
            stop_loss = float(stop_match.group(1))
            target_price = float(target_match.group(1))
            current_price = float(current_price_match.group(1))
            trend = trend_match.group(1) if trend_match else "UNKNOWN"
            signal_strength = signal_strength_match.group(1) if signal_strength_match else "MODERATE"
            
            # Ensure trend and signal_strength are strings, not None
            if trend is None:
                trend = "UNKNOWN"
            if signal_strength is None:
                signal_strength = "MODERATE"
            
            # Calculate position size
            position_info = TradingStrategyAnalyzer.calculate_position_size(
                account_value=account_value,
                entry_price=entry_price,
                stop_loss=stop_loss,
                risk_per_trade_pct=risk_per_trade_pct
            )
            
            # Get stock info for forecasts
            ticker = yf.Ticker(ticker_symbol)
            try:
                info = ticker.info
                company_name = info.get('longName', ticker_symbol) if info else ticker_symbol
            except:
                company_name = ticker_symbol
            
            # Calculate price forecast
            risk = entry_price - stop_loss
            reward = target_price - entry_price
            forecast_pct = (reward / entry_price) * 100
            
            # Determine forecast direction and timeframe
            # Ensure we're working with strings
            trend_str = str(trend).upper() if trend else "UNKNOWN"
            signal_str = str(signal_strength).upper() if signal_strength else "MODERATE"
            
            if trend_str == "BULLISH" and signal_str in ["STRONG", "MODERATE"]:
                forecast_direction = "UP"
                forecast_timeframe = "1-3 months"
                forecast_confidence = "HIGH" if signal_str == "STRONG" else "MODERATE"
            elif trend_str == "BEARISH" or signal_str == "WEAK":
                forecast_direction = "DOWN or SIDEWAYS"
                forecast_timeframe = "Wait for better entry"
                forecast_confidence = "LOW"
            else:
                forecast_direction = "SIDEWAYS"
                forecast_timeframe = "1-2 months"
                forecast_confidence = "MODERATE"
            
            # Build comprehensive output
            output = f"""
╔══════════════════════════════════════════════════════════════╗
║     COMPREHENSIVE STOCK ANALYSIS - {ticker_symbol:^10}          ║
╚══════════════════════════════════════════════════════════════╝

📊 COMPANY: {company_name} ({ticker_symbol})
   Current Trend: {trend_str}
   Signal Strength: {signal_str}
"""
            
            # Add company research if available
            if company_research:
                output += f"""
🔍 COMPANY RESEARCH & HEALTH ANALYSIS:
{company_research}

"""
            
            # Add technical analysis
            output += technical_result
            
            # Add position sizing
            output += f"""

💰 POSITION SIZING RECOMMENDATIONS:
   Account Value: ${account_value:,.2f}
   Risk per Trade: {risk_per_trade_pct}% of account (${account_value * risk_per_trade_pct / 100:,.2f})
   
   📊 RECOMMENDED POSITION:
   • Number of Shares: {position_info['num_shares']} shares
   • Entry Price: ${entry_price:.2f} per share
   • Total Investment: ${position_info['total_cost']:,.2f}
   • Maximum Loss (if stop loss hit): ${position_info['max_loss']:,.2f} ({risk_per_trade_pct}% of account)
   • Potential Profit (if target reached): ${position_info['num_shares'] * reward:,.2f}
   
   • Simple Explanation: Based on your account size, you should buy {position_info['num_shares']} shares.
     This way, if the trade goes wrong and hits your stop loss, you'll only lose {risk_per_trade_pct}% of your account.
     Never risk more than you can afford to lose!

📈 PRICE FORECAST:
   Current Price: ${current_price:.2f}
   Forecast Direction: {forecast_direction}
   Expected Move: {abs(forecast_pct):.2f}% {'up' if forecast_direction == 'UP' else 'down' if 'DOWN' in forecast_direction else ''}
   Target Price: ${target_price:.2f}
   Timeframe: {forecast_timeframe}
   Confidence: {forecast_confidence}
   
   • Simple Explanation: Based on technical analysis, the stock is expected to move {forecast_direction.lower()} 
     toward ${target_price:.2f} over the next {forecast_timeframe}. However, remember that forecasts are not 
     guarantees - the stock market is unpredictable!

🎯 WHEN TO BUY:
"""
            
            # Determine buy recommendation (use string versions)
            if signal_str == "STRONG" and trend_str == "BULLISH":
                buy_recommendation = "✅ STRONG BUY - Multiple indicators agree, good time to enter"
                buy_timing = "Buy now or on any small pullback"
            elif signal_str == "MODERATE" and trend_str == "BULLISH":
                buy_recommendation = "✅ BUY - Good opportunity, but watch for confirmation"
                buy_timing = "Buy on pullback to support or moving average"
            elif signal_str == "WEAK" or trend_str == "BEARISH":
                buy_recommendation = "⏸️ WAIT - Weak signals or bearish trend detected"
                buy_timing = "Wait for trend reversal or stronger bullish signals"
            else:
                buy_recommendation = "⚠️ CAUTION - Mixed signals, proceed carefully"
                buy_timing = "Wait for clearer signals or better entry point"
            
            output += f"""   Recommendation: {buy_recommendation}
   Best Entry: {buy_timing}
   Entry Price: ${entry_price:.2f}
   Stop Loss: ${stop_loss:.2f} (safety net - exit here if wrong)
   Target Price: ${target_price:.2f} (take profit here)

👶 KID-FRIENDLY EXPLANATION:
"""
            
            # Kid-friendly explanation (use string versions)
            if signal_str == "STRONG" and trend_str == "BULLISH":
                kid_explanation = f"""
   🎉 GOOD NEWS! This stock looks like a good opportunity right now!
   
   • What's happening: The stock is in an UPTREND (going up) and multiple indicators agree
   • What to do: This is a good time to BUY, but remember:
     - Only invest money you can afford to lose
     - Buy {position_info['num_shares']} shares at ${entry_price:.2f} each
     - Set a stop loss at ${stop_loss:.2f} (like a safety net)
     - Target price is ${target_price:.2f} (where you might want to sell)
   
   • Think of it like: You're buying a toy that might increase in value. You set a safety 
     net (stop loss) so if it goes wrong, you don't lose too much. And you have a goal 
     price (target) where you might want to sell and take your profit.
   
   • Next steps: 
     1. Make sure you have ${position_info['total_cost']:,.2f} available
     2. Buy {position_info['num_shares']} shares at ${entry_price:.2f} or better
     3. Set your stop loss at ${stop_loss:.2f}
     4. Watch the stock and consider selling at ${target_price:.2f}
"""
            elif signal_str == "WEAK" or trend_str == "BEARISH":
                kid_explanation = f"""
   ⚠️ WAIT! This stock is not a good buy right now.
   
   • What's happening: The stock is in a DOWNTREND (going down) or signals are weak
   • What to do: WAIT and watch. Don't buy yet!
   
   • Think of it like: You're at a store and the item you want is on sale, but it might 
     go on an even better sale later. It's better to wait for a clearer sign that it's 
     the right time to buy.
   
   • What to watch for:
     - Stock price stops falling and starts rising
     - Multiple indicators turn bullish (positive)
     - Price moves above key moving averages
   
   • Next steps:
     1. Don't buy right now - wait for better signals
     2. Check back in a few days or weeks
     3. Look for the stock to show signs of recovery
     4. Consider looking at other stocks with stronger buy signals
"""
            else:
                kid_explanation = f"""
   🤔 MIXED SIGNALS - Be careful!
   
   • What's happening: Some indicators say buy, others say wait - they don't all agree
   • What to do: PROCEED WITH CAUTION or wait for clearer signals
   
   • Think of it like: You're trying to decide if you should buy something, but half 
     your friends say yes and half say no. It's better to wait until more people agree 
     or you get more information.
   
   • Next steps:
     1. Wait for stronger confirmation (2+ indicators agreeing)
     2. Or if you do buy, use a smaller position size
     3. Be extra careful with your stop loss
     4. Consider waiting a few days for clearer signals
"""
            
            output += kid_explanation
            
            output += f"""

📋 SUMMARY - WHAT TO DO NEXT:
"""
            
            # Action items (use string versions)
            if signal_str == "STRONG" and trend_str == "BULLISH":
                output += f"""   1. ✅ This is a STRONG BUY opportunity
   2. 💰 Prepare ${position_info['total_cost']:,.2f} to buy {position_info['num_shares']} shares
   3. 📈 Buy at ${entry_price:.2f} or better
   4. 🛡️ Set stop loss at ${stop_loss:.2f} (protects you from big losses)
   5. 🎯 Target price: ${target_price:.2f} (consider selling here)
   6. ⏰ Timeframe: {forecast_timeframe}
   7. 📊 Expected move: {abs(forecast_pct):.2f}% {'up' if forecast_direction == 'UP' else ''}
"""
            elif signal_str == "WEAK" or trend_str == "BEARISH":
                output += f"""   1. ⏸️ WAIT - Not a good time to buy
   2. 👀 Watch for trend reversal or stronger signals
   3. 📊 Check back in a few days/weeks
   4. 🔍 Look for other stocks with better opportunities
   5. 📚 Use this time to learn more about the company
"""
            else:
                output += f"""   1. ⚠️ CAUTION - Mixed signals
   2. 🤔 Wait for stronger confirmation
   3. 💡 If buying, use smaller position size
   4. 🛡️ Be extra careful with stop loss
   5. 📊 Monitor closely for clearer signals
"""
            
            output += f"""
⚠️  IMPORTANT REMINDERS:
   • Never invest more than you can afford to lose
   • Always use stop losses (safety nets)
   • Past performance doesn't guarantee future results
   • Do your own research before investing
   • Consider your risk tolerance
   • This is not financial advice - just analysis!

"""
            
            return output
            
        except Exception as e:
            return f"Error in comprehensive analysis for {ticker_symbol}: {str(e)}"


if __name__ == "__main__":
    # Example usage:
    start_date = "2011-01-01"
    end_date = "2012-12-31"
    ticker = "MSFT"
    # BackTraderUtils.back_test(
    #     ticker, start_date, end_date, "SMA_CrossOver", {"fast": 10, "slow": 30}
    # )
    # BackTraderUtils.back_test(
    #     ticker,
    #     start_date,
    #     end_date,
    #     "test_module:TestStrategy",
    #     {"exitbars": 5},
    # )
    
    # Test Trading Strategy Analyzer
    print("Testing Trading Strategy Analyzer...")
    result = TradingStrategyAnalyzer.analyze_trading_opportunity(
        ticker_symbol="AAPL",
        period="6mo",
        risk_reward_ratio=2.0,
        stop_loss_method="atr"
    )
    print(result)
