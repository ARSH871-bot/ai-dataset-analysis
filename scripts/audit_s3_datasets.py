"""
S3 Dataset Audit Script
Checks structure and file types in all image datasets
"""
import boto3
from collections import defaultdict, Counter
from pathlib import Path
import json

def audit_dataset(bucket, prefix):
    """Audit a single dataset folder"""
    print(f"\n{'='*70}")
    print(f"📊 AUDITING: s3://{bucket}/{prefix}")
    print(f"{'='*70}")
    
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    
    # Statistics
    total_files = 0
    total_size = 0
    file_extensions = Counter()
    folder_structure = defaultdict(int)
    sample_files = []
    
    try:
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            if 'Contents' not in page:
                print("   ⚠️  No files found")
                return None
            
            for obj in page['Contents']:
                key = obj['Key']
                size = obj['Size']
                
                # Skip the prefix itself
                if key == prefix or key == prefix + '/':
                    continue
                
                total_files += 1
                total_size += size
                
                # Get file extension
                ext = Path(key).suffix.lower()
                if ext:
                    file_extensions[ext] += 1
                
                # Get folder structure (first level after prefix)
                relative_path = key.replace(prefix + '/', '', 1)
                parts = relative_path.split('/')
                if len(parts) > 1:
                    folder_structure[parts[0]] += 1
                
                # Collect samples
                if len(sample_files) < 10:
                    sample_files.append(key)
        
        # Print results
        print(f"\n📈 STATISTICS:")
        print(f"   Total Files: {total_files:,}")
        print(f"   Total Size: {total_size / (1024**3):.2f} GB")
        
        print(f"\n📁 FOLDER STRUCTURE:")
        if folder_structure:
            for folder, count in sorted(folder_structure.items()):
                print(f"   {folder}/: {count:,} files")
        else:
            print("   ⚠️  No folder structure (flat hierarchy)")
        
        print(f"\n📄 FILE TYPES:")
        for ext, count in file_extensions.most_common():
            print(f"   {ext}: {count:,} files")
        
        print(f"\n🔍 SAMPLE FILES (first 10):")
        for sample in sample_files[:10]:
            print(f"   {sample}")
        
        # Return audit results
        return {
            "dataset": prefix,
            "total_files": total_files,
            "total_size_gb": round(total_size / (1024**3), 2),
            "folders": dict(folder_structure),
            "extensions": dict(file_extensions),
            "samples": sample_files[:10]
        }
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def check_standardization(audit_results):
    """Check if dataset follows standard train/real, train/fake structure"""
    folders = audit_results.get('folders', {})
    
    # Expected patterns
    standard_patterns = [
        {'train', 'test'},  # train/ and test/
        {'real', 'fake'},   # real/ and fake/
        {'0_real', '1_fake'},  # numbered
    ]
    
    has_train = any('train' in f.lower() for f in folders.keys())
    has_test = any('test' in f.lower() for f in folders.keys())
    has_real = any('real' in f.lower() for f in folders.keys())
    has_fake = any('fake' in f.lower() for f in folders.keys())
    
    issues = []
    
    if not has_train and not has_test:
        issues.append("❌ Missing train/test split")
    
    if not has_real and not has_fake:
        issues.append("❌ Missing real/fake labels")
    
    if len(folders) > 10:
        issues.append(f"⚠️  Too many folders ({len(folders)}) - needs cleanup")
    
    # Check for non-standard folder names
    non_standard = []
    for folder in folders.keys():
        if not any(pattern in folder.lower() for pattern in ['train', 'test', 'real', 'fake', 'val', 'metadata', 'annotation']):
            non_standard.append(folder)
    
    if non_standard:
        issues.append(f"⚠️  Non-standard folders: {', '.join(non_standard[:5])}")
    
    return issues

def main():
    print("="*70)
    print("🔍 S3 DATASET AUDIT - ALL IMAGE DATASETS")
    print("="*70)
    
    BUCKET = "ad-datascience"
    
    # All datasets to audit
    datasets = [
        "image-datasets/cifake_v1_synthetic-real_combined",
        "image-datasets/stable-diffusion-faces_v1_ai-generated",
        "image-datasets/ai-generated-vs-real_v1_fake-real_combined",
        "image-datasets/diffusiondb_v1_prompts_2m",
        "image-datasets/aigi-holmes",
        "image-datasets/br-gen"
    ]
    
    all_audits = []
    all_issues = []
    
    for dataset_prefix in datasets:
        audit_result = audit_dataset(BUCKET, dataset_prefix)
        if audit_result:
            all_audits.append(audit_result)
            
            # Check for issues
            issues = check_standardization(audit_result)
            if issues:
                all_issues.append({
                    "dataset": dataset_prefix,
                    "issues": issues
                })
    
    # Summary report
    print("\n" + "="*70)
    print("📋 AUDIT SUMMARY")
    print("="*70)
    
    print(f"\n✅ Datasets Audited: {len(all_audits)}")
    
    total_files = sum(a['total_files'] for a in all_audits)
    total_size = sum(a['total_size_gb'] for a in all_audits)
    
    print(f"📊 Total Files: {total_files:,}")
    print(f"💾 Total Size: {total_size:.2f} GB")
    
    # Issues report
    print(f"\n🚨 STANDARDIZATION ISSUES FOUND:")
    if all_issues:
        for item in all_issues:
            print(f"\n📁 {item['dataset']}:")
            for issue in item['issues']:
                print(f"   {issue}")
    else:
        print("   ✅ All datasets are standardized!")
    
    # Save audit to file
    audit_file = Path("s3_dataset_audit.json")
    with open(audit_file, 'w') as f:
        json.dump({
            "audits": all_audits,
            "issues": all_issues,
            "summary": {
                "total_datasets": len(all_audits),
                "total_files": total_files,
                "total_size_gb": total_size
            }
        }, f, indent=2)
    
    print(f"\n📄 Full audit saved to: {audit_file}")
    
    # Generate cleanup recommendations
    print("\n" + "="*70)
    print("🛠️  CLEANUP RECOMMENDATIONS")
    print("="*70)
    
    for item in all_issues:
        dataset_name = item['dataset'].split('/')[-1]
        print(f"\n📁 {dataset_name}:")
        print(f"   Current issues: {len(item['issues'])}")
        print(f"   Recommended action: Reorganize to standard structure")
        print(f"   Target structure:")
        print(f"      ├── train/")
        print(f"      │   ├── real/")
        print(f"      │   └── fake/")
        print(f"      ├── test/")
        print(f"      │   ├── real/")
        print(f"      │   └── fake/")
        print(f"      └── metadata/")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Audit interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()