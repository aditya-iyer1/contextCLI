import os
from pathlib import path

def get_db_path():
    local_db = Path("state.db")
    if