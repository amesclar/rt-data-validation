# Use the newer, lightweight official Python image
FROM python:3.11-slim

# Create a non-root user to run the application for security.
# 'useradd -m' creates a home directory specifically for this user.
RUN useradd -m -s /bin/bash cfa

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt FIRST. This allows Docker to cache the dependency layer
# so pip install only re-runs if requirements.txt changes.
COPY requirements.txt .

# Install dependencies.
# We install as root *before* switching users so packages go into system-wide paths easily.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Application Setup ---
# Copy the rest of the application code into the container.
# IMPORTANT: We use '--chown=cfa:cfa' to ensure the non-root user created above
# has ownership permissions over the application files.
COPY --chown=cfa:cfa . .

# Switch to the non-root user defined earlier so the app doesn't run as root.
USER cfa
