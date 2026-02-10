import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from app.core.logger import logger

def download_nltk_resources():
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        logger.info("NLTK resources downloaded successfully")
    except Exception as e:
        logger.error(f"Error downloading NLTK resources: {str(e)}")
        # Don't raise here, just log, in case internet is down and we have them cached

def preprocess_text(text: str) -> str:
    try:
        # Check if text is string
        if not isinstance(text, str):
            return ""

        # Initialize stop words (lazy load might be better but this is fine for now)
        try:
             stop_words = set(stopwords.words('english'))
        except LookupError:
             download_nltk_resources()
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
        return "" 

def clean_dataframe(df):
    try:
        logger.info("Cleaning text data...")
        
        df['clean_text'] = df['content'].apply(preprocess_text)
        # Don't drop content if we might need it, but the original code did
        # df = df.drop(columns=['content']) 
        df['clean_text'] = df['clean_text'].fillna('')
        df['clean_text'] = df['clean_text'].astype(str)
        
        logger.info("Text data cleaned successfully")
        return df
    
    except Exception as e:
        logger.error(f"Error cleaning dataframe: {str(e)}")
        raise
