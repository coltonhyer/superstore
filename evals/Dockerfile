FROM node:22-bookworm-slim@sha256:83f487e0a63425e5b4d146fb5e5be574bcbe1b7b843d3ebafdd95eaf7767a7e5

ARG TARGETARCH
ARG CODEX_VERSION=0.155.0
ARG CLAUDE_VERSION=2.1.251
ARG AGY_VERSION=1.4.0
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
            agy_url="https://storage.googleapis.com/antigravity-public/antigravity-cli/${AGY_VERSION}-5281842794987520/linux-x64/cli_linux_x64.tar.gz"; \
            agy_sha="6c4b298c2a69b6bd0f58567031cc56d8097a32be54c4b633aa80ad395871b389618ab3860d4ba0a12599831b8226b51b03e258ee2ec7fae105a45b8e0fce2188"; \
            jj_target="x86_64-unknown-linux-musl"; \
            jj_sha="0a07bab4641a55fd2bc2fd1563ba3a3f9a577584086ad74086a1c5b69b3ffce9" \
            ;; \
        arm64) \
            agy_url="https://storage.googleapis.com/antigravity-public/antigravity-cli/${AGY_VERSION}-5281842794987520/linux-arm/cli_linux_arm64.tar.gz"; \
            agy_sha="64dfb2a9665ebd19b6e9d687c094673b61ca9f5ffdebc81391cea8e3858773e1c88154f088e8a8691208561d946a7aea9acbec7a3bdca9e5d8a48fa197b0a308"; \
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
