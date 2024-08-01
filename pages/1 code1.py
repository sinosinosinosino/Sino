import textwrap
import google.generativeai as genai
import streamlit as st
import toml
import pathlib

# secrets.toml 파일 경로
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기 (UTF-8 인코딩 지정)with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = toml.load(f)

# secrets.toml 파일에서 API 키 값 가져오기
api_key = secrets.get("api_key")

def to_markdown(text):
    """텍스트를 마크다운 형식으로 변환합니다."""
    text = text.replace('•', '*')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

def generate_counterargument(api_key, claim):
    """주어진 주장에 대한 반박을 생성합니다."""
    try:
        genai.configure(api_key=api_key)

        prompt = f"""
        다음 주장에 대한 반박을 생성해 주세요. 가능하면 여러 근거를 바탕으로 객관적인 정보를 제공하고,
        주장에 대한 완벽한 부정보다는 다른 시각을 제시하는 데 집중해 주세요.

        주장: {claim}
        """

        model = genai.GenerativeModel(
            model_name="gemini-1.0-pro",
            generation_config={
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ],
        )

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"API 호출 실패: {e}")
        return None

# 스트림릿 앱 인터페이스 구성
st.title("주장 반박 생성")

# 사용자 입력 받기
claim = st.text_area("반박할 주장을 입력하세요.")

if st.button("반박 생성"):
    if claim:
        counterargument = generate_counterargument(api_key, claim)

        if counterargument:
            st.markdown(to_markdown(counterargument))
        else:
            st.error("API 호출에 실패했습니다. 나중에 다시 시도해주세요.")
    else:
        st.warning("주장을 입력해주세요.")