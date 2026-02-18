"""
AI Image Detection Dataset Dashboard
Interactive Streamlit dashboard for dataset statistics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="AI Image Dataset Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">📊 AI Image Detection Dataset Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    """Load dataset statistics"""
    try:
        with open('dataset_statistics.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Mock data for development
        return [
            {
                "dataset": "CIFAKE",
                "generator": "Unknown (mixed)",
                "real_source": "CIFAR-10 (real photos)",
                "train_real": 50000,
                "train_fake": 50000,
                "test_real": 10000,
                "test_fake": 10000,
                "total": 120000
            },
            {
                "dataset": "Stable Diffusion Faces",
                "generator": "Stable Diffusion",
                "real_source": "None (all AI-generated)",
                "train_real": 0,
                "train_fake": 7200,
                "test_real": 0,
                "test_fake": 1800,
                "total": 9000
            },
            {
                "dataset": "AI-Generated vs Real",
                "generator": "Multiple (GAN-based)",
                "real_source": "Mixed real photos",
                "train_real": 24000,
                "train_fake": 23999,
                "test_real": 6000,
                "test_fake": 6000,
                "total": 59999
            },
            {
                "dataset": "DiffusionDB",
                "generator": "Stable Diffusion",
                "real_source": "None (all AI-generated)",
                "train_real": 0,
                "train_fake": 1968,
                "test_real": 0,
                "test_fake": 492,
                "total": 2460
            },
            {
                "dataset": "AIGI-Holmes",
                "generator": "Multiple (FLUX, SD, DALL-E, Midjourney)",
                "real_source": "Real camera photos",
                "train_real": 33850,
                "train_fake": 31147,
                "test_real": 50000,
                "test_fake": 50000,
                "total": 164997
            },
            {
                "dataset": "BR-Gen",
                "generator": "AI Inpainting",
                "real_source": "COCO/ImageNet/Places (not included)",
                "train_real": 0,
                "train_fake": 24000,
                "test_real": 0,
                "test_fake": 6000,
                "total": 30000
            }
        ]

data = load_data()
df = pd.DataFrame(data)

# Calculate totals
total_images = df['total'].sum()
total_real = (df['train_real'] + df['test_real']).sum()
total_fake = (df['train_fake'] + df['test_fake']).sum()

# Overview metrics
st.header("📈 Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📚 Total Datasets",
        value=len(df),
        help="Number of datasets in collection"
    )

with col2:
    st.metric(
        label="🖼️ Total Images",
        value=f"{total_images:,}",
        help="Total number of images across all datasets"
    )

with col3:
    st.metric(
        label="✅ Real Images",
        value=f"{total_real:,}",
        help="Total authentic/real images"
    )

with col4:
    st.metric(
        label="🤖 AI-Generated Images",
        value=f"{total_fake:,}",
        help="Total AI-generated/fake images"
    )

st.markdown("---")

# Dataset breakdown
st.header("📊 Dataset Breakdown")

col1, col2 = st.columns([2, 1])

with col1:
    # Bar chart - images per dataset
    fig_bar = go.Figure()
    
    fig_bar.add_trace(go.Bar(
        name='Train Real',
        x=df['dataset'],
        y=df['train_real'],
        marker_color='#2ecc71'
    ))
    
    fig_bar.add_trace(go.Bar(
        name='Train Fake',
        x=df['dataset'],
        y=df['train_fake'],
        marker_color='#e74c3c'
    ))
    
    fig_bar.add_trace(go.Bar(
        name='Test Real',
        x=df['dataset'],
        y=df['test_real'],
        marker_color='#3498db'
    ))
    
    fig_bar.add_trace(go.Bar(
        name='Test Fake',
        x=df['dataset'],
        y=df['test_fake'],
        marker_color='#f39c12'
    ))
    
    fig_bar.update_layout(
        title='Images per Dataset by Category',
        xaxis_title='Dataset',
        yaxis_title='Number of Images',
        barmode='stack',
        height=500
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    # Pie chart - total distribution
    fig_pie = px.pie(
        values=[total_real, total_fake],
        names=['Real Images', 'AI-Generated Images'],
        title='Overall Real vs Fake Distribution',
        color_discrete_map={
            'Real Images': '#2ecc71',
            'AI-Generated Images': '#e74c3c'
        },
        hole=0.4
    )
    
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=500)
    
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# Generators breakdown
st.header("🤖 AI Generators Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Generators Used")
    
    generator_data = df[['dataset', 'generator']].copy()
    
    for idx, row in generator_data.iterrows():
        with st.expander(f"📁 {row['dataset']}"):
            st.write(f"**Generator:** {row['generator']}")
            st.write(f"**Images:** {df.iloc[idx]['total']:,}")

with col2:
    st.subheader("Real Image Sources")
    
    source_data = df[['dataset', 'real_source']].copy()
    
    for idx, row in source_data.iterrows():
        with st.expander(f"📁 {row['dataset']}"):
            st.write(f"**Source:** {row['real_source']}")
            real_count = df.iloc[idx]['train_real'] + df.iloc[idx]['test_real']
            st.write(f"**Real Images:** {real_count:,}")

st.markdown("---")

# Detailed dataset table
st.header("📋 Detailed Statistics")

# Create detailed dataframe
detailed_df = df.copy()
detailed_df['Real Total'] = detailed_df['train_real'] + detailed_df['test_real']
detailed_df['Fake Total'] = detailed_df['train_fake'] + detailed_df['test_fake']
detailed_df['Real %'] = (detailed_df['Real Total'] / detailed_df['total'] * 100).round(1)
detailed_df['Fake %'] = (detailed_df['Fake Total'] / detailed_df['total'] * 100).round(1)

display_df = detailed_df[[
    'dataset', 
    'train_real', 
    'train_fake', 
    'test_real', 
    'test_fake',
    'Real Total',
    'Fake Total',
    'total',
    'Real %',
    'Fake %',
    'generator',
    'real_source'
]]

# Format numbers
display_df['train_real'] = display_df['train_real'].apply(lambda x: f"{x:,}")
display_df['train_fake'] = display_df['train_fake'].apply(lambda x: f"{x:,}")
display_df['test_real'] = display_df['test_real'].apply(lambda x: f"{x:,}")
display_df['test_fake'] = display_df['test_fake'].apply(lambda x: f"{x:,}")
display_df['Real Total'] = display_df['Real Total'].apply(lambda x: f"{x:,}")
display_df['Fake Total'] = display_df['Fake Total'].apply(lambda x: f"{x:,}")
display_df['total'] = display_df['total'].apply(lambda x: f"{x:,}")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# Key insights
st.header("💡 Key Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **Largest Dataset**
    
    AIGI-Holmes with {df[df['dataset'] == 'AIGI-Holmes']['total'].values[0]:,} images
    """)

