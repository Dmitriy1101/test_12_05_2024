"""
Список команд:

-h  --help    : помлощь в управлении
-l  --lenght  : длинна обрабатываемого диапазона значений по типу 'начало:конец'
-n  --name    : 'имя_файла.png' в который сохранится график
-c  --columns : перечисление имен обрабатываемых столбцов по типу 'столбец1/столбец2/столбец3'

Пример: '--help -l 100:200 -n test.png -c mean'

Список столбцов:

gt_corners   :  колличество углов
rb_corners   :  углов найдено
mean         :  среднее значение отклонений
max          :  максимальное отклонение
min          :  минимальное отклонение
floor_mean   :  среднее значение отклонений пола
floor_max    :  максимальное отклонение пола 
floor_min    : минимальное отклонение пола 
ceiling_mean :  среднее значение отклонений потолка
ceiling_max  :  максимальное отклонение потолка
ceiling_min  :  минимальное отклонение потолка
"""
import os
import sys
import time
import requests
from typing import Annotated, Literal, Callable
from pathlib import Path
from annotated_types import Ge, Gt, MinLen
from copy import copy
import logging
import pandas as pd
import matplotlib.pyplot as p

log: logging.Logger = logging.getLogger("pandas_script")
URL = "https://ai-process-sandy.s3.eu-west-1.amazonaws.com/purge/deviation.json"
TEMP_FILE_NAME = "temp.json"
PLOTS_PATH: Path = Path(__file__).resolve().with_name("plots")


def _docs(*args, **kwargs) -> None:
    """Строка документации."""

    print(__doc__)


def _lenght(data: list[str], plots_kwargs: dict) -> None:
    """Обработка переданной длинны диапазона."""

    val = list(map(int, data.pop(0).split(":")))
    if len(val) > 2:
        print(f"{val[:2:]} лишние данные не будут использованы.")
    plots_kwargs["first_index"], plots_kwargs["last_index"] = val[0], val[1]


def _name(data: list[str], plots_kwargs: dict) -> None:
    """Обработка переданного имени файла."""

    plots_kwargs["file_name"] = data.pop(0)


def _columns(data: list[str], plots_kwargs: dict) -> None:
    """Создаём список столбцов для обработки."""

    plots_kwargs["columns"] = data.pop(0).split("/")


# Маленькое_приложение : простое_решение
commands: dict[str, Callable] = {
    "-h": _docs,
    "--help": _docs,
    "-l": _lenght,
    "--lenght": _lenght,
    "-n": _name,
    "--name": _name,
    "-c": _columns,
    "--columns": _columns,
}


def ping_file(file_name: str) -> bool:
    """Ищем сохраненный файл."""

    ping_dir()
    is_filename(file_name)
    new_name = Path(PLOTS_PATH, file_name)
    if os.path.isfile(new_name):
        log.info(f"Файл {file_name} будет перезаписан!")
    return str(new_name)


def is_filename(file_name: str) -> Literal[True]:
    """Вернёт True если это имя .png файла, или выбросит ошибку"""

    if not file_name or not file_name[-4:] == ".png" or len(file_name) < 5:
        e = f"{file_name} <- Не имя '.png' файла"
        log.info(e)
        raise ValueError(e)
    return True


def ping_dir() -> bool:
    """Если нету директории plots создаём."""

    if not os.path.isdir(PLOTS_PATH):
        os.mkdir(PLOTS_PATH)
        log.info("Папка plots создана.")
        return True
    return False


def get_json_datafile(url: str):
    """Получаем файл по переданной ссылке."""

    res: requests.Response = requests.get(url)
    if res.status_code != 200:
        log.info("Невозможно получить данные")
        return False
    src: bytes = res.content
    with open(TEMP_FILE_NAME, "wb") as f:
        f.write(src)
    return True


def is_columns(tested_data: list[str], correct_data: list[str]) -> list[str]:
    """Сверяем имена столбцов."""

    return_data: list[str] = []

    if not tested_data:
        return_data = correct_data
        return_data.remove("name")
        return return_data

    elif len(tested_data) == 1 and "name" in tested_data:
        e = f"Неверное имя столбца:{tested_data}"
        log.info(e)
        raise ValueError(e)

    return_data = [i for i in correct_data if i in tested_data and i != "name"]

    if not return_data:
        e = f"Неверные имена столбцов:{tested_data}"
        log.info(e)
        raise ValueError(e)

    return return_data


def draw_plots(
    file_name: Annotated[str, MinLen(5)],
    first_index: Annotated[int, Ge(0)] | None = None,
    last_index: Annotated[int, Gt(0)] | None = None,
    columns: list[str] = [],
) -> str:
    """
    filename: имя_файла.png,
    first_index: первая строка выборки,
    last_index: последняя строка выборки,
    columns: имя колонки таблицы или список_имен_таблицы,
    если нету
    """

    file_name = ping_file(file_name)

    if (first_index and last_index) and first_index >= last_index:
        e = f"Значение выборки данных первого индекса: {first_index} больше последнего: {last_index}"
        log.info(e)
        raise ValueError(e)

    w_data: pd.DataFrame = pd.read_json(TEMP_FILE_NAME)

    if isinstance(columns, str):
        columns = [columns]

    columns = is_columns(tested_data=columns, correct_data=list(w_data.columns))

    ret_data: pd.DataFrame = w_data.loc[first_index:last_index, columns]
    p.plot(ret_data)
    p.savefig(file_name)
    return str(PLOTS_PATH)


def get_start():
    """Обработка команд запуска из консоли."""

    if len(sys.argv) == 1:
        get_json_datafile(url=URL)
        return draw_plots(
            f"{time.time()}_test.png", last_index=200, columns=["min", "max", "mean"]
        )
    data: list[str] = copy(sys.argv)
    plots_kwargs: dict = {}
    print(f"{data.pop(0)} запуск создания графика.")
    try:
        while len(data) > 0:
            commands[data.pop(0)](data, plots_kwargs)
    except Exception as e:
        print(f"Ошибка причина: {e} \n --help : список команд")
        return
    if len(plots_kwargs.keys()) == 0:
        return
    get_json_datafile(url=URL)
    return draw_plots(**plots_kwargs)


if __name__ == "__main__":
    get_start()
