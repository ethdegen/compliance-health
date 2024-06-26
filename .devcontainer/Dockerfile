ARG POSTGRES_VERSION=16

FROM postgres:${POSTGRES_VERSION}-bookworm

ARG PYTHON_VERSION=3.11.9
ARG NODEJS_VERSION=20.x

USER root

WORKDIR /tmp

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt update && apt install -y apt build-essential curl gdb git libncursesw5-dev libssl-dev libsqlite3-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev postgresql-server-dev-all procps software-properties-common tk-dev zlib1g-dev


# Install PGvector

RUN git clone https://github.com/pgvector/pgvector.git && cd pgvector && make && make install

# Install Docker

RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
RUN apt update && apt install -y docker-ce-cli

# Install Python

RUN curl -fsSL https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz | tar -zx -C ~/
RUN cd ~/Python-${PYTHON_VERSION} && ./configure --with-pydebug && make -s -j$(nproc) && make install && update-alternatives --install /usr/bin/python python /usr/local/bin/python3 0 && update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3 0
RUN pip install --no-cache-dir --upgrade debugpy pip poetry && poetry config virtualenvs.create false

# Install NodeJS

RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODEJS_VERSION} nodistro main" > /etc/apt/sources.list.d/nodesource.list
RUN apt update && apt install -y nodejs
RUN npm install -g npm prettier eslint
