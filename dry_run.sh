
#!/bin/bash
set -e

echo "=== 1. PREPARE (Using verification script for speed) ==="
# We already ran verify_sampler.py which created manifest.json.
# But let's verify contextcliff prepare works too (although it might take long if full dataset).
# For now, let's trust manifest.json from verify_sampler exists.
if [ ! -f manifest.json ]; then
    echo "manifest.json missing. Running verify_sampler.py..."
    python3 verify_sampler.py
fi

echo "=== 2. RUN (Mock Model) ==="
# We capture the output to find the run id timestamp or just rely on 'mock_<timestamp>' pattern
# Since run_id is generated inside, we might need to grep it or force a run_id?
# CLI doesn't allow forcing run_id easily in current code (generated inside run).
# Wait, CLI 'prepare' doesn't return run_id. 'run' generates it.
# 'profile' needs run_id.
# I will modify CLI run command to print the run_id clearly so I can capture it, 
# or I will just list the state.db to find it.

contextcliff run --manifest manifest.json --model mock > run_output.txt 2>&1
cat run_output.txt

# Extract run_id. It says "Initializing run mock_12345..."
RUN_ID=$(grep "Initializing run" run_output.txt | awk '{print $3}')
echo "Captured Run ID: $RUN_ID"

echo "=== 3. PROFILE ==="
contextcliff profile $RUN_ID

echo "=== DONE ==="
