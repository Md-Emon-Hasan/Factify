import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter
from wordcloud import WordCloud
import os
from PIL import Image
from src.logger import logger

def create_plots_directory():
    """Create directory for saving plots if it doesn't exist"""
    plots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img', 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    return plots_dir

def plot_class_distribution(df, target_column='target', save_path=None):
    try:
        logger.info("Plotting class distribution...")
        
        plt.figure(figsize=(10, 6))
        
        # Create countplot
        ax = sns.countplot(x=target_column, data=df)
        
        # Add count labels
        for p in ax.patches:
            ax.annotate(f'{p.get_height()}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom')
        
        plt.title('Distribution of News Classes (0=Fake, 1=Real)')
        plt.xlabel('News Type')
        plt.ylabel('Count')
        
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Class distribution plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
        
        # Create pie chart
        plt.figure(figsize=(8, 8))
        label_counts = df[target_column].value_counts()
        plt.pie(label_counts, labels=['Fake News', 'Real News'], 
                autopct='%1.1f%%', startangle=90, 
                colors=['#03fcec','#0330fc'],
                explode=(0.05, 0))
        plt.title('Proportion of News Classes')
        
        if save_path:
            pie_path = save_path.replace('.png', '_pie.png')
            plt.savefig(pie_path)
            logger.info(f"Pie chart saved to {pie_path}")
        else:
            plt.show()
        
        plt.close()
        
    except Exception as e:
        logger.error(f"Error plotting class distribution: {str(e)}")
        plt.close()

def plot_text_features(df, save_path=None):
    try:
        logger.info("Plotting text features distribution...")
        
        features = ['num_characters', 'num_words', 'num_sentences']
        
        plt.figure(figsize=(15, 10))
        
        for i, feature in enumerate(features, 1):
            if feature in df.columns:
                plt.subplot(3, 1, i)
                sns.histplot(data=df, x=feature, hue='target', bins=50, kde=True)
                plt.title(f'Distribution of {feature}')
                plt.xlabel(feature)
                plt.ylabel('Count')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Text features plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
        
    except Exception as e:
        logger.error(f"Error plotting text features: {str(e)}")
        plt.close()

def create_wordcloud(df, target_value, text_column='clean_text', mask_path=None, save_path=None):

    try:
        logger.info(f"Creating wordcloud for target={target_value}...")
        
        # Filter dataframe by target value
        filtered_df = df[df['target'] == target_value]
        
        # Check if the filtered dataframe is empty
        if filtered_df.empty:
            logger.warning(f"No data available for target={target_value}")
            return
        
        # Load mask
        mask = None
        if mask_path and os.path.exists(mask_path):
            mask = np.array(Image.open(mask_path))
        
        # Generate text corpus
        text = filtered_df[text_column].str.cat(sep=' ')
        
        # Create wordcloud
        wc = WordCloud(width=2000, height=800, 
                      background_color='white', 
                      mask=mask,
                      colormap='rainbow',
                      max_words=200,
                      contour_width=3,
                      contour_color='steelblue')
        
        wc.generate(text)
        
        # Display wordcloud
        plt.figure(figsize=(20, 10))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title(f"Wordcloud for {'Real' if target_value == 1 else 'Fake'} News")
        
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Wordcloud saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
        
    except Exception as e:
        logger.error(f"Error creating wordcloud: {str(e)}")
        plt.close()

def plot_common_words(df, target_value, text_column='clean_text', n_words=10, save_path=None):

    try:
        logger.info(f"Plotting {n_words} most common words for target={target_value}...")
        
        # Filter dataframe by target value
        filtered_df = df[df['target'] == target_value]
        
        # Check if the filtered dataframe is empty
        if filtered_df.empty:
            logger.warning(f"No data available for target={target_value}")
            return
        
        # Create corpus of words
        corpus = []
        for text in filtered_df[text_column].dropna().tolist():
            if isinstance(text, str):
                for word in text.split():
                    corpus.append(word)
        
        # Count word frequencies
        word_counts = Counter(corpus).most_common(n_words)
        words, counts = zip(*word_counts)
        
        # Create bar plot
        plt.figure(figsize=(12, 8))
        sns.barplot(x=list(words), y=list(counts), palette="viridis")
        plt.title(f"Top {n_words} Most Common Words in {'Real' if target_value == 1 else 'Fake'} News")
        plt.xlabel('Words')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Common words plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
        
    except Exception as e:
        logger.error(f"Error plotting common words: {str(e)}")
        plt.close()

def run_eda(df, img_dir):

    try:
        logger.info("Starting exploratory data analysis...")
        
        # Create plots directory
        plots_dir = create_plots_directory()
        
        # Calculate text features
        from src.preprocessing import calculate_text_features
        df = calculate_text_features(df)
        
        # Plot class distribution
        plot_class_distribution(df, save_path=os.path.join(plots_dir, 'class_distribution.png'))
        
        # Plot text features
        plot_text_features(df, save_path=os.path.join(plots_dir, 'text_features.png'))
        
        # Create wordclouds
        mask_path = os.path.join(img_dir, 'mask-butterfly.png')
        if os.path.exists(mask_path):
            create_wordcloud(df, 0, mask_path=mask_path, 
                           save_path=os.path.join(plots_dir, 'fake_news_wordcloud.png'))
            create_wordcloud(df, 1, mask_path=mask_path, 
                           save_path=os.path.join(plots_dir, 'real_news_wordcloud.png'))
        
        # Plot common words
        plot_common_words(df, 0, save_path=os.path.join(plots_dir, 'fake_news_common_words.png'))
        plot_common_words(df, 1, save_path=os.path.join(plots_dir, 'real_news_common_words.png'))
        
        logger.info("Exploratory data analysis completed successfully")
        return df
        
    except Exception as e:
        logger.error(f"Error in EDA process: {str(e)}")
        raise