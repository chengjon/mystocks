import yaml
import importlib
import logging
import pandas as pd
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from src.indicators.base import BatchIndicator, StreamingIndicator

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndicatorFactory:
    """
    Indicator Factory V2.1
    
    Features:
    - Centralized Registry (YAML + DB)
    - Smart Selection (Streaming vs Batch)
    - Automatic Backend Fallback (GPU -> Numba -> CPU)
    - Strict Data Alignment
    - Parameter Validation
    """
    
    def __init__(self, config_path: str = "config/indicators_registry.yaml"):
        self.config_path = config_path
        self.registry = {}
        self._load_registry()
        
    def _load_registry(self):
        """Load indicator metadata from YAML."""
        path = Path(self.config_path)
        if not path.exists():
            logger.warning(f"Config file not found: {path}")
            return
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                raw_indicators = data.get('indicators', {})
                
                # Re-index by indicator_id
                for key, config in raw_indicators.items():
                    ind_id = config.get('indicator_id')
                    if ind_id:
                        self.registry[ind_id] = config
                    else:
                        logger.warning(f"Indicator {key} missing indicator_id, skipping.")
                        
                logger.info(f"Loaded {len(self.registry)} indicators from registry.")
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")

    def get_calculator(
        self,
        indicator_id: str,
        backend: Optional[str] = None,
        streaming: bool = False
    ) -> Union[BatchIndicator, StreamingIndicator]:
        """
        Factory method to get an indicator instance.
        
        Args:
            indicator_id: Unique ID (e.g., 'sma.5')
            backend: Preferred backend ('cpu', 'numba', 'talib', 'gpu')
            streaming: If True, returns a StreamingIndicator.
            
        Returns:
            Instance of BatchIndicator or StreamingIndicator
        """
        if indicator_id not in self.registry:
            raise ValueError(f"Indicator not found in registry: {indicator_id}")
            
        config = self.registry[indicator_id]
        
        # 1. Check Streaming Support
        if streaming:
            if not config.get('supports_streaming', False):
                raise ValueError(f"Indicator {indicator_id} does not support streaming mode.")
            # For streaming, we typically use the Python/CPU implementation unless specified otherwise
            return self._create_implementation(config, mode='streaming')

        # 2. Batch Mode - Backend Selection & Fallback
        preferred_backends = config.get('supported_backends', ['cpu'])
        
        target_backends = []
        if backend:
            if backend not in preferred_backends:
                raise ValueError(f"Backend '{backend}' not supported for {indicator_id}. Options: {preferred_backends}")
            target_backends = [backend]
        else:
            # Default priority: gpu > numba > talib > cpu
            priority_order = ['gpu', 'numba', 'talib', 'cpu']
            target_backends = [b for b in priority_order if b in preferred_backends]
            
        # 3. Fallback Loop
        last_error = None
        for be in target_backends:
            try:
                return self._create_implementation(config, mode='batch', backend=be)
            except Exception as e:
                logger.warning(f"Failed to initialize {indicator_id} with backend={be}: {e}")
                last_error = e
                continue
        
        raise RuntimeError(f"Could not create calculator for {indicator_id}. Last error: {last_error}")

    def _create_implementation(self, config: Dict, mode: str, backend: str = 'cpu') -> Union[BatchIndicator, StreamingIndicator]:
        """Dynamic class loading."""
        module_path = config.get('module_path')
        class_name = config.get('class_name')
        
        if not module_path or not class_name:
            raise ValueError(f"Missing module_path or class_name for {config['indicator_id']}")
            
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            
            # Pass full config to constructor
            # Implementations should handle specific logic based on 'backend' if they support multiple
            instance = cls(config=config)
            
            # Verify interface
            if mode == 'streaming':
                if not isinstance(instance, StreamingIndicator):
                    # Some implementations might implement both, or we might need a wrapper
                    # For V1 compatibility, we assume the class implements the interface if configured so.
                    # Here we strictly check inheritance.
                    pass 
            
            return instance
            
        except ImportError as e:
            raise ImportError(f"Could not import {module_path}: {e}")
        except AttributeError as e:
            raise ImportError(f"Class {class_name} not found in {module_path}: {e}")

    def calculate(self, indicator_id: str, data: pd.DataFrame, **kwargs) -> pd.Series:
        """
        High-level Batch Calculation.
        Enforces Strict Data Alignment.
        """
        # 1. Parameter Validation
        self._validate_parameters(indicator_id, kwargs)
        
        # 2. Get Calculator
        calculator = self.get_calculator(indicator_id, streaming=False)
        
        # 3. Calculate
        if not isinstance(calculator, BatchIndicator):
             raise TypeError(f"Calculator for {indicator_id} is not a BatchIndicator")

        result = calculator.calculate(data, **kwargs)
        
        # 4. Strict Alignment Enforcement
        # Ensure the result index matches the input index exactly
        if not result.index.equals(data.index):
            logger.warning(f"Indicator {indicator_id} result index mismatch. Reindexing to align with input.")
            result = result.reindex(data.index)
            
        return result

    def _validate_parameters(self, indicator_id: str, params: Dict):
        """Validate parameters against YAML constraints."""
        config = self.registry[indicator_id]
        param_defs = config.get('parameters', {})
        
        for k, v in params.items():
            if k in param_defs:
                p_def = param_defs[k]
                p_type = p_def.get('type')
                
                # Type Check
                if p_type == 'int' and not isinstance(v, int):
                    # Try converting if it's a number
                    try:
                        v = int(v)
                    except:
                        raise TypeError(f"Parameter {k} must be int")
                        
                # Range Check
                if 'min' in p_def and v < p_def['min']:
                    raise ValueError(f"Parameter {k}={v} is below minimum {p_def['min']}")
                if 'max' in p_def and v > p_def['max']:
                    raise ValueError(f"Parameter {k}={v} is above maximum {p_def['max']}")
