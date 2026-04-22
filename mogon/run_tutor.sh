#!/bin/bash
###############################################################################
# SLURM batch script for Course Tutor on MOGON II
# 
# This script:
#   1. Starts Ollama server inside an Apptainer container (with GPU)
#   2. Pulls llama3.2 if not already cached
#   3. Launches the Streamlit Course Tutor app
#
# Usage:  sbatch run_tutor.sh
###############################################################################

#SBATCH --account=nhr-haloed
#SBATCH --comment="Course Tutor Streamlit + Ollama"
#SBATCH --gres=gpu:a100:1
#SBATCH --job-name=course-tutor
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=$HOME/logs/tutor_%j.log
#SBATCH --partition=a100dl
#SBATCH --time=04:00:00

###############################################################################
# Setup
###############################################################################

# Load Apptainer module
module load tools/Apptainer/1.3.4-GCCcore-13.3.0
module load squashfuse

# Prevent /tmp overflow for large images (per MOGON docs)
APPTAINER_TMPDIR=/localscratch/${SLURM_JOB_ID}/apptainer_tmp/
export APPTAINER_TMPDIR
mkdir -p "$APPTAINER_TMPDIR"

# Directories
WORK_DIR="$HOME/course-tutor"
OLLAMA_DATA="$WORK_DIR/ollama_models"
LOGS_DIR="$HOME/logs"
mkdir -p "$OLLAMA_DATA" "$LOGS_DIR"

# Container images (must be built beforehand — see MOGON_SETUP.md)
OLLAMA_SIF="$WORK_DIR/ollama.sif"
TUTOR_SIF="$WORK_DIR/course-tutor.sif"

###############################################################################
# Print connection info
###############################################################################
echo "========================================================="
echo " Course Tutor - MOGON II"
echo "========================================================="
echo " Job ID    : $SLURM_JOB_ID"
echo " Node      : $(hostname)"
echo " Started   : $(date)"
echo ""
echo " To access the Streamlit UI, run on your LOCAL machine:"
echo ""
echo "   ssh -L 8501:$(hostname):8501 mogon"
echo ""
echo " Then open: http://localhost:8501"
echo "========================================================="

###############################################################################
# 1. Start Ollama server (background)
###############################################################################
echo "[$(date)] Starting Ollama server..."

apptainer exec  \
    --bind "$OLLAMA_DATA":/root/.ollama \
    "$OLLAMA_SIF" \
    ollama serve &

OLLAMA_PID=$!
echo "[$(date)] Ollama PID: $OLLAMA_PID"

# Wait for Ollama to be ready
echo "[$(date)] Waiting for Ollama to start..."
for i in $(seq 1 30); do
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "[$(date)] Ollama is ready."
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "[$(date)] ERROR: Ollama failed to start after 30s. Exiting."
        exit 1
    fi
    sleep 1
done

###############################################################################
# 2. Pull llama3.2 model (skipped if already cached)
###############################################################################
echo "[$(date)] Ensuring llama3.2 model is available..."

apptainer exec  \
    --bind "$OLLAMA_DATA":/root/.ollama \
    "$OLLAMA_SIF" \
    ollama pull llama3.2

echo "[$(date)] Model ready."

###############################################################################
# 3. Start Streamlit Course Tutor
###############################################################################
echo "[$(date)] Starting Course Tutor Streamlit app..."

apptainer exec \
    --bind "$LOGS_DIR":/app/logs \
    --bind "$WORK_DIR/config.yaml":/app/config.yaml \
    "$TUTOR_SIF" \
    streamlit run /app/app.py \
        --server.port=8501 \
        --server.address=0.0.0.0

###############################################################################
# Cleanup
###############################################################################
echo "[$(date)] Streamlit exited. Stopping Ollama..."
kill "$OLLAMA_PID" 2>/dev/null
wait "$OLLAMA_PID" 2>/dev/null
echo "[$(date)] Done."
