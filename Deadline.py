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
##Загрузка данных о задаче 
def load_data(file_path: str):
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    tasks = []
    for item in data["tasks"]:
        tasks.append(
            Task(
                name=item["name"],
                task_class=item["class"],
                C=float(item["C"]),
                D=float(item["D"]),
                T=float(item["T"])
            )
        )

    system = data["system"]
    return tasks, system["n_cpu"], system["has_network"], system["name"]
##Расчет временного резерва
def slack(task: Task) -> float:
    return task.D - task.C
