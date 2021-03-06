#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Программа удаления файлов журналов, создаваемых python программами.
"""

import sys
import os
import os.path
import traceback
import locale

try:
    if sys.version_info.major == 2:
        import ConfigParser
    elif sys.version_info.major == 3:
        import configparser as ConfigParser
except ImportError:
    print(u'ERROR! Import error ConfigParser module')
    exit(0)

try:
    import dialog
except ImportError:
    print(u'ERROR. Import error python-dialog')
    exit(0)


__version__ = (0, 1, 1, 1)

# Кодировка коммандной оболочки по умолчанию
DEFAULT_ENCODING = sys.stdout.encoding if sys.platform.startswith('win') else locale.getpreferredencoding()

# Цвета в консоли
RED_COLOR_TEXT = '\x1b[31;1m'       # red
GREEN_COLOR_TEXT = '\x1b[32m'       # green
YELLOW_COLOR_TEXT = '\x1b[33;1m'    # yellow
BLUE_COLOR_TEXT = '\x1b[34m'        # blue
PURPLE_COLOR_TEXT = '\x1b[35m'      # purple
CYAN_COLOR_TEXT = '\x1b[36m'        # cyan
WHITE_COLOR_TEXT = '\x1b[37m'       # white
NORMAL_COLOR_TEXT = '\x1b[0m'       # normal


def get_default_encoding():
    """
    Определить актуальную кодировку для вывода текста.
    @return: Актуальная кодировка для вывода текста.
    """
    return DEFAULT_ENCODING


def print_color_txt(sTxt, sColor=NORMAL_COLOR_TEXT):
    """
    Печать цветного текста.
    @param sTxt: Текст.
    @param sColor: Консольный цвет.
    """
    if sys.platform.startswith('win'):
        # Для Windows систем цветовая раскраска отключена
        txt = sTxt
    else:
        # Добавление цветовой раскраски
        txt = sColor + sTxt + NORMAL_COLOR_TEXT
    print(txt)


def debug(sMsg=u''):
    """
    Вывести ОТЛАДОЧНУЮ информацию.
    @param sMsg: Текстовое сообщение.
    """
    print_color_txt('DEBUG. ' + sMsg, BLUE_COLOR_TEXT)


def info(sMsg=u''):
    """
    Вывести ТЕКСТОВУЮ информацию.
    @param sMsg: Текстовое сообщение.
    """
    print_color_txt('INFO. ' + sMsg, GREEN_COLOR_TEXT)


def error(sMsg=u''):
    """
    Вывести информацию ОБ ОШИБКЕ.
    @param sMsg: Текстовое сообщение.
    """
    print_color_txt('ERROR. ' + sMsg, RED_COLOR_TEXT)


def warning(sMsg=u''):
    """
    Вывести информацию ОБ ПРЕДУПРЕЖДЕНИИ.
    @param sMsg: Текстовое сообщение.
    """
    print_color_txt('WARNING. ' + sMsg, YELLOW_COLOR_TEXT)


def fatal(sMsg=u''):
    """
    Вывести информацию ОБ ОШИБКЕ.
    @param sMsg: Текстовое сообщение.
    """
    trace_txt = traceback.format_exc()

    try:
        msg = sMsg + u'\n' + trace_txt
    except UnicodeDecodeError:
        if not isinstance(sMsg, str):
            sMsg = str(sMsg)
        if not isinstance(trace_txt, str):
            trace_txt = str(trace_txt)
        msg = sMsg + u'\n' + trace_txt

    print_color_txt('FATAL. ' + msg, RED_COLOR_TEXT)


def INI2Dict(sINIFileName):
    """
    Представление содержимого INI файла в виде словаря.
    @type sINIFileName: C{string}
    @param sINIFileName: Полное имя файла настроек.
    @return: Заполненный словарь или None в случае ошибки.
    """
    ini_file = None
    try:
        if not os.path.exists(sINIFileName):
            warning(u'INI file <%s> not exists' % sINIFileName)
            return None

        # Создать объект конфигурации
        ini_parser = ConfigParser.ConfigParser()
        ini_file = open(sINIFileName, 'r')
        ini_parser.readfp(ini_file)
        ini_file.close()
        ini_file = None

        # Заполнение словаря
        dct = {}
        sections = ini_parser.sections()
        for section in sections:
            params = ini_parser.options(section)
            dct[section] = {}
            for param in params:
                param_str = ini_parser.get(section, param)
                try:
                    # Возможно в виде параметра записан словарь/список/None/число и т.д.
                    param_value = eval(param_str)
                except:
                    # Нет вроде строка
                    param_value = param_str
                dct[section][param] = param_value

        return dct
    except:
        if ini_file:
            ini_file.close()
        fatal(u'Conver INI file <%s> to dictionary' % sINIFileName)
    return None


DEFAULT_BACKGROUND_DIALOG_TITLE = '---'    # 'Очистка диска от файлов журналов'

DEFAULT_DLG_HEIGHT = 30
DEFAULT_DLG_WIDTH = 100
DEFAULT_LIST_ITEM_COUNT = 20


class icCheckListDialog(dialog.Dialog):
    """
    Диалоговое окно со списком чекбоксов.
    """
    def __init__(self, title=DEFAULT_BACKGROUND_DIALOG_TITLE,
                 height=DEFAULT_DLG_HEIGHT, width=DEFAULT_DLG_WIDTH,
                 item_count=DEFAULT_LIST_ITEM_COUNT, items=(),
                 *args, **kwargs):
        dialog.Dialog.__init__(self, *args, **kwargs)

        self.title = title
        self.width = width
        self.height = height

        self.item_count = item_count
        self.items = items

        try:
            self.set_background_title(title)
        except AttributeError:
            # Для поддержки более ранних версий
            self.setBackgroundTitle(title)

    def main(self):
        """
        Запуск диалога.
        @return:
        """
        try:
            if self.items:
                self.result = self.checklist(text=self.title, width=self.width, height=self.height,
                                             list_height=self.item_count, choices=self.items)
            else:
                self.result = (self.msgbox(u'ВНИМАНИЕ! Пустой список выбора',
                               width=self.width, height=self.height, title=self.title), None)
            return self.result[0] == self.OK, self.result[1:]
        except:
            fatal(u'Ошибка запуска диалогового окна')
        return False, None


def do_checklist(title=DEFAULT_BACKGROUND_DIALOG_TITLE,
                 height=DEFAULT_DLG_HEIGHT, width=DEFAULT_DLG_WIDTH,
                 list_height=DEFAULT_LIST_ITEM_COUNT, items=()):
    choice_count = int(len(items)/3)
    choices = [(items[i*3], items[i*3+1],
                items[i*3+2]) for i in range(choice_count)]
    return icCheckListDialog(title=title, width=width, height=height,
                             item_count=list_height, items=choices)


def main():
    """
    Главная запускаемая процедура.
    """
    # Читаем данные из настроечного файла
    ini_filename = os.path.join(os.path.dirname(__file__), 'settings.ini')
    ini_dict = INI2Dict(ini_filename)

    dlg = do_checklist(items=('txt1', 'text1', 'on', 'text2', 'txt2', 'on'))
    result = dlg.main()
    debug(u'Check list <%s>' % str(result))


if __name__ == '__main__':
    main()
