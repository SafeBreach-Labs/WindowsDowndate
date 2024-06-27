from dataclasses import dataclass
from typing import Dict

from windows_downdate.filesystem_utils import Path, is_path_exists


@dataclass
class UpdateFile:
    source_path_obj: Path
    destination_path_obj: Path
    should_retrieve_oldest: bool = False
    is_oldest_retrieved: bool = False

    def __post_init__(self):
        if not self.destination_path_obj.exists:
            raise FileNotFoundError(f"The file to update {self.destination_path_obj.full_path} does not exist")

        if not self.should_retrieve_oldest and not self.source_path_obj.exists:
            raise FileNotFoundError(f"The source file {self.source_path_obj.full_path} does not exist")

    def validate(self):
        if self.should_retrieve_oldest and not self.is_oldest_retrieved:
            raise Exception("Oldest destination file retrieval failed. "
                            f"Destination {self.destination_path_obj.name} may not be part of the component store")

    def to_hardlink_dict(self) -> Dict[str, str]:
        return {"source": self.source_path_obj.nt_path, "destination": self.destination_path_obj.nt_path}
