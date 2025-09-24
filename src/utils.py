import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from src.logger import logger

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
            logger.info(f"Loading model from {self.model_path}")
            self.model = load_model(self.model_path)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
            
    def _load_tokenizer(self):
        try:
            logger.info(f"Loading tokenizer from {self.tokenizer_path}")
            with open(self.tokenizer_path, 'rb') as handle:
                self.tokenizer = pickle.load(handle)
            logger.info("Tokenizer loaded successfully")
        except Exception as e:
            logger.error(f"Error loading tokenizer: {str(e)}")
            raise
            
    def preprocess_text(self, text):

        try:
            # Convert text to sequence
            sequence = self.tokenizer.texts_to_sequences([text])
            
            # Pad sequence
            padded_sequence = pad_sequences(sequence, maxlen=self.max_length, padding='post')
            
            return padded_sequence
        except Exception as e:
            logger.error(f"Error preprocessing text: {str(e)}")
            raise
            
    def predict(self, text):

        try:
            logger.info("Making prediction...")
            
            # Preprocess text
            padded_sequence = self.preprocess_text(text)
            
            # Make prediction
            probability = self.model.predict(padded_sequence)[0][0]
            
            # Convert probability to label
            prediction = 1 if probability > 0.5 else 0
            label = "REAL" if prediction == 1 else "FAKE"
            
            logger.info(f"Prediction: {label} (probability: {probability:.4f})")
            
            return label, probability
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise

def predict_batch(detector, texts):

    try:
        logger.info(f"Making batch predictions on {len(texts)} texts...")
        
        results = []
        for text in texts:
            label, probability = detector.predict(text)
            results.append((text, label, probability))
            
        logger.info("Batch prediction completed")
        return results
    except Exception as e:
        logger.error(f"Error in batch prediction: {str(e)}")
        raise