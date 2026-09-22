import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import sys

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
        widths = [len(header) for header in headers]

    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    print(separator)
    print("| " + " | ".join(
        headers[index].ljust(widths[index])
        for index in range(len(headers))
    ) + " |")
    print(separator)

    for row in rows:
        print("| " + " | ".join(
            row[index].ljust(widths[index])
            for index in range(len(row))
        ) + " |")

    print(separator)

def print_conclusion(
    tasks: List[Task],
    system_name: str,
    n_cpu: int,
    has_network: bool
) -> None:
    system_class = classify_system(tasks)
    critical = critical_task(tasks)
    reaction_time = required_reaction_time(tasks)
    load = utilization(tasks)
    architecture = classify_architecture(n_cpu, has_network)

    all_deadlines_feasible = all(is_feasible(task) for task in tasks)

    print("\nЗаключение:")
    print(f"Система: {system_name}.")
    print(f"Класс системы: {system_class}.")

    if critical is not None:
        print(
            f"Критическая задача: «{critical.name}», "
            f"L = {format_number(slack(critical))} мс."
        )
    else:
        print("Критическая задача: отсутствует, так как жёстких задач нет.")

    print(f"Требуемое время реакции R_треб = {format_number(reaction_time)} мс.")
    print(f"Коэффициент загрузки U = {load:.2f}.")
    print(f"Условие U <= 1: {'выполнено' if load <= 1 else 'не выполнено'}.")
    print(
        "Все дедлайны выполнимы: "
        f"{'да' if all_deadlines_feasible else 'нет'}."
    )
    print(f"Архитектура: {architecture}.")


def main() -> None:
    # Если при запуске передали имя файла, берем его. Иначе берем по умолчанию tasks.json
    filename = sys.argv[1] if len(sys.argv) > 1 else "specifications.json"
    
    # Собираем путь (теперь имя файла находится в переменной filename)
    data_file = Path(__file__).resolve().parent.parent / "data" / filename

    if not data_file.exists():
        print(f"Ошибка: Файл не найден по пути {data_file}")
        return

    tasks, n_cpu, has_network, system_name = load_data(str(data_file))
    
    print(f"Вариант: {system_name}")
    print(f"Процессоров: {n_cpu}")
    print(f"Сеть: {'есть' if has_network else 'нет'}\n")

    print_table(tasks)
    print_conclusion(tasks, system_name, n_cpu, has_network)


if __name__ == "__main__":
    main()
