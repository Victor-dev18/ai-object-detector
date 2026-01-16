# Use a lightweight Python version
FROM python:3.9-slim

# Set up the working directory inside the container
WORKDIR /app

# Copy the requirements file first (to cache dependencies)
COPY requirements.txt .

# Install the libraries (Streamlit, Transformers, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Tell Docker to listen on port 7860 (Hugging Face's default)
EXPOSE 7860

# The command to start the app
CMD ["streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
