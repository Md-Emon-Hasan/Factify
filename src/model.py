import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import GRU
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from src.logger import logger

def tokenize_and_pad(texts, vocab_size=10000, max_length=100, oov_token="<OOV>"):

    try:
        logger.info(f"Tokenizing texts with vocab_size={vocab_size}, max_length={max_length}...")
        
        # Create tokenizer
        tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
        tokenizer.fit_on_texts(texts)
        
        # Convert texts to sequences
        sequences = tokenizer.texts_to_sequences(texts)
        
        # Pad sequences
        padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post')
        
        logger.info("Tokenization and padding completed successfully")
        return tokenizer, padded_sequences
    
    except Exception as e:
        logger.error(f"Error in tokenization process: {str(e)}")
        raise

def prepare_data(df, test_size=0.2, random_state=42, vocab_size=10000, max_length=100):

    try:
        logger.info("Preparing data for model training...")
        
        # Split data into features and target
        X = df['clean_text']
        y = df['target']
        
        # Tokenize and pad sequences
        tokenizer, X_padded = tokenize_and_pad(X, vocab_size, max_length)
        
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X_padded, y, test_size=test_size, random_state=random_state
        )
        
        logger.info(f"Data prepared: X_train shape={X_train.shape}, X_test shape={X_test.shape}")
        return X_train, X_test, y_train, y_test, tokenizer
    
    except Exception as e:
        logger.error(f"Error preparing data: {str(e)}")
        raise

def build_lstm_gru_model(vocab_size, embedding_dim=100, max_length=100):

    try:
        logger.info(f"Building LSTM-GRU model with vocab_size={vocab_size}, embedding_dim={embedding_dim}...")
        
        # Build the model
        model = Sequential([
            Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=max_length),
            LSTM(100, return_sequences=True),
            GRU(100),
            Dropout(0.2),
            Dense(1, activation='sigmoid')
        ])
        
        # Compile the model
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
        logger.info("LSTM-GRU model built successfully")
        return model
    
    except Exception as e:
        logger.error(f"Error building model: {str(e)}")
        raise

def train_model(model, X_train, y_train, X_test, y_test, epochs=5, batch_size=64):
  
    try:
        logger.info(f"Training model for {epochs} epochs with batch_size={batch_size}...")
        
        # Create callback to save best model
        checkpoint_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'models',
            'best_model_checkpoint.h5'
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        
        checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
            filepath=checkpoint_path,
            save_best_only=True,
            monitor='val_accuracy',
            mode='max',
            verbose=1
        )
        
        # Early stopping to prevent overfitting
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=3,
            restore_best_weights=True,
            verbose=1
        )
        
        # Train the model
        history = model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[checkpoint_callback, early_stopping]
        )
        
        logger.info("Model training completed successfully")
        return model, history
    
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise

def save_model(model, model_path, tokenizer=None, tokenizer_path=None):

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save the model
        model.save(model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Save the tokenizer if provided
        if tokenizer and tokenizer_path:
            import pickle
            with open(tokenizer_path, 'wb') as handle:
                pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
            logger.info(f"Tokenizer saved to {tokenizer_path}")
    
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise