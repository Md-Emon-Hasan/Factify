import os
import tensorflow as tf

# disable GPU usage
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# TensorFlow logs and warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

tf.get_logger().setLevel('ERROR')

# Check if TensorFlow is detecting a GPU
if tf.config.list_physical_devices('GPU'):
    print("TensorFlow is using GPU, which is not expected as we disabled it.")
else:
    print("TensorFlow is using the CPU as expected.")

from flask import Flask, request, render_template
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')

app = Flask(__name__)

# Load model and tokenizer
base_dir = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(base_dir, 'models', 'saved_models', 'fake_news_detector.h5')
tokenizer_path = os.path.join(base_dir, 'models', 'saved_models', 'tokenizer.pickle')

# Load the model
model = load_model(model_path)

# Load the tokenizer
with open(tokenizer_path, 'rb') as f:
    tokenizer = pickle.load(f)

# Preprocessing function
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r"[^a-zA-Z\s]", '', text)
    text = text.strip()
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)

@app.route('/')
def home():
    return render_template('index.html', prediction=None)

@app.route('/predict', methods=['POST'])
def predict():
    input_text = request.form['text']
    cleaned_text = preprocess_text(input_text)
    sequences = tokenizer.texts_to_sequences([cleaned_text])
    padded = pad_sequences(sequences, maxlen=100, padding='post')
    prediction = model.predict(padded)
    result = "Fake News" if prediction < 0.5 else "Real News"
    return render_template('index.html', prediction=result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)