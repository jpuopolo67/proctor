import logging
from pathlib import Path
import os
import re
import csv


class GradeBook:
    """Creates and manages a project's grade book."""

    def __init__(self, proctor_working_dir, project_name):
        self._logger = logging.getLogger("proctor")
        self._file_name = self._init_file_name(proctor_working_dir, project_name)
        self._cols = ['email', 'due_dt', 'latest_commit_dt', 'is_onetime', 'days', 'hours', 'mins',
                      'internal_test ratio', 'external_test_ratio', 'grade']
        self._thefile = None

    def _init_file_name(self, proctor_working_dir, project_name):
        gradebook_name = os.sep.join([proctor_working_dir, project_name, 'grades-1.csv'])
        path = Path(gradebook_name)
        while path.exists():
            path = self._get_next_file_name(path)
        return str(path)

    def _get_next_file_name(self, path):
        pattern = r'grades-(\d+)'
        spath = str(path)
        match = re.search(pattern, spath)
        if match:
            current_file_version = int(match.groups(1)[0])
            new_file_version = current_file_version + 1
            spath = spath.replace(str(f'grades-{current_file_version}'), str(f'grades-{new_file_version}'))
        return Path(spath)

    def open(self):
        try:
            self._thefile = open(self._file_name, mode='wt', encoding='utf-8')
            self._gb_writer = csv.writer(self._thefile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            self._gb_writer.writerow(self._cols)
        except FileNotFoundError:
            self._logger.warning("FAILED OPEN: Cannot open gradebook file {}. Check that directory exists."
                                 .format(self._file_name))

    def record_grade(self, email, project_due_date, latest_commit_date, is_ontime, days, hours, mins, grade):
        self._gb_writer.writerow([email, project_due_date, latest_commit_date, is_ontime,
                                  days, hours, mins, 1.0, 1.0, grade])

    def close(self):
        self._thefile.close()

