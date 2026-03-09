"""
Chip distribution analysis data models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ChipConcentration:
    concentration_index: float
    peak_price: float
    peak_density: float
    cost_area_width: float
    main_cost_area: Tuple[float, float]
    secondary_peaks: List[Tuple[float, float]]


@dataclass
class ChipFlowDynamics:
    flow_direction: str
    flow_intensity: float
    cost_shift: float
    distribution_change: float
    new_chip_ratio: float
    old_chip_ratio: float


@dataclass
class WinningProbability:
    current_win_prob: float
    break_up_prob: float
    break_down_prob: float
    hold_prob: float
    risk_reward_ratio: float
    optimal_entry: float
    optimal_exit: float


@dataclass
class CostAreaAnalysis:
    support_areas: List[Tuple[float, float, float]]
    resistance_areas: List[Tuple[float, float, float]]
    equilibrium_price: float
    cost_pressure: str
    pressure_strength: float
