import argparse
import fnmatch
from os import getcwd, listdir, makedirs, rename, remove, rmdir, walk
from os.path import exists, isdir, getsize, join
from sys import exit
from shutil import rmtree, move, copy2, copytree


"""Размеры файлов"""


def human_readable_size(size):
    if size < 1024:
        return f'{size} Б'
    elif size < 1024**2:
        return f'{size / 1024:.1f} КБ'
    elif size < 1024**3:
        return f'{size / 1024**2:.1f} МБ'
    else:
        return f'{size / 1024**3:.1f} ГБ'


"""Метод для склонения"""


def pluralize(number, form1, form2, form3):
    n = number % 100
    n1 = n % 10

    if 10 < n < 20:
        return form3
    if n1 == 1:
        return form1
    if 2 <= n1 <= 4:
        return form2
    return form3


"""Реализация команды create для создания файлов или папок"""


def create_file_or_dir(type_obj, name, path='.'):
    try:
        if type_obj == 'file':
            full_path_file = join(path, name)
            if not exists(full_path_file):
                open(full_path_file, 'w+').close()
                print(f'Файл успешно создан в {path}')
                return True
            else:
                print('Файл уже существует!')
                return False
        elif type_obj == 'dir':
            full_path_file = join(path, name)
            if not exists(full_path_file):
                makedirs(full_path_file, exist_ok=True)
                print(f'Директория успешно создана в {path}')
                return True
            else:
                print('Директория уже существует!')
                return False
    except PermissionError:
        print(f'Ошибка! Нет прав для создания в {path}')
        return False
    except OSError as e:
        print(f'Ошибка создания {e}')
        return False


def delete_file(path, name):
    try:
        remove(path)
        print('Файл успешно удален!')
    except PermissionError:
        print(f'Нет прав на удаление файла {name}')
        exit(1)
    except OSError as e:
        print(f'При попытке удаления {name},'
              f' возникла ошибка: {e}')
        exit(1)


def delete_empty_dir(path, name):
    try:
        rmdir(path)
        print('Директория успешно удалена!')
    except PermissionError:
        print(f'Нет прав на удаление директории {name}')
        exit(1)
    except OSError as e:
        print(f'При попытке удаления {name},'
              f' возникла ошибка: {e}')
        exit(1)


def delete_recursive_dir(path, name):
    try:
        rmtree(path)
        print('Директория успешно удалена!'
              '(Вместе c содержимым)!')
    except PermissionError:
        print(f'Нет прав на удаление директории {name}')
        exit(1)
    except OSError as e:
        print(f'При попытке удаления {name},'
              f' возникла ошибка: {e}')
        exit(1)


def check_user_input(name):
    print(f'Вы действительно хотите удалить {name}?'
          f' Введите y/n, д/н для подтверждения:')
    user_input = input()
    while user_input not in ['y', 'n', 'д', 'н']:
        print('Введены некорректные данные!'
              ' Пожалуйста введите y/n, д/н')
        user_input = input()
    return user_input


"""Главный парсер программы"""
parser = argparse.ArgumentParser(description='pyexplorer parser')

"""Парсер для команд"""
subparser = parser.add_subparsers(dest='command', help='Доступные команды')

"""Парсер для list"""
list_parser = subparser.add_parser('list', help='Показать содержимое')

list_parser.add_argument(
    'path',
    type=str,
    nargs='?',
    default='.',
    help='Путь к директории',
)

"""Парсер для create"""
comand_parser = subparser.add_parser(
    'create', help='Создание файла или директории'
)

comand_parser.add_argument(
    'type',
    choices=["file", "dir"],
    help='Тип создаваемого объекта',
)

comand_parser.add_argument(
    'name',
    type=str,
    help='Название файла или директории'
)

comand_parser.add_argument(
    '--path',
    '-p',
    type=str,
    nargs='?',
    default='.',
    help='Где создавать(По умолчанию текущая директория)',
)

