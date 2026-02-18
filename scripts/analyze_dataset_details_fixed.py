"""
FIXED: Detailed Dataset Analysis
Properly handles S3 pagination to count ALL files
"""
import boto3
from collections import defaultdict, Counter
from pathlib import Path
import json
from tqdm import tqdm

BUCKET = "ad-datascience"
PREFIX = "image-datasets"

def count_images_in_path(s3_client, bucket, prefix):
    """Count all image files in an S3 path with proper pagination"""
    paginator = s3_client.get_paginator('list_objects_v2')
    count = 0
    
    try:
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key'].lower()
                    if any(key.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']):
                        count += 1
    except Exception as e:
        print(f"      Error counting {prefix}: {e}")
    
    return count

def analyze_all_datasets():
    """Analyze all datasets for detailed statistics"""
    
    print("="*70)
    print("📊 DETAILED DATASET ANALYSIS (FIXED)")
    print("="*70)
    
    s3 = boto3.client('s3')
    
    datasets = {
        "cifake_v1_synthetic-real_combined": {
            "name": "CIFAKE",
            "source": "Kaggle",
            "generator": "Unknown (mixed)",
            "real_source": "CIFAR-10 (real photos)"
        },
        "stable-diffusion-faces_v1_ai-generated": {
            "name": "Stable Diffusion Faces",
            "source": "Hugging Face",
            "generator": "Stable Diffusion v1.4",
            "real_source": "None (all AI-generated)"
        },
        "ai-generated-vs-real_v1_fake-real_combined": {
            "name": "AI-Generated vs Real",
            "source": "Kaggle",
            "generator": "Multiple GANs (StyleGAN, ProGAN, etc.)",
            "real_source": "Mixed real photos (various sources)"
        },
        "diffusiondb_v1_prompts_2m": {
            "name": "DiffusionDB",
            "source": "Hugging Face",
            "generator": "Stable Diffusion v1.4",
            "real_source": "None (all AI-generated)"
        },
        "aigi-holmes": {
            "name": "AIGI-Holmes",
            "source": "Hugging Face",
            "generator": "Multiple (FLUX, Stable Diffusion, DALL-E 3, Midjourney v6)",
            "real_source": "Real camera photos (various photographers)"
        },
        "br-gen": {
            "name": "BR-Gen",
            "source": "Google Drive",
            "generator": "AI Inpainting (DeepFill, EdgeConnect, CoModGAN)",
            "real_source": "COCO/ImageNet/Places365 (not included - need separate download)"
        }
    }
    
    results = []
    
    for dataset_key, info in datasets.items():
        print(f"\n{'='*70}")
        print(f"📦 Analyzing: {info['name']}")
        print(f"{'='*70}")
        
        dataset_prefix = f"{PREFIX}/{dataset_key}"
        
        # Count files in each category
        stats = {
            "dataset": info['name'],
            "dataset_key": dataset_key,
            "generator": info['generator'],
            "real_source": info['real_source'],
            "source": info['source']
        }
        
        # Define paths to check
        paths = {
            'train_real': f"{dataset_prefix}/train/real/",
            'train_fake': f"{dataset_prefix}/train/fake/",
            'test_real': f"{dataset_prefix}/test/real/",
            'test_fake': f"{dataset_prefix}/test/fake/",
        }
        
        print("   Counting files (this may take a moment)...")
        
        for key, path in paths.items():
            count = count_images_in_path(s3, BUCKET, path)
            stats[key] = count
            print(f"   {key.replace('_', ' ').title()}: {count:,}")
        
        stats['total'] = stats['train_real'] + stats['train_fake'] + stats['test_real'] + stats['test_fake']
        
        print(f"   📊 Total: {stats['total']:,}")
        print(f"   🤖 Generator: {stats['generator']}")
        print(f"   📷 Real Source: {stats['real_source']}")
        
        results.append(stats)
    
    # Save results
    output_file = Path("dataset_statistics.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print("📊 COMPREHENSIVE SUMMARY")
    print(f"{'='*70}")
    
    total_real = sum(r['train_real'] + r['test_real'] for r in results)
    total_fake = sum(r['train_fake'] + r['test_fake'] for r in results)
    total_all = total_real + total_fake
    
    print(f"\n🎯 Overall Statistics:")
    print(f"   Total Real Images: {total_real:,}")
    print(f"   Total Fake Images: {total_fake:,}")
    print(f"   Total All Images: {total_all:,}")
    print(f"   Real/Fake Ratio: {total_real}:{total_fake}")
    print(f"   Real Percentage: {(total_real/total_all*100):.1f}%")
    print(f"   Fake Percentage: {(total_fake/total_all*100):.1f}%")
    
    # Generator breakdown
    print(f"\n🤖 GENERATORS BREAKDOWN:")
    print(f"\n   Stable Diffusion:")
    sd_datasets = [r for r in results if 'Stable Diffusion' in r['generator']]
    sd_total = sum(r['total'] for r in sd_datasets)
    print(f"      • {len(sd_datasets)} datasets, {sd_total:,} images")
    for d in sd_datasets:
        print(f"        - {d['dataset']}: {d['total']:,}")
    
    print(f"\n   Multiple Generators:")
    multi_datasets = [r for r in results if 'Multiple' in r['generator'] or 'FLUX' in r['generator']]
    multi_total = sum(r['total'] for r in multi_datasets)
    print(f"      • {len(multi_datasets)} datasets, {multi_total:,} images")
    for d in multi_datasets:
        print(f"        - {d['dataset']}: {d['total']:,}")
        print(f"          Generators: {d['generator']}")
    
    print(f"\n   GANs (StyleGAN, ProGAN, etc.):")
    gan_datasets = [r for r in results if 'GAN' in r['generator']]
    gan_total = sum(r['total'] for r in gan_datasets)
    print(f"      • {len(gan_datasets)} datasets, {gan_total:,} images")
    for d in gan_datasets:
        print(f"        - {d['dataset']}: {d['total']:,}")
    
    print(f"\n   AI Inpainting:")
    inpaint_datasets = [r for r in results if 'Inpainting' in r['generator']]
    inpaint_total = sum(r['total'] for r in inpaint_datasets)
    print(f"      • {len(inpaint_datasets)} datasets, {inpaint_total:,} images")
    for d in inpaint_datasets:
        print(f"        - {d['dataset']}: {d['total']:,}")
    
    print(f"\n   Unknown/Mixed:")
    unknown_datasets = [r for r in results if 'Unknown' in r['generator']]
    unknown_total = sum(r['total'] for r in unknown_datasets)
    print(f"      • {len(unknown_datasets)} datasets, {unknown_total:,} images")
    
    # Real image sources
    print(f"\n📷 REAL IMAGE SOURCES:")
    print(f"\n   Camera Photos:")
    camera_datasets = [r for r in results if 'camera' in r['real_source'].lower()]
    camera_real = sum(r['train_real'] + r['test_real'] for r in camera_datasets)
    print(f"      • {len(camera_datasets)} datasets, {camera_real:,} real images")
    for d in camera_datasets:
        real_count = d['train_real'] + d['test_real']
        print(f"        - {d['dataset']}: {real_count:,}")
    
    print(f"\n   Public Datasets (CIFAR, COCO, etc.):")
    public_datasets = [r for r in results if any(x in r['real_source'] for x in ['CIFAR', 'COCO', 'ImageNet', 'Places'])]
    public_real = sum(r['train_real'] + r['test_real'] for r in public_datasets)
    print(f"      • {len(public_datasets)} datasets, {public_real:,} real images")
    for d in public_datasets:
        real_count = d['train_real'] + d['test_real']
        print(f"        - {d['dataset']}: {real_count:,}")
        print(f"          Source: {d['real_source']}")
    
    print(f"\n   Mixed/Various Sources:")
    mixed_datasets = [r for r in results if 'Mixed' in r['real_source'] or 'various' in r['real_source'].lower()]
    mixed_real = sum(r['train_real'] + r['test_real'] for r in mixed_datasets)
    print(f"      • {len(mixed_datasets)} datasets, {mixed_real:,} real images")
    
    print(f"\n   No Real Images (Fake-only):")
    no_real = [r for r in results if 'None' in r['real_source']]
    print(f"      • {len(no_real)} datasets (Stable Diffusion Faces, DiffusionDB)")
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    try:
        analyze_all_datasets()
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()