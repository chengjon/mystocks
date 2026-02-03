import collections

class TDSequential:
    def __init__(self, closes, highs, lows):
        """
        初始化 TD Sequential 指标计算器。
        :param closes: 收盘价序列 (list 或 array)
        :param highs: 最高价序列 (list 或 array)
        :param lows: 最低价序列 (list 或 array)
        """
        self.closes = closes
        self.highs = highs
        self.lows = lows
        self.num_bars = len(closes)

        # TD Setup 状态
        self.buy_setup_window = collections.deque(maxlen=9) # 存储买入 Setup 条件是否满足 (True/False)
        self.sell_setup_window = collections.deque(maxlen=9) # 存储卖出 Setup 条件是否满足 (True/False)
        self._is_buy_setup_active = False # 标记当前是否有买入 Setup 正在形成
        self._buy_setup_start_bar_idx = -1 # 正在形成的买入 Setup 的起始K线索引
        self._is_sell_setup_active = False # 标记当前是否有卖出 Setup 正在形成
        self._sell_setup_start_bar_idx = -1 # 正在形成的卖出 Setup 的起始K线索引

        # TD Countdown 状态
        self._is_buy_countdown_active = False # 标记买入 Countdown 是否激活
        self._buy_countdown_count = 0 # 买入 Countdown 计数
        self._is_sell_countdown_active = False # 标记卖出 Countdown 是否激活
        self._sell_countdown_count = 0 # 卖出 Countdown 计数

        # 存储 Setup 完成时的关键信息，用于 Countdown 的中断判断
        self.buy_setup_completion_info = {'bar_idx': -1, 'high_extreme': -1.0}
        self.sell_setup_completion_info = {'bar_idx': -1, 'low_extreme': -1.0}

        # 存储生成的信号
        self.signals = []

    def _process_td_setup(self, bar_idx):
        """
        处理单根 K 线的 TD Setup 逻辑。
        """
        # TD Setup 需要至少 4 根 K 线之前的数据
        if bar_idx < 4:
            return

        current_close = self.closes[bar_idx]
        prev_4_close = self.closes[bar_idx-4]
        prev_4_high = self.highs[bar_idx-4]
        prev_4_low = self.lows[bar_idx-4]

        # --- 买入 Setup (Buy Setup) 逻辑 ---
        is_buy_condition_met = (current_close < prev_4_close)

        # 仅当 Setup 可能活跃或刚刚开始时才检查并更新窗口和状态
        # 这里的逻辑优化：即使 Setup 不活跃，但当前K线满足条件，也应尝试启动新的 Setup
        if not self._is_buy_setup_active and is_buy_condition_met:
            self._is_buy_setup_active = True
            self._buy_setup_start_bar_idx = bar_idx
            self.buy_setup_window.clear() # 开始新的窗口
            self.buy_setup_window.append(is_buy_condition_met)
        elif self._is_buy_setup_active:
            # 先检查中断条件
            if current_close > prev_4_high: # 买入 Setup 中断
                self.signals.append(f"Bar {bar_idx}: Buy Setup CANCELLED. Price broke above High(i-4).")
                self._reset_buy_setup_state()
            else:
                # 未中断，更新 Setup 状态
                self.buy_setup_window.append(is_buy_condition_met)

                # 检查买入 Setup 是否完成
                if len(self.buy_setup_window) == 9:
                    num_conditions_met = sum(self.buy_setup_window)
                    if num_conditions_met >= 7:
                        # 买入 Setup 完成
                        self.signals.append(f"Bar {bar_idx}: Buy Setup COMPLETED with {num_conditions_met}/9 conditions met (potential bearish exhaustion).")
                        self.buy_setup_completion_info['bar_idx'] = bar_idx
                        # 计算 Setup 期间最高价，用于 Countdown 的中断判断
                        # Setup 期间的 K 线是从 _buy_setup_start_bar_idx 到 bar_idx
                        self.buy_setup_completion_info['high_extreme'] = max(self.highs[self._buy_setup_start_bar_idx : bar_idx + 1])
                        self._is_buy_countdown_active = True # 激活买入 Countdown
                        self._buy_countdown_count = 0 # 重置 Countdown 计数
                    self._reset_buy_setup_state() # Setup 完成后重置，准备下一个 Setup


        # --- 卖出 Setup (Sell Setup) 逻辑 ---
        is_sell_condition_met = (current_close > prev_4_close)

        # 仅当 Setup 可能活跃或刚刚开始时才检查并更新窗口和状态
        if not self._is_sell_setup_active and is_sell_condition_met:
            self._is_sell_setup_active = True
            self._sell_setup_start_bar_idx = bar_idx
            self.sell_setup_window.clear()
            self.sell_setup_window.append(is_sell_condition_met)
        elif self._is_sell_setup_active:
            # 先检查中断条件
            if current_close < prev_4_low: # 卖出 Setup 中断
                self.signals.append(f"Bar {bar_idx}: Sell Setup CANCELLED. Price broke below Low(i-4).")
                self._reset_sell_setup_state()
            else:
                # 未中断，更新 Setup 状态
                self.sell_setup_window.append(is_sell_condition_met)

                # 检查卖出 Setup 是否完成
                if len(self.sell_setup_window) == 9:
                    num_conditions_met = sum(self.sell_setup_window)
                    if num_conditions_met >= 7:
                        # 卖出 Setup 完成
                        self.signals.append(f"Bar {bar_idx}: Sell Setup COMPLETED with {num_conditions_met}/9 conditions met (potential bullish exhaustion).")
                        self.sell_setup_completion_info['bar_idx'] = bar_idx
                        # Setup 期间的 K 线是从 _sell_setup_start_bar_idx 到 bar_idx
                        self.sell_setup_completion_info['low_extreme'] = min(self.lows[self._sell_setup_start_bar_idx : bar_idx + 1])
                        self._is_sell_countdown_active = True # 激活卖出 Countdown
                        self._sell_countdown_count = 0 # 重置 Countdown 计数
                    self._reset_sell_setup_state() # Setup 完成后重置，准备下一个 Setup

    def _reset_buy_setup_state(self):
        self._is_buy_setup_active = False
        self.buy_setup_window.clear()
        self._buy_setup_start_bar_idx = -1
        # Setup 中断/完成也会影响到 Countdown
        self._is_buy_countdown_active = False
        self._buy_countdown_count = 0
        self.buy_setup_completion_info = {'bar_idx': -1, 'high_extreme': -1.0}

    def _reset_sell_setup_state(self):
        self._is_sell_setup_active = False
        self.sell_setup_window.clear()
        self._sell_setup_start_bar_idx = -1
        # Setup 中断/完成也会影响到 Countdown
        self._is_sell_countdown_active = False
        self._sell_countdown_count = 0
        self.sell_setup_completion_info = {'bar_idx': -1, 'low_extreme': -1.0}

    def _process_td_countdown(self, bar_idx):
        """
        处理单根 K 线的 TD Countdown 逻辑。
        """
        # Countdown 需要至少 2 根 K 线之前的数据
        if bar_idx < 2:
            return

        current_close = self.closes[bar_idx]
        prev_2_high = self.highs[bar_idx-2]
        prev_2_low = self.lows[bar_idx-2]

        # --- 买入 Countdown (Buy Countdown) 逻辑 ---
        if self._is_buy_countdown_active:
            # 检查中断条件：收盘价 >= 买入 Setup 期间的最高价
            # 只有当 buy_setup_completion_info['high_extreme'] 被有效设置后才进行中断判断
            if self.buy_setup_completion_info['high_extreme'] != -1.0 and current_close >= self.buy_setup_completion_info['high_extreme']:
                self.signals.append(f"Bar {bar_idx}: Buy Countdown CANCELLED. Price broke above Buy Setup High Extreme ({self.buy_setup_completion_info['high_extreme']}).")
                self._is_buy_countdown_active = False
                self._buy_countdown_count = 0
                self.buy_setup_completion_info = {'bar_idx': -1, 'high_extreme': -1.0} # 重置 Setup 信息
                return # 中断后，当前 K 线不再处理 Countdown

            # 检查买入 Countdown 条件：Close(i) < Low(i-2)
            if current_close < prev_2_low:
                self._buy_countdown_count += 1
                if self._buy_countdown_count == 13:
                    self.signals.append(f"Bar {bar_idx}: Buy Countdown COMPLETED (STRONG BUY SIGNAL - Bearish Reversal)!")
                    self._is_buy_countdown_active = False # Countdown 完成，失活
                    self._buy_countdown_count = 0 # 重置计数
                    self.buy_setup_completion_info = {'bar_idx': -1, 'high_extreme': -1.0} # 重置 Setup 信息

        # --- 卖出 Countdown (Sell Countdown) 逻辑 ---
        if self._is_sell_countdown_active:
            # 检查中断条件：收盘价 <= 卖出 Setup 期间的最低价
            # 只有当 sell_setup_completion_info['low_extreme'] 被有效设置后才进行中断判断
            if self.sell_setup_completion_info['low_extreme'] != -1.0 and current_close <= self.sell_setup_completion_info['low_extreme']:
                self.signals.append(f"Bar {bar_idx}: Sell Countdown CANCELLED. Price broke below Sell Setup Low Extreme ({self.sell_setup_completion_info['low_extreme']}).")
                self._is_sell_countdown_active = False
                self._sell_countdown_count = 0
                self.sell_setup_completion_info = {'bar_idx': -1, 'low_extreme': -1.0} # 重置 Setup 信息
                return # 中断后，当前 K 线不再处理 Countdown

            # 检查卖出 Countdown 条件：Close(i) > High(i-2)
            if current_close > prev_2_high:
                self._sell_countdown_count += 1
                if self._sell_countdown_count == 13:
                    self.signals.append(f"Bar {bar_idx}: Sell Countdown COMPLETED (STRONG SELL SIGNAL - Bullish Reversal)!")
                    self._is_sell_countdown_active = False # Countdown 完成，失活
                    self._sell_countdown_count = 0 # 重置计数
                    self.sell_setup_completion_info = {'bar_idx': -1, 'low_extreme': -1.0} # 重置 Setup 信息

    def run_td_sequential(self):
        """
        运行 TD Sequential 指标计算并返回所有信号。
        """
        if self.num_bars < 9: # 至少需要 9 根 K 线才能完成一个 Setup
            self.signals.append("Not enough data to calculate TD Sequential (requires at least 9 bars).")
            return []

        for i in range(self.num_bars):
            self._process_td_setup(i)
            self._process_td_countdown(i)
        return self.signals

