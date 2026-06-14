# ---- Stage 1: Build WeeChat from source ----
ARG BUILD_FROM
FROM ${BUILD_FROM} AS build

SHELL ["/bin/ash", "-eo", "pipefail", "-c"]

# Pin version in one place
ARG WEECHAT_VERSION=v4.9.2
ENV WEECHAT_REPO=https://github.com/weechat/weechat.git

# Install ONLY build dependencies (runtime deps go in final stage)
RUN apk add --no-cache \
        git \
        cmake \
        build-base \
        autoconf \
        automake \
        libtool \
        pkgconfig \
        ncurses-dev \
        python3-dev \
        perl-dev \
        ruby-dev \
        libgcrypt-dev \
        lua5.4-dev \
        gnutls-dev \
        zlib-dev \
        zstd-dev \
        xz-dev \
        cjson-dev \
        curl-dev \
        aspell-dev \
        gettext-dev

# Clone WeeChat source
RUN git clone --branch "$WEECHAT_VERSION" --depth 1 "$WEECHAT_REPO" /src

WORKDIR /src/build

# Configure and build WeeChat
RUN cmake .. \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DCMAKE_BUILD_TYPE=Release \
        -DENABLE_HEADLESS=ON \
        -DENABLE_NCURSES=ON \
        -DENABLE_PYTHON=ON \
        -DENABLE_PERL=ON \
        -DENABLE_RUBY=ON \
        -DENABLE_LUA=ON \
        -DENABLE_SPELL=ON \
        -DENABLE_XFER=ON \
        -DENABLE_RELAY=ON \
        -DENABLE_DOC=OFF \
        -DENABLE_GUILE=OFF \
        -DENABLE_JAVASCRIPT=OFF \
        -DENABLE_TCL=OFF \
        -DENABLE_QT=OFF \
        -DENABLE_NLS=ON \
        -DENABLE_PHP=OFF \
    && make -j"$(nproc)" \
    && make install

# ---- Stage 2: Runtime ----
FROM ${BUILD_FROM}

SHELL ["/bin/ash", "-eo", "pipefail", "-c"]

# Metadata and environment
LABEL maintainer="stulleamgym@gmx.net"
ENV LANG="C.UTF-8"
ENV TERM="xterm-256color"

# Install ONLY runtime dependencies
RUN apk add --no-cache \
    ca-certificates \
    tzdata \
    bash \
    net-tools \
    ncurses-libs \
    ncurses-terminfo \
    python3 \
    perl \
    ruby \
    lua5.4 \
    zlib \
    zstd-libs \
    xz-libs \
    cjson \
    curl \
    libcurl \
    aspell \
    aspell-en \
    libintl \
    libgcrypt \
    gnutls \
    gettext

# Copy compiled WeeChat from build stage
COPY --from=build /usr/local /usr/local

ENV PATH="/usr/local/bin:${PATH}"

# Verify WeeChat installation
RUN weechat-headless --version

# Add scripts
COPY run.sh /run.sh
RUN chmod +x /run.sh

COPY weechat_monitor.py /app/weechat_monitor.py
RUN chmod 644 /app/weechat_monitor.py

CMD ["/run.sh"]