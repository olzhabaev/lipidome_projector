"""Module concerning the drawing of lipid structures."""

import base64
import logging

from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D  # type: ignore


logger: logging.Logger = logging.getLogger(__name__)


def get_lipid_structure_image(smiles: str, size: dict | None = None) -> str:
    """Get the lipid structure image.
    :param smiles: SMILES of the lipid.
    :param size: Size of the image.
    :returns: Base64 encoded image.
    """

    size = size if size is not None else {"width": 300, "height": 300}

    mol: Chem.Mol = Chem.MolFromSmiles(smiles)  # type: ignore

    drawer: rdMolDraw2D.MolDraw2DCairo = rdMolDraw2D.MolDraw2DCairo(**size)
    opts = rdMolDraw2D.MolDrawOptions()
    opts.clearBackground = False
    drawer.SetDrawOptions(opts)
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    img: str = drawer.GetDrawingText()
    img_base64: str = base64.b64encode(img).decode("utf-8")  # type: ignore

    return img_base64
