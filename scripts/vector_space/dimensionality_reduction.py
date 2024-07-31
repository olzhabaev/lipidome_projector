import logging

from pathlib import Path

from lipid_vector_space.embedding.dimensionality_reduction import tsne_sklearn
from lipid_vector_space.embedding.embedding import Embedding

logging.basicConfig(level=logging.INFO)
logging.getLogger("numba").setLevel(logging.WARNING)

logger: logging.Logger = logging.getLogger(__name__)

# Output Directory

output_dir_path: Path = Path("output")

# Dimensionality Reduction

embedding_hd: Embedding = Embedding.from_files(
    vec_csv_path=output_dir_path / "w2v_vectors.csv", index_col=0
)

tsne_params_2d: dict = {
    "n_components": 2,
    "perplexity": 150,
    "max_iter": 2000,
    "metric": "cosine",
    "n_jobs": 20,
    "verbose": 10,
}

tsne_params_3d: dict = tsne_params_2d.copy()
tsne_params_3d["n_components"] = 3

embedding_2d: Embedding = embedding_hd.derive(tsne_sklearn, **tsne_params_2d)
embedding_2d.vectors_df.rename(
    columns={0: "t-SNE 1 (2D)", 1: "t-SNE 2 (2D)"}, inplace=True
)
embedding_2d.save(output_dir_path / "vectors_2d.csv")

embedding_3d: Embedding = embedding_hd.derive(tsne_sklearn, **tsne_params_3d)
embedding_3d.vectors_df.rename(
    columns={0: "t-SNE 1 (3D)", 1: "t-SNE 2 (3D)", 2: "t-SNE 3 (3D)"},
    inplace=True,
)
embedding_3d.save(output_dir_path / "vectors_3d.csv")
