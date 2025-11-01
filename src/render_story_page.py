# Description: Render story pages in premium A4 layout with 2 panels per page.
import os, json, math, textwrap, logging, traceback
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ===============================
# LOGGING CONFIGURATION
# ===============================
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"render_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
logging.getLogger().addHandler(console)


def render_story_page(
    json_path="outputs/storyboard.json",
    panels_dir="outputs",
    output_pdf=True
):
    """
    Philosophy-Unfolded – Premium A4 Layout v3.3
    --------------------------------------------
    • 2 panels per A4 page – optimized for clear, large storytelling
    • Auto font detection for Chinese/Vietnamese (Noto Sans/Serif SC)
    • Balanced text sizes (~12–14pt printed)
    • Returns metadata for Streamlit integration
    """

    try:
        logging.info(f"=== Render Story Started ===")
        logging.info(f"JSON Path: {json_path}")
        logging.info(f"Panels Dir: {panels_dir}")

        # LOAD STORY JSON
        if not os.path.exists(json_path):
            logging.error("❌ storyboard.json not found.")
            return None

        with open(json_path, "r", encoding="utf-8") as f:
            story = json.load(f)

        story_title = story.get("story_title", "Untitled Story")
        panels = story.get("panels", [])
        logging.info(f"Loaded story '{story_title}' with {len(panels)} panels metadata")

        # LOAD PANEL IMAGES
        image_files = sorted([
            f for f in os.listdir(panels_dir)
            if f.startswith("panel_") and f.endswith(".png")
        ])
        if not image_files:
            logging.warning("⚠️ No panel images found to render.")
            return None

        # CONFIG
        A4_W, A4_H = 2480, 3508  # A4 at 300 DPI
        MARGIN_X, MARGIN_Y = 160, 200
        PANELS_PER_PAGE = 2
        BG_COLOR = (255, 255, 255)

        # FONT DETECTION – PRIORITIZE CJK FONTS
        font_candidates = [
            "assets/fonts/NotoSansSC-Regular.otf",
            "assets/fonts/NotoSerifSC-Regular.otf",
            os.path.expanduser("~/Library/Fonts/NotoSansSC[wght].ttf"),
            os.path.expanduser("~/Library/Fonts/NotoSerifSC-Regular.otf"),
            "/Library/Fonts/NotoSansSC[wght].ttf",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "assets/fonts/NotoSans-Regular.ttf"
        ]
        font_path = next((f for f in font_candidates if os.path.exists(f)), None)

        if font_path:
            logging.info(f"Using font: {font_path}")
            title_font   = ImageFont.truetype(font_path, 100)
            body_font    = ImageFont.truetype(font_path, 35)
            caption_font = ImageFont.truetype(font_path, 45)
        else:
            logging.warning("⚠️ No CJK font found — fallback to default.")
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            caption_font = ImageFont.load_default()

        # PAGE RENDERING LOOP
        total_panels = len(image_files)
        total_pages = math.ceil(total_panels / PANELS_PER_PAGE)
        pdf_pages = []

        logging.info(f"Rendering {total_panels} panels → {total_pages} A4 pages")

        for page_num in range(total_pages):
            try:
                start_idx = page_num * PANELS_PER_PAGE
                end_idx = min(start_idx + PANELS_PER_PAGE, total_panels)
                batch_files = image_files[start_idx:end_idx]

                page = Image.new("RGB", (A4_W, A4_H), color=BG_COLOR)
                draw = ImageDraw.Draw(page)

                # HEADER
                title_y = 80
                title_w = draw.textlength(story_title, font=title_font)
                draw.text(((A4_W - title_w) / 2, title_y), story_title, fill=(0, 0, 0), font=title_font)

                # GRID CONFIG
                grid_top = 400
                grid_bottom = A4_H - 200
                available_h = grid_bottom - grid_top
                cell_h = int((available_h - MARGIN_Y) / 2)
                cell_w = A4_W - 2 * MARGIN_X

                # RENDER EACH PANEL
                for i, fname in enumerate(batch_files):
                    try:
                        img_path = os.path.join(panels_dir, fname)
                        if not os.path.exists(img_path):
                            logging.warning(f"Panel image not found: {fname}")
                            continue

                        panel_img = Image.open(img_path)
                        img_ratio = panel_img.width / panel_img.height

                        # Resize image
                        new_w = cell_w
                        new_h = int(cell_w / img_ratio)
                        if new_h > int(cell_h * 0.7):
                            new_h = int(cell_h * 0.7)
                            new_w = int(new_h * img_ratio)
                        panel_img = panel_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                        x = MARGIN_X + (cell_w - new_w)//2
                        y = grid_top + i * (cell_h + MARGIN_Y//2)
                        page.paste(panel_img, (x, y))

                        # CAPTION
                        caption_y = y + new_h + 50
                        global_idx = start_idx + i
                        caption_text = panels[global_idx].get("moral_link", "").strip() if global_idx < len(panels) else ""

                        if caption_text:
                            wrapped_lines = textwrap.wrap(caption_text, width=80)
                            line_height = int(caption_font.size * 1.5)
                            for j, line in enumerate(wrapped_lines[:8]):
                                lw = draw.textlength(line, font=caption_font)
                                draw.text(
                                    (MARGIN_X + (cell_w - lw) / 2, caption_y + j * line_height),
                                    line,
                                    fill=(0, 0, 0),
                                    font=caption_font
                                )
                    except Exception as e:
                        logging.error(f"Error rendering panel {fname}: {e}")
                        logging.debug(traceback.format_exc())

                # FOOTER
                footer_text = "Philosophy Unfolded – The Great Learning (大学 / Đại Học)"
                fw = draw.textlength(footer_text, font=body_font)
                draw.text(((A4_W - fw) / 2, A4_H - 130), footer_text, fill=(100, 100, 100), font=body_font)

                pdf_pages.append(page)
                logging.info(f"✅ Rendered page {page_num + 1}/{total_pages}")

            except Exception as e:
                logging.error(f"Error rendering page {page_num + 1}: {e}")
                logging.debug(traceback.format_exc())

        # PDF MERGE
        out_pdf = None
        if output_pdf and pdf_pages:
            try:
                out_pdf = os.path.join(panels_dir, "comic_story_full.pdf")
                pdf_pages[0].save(out_pdf, save_all=True, append_images=pdf_pages[1:], resolution=300.0)
                logging.info(f"🎉 Exported Premium PDF: {out_pdf}")
                logging.info(f"🖼️ {total_pages} pages | {total_panels} panels total")
                logging.info(f"🈶 Font used: {font_path}")
            except Exception as e:
                logging.error(f"PDF export failed: {e}")
                logging.debug(traceback.format_exc())

        logging.info("=== Render Story Completed ===\n")

        # RETURN METADATA
        return {
            "total_pages": total_pages,
            "total_panels": total_panels,
            "output_dir": panels_dir,
            "pdf_path": out_pdf,
            "font": font_path
        }

    except Exception as e:
        logging.critical(f"Fatal error in render_story_page: {e}")
        logging.debug(traceback.format_exc())
        return None


# ===============================
# MAIN EXECUTION
# ===============================
if __name__ == "__main__":
    result = render_story_page()
    if result:
        logging.info(f"Result: {result}")
    else:
        logging.error("Rendering failed.")
