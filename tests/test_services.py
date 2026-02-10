import pytest
import pandas as pd
import numpy as np
import os
import importlib
import sys
from unittest.mock import patch, MagicMock, mock_open
from app.services.data_loader import load_data
from app.services.preprocessing import preprocess_text, clean_dataframe, download_nltk_resources
from app.services.prediction import FakeNewsDetector
import app.services.prediction
from app.services.model import prepare_data, build_lstm_gru_model, train_model, save_model, tokenize_and_pad

# --- Data Loader Tests ---
def test_load_data(tmp_path):
    true_csv = tmp_path / "true.csv"
    fake_csv = tmp_path / "fake.csv"
    df_true = pd.DataFrame({'title': ['T1', 'T1'], 'text': ['Text1', 'Text1'], 'date': ['D1', 'D1'], 'subject': ['S1', 'S1']})
    df_fake = pd.DataFrame({'title': ['F1'], 'text': ['Text2'], 'date': ['D2'], 'subject': ['S2']})
    df_true.to_csv(true_csv, index=False)
    df_fake.to_csv(fake_csv, index=False)
    
    df = load_data(str(true_csv), str(fake_csv))
    assert len(df) == 2

def test_load_data_error():
    with pytest.raises(Exception):
        load_data("non_existent.csv", "non_existent.csv")

# --- Preprocessing Tests ---
def test_preprocess_text():
    text = "Hello World! https://example.com <html>"
    processed = preprocess_text(text)
    assert "hello" in processed
    # Ensure regex coverage
    text2 = "http://test.com www.test.com"
    processed2 = preprocess_text(text2)
    assert "http" not in processed2

def test_preprocess_text_empty():
    assert preprocess_text(None) == ""

@patch("app.services.preprocessing.logger")
def test_download_nltk_success(mock_logger):
    with patch("nltk.download") as mock_download:
        download_nltk_resources()
        assert mock_download.call_count == 2
        mock_logger.info.assert_called()

@patch("app.services.preprocessing.logger")
def test_download_nltk_error(mock_logger):
    with patch("nltk.download", side_effect=Exception("Download failed")):
        download_nltk_resources()
        mock_logger.error.assert_called()

def test_clean_dataframe():
    df = pd.DataFrame({'content': ['Test content']})
    clean_df = clean_dataframe(df)
    assert 'clean_text' in clean_df.columns

def test_clean_dataframe_error():
    with pytest.raises(Exception):
        clean_dataframe(None)

@patch("app.services.preprocessing.stopwords")
def test_preprocess_text_lookup_error(mock_stopwords):
    mock_stopwords.words.side_effect = [LookupError("Resource not found"), ["i", "me"]]
    with patch("app.services.preprocessing.download_nltk_resources") as mock_download:
        text = "i am text"
        preprocess_text(text)
        mock_download.assert_called_once()

# --- Prediction Tests ---
# --- Prediction Tests ---
@patch("app.services.prediction.logger")
@patch("app.services.prediction.load_model")
@patch("app.services.prediction.pickle.load")
def test_detector_init(mock_pickle, mock_load_model, mock_logger):
    # Patch os.path.exists globally via context manager
    with patch("os.path.exists", return_value=True):
        # Patch open globally via context manager
        # Patch both builtins.open and io.open for robustness
        with patch("builtins.open", mock_open(read_data=b"dummy_data")) as mock_file:
             with patch("io.open", mock_file):
                path = "dummy_model"
                tok_path = "dummy_tok"
                
                # Configure mocks
                mock_load_model.return_value = MagicMock()
                mock_pickle.return_value = MagicMock()
            
                detector = FakeNewsDetector(path, tok_path)
                
                # Debugging info
                if mock_logger.error.called:
                     print(f"Logger error called: {mock_logger.error.call_args}")
                     
                assert detector.model is not None, "Model was not loaded"
                assert detector.tokenizer is not None, "Tokenizer was not loaded"

