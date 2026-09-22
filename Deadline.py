import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

##cоздание класса данных
@dataclass
class Task:
    name: str
    task_class: str
    C: float
    D: float
    T: float

