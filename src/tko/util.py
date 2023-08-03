import tempfile
import os
import shutil


class Util:

    def __init__(self):
        pass

    @staticmethod
    def copy_to_temp(folder):
        temp_dir = tempfile.mkdtemp()
        for file in os.listdir(folder):
            if os.path.isfile(os.path.join(folder, file)):
                shutil.copyfile(os.path.join(folder, file), os.path.join(temp_dir, file))
        return temp_dir
