import streamlit as st

from openai import OpenAI
import edge_tts



# Initialize the OpenAI client with proper configuration

st.set_page_config(
    page_title="EsMa Pro",
    page_icon=":writing_hand:",
    layout="wide"
)
# Debug: Show loaded secrets (remove after testing)
if not st.user.is_logged_in:
    if st.button("Sign In"):
        st.login("auth0")
    st.stop()  # Stop execution if not logged in

# Now safely access user info
logged_in_name = st.user.name
try:
    # Access nested secrets
    api_key = st.secrets.openrouter.OPENAI_API_KEY
    base_url = st.secrets.openrouter.OPENAI_BASE_URL

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    # Test connection
    client.models.list()

except AttributeError as e:
    st.error(f"""
    Secret configuration error: {str(e)}
    Current secret structure: {dict(st.secrets)}
    Required structure:
    ```
    [openrouter]
    OPENAI_API_KEY = "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"
    OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
    ```
    """)
    st.stop()
except Exception as d:
    st.error(f"API connection failed: {str(d)}")
    st.stop()

# Rest of your app...



list_essay_type = [
    "Argumentative", "Persuasive", 'Explanatory', 'Descriptive',
    "Narrative", 'Cause and Effect', "Process Analysis",
    "Compare/Contrast","Critique", "Definition", "General"
]


list_level = ["Elementary", "Junior High", "Senior High", "Undergraduate", "Graduate", "Postgraduate", "PhD", "Masters", "Doctorate"]
list_speech_type = ["Casual", "Intimate", "Formal", "Frozen", "Consultative"]
left, right = st.columns(2, vertical_alignment="top")


def ai_assistant(prompt):
    try:
        response = client.chat.completions.create(
            model="nousresearch/deephermes-3-mistral-24b-preview:free",
            messages=[
                {
                    "role": "system",
                    "content": """You are EsMa (Essay Maker). Strictly only write the requested essay content. 
                    Do not write any other information. Meaning, only write paragraphs. Also the output must have be clear and specific with no vague output"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=20000  # Added to prevent timeouts
        )
        return response.choices[0].message.content
    except Exception as det:
        st.error(f"Failed to generate essay: {str(det)}")
        return None


# Main app interface
def main():
    with st.container():
        left.subheader("EsMa by Elley")
        left.title(f"Hi {logged_in_name} Your Free Essay Maker Tool")
        right.subheader("")
        right.title("")
    with st.container():
        level_essay = left.selectbox("Type-Level", list_level)
        speech_type = left.selectbox("Type of Speech", list_speech_type)
        essay_type = left.selectbox("Essay Type", list_essay_type)
        word_num = left.slider("Select Number Words", min_value=0, max_value=1500, step=100)
        selected_pov = left.segmented_control('Point of View', ['First', 'Second', 'Third'], selection_mode = "single")

    with st.container():
        content_prompt = left.text_area("Prompt", "", height=150)
        other_info_prompt = left.text_area("Other Instructions", "", height=70)

        if st.button("Generate Essay"):
            if content_prompt.strip() in ("", "Generated prompt"):
                st.warning("Please enter a valid prompt")
            else:
                with st.spinner("Generating your essay..."):
                    full_prompt = f"Write a comprehensive {essay_type}, point of view: {selected_pov} point of view, education level: {level_essay},  type of speech: {speech_type}, number of minimum words: {word_num}, essay about: {content_prompt}. With extra task {other_info_prompt}"
                    essay = ai_assistant(full_prompt)
                    if essay:
                        right.text_area("Generated Essay", value=essay, height=680)

        else:
            right.text_area("Generated Essay", "", height=680)


if __name__ == "__main__":
    main()
