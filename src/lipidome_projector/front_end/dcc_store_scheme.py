"""Module concerning the dcc.Store scheme."""


from dataclasses import dataclass
from typing import Self


# TODO Utilize or remove.
@dataclass
class DCCStoreScheme:
    @classmethod
    def from_dict(cls, dcc_store_dict: dict) -> Self:
        """Create a DCCStoreScheme from a dictionary.
        :param dcc_store_dict: Dictionary containing the
            dcc.Store data.
        :returns: DCCStoreScheme.
        """
        dcc_store_scheme: Self = cls()

        return dcc_store_scheme

    def to_dict(self) -> dict:
        """Create a dictionary from a DCCStoreScheme.
        :returns: Dictionary containing the dcc.Store data.
        """
        dcc_store_dict: dict = {}

        return dcc_store_dict

    @classmethod
    def get_empty_scheme(cls) -> Self:
        """Get an empty DCCStoreScheme.
        :returns: DCCStoreScheme.
        """
        dcc_store_scheme: Self = cls()

        return dcc_store_scheme

    @staticmethod
    def is_dataset_loaded(dcc_store_dict: dict) -> bool:
        """Check if a dataset is loaded.
        :param dcc_store_dict: Dictionary containing the dcc.Store
            data.
        :returns: True if a dataset is loaded, False otherwise.
        """
        return dcc_store_dict["current_lipidome_dataset"] != ""
