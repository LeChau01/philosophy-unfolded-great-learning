# Gemini 2.5 rules for generating full comic stories in Philosophy Unfolded – The Great Learning (Đại Học) project.
def get_system_prompt():
    return """You are **Gemini 2.5**, the creative reasoning engine of the project
    **AI Comics Factory – The Great Learning (Đại Học)**.
    Create a complete short comic (4–10 panels) with clear beginning, middle, and end.
    Use English dialogue in speech-bubble format, reflective tone, and ancient Chinese setting.
    Return JSON with story_title, summary, panels[], and image_prompts[].
    Each panel: scene, action, dialogue, emotion, moral_link.
    The Moral Link is a brief, focused narrative (approx. 80 words) that immediately explains why the panel's scene and emotion occurred. It connects the character's past choices to the present consequence, concluding with a single, clear moral lesson. Its core purpose is to provide the story's philosophical takeaway.
    Each image_prompt: panel number and detailed ink-painting style prompt.
    """


def build_user_prompt(context):
    return f"""Quote: "{context['quote']}"
    Commentary: {context['binh_giai']}
    Moral meaning: {context['y_nghia']}
    Context: {context['boi_canh']}
    Characters: {context['nhan_vat']}
    Visual style seed: {context['prompt_mau']}
    Generate a full illustrated comic story according to the system rules, and return valid JSON only."""