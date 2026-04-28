from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, ClassVar
from pathlib import Path

from copydetect import defaults


@dataclass
class CopydetectConfig:
    """Utility class for providing a full list of configuration
    parameters with type/value checking and simple conversion to and from
    the JSON format used by the copydetect CLI.
    """

    test_dirs: List[str] = field(default_factory=lambda: [])
    ref_dirs: Optional[List[str]] = field(default_factory=lambda: [])
    boilerplate_dirs: Optional[List[str]] = field(default_factory=lambda: [])
    extensions: Optional[List[str]] = field(default_factory=lambda: ["*"])
    noise_t: int = defaults.NOISE_THRESHOLD
    guarantee_t: int = defaults.GUARANTEE_THRESHOLD
    display_t: float = defaults.DISPLAY_THRESHOLD
    same_name_only: bool = False
    ignore_leaf: bool = False
    autoopen: bool = True
    disable_filtering: bool = False
    force_language: Optional[str] = None
    truncate: bool = False
    out_file: str = "./report.html"
    css_files: List[str] = field(default_factory=lambda: [])
    silent: bool = False
    encoding: str = "utf-8"

    window_size: int = field(init=False, default=guarantee_t - noise_t + 1)
    short_names: ClassVar[Dict[str, str]] = {
        "noise_threshold": "noise_t",
        "guarantee_threshold": "guarantee_t",
        "display_threshold": "display_t",
        "test_directories": "test_dirs",
        "reference_directories": "ref_dirs",
        "boilerplate_directories": "boilerplate_dirs",
    }

    def _check_arguments(self):
        """Checks type/value of all parameters"""
        pass

    @staticmethod
    def normalize_outfile(file_path: str) -> str:
        """Ensures that the outfile has an html suffix. If the provided
        out file is a directory, append report.html to the path.
        """
        pass

    def to_json(self) -> dict:
        """Converts the parameters of this configuration to the JSON
        format used for copydetect config files
        """
        dict_params = asdict(self)
        for long_name, short_name in self.short_names.items():
            dict_params[long_name] = dict_params[short_name]
            del dict_params[short_name]
        dict_params["disable_autoopen"] = not dict_params["autoopen"]
        del dict_params["autoopen"]
        if self.force_language is None:
            del dict_params["force_language"]
        return dict_params

    @staticmethod
    def normalize_json(config: dict) -> dict:
        """Converts the longer names used by the JSON configuration
        format to the arguments used by the CopyDetector class.
        """
        for long_name, short_name in CopydetectConfig.short_names.items():
            if long_name in config:
                config[short_name] = config[long_name]
                del config[long_name]
        if "disable_autoopen" in config:
            config["autoopen"] = not config["disable_autoopen"]
            del config["disable_autoopen"]
        return config

    def __post_init__(self):
        """Sets reference directories to test directories if needed and
        performs argument checking.
        """
        pass
