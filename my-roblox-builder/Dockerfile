FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Cài đặt Wine và Python
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y wine32 wine64 python3 python3-pip wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install pyinstaller

COPY . .

EXPOSE 10000

CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
