FROM node:22-bookworm-slim@sha256:83f487e0a63425e5b4d146fb5e5be574bcbe1b7b843d3ebafdd95eaf7767a7e5

ARG TARGETARCH
ARG CODEX_VERSION=0.150.1
ARG CLAUDE_VERSION=2.1.251
ARG AGY_VERSION=1.1.22
ARG JJ_VERSION=0.44.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        git \
        python3 \
        ripgrep \
    && rm -rf /var/lib/apt/lists/*

RUN npm install --global \
        "@openai/codex@${CODEX_VERSION}" \
        "@anthropic-ai/claude-code@${CLAUDE_VERSION}" \
    && npm cache clean --force

RUN set -eu; \
    case "${TARGETARCH}" in \
        amd64) \
            agy_url="https://storage.googleapis.com/antigravity-public/antigravity-cli/${AGY_VERSION}-5711547746615296/linux-x64/cli_linux_x64.tar.gz"; \
            agy_sha="40225d4b1f009412e905f0a234ba3d51487038d1ad1b8fa19331c84be55610a01f5b0ad9916fb871151cc45456c6bc30cc0b1ea5dab6c0616bc8fb262bcdd7a9"; \
            jj_target="x86_64-unknown-linux-musl"; \
            jj_sha="0a07bab4641a55fd2bc2fd1563ba3a3f9a577584086ad74086a1c5b69b3ffce9" \
            ;; \
        arm64) \
            agy_url="https://storage.googleapis.com/antigravity-public/antigravity-cli/${AGY_VERSION}-5711547746615296/linux-arm/cli_linux_arm64.tar.gz"; \
            agy_sha="b37a718330eb5e270e1ca70135bf964a407ba626fbff7537ac58e094ea31bc623e6d216ef197188fe8b5c46e6f57aee64a3b7c9e23fc855cefee43fe434179d3"; \
            jj_target="aarch64-unknown-linux-musl"; \
            jj_sha="60d42fa2a9abaa445eff10cd2087458562aaad5a54b90309e5a3787ecc985ff2" \
            ;; \
        *) echo "unsupported architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl -fsSL "${agy_url}" -o /tmp/agy.tar.gz; \
    echo "${agy_sha}  /tmp/agy.tar.gz" | sha512sum --check --strict; \
    tar -xzf /tmp/agy.tar.gz -C /tmp antigravity; \
    install -m 0755 /tmp/antigravity /usr/local/bin/agy; \
    jj_archive="jj-v${JJ_VERSION}-${jj_target}.tar.gz"; \
    curl -fsSL \
        "https://github.com/jj-vcs/jj/releases/download/v${JJ_VERSION}/${jj_archive}" \
        -o "/tmp/${jj_archive}"; \
    echo "${jj_sha}  /tmp/${jj_archive}" | sha256sum --check --strict; \
    mkdir /tmp/jj-release; \
    tar -xzf "/tmp/${jj_archive}" -C /tmp/jj-release; \
    install -m 0755 /tmp/jj-release/jj /usr/local/bin/jj; \
    rm -rf /tmp/agy.tar.gz /tmp/antigravity "/tmp/${jj_archive}" /tmp/jj-release

ENV HOME=/state \
    DISABLE_AUTOUPDATER=1

WORKDIR /workspace

CMD ["bash"]
