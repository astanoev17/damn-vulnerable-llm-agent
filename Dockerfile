# Stage 1: build dependencies into a venv
FROM python:3.9-slim AS build

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
  && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .


# Stage 2: runtime image
FROM python:3.9-slim

WORKDIR /usr/src/app

# optional runtime libs, keep minimal
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/venv /opt/venv
COPY --from=build /usr/src/app /usr/src/app

ENV PATH="/opt/venv/bin:$PATH"

# Copy start.sh into a writable location and set perms BEFORE dropping privileges
COPY start.sh /usr/local/bin/start.sh
RUN chmod 755 /usr/local/bin/start.sh

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /usr/src/app
USER appuser

# Your two ports (Streamlit UI + API)
EXPOSE 8501
EXPOSE 8080

# Single CMD only
CMD ["/usr/local/bin/start.sh"]
