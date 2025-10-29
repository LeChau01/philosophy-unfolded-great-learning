import streamlit as st
import os
import json
import io
import zipfile
from src.main_pipeline import run_pipeline
from src.render_story_page import render_story_page

st.set_page_config(page_title="The Great Learning (大学 / Đại Học)", layout="wide")

# HEADER
st.title("The Great Learning (大学 / Đại Học)")
st.markdown("""
*Exploring Confucian wisdom through AI-generated visual narratives*  
**Workflow:** Quote → Storyboard → Illustrated Panels → A4 Output
""")

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Output Settings")

    st.subheader("📦 Export Options")
    export_pdf = st.checkbox("📄 Generate PDF", value=True,
                             help="Combine all pages into single PDF file")

    st.divider()

    st.subheader("🎨 Generation Mode")
    fast_mode = st.toggle("⚡ Fast Mode (Mock Panels)",
                          help="Preview quickly without heavy diffusion rendering")

    st.divider()

# --- CSS + caption tách riêng ---
st.markdown(
    """
    <style>
    /* Ghim phần chú thích ở góc dưới sidebar */
    [data-testid="stSidebar"]::after {
        content: "From the Confucian classic The Great Learning (大學) — a guide to moral and social harmony — emerges a new vision: timeless philosophy reinterpreted through generative AI imagery.";
        position: absolute;
        bottom: 1.2rem;
        left: 1rem;
        right: 1rem;
        font-size: 0.8rem;
        color: #6c757d;
        line-height: 1.3;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# MAIN INPUT
quote = st.text_area(
    "Enter a quote from *The Great Learning (大学 / Đại Học)*:",
    "Thiên Khang Cáo nói rằng: 'Hay làm sáng tỏ đức.'",
    height=120,
    help="Provide a quote from *The Great Learning* to unfold as an illustrated philosophical story."
)

# CONTROL BUTTONS
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    generate = st.button("Unfold the Story", type="primary", use_container_width=True)

with col2:
    if st.button("Re-render Layout", help="Re-render A4 pages from existing panels"):
        with st.spinner("Re-rendering pages..."):
            output_dir = "outputs"
            result = render_story_page(
                json_path=os.path.join(output_dir, "storyboard.json"),
                panels_dir=output_dir,
                output_pdf=export_pdf
            )
            if result:
                st.success(f"Re-rendered {result.get('total_pages', 0)} pages!")
            else:
                st.info("Re-render finished (no summary returned).")
            st.rerun()

with col3:
    if st.button("Clear Outputs", help="Delete all generated files"):
        output_dir = "outputs"
        import glob
        files = glob.glob(os.path.join(output_dir, "*.png")) + \
                glob.glob(os.path.join(output_dir, "*.pdf")) + \
                glob.glob(os.path.join(output_dir, "*.json"))
        for f in files:
            try:
                os.remove(f)
            except:
                pass
        st.success("Outputs cleared!")
        st.rerun()

# RUN PIPELINE
if generate:
    if not quote.strip():
        st.error("⚠️ Please enter a quote first!")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("🧠 Generating story from quote...")
        progress_bar.progress(10)

        os.environ["FAST_MODE"] = "true" if fast_mode else "false"

        try:
            status_text.text("🎨 Generating image panels... This may take several minutes.")
            progress_bar.progress(40)

            run_pipeline(quote)

            progress_bar.progress(75)
            status_text.text("🖨️ Rendering A4 layout and exporting results...")

            output_dir = "outputs"
            result = render_story_page(
                json_path=os.path.join(output_dir, "storyboard.json"),
                panels_dir=output_dir,
                output_pdf=export_pdf
            )

            progress_bar.progress(100)
            status_text.empty()

            if result:
                st.success(f"✅ Story generation complete! ({result.get('total_pages', 0)} pages, {result.get('total_panels', 0)} panels)")
            else:
                st.success("✅ Story generation complete!")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# DISPLAY OUTPUTS
output_dir = "outputs"
has_outputs = False

if os.path.exists(output_dir):
    files = os.listdir(output_dir)
    has_a4_pages = any(f.startswith("comic_page_A4_") and f.endswith(".png") for f in files)
    has_panels = any(f.startswith("panel_") and f.endswith(".png") for f in files)
    has_storyboard = "storyboard.json" in files
    has_outputs = has_a4_pages or (has_panels and has_storyboard)

if has_outputs:
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["📖 A4 Pages", "🖼️ Individual Panels", "📋 Storyboard", "📥 Downloads"])

    # TAB 1: A4 Pages
    with tab1:
        st.markdown("## 📖 A4 Layout Preview (Printable)")
        a4_images = sorted([f for f in os.listdir(output_dir) if f.startswith("comic_page_A4_") and f.endswith(".png")])

        if a4_images:
            for img_file in a4_images:
                st.image(os.path.join(output_dir, img_file), use_container_width=True)
        else:
            st.info("💡 No A4 pages found. Click 'Re-render Layout' to generate them.")

    # TAB 2: INDIVIDUAL PANELS (Save + ZIP)
    with tab2:
        st.markdown("## 🖼️ Individual Panels")
        st.caption("Raw panels before layout composition")

        panel_images = sorted([
            f for f in os.listdir(output_dir)
            if f.startswith("panel_") and f.endswith(".png")
        ])

        if panel_images:
            cols = st.columns(3)
            for idx, img_file in enumerate(panel_images):
                img_path = os.path.join(output_dir, img_file)
                with cols[idx % 3]:
                    st.image(img_path, caption=f"Panel {idx + 1}", use_container_width=True)

                    # 💾 Nút tải riêng từng ảnh
                    with open(img_path, "rb") as f:
                        st.download_button(
                            label="💾 Save PNG",
                            data=f.read(),
                            file_name=img_file,
                            mime="image/png",
                            use_container_width=True,
                            key=f"download_panel_{idx}"
                        )

            st.markdown("---")
            st.markdown("### 📦 Download All Panels (ZIP)")

            # 📦 Nút tải toàn bộ panels
            if st.button("📦 Prepare ZIP of all panels", use_container_width=True):
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for img_file in panel_images:
                        img_path = os.path.join(output_dir, img_file)
                        zip_file.write(img_path, img_file)

                st.download_button(
                    "⬇️ Download All Panels (ZIP)",
                    zip_buffer.getvalue(),
                    file_name="panels_raw.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key="download_all_panels_zip"
                )

        else:
            st.warning("⚠️ No panel images found.")

    # TAB 3: STORYBOARD
    with tab3:
        st.markdown("## 📋 Storyboard Data")

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Full Storyboard")
            json_path = os.path.join(output_dir, "storyboard.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    st.json(json.load(f))
            else:
                st.info("No storyboard.json found")

        with col_b:
            st.subheader("Captions Only")
            captions_path = os.path.join(output_dir, "storyboard_captions.json")
            if os.path.exists(captions_path):
                with open(captions_path, "r", encoding="utf-8") as f:
                    captions_data = json.load(f)
                    st.json(captions_data)

                st.markdown("### 📝 Caption List")
                for item in captions_data.get("captions", []):
                    st.markdown(f"**Panel {item['panel']}**: {item['moral_link']}")
            else:
                st.info("No storyboard_captions.json found.")

    # TAB 4: DOWNLOADS
    with tab4:
        st.markdown("## 📥 Download Files")
        download_col1, download_col2 = st.columns(2)

        # PDF Download
        with download_col1:
            pdf_path = os.path.join(output_dir, "comic_story_full.pdf")
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📄 Download PDF",
                        f,
                        file_name="comic_story_full.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.caption(f"📊 Size: {os.path.getsize(pdf_path)/1024/1024:.2f} MB")
            else:
                st.info("PDF not available.")

        # Full Storyboard JSON
        with download_col2:
            json_path = os.path.join(output_dir, "storyboard.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        "📊 Download Full Storyboard",
                        f,
                        file_name="storyboard_full.json",
                        mime="application/json",
                        use_container_width=True
                    )

else:
    # EMPTY STATE
    st.markdown("---")
    st.markdown("""
    ### 👋 Welcome to AI Comics Factory!
    
    Transform philosophical quotes from **The Great Learning (Đại Học)** 
    into visual philosophical comics.

    #### 🚀 Quick Start:
    1. Enter a quote above  
    2. Adjust settings in the sidebar (optional)  
    3. Click **“Unfold the Story”**  
    4. Wait for AI generation  
    5. View your results in tabs below
    """)

# FOOTER
st.divider()
st.caption("Philosophy Unfolded – The Great Learning (大学 / Đại Học) | Powered by Stable Diffusion")