"""Парсер для команды rename"""
rename_parser = subparser.add_parser('rename', help='Переименовывает файл',)

rename_parser.add_argument(
    'old_file_name',
    type=str,
    help='Название изменяемого файла',
)

rename_parser.add_argument(
    'new_file_name',
    type=str,
    help='Новое название файла',
)

rename_parser.add_argument(
    '--path',
    '-p',
    type=str,
    default='.',
    nargs='?',
    help='Директория где находится файл (по умолчанию текущая)',
)

delete_parser = subparser.add_parser('delete', help='Удаление файлов/папок')

delete_parser.add_argument(
    'name',
    type=str,
    help='Название удаляемого файла',
)

delete_parser.add_argument(
    '--recursive',
    '-r',
    action='store_true',
    help='Удаление поддиректорий',
)

delete_parser.add_argument(
    '--force',
    '-f',
    action='store_true',
    help='Автомотическое подтверждение удаления',
)

delete_parser.add_argument(
    '--path',
    '-p',
    type=str,
    nargs='?',
    default='.',
    help='Путь удаляемого файла(По умолчанию текущая директория)'
)

"""Парсер для команды move"""
move_parser = subparser.add_parser(
    'move', help='Перемещение файла из src в dst'
)

move_parser.add_argument(
    'name',
    type=str,
    help='Имя перемещаемого файла',
)

move_parser.add_argument(
    'destination',
    type=str,
    help='Куда переместить файл',
)

move_parser.add_argument(
    '--path',
    '-p',
    type=str,
    nargs='?',
    default='.',
    help='Откуда брать файл',
)

copy_parser = subparser.add_parser(
    'copy',
    help='Копирование файла из src в dst',
)

copy_parser.add_argument(
    'source',
    type=str,
    help='Что копировать(файл или папка)',
)

copy_parser.add_argument(
    'destination',
    type=str,
    help='Куда копировать',
)

copy_parser.add_argument(
    '--recursive',
    '-r',
    action='store_true',
    help='Флаг для рекурсивного копирования',
)

copy_parser.add_argument(
    '--path',
    '-p',
    type=str,
    nargs='?',
    default='.',
    help='Где находится исходный файл',
)

"""Парсер для команды search"""
search_parser = subparser.add_parser(
    'search',
    help='Посик файлов',
)

search_parser.add_argument(
    'pattern',
    type=str,
    help='Шаблон поиска(например, *.txt, file*, report.*)'
)

search_parser.add_argument(
    '--path',
    '-p',
    type=str,
    nargs='?',
    default='.',
    help='Где искать(по умолчанию текущая директория)'
)

search_parser.add_argument(
    '--recursive',
    '-r',
    action='store_true',
    help='Ключ для рекурсивного поиска'
)

args = parser.parse_args()

# Логика команды list
if args.command == 'list':
    if args.path:
        current_path = args.path
        print(f'Вы находитесь в {current_path}')
    else:
        current_path = getcwd()
        print(f'Вы находитесь в {current_path}')
    if not exists(current_path):
        print('Текущего пути не существует!')
    else:
        print('Текущий путь существует!')
        if not isdir(current_path):
            print('Путь не является директорией!')
        else:
            print('Путь является директорией!')
        list_dir = listdir(current_path)
        list_dir = sorted(list_dir)
        total_files = 0
        total_dirs = 0
        total_size = 0
        max_name_len = max(len(item) for item in list_dir) if list_dir else 0

        for item in list_dir:
            full_path = join(current_path, item)
            if isdir(full_path):
                total_dirs += 1
                print(f'[DIR]  {item:{max_name_len}}/')
            else:
                try:
                    size_file = getsize(full_path)
                    total_files += 1
                    total_size += size_file
                    print(f'[FILE] {item:{max_name_len}}'
                          f'{human_readable_size(size_file):>10}')
                except PermissionError:
                    print(f'[FILE] {item:{max_name_len}}'
                          f'{"Нет прав":>10}')

                except OSError:
                    print(f'[FILE] {item:{max_name_len}}'
                          f'{"Ошибка":>10}')

        files_word = pluralize(total_files, "файл", "файла", "файлов")
        folders_word = pluralize(total_dirs, "папка", "папки", "папок")
        print(f'Итого: {total_files} {files_word}, '
              f'{total_dirs} {folders_word}, общий размер: '
              f'{human_readable_size(total_size)}')
