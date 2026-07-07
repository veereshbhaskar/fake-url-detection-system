FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download required NLTK/Spacy data if needed, or simply run app
COPY . .

# Expose port (Hugging Face standard is 7860, Heroku/Render use the PORT env var)
# We will launch via gunicorn on port 7860 to match typical container environments
EXPOSE 7860

CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]
