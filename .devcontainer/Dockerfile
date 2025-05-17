FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git curl build-essential coreutils tree nano\
    && rm -rf /var/lib/apt/lists/* \
    && pip install yfinance

WORKDIR /workspaces/Taro

# Setup git editor
RUN if [[ "$PATH" == *"cursor-server"* ]]; then \
        git config --global core.editor "cursor --wait"; \
    else \
        git config --global core.editor "code --wait"; \
    fi

# Enable color output for common terminal commands
RUN echo 'eval "$(dircolors -b)"' >> /root/.bashrc && \
    echo 'alias ls="ls --color=auto"' >> /root/.bashrc && \
    echo 'alias grep="grep --color=auto"' >> /root/.bashrc && \
    echo 'alias fgrep="fgrep --color=auto"' >> /root/.bashrc && \
    echo 'alias egrep="egrep --color=auto"' >> /root/.bashrc
    