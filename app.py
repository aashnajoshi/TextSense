from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.core.credentials import AzureKeyCredential
import azure.cognitiveservices.speech as speechsdk
from azure.ai.translation.text.models import InputTextItem
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import os

load_dotenv()

text_analytics_endpoint = os.getenv('TEXT_ANALYTICS_ENDPOINT')
text_analytics_key = os.getenv('TEXT_ANALYTICS_KEY')
ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
ai_key = os.getenv('AI_SERVICE_KEY')
translator_region = os.getenv('TRANSLATOR_REGION')
translator_key = os.getenv('TRANSLATOR_KEY')
speech_key = os.getenv("SPEECH_API_KEY")
speech_region = os.getenv("SPEECH_REGION")

def analyze_sentiment(input_text):
    client = TextAnalyticsClient(endpoint=text_analytics_endpoint, credential=AzureKeyCredential(text_analytics_key))
    response = client.analyze_sentiment([input_text])
    return response[0]

def display_results(language_info, sentiment_info):
    st.write(f"Language detected: {language_info['name']} ({language_info['code']})")
    st.write(f"Sentiment detected: {sentiment_info['sentiment']}")
    st.write(f"Confidence Scores: Positive: {sentiment_info['confidence_scores'].positive}, Neutral: {sentiment_info['confidence_scores'].neutral}, Negative: {sentiment_info['confidence_scores'].negative}")
    st.write("\n")
    st.write("Please visit the following link to find the language codes of the supported Languages: https://docs.microsoft.com/en-us/azure/cognitive-services/translator/language-support")

def translate_text(input_text, target_language):
    translator_client = TextTranslationClient(TranslatorCredential(translator_key, translator_region))
    input_text_elements = [InputTextItem(text=input_text)]
    translation_response = translator_client.translate(content=input_text_elements, to=[target_language])
    translation = translation_response[0].translations[0].text
    return translation

def analyze_image(image_file):
    client = ImageAnalysisClient(endpoint=ai_endpoint, credential=AzureKeyCredential(ai_key))
    image = Image.open(image_file)
    result = client.analyze(image_data=image.tobytes(), visual_features=["Read"])
    detected_text = " ".join([line.text for block in result.read.blocks for line in block.lines]) if result.read.blocks else None
    return detected_text, image  

def speech_to_text():
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    audio_config = speechsdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    else:
        return None

# Streamlit UI
st.title('TextSense')

input_type = st.selectbox("Choose input type:", ["Text", "Image", "Voice"])

if input_type == 'Text':
    input_text = st.text_area("Enter text to analyze")
    if st.button("Analyze Text"):
        sentiment_result = analyze_sentiment(input_text)
        language_info = {'name': 'English', 'code': 'en'}
        sentiment_info = {
            'sentiment': sentiment_result.sentiment, 
            'confidence_scores': sentiment_result.confidence_scores
        }
        display_results(language_info, sentiment_info)
        st.session_state['input_text'] = input_text

elif input_type == 'Image':
    image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if image_file and st.button("Analyze Image"):
        detected_text, image = analyze_image(image_file)
        if detected_text:
            st.session_state['input_text'] = detected_text
            sentiment_result = analyze_sentiment(detected_text)
            language_info = {'name': 'English', 'code': 'en'}
            sentiment_info = {
                'sentiment': sentiment_result.sentiment, 
                'confidence_scores': sentiment_result.confidence_scores
            }
            display_results(language_info, sentiment_info)
            st.image(image, caption="Uploaded Image", use_column_width=True)
        else:
            st.write("No text detected in the image.")

elif input_type == 'Voice':
    if st.button("Record Voice"):
        recognized_text = speech_to_text()
        if recognized_text:
            st.session_state['input_text'] = recognized_text
            st.write("Detected Voice:")
            st.write(recognized_text)
            sentiment_result = analyze_sentiment(recognized_text)
            language_info = {'name': 'English', 'code': 'en'}
            sentiment_info = {
                'sentiment': sentiment_result.sentiment, 
                'confidence_scores': sentiment_result.confidence_scores
            }
            display_results(language_info, sentiment_info)
        else:
            st.write("No speech recognized.")

if 'input_text' in st.session_state:
    target_language = st.text_input("Enter the target language code for translation")
    if st.button("Translate"):
        if input_type == 'Voice':
            st.write("Detected Voice:")
            st.write(st.session_state['input_text'])
        translated_text = translate_text(st.session_state['input_text'], target_language)
        st.write(f"Translated text: {translated_text}")