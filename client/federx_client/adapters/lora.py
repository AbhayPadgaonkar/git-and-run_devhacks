"""
LoRA (Low-Rank Adaptation) adapter for Large Language Models
Enables efficient federated learning of LLMs by training only small adapter matrices
"""
from typing import Dict, Any, Optional
import numpy as np
from .base import BaseFLModel

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class LoRALayer(nn.Module):
    """
    LoRA layer that replaces a standard Linear layer
    Instead of updating W (d x k), we learn A (d x r) and B (r x k) where r << d, k
    
    Forward: h = W_0 x + (B A) x  where W_0 is frozen
    """
    def __init__(
        self, 
        original_layer: nn.Linear,
        rank: int = 8,
        alpha: int = 16,
        dropout: float = 0.0
    ):
        super().__init__()
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank
        
        # Freeze the original weights
        self.original_layer = original_layer
        for param in self.original_layer.parameters():
            param.requires_grad = False
        
        # LoRA low-rank matrices
        in_features = original_layer.in_features
        out_features = original_layer.out_features
        
        # A: (in_features, rank) - initialized with Kaiming uniform
        self.lora_A = nn.Parameter(torch.zeros(in_features, rank))
        nn.init.kaiming_uniform_(self.lora_A, a=np.sqrt(5))
        
        # B: (rank, out_features) - initialized to zero (so initially LoRA has no effect)
        self.lora_B = nn.Parameter(torch.zeros(rank, out_features))
        
        self.dropout = nn.Dropout(dropout) if dropout > 0 else None
    
    def forward(self, x):
        # Original frozen layer
        result = self.original_layer(x)
        
        # LoRA adaptation: x @ A @ B
        if self.dropout:
            x = self.dropout(x)
        
        lora_out = (x @ self.lora_A @ self.lora_B) * self.scaling
        return result + lora_out


