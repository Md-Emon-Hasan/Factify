import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from app.core.logger import logger
from app.core.config import settings

class FakeNewsDetector:

    def __init__(self, model_path, tokenizer_path, max_length=100):

        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.max_length = max_length
        self.model = None
        self.tokenizer = None
        
        # Load model and tokenizer
        self._load_model()
        self._load_tokenizer()
        
    def _load_model(self):
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Model file not found at {self.model_path}")
                return

            logger.info(f"Loading model from {self.model_path}")
            self.model = load_model(self.model_path)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            # Don't raise, allowing app to start without model (e.g. for first run/training)
            
    def _load_tokenizer(self):
        try:
            if not os.path.exists(self.tokenizer_path):
                logger.warning(f"Tokenizer file not found at {self.tokenizer_path}")
                return

            logger.info(f"Loading tokenizer from {self.tokenizer_path}")
            with open(self.tokenizer_path, 'rb') as handle:
                self.tokenizer = pickle.load(handle)
            logger.info("Tokenizer loaded successfully")
        except Exception as e:
            logger.error(f"Error loading tokenizer: {str(e)}")
            
    def preprocess_text(self, text):
        try:
            if not self.tokenizer:
                raise ValueError("Tokenizer not loaded")

            # Convert text to sequence
            # Note: The original code expected raw text, but usually we should apply the same cleaning 
            # (preprocess_text from preprocessing.py) before tokenizing. 
            # However, I will stick to the original logic for now which seems to assume the tokenizer handles it 
            # OR the input text is raw. 
            # Wait, the original pipeline `prediction_pipeline` passed raw text to `detector.predict`.
            # And `detector.predict` called `self.preprocess_text` (internal) which just did `texts_to_sequences`.
            # This implies the tokenizer was trained on raw text? 
            # In `train_model`, `prepare_data` called `tokenize_and_pad(X, ...)` where X was `df['clean_text']`.
            # So the tokenizer expects CLEAN text.
            # I must clean the text first!
            
            from app.services.preprocessing import preprocess_text as clean_text_func
            cleaned_text = clean_text_func(text)

            sequence = self.tokenizer.texts_to_sequences([cleaned_text])
            
            # Pad sequence
            padded_sequence = pad_sequences(sequence, maxlen=self.max_length, padding='post')
            
            return padded_sequence
        except Exception as e:
            logger.error(f"Error preprocessing text for prediction: {str(e)}")
            raise
            
    def predict(self, text):
        try:
            logger.info(f"Making prediction for text: {text[:50]}...")
            
            # Preprocess text
            try:
                padded_sequence = self.preprocess_text(text)
                logger.info("Text preprocessing and padding successful")
            except Exception as e:
                logger.error(f"Preprocessing failed: {e}")
                return "ERROR", 0.0

            # Make prediction
            try:
                # Ensure input is int32 for Embedding layer compatibility
                padded_sequence = np.array(padded_sequence, dtype=np.int32)
                
                logger.info(f"Calling model.predict on shape {padded_sequence.shape} with dtype {padded_sequence.dtype}...")
                
                # Force CPU execution to avoid Windows/GPU/OneDNN conflicts like [Errno 22]
                with tf.device('/cpu:0'):
                    prediction_result = self.model.predict(padded_sequence, verbose=0)
                
                logger.info(f"Raw prediction result: {prediction_result}")
                probability = float(prediction_result[0][0])
            except Exception as e:
                logger.error(f"Model prediction failed: {e}")
                # Return ERROR label so frontend can show the issue
                return "ERROR", 0.0
            
            # Convert probability to label
            prediction = 1 if probability > 0.5 else 0
            label = "REAL" if prediction == 1 else "FAKE"
            
            logger.info(f"Prediction: {label} (probability: {probability:.4f})")
            
            return label, float(probability)
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return "ERROR", 0.0

# Singleton instance
# Using paths from configuration for reliability
detector = FakeNewsDetector(settings.MODEL_PATH, settings.TOKENIZER_PATH)