@patch("app.services.prediction.load_model")
def test_detector_init_no_files(mock_load_model):
    with patch("os.path.exists", return_value=False):
        detector = FakeNewsDetector("path", "path")
        assert detector.model is None

def test_detector_predict_no_model():
    detector = FakeNewsDetector("bad_path", "bad_path")
    detector.model = None
    detector.preprocess_text = MagicMock(return_value=np.zeros((1, 100)))
    
    label, prob = detector.predict("test")
    assert label == "ERROR" 

@patch("app.services.prediction.logger")
def test_detector_predict_error(mock_logger):
    detector = FakeNewsDetector("bad_path", "bad_path")
    detector.model = MagicMock()
    detector.model.predict.side_effect = Exception("Model error")
    detector.tokenizer = MagicMock()
    detector.preprocess_text = MagicMock(return_value=np.zeros((1, 100)))
    
    label, prob = detector.predict("test")
    assert label == "ERROR"
    assert prob == 0.0

@patch("app.services.prediction.logger")
def test_detector_predict_preprocess_error(mock_logger):
    detector = FakeNewsDetector("bad_path", "bad_path")
    # Preprocess raises Exception
    detector.preprocess_text = MagicMock(side_effect=Exception("Preprocess Error"))
    
    # Expect graceful failure (ERROR) instead of raise, as per updated logic
    label, prob = detector.predict("test")
    assert label == "ERROR"
    assert prob == 0.0

def test_preprocess_text_error_in_detector():
     detector = FakeNewsDetector("p", "t")
     detector.tokenizer = None
     with pytest.raises(ValueError):
         detector.preprocess_text("test")

@patch("app.services.prediction.logger")
def test_load_tokenizer_error(mock_logger):
    with patch("os.path.exists", return_value=True):
         with patch("builtins.open", side_effect=Exception("File error")):
             detector = FakeNewsDetector("p", "t")
             assert detector.tokenizer is None
             mock_logger.error.assert_called()

def test_singleton_init():
    with patch("os.path.exists", return_value=False):
        importlib.reload(app.services.prediction)
        assert app.services.prediction.detector is not None

@patch("app.services.prediction.tf.device")
def test_detector_predict_cpu_device(mock_tf_device):
    detector = FakeNewsDetector("dummy", "dummy")
    detector.model = MagicMock()
    detector.model.predict.return_value = np.array([[0.9]])
    detector.tokenizer = MagicMock()
    detector.preprocess_text = MagicMock(return_value=np.zeros((1, 100)))

    mock_tf_device.return_value.__enter__.return_value = None 
    
    label, prob = detector.predict("test")
    
    mock_tf_device.assert_called_with('/cpu:0')
    assert label == "REAL"
    assert prob == 0.9

@patch("app.services.prediction.pad_sequences")
def test_preprocess_text_success(mock_pad_sequences):
    detector = FakeNewsDetector("p", "t")
    detector.tokenizer = MagicMock()
    detector.tokenizer.texts_to_sequences.return_value = [[1, 2, 3]]
    mock_pad_sequences.return_value = np.array([[1, 2, 3]])
    
    # Patch the function where it is imported/used
    # Since prediction.py does: 'from app.services.preprocessing import preprocess_text as clean_text_func'
    # We must patch 'app.services.prediction.clean_text_func' ? 
    # BUT that import happens INSIDE preprocess_text method.
    # So we MUST patch 'app.services.preprocessing.preprocess_text' because 'from ... import ...' inside a function 
    # looks up the module again.
    
    with patch("app.services.preprocessing.preprocess_text", return_value="cleaned"):
       res = detector.preprocess_text("raw text")
       assert res is not None
       detector.tokenizer.texts_to_sequences.assert_called_with(["cleaned"])




# --- Model Services Tests ---
def test_tokenize_and_pad():
    texts = ["hello world"]
    tokenizer, padded = tokenize_and_pad(texts, vocab_size=100)
    assert padded.shape == (1, 100)

def test_request_tokenization_error():
    with pytest.raises(Exception):
         tokenize_and_pad(None)

