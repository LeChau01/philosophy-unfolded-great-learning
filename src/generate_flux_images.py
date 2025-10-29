import os
import torch
from PIL import Image, ImageDraw
from dotenv import load_dotenv

load_dotenv()

def generate_flux_images(image_prompts):
    """
    Auto generate comics:
    - FAST_MODE=true → mock image (no render)
    - If GPU + HF token available → use FLUX.1-dev
    - If GPU or token not available → use SDXL-base
    - Automatically number panels if missing
    """

    os.makedirs("outputs", exist_ok=True)

    # FAST MODE: mock preview
    if os.getenv("FAST_MODE", "false").lower() == "true":
        print("⚡ FAST_MODE: Generating mock panels (no diffusion).")
        for i, p in enumerate(image_prompts, start=1):
            panel = p.get("panel") or f"{i:02d}"
            img = Image.new("RGB", (768, 512), "white")
            d = ImageDraw.Draw(img)
            d.text((30, 30), f"Panel {panel}", fill="black")
            prompt = p.get("prompt", "")[:220]
            if len(prompt) > 350:
                prompt = prompt[:350]
            d.text((30, 80), prompt, fill="gray")
            out_path = f"outputs/panel_{panel}_mock.png"
            img.save(out_path)
        print("Mock images saved.")
        return

    # Identify device (GPU / MPS priority)
    device = "cuda" if torch.cuda.is_available() else (
        "mps" if torch.backends.mps.is_available() else "cpu"
    )
    print(f"Using device: {device}")

    from diffusers import DiffusionPipeline
    from huggingface_hub import login

    hf_token = os.getenv("HUGGINGFACE_TOKEN", "").strip()
    model_id = None

    # Select model automatically
    if device == "mps":
        model_id = "stabilityai/stable-diffusion-xl-base-1.0" # mac mps still running SDXL-base
        print("🎨 Using high-quality model (optimized for Mac MPS):", model_id)
    elif device == "cpu" or not hf_token:
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        print("Using lightweight model:", model_id)
    else:
        try:
            login(token=hf_token)
            model_id = "black-forest-labs/FLUX.1-dev"
            print("🎨 Using high-quality model:", model_id)
        except Exception as e:
            print("⚠️ Hugging Face login failed, falling back to SDXL:", e)
            model_id = "stabilityai/stable-diffusion-xl-base-1.0"

    # Load model (optimized for Mac)
    print("Loading diffusion pipeline…")
    # pipe = DiffusionPipeline.from_pretrained(
    #     model_id,
    #     # torch_dtype=torch.float16 if device != "cpu" else torch.float32,
    #     torch_dtype=torch.float32,

    #     use_auth_token=hf_token if "black-forest" in model_id else None
    # ).to(device)
    pipe = DiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float32,).to(device)
    
    # if device == "mps":
    #     pipe.enable_attention_slicing()
    #     torch.set_default_dtype(torch.float16)
    #     print("Optimized attention slicing for Apple Silicon (MPS).")
    if device == "mps": # Force all models to float32
        pipe.to(torch.float32)
        pipe.unet.to(torch.float32)
        pipe.text_encoder.to(torch.float32)
    if hasattr(pipe, "vae"):
        pipe.vae.to(torch.float32)
        pipe.enable_attention_slicing()
        print("Fixed: forced all modules to float32 for MPS (prevent Half overflow).")

    # Generate images for each panel
    for i, p in enumerate(image_prompts, start=1):
        panel_id = p.get("panel") or f"{i:02d}"
        prompt = p.get("prompt", "")
        print(f"Generating panel {panel_id} with model {model_id}…")

        try:
            image = pipe(
                prompt,
                num_inference_steps=20 if "stabilityai" in model_id else 25,
                guidance_scale=3.5
            ).images[0]
            out_path = f"outputs/panel_{panel_id}.png"
            image.save(out_path)
            print(f"Saved {out_path}")
        except Exception as e:
            print(f"Error rendering panel {panel_id}: {e}")
            # fallback → mock preview if render fails
            img = Image.new("RGB", (768, 512), "white")
            d = ImageDraw.Draw(img)
            d.text((20, 20), f"Panel {panel_id}", fill="black")
            d.text((20, 60), "Render failed", fill="red")
            img.save(f"outputs/panel_{panel_id}_error.png")

    print("All panels generated successfully.")