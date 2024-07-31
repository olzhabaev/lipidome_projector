import logging

from pathlib import Path

from lipid_vector_space.databases.db_processing import Databases
from lipid_vector_space.databases.lmsd_processor import LMSDProcessor
from lipid_vector_space.databases.sl_processor import SLProcessor
from lipid_vector_space.descriptors.atom_radius_bit_map import (
    AtomRadiusBitMapWriter,
)

logging.basicConfig(level=logging.INFO)

logger: logging.Logger = logging.getLogger(__name__)

# Output Directory

output_dir_path: Path = Path("output")
Path.mkdir(output_dir_path, exist_ok=True)

# Databases and Structures

lmsd_processor: LMSDProcessor = LMSDProcessor(
    source_file_path=Path("lmsd.sdf"),
    output_dir_path=output_dir_path,
    canonize_mols=True,
    uncharge_mols=True,
    num_mol_chunks=1,
)

sl_processor: SLProcessor = SLProcessor(
    source_file_path=Path("sl.tsv"),
    output_dir_path=output_dir_path,
    canonize_mols=True,
    uncharge_mols=True,
    num_mol_chunks=20,
)

processors: list = [lmsd_processor, sl_processor]
databases: Databases = Databases(processors)

databases.proc_and_write_structures()

databases.parse_and_write()

# Model Descriptors

mols_paths: list[Path] = [
    path for processor in processors for path in processor.mols_output_paths
]

atom_radius_bit_map_writer: AtomRadiusBitMapWriter = AtomRadiusBitMapWriter(
    mols_paths=mols_paths,
    output_dir_path=output_dir_path,
    max_radius=50,
    include_chirality=True,
)

atom_radius_bit_map_writer()
