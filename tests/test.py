"""
В процессе тестов создаются тестовые фалы, в конце они будут удалены.
"""
import os
from pathlib import Path
import pandas as pd
from unittest import TestCase
from main import *


class TestMain(TestCase):
    """main.py"""

    def test_is_filename(self):
        """функция is_filename тест на ошибки и на совпадения."""

        self.assertRaises(ValueError, lambda: is_filename("file.not"))
        self.assertRaises(ValueError, lambda: is_filename("file.txt"))
        self.assertRaises(ValueError, lambda: is_filename("file.jpg"))
        self.assertRaises(ValueError, lambda: is_filename("filepng"))
        self.assertTrue(is_filename("file.png"))

    def test_ping_dir(self):
        """Функция ping_dir существование папки plots не обязательно."""

        if not os.path.isdir(PLOTS_PATH):
            self.assertTrue(ping_dir())
        self.assertFalse(ping_dir())

    def test_get_json_datafile(self):
        """Ф
        ункция get_json_datafile проверка загрузки файла,
        так же существует "Долгая" проверка ошибки загрузки.
        """

        if os.path.isfile(TEMP_FILE_NAME):
            os.remove(TEMP_FILE_NAME)
        self.assertFalse(
            get_json_datafile("https://github.com/Dmitriy1101/test_12_05_2024/settings")
        )
        self.assertTrue(get_json_datafile(URL))
        self.assertTrue(os.path.isfile(TEMP_FILE_NAME))

    def test_ping_file(self):
        """
        Функция def test_ping_file создаём тестовый файл загружая в него данные,
        пингуем, в конце удаляем.
        """

        test_file = Path(PLOTS_PATH, "test_file.png")
        if not os.path.isfile(test_file):
            self.assertTrue(get_json_datafile(URL))
            os.replace(TEMP_FILE_NAME, test_file)
        self.assertEqual(str(test_file), ping_file(test_file.name))
        os.remove(test_file)

    def test_is_columns(self):
        """
        Функция is_columns сверка значений с результатом.
        """

        test_data_list = ["name", "surname", "some_data", "some_dude"]
        self.assertEqual(
            ["surname", "some_data", "some_dude"].sort(),
            is_columns(tested_data=test_data_list, correct_data=test_data_list).sort(),
        )
        self.assertEqual(
            ["some_data", "surname"].sort(),
            is_columns(
                tested_data=["some_data", "surname"], correct_data=test_data_list
            ).sort(),
        )
        self.assertEqual(
            ["surname"].sort(),
            is_columns(
                tested_data=["not_some_data", "surname"], correct_data=test_data_list
            ).sort(),
        )
        self.assertEqual(
            ["surname", "some_data", "some_dude"].sort(),
            is_columns(tested_data=[], correct_data=test_data_list).sort(),
        )
        self.assertRaises(
            ValueError,
            lambda: is_columns(
                tested_data=["not_some_data", "not_surname"],
                correct_data=test_data_list,
            ),
        )
        self.assertRaises(
            ValueError,
            lambda: is_columns(tested_data=["name"], correct_data=test_data_list),
        )

    def test_draw_plots(self):
        """
        Основная функция draw_plots тестируем на ошибки, создание тестовога файла,
        тестовый файл в конце удаляем.
        """

        self.assertTrue(get_json_datafile(URL))
        test_file = "test_file.png"
        self.assertRaises(
            ValueError,
            lambda: draw_plots(file_name=test_file, first_index=200, last_index=100),
        )
        self.assertRaises(
            ValueError,
            lambda: draw_plots(file_name=test_file, first_index=100, last_index=100),
        )
        self.assertRaises(
            ValueError,
            lambda: draw_plots(
                file_name=test_file, first_index=100, last_index=200, columns=""
            ),
        )
        if os.path.isfile(n := Path(PLOTS_PATH, test_file)):
            os.remove(n)

        self.assertEqual(str(PLOTS_PATH), draw_plots(file_name=test_file))
        self.assertTrue(os.path.isfile(Path(PLOTS_PATH, test_file)))

        if os.path.isfile(n := Path(PLOTS_PATH, test_file)):
            os.remove(n)
