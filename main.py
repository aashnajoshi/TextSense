from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
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

def analyze_sentiment(input_text):
    client = TextAnalyticsClient(endpoint=text_analytics_endpoint, credential=AzureKeyCredential(text_analytics_key))
    response = client.analyze_sentiment([input_text])
    return response[0]

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
            "translated_text": translated_text}
    return None

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
    return detected_text

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        input_type = input("What type of input do you want to analyze and translate?\n1. Text\n2. Image\nEnter your choice (1 or 2): ")
        if input_type == '1':
            inputText = input("Enter text to analyze: ")
            target_language = input("Enter the target language code for translation (e.g., 'fr' for French): ")
            results = analyze_text_input(inputText, target_language)
            if results:
                print(f"Detected language: {results['source_language']}")
                print(f"Sentiment: {results['sentiment']}")
                print(f"Confidence scores: Positive: {results['confidence_scores'].positive}, Neutral: {results['confidence_scores'].neutral}, Negative: {results['confidence_scores'].negative}")
                print(f"Translated text in {target_language}: {results['translated_text']}")
                time.sleep(5)
            else:
                print("Error in translation.")
        elif input_type == '2':
            image_file = get_image_file()
            if image_file:
                detected_text = analyze_image(image_file)
                time.sleep(5)
                if detected_text:
                    print("Detected Text:")
                    for line in detected_text:
                        print(line)
                else:
                    print("No text detected in the image.")
            else:
                print("No file selected.")
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()