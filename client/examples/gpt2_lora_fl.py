"""
GPT-2 LoRA Federated Learning Example
Demonstrates efficient fine-tuning of LLMs using LoRA in federated setting

This example shows:
1. Loading GPT-2 (124M parameters)
2. Injecting LoRA adapters (~300K trainable parameters, ~400x compression)
3. Federated learning across multiple clients
4. Compression benefits for model transfers

Requirements:
    pip install transformers datasets
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
import numpy as np
import sys
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from client.federx_client.client import FederatedClient
from client.federx_client.adapters.lora import LoRAAdapter
from client.federx_client.utils.serialization import serialize_weights, get_compression_stats

try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config
    from datasets import load_dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("⚠️  transformers or datasets not installed")
    print("Install with: pip install transformers datasets")
    TRANSFORMERS_AVAILABLE = False


def create_gpt2_model(model_size='gpt2', use_pretrained=True):
    """
    Create GPT-2 model
    
    Args:
        model_size: 'gpt2' (124M), 'gpt2-medium' (355M), 'gpt2-large' (774M)
        use_pretrained: Load pretrained weights or random init
    
    Returns:
        model, tokenizer
    """
    if use_pretrained:
        print(f"📥 Loading pretrained {model_size}...")
        model = GPT2LMHeadModel.from_pretrained(model_size)
        tokenizer = GPT2Tokenizer.from_pretrained(model_size)
    else:
        print(f"🎲 Creating random {model_size}...")
        config = GPT2Config.from_pretrained(model_size)
        model = GPT2LMHeadModel(config)
        tokenizer = GPT2Tokenizer.from_pretrained(model_size)
    
    # Set padding token
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = model.config.eos_token_id
    
    return model, tokenizer


def prepare_data(tokenizer, num_samples=1000):
    """
    Prepare a simple text dataset for demonstration
    Using WikiText-2 dataset
    """
    print("📚 Loading WikiText-2 dataset...")
    
    try:
        dataset = load_dataset('wikitext', 'wikitext-2-raw-v1', split='train')
    except Exception as e:
        print(f"⚠️  Could not load dataset: {e}")
        print("Creating synthetic dataset...")
        # Fallback: create synthetic data
        dataset = [
            {"text": f"This is sample text number {i}. " * 10}
            for i in range(num_samples)
        ]
    
    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples['text'] if 'text' in examples else examples,
            padding='max_length',
            truncation=True,
            max_length=128,
            return_tensors='pt'
        )
    
    # Take subset
    if isinstance(dataset, list):
        texts = dataset[:num_samples]
        tokenized = tokenizer(
            [t['text'] if isinstance(t, dict) else t for t in texts],
            padding='max_length',
            truncation=True,
            max_length=128,
            return_tensors='pt'
        )
    else:
        subset = dataset.select(range(min(num_samples, len(dataset))))
        tokenized = tokenize_function(subset)
    
    return tokenized


def train_local(model, train_data, device, epochs=1, lr=5e-4):
    """Train model locally for a few epochs"""
    model.train()
    model = model.to(device)
    
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=lr
    )
    
    # Create simple dataloader
    input_ids = train_data['input_ids']
    attention_mask = train_data['attention_mask']
    
    dataset = torch.utils.data.TensorDataset(input_ids, attention_mask)
    loader = DataLoader(dataset, batch_size=4, shuffle=True)
    
    total_loss = 0
    steps = 0
    
    print(f"  Training for {epochs} epoch(s)...")
    for epoch in range(epochs):
        for batch_idx, (input_ids_batch, attention_mask_batch) in enumerate(loader):
            input_ids_batch = input_ids_batch.to(device)
            attention_mask_batch = attention_mask_batch.to(device)
            
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(
                input_ids=input_ids_batch,
                attention_mask=attention_mask_batch,
                labels=input_ids_batch  # Language modeling: predict next token
            )
            
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            steps += 1
            
            if batch_idx % 10 == 0:
                print(f"    Step {batch_idx}, Loss: {loss.item():.4f}")
    
    avg_loss = total_loss / steps if steps > 0 else 0
    return avg_loss


def federated_training(args):
    """Main federated learning loop with LoRA"""
    
    if not TRANSFORMERS_AVAILABLE:
        print("❌ transformers library not available. Exiting.")
        return
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"🖥️  Using device: {device}\n")
    
    print("="*80)
    print("🚀 GPT-2 LoRA FEDERATED LEARNING")
    print("="*80)
    
    # 1. Create base model
    model, tokenizer = create_gpt2_model('gpt2', use_pretrained=args.pretrained)
    
    # 2. Setup LoRA
    print(f"\n📝 Setting up LoRA (rank={args.rank}, alpha={args.alpha})...")
    lora_adapter = LoRAAdapter(
        rank=args.rank,
        alpha=args.alpha,
        dropout=0.05,
        target_modules=['c_attn', 'c_proj']  # GPT-2 attention modules
    )
    
    # Inject LoRA layers
    num_lora = lora_adapter.inject_lora(model, verbose=True)
    print(f"\n✅ Injected {num_lora} LoRA layers")
    
    # 3. Prepare data
    print(f"\n📊 Preparing dataset...")
    train_data = prepare_data(tokenizer, num_samples=args.num_samples)
    
    # Split data across clients
    num_samples = len(train_data['input_ids'])
    samples_per_client = num_samples // args.num_clients
    
    print(f"   Total samples: {num_samples}")
    print(f"   Samples per client: {samples_per_client}")
    
    # 4. Extract initial LoRA weights
    print(f"\n🔍 Analyzing weight compression...")
    initial_weights = lora_adapter.get_weights(model)
    
    # Show compression stats
    stats_no_compression = get_compression_stats(initial_weights)
    print(f"\n📦 Weight Transfer Sizes:")
    print(f"   Original (no compression): {stats_no_compression['original_size_mb']:.2f} MB")
    
    serialized_compressed = serialize_weights(initial_weights, compression='zlib')
    compressed_size_mb = len(serialized_compressed.encode('utf-8')) / (1024 * 1024)
    print(f"   With zlib compression: {compressed_size_mb:.2f} MB")
    print(f"   Compression ratio: {stats_no_compression['compression_ratio']:.2f}x")
    print(f"   Space saved: {stats_no_compression['space_saved_percent']:.1f}%")
    
    # 5. Federated training rounds
    print(f"\n{'='*80}")
    print(f"🔄 Starting Federated Learning ({args.num_rounds} rounds)")
    print(f"{'='*80}")
    
    for round_num in range(args.num_rounds):
        print(f"\n📍 Round {round_num + 1}/{args.num_rounds}")
        print("-" * 80)
        
        round_weights = []
        
        # Each client trains locally
        for client_id in range(args.num_clients):
            print(f"\n  Client {client_id + 1}/{args.num_clients}:")
            
            # Get client's data slice
            start_idx = client_id * samples_per_client
            end_idx = start_idx + samples_per_client
            
            client_data = {
                'input_ids': train_data['input_ids'][start_idx:end_idx],
                'attention_mask': train_data['attention_mask'][start_idx:end_idx]
            }
            
            # Train locally
            avg_loss = train_local(model, client_data, device, epochs=args.local_epochs)
            print(f"    Average loss: {avg_loss:.4f}")
            
            # Extract LoRA weights
            client_weights = lora_adapter.get_weights(model)
            round_weights.append(client_weights)
        
        # 6. Aggregate (simple averaging for this demo)
        print(f"\n  🔀 Aggregating {len(round_weights)} client updates...")
        aggregated_weights = {}
        
        for key in round_weights[0].keys():
            # Average weights across clients
            stacked = np.stack([w[key] for w in round_weights])
            aggregated_weights[key] = np.mean(stacked, axis=0)
        
        # 7. Update global model
        lora_adapter.set_weights(model, aggregated_weights)
        print(f"  ✅ Global model updated")
    
    print(f"\n{'='*80}")
    print("✅ Federated Learning Complete!")
    print(f"{'='*80}")
    
    # 8. Optional: Merge LoRA and save
    if args.merge_and_save:
        print("\n💾 Merging LoRA weights into base model...")
        merged_model = lora_adapter.merge_and_unload(model)
        
        output_dir = Path("./gpt2_fl_finetuned")
        output_dir.mkdir(exist_ok=True)
        
        merged_model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        print(f"   Model saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='GPT-2 LoRA Federated Learning')
    
    # Model args
    parser.add_argument('--pretrained', action='store_true', default=False,
                       help='Use pretrained GPT-2 (default: random init)')
    parser.add_argument('--rank', type=int, default=8,
                       help='LoRA rank (default: 8)')
    parser.add_argument('--alpha', type=int, default=16,
                       help='LoRA alpha (default: 16)')
    
    # Data args
    parser.add_argument('--num-samples', type=int, default=500,
                       help='Total training samples (default: 500)')
    
    # FL args
    parser.add_argument('--num-clients', type=int, default=3,
                       help='Number of clients (default: 3)')
    parser.add_argument('--num-rounds', type=int, default=2,
                       help='Number of FL rounds (default: 2)')
    parser.add_argument('--local-epochs', type=int, default=1,
                       help='Local training epochs (default: 1)')
    
    # Output args
    parser.add_argument('--merge-and-save', action='store_true',
                       help='Merge LoRA and save final model')
    
    args = parser.parse_args()
    
    federated_training(args)


if __name__ == '__main__':
    main()
