from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

# Initialize Azure service credentials
text_analytics_endpoint = os.getenv('TEXT_ANALYTICS_ENDPOINT')
text_analytics_key = os.getenv('TEXT_ANALYTICS_KEY')
ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
ai_key = os.getenv('AI_SERVICE_KEY')
translator_region = os.getenv('TRANSLATOR_REGION')
translator_key = os.getenv('TRANSLATOR_KEY')

# Function to analyze sentiment
def analyze_sentiment(input_text):
    client = TextAnalyticsClient(endpoint=text_analytics_endpoint, credential=AzureKeyCredential(text_analytics_key))
    response = client.analyze_sentiment([input_text])
    return response[0]

# Function to analyze text input
def analyze_text_input(inputText, target_language):
    translator_client = TextTranslationClient(TranslatorCredential(translator_key, translator_region))
    client = TextAnalyticsClient(endpoint=text_analytics_endpoint, credential=AzureKeyCredential(text_analytics_key))
    
    sentiment_result = analyze_sentiment(inputText)
    sentiment = sentiment_result.sentiment
    confidence_scores = sentiment_result.confidence_scores

    input_text_elements = [InputTextItem(text=inputText)]
    translationResponse = translator_client.translate(content=input_text_elements, to=[target_language])
    translation = translationResponse[0] if translationResponse else None

    if translation:
        sourceLanguage = translation.detected_language
        translated_text = translation.translations[0].text
        return {
            "source_language": sourceLanguage,
            "sentiment": sentiment,
            "confidence_scores": confidence_scores,
            "translated_text": translated_text
        }
    return None

# Function to analyze image
def analyze_image(image_file):
    client = ImageAnalysisClient(endpoint=ai_endpoint, credential=AzureKeyCredential(ai_key))
    with open(image_file, "rb") as f:
        image_data = f.read()
        
    result = client.analyze(image_data=image_data, visual_features=[VisualFeatures.READ])
    
    detected_text = []
    if result.read and result.read.blocks:
        for block in result.read.blocks:
            for line in block.lines:
                detected_text.append(line.text)
    return detected_text

# Streamlit app
def main():
    st.title("Analyzer and Translator")

    input_type = st.selectbox("Select input type:", ["Text", "Image"])

    if input_type == "Text":
        inputText = st.text_area("Enter text to analyze:")
        target_language = st.text_input("Enter the target language code for translation (e.g., 'fr' for French):")

        if st.button("Analyze Text"):
            if inputText and target_language:
                results = analyze_text_input(inputText, target_language)
                if results:
                    st.write(f"Detected language: {results['source_language']}")
                    st.write(f"Sentiment: {results['sentiment']}")
                    st.write(f"Confidence scores: Positive: {results['confidence_scores'].positive}, Neutral: {results['confidence_scores'].neutral}, Negative: {results['confidence_scores'].negative}")
                    st.write(f"Translated text in {target_language}: {results['translated_text']}")
                else:
                    st.error("Error in translation.")

    elif input_type == "Image":
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "bmp"])
        
        if uploaded_file is not None:
            with open("temp_image", "wb") as f:
                f.write(uploaded_file.getbuffer())
            if st.button("Analyze Image"):
                detected_text = analyze_image("temp_image")
                if detected_text:
                    st.write("Detected Text:")
                    for line in detected_text:
                        st.write(line)
                else:
                    st.write("No text detected in the image.")

if __name__ == "__main__":
    main()