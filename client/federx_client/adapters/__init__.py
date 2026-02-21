from .base import BaseFLModel
from .pytorch import PyTorchAdapter

# Optional framework adapters (imported only if framework is available)
try:
    from .tensorflow import TensorFlowAdapter, KerasAdapter
    __all__ = ['BaseFLModel', 'PyTorchAdapter', 'TensorFlowAdapter', 'KerasAdapter']
except ImportError:
    __all__ = ['BaseFLModel', 'PyTorchAdapter']

try:
    from .sklearn import SklearnAdapter
    __all__.append('SklearnAdapter')
except ImportError:
    pass

try:
    from .lora import LoRAAdapter, LoRALayer
    __all__.extend(['LoRAAdapter', 'LoRALayer'])
except ImportError:
    pass
