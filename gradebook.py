import logging
from pathlib import Path
import os
import re
import csv


class GradeBook:
    """Creates and manages a project's grade book."""

    COLS = ['project_name', 'email', 'due_dt', 'latest_commit_dt', 'is_ontime', 'days', 'hours', 'mins',
            'source_builds', 'tests_build', 'internal_test_ratio', 'external_test_ratio', 'grade', 'notes']

    def __init__(self, proctor_working_dir, project_name, project_due_dt):
        self._logger = logging.getLogger("proctor")
        self._project_name = project_name
        self._project_due_dt = project_due_dt
        self._file_name = self._init_file_name(proctor_working_dir, project_name)
        self._gradesheet = [GradeBook.COLS]

    def _init_file_name(self, proctor_working_dir, project_name):
        gradebook_name = os.sep.join([proctor_working_dir, project_name, 'grades-1.csv'])
        path = Path(gradebook_name)
        while path.exists():
            path = self._get_next_file_name(path)
        return str(path)

    def local_project_not_found(self, email):
        self._record_grade_not_found(email, 'Project not found locally. Cloned correctly?')

    def server_project_not_found(self, email):
        self._record_grade_not_found(email, 'Project not found on server. Handed in?')

    def commit_not_found(self, email):
        self._record_grade_not_found(email, 'Commit not found on server. Pushed?')

    def _record_grade_not_found(self, email, notes):
        self._gradesheet.append([self._project_name, email, self._project_due_dt, 'N/A',
                                 False, 0, 0, 0, False, False, 0.0, 0.0, 'TBD', notes])

    def record_grade(self, ginfo):
        grade_record = []
        for col in GradeBook.COLS:
            grade_record.append(ginfo[col])
        self._gradesheet.append(grade_record)

    def save(self):
        try:
            with open(self._file_name, mode='wt', encoding='utf-8') as thefile:
                writer = csv.writer(thefile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for grade_record in self._gradesheet:
                    writer.writerow(grade_record)
        except FileNotFoundError:
            self._logger.warning("FAILED OPEN: Cannot open gradebook file {}. Check that directory exists."
                                 .format(self._file_name))

    def _get_next_file_name(self, path):
        pattern = r'grades-(\d+)'
        spath = str(path)
        match = re.search(pattern, spath)
        if match:
            current_file_version = int(match.groups(1)[0])
            new_file_version = current_file_version + 1
            spath = spath.replace(str(f'grades-{current_file_version}'), str(f'grades-{new_file_version}'))
        return Path(spath)
