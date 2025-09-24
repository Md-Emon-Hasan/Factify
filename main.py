import os
import yaml
import argparse
import pandas as pd
import numpy as np
import tensorflow as tf
from src.logger import logger
from src.data_loader import load_data
from src.preprocessing import download_nltk_resources
from src.preprocessing import calculate_text_features
from src.preprocessing import clean_dataframe
from src.eda import run_eda
from src.model import prepare_data
from src.model import build_lstm_gru_model
from src.model import train_model
from src.model import save_model
from src.evaluation import evaluate_and_visualize
from src.utils import FakeNewsDetector
from src.utils import predict_batch

def load_config(config_path):

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise

def create_directories(config):

    try:
        # Create data directories
        os.makedirs(os.path.dirname(config['paths']['data']['clean_data']), exist_ok=True)
        
        # Create model directory
        os.makedirs(config['paths']['models']['model_dir'], exist_ok=True)
        
        # Create image directory
        os.makedirs(config['paths']['img']['plots_dir'], exist_ok=True)
        
        logger.info("Directories created successfully")
    except Exception as e:
        logger.error(f"Error creating directories: {str(e)}")
        raise

def data_preparation_pipeline(config):

    try:
        logger.info("Starting data preparation pipeline...")
        
        # Download NLTK resources
        download_nltk_resources()
        
        # Load data
        df = load_data(
            config['paths']['data']['true_news'],
            config['paths']['data']['fake_news']
        )
        
        # Run EDA
        df = run_eda(df, config['paths']['img']['img_dir'])
        
        # Clean data
        df = clean_dataframe(df)
        
        # Save clean data
        clean_data_path = config['paths']['data']['clean_data']
        os.makedirs(os.path.dirname(clean_data_path), exist_ok=True)
        df.to_csv(clean_data_path, index=False)
        logger.info(f"Clean data saved to {clean_data_path}")
        
        return df
    
    except Exception as e:
        logger.error(f"Error in data preparation pipeline: {str(e)}")
        raise

def model_training_pipeline(config, df=None):

    try:
        logger.info("Starting model training pipeline...")
        
        # Load clean data if not provided
        if df is None:
            clean_data_path = config['paths']['data']['clean_data']
            if os.path.exists(clean_data_path):
                df = pd.read_csv(clean_data_path)
                logger.info(f"Clean data loaded from {clean_data_path}")
            else:
                logger.error(f"Clean data file not found at {clean_data_path}")
                raise FileNotFoundError(f"Clean data file not found at {clean_data_path}")
        
        # Prepare data
        X_train, X_test, y_train, y_test, tokenizer = prepare_data(
            df,
            test_size=config['test_size'],
            random_state=config['random_state'],
            vocab_size=config['vocab_size'],
            max_length=config['max_length']
        )
        
        # Build model
        model = build_lstm_gru_model(
            vocab_size=config['vocab_size'],
            embedding_dim=config['embedding_dim'],
            max_length=config['max_length']
        )
        
        # Train model
        trained_model, history = train_model(
            model,
            X_train, y_train,
            X_test, y_test,
            epochs=config['epochs'],
            batch_size=config['batch_size']
        )
        
        # Evaluate model
        plots_dir = config['paths']['img']['plots_dir']
        accuracy = evaluate_and_visualize(
            trained_model,
            X_test, y_test,
            history=history,
            plots_dir=plots_dir
        )
        
        # Save model and tokenizer
        save_model(
            trained_model,
            config['paths']['models']['best_model'],
            tokenizer=tokenizer,
            tokenizer_path=config['paths']['models']['tokenizer']
        )
        
        return trained_model, accuracy
    
    except Exception as e:
        logger.error(f"Error in model training pipeline: {str(e)}")
        raise

def prediction_pipeline(config, text):

    try:
        logger.info("Starting prediction pipeline...")
        
        # Initialize detector
        detector = FakeNewsDetector(
            model_path=config['paths']['models']['best_model'],
            tokenizer_path=config['paths']['models']['tokenizer'],
            max_length=config['max_length']
        )
        
        # Make prediction
        label, probability = detector.predict(text)
        
        return label, probability
    
    except Exception as e:
        logger.error(f"Error in prediction pipeline: {str(e)}")
        raise

def main():
    """Main function to run the pipeline"""
    parser = argparse.ArgumentParser(description='Fake News Detection')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--mode', type=str, default='train',
                        choices=['train', 'predict'],
                        help='Mode: train or predict')
    parser.add_argument('--text', type=str, default=None,
                        help='Text to predict (used in predict mode)')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Create directories
        create_directories(config)
        
        if args.mode == 'train':
            # Data preparation
            df = data_preparation_pipeline(config)
            
            # Model training
            model, accuracy = model_training_pipeline(config, df)
            
            logger.info(f"Model training completed with accuracy: {accuracy:.4f}")
            
        elif args.mode == 'predict':
            # Check if text is provided
            if args.text is None:
                logger.error("Text argument is required in predict mode")
                raise ValueError("Text argument is required in predict mode")
            
            # Make prediction
            label, probability = prediction_pipeline(config, args.text)
            
            logger.info(f"Prediction result: {label} (probability: {probability:.4f})")
            print(f"Prediction result: {label} (probability: {probability:.4f})")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        raise