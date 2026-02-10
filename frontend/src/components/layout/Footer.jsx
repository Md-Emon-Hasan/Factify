import React from 'react';

const Footer = () => {
    return (
        <footer className="mt-16 pt-8 border-t border-gray-200 text-center">
            <div className="glass-panel p-8 rounded-2xl text-center text-gray-500 text-sm">
                <div className="mb-2">
                    <div className="mb-4">
                        <div className="text-gray-900">
                            <h4 className="font-bold text-lg">Md Emon Hasan</h4>
                            <span className="text-xs opacity-80">Machine Learning Engineer</span>
                        </div>
                    </div>

                    <div className="flex flex-wrap justify-center gap-6 mt-6">
                        <a href="mailto:emon.mlengineer@gmail.com" className="contact-item flex items-center justify-center w-[60px] h-[60px] bg-white border border-gray-200 rounded-full text-slate-700 text-2xl transition-all duration-300 shadow-sm hover:border-indigo-600 hover:text-indigo-600 hover:-translate-y-1 hover:scale-110 hover:shadow-lg hover:shadow-indigo-500/30 hover:bg-slate-50" title="Email">
                            <ion-icon name="mail-outline"></ion-icon>
                        </a>
                        <a href="https://wa.me/8801834363533" target="_blank" rel="noreferrer" className="contact-item flex items-center justify-center w-[60px] h-[60px] bg-white border border-gray-200 rounded-full text-slate-700 text-2xl transition-all duration-300 shadow-sm hover:border-indigo-600 hover:text-indigo-600 hover:-translate-y-1 hover:scale-110 hover:shadow-lg hover:shadow-indigo-500/30 hover:bg-slate-50" title="WhatsApp">
                            <ion-icon name="logo-whatsapp"></ion-icon>
                        </a>
                        <a href="https://github.com/Md-Emon-Hasan" target="_blank" rel="noreferrer" className="contact-item flex items-center justify-center w-[60px] h-[60px] bg-white border border-gray-200 rounded-full text-slate-700 text-2xl transition-all duration-300 shadow-sm hover:border-indigo-600 hover:text-indigo-600 hover:-translate-y-1 hover:scale-110 hover:shadow-lg hover:shadow-indigo-500/30 hover:bg-slate-50" title="GitHub">
                            <ion-icon name="logo-github"></ion-icon>
                        </a>
                        <a href="https://www.linkedin.com/in/md-emon-hasan-695483237/" target="_blank" rel="noreferrer" className="contact-item flex items-center justify-center w-[60px] h-[60px] bg-white border border-gray-200 rounded-full text-slate-700 text-2xl transition-all duration-300 shadow-sm hover:border-indigo-600 hover:text-indigo-600 hover:-translate-y-1 hover:scale-110 hover:shadow-lg hover:shadow-indigo-500/30 hover:bg-slate-50" title="LinkedIn">
                            <ion-icon name="logo-linkedin"></ion-icon>
                        </a>
                        <a href="https://www.facebook.com/mdemon.hasan2001/" target="_blank" rel="noreferrer" className="contact-item flex items-center justify-center w-[60px] h-[60px] bg-white border border-gray-200 rounded-full text-slate-700 text-2xl transition-all duration-300 shadow-sm hover:border-indigo-600 hover:text-indigo-600 hover:-translate-y-1 hover:scale-110 hover:shadow-lg hover:shadow-indigo-500/30 hover:bg-slate-50" title="Facebook">
                            <ion-icon name="logo-facebook"></ion-icon>
                        </a>
                    </div>
                </div>

                <div className="mt-6 opacity-70">
                    <p>&copy; 2026 Factify AI. Engineered for Truth.</p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
