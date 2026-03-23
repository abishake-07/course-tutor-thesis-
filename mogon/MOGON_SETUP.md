# MOGON II Deployment Guide — Course Tutor

This guide walks through deploying the Course Tutor (Streamlit + Ollama/llama3.2) on MOGON II using Apptainer containers.

---

## Prerequisites

- MOGON II cluster access with a valid project allocation
- Docker installed on your **local machine** (for building images)
- SSH config for MOGON II (see MOGON docs)

---

## Overview

Two Apptainer container images are needed:

| Image | Purpose |
|---|---|
| `course-tutor.sif` | Streamlit app (this project) |
| `ollama.sif` | Ollama LLM server running llama3.2 |

---

## Step 1: Build Docker Images Locally

### 1a. Course Tutor image

```bash
cd /path/to/course-tutor
docker build -t course-tutor .
```

### 1b. Save as tarball

```bash
docker images   # note the IMAGE ID for course-tutor
docker save <IMAGE_ID> -o course-tutor.tar
```

### 1c. Ollama image (pull from Docker Hub)

```bash
docker pull ollama/ollama
docker images   # note the IMAGE ID for ollama/ollama
docker save <OLLAMA_IMAGE_ID> -o ollama.tar
```

---

## Step 2: Transfer to MOGON II

```bash
scp course-tutor.tar mogon2:~/course-tutor/
scp ollama.tar       mogon2:~/course-tutor/
scp config.yaml      mogon2:~/course-tutor/
scp mogon/run_tutor.sh mogon2:~/course-tutor/
```

> Replace `mogon2` with `<username>@mogon2.zdv.uni-mainz.de` if you haven't set up an SSH alias.

---

## Step 3: Convert to Apptainer Images on MOGON II

```bash
ssh mogon2
cd ~/course-tutor

module load tools/AppTainer

# Convert Course Tutor
apptainer build course-tutor.sif docker-archive://course-tutor.tar

# Convert Ollama
apptainer build ollama.sif docker-archive://ollama.tar

# Clean up tarballs to save space
rm course-tutor.tar ollama.tar
```

---

## Step 4: Configure

Edit `~/course-tutor/config.yaml` on MOGON II if needed. The key settings:

```yaml
model:
  provider: ollama
  name: llama3.2
  ollama_base_url: http://localhost:11434   # Ollama runs on same node
```

No changes needed if using the default config since Ollama will run on `localhost:11434` on the same compute node.

---

## Step 5: Edit the SLURM Script

Open `~/course-tutor/run_tutor.sh` and replace the two `TODO` placeholders:

```bash
#SBATCH -A <your_allocation>          # your project allocation code
#SBATCH --partition=<partition_name>   # GPU partition (run `sinfo` to check)
```

Also update the `<user>` placeholder in the SSH tunnel echo line.

---

## Step 6: Submit the Job

```bash
cd ~/course-tutor
mkdir -p logs
sbatch run_tutor.sh
```

Monitor:
```bash
squeue -u $USER             # check job status
cat logs/tutor_<JOBID>.log  # view output once running
```

---

## Step 7: Connect to the UI

Once the job is running, check the log for the compute node name, then from your **local machine**:

```bash
ssh -L 8501:<compute-node>:8501 mogon2
```

Open **http://localhost:8501** in your browser.

---

## File Structure on MOGON II

```
~/course-tutor/
├── course-tutor.sif      # App container image
├── ollama.sif            # Ollama container image
├── config.yaml           # Tutor configuration
├── run_tutor.sh          # SLURM batch script
├── logs/                 # Streamlit session logs (bind-mounted)
└── ollama_models/        # Cached Ollama models (bind-mounted, persists across jobs)
```

---

## Notes

- **Model caching**: The Ollama model directory is bind-mounted to `~/course-tutor/ollama_models/`. The first run will download llama3.2 (~2GB). Subsequent jobs reuse the cached model.
- **GPU**: The SLURM script requests 1 GPU (`--gres=gpu:1`). Ollama uses `--nv` for GPU passthrough.
- **Walltime**: Default is 4 hours. Adjust `--time` in the SLURM script as needed.
- **Logs**: Streamlit logs are persisted via bind-mount to `~/course-tutor/logs/`.
- **Rebuilding**: If you change app code, rebuild only `course-tutor.sif`. The `ollama.sif` image is reusable.

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Ollama fails to start | Check GPU availability: `sinfo -p <partition> -o "%G"`. Ensure `--gres=gpu:1` is set. |
| Model download is slow | First pull can take time. The model is cached in `ollama_models/` for future runs. |
| Can't connect to Streamlit | Verify the SSH tunnel points to the correct compute node from the job log. |
| `/tmp` full error | The script sets `APPTAINER_TMPDIR` to localscratch, which should prevent this. |
| Job killed for memory | Increase `--mem` in the SLURM script (e.g., `--mem=32G`). |
