import React from 'react';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import PredictionForm from '../components/features/PredictionForm';

const Home = () => {
    return (
        <div className="app-wrapper max-w-[900px] mx-auto py-8 px-4 flex flex-col min-h-screen relative z-10">
            <Header />
            <PredictionForm />
            <Footer />
        </div>
    );
};

export default Home;
