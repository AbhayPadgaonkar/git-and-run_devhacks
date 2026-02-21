"""Scikit-learn adapter for federated learning"""
from typing import Dict, Any
import numpy as np
from .base import BaseFLModel

try:
    from sklearn.base import BaseEstimator
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class SklearnAdapter(BaseFLModel):
    """Adapter for scikit-learn models"""
    
    def __init__(self):
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn not installed. Install with: pip install scikit-learn")
    
    def get_weights(self, model: BaseEstimator) -> Dict[str, np.ndarray]:
        """
        Extract weights from scikit-learn model
        
        Supports:
        - Linear models (LinearRegression, LogisticRegression, etc.)
        - MLPClassifier/MLPRegressor (neural networks)
        - SGDClassifier/SGDRegressor
        
        Args:
            model: scikit-learn estimator
            
        Returns:
            Dictionary of model parameters as numpy arrays
        """
        weights_dict = {}
        
        # Linear models (coef_ and intercept_)
        if hasattr(model, 'coef_'):
            weights_dict['coef'] = np.array(model.coef_).copy()
        
        if hasattr(model, 'intercept_'):
            weights_dict['intercept'] = np.array(model.intercept_).copy()
        
        # MLP (multi-layer perceptron) - has multiple coefs and intercepts
        if hasattr(model, 'coefs_'):
            for i, coef in enumerate(model.coefs_):
                weights_dict[f'layer_{i}_coef'] = np.array(coef).copy()
        
        if hasattr(model, 'intercepts_'):
            for i, intercept in enumerate(model.intercepts_):
                weights_dict[f'layer_{i}_intercept'] = np.array(intercept).copy()
        
        # Tree-based models need special handling (not typical for FL)
        if hasattr(model, 'estimators_'):
            # For ensemble methods - would need custom logic
            pass
        
        if not weights_dict:
            raise ValueError(
                f"Model type {type(model).__name__} is not supported. "
                "Supported: LinearRegression, LogisticRegression, MLPClassifier, "
                "MLPRegressor, SGDClassifier, SGDRegressor"
            )
        
        return weights_dict
    
    def set_weights(self, model: BaseEstimator, weights: Dict[str, np.ndarray]):
        """
        Load weights into scikit-learn model
        
        Args:
            model: scikit-learn estimator (must be fitted first)
            weights: Dictionary of model parameters
        """
        # Check if model is fitted
        if not hasattr(model, 'coef_') and not hasattr(model, 'coefs_'):
            raise ValueError(
                "Model must be fitted before setting weights. "
                "Call model.fit() with a small sample first."
            )
        
        # Linear models
        if 'coef' in weights:
            model.coef_ = weights['coef'].copy()
        
        if 'intercept' in weights:
            model.intercept_ = weights['intercept'].copy()
        
        # MLP models
        if any(k.startswith('layer_') and k.endswith('_coef') for k in weights.keys()):
            model.coefs_ = []
            model.intercepts_ = []
            
            i = 0
            while f'layer_{i}_coef' in weights:
                model.coefs_.append(weights[f'layer_{i}_coef'].copy())
                if f'layer_{i}_intercept' in weights:
                    model.intercepts_.append(weights[f'layer_{i}_intercept'].copy())
                i += 1
    
    def get_output_shape(self, model: BaseEstimator) -> tuple:
        """
        Get output shape of model
        
        Args:
            model: scikit-learn estimator
            
        Returns:
            Output shape tuple
        """
        if hasattr(model, 'n_outputs_'):
            return (model.n_outputs_,)
        elif hasattr(model, 'coef_'):
            if len(model.coef_.shape) == 1:
                return (1,)  # Binary classification
            return (model.coef_.shape[0],)  # Multi-class
        return (0,)  # Unknown