# --- 示例用法 (Dummy Data Example) ---
if __name__ == "__main__":
    # 模拟一些价格数据
    sample_closes = [
        10, 11, 12, 11, 10,  # 0-4
        9, 8, 7, 6, 5,   # 5-9: Potential Buy Setup
        6, 7, 8, 7, 6,   # 10-14
        5, 4, 3, 2, 1,   # 15-19: More down, leading to Buy Countdown
        2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, # 20-32: Buy Countdown completion
        13, 12, 11, 10, 11, 12, 13, 14, 15, 16, # 33-42: Potential Sell Setup
        17, 18, 19, 20, 21, 22, 23, 24, 25, 26, # 43-52: Sell Countdown completion
        25, 24, 23, 22, 21, 20, 19, 18, 17, 16,
    ]
    # 为简化，假设 Highs 和 Lows 与 Closes 接近，或者略有波动
    # 实际应用中需要真实的 OHLC 数据
    sample_highs = [c + 0.5 for c in sample_closes]
    sample_lows = [c - 0.5 for c in sample_closes]

    # 确保数据长度一致
    assert len(sample_closes) == len(sample_highs) == len(sample_lows)

    td_sequential = TDSequential(sample_closes, sample_highs, sample_lows)
    signals = td_sequential.run_td_sequential()

    print("\n--- Generated TD Sequential Signals ---")
    for signal in signals:
        print(signal)

    # 另一个模拟，尝试触发 Sell Setup 和 Countdown
    print("\n--- Testing Sell Setup & Countdown ---")
    sample_closes_sell = [
        10, 11, 12, 13, 14, # 0-4
        15, 16, 17, 18, 19, # 5-9: Potential Sell Setup
        18, 17, 16, 17, 18, # 10-14
        19, 20, 21, 22, 23, # 15-19: More up, leading to Sell Countdown
        22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, # 20-32: Sell Countdown completion
    ]
    sample_highs_sell = [c + 0.5 for c in sample_closes_sell]
    sample_lows_sell = [c - 0.5 for c in sample_closes_sell]
    td_sequential_sell = TDSequential(sample_closes_sell, sample_highs_sell, sample_lows_sell)
    signals_sell = td_sequential_sell.run_td_sequential()

    print("\n--- Generated TD Sequential Signals (Sell Test) ---")
    for signal in signals_sell:
        print(signal)
