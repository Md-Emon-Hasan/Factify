from setuptools import setup, find_packages

setup(
    name="Factify",               
    version="0.1.0",                            
    author="Md Emon Hasan",                     
    author_email="iconicemon01@gmail.com",     
    description="A fake news detection package using NLP and deep learning",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Md-Emon-Hasan/Factify",
    packages=find_packages(include=["src", "src.*"]),  
    python_requires=">=3.9",                  
    install_requires=[                          
        "pandas",
        "numpy",
        "Pillow",
        "nltk",
        "gensim",
        "scikit-learn",
        "tensorflow",      
        "Flask",
        "gunicorn",
    ],
    extras_require={                        
        "dev": [
            "pytest",
        ],
    },
    entry_points={                              
        "console_scripts": [
            "run-fake-news=src.main:main",      
        ],
    },
    classifiers=[                              
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
