# Lipidome Projector

Lipidome Projector is a web-based application for the interactive visualization and analysis of lipidome datasets.

## Installation / Startup

Currently there is no pip / conda package available. To install this package with pip, clone the repository and from the projects root directory and run:

```pip install .```

This will install the package and all Python dependencies. Note that a working installation of a C and C++ compiler is required to build some of the dependencies.

To start the application from the command line, run:

```lipidome_projector```

This will start a local server. Open a web browser and navigate to
```http://localhost:8050``` to access the application.

## Expected File Formats

For any lipidome dataset, Lipidome Projector expects four CSV files to be provided through the upload interface:

Abundances:

- Simple CSV format, where rows correspond to lipidome samples and columns correspond to lipid abundances
- First row (header): Sample index name followed by lipid names
- First column (index): Sample index name followed by sample names
- Example:

```
LIPIDOME,DG 34:4,PC 28:2
Sample 1,0.12345,1.23456
Sample 2,2.34567,3.45678
```

Features:

- Simple CSV format, where rows correspond to lipidome samples and columns correspond to sample features
- First row (header): Sample index name followed by feature names
- First column (index): Sample index name followed by sample names
- Example:

```
LIPIDOME,Feature 1,Feature 2,
Sample 1,A,1
Sample 2,B,2
```

FA constraints:

- Single column CSV file listing the fatty acyl constraints to be applied during lipid matching
- FA descriptions start with the number of carbons (no "FA" prefix)
- Example:

```
10:0
12:1(7Z)
14:2(7Z,9Z)
```

LCB constraints:

- Single column CSV file listing the long-chain-base constraints to be applied during lipid matching
- LCB descriptions start with the number of carbons (no "LCB / SPB" prefix)
- Example:

```
14:1(4E);3OH
16:1(4E);3OH
14:2(4E,6E);3OH
```


# Data Sources

The databases used for the computation of the included lipid vector space are:

- Lipid Maps Structure Database (LMSD) (https://www.lipidmaps.org/) ([download](https://www.lipidmaps.org/files/?file=LMSD&ext=sdf.zip))
- SwissLipids (https://www.swisslipids.org/) ([download](https://www.swisslipids.org/api/file.php?cas=download_files&file=lipids.tsv))

The default example datasets included in this repository (``src/lipidome_projector/data/datasets/``) and used in the application are derived from data obtained from the following publications:

- Drosophila: "CARVALHO, Maria, et al. Effects of diet and development on the Drosophila lipidome. Molecular systems biology, 2012, 8. Jg., Nr. 1, S. 600."
- Yeast: "EJSING, Christer S., et al. Global analysis of the yeast lipidome by quantitative shotgun mass spectrometry. Proceedings of the National Academy of Sciences, 2009, 106. Jg., Nr. 7, S. 2136-2141."
- LAMP3: "LUNDING, Lars P., et al. LAMP3 deficiency affects surfactant homeostasis in mice. PLoS Genetics, 2021, 17. Jg., Nr. 6, S. e1009619."

Scripts for the extraction of the relevant data and the formatting into a format required for Lipidome Projector can be found in ``scripts/dataset_derivation``, where a local ``README.md`` file lists links to the published original dataset files.
