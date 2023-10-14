FROM python:3.9

# Create a non-root user with specific user ID and group ID
RUN groupadd -g 1001 appgroup && useradd -r -u 1001 -g appgroup -d /home/appuser -s /bin/bash appuser

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN mkdir -p /app && \
  chown -R appuser:appgroup /app

USER appuser

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY main.py /app

EXPOSE 7860

CMD ["python", "main.py"]
