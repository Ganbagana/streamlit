import streamlit as st
from openai import OpenAI
import PyPDF2
import requests

# ================= ТОХИРГОО (CONFIGURATION) =================
st.set_page_config(page_title="CV Hiring System", layout="wide")

# 1. OPENAI API KEY
# Эхлээд Streamlit Secrets-оос уншина
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)

# Client-г key олдсон үед үүсгэнэ
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ================= АЖЛЫН БАЙРНЫ ЖАГСААЛТ =================
JOB_POSITIONS = [
    "Давхар даатгалын менежер", "Жолооч", "Ахлах менежер",
    "Зуучлал хамтын ажиллагааны менежер", "Үйл ажиллагаа хариуцсан ерөнхий менежер",
    "Дизайнер", "Маркетингийн менежер", "Мэдээлэл технологийн менежер",
    "ERP хөгжүүлэгч", "Нөхөн төлбөрийн хэлтсийн захирал",
    "Нөхөн төлбөрийн мэргэжилтэн", "Нөхөн төлбөрийн ахлах менежер",
    "Нөхөн төлбөрийн менежер", "Эрүүл мэндийн даатгалын нөхөн төлбөрийн менежер",
    "Санхүү бүртгэлийн хэлтсийн захирал",
    "Нягтлан бодогч", "Ахлах нягтлан бодогч", "Нярав",
    "Архив, гэрээ бүртгэлийн мэргэжилтэн", "Шууд борлуулалтын албаны менежер",
    "Шууд борлуулалтын захирал", "Даатгалын менежер", "Хуульч", "Ахлах Хуульч",
    "Хянан нийцүүлэлтийн мэргэжилтэн", "Гүйцэтгэх захирлын туслах",
    "Хүний нөөцийн менежер", "Андеррайтер", "Эрсдэлийн шинжээч",
    "Эрсдэл хөрөнгийн үнэлгээний менежер", "Эрсдэлийн удирдлагын хэлтсийн захирал"
]

# ================= ФУНКЦУУД =================
def extract_text_from_uploaded_file(uploaded_file):
    """PDF файлаас текст унших"""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except Exception:
        return None


