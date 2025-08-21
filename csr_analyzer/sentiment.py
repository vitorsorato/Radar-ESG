from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class SentimentResult:
    label: str
    score: float


class SentimentAnalyzer:
    """Analyze text sentiment using a Transformers pipeline or lexicon fallback.

    Default model: multilingual (CardiffNLP). Use model_name="lexicon" to force fallback.
    """

    def __init__(self, model_name: Optional[str] = None, batch_size: int = 16) -> None:
        self.batch_size = batch_size
        self._use_lexicon = False
        self._pipe = None

        chosen_model = model_name or "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        if model_name == "lexicon":
            self._use_lexicon = True
            return

        # Lazy import to avoid warnings when no backend is installed
        try:
            from transformers import pipeline as hf_pipeline  # type: ignore
        except Exception:
            self._use_lexicon = True
            return

        try:
            self._pipe = hf_pipeline("sentiment-analysis", model=chosen_model)
        except Exception:
            # If model download or init fails, fallback to lexicon
            self._use_lexicon = True

    # --- public API ---
    def analyze(self, text: str) -> Dict[str, Any]:
        if not text:
            return {"label": "neutral", "score": 0.0}
        if self._use_lexicon:
            return self._lexicon_predict(text)
        assert self._pipe is not None
        output = self._pipe(text)[0]
        return self._normalize_transformers_output(output)

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        if self._use_lexicon or not texts:
            return [self._lexicon_predict(t) for t in texts]
        assert self._pipe is not None
        results: List[Dict[str, Any]] = []
        for start in range(0, len(texts), self.batch_size):
            chunk = texts[start : start + self.batch_size]
            outputs = self._pipe(chunk)
            for out in outputs:
                results.append(self._normalize_transformers_output(out))
        return results

    # --- internals ---
    @staticmethod
    def _normalize_transformers_output(raw: Dict[str, Any]) -> Dict[str, Any]:
        label = str(raw.get("label", "")).upper()
        score = float(raw.get("score", 0.0))
        # Map various label schemes to {negative, neutral, positive}
        mapping = {
            "NEGATIVE": "negative",
            "NEUTRAL": "neutral",
            "POSITIVE": "positive",
            "LABEL_0": "negative",  # CardiffNLP
            "LABEL_1": "neutral",
            "LABEL_2": "positive",
            "1 STAR": "negative",
            "2 STARS": "negative",
            "3 STARS": "neutral",
            "4 STARS": "positive",
            "5 STARS": "positive",
        }
        return {"label": mapping.get(label, "neutral"), "score": score}

    # Very small lexicon for fallback; extend as needed.
    POSITIVE_WORDS = {
        "bom", "boa", "excelente", "positivo", "melhoria", "sustentável", "sustentabilidade",
        "redução", "reciclagem", "conservação", "proteção", "responsável", "premiado", "liderança",
        "inovação", "inclusão", "diversidade", "transparência", "ética", "compliance",
    }
    NEGATIVE_WORDS = {
        "ruim", "péssimo", "negativo", "queda", "poluição", "desmatamento", "desastre",
        "crime", "multas", "corrupção", "fraude", "vazamento", "derramamento", "emissões",
        "escravidão", "trabalho escravo", "exploração", "discriminação", "ilegal",
    }

    def _lexicon_predict(self, text: str) -> Dict[str, Any]:
        lowered = text.lower()
        pos_hits = sum(1 for w in self.POSITIVE_WORDS if w in lowered)
        neg_hits = sum(1 for w in self.NEGATIVE_WORDS if w in lowered)
        score = 0.0
        label = "neutral"
        if pos_hits > neg_hits:
            label = "positive"
            score = (pos_hits - neg_hits) / max(1, pos_hits + neg_hits)
        elif neg_hits > pos_hits:
            label = "negative"
            score = (neg_hits - pos_hits) / max(1, pos_hits + neg_hits)
        return {"label": label, "score": score}
