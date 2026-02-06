
import logging
import time
import json
from typing import List, Optional
from dataclasses import asdict

from contextcliff.data.formats import Example, Prediction, EvalRecord
from contextcliff.models.client import ModelClient
from contextcliff.models.openai_client import OpenAIClient
from contextcliff.runner.state import StateManager
# from contextcliff.eval.metrics import compute_metrics # Will serve as placeholder

from contextcliff.eval.metrics import evaluate_example

class Runner:
    """Orchestrates the evaluation process."""
    
    def __init__(self, manifest_path: str, model_name: str, run_id: str, db_path: str = "state.db"):
        self.manifest_path = manifest_path
        self.model_name = model_name
        self.run_id = run_id
        
        # Init components
        self.state = StateManager(db_path)
        
        # Model Factory
        if "gpt" in model_name:
            self.client = OpenAIClient(model_name)
        else:
            raise NotImplementedError("Only OpenAI supported in Phase 1")
            
        # Load Data
        with open(manifest_path, 'r') as f:
            data = json.load(f)
            self.examples = [Example(**d) for d in data]

    def check_cost(self) -> float:
        """Estimate total cost."""
        total_prompt_tokens = sum(ex.context_tokens for ex in self.examples)
        # Use simple heuristic for comparison tokens (e.g. 100) or assume max_tokens
        est_completion = len(self.examples) * 100
        
        cost = self.client.cost_estimate(total_prompt_tokens, est_completion)
        return cost

    def run(self):
        """Execute the run loop."""
        cost = self.check_cost()
        print(f"Starting run {self.run_id} with {len(self.examples)} examples.")
        print(f"Estimated Cost: ${cost:.2f} (Confirm with user in CLI if > threshold)")
        
        completed = self.state.get_completed_ids(self.run_id)
        if completed:
            print(f"Resuming: Skipping {len(completed)} already completed items.")
        
        for example in self.examples:
            if example.id in completed:
                continue
                
            # Build Prompt
            prompt = f"Context:\n{example.context}\n\nQuestion:\n{example.question}\nAnswer:"
            
            # Run Inference
            start_t = time.perf_counter()
            try:
                output = self.client.generate(prompt, max_tokens=100)
                latency = (time.perf_counter() - start_t) * 1000
                
                # Create Prediction object
                usage = self.client.get_token_usage()
                pred = Prediction(
                    example_id=example.id,
                    raw_output=output,
                    latency_ms=latency,
                    usage=usage
                )
                
                # Compute Metrics
                metrics = evaluate_example(example, output)
                
                # Save
                self.state.save_prediction(self.run_id, example.id, pred, metrics)
                print(f"Processed {example.id}: F1={metrics.f1_score:.2f}, Latency={latency:.0f}ms")
                
            except Exception as e:
                print(f"Failed {example.id}: {e}")
                continue

        print("Run complete.")
