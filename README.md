# Philosophy Unfolded - The Great Learning (大学 / Đại Học)

## Overview

**Philosophy-Unfolded – The Great Learning** is a **Digital Humanities generative framework** that transforms the classical Confucian text *The Great Learning (大学 / Đại Học)* into illustrated moral narratives.  
It bridges **philology, moral reasoning, and visual imagination** through a multimodal AI pipeline combining:

- **Large Language Models** (Gemini 2.5) for narrative generation  
- **Diffusion Models** (Stable Diffusion XL / FLUX.1) for ink-style illustration  
- **Interactive Streamlit App** for real-time exploration and visualization  

This project extends the *Graphilosophy* initiative — originally focused on **knowledge-graph modeling of The Four Books** — into the generative domain, showing how classical wisdom can be interpreted, narrated, and visualized through computational means.

## Installation

```bash
# Clone the repository
git clone https://github.com/LeChau01/philosophy-unfolded-great-learning.git
cd philosophy-unfolded-great-learning

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Set up .env
GOOGLE_API_KEY=
MODEL_TEXT=models/gemini-2.5-pro
HUGGINGFACE_TOKEN=your_hf_token
FAST_MODE=false

# Usage
streamlit run app.py
```
Please find the attached link for more information
- [Video demo](https://www.youtube.com/watch?v=b1ScLcSUyhg)
- [The report with IEEE format](https://drive.google.com/drive/folders/1B3UDgX4xbgjQbwcSdKo_g-HhRJQFyeQy?usp=sharing)



