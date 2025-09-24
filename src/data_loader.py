import pandas as pd
import os
from src.logger import logger

def load_data(true_path, fake_path):
    try:
        logger.info("Loading data from files...")
        
        # Load datasets
        df_true = pd.read_csv(true_path)
        df_fake = pd.read_csv(fake_path)
        
        # Add target column
        df_true['target'] = 1
        df_fake['target'] = 0
        
        # Concatenate datasets
        df = pd.concat([df_true, df_fake]).reset_index(drop=True)
        
        # Remove duplicates
        duplicates_count = df.duplicated().sum()
        if duplicates_count > 0:
            logger.info(f"Removing {duplicates_count} duplicate entries")
            df.drop_duplicates(inplace=True)
        
        # Combine title and text into content
        df['content'] = df['title'] + ' ' + df['text']
        
        # Drop unnecessary columns
        df = df.drop(columns=['date', 'subject'])
        
        logger.info(f"Data loaded successfully: {df.shape[0]} rows and {df.shape[1]} columns")
        return df
    
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise