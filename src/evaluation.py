import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import os
from src.logger import logger

def evaluate_model(model, X_test, y_test):

    try:
        logger.info("Evaluating model performance...")
        
        # Get predictions
        probabilities = model.predict(X_test)
        predictions = np.where(probabilities > 0.5, 1, 0)
        
        # Calculate accuracy
        accuracy = accuracy_score(y_test, predictions)
        logger.info(f"Model accuracy: {accuracy:.4f}")
        
        return accuracy, predictions, probabilities
    
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        raise

def plot_confusion_matrix(y_true, y_pred, save_path=None):

    try:
        logger.info("Plotting confusion matrix...")
        
        # Compute confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Create plot
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Fake', 'Real'], 
                   yticklabels=['Fake', 'Real'])
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.title('Confusion Matrix')
        
        if save_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path)
            logger.info(f"Confusion matrix saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
        
    except Exception as e:
        logger.error(f"Error plotting confusion matrix: {str(e)}")
        plt.close()

def print_classification_report(y_true, y_pred):

    try:
        logger.info("Generating classification report...")
        
        # Get classification report
        report = classification_report(y_true, y_pred)
        
        # Print and log the report
        print(report)
        logger.info(f"\n{report}")
        
    except Exception as e:
        logger.error(f"Error generating classification report: {str(e)}")
        raise

def plot_training_history(history, save_path=None):

    try:
        logger.info("Plotting training history...")
        
        # Create plot
        plt.figure(figsize=(12, 5))
        
        # Plot accuracy
        plt.subplot(1, 2, 1)
        plt.plot(history.history['accuracy'], label='Training Accuracy')
        plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        
        # Plot loss
        plt.subplot(1, 2, 2)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        plt.tight_layout()
        
        if save_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path)
            logger.info(f"Training history plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
        
    except Exception as e:
        logger.error(f"Error plotting training history: {str(e)}")
        plt.close()

def evaluate_and_visualize(model, X_test, y_test, history=None, plots_dir=None):

    try:
        logger.info("Starting model evaluation and visualization...")
        
        # Create plots directory if provided
        if plots_dir:
            os.makedirs(plots_dir, exist_ok=True)
        
        # Evaluate model
        accuracy, predictions, _ = evaluate_model(model, X_test, y_test)
        
        # Print classification report
        print_classification_report(y_test, predictions)
        
        # Plot confusion matrix
        cm_path = os.path.join(plots_dir, 'confusion_matrix.png') if plots_dir else None
        plot_confusion_matrix(y_test, predictions, save_path=cm_path)
        
        # Plot training history if provided
        if history:
            history_path = os.path.join(plots_dir, 'training_history.png') if plots_dir else None
            plot_training_history(history, save_path=history_path)
        
        logger.info("Model evaluation and visualization completed successfully")
        return accuracy
        
    except Exception as e:
        logger.error(f"Error in model evaluation and visualization: {str(e)}")
        raise