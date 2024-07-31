import logging

from pathlib import Path

from lipid_vector_space.bit2vec.workflow import L2VModel

logging.basicConfig(level=logging.INFO)

logger: logging.Logger = logging.getLogger(__name__)

# Directories

output_dir_path: Path = Path("output")

# Training

atom_radius_bit_map_paths: list[Path] = [
    output_dir_path / Path("lmsd_mols_0_atom_radius_bit_map.pkl")
] + [
    output_dir_path / Path(f"sl_mols_{i}_atom_radius_bit_map.pkl")
    for i in range(20)
]

w2v_params: dict = {
    "epochs": 10,
    "vector_size": 100,
    "sg": 1,
    "window": 4,
    "min_count": 1,
    "hs": 1,
    "negative": 0,
    "sample": 0,
    "workers": 20,
}

radii: list[int] = [0, 1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

l2v_model: L2VModel = L2VModel(
    output_dir_path=output_dir_path,
    model="w2v",
    orderings=["radius_atom"],
    radii=radii,
    model_params=w2v_params,
    shuffle=True,
    atom_radius_bit_map_paths=atom_radius_bit_map_paths,
)

l2v_model()
