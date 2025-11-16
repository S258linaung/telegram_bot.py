# 1️⃣ Base image
FROM python:3.13-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4️⃣ Copy all project files
COPY . .

# 5️⃣ Expose port for Koyeb
ENV PORT 5000
EXPOSE $PORT

# 6️⃣ Start bot
CMD ["python", "bot.py"]
