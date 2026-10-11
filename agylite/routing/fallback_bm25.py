"""BM25 over capability cards: the router's semantic-retrieval fallback (spec §15 "fallback/secondary").

Runs only when deterministic rules and intent tags are not confident. Documents are the rendered CARD.md (L1) plus
the card's name, description and intent tags; only routable (on-demand / explicit) capabilities are indexed.
"""
import math
import re
from collections import Counter

STOPWORDS = frozenset("""a an and are as at be but by can do does for from has have how i if in into is it its make me
my of on or our please so that the their them then there these this to us want was we what when where which who why
will with you your""".split())
_WORD = re.compile(r"[a-z0-9][a-z0-9+#.-]*[a-z0-9+#]|[a-z0-9]")


def tokenize(text: str):
    out = []
    for w in _WORD.findall(text.lower()):
        if w in STOPWORDS or len(w) < 2:
            continue
        if len(w) > 4 and w.endswith("ies"):
            w = w[:-3] + "y"
        elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


class BM25:
    def __init__(self, docs: dict, k1: float = 1.2, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = {key: Counter(tokenize(text)) for key, text in docs.items()}
        self.len = {key: sum(c.values()) for key, c in self.tf.items()}
        self.avg = (sum(self.len.values()) / len(self.len)) if self.len else 0.0
        df = Counter(t for c in self.tf.values() for t in c)
        n = len(self.tf)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def score(self, query: str):
        terms = set(tokenize(query))
        scores = {}
        for key, tf in self.tf.items():
            s = 0.0
            for t in terms:
                f = tf.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.len[key] / self.avg))
            if s > 0:
                scores[key] = s
        return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))

    def top(self, query: str, k: int, min_score: float):
        """Up to k (key, score) pairs scoring at least min_score and at least 60% of the best score."""
        ranked = self.score(query)
        if not ranked:
            return []
        best = ranked[0][1]
        return [(key, round(s, 3)) for key, s in ranked[:k] if s >= min_score and s >= best * 0.6]
