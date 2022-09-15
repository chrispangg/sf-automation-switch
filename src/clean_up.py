import os
import shutil

class CleanUpUtil:

    def delete(self, path):
        """path could either be relative or absolute. """
        # check if file or directory exists
        if os.path.isfile(path) or os.path.islink(path):
            # remove file
            os.remove(path)
        elif os.path.isdir(path):
            # remove directory and all its content
            shutil.rmtree(path)
        else:
            raise ValueError("Path {} is not a file or dir.".format(path))
