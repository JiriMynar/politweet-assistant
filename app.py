import streamlit as st
import openai
import os
from PIL import Image
import io
import base64

# Kontrola API klíče
if not os.environ.get("OPENAI_API_KEY"):
    st.error("Chybí proměnná prostředí OPENAI_API_KEY. Zadejte svůj OpenAI API klíč.")
    st.stop()
openai.api_key = os.environ.get("OPENAI_API_KEY")

st.set_page_config(page_title="Univerzální Factchecker", page_icon="✅", layout="centered")
st.title("🕵️‍♂️ Univerzální Factchecker")
st.write(
    "Nahraj obrázek **nebo** zadej textové tvrzení k ověření. "
    "Výsledek dostaneš s detailním vysvětlením a zdroji. "
    "Hodnocení je na pětistupňové škále: **Pravda, Spíše pravda, Zavádějící, Spíše lež, Lež**."
)

ANALYZE_PROMPT = (
    "Analyzuj předložené tvrzení (nebo informaci na obrázku) a ověř jeho pravdivost na základě dostupných faktických informací. "
    "Hodnoť výsledek na této pětistupňové škále:\n"
    "1. Pravda\n"
    "2. Spíše pravda\n"
    "3. Zavádějící\n"
    "4. Spíše lež\n"
    "5. Lež\n\n"
    "Uveď jasný status a detailně vysvětli své hodnocení (na úrovni vysokoškoláka, včetně souvislostí, relevantních dat a argumentace). "
    "Připoj také konkrétní ověřitelné zdroje (odkazy na články, studie, oficiální statistiky apod.), které své tvrzení podporují. "
    "Piš česky, přehledně a v několika odstavcích.\n\n"
    "Struktura odpovědi:\n"
    "Status: [zvol jeden z 5 stupňů]\n"
    "Vysvětlení: [podrobné odůvodnění]\n"
    "Zdroje: [seznam konkrétních odkazů]\n"
)

def get_factcheck_result(image_file=None, text=None):
    try:
        if image_file and not text:
            img = Image.open(image_file)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64_image = base64.b64encode(buf.getvalue()).decode()
            user_prompt = ANALYZE_PROMPT
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64_image}"
                                },
                            },
                            {
                                "type": "text",
                                "text": user_prompt,
                            },
                        ],
                    }
                ],
            )
        elif text and not image_file:
            user_prompt = ANALYZE_PROMPT + f"\nTvrzení: {text}"
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
            )
        else:
            return None, "Vyplňte buď obrázek, nebo text, ne obojí zároveň."
        answer = response.choices[0].message.content
        return answer, None
    except Exception as e:
        return None, f"Došlo k chybě: {str(e)}"

def render_status(status_line):
    status_line = status_line.strip().lower()
    # Nejprve kontrolujeme "spíše pravda", pak až "pravda"
    if status_line.startswith("spíše pravda"):
        st.info("🟢 " + status_line.capitalize())
    elif status_line.startswith("pravda"):
        st.success("🟢 " + status_line.capitalize())
    elif status_line.startswith("zavádějící"):
        st.warning("🟠 " + status_line.capitalize())
    elif status_line.startswith("spíše lež"):
        st.error("🟠 " + status_line.capitalize())
    elif status_line.startswith("lež"):
        st.error("🔴 " + status_line.capitalize())
    else:
        st.write(status_line)

with st.form("analyze_form"):
    col1, col2 = st.columns(2)
    with col1:
        image_file = st.file_uploader("Obrázek k analýze", type=["png", "jpg", "jpeg"])
    with col2:
        text = st.text_area("Text k analýze", "", height=150)

    submitted = st.form_submit_button("Analyzovat")

if submitted:
    if (image_file and text.strip()) or (not image_file and not text.strip()):
        st.warning("Vyplňte **buď obrázek, nebo text**, ne obojí zároveň.")
    else:
        with st.spinner("Ověřuji, čekejte prosím..."):
            result, error = get_factcheck_result(image_file=image_file, text=text.strip())
        if error:
            st.error(error)
        else:
            # Robustnější parsování odpovědi
            lines = [l for l in result.split("\n") if l.strip()]
            status_line = next((l for l in lines if l.lower().startswith("status:")), None)
            vysvetleni_idx = next((i for i,l in enumerate(lines) if l.lower().startswith("vysvětlení:")), None)
            zdroje_idx = next((i for i,l in enumerate(lines) if l.lower().startswith("zdroje:")), None)
            if status_line:
                render_status(status_line.replace("Status:", "").strip())
            if vysvetleni_idx is not None and zdroje_idx is not None:
                st.markdown("### Vysvětlení")
                st.write("\n".join(lines[vysvetleni_idx+1:zdroje_idx]).strip())
                st.markdown("### Zdroje")
                st.write("\n".join(lines[zdroje_idx+1:]).strip())
            else:
                st.write(result)