# Вызов метода для команды create
elif args.command == 'create':
    create_file_or_dir(args.type, args.name, args.path)
# Логика команды rename
elif args.command == 'rename':
    old_name = args.old_file_name
    new_name = args.new_file_name
    path_for_file = args.path
    full_old_path = join(args.path, args.old_file_name)
    if not exists(full_old_path):
        print(f'{old_name} не существует!')
        exit(1)
    else:
        full_new_path = join(path_for_file, new_name)
        if exists(full_new_path):
            print(f'{new_name} уже существует!')
            exit(1)
        else:
            try:
                rename(full_old_path, full_new_path)
                print('Файл успешно переименован!')
            except PermissionError:
                print('Нет прав на переименование!')
                exit(1)
            except OSError as e:
                print(f'При попытке переименования возникла ошибка {e}')
                exit(1)
# Логика команды delete
elif args.command == 'delete':
    delete_name = args.name
    full_delete_path = join(args.path, delete_name)
    if not exists(full_delete_path):
        print(f'{delete_name} Не существует!')
        exit(1)
    else:
        if not isdir(full_delete_path):
            if args.force:
                delete_file(full_delete_path, delete_name)
            else:
                if check_user_input(delete_name) in ['y', 'д']:
                    delete_file(full_delete_path, delete_name)
                else:
                    exit(0)
        else:
            if len(listdir(full_delete_path)) == 0:
                if args.force:
                    delete_empty_dir(full_delete_path, delete_name)
                else:
                    if check_user_input(delete_name) in ['y', 'д']:
                        delete_empty_dir(full_delete_path, delete_name)
                    else:
                        exit(0)
            else:
                if args.recursive:
                    if args.force:
                        delete_recursive_dir(full_delete_path, delete_name)
                    else:
                        if check_user_input(delete_name) in ['y', 'д']:
                            delete_recursive_dir(full_delete_path, delete_name)
                        else:
                            exit(0)
                else:
                    print('Невозможно удалить директорию без'
                          ' ключа --recursive или -r!')
# Логика команды move
elif args.command == 'move':
    source_name = args.name
    destination = args.destination
    source_path = args.path

    full_source = join(source_path, source_name)

    if not exists(full_source):
        print(f'Ошибка: файл {source_name} не существует')
        exit(1)

    if destination.endswith('/') or destination.endswith('\\'):
        dest_dir = destination.rstrip('/\\')
        if not exists(dest_dir):
            print(f'Ошибка: папка {dest_dir} не существует')
            exit(1)
        if not isdir(dest_dir):
            print(f'Ошибка: {dest_dir} не является папкой')
            exit(1)
        filename = source_name
        final_destination = join(dest_dir, filename)
    else:
        final_destination = destination

    if exists(final_destination):
        print(f'Ошибка: {final_destination} уже существует')
        exit(1)

    try:
        move(full_source, final_destination)
        print(f'Успешно перемещено: {source_name} -> {final_destination}')
    except PermissionError:
        print('Ошибка: нет прав для перемещения')
        exit(1)
    except OSError as e:
        print(f'Ошибка перемещения: {e}')
        exit(1)
