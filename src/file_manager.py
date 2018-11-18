import os
import hashlib


class FileManager():
    """
    Class interacts with the physical storage.
    """

    def __init__(self, path_store):
        if not os.path.exists(path_store):
            os.makedirs(path_store)
        elif os.path.isfile(path_store):
            pass
            # print(f"Error, path {path_store} is file. Past must directory")

        self.work_directory = path_store
        self.letter = 2

    def download(self, hash_file: str):
        """
        Get file from stogare
        :param hash_file: name file
        :return: file
        """
        name_directory = hash_file[0:self.letter]
        # если это папка
        if os.path.isdir(os.path.join(self.work_directory, name_directory)):
            # если это файл
            if os.path.isfile(os.path.join(self.work_directory, name_directory, hash_file)):
                return os.path.join(self.work_directory, name_directory), hash_file

        return None, None

    def delete(self, hash_file: str):
        """
        Delete file from storage
        :param hash_file:
        :return: bool
        """
        name_directory = hash_file[0:self.letter]

        # если это папка
        if os.path.isdir(os.path.join(self.work_directory, name_directory)):
            # если это файл
            if os.path.isfile(os.path.join(self.work_directory, name_directory, hash_file)):
                # удаляем файл
                try:
                    os.remove(os.path.join(self.work_directory, name_directory, hash_file))
                except:
                    return False

                try:
                    os.rmdir(os.path.join(self.work_directory, name_directory))
                except:
                    pass

                return True

        # print(f"Error, file with hash {hash_file} don't exists")
        return False

    def upload(self, file):
        """
        Create file in storge
        :param file:
        :return: hash
        """
        # получаем хэш файла
        hash_file = hashlib.md5(file.read()).hexdigest()

        # получаем имя дериктории
        name_directory = hash_file[0:self.letter]

        # если существует
        if os.path.exists(os.path.join(self.work_directory, name_directory)):
            # если пути не существует
            if os.path.exists(os.path.join(self.work_directory, name_directory, hash_file)):
                return None

        else:
            # создаем папку
            os.makedirs(os.path.join(self.work_directory, name_directory))

        # сохраняем в файл
        file.stream.seek(0)
        file.save(os.path.join(self.work_directory, name_directory, hash_file))
        return hash_file
