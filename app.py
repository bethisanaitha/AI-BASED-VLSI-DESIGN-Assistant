import os
import hashlib
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI-Based VLSI Design Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI-Based VLSI Design Assistant")

st.write(
    "Upload a VLSI PDF, get a quick and clear explanation, "
    "and ask questions about the document."
)


# =========================================================
# FOLDER
# =========================================================

os.makedirs("uploaded_files", exist_ok=True)


# =========================================================
# OLLAMA
# =========================================================

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
    num_predict=500
)


# =========================================================
# SESSION STATE
# =========================================================

if "file_hash" not in st.session_state:
    st.session_state.file_hash = None

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "explanation" not in st.session_state:
    st.session_state.explanation = ""

if "answer" not in st.session_state:
    st.session_state.answer = ""


# =========================================================
# UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📄 Upload VLSI PDF",
    type=["pdf"]
)


if uploaded_file is not None:

    file_data = uploaded_file.getvalue()

    current_hash = hashlib.md5(
        file_data
    ).hexdigest()


    # =====================================================
    # PROCESS ONLY NEW PDF
    # =====================================================

    if current_hash != st.session_state.file_hash:

        pdf_path = os.path.join(
            "uploaded_files",
            uploaded_file.name
        )

        with open(pdf_path, "wb") as file:
            file.write(file_data)


        # =================================================
        # READ PDF
        # =================================================

        with st.spinner("📖 Reading VLSI PDF..."):

            loader = PyPDFLoader(pdf_path)

            documents = loader.load()


        # =================================================
        # GET REPRESENTATIVE TEXT
        # =================================================

        total_pages = len(documents)

        selected_text = ""

        # First pages
        for doc in documents[:3]:

            selected_text += doc.page_content
            selected_text += "\n\n"


        # Middle pages
        if total_pages > 6:

            middle_start = total_pages // 2

            for doc in documents[
                middle_start:middle_start + 2
            ]:

                selected_text += doc.page_content
                selected_text += "\n\n"


        # Last pages
        if total_pages > 3:

            for doc in documents[-2:]:

                selected_text += doc.page_content
                selected_text += "\n\n"


        # Keep prompt small
        selected_text = selected_text[:12000]

        st.session_state.pdf_text = selected_text


        # =================================================
        # FAST EXPLANATION
        # =================================================

        explanation_prompt = f"""
You are an expert VLSI Design Assistant.

Analyze this VLSI PDF content and explain it clearly
for a student.

PDF CONTENT:

{selected_text}

Give a clear explanation using:

1. What this PDF is about
2. Main VLSI topics
3. Important concepts
4. How the important concepts work
5. Important formulas or technical points
6. Applications
7. Short summary

Rules:

- Use simple English.
- Explain technical terms.
- Give small examples when useful.
- Focus only on VLSI topics.
- Do not invent information.
- Keep the answer concise but useful.
- Maximum 350 words.
"""


        with st.spinner("🤖 Generating VLSI explanation..."):

            response = llm.invoke(
                explanation_prompt
            )

        st.session_state.explanation = response.content


        # =================================================
        # SAVE HASH
        # =================================================

        st.session_state.file_hash = current_hash


    # =====================================================
    # EXPLANATION
    # =====================================================

    st.subheader("📖 VLSI PDF Explanation")

    st.markdown(
        st.session_state.explanation
    )


    # =====================================================
    # SUGGESTIONS
    # =====================================================

    st.subheader("💡 VLSI Design Suggestions")

    st.write(
        "Get useful study and design suggestions "
        "based on this PDF."
    )

    if st.button("Generate Suggestions"):

        suggestion_prompt = f"""
You are a VLSI Design Engineer.

Based on this VLSI PDF content:

{st.session_state.pdf_text}

Give 5 useful suggestions.

Include:
- Topics to study
- Concepts to practice
- VLSI design exercises
- Interview questions
- Project ideas

Keep the suggestions short.
"""


        with st.spinner("💡 Generating suggestions..."):

            suggestion = llm.invoke(
                suggestion_prompt
            )

        st.markdown(
            suggestion.content
        )


    # =====================================================
    # ASK QUESTIONS
    # =====================================================

    st.subheader("💬 Ask Questions About the VLSI PDF")

    question = st.text_input(
        "🔎 Enter your VLSI question"
    )


    if st.button("Ask Question"):

        if question.strip() == "":

            st.warning(
                "Please enter a question."
            )

        else:

            question_prompt = f"""
You are an expert VLSI Design Assistant.

Answer this question using the VLSI PDF content.

PDF CONTENT:

{st.session_state.pdf_text}

QUESTION:

{question}

Instructions:

- Answer clearly.
- Use simple English.
- Explain step by step.
- Give an example if useful.
- Explain VLSI terms.
- Do not invent information.
- If the PDF does not contain enough information,
  say so clearly.
- Maximum 250 words.
"""


            with st.spinner("🤔 Answering..."):

                answer = llm.invoke(
                    question_prompt
                )


            st.session_state.answer = answer.content


    # =====================================================
    # ANSWER
    # =====================================================

    if st.session_state.answer:

        st.subheader("📝 Answer")

        st.markdown(
            st.session_state.answer
        )