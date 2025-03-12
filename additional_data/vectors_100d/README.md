# 100-Dimensional Vectors

This directory contains 100-dimensional vectors for lipid structures from the LMSD and SwissLipids databases, which were computed using the ```src/lipid_vector_space``` package and subsequently reduced to 2 and 3 dimensions with t-SNE for use in the "Lipidome Projector" software (see ```scripts``` for more details). 

To stay below the 100 MB file size limit, the vectors were split into multiple files and compressed. Note that only the first file "```_split_0```" contains the header with the column names.