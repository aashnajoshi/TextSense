from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog
import time
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
    print(f"Language detected: {language_info['name']} ({language_info['code']})")
    print(f"Sentiment detected: {sentiment_info['sentiment']}\n")
    print("Please visit the following link to find the language codes of the supported Languages: https://docs.microsoft.com/en-us/azure/cognitive-services/translator/language-support\n")

def analyze_text_input(inputText):
    translator_client = TextTranslationClient(TranslatorCredential(translator_key, translator_region))
    sentiment_result = analyze_sentiment(inputText)
    sentiment = sentiment_result.sentiment
    confidence_scores = sentiment_result.confidence_scores
    language_info = {'name': 'English', 'code': 'en'}
    sentiment_info = {
        'sentiment': sentiment,
        'confidence_scores': confidence_scores}

    display_results(language_info, sentiment_info)
    target_language = input("Enter the target language code for translation (e.g., 'fr' for French) or 'q' for quit: ")
    if target_language.lower() == 'q':
        print("Exiting the program.")
        return

    input_text_elements = [InputTextItem(text=inputText)]
    translationResponse = translator_client.translate(content=input_text_elements, to=[target_language])
    translation = translationResponse[0] if translationResponse else None

    if translation:
        translated_text = translation.translations[0].text
        print(f"\nTranslated text in language: {translated_text}\n")

def get_image_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
    root.destroy()
    return file_path

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
    
    if detected_text:
        full_text = " ".join(detected_text)
        print("Detected text from image:")
        print(full_text)
        analyze_text_input(full_text)
    else:
        print("No text detected in the image.")

def speech_to_text():
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    audio_config = speechsdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    print("Listening...")
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Recognized: {result.text}")
        return result.text
    else:
        print("No speech recognized.")
        return None

def analyze_voice_input():
    recognized_text = speech_to_text()
    if recognized_text:
        sentiment_result = analyze_sentiment(recognized_text)
        sentiment = sentiment_result.sentiment
        confidence_scores = sentiment_result.confidence_scores
        language_info = {'name': 'English', 'code': 'en'}
        sentiment_info = {
            'sentiment': sentiment,
            'confidence_scores': confidence_scores}
        
        display_results(language_info, sentiment_info)
        
        target_language = input("Enter the target language code for translation (e.g., 'fr' for French) or 'q' for quit: ")
        if target_language.lower() == 'q':
            print("Exiting the program.")
            return
        
        translator_client = TextTranslationClient(TranslatorCredential(translator_key, translator_region))
        input_text_elements = [InputTextItem(text=recognized_text)]
        translationResponse = translator_client.translate(content=input_text_elements, to=[target_language])
        translation = translationResponse[0] if translationResponse else None

        if translation:
            translated_text = translation.translations[0].text
            print(f"\nTranslated text in language: {translated_text}\n")

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        input_type = input("What type of input do you want to analyze and translate?\n1. Text\n2. Image\n3. Voice\nEnter your choice (1, 2, or 3): ")
        if input_type == '1':
            inputText = input("Enter text to analyze: ")
            analyze_text_input(inputText)
            time.sleep(10)
        elif input_type == '2':
            image_file = get_image_file()
            if image_file:
                analyze_image(image_file)
                time.sleep(10)
            else:
                print("No file selected.")
        elif input_type == '3':
            analyze_voice_input()
            time.sleep(10)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()