# Локгика команды copy
elif args.command == 'copy':
    copy_name = args.source
    destination = args.destination
    source_path = args.path
    full_copy_path = join(source_path, copy_name)
    if not exists(full_copy_path):
        print(f'Файл {copy_name}, не существует!')
        exit(1)
    else:
        if destination.endswith('/') or destination.endswith('\\'):
            dest_dir = destination.rstrip('/\\')
            if not exists(dest_dir):
                print(f'Директории {dest_dir} не существует')
                exit(1)
            if not isdir(dest_dir):
                print(f'{dest_dir}, не является директорией!')
                exit(1)
            final_destination = join(dest_dir, copy_name)
        else:
            final_destination = destination

        if exists(final_destination):
            print(f'{final_destination} уже существует!')
            exit(1)

        if not isdir(full_copy_path):
            try:
                copy2(full_copy_path, final_destination)
                print(f'Файл {copy_name} успешно'
                      f' скопирован в {final_destination}!')
            except PermissionError:
                print('Ошибка: нет прав для копирования')
                exit(1)
            except OSError as e:
                print(f'В процессе копирования возникла ошибка: {e}')
                exit(1)
        else:
            if args.recursive:
                try:
                    copytree(full_copy_path, final_destination)
                    print(f'Файл {copy_name} успешно'
                          f' скопирован в {final_destination}!')
                except PermissionError:
                    print('Ошибка: нет прав для копирования')
                    exit(1)
                except OSError as e:
                    print(f'В процессе копирования возникла ошибка: {e}')
                    exit(1)
            else:
                print('Для папок используйте ключ --recursive или -r')
# Логика команды search
elif args.command == 'search':
    pattern = args.pattern
    search_path = args.path
    count_find_files = 0

    if not exists(search_path):
        print(f'Ошибка: путь "{search_path}" не существует!')
        exit(1)

    if not args.recursive:
        try:
            search_list = listdir(search_path)
            for element in search_list:
                if fnmatch.fnmatch(element, pattern):
                    full_search_path = join(search_path, element)
                    count_find_files += 1

                    if isdir(full_search_path):
                        print(f'[DIR]  {full_search_path}/')
                    else:
                        try:
                            size = getsize(full_search_path)
                            print(f'[FILE] {full_search_path}'
                                  f' ({human_readable_size(size)})')
                        except (PermissionError, OSError):
                            print(f'[FILE] {full_search_path}'
                                  f' (не удалось получить размер)')

            if count_find_files > 0:
                file_word = pluralize(count_find_files, 'объект',
                                      'объекта', 'объектов')
                print(f'\nВсего {file_word} найдено: {count_find_files}')
            else:
                print(f'Файлы по шаблону "{pattern}"'
                      f' не найдены в "{search_path}"')

        except PermissionError:
            print('Ошибка: нет прав для чтения папки!')
            exit(1)
        except OSError as e:
            print(f'Ошибка поиска: {e}')
            exit(1)

    else:
        try:
            for current_dir, subdirs, files in walk(search_path):
                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        count_find_files += 1
                        full_finded_file = join(current_dir, file)
                        try:
                            size = getsize(full_finded_file)
                            print(f'[FILE] {full_finded_file}'
                                  f'({human_readable_size(size)})')
                        except (PermissionError, OSError):
                            print(f'[FILE] {full_finded_file}'
                                  '(не удалось получить размер)')

                for dir_name in subdirs:
                    if fnmatch.fnmatch(dir_name, pattern):
                        count_find_files += 1
                        full_finded_dir = join(current_dir, dir_name)
                        print(f'[DIR]  {full_finded_dir}/')

            if count_find_files > 0:
                file_word = pluralize(count_find_files, 'объект',
                                      'объекта', 'объектов')
                print(f'\nВсего {file_word} найдено: {count_find_files}')
            else:
                print(f'Файлы по шаблону "{pattern}" не найдены в'
                      f'"{search_path}" и подпапках')

        except PermissionError:
            print('Ошибка: нет прав для чтения папки!')
            exit(1)
        except OSError as e:
            print(f'Ошибка поиска: {e}')
            exit(1)
