# Use the official uv + Python image
FROM ghcr.io/astral-sh/uv:python3.11-bookworm

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies using uv
RUN uv sync --frozen

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app using uv
CMD ["uv", "run", "run_fastapi.py"]
