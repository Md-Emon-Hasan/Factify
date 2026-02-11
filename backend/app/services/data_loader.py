import pandas as pd
from app.core.logger import logger

def load_data(true_path: str, fake_path: str) -> pd.DataFrame:
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
        # Check if columns exist before dropping to avoid errors if re-running
        cols_to_drop = ['date', 'subject']
        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
        
        logger.info(f"Data loaded successfully: {df.shape[0]} rows and {df.shape[1]} columns")
        return df
    
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise
