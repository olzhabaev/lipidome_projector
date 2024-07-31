# Lipidome Projector

Lipidome Projector is a web-based application for the interactive visualization and analysis of lipidome datasets.

## Installation / Usage

Currently there is no pip / conda package available. To install this package with pip, clone the repository and from the projects root directory and run:

```pip install .```

This will install the package and all Python dependencies. Note that a working installation of a C and C++ compiler is required to build some of the dependencies.

To start the application from the command line, run:

```lipidome_projector```

This will start a local server. Open a web browser and navigate to
```http://localhost:8050``` to access the application.

# Data Sources

The databases used for the computation of the included lipid vector space are:

- Lipid Maps Structure Database (LMSD) (https://www.lipidmaps.org/)
- SwissLipids (https://www.swisslipids.org/)

The example dataset projections are derived from data obtained from the following publications:

- Drosophila: "CARVALHO, Maria, et al. Effects of diet and development on the Drosophila lipidome. Molecular systems biology, 2012, 8. Jg., Nr. 1, S. 600."
- Yeast: "EJSING, Christer S., et al. Global analysis of the yeast lipidome by quantitative shotgun mass spectrometry. Proceedings of the National Academy of Sciences, 2009, 106. Jg., Nr. 7, S. 2136-2141."
- LAMP3: "LUNDING, Lars P., et al. LAMP3 deficiency affects surfactant homeostasis in mice. PLoS Genetics, 2021, 17. Jg., Nr. 6, S. e1009619."

