# Dockerfile — OpenClaw Specialist Agent
FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    openssh-client \
    ca-certificates \
    python3 \
    python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

# Force git to use HTTPS instead of SSH
RUN git config --global url."https://github.com/".insteadOf ssh://git@github.com/

# Install OpenClaw globally
RUN npm install -g openclaw@latest

# Set working directory
WORKDIR /app

# Copy the configuration file
COPY openclaw.json /root/.openclaw/openclaw.json

# Expose the gateway port (from clawdbot.json)
EXPOSE 18789

# Start OpenClaw Gateway
CMD ["openclaw", "gateway", "run", "--allow-unconfigured", "--verbose"]
