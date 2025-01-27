# Use an official lightweight Python image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --upgrade redis
RUN pip3 install --upgrade pandas numpy

# Copy the application code
COPY . .

# Expose the Streamlit default port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
