# Base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /food_waste_management

RUN apt-get update && apt-get install -y gcc libpq-dev

COPY requirements.txt /food_waste_management/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /food_waste_management/

EXPOSE 8000


CMD ["./entrypoints.sh"]