import pandas as pd
from rapidfuzz import process, fuzz

def load_all(pks_path, binh_path, style_path):
    df_pks = pd.read_csv(pks_path)
    df_binh = pd.read_csv(binh_path)
    df_style = pd.read_csv(style_path)
    for df in [df_pks, df_binh, df_style]:
        df.columns = [c.strip() for c in df.columns]
    return df_pks, df_binh, df_style

def find_id_from_quote(quote, df_pks):
    """
    Find the ID corresponding to the input sentence (can be in column C, V or M).
    Choose the best match in the 3 columns, safely handling the RapidFuzz index.
    """
    cols = [c for c in ["M", "V", "C"] if c in df_pks.columns]
    if not cols:
        raise ValueError("Dataset is missing all 3 columns C/V/M.")

    best_score = -1
    best_idx = None
    best_col = None

    for col in cols:
        corpus = df_pks[col].fillna("").astype(str).tolist()
        try:
            result = process.extractOne(quote, corpus, scorer=fuzz.token_set_ratio)
            if result is None:
                continue
            text_match, score, idx = result  # Unpack safely
        except Exception:
            continue

        if score > best_score:
            best_score = score
            best_idx = idx
            best_col = col

    if best_idx is None:
        raise ValueError("No match found in columns C/V/M.")

    best_idx = int(best_idx)
    row = df_pks.iloc[best_idx]

    id_value = str(row.get("sent_id", "")) or str(row.get("sect_id", "")) or str(row.get("file_id", ""))
    print(f"🔍 Best match in column '{best_col}' (score={best_score:.1f}) → ID={id_value}")

    return id_value, row.to_dict()

def get_binhgiai_from_id(id_value, df_binh):
    """
    Retrieve Commentaries by ID (sect_id) in TuThu_BinhGiai_PKS_007.csv.
    File structure: ['file_id', 'sect_id', 'E']
    """
    # Ưu tiên cột sect_id để match với id_value
    id_col = "sect_id" if "sect_id" in df_binh.columns else "ID"
    text_col = "E" if "E" in df_binh.columns else None

    if text_col is None:
        raise ValueError("Cannot found E (Bình Giải) in TuThu_BinhGiai_PKS_007.csv")

    matches = df_binh[df_binh[id_col].astype(str) == str(id_value)]

    if matches.empty:
        print(f"⚠️ No E (Bình Giải) found for {id_value}, try fuzzy match by sect_id...")
        # Fallback fuzzy
        from rapidfuzz import process, fuzz
        corpus = df_binh[id_col].astype(str).tolist()
        text, score, idx = process.extractOne(str(id_value), corpus, scorer=fuzz.partial_ratio)
        row = df_binh.iloc[int(idx)]
        print(f"Fuzzy match sect_id={row[id_col]} (score={score:.1f})")
    else:
        row = matches.iloc[0]

    # Return a dict with default empty fields
    return {
        "id": row.get(id_col),
        "binh_giai": row.get(text_col, ""),
        "y_nghia": "",
        "boi_canh": "",
        "nhan_vat": "",
        "prompt_mau": ""
    }

def build_context(id_value, df_style, df_binh_row, df_pks_row):
    matched_style = df_style[df_style["STT"].astype(str).str.contains(id_value, na=False)]
    if matched_style.empty:
        matched_style = df_style.head(1)
    style = matched_style.iloc[0].to_dict()
    return {
        "id": id_value,
        "quote": df_pks_row.get("Nguyên văn", ""),
        "binh_giai": df_binh_row.get("Bình giải", ""),
        "y_nghia": df_binh_row.get("Tư tưởng chính", ""),
        "boi_canh": style.get("Bối cảnh", ""),
        "nhan_vat": style.get("Nhân vật", ""),
        "prompt_mau": style.get("Prompt truyện tranh", "")
    }
