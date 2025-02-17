import streamlit as st
import fitz  # PyMuPDF
import openai
import os

# ---------------------------
# Utility Functions
# ---------------------------
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        # Read the entire file as bytes
        pdf_bytes = pdf_file.read()
        # Open the PDF from bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        # Iterate over all pages explicitly using an index
        for page_number in range(len(doc)):
            page = doc[page_number]
            page_text = page.get_text("text")  # explicitly get text mode
            text += f"\n\n--- Page {page_number+1} ---\n\n"  # optional page separator
            text += page_text
        doc.close()
    except Exception as e:
        st.error(f"Error extracting text: {e}")
    return text

def preprocess_text(text):
    """
    Basic preprocessing: cleaning up whitespace.
    You can add more cleaning or segmentation as needed.
    """
    # Remove extra whitespace/newlines
    cleaned_text = " ".join(text.split())
    return cleaned_text

def generate_marketing_concepts(processed_text):
    """
    Uses OpenAI's GPT to generate marketing concepts.
    """
    # Craft a prompt that includes the processed text
    prompt = (
        "You are an expert marketer in Ayurvedic herbs. "
        "Given the following research summary, generate three innovative and engaging marketing concepts that highlight the benefits, unique qualities, and potential market positioning of these herbs.\n\n"
        f"Research Summary:\n{processed_text}\n\n"
        "Marketing Concepts:"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert marketer with deep domain knowledge in Ayurveda."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        output = response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating concepts: {e}")
        output = "Failed to generate concepts."
    return output

def save_feedback(feedback_data):
    """
    Save feedback data to a local file.
    In production, consider storing feedback in a database.
    """
    try:
        with open("feedback.txt", "a") as f:
            f.write(feedback_data + "\n")
    except Exception as e:
        st.error(f"Error saving feedback: {e}")

# ---------------------------
# Streamlit App Layout
# ---------------------------
st.title("Marketing Concepts Tool")

# --- API Key Section ---
st.header("Enter Your OpenAI API Key")
user_api_key = st.text_input("Your OpenAI API Key", type="password")

if not user_api_key:
    st.warning("Please enter your OpenAI API Key to proceed.")
    st.stop()
else:
    # Set the API key provided by the user.
    openai.api_key = user_api_key

    # Optionally, test the API key
    if st.button("Test API Key"):
        try:
            _ = openai.Model.list()
            st.success("API Key is valid!")
        except Exception as e:
            st.error(f"API Key test failed: {e}")
            st.stop()

    # --- Main Application ---
    st.header("1. Upload Research Paper")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        st.info("Extracting text from PDF...")
        extracted_text = extract_text_from_pdf(uploaded_file)
        
        if extracted_text:
            st.subheader("Extracted Text")
            # Using text_area with a fixed height makes the content scrollable.
            st.text_area("Extracted Text", value=extracted_text, height=300, disabled=True)
            
            st.header("2. Preprocessing")
            processed_text = preprocess_text(extracted_text)
            st.subheader("Preprocessed Text Preview")
            st.text_area("Preprocessed Text", value=processed_text, height=300, disabled=True)
            
            st.header("3. Generate Marketing Concepts")
            if st.button("Generate Concepts"):
                with st.spinner("Generating marketing concepts..."):
                    marketing_concepts = generate_marketing_concepts(processed_text)
                st.subheader("Generated Marketing Concepts")
                st.write(marketing_concepts)
                
                st.header("4. Provide Feedback")
                st.write("Please rate the quality of the generated marketing concepts.")
                rating = st.radio("Rating", ("Excellent", "Good", "Average", "Poor"))
                comments = st.text_area("Additional Comments (optional)")
                
                if st.button("Submit Feedback"):
                    feedback_data = f"Rating: {rating} | Comments: {comments} | Concepts: {marketing_concepts}"
                    save_feedback(feedback_data)
                    st.success("Thank you for your feedback!")
        else:
            st.error("No text could be extracted from the uploaded PDF.")
    else:
        st.info("Please upload a research paper in PDF format to begin.")
