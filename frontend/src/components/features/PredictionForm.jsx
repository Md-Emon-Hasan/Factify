import React, { useState } from 'react';
import { predictNews } from '../../services/api';

const MIN_INPUT_LENGTH = 50;
const MIN_WORD_COUNT = 10;

const getInputValidationMessage = (value) => {
    const trimmed = value.trim();

    if (!trimmed) {
        return 'Please paste or type some text before analyzing it.';
    }

    if (trimmed.length < MIN_INPUT_LENGTH) {
        return `Your text is too short. Please provide at least ${MIN_INPUT_LENGTH} characters so the analysis is meaningful.`;
    }

    if (trimmed.split(/\s+/).length < MIN_WORD_COUNT) {
        return `Please provide at least ${MIN_WORD_COUNT} words so the analysis can work properly.`;
    }

    return null;
};

const getApiErrorMessage = (err) => {
    const detail = err?.response?.data?.detail;

    if (typeof detail === 'string' && detail.trim()) {
        return detail;
    }

    const errors = err?.response?.data?.errors;
    if (Array.isArray(errors) && errors.length > 0) {
        const firstMessage = errors[0]?.msg;
        if (typeof firstMessage === 'string' && firstMessage.trim()) {
            return firstMessage;
        }
    }

    if (err?.response?.status === 422) {
        return 'The text does not meet the validation rules. Please use a longer, readable news paragraph.';
    }

    return 'Analysis failed. Please check the backend connection and try again.';
};

const PredictionForm = () => {
    const [text, setText] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleClear = () => {
        setText('');
        setResult(null);
        setError(null);
    };

    const handleVerify = async () => {
        const validationMessage = getInputValidationMessage(text);
        if (validationMessage) {
            setResult(null);
            setError(validationMessage);
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const data = await predictNews(text);
            setResult(data);
        } catch (err) {
            console.error(err);
            setError(getApiErrorMessage(err));
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="flex-1 w-full">
            <div className="glass-panel p-8 rounded-2xl transition-transform duration-200">
                <div className="flex justify-between items-center mb-4 text-gray-500 font-medium">
                    <h2 className="text-lg flex items-center gap-2">
                        <ion-icon name="newspaper-outline"></ion-icon> Analyze Content
                    </h2>
                    <span className="text-sm">{text.length} / 5000</span>
                </div>

                <textarea
                    id="newsText"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Paste the full text of the news article here to analyze its linguistic patterns..."
                    spellCheck="false"
                    className="w-full h-[200px] p-4 border-2 border-gray-200 rounded-xl font-inherit text-base bg-gray-50 resize-y transition-all duration-200 focus:outline-none focus:bg-white focus:border-indigo-600 focus:ring-4 focus:ring-indigo-100"
                ></textarea>

                <div className="mt-3 flex items-center justify-between gap-4 text-sm text-gray-500">
                    <p>
                        Paste at least {MIN_INPUT_LENGTH} characters and {MIN_WORD_COUNT} words for a reliable result.
                    </p>
                    <p className="whitespace-nowrap">
                        {text.trim().length} / 5000
                    </p>
                </div>

                <div className="flex justify-end gap-4 mt-6">
                    <button
                        onClick={handleClear}
                        className="btn btn-ghost text-gray-500 hover:bg-red-50 hover:text-red-600 normal-case font-semibold text-[0.95rem]"
                        title="Clear Text"
                    >
                        <ion-icon name="trash-outline"></ion-icon> Clear
                    </button>
                    <button
                        onClick={handleVerify}
                        disabled={loading || !text}
                        className="btn bg-indigo-600 hover:bg-indigo-700 text-white border-none shadow-md hover:shadow-lg hover:-translate-y-[1px] normal-case font-semibold text-[0.95rem] px-6"
                    >
                        {loading ? (
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        ) : (
                            <span className="flex items-center gap-2">
                                <ion-icon name="scan-circle-outline"></ion-icon> Verify Authenticity
                            </span>
                        )}
                    </button>
                </div>
            </div>

            {/* Result Display */}
            {result && (
                <div className={`mt-8 bg-white/80 border border-white/50 backdrop-blur-md rounded-xl shadow-lg overflow-hidden animate-[slideUp_0.4s_ease-out] ${result.label === 'REAL' ? 'border-t-[6px] border-t-emerald-600' : 'border-t-[6px] border-t-red-600'}`}>
                    <div className="p-8 text-center">
                        <div className={`text-5xl mb-2 ${result.label === 'REAL' ? 'text-emerald-600' : 'text-red-600'}`}>
                            <ion-icon name={result.label === 'REAL' ? "check-circle" : "alert-circle"}></ion-icon>
                        </div>

                        <div className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-4 ${result.label === 'REAL' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                            {result.label === 'REAL' ? "Authentic Source Verified" : "Likely Misinformation Detected"}
                        </div>

                        <div className="bg-gray-100 h-2 rounded-full mt-6 mx-auto max-w-[300px] overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all duration-1000 ease-out ${result.label === 'REAL' ? 'bg-emerald-600' : 'bg-red-600'}`}
                                style={{ width: `${result.probability * 100}%` }}
                            ></div>
                        </div>
                    </div>
                </div>
            )}

            {error && (
                <div className="mt-8 p-4 bg-red-100 text-red-700 border border-red-200 rounded-xl text-center">
                    {error}
                </div>
            )}
        </main>
    );
};

export default PredictionForm;
