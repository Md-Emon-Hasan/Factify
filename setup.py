from setuptools import setup, find_packages

setup(
    name="factify",
    version="1.0.0",
    description="A monolithic AI-powered Fact Checking application",
    author="Md Emon Hasan",
    packages=find_packages(where=".", include=["app*"]),
    python_requires=">=3.10",
    install_requires=[
        "fastapi==0.109.2",
        "uvicorn==0.27.1",
        "jinja2==3.1.3",
        "python-multipart==0.0.9",
        "email-validator==2.1.0.post1",
        "pydantic==2.6.1",
        "pydantic-settings==2.1.0",
        "pandas==2.2.0",
        "numpy==1.26.4",
        "pillow==10.2.0",
        "nltk==3.8.1",
        "gensim==4.3.2",
        "scikit-learn==1.4.0",
        "tensorflow-cpu==2.15.0",
        "httpx==0.26.0",
        "pyyaml==6.0.1",
        "aiofiles==23.2.1",
    ],
    extras_require={
        "test": [
            "pytest==8.0.0",
            "pytest-cov==4.1.0",
        ],
    },
)
