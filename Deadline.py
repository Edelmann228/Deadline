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
##Проверка, выполнима ли конкретная задача в изолированных условиях.
def is_feasible(task: Task) -> bool:
    return slack(task) >= 0
## определение категории дедлайна
def deadline_type(task: Task) -> str:
    if task.D == task.T:
        return "неявный"
    if task.D < task.T:
        return "ограниченный"
    return "произвольный"
## определение строгости системы
def classify_system(tasks: List[Task]) -> str:
    for task in tasks:
        if task.task_class == "жёсткое":
            return "жёсткого реального времени"
    return "мягкого реального времени"
## нахождение критической задачи
def critical_task(tasks: List[Task]) -> Optional[Task]:
    hard_tasks = [task for task in tasks if task.task_class == "жёсткое"]

    if not hard_tasks:
        return None

    return min(hard_tasks, key=slack)