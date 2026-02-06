
from contextcliff.data.formats import Example, EvalRecord

def compute_f1(a_gold: str, a_pred: str) -> float:
    """Compute normalized token-level F1 score."""
    def normalize(text):
        return text.lower().strip()
    
    pred_toks = normalize(a_pred).split()
    gold_toks = normalize(a_gold).split()
    
    common = 0
    g_toks_copy = list(gold_toks)
    for p in pred_toks:
        if p in g_toks_copy:
            common += 1
            g_toks_copy.remove(p)
            
    if len(pred_toks) == 0 or len(gold_toks) == 0:
        return float(pred_toks == gold_toks)
        
    prec = common / len(pred_toks)
    rec = common / len(gold_toks)
    
    if prec + rec == 0:
        return 0.0
    return 2 * (prec * rec) / (prec + rec)

def exact_match_score(prediction: str, ground_truth: str) -> float:
    return 1.0 if prediction.lower().strip() == ground_truth.lower().strip() else 0.0

def evaluate_example(example: Example, prediction_text: str) -> EvalRecord:
    """Compare prediction to all valid answers and take the best score."""
    best_f1 = 0.0
    best_em = 0.0
    
    # Check against all acceptable answers
    for ans in example.answers:
        em = exact_match_score(prediction_text, ans)
        f1 = compute_f1(ans, prediction_text)
        
        if em > best_em: best_em = em
        if f1 > best_f1: best_f1 = f1
            
    return EvalRecord(
        example_id=example.id,
        context_tokens=example.context_tokens,
        f1_score=best_f1,
        em_score=best_em
    )
