# Step 1: Use the official Python image from Docker Hub as the base image
FROM python:3.9-slim

# Step 2: Install necessary system dependencies
RUN apt-get update && apt-get install -y curl

# Step 3: Install Ollama using the official install script
RUN curl -fsSL https://ollama.com/install.sh | sh

# Step 4: Set the working directory inside the container
WORKDIR /app

# Step 5: Copy the requirements.txt into the container
COPY requirements.txt .

# Step 6: Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Step 7: Copy the rest of your app into the container
COPY . .

# Step 8: Expose the port the app will run on (default FastAPI is 8000)
EXPOSE 8000

# Step 9: Command to run the app using Gunicorn (production-ready server)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]