# Saheeli

Saheeli orchestrates Docker-based Servo agents to execute complex tasks. This repository contains the host controller and the Servo worker implementation.

## Docker Compose v2

Saheeli can run inside a container using **docker compose v2**. The compose
configuration mounts the repository and the Docker socket so the orchestrator can
launch Servo containers on the host.

1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
2. Build the image:

```bash
docker compose build
```

3. Run the CLI:

```bash
docker compose run --rm saheeli --help
```

Tasks can then be submitted from within the container:

```bash
docker compose run --rm saheeli task submit --prompt /app/prompts/validation_task.md
```

Result artifacts are written to `results/` on the host.
