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
## определение требуемого времени реакции системы
def required_reaction_time(tasks: List[Task]) -> float:
    hard_tasks = [task for task in tasks if task.task_class == "жёсткое"]

    if hard_tasks:
        return min(task.D for task in hard_tasks)

    return min(task.D for task in tasks)
## Рассчет суммарного коэффициентфа загрузки вычислительной системы
def utilization(tasks: List[Task]) -> float:
    return sum(task.C / task.T for task in tasks)
##Классификация архитектуры вычислительной системы по числу процессоров и наличию сетевых связей.
def classify_architecture(n_cpu: int, has_network: bool) -> str:
    if has_network:
        return "распределённая"
    if n_cpu == 1:
        return "однопроцессорная"
    return "многопроцессорная"
## форматирование чисел с плавающей точкой
def format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}"
## вывод таблицы
def print_table(tasks: List[Task]) -> None:
    headers = [
        "Задача", "Класс", "C", "D", "T",
        "L", "Выполнимо", "Тип дедлайна"
    ]
    rows = []
    for task in tasks:
        rows.append([
            task.name,
            task.task_class,
            format_number(task.C),
            format_number(task.D),
            format_number(task.T),
            format_number(slack(task)),
            "да" if is_feasible(task) else "нет",
            deadline_type(task)
        ])