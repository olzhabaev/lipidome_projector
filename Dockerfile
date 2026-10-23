# Define the build stage.
FROM python:3.12-slim AS builder

# Set the working directory for the build stage.
WORKDIR /build

# Set up the Python virtual environment.
ENV VIRTUAL_ENV=/env
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
RUN python -m venv "${VIRTUAL_ENV}"

# Copy the project file.
COPY pyproject.toml README.md ./

# Install the project dependencies.
RUN python - <<'PY'
import subprocess
import tomllib
with open("pyproject.toml", "rb") as pyproject_file:
    dependencies = tomllib.load(pyproject_file)["project"]["dependencies"]
subprocess.check_call(
    ["pip", "install", "--no-cache-dir", "--only-binary=:all:", *dependencies]
)
PY

# Copy the source code and install the project.
COPY src ./src
RUN pip install --no-cache-dir --no-deps .


# Define the runtime stage.
FROM python:3.12-slim AS runtime

# Install required system dependencies.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libexpat1 \
        libsm6 \
        libxext6 \
        libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Set up the Python virtual environment.
ENV VIRTUAL_ENV=/env
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Copy the project.
COPY --from=builder /env /env

# Create the application user and group.
RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app --create-home app

# Switch to the application user and set the working directory.
USER app
WORKDIR /app

# Expose the application port.
EXPOSE 8050

# Run the application.
CMD ["gunicorn", \
     "--bind=0.0.0.0:8050", \
     "--workers=1", \
     "--threads=16", \
     "--keep-alive=30", \
     "--timeout=120", \
     "--preload", \
     "--access-logfile=-", \
     "lipidome_projector.main:server"]