class LoRAAdapter(BaseFLModel):
    """
    LoRA adapter for federated learning of large language models
    
    Features:
    - Only trains small adapter matrices (rank r << hidden_dim)
    - 1000x smaller updates compared to full model
    - Compatible with Hugging Face Transformers
    
    Example:
        # 7B parameter model -> ~10MB LoRA weights vs 28GB full weights
        adapter = LoRAAdapter(rank=8, alpha=16)
        adapter.inject_lora(model, target_modules=['q_proj', 'v_proj'])
        weights = adapter.get_weights(model)  # Only LoRA params
    """
    
    def __init__(
        self,
        rank: int = 8,
        alpha: int = 16,
        dropout: float = 0.0,
        target_modules: Optional[list] = None
    ):
        """
        Initialize LoRA adapter
        
        Args:
            rank: Rank of LoRA matrices (lower = more compression, typically 4-64)
            alpha: LoRA scaling factor (typically 16-32)
            dropout: Dropout probability for LoRA layers
            target_modules: List of module names to apply LoRA to
                          (e.g., ['q_proj', 'v_proj', 'k_proj', 'o_proj'])
                          If None, applies to all Linear layers in attention
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not installed. Install with: pip install torch")
        
        self.rank = rank
        self.alpha = alpha
        self.dropout = dropout
        self.target_modules = target_modules or ['q_proj', 'v_proj']  # Default: Query and Value
        self.lora_layers = {}  # Track injected LoRA layers
    
    def inject_lora(self, model: nn.Module, verbose: bool = True):
        """
        Inject LoRA layers into the model
        
        Args:
            model: PyTorch model (typically Hugging Face Transformer)
            verbose: Print injection progress
        
        Returns:
            Number of LoRA layers injected
        """
        lora_count = 0
        
        for name, module in model.named_modules():
            # Check if this is a target module
            should_apply = any(target in name for target in self.target_modules)
            
            if should_apply and isinstance(module, nn.Linear):
                # Get parent module and attribute name
                parent_name = '.'.join(name.split('.')[:-1])
                attr_name = name.split('.')[-1]
                
                parent = model
                if parent_name:
                    for part in parent_name.split('.'):
                        parent = getattr(parent, part)
                
                # Replace with LoRA layer
                lora_layer = LoRALayer(
                    module,
                    rank=self.rank,
                    alpha=self.alpha,
                    dropout=self.dropout
                )
                setattr(parent, attr_name, lora_layer)
                self.lora_layers[name] = lora_layer
                lora_count += 1
                
                if verbose:
                    in_f = module.in_features
                    out_f = module.out_features
                    original_params = in_f * out_f
                    lora_params = in_f * self.rank + self.rank * out_f
                    compression = original_params / lora_params
                    print(f"  ✓ Injected LoRA into {name}: "
                          f"{original_params:,} → {lora_params:,} params "
                          f"({compression:.1f}x compression)")
        
        if verbose:
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            print(f"\n📊 Model Stats:")
            print(f"   Total parameters: {total_params:,}")
            print(f"   Trainable (LoRA): {trainable_params:,}")
            print(f"   Frozen: {total_params - trainable_params:,}")
            print(f"   LoRA layers: {lora_count}")
            print(f"   Reduction: {total_params / max(trainable_params, 1):.1f}x")
        
        return lora_count
    
    def get_weights(self, model: nn.Module) -> Dict[str, np.ndarray]:
        """
        Extract only LoRA weights (not the frozen base model)
        
        Returns:
            Dictionary with only LoRA parameters (A and B matrices)
        """
        lora_weights = {}
        
        for name, param in model.named_parameters():
            # Only extract LoRA parameters (those with 'lora_' in name)
            if param.requires_grad and 'lora_' in name:
                lora_weights[name] = param.detach().cpu().numpy().copy()
        
        return lora_weights
    
    def set_weights(self, model: nn.Module, weights: Dict[str, np.ndarray]):
        """
        Load LoRA weights into model
        
        Args:
            model: Model with LoRA layers already injected
            weights: Dictionary of LoRA parameters
        """
        # Create state dict with only LoRA parameters
        lora_state_dict = {}
        for name, weight in weights.items():
            if 'lora_' in name:
                lora_state_dict[name] = torch.from_numpy(weight)
        
        # Load only LoRA parameters (strict=False allows partial loading)
        model.load_state_dict(lora_state_dict, strict=False)
    
    def merge_and_unload(self, model: nn.Module) -> nn.Module:
        """
        Merge LoRA weights back into original layers and remove LoRA
        Useful for inference or final model export
        
        Returns:
            Model with LoRA merged into base weights
        """
        for name, lora_layer in self.lora_layers.items():
            # Merge LoRA into original weights: W_new = W_0 + (B @ A) * scaling
            with torch.no_grad():
                merged_weight = (
                    lora_layer.original_layer.weight.data +
                    (lora_layer.lora_B @ lora_layer.lora_A.T) * lora_layer.scaling
                )
                lora_layer.original_layer.weight.data = merged_weight
            
            # Replace LoRA layer with original layer
            parent_name = '.'.join(name.split('.')[:-1])
            attr_name = name.split('.')[-1]
            
            parent = model
            if parent_name:
                for part in parent_name.split('.'):
                    parent = getattr(parent, part)
            
            setattr(parent, attr_name, lora_layer.original_layer)
        
        self.lora_layers.clear()
        return model
    
    def get_output_shape(self, model: nn.Module) -> tuple:
        """
        Get output shape of the model
        
        Args:
            model: PyTorch model with LoRA layers
        
        Returns:
            Tuple representing output shape
        """
        # Try to get output shape from the last layer
        last_layer = None
        for module in model.modules():
            if isinstance(module, (nn.Linear, LoRALayer)):
                last_layer = module
        
        if last_layer is not None:
            if isinstance(last_layer, LoRALayer):
                return (last_layer.original_layer.out_features,)
            elif hasattr(last_layer, 'out_features'):
                return (last_layer.out_features,)
        
        return (0,)  # Unknown
    
    def get_compression_ratio(self, model: nn.Module) -> float:
        """Calculate compression ratio (original params / LoRA params)"""
        total = sum(p.numel() for p in model.parameters())
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        return total / max(trainable, 1)
    
    def print_trainable_parameters(self, model: nn.Module):
        """Print detailed breakdown of trainable vs frozen parameters"""
        trainable = 0
        total = 0
        
        for name, param in model.named_parameters():
            total += param.numel()
            if param.requires_grad:
                trainable += param.numel()
                print(f"  ✓ {name}: {param.numel():,} params")
        
        print(f"\nTrainable: {trainable:,} / {total:,} ({100 * trainable / total:.2f}%)")
