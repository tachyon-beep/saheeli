# Saheeli

A host-based orchestration system using Docker-based agents for complex or high risk tasks.

## **1. High-Level Architecture: The Foreman & Worker Model**

The system is composed of two primary, decoupled components:

* **The "Saheeli" Backbone (The Foreman):** A trusted, persistent application running on the host machine. Its role is to manage the overall workflow, tasks, and resources. It does not perform the "dangerous" work itself.
* **The "Servo" Agents (The Workers):** Single-use, disposable agents that are spawned by Saheeli inside new Docker containers. Each Servo is responsible for executing one specific task from start to finish and then terminating.

---

## **2. The "Saheeli" Backbone: Host System Requirements**

**2.1. Task & Lifecycle Management**
* **Task Queuing:** Must manage a queue of tasks submitted by the user. Each task is defined by a prompt file and a set of goals.
* **Servo Spawning:** Must be able to build a Servo Docker image and spawn new, isolated containers for each task.
* **Resource Allocation:** Must assign specific CPU and memory limits to each Servo container upon creation.
* **Monitoring & Termination:** Must monitor the health of active Servos (e.g., via a heartbeat file) and have a timeout mechanism to automatically terminate stalled or long-running Servos.

**2.2. Results & Data Handling**
* **Artifact Collection:** When a Servo terminates, Saheeli must automatically copy the entire contents of the Servo's `/workspace` (code, logs, results) to a local directory on the host for archival and analysis.
* **Results Synthesis:** Must include a module to parse the results from multiple parallel Servo runs (e.g., a hyperparameter sweep) and generate a single summary report identifying the best performer based on task-specific metrics.

**2.3. User Interface (CLI)**
* Must provide a clear CLI for the user to manage the system:
    * `saheeli task submit --prompt <path_to_prompt.md>`
    * `saheeli task list`
    * `saheeli servo status <servo_id>`
    * `saheeli servo terminate <servo_id>`
    * `saheeli results get <task_id>`

---

### **3. The "Servo" Agent: Dockerized Worker Requirements**

**3.1. Core Agentic Loop**
* **Orchestrator Logic:** Each Servo contains the core agentic loop: it reads the task prompt, forms a master prompt including its history and environment state, communicates with an LLM API (e.g., Gemini or OpenAI-compatible), parses the response, and executes the requested command.
* **LLM Interface:** Must have a modular interface for communicating with the LLM, configured via environment variables passed by Saheeli.

**3.2. State and Workspace**
* **Workspace Confinement:** All file operations must be strictly confined to a `/workspace` directory inside the container.
* **Session Persistence:** The Servo should periodically save its state (conversation history, etc.) to a `session.json` within its workspace. This allows Saheeli to recover and analyze the state of a failed or terminated Servo.
* **Task Completion:** The Servo must recognize a `{"tool": "task_complete", ...}` command from the LLM, at which point it will write its final results, clean up, and terminate itself.

**3.3. Tooling & Execution**
* **Structured Tool Use:** Must be designed to parse structured JSON commands from the LLM, supporting a range of tools beyond simple shell execution:
    * `execute_shell`
    * `create_file`
    * `read_file`
    * `edit_file`
    * `list_files`
* **Error Handling:** The `stderr` and non-zero exit codes from any failed command must be captured and sent back to the LLM in the next turn, making the LLM responsible for debugging its own errors.

---

### **4. Global System Requirements**

* **Configuration:** All system settings (API keys, model names, default resource limits, etc.) must be managed via a central `config.yaml` or `.env` file used by Saheeli.
* **Security:**
    * Servos must run as a **non-root user** inside their Docker containers.
    * Human-in-the-Loop (HITL) confirmation should be a configurable option in Saheeli for approving potentially destructive Servo commands.
* **Auditing:** Both Saheeli and every Servo must produce detailed, structured (JSON) logs of all actions, decisions, and API calls, creating a complete and transparent audit trail for every task.
