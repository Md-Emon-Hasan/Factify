import React from 'react';

const Header = () => {
    return (
        <header className="text-center mb-12">
            <div className="flex justify-center items-center gap-3 mb-2">
                <ion-icon name="shield-checkmark" class="text-5xl text-indigo-600"></ion-icon>
                <div className="text-slate-800">
                    <h1 className="text-4xl font-extrabold tracking-tight leading-none">Factify</h1>
                </div>
            </div>
            <div className="w-full mb-4">
                <p className="text-lg font-bold text-white drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)] bg-black/20 inline-block px-4 py-1 rounded-full backdrop-blur-sm">
                    Next-Gen News Authenticity Verification
                </p>
            </div>
            <div className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-900 shadow-sm">
                <ion-icon name="hardware-chip-outline" class="text-indigo-600"></ion-icon>
                Powered by Hybrid LSTM-GRU Deep Learning Architecture
            </div>
        </header>
    );
};

export default Header;
