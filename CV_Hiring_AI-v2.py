
import streamlit as st
import google.generativeai as genai
import PyPDF2

# ================= ТОХИРГОО (CONFIGURATION) =================

# 1. GEMINI API KEY
# Энд түлхүүрээ бичнэ үү (эсвэл доор програмаас оруулж болно)
GEMINI_API_KEY = "AIzaSyCWuMT2-P2ddC7qBkBrZfZgaKwObij6GZw"

# ================= АЖЛЫН БАЙРНЫ ЖАГСААЛТ =================
JOB_POSITIONS = [
    "Давхар даатгалын менежер", "Жолооч", "Ахлах менежер", 
    "Зуучлал хамтын ажиллагааны менежер", "Үйл ажиллагаа хариуцсан ерөнхий менежер", 
    "Дизайнер", "Маркетингийн менежер", "Мэдээлэл технологийн менежер", 
    "ERP хөгжүүлэгч", "Нөхөн төлбөрийн хэлтсийн захирал", 
    "Нөхөн төлбөрийн мэргэжилтэн", "Нөхөн төлбөрийн ахлах менежер", 
    "Нөхөн төлбөрийн менежер", "Эрүүл мэндийн даатгалын нөхөн төлбөрийн менежер", 
    "Өмнөговь салбарын захирал", "Хөвсгөл салбарын захирал", 
    "Өмнөговь салбарын мэргэжилтэн", "Санхүү бүртгэлийн хэлтсийн захирал", 
    "Нягтлан бодогч", "Ахлах нягтлан бодогч", "Нярав", 
    "Архив, гэрээ бүртгэлийн мэргэжилтэн", "Шууд борлуулалтын албаны менежер", 
    "Шууд борлуулалтын захирал", "Даатгалын менежер", "Хуульч", "Ахлах Хуульч", 
    "Хянан нийцүүлэлтийн мэргэжилтэн", "Гүйцэтгэх захирлын туслах", 
    "Хүний нөөцийн менежер", "Андеррайтер", "Эрсдэлийн шинжээч", 
    "Эрсдэл хөрөнгийн үнэлгээний менежер", "Эрсдэлийн удирдлагын хэлтсийн захирал"
]

# ================= GEMINI ТОХИРГОО =================
try:
    if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    pass # Алдааг доор UI дээр харуулна

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
    except Exception as e:
        return None

def analyze_cv_with_gemini(cv_text, target_position, extra_requirements):
    """Gemini руу CV болон шаардлагуудыг илгээж анализ хийх"""
    
    # Таны сонгосон хамгийн тохиромжтой модель
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Хэрэглэгчийн оруулсан нэмэлт шаардлага байгаа эсэхийг шалгах
    extra_req_text = ""
    if extra_requirements:
        extra_req_text = f"\nОНЦГОЙ НЭМЭЛТ ШААРДЛАГУУД (Заавал хангасан байх ёстой):\n{extra_requirements}\n"
    
    prompt = f"""
    You are a Senior HR Recruiter for a Mongolian company.
    
    Target Job Position: "{target_position}"
    {extra_req_text}
    
    Candidate CV Content:
    {cv_text[:10000]} 
    
    Task:
    Analyze the CV against the Target Job Position AND the Special Requirements.
    
    Output Format (in Mongolian language):
    1. **Тохирох хувь (Match Score):** Give a score from 0 to 100. (If special requirements are NOT met, lower the score significantly).
    2. **Дүгнэлт (Summary):** A 2-sentence summary.
    3. **Нэмэлт шаардлага хангасан эсэх:** (Explain specifically if the candidate meets the "Special Requirements" listed above).
    4. **Давуу тал (Strengths):** List 3 key strengths.
    5. **Сул тал (Weaknesses):** List 2 potential weaknesses.
    6. **Шийдвэр (Recommendation):** 'Ярилцлагад дуудна' (Call) or 'Татгалзана' (Reject).
    
    Be strict regarding the special requirements.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Service Error: {str(e)}"

# ================= ҮНДСЭН UI (ХЭРЭГЛЭГЧИЙН ХЭСЭГ) =================

st.set_page_config(page_title="CV Hiring System", layout="wide")

st.title("📄 CV Шүүлтүүрийн Систем (Gemini 2.0)")
st.markdown("Таны компьютер дээрх PDF файлуудыг уншиж, ажлын байрны шаардлагад нийцэх эсэхийг шүүнэ.")

# --- Sidebar (Зүүн талын цэс) ---
with st.sidebar:
    st.header("Тохиргоо")
    
    # 1. Ажлын байр сонгох
    target_job = st.selectbox("🎯 Албан тушаал сонгох:", JOB_POSITIONS)
    
    st.divider()
    
    # 2. НЭМЭЛТ ШААРДЛАГА (ШИНЭ)
    st.markdown("**🛠 Тусгай шаардлага (Optional):**")
    extra_reqs = st.text_area(
        "Жишээ нь: Англи хэлний C1 түвшинтэй байх, Жолооны B ангилалтай байх...",
        height=150,
        placeholder="Энд бичсэн шаардлагуудыг AI онцгойлон шалгах болно."
    )
    
    st.divider()
    
    # 3. API Key оруулах (Код дотор байхгүй бол)
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        st.warning("⚠️ API Key тохируулаагүй байна.")
        user_key = st.text_input("Gemini API Key энд хуулна уу:", type="password")
        if user_key:
            genai.configure(api_key=user_key)
    else:
        st.success("✅ API Key холбогдсон")

# --- Үндсэн хэсэг ---

st.info(f"Одоогоор **'{target_job}'** албан тушаалд горилогчийг шалгаж байна.")
if extra_reqs:
    st.warning(f"⚠️ **Тусгай шаардлага идэвхжсэн:** \n {extra_reqs}")

# File Upload
uploaded_files = st.file_uploader(
    "CV файлуудаа энд чирч оруулна уу (Зөвхөн PDF)", 
    type=['pdf'], 
    accept_multiple_files=True
)

if st.button("🔍 CV-нүүдэд Анализ Хийх") and uploaded_files:
    
    st.write("---")
    progress_bar = st.progress(0)
    
    for i, file in enumerate(uploaded_files):
        with st.expander(f"📄 {file.name}", expanded=True):
            col1, col2 = st.columns([1, 3])
            
            # 1. Текст унших
            cv_text = extract_text_from_uploaded_file(file)
            
            with col1:
                if not cv_text or len(cv_text) < 50:
                    st.error("⚠️ PDF уншигдахгүй байна")
                    st.caption("Зурган файл эсвэл хоосон байна.")
                else:
                    st.success("Текст уншигдлаа")
                    st.caption(f"Тэмдэгт: {len(cv_text)}")
            
            # 2. AI Анализ хийх
            with col2:
                if cv_text and len(cv_text) >= 50:
                    with st.spinner("Gemini бодож байна..."):
                        # Шинэ функцийг нэмэлт шаардлагын хамт дуудна
                        result = analyze_cv_with_gemini(cv_text, target_job, extra_reqs)
                        st.markdown(result)
        
        # Progress bar шинэчлэх
        progress_bar.progress((i + 1) / len(uploaded_files))

    st.success("✅ Бүх файлуудыг шалгаж дууслаа!")

elif st.button("🔍 CV-нүүдэд Анализ Хийх") and not uploaded_files:
    st.warning("Эхлээд дор хаяж нэг PDF файл оруулна уу.")