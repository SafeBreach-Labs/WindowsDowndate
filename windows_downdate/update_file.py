from dataclasses import dataclass

from windows_downdate.filesystem_utils import Path


# TODO: Find a better place, probably not the best to create a file just for this class


@dataclass
class UpdateFile:
    source: Path
    destination: Path
    should_retrieve_oldest: bool
    is_oldest_retrieved: bool

    def to_hardlink_dict(self):
        return {"source": self.source.nt_path, "destination": self.destination.nt_path}
