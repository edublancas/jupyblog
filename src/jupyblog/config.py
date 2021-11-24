import importlib
import os
from pathlib import Path

import yaml

from pydantic import BaseModel


class Config(BaseModel):
    """

    Parameters
    ----------
    root : str
        Paths are relative to this directory

    path_to_posts : str
        Where to store output .md, relative to root

    path_to_posts : str
        Where to store images, relative to root

    prefix_img : str
        A prefix to add to all image tags

    language_mapping : dict
        Mapping to apply to code chunks

    image_placeholders : bool
        Adds a placeholder before each image tag, useful if uploading
        to a platform that needs manual image upload (e.g., Medium)

    processor : str
        Dotted path with a function to execute to finalize processing, must
        return a string with the modified document content, which represents
        the .md to store

    postprocessor : str
        Dotted path with a function to execute after processing the document
    """
    root: str
    path_to_posts: str
    path_to_static: str
    prefix_img: str = ''
    language_mapping: dict = None
    image_placeholders: bool = False
    processor: str = None
    postprocessor: str = None

    def path_to_posts_abs(self):
        return Path(self.root, self.path_to_posts)

    def path_to_static_abs(self):
        return Path(self.root, self.path_to_static)

    def read_footer_template(self):
        path = Path(self.root, 'jupyblog-footer.md')
        return None if not path.is_file() else path.read_text()

    def load_processor(self):
        if self.processor:
            return self._load_dotted_path(self.processor)

    def load_postprocessor(self):
        if self.postprocessor:
            return self._load_dotted_path(self.postprocessor)

    @staticmethod
    def _load_dotted_path(dotted_path):
        mod, _, attr = dotted_path.rpartition('.')
        return getattr(importlib.import_module(mod), attr)


def find_file_recursively(name, max_levels_up=6, starting_dir=None):
    """
    Find a file by looking into the current folder and parent folders,
    returns None if no file was found otherwise pathlib.Path to the file

    Parameters
    ----------
    name : str
        Filename

    Returns
    -------
    path : str
        Absolute path to the file
    levels : int
        How many levels up the file is located
    """
    current_dir = starting_dir or os.getcwd()
    current_dir = Path(current_dir).resolve()
    path_to_file = None
    levels = None

    for levels in range(max_levels_up):
        current_path = Path(current_dir, name)

        if current_path.exists():
            path_to_file = current_path.resolve()
            break

        current_dir = current_dir.parent

    return path_to_file, levels


def get_config(name='jupyblog.yaml'):
    """
    Load jupyblog configuration file
    """

    path, _ = find_file_recursively(name)

    if path is None:
        raise FileNotFoundError(f'Could not find {name}')

    cfg = Config(**yaml.safe_load(Path(path).read_text()),
                 root=str(path.parent))

    if cfg.path_to_posts_abs().is_dir() and cfg.path_to_static_abs().is_dir():
        return cfg
    else:
        raise NotADirectoryError(
            f'missing {cfg.path_to_posts_abs()} or {cfg.path_to_static_abs()}')


def get_local_config():
    Path('output').mkdir()
    return Config(path_to_posts='output',
                  path_to_static='output',
                  prefix_img='',
                  root='.')
