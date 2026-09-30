from pathlib import Path
from typing import List, Dict, Any

import faiss
import numpy as np


class FAISSVectorStore:

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.metadata: List[Dict[str, Any]] = []

    def add(
        self,
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ):
        if len(embeddings) != len(metadata):
            raise ValueError(
                "Number of embeddings must match number of metadata records."
            )

        vectors = np.asarray(
            embeddings,
            dtype="float32"
        )

        self.index.add(vectors)
        self.metadata.extend(metadata)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ):
        if self.index.ntotal == 0:
            return []

        query_vector = np.asarray(
            [query_embedding],
            dtype="float32"
        )

        scores, indices = self.index.search(
            query_vector,
            min(top_k, self.index.ntotal)
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            results.append({
                "score": float(score),
                "embedding": self.index.reconstruct(
                    int(index)
                ).tolist(),
                "metadata": self.metadata[index]
            })

        return results

    def save(self, directory: str):
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)

        faiss.write_index(
            self.index,
            str(path / "knowledge.index")
        )

        np.save(
            path / "metadata.npy",
            np.array(self.metadata, dtype=object),
            allow_pickle=True
        )

    def load(self, directory: str):
        path = Path(directory)

        index_path = path / "knowledge.index"
        metadata_path = path / "metadata.npy"

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )

        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {metadata_path}"
            )

        self.index = faiss.read_index(
            str(index_path)
        )

        self.metadata = np.load(
            metadata_path,
            allow_pickle=True
        ).tolist()

    def size(self) -> int:
        return self.index.ntotal