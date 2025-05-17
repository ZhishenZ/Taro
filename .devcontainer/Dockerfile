FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install yfinance

WORKDIR /workspaces/Taro

# Setup git editor
RUN if [[ "$PATH" == *"cursor-server"* ]]; then \
        git config --global core.editor "cursor --wait"; \
    else \
        git config --global core.editor "code --wait"; \
    fi
    