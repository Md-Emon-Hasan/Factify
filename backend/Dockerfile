# Use Python 3.9 as base image
FROM python:3.9

# Set working directory
WORKDIR /code

# Copy requirements first to leverage Docker cache
COPY ./requirements.txt /code/requirements.txt

# Install dependencies (no cache dir to keep image small)
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code
COPY ./app /code/app
COPY ./models /code/models
COPY ./logs /code/logs
COPY ./tests /code/tests
COPY ./pytest.ini /code/pytest.ini
COPY ./run.py /code/run.py

# Create a non-root user (good practice and required by some platforms)
RUN useradd -m -u 1000 user

# Change ownership of the working directory to the non-root user
RUN chown -R user:user /code

# Switch to the non-root user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Expose the port (FastAPI default is 8000, but HF Spaces expects 7860 usually, 
# but we can configure it. Let's stick to 7860 as standard for HF)
EXPOSE 7860

# Command to run the application using uvicorn
# Note: Changing port to 7860 for Hugging Face Spaces compatibility
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]