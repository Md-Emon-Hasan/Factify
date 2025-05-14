import re
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from src.logger import logger

# Ensure NLTK resources are downloaded
def download_nltk_resources():
    """Download required NLTK resources if not already present"""
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        logger.info("NLTK resources downloaded successfully")
    except Exception as e:
        logger.error(f"Error downloading NLTK resources: {str(e)}")
        raise

def calculate_text_features(df):
    """
    Calculate text features like character count, word count, sentence count
    
    Args:
        df (pd.DataFrame): Dataframe containing 'content' column
        
    Returns:
        pd.DataFrame: Dataframe with added text features
    """
    try:
        logger.info("Calculating text features...")
        
        # Create number of characters
        df['num_characters'] = df['content'].apply(len)
        
        # Create number of words
        df['num_words'] = df['content'].apply(lambda x: len(nltk.word_tokenize(x)))
        
        # Create number of sentences
        df['num_sentences'] = df['content'].apply(lambda x: len(nltk.sent_tokenize(x)))
        
        logger.info("Text features calculated successfully")
        return df
    
    except Exception as e:
        logger.error(f"Error calculating text features: {str(e)}")
        raise

def preprocess_text(text):
    """
    Clean and preprocess text data
    
    Args:
        text (str): Text to preprocess
        
    Returns:
        str: Preprocessed text
    """
    try:
        # Initialize stop words
        stop_words = set(stopwords.words('english'))
        
        # Step 1: Convert to lowercase
        text = text.lower()
        
        # Step 2: Remove URLs
        text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
        
        # Step 3: Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Step 4: Remove special characters, punctuation, and numbers
        text = re.sub(r"[^a-zA-Z\s]", '', text)
        
        # Step 5: Tokenize text
        words = word_tokenize(text)
        
        # Step 6: Remove stop words
        words = [word for word in words if word not in stop_words]
        
        # Step 7: Join words back into a single string
        processed_text = ' '.join(words)
        
        return processed_text
    
    except Exception as e:
        logger.error(f"Error preprocessing text: {str(e)}")
        return ""  # Return empty string if preprocessing fails

def clean_dataframe(df):
    """
    Clean the dataframe by applying text preprocessing to content column
    
    Args:
        df (pd.DataFrame): Dataframe with 'content' column
        
    Returns:
        pd.DataFrame: Cleaned dataframe with 'clean_text' column
    """
    try:
        logger.info("Cleaning text data...")
        
        # Apply preprocessing to content column
        df['clean_text'] = df['content'].apply(preprocess_text)
        
        # Drop unnecessary columns if needed
        df = df.drop(columns=['content'])
        
        # Handle NaN values
        df['clean_text'] = df['clean_text'].fillna('')
        
        # Ensure all values in the clean_text column are strings
        df['clean_text'] = df['clean_text'].astype(str)
        
        logger.info("Text data cleaned successfully")
        return df
    
    except Exception as e:
        logger.error(f"Error cleaning dataframe: {str(e)}")
        raise