def test_prepare_data():
    df = pd.DataFrame({'clean_text': ['text1', 'text2'], 'target': [1, 0]})
    X_train, X_test, y_train, y_test, tokenizer = prepare_data(df, test_size=0.5)
    assert len(X_train) == 1

def test_prepare_data_error_no_col():
    df = pd.DataFrame({'wrong_col': []})
    with pytest.raises(Exception):
        prepare_data(df)

def test_build_model():
    model = build_lstm_gru_model(vocab_size=100)
    assert model is not None

@patch("app.services.model.Sequential")
def test_build_model_error(mock_sequential):
    mock_sequential.side_effect = Exception("Build error")
    with pytest.raises(Exception):
        build_lstm_gru_model(100)

@patch("app.services.model.os.makedirs")
@patch("app.services.model.tf.keras.models.Sequential.fit")
def test_train_model(mock_fit, mock_makedirs):
    model = MagicMock()
    model.fit.return_value = "history"
    X = np.random.rand(10, 10)
    y = np.random.randint(0, 2, 10)
    result_model, history = train_model(model, X, y, X, y, epochs=1)
    assert result_model == model

def test_train_model_error():
    with pytest.raises(Exception):
        train_model(None, None, None, None, None)

@patch("app.services.model.os.makedirs")
def test_save_model(mock_makedirs):
    model = MagicMock()
    save_model(model, "model_path.h5")
    model.save.assert_called_with("model_path.h5")

def test_save_model_error():
    with pytest.raises(Exception):
        save_model(None, None)

@patch("app.services.model.os.makedirs")
def test_save_model_with_tokenizer(mock_makedirs):
    model = MagicMock()
    tokenizer = MagicMock()
    
    with patch("builtins.open", new_callable=mock_open) as mock_file:
        with patch("pickle.dump") as mock_dump:
            save_model(model, "model.h5", tokenizer, "tok.pickle")
            
            model.save.assert_called_with("model.h5")
            mock_dump.assert_called()
            # Verify open called for tokenizer
            mock_file.assert_called_with("tok.pickle", "wb")

# --- Additional Coverage Tests ---
@patch("app.services.prediction.logger")
@patch("app.services.prediction.load_model")
def test_detector_init_load_error(mock_load_model, mock_logger):
    with patch("os.path.exists", return_value=True):
        mock_load_model.side_effect = Exception("Load failed")
        detector = FakeNewsDetector("model", "tok")
        # Just creating it triggers the load.
        # Check logs
        assert mock_logger.error.called
        assert detector.model is None

@patch("app.services.prediction.logger")
@patch("app.services.prediction.load_model")
def test_detector_init_tokenizer_error(mock_load_model, mock_logger):
    with patch("os.path.exists", return_value=True):
        # We need to ensure we don't open the file if we want to test pickle error only,
        # OR we let open succeed and pickle fail.
        # But wait, to test pickle load error, open MUST succeed.
        with patch("builtins.open", mock_open(read_data=b"data")):
             with patch("io.open", mock_open(read_data=b"data")):
                with patch("app.services.prediction.pickle.load", side_effect=Exception("Pickle error")):
                    detector = FakeNewsDetector("model", "tok")
                    # The error message in _load_tokenizer is "Error loading tokenizer: Pickle error"
                    mock_logger.error.assert_called()
                    assert detector.tokenizer is None

@patch("app.services.preprocessing.re.sub")
@patch("app.services.preprocessing.logger")
def test_preprocess_text_generic_error(mock_logger, mock_re_sub):
    mock_re_sub.side_effect = Exception("Regex failed")
    assert preprocess_text("test") == ""
    mock_logger.error.assert_called()

@patch("app.services.prediction.logger")
def test_detector_predict_generic_error(mock_logger):
    detector = FakeNewsDetector("bad_path", "bad_path")
    # predict(None) will crash at logger line 'text[:50]' with TypeError
    label, prob = detector.predict(None)
    assert label == "ERROR"
    assert prob == 0.0
    mock_logger.error.assert_called()
