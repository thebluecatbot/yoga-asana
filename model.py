from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


app = Flask(__name__)

# Load English language model in spaCy
nlp = spacy.load("en_core_web_sm")

# Load the training dataset
train_df = pd.read_csv("train.csv")  
test_df = pd.read_csv("test (3).csv")  

# Lowercase the text in datasets
train_df['Benefits'] = train_df['Benefits'].str.lower()
test_df['Benefits'] = test_df['Benefits'].str.lower()

# Define function to remove punctuation
def remove_punctuation(text):
    return re.sub(r'[^\w\s]', '', text)

# Define function to remove words containing digits
def remove_digits(text):
    return re.sub(r'\w*\d\w*', '', text)

# Define function to remove stopwords
def remove_stopwords(text):
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop]
    return ' '.join(tokens)

# Define function to lemmatize words
def lemmatize_words(text):
    doc = nlp(text)
    lemmatized_tokens = [token.lemma_ for token in doc]
    return ' '.join(lemmatized_tokens)

# Apply text preprocessing steps to datasets
for df in [train_df, test_df]:
    df['Benefits'] = df['Benefits'].apply(remove_punctuation)
    df['Benefits'] = df['Benefits'].apply(remove_digits)
    df['Benefits'] = df['Benefits'].apply(remove_stopwords)
    df['Benefits'] = df['Benefits'].apply(lemmatize_words)
    df['Benefits'] = df['Benefits'].apply(lambda x: ' '.join(x.split()))

# Split the data into train and test sets
X_train = train_df['Benefits']
y_train = train_df['Asana']
X_test = test_df['Benefits']
y_test = test_df['Asana']

# Define the pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('model', LogisticRegression(n_jobs=1, C=1e5, penalty='l2',solver='lbfgs'))
])

# Fit the pipeline on the training data
pipeline.fit(X_train, y_train)


def selected_pose():
    input_text = request.json.get('text')
    input_text_processed = ' '.join(lemmatize_words(remove_stopwords(remove_digits(remove_punctuation(input_text)))).split())
    prediction_probs = pipeline.predict_proba([input_text_processed])[0]
    top_indices = np.argsort(prediction_probs)[-3:][::-1]
    top_classes = pipeline.classes_[top_indices]
    top_probs = prediction_probs[top_indices]
    result = [{'class': top_classes[i], 'probability': top_probs[i]} for i in range(3)]
    return jsonify(result)