def analyze_cv_with_openai(cv_text, target_position, extra_requirements, client: OpenAI):
    """OpenAI руу CV болон шаардлагуудыг илгээж анализ хийх"""

    # Загвар модель (хүсвэл өөрчилж болно)
    model_name = "gpt-4.1-mini"

    extra_req_text = ""
    if extra_requirements:
        extra_req_text = (
            "\nОНЦГОЙ НЭМЭЛТ ШААРДЛАГУУД (Заавал хангасан байх ёстой):\n"
            f"{extra_requirements}\n"
        )

    prompt = f"""
You are a Senior HR Recruiter for a Mongolian company.

Target Job Position: "{target_position}"
{extra_req_text}

Candidate CV Content:
{cv_text[:10000]}

Task:
Analyze the CV against the Target Job Position AND the Special Requirements.

Output Format (in Mongolian language):
1. **Тохирох хувь (Match Score):** 0–100 хооронд оноо. (Нэмэлт тусгай шаардлагыг хангаагүй бол оноог бага тавь.)
2. **Дүгнэлт (Summary):** 2 өгүүлбэрийн дүгнэлт.
3. **Нэмэлт шаардлага хангасан эсэх:** Дээр бичсэн тусгай шаардлагуудыг хангаж байгаа эсэхийг тодорхой тайлбарла.
4. **Давуу тал (Strengths):** Гол 3 давуу талыг жагсаа.
5. **Сул тал (Weaknesses):** Болзошгүй 2 сул тал.
6. **Шийдвэр (Recommendation):** 'Ярилцлагад дуудна' эсвэл 'Татгалзана' гэж дүгнэ.

Боломжит хэмжээнд бодитой, хатуу шалгуураар дүгнэ.
    """.strip()

    try:
        response = client.responses.create(
            model=model_name,
            input=[
                {"role": "system", "content": "You are a strict, fair HR screening assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.output_text
    except Exception as e:
        return f"AI Service Error: {str(e)}"


# ✅ GitHub-оос файл татах (cache ашиглана)
@st.cache_data(ttl=3600)
def fetch_file_bytes(url: str) -> bytes:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content


# ================= ҮНДСЭН UI (ХЭРЭГЛЭГЧИЙН ХЭСЭГ) =================
st.title("📄 CV Шүүлтүүрийн Систем (OpenAI)")
st.markdown(
    "Таны компьютер дээрх PDF файлуудыг уншиж, ажлын байрны шаардлагад "
    "нийцэх эсэхийг шүүнэ."
)

# --- Sidebar (Зүүн талын цэс) ---
with st.sidebar:
    st.header("Тохиргоо")

    # ✅ Sample CV download buttons (from GitHub)
    st.subheader("📥 Жишээ CV")
    SAMPLE_URLS = {
        "Туршлагатай ажилтан": "https://raw.githubusercontent.com/Ganbagana/streamlit/main/sample_cvs/sample1-experience.pdf",
        "Туршлагагүй ажилтан": "https://raw.githubusercontent.com/Ganbagana/streamlit/main/sample_cvs/sample2-no-experience.pdf",
    }

    for fname, url in SAMPLE_URLS.items():
        try:
            data = fetch_file_bytes(url)
            st.download_button(
                label=f"Download: {fname}",
                data=data,
                file_name=fname,
                mime="application/pdf",
                key=f"gh_dl_{fname}",  # unique key
            )
        except Exception as e:
            st.caption(f"⚠️ Cannot fetch {fname}: {e}")

    st.divider()

    # 1. Ажлын байр сонгох
    target_job = st.selectbox("🎯 Албан тушаал сонгох:", JOB_POSITIONS)

    st.divider()

    # 2. НЭМЭЛТ ШААРДЛАГА
    st.markdown("**🛠 Тусгай шаардлага (Optional):**")
    extra_reqs = st.text_area(
        "Жишээ нь: Англи хэлний C1 түвшинтэй байх, Жолооны B ангилалтай байх...",
        height=150,
        placeholder="Энд бичсэн шаардлагуудыг AI онцгойлон шалгах болно.",
    )

    st.divider()

    # 3. API Key оруулах (хийх боломжтой нэмэлт)
    if not OPENAI_API_KEY:
        st.warning("⚠️ Streamlit Secrets дээр OPENAI_API_KEY тохируулаагүй байна.")
        user_key = st.text_input("OpenAI API Key энд хуулна уу:", type="password")
        if user_key:
            OPENAI_API_KEY = user_key
            client = OpenAI(api_key=OPENAI_API_KEY)
            st.success("✅ API Key амжилттай холбогдлоо.")
    else:
        st.success("✅ API Key (Secrets) амжилттай уншигдлаа.")
        # ✅ Links (below main info)
        st.markdown(
            """
        - **Нэг CV дундаж хиймэл ашигласан өртөг 35₮:** https://platform.openai.com/docs/pricing
        - **Эх код:** https://github.com/Ganbagana/streamlit/blob/main/streamlit_app.py
        """
        )

# API key огт байхгүй бол анализ хийх боломжгүй
if not OPENAI_API_KEY or client is None:
    st.error("❌ OpenAI API Key байхгүй байна. Secrets эсвэл Sidebar-оор оруулна уу.")
    st.stop()

# --- Үндсэн хэсэг ---
st.info(f"Одоогоор **'{target_job}'** албан тушаалд горилогчийг шалгаж байна.")
if extra_reqs:
    st.warning(f"⚠️ **Тусгай шаардлага идэвхжсэн:** \n\n{extra_reqs}")

# File Upload
uploaded_files = st.file_uploader(
    "CV файлуудаа энд чирч оруулна уу (Зөвхөн PDF)",
    type=["pdf"],
    accept_multiple_files=True,
)

# Нэг л товч үүсгэнэ (давхардсан ID-гаас сэргийлнэ)
analyze_clicked = st.button("🔍 CV-нүүдэд Анализ Хийх", key="analyze_cvs")

if analyze_clicked:
    if not uploaded_files:
        st.warning("Эхлээд дор хаяж нэг PDF файл оруулна уу.")
    else:
        st.write("---")
        progress_bar = st.progress(0)

        for i, file in enumerate(uploaded_files):
            with st.expander(f"📄 {file.name}", expanded=True):
                col1, col2 = st.columns([1, 3])

                # 1. Текст унших
                cv_text = extract_text_from_uploaded_file(file)

                with col1:
                    if not cv_text or len(cv_text) < 50:
                        st.error("⚠️ PDF уншигдахгүй байна.")
                        st.caption("Зурган файл эсвэл хоосон PDF байх магадлалтай.")
                    else:
                        st.success("Текст амжилттай уншигдлаа.")
                        st.caption(f"Тэмдэгтийн тоо: {len(cv_text)}")

                # 2. AI Анализ хийх
                with col2:
                    if cv_text and len(cv_text) >= 50:
                        with st.spinner("OpenAI бодож байна..."):
                            result = analyze_cv_with_openai(
                                cv_text=cv_text,
                                target_position=target_job,
                                extra_requirements=extra_reqs,
                                client=client,
                            )
                            st.markdown(result)

            # Progress bar шинэчлэх
            progress_bar.progress((i + 1) / len(uploaded_files))

        st.success("✅ Бүх файлуудыг шалгаж дууслаа!")








