import os, json
import google.generativeai as genai
from dotenv import load_dotenv
from .data_utils import load_all, find_id_from_quote, get_binhgiai_from_id, build_context
from .gemini_rules_full import get_system_prompt, build_user_prompt
from .generate_flux_images import generate_flux_images
from .render_story_page import render_story_page
from src.log_prompt_history import append_story_log

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_TEXT = os.getenv("MODEL_TEXT", "models/gemini-2.5-pro")

DATA_PKS = "data/TuThu_PKS_007.csv"
DATA_BINH = "data/TuThu_BinhGiai_PKS_007.csv"
DATA_STYLE = "data/TuThu_Data_Example.csv"

def call_gemini(context):
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(MODEL_TEXT, system_instruction=get_system_prompt())
    resp = model.generate_content(
        build_user_prompt(context),
        generation_config={"response_mime_type": "application/json"}
    )
    data = json.loads(resp.candidates[0].content.parts[0].text)
    return data

def run_pipeline(quote):
    df_pks, df_binh, df_style = load_all(DATA_PKS, DATA_BINH, DATA_STYLE)
    id_value, row_pks = find_id_from_quote(quote, df_pks)
    row_binh = get_binhgiai_from_id(id_value, df_binh)
    context = build_context(id_value, df_style, row_binh, row_pks)
    print(f"📘 Building story for ID {id_value} – {context['quote'][:40]}...")
    story = call_gemini(context)
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/storyboard.json", "w", encoding="utf-8") as f:
        json.dump(story, f, ensure_ascii=False, indent=2)
    print("Saved outputs/storyboard.json")
    # Log information
    story_id = id_value
    story_title = story.get("story_title", "Untitled Story")
    # append_story_log(context["quote"], story_id, story_title)
    append_story_log(
        quote=context["quote"],
        story_id=id_value,
        story_title=story.get("story_title", "Untitled Story"),
        storyboard_path="outputs/storyboard.json"
        )

    if "image_prompts" in story:
        generate_flux_images(story["image_prompts"])
        render_story_page("outputs/storyboard.json", "outputs", output_pdf=True)  

if __name__ == "__main__":
    run_pipeline("康誥曰：克明德。")