with col2:
    balance_ratio = (total_real / total_fake) if total_fake > 0 else 0
    st.warning(f"""
    **Class Balance**
    
    Real:Fake ratio is {balance_ratio:.2f}:1
    """)

with col3:
    datasets_with_real = len(df[df['train_real'] + df['test_real'] > 0])
    st.success(f"""
    **Real Images Available**
    
    {datasets_with_real} out of {len(df)} datasets include real images
    """)

# Generator summary
st.markdown("---")
st.header("🎨 Generator Summary")

generators_info = """
### Identified Generators:

1. **Stable Diffusion** (2 datasets)
   - Stable Diffusion Faces: 9,000 images
   - DiffusionDB: 2,460 images
   
2. **Multiple Generators** (2 datasets)
   - AIGI-Holmes: Includes FLUX, Stable Diffusion, DALL-E, Midjourney
   - AI-Generated vs Real: GAN-based generators
   
3. **AI Inpainting** (1 dataset)
   - BR-Gen: Broad-region manipulation
   
4. **Unknown/Mixed** (1 dataset)
   - CIFAKE: Mixed generators

### Real Image Sources:

1. **Camera Photos**
   - AIGI-Holmes: Real camera photographs
   
2. **Public Datasets**
   - CIFAKE: CIFAR-10 dataset
   - AI-Generated vs Real: Mixed real photos
   - BR-Gen: COCO/ImageNet/Places (not included, need separate download)
   
3. **No Real Images** (Fake-only datasets)
   - Stable Diffusion Faces
   - DiffusionDB
"""

st.markdown(generators_info)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>AI Image Detection Dataset Dashboard</strong></p>
    <p>Data Science Team | Last Updated: January 2026</p>
    <p>S3 Bucket: ad-datascience/image-datasets/</p>
</div>
""", unsafe_allow_html=True)
