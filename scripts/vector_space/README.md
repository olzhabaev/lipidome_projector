# Vector Space Computation

This directory contains scripts for the computation of the lipid vector space.
The scripts require the LMSD and SwissLipids source files to be present here 
named "lmsd.sdf" and "sl.tsv", respectively.

The scripts must be executed in the following order:

- "preprocessing.py":
    - Extracts and preprocesses molecule structures from the LMSD and SwissLipids files.
    - Parses the database nomenclature.
    - Writes the processed data into the "output" directory.
- "training.py":
    - Trains the word2vec model on the processed data.
    - Writes the trained model files into the "output" directory.
- "dimensionality_reduction.py":
    - Applies t-SNE to the word2vec vectors.
    - Writes the reduced vectors into the "output" directory.
- "postprocessing.py":
    - Filters and packages the results.

After running the scripts, the relevant results in the "output" directory are:

- "database.zip": The combined parsed LMSD and SwissLipids databases.
- "smiles.zip": The SMILES strings of the molecules.
- "vectors_2d.zip": The 2D t-SNE vectors.
- "vectors_3d.zip": The 3D t-SNE vectors.

To update the vector space, place these files in the "data/database" directory
of the Lipidome Projector repository.
