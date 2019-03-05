import logging
from pathlib import Path
import os
import re


class GradeBook:
    """Creates and manages a project's grade book."""

    def __init__(self, proctor_working_dir, project_name):
        self._logger = logging.getLogger("proctor")
        self._file_name = self._init_file_name(proctor_working_dir, project_name)
        self._cols = ['email', 'is_onetime', 'latest_commit', 'days', 'hours', 'mins',
                      'internal_test ratio', 'external_test_ratio']

    def _init_file_name(self, proctor_working_dir, project_name):
        gradebook_name = f'{project_name}-grades-1.csv'
        path = Path(os.sep.join([proctor_working_dir, gradebook_name]))
        while path.exists():
            path = self._get_next_file_name(path)
        print("Final file name = {}".format(str(path)))

    def _get_next_file_name(self, path):
        pattern = r'-grades-(\d+)'
        spath = str(path)
        match = re.search(pattern, spath)
        if match:
            current_file_version = int(match.groups(1)[0])
            new_file_version = current_file_version + 1
            spath = spath.replace(str(current_file_version), str(new_file_version))
        return Path(spath)


