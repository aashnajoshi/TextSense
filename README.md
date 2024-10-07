# TextSense
TextSense is a text analysis tool that processes and analyzes text data using machine learning techniques. It provides insights such as sentiment analysis, keyword extraction, and named entity recognition to help users understand textual data in depth.

## Features
- Sentiment Analysis to determine the emotional tone of the text.
- Keyword Extraction to identify important terms.
- Named Entity Recognition to classify entities such as names, organizations, and locations.

## Usage

### All required libraries can be installed using a single-line command:
```bash
pip install -r requirements.txt
```

### While to run the code:

#### Console-based version:
```bash
python main.py
```

#### Streamlit-based version:
```bash
streamlit run app.py
```

## Description about various files:
- **.env** Contains all the credentials and secret information.
- **app.py:** Contains a streamlit-based version of the main code for interactive text analysis.
- **main.py:** Handles the console-based version of the project and runs all primary text analysis functions.
- **requirements.txt:** File containing all required Python modules.
