from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F


class TransformerAnalyzer:
    def __init__(self):
        self.model_name = "cardiffnlp/twitter-roberta-base-emotion"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.labels = ["anger", "joy", "optimism", "sadness"]

    def analyze(self, lyric: str) -> dict:
        inputs = self.tokenizer(
            lyric, return_tensors="pt", truncation=True, max_length=512
        )
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probs = F.softmax(logits, dim=-1)[0]
        top_idx = torch.argmax(probs).item()
        return {
            "method": "transformer",
            "emotion": self.labels[top_idx],
            "confidence": float(probs[top_idx]),
            "distribution": {label: float(p) for label, p in zip(self.labels, probs)},
        }


"""
Prueba unitaria de modelo de inferencia emocional
"""
if __name__ == "__main__":
    lyrics = "I'm so tired of being here Suppressed by all my childish fears And if you have to leave I wish that you would just leave 'Cause your presence still lingers here And it won't leave me alone These wounds won't seem to heal This pain is just too real There's just too much that time cannot erase When you cried I'd wipe away all of your tears When you'd scream I'd fight away all of your fears I held your hand through all of these years But you still have All of me You used to captivate me By your resonating light Now I'm bound by the life you left behind Your face it haunts My once pleasant dreams Your voice it chased away All the sanity in me These wounds won't seem to heal This pain is just too real There's just too much that time cannot erase When you cried I'd wipe away all of your tears When you'd scream I'd fight away all of your fears I held your hand through all of these years But you still have All of me I've tried so hard to tell myself that you're gone But though you're still with me I've been alone all along When you cried I'd wipe away all of your tears When you'd scream I'd fight away all of your fears I held your hand through all of these years But you still have All of me, me, me"
    model = TransformerAnalyzer()
    result = model.analyze(lyrics)
    print(result)
