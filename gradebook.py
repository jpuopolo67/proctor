import logging
import os
import re
import csv
from pathlib import Path

class GradeBook:
    """Creates and manages a project's gradebook."""

    # Column headers for the gradebook, which is saved as a CSV file.
    COLS = ['project_name', 'email', 'due_dt', 'latest_commit_dt', 'is_ontime', 'days', 'hours', 'mins',
            'source_builds', 'student_tests_build', 'student_tests_ratio', 'instructor_tests_ratio', 'grade', 'notes']

    def __init__(self, proctor_working_dir, project_name, project_due_dt):
        """Initializes the GradeBook.
        :param proctor_working_dir: Proctor's working directory
        :param project_name: Name of project being graded
        :param project_due_dt: Project's due datetime in UTC"""
        self._logger = logging.getLogger("proctor")
        self._project_name = project_name
        self._project_due_dt = project_due_dt
        self._file_name = self._init_file_name(proctor_working_dir, project_name)
        self._gradesheet = [GradeBook.COLS]

    def get_file_name(self):
        """Returns the gradebook's file name.
        :returns The name of the gradebook file."""
        return self._file_name

    def local_project_not_found(self, email):
        """Records a grade record that indicates the project being graded could not be found locally.
        :param email: Project owner's email"""
        self._record_grade_not_found(email, 'Project not found locally. Cloned correctly?')

    def server_project_not_found(self, email):
        """Records a grade record that indicates the project being graded could not be found on the server.
        :param email: Project owner's email"""
        self._record_grade_not_found(email, 'Project not found on server. Handed in?')

    def commit_not_found(self, email):
        """Records a grade record that indicates the project being graded has no server commits.
        :param email: Project owner's email"""
        self._record_grade_not_found(email, 'Commit not found on server. Pushed?')

    def _record_grade_not_found(self, email, notes=''):
        """Writes an 'error' grade record to the memory-based gradebook.
        :param email: Project owner's email
        :param notes: Free-form text comments added to the grade record"""
        self._gradesheet.append([self._project_name, email, self._project_due_dt, 'N/A',
                                 False, 0, 0, 0, False, False, 0.0, 0.0, 'TBD', notes])

    def record_grade(self, ginfo):
        """Writes a grade record to the memory-based gradebook.
        :param ginfo: Dictionary containing the grade record info."""
        grade_record = []
        for col in GradeBook.COLS:
            grade_record.append(ginfo[col])
        self._gradesheet.append(grade_record)

    def save(self):
        """Saves the memory-based gradebook to the local machine as a CSV file."""
        try:
            with open(self._file_name, mode='wt', encoding='utf-8') as thefile:
                writer = csv.writer(thefile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for grade_record in self._gradesheet:
                    writer.writerow(grade_record)
        except FileNotFoundError:
            self._logger.warning("Cannot open gradebook file {}. Check that directory exists."
                                 .format(self._file_name))

    def _init_file_name(self, proctor_working_dir, project_name):
        """Determines the file name under which the gradebook will be stored. The format is grades-N.csv where
        N is the 'version' of the file. This prevents accidental overwrite of an existing gradebook file.
        :param proctor_working_dir: Proctor's working directory
        :param project_name: Project being graded
        :returns The new gradebook's file name."""
        gradebook_name = os.sep.join([proctor_working_dir, project_name, 'grades-1.csv'])
        path = Path(gradebook_name)
        while path.exists():
            path = self._get_next_file_name(path)
        return str(path)

    def _get_next_file_name(self, path):
        """Calculates the next file name by incrementing the 'version'.
        :param path: Path to gradebook file
        :returns Path representing the new gradebook file."""
        pattern = r'grades-(\d+)'
        spath = str(path)
        match = re.search(pattern, spath)
        if match:
            current_file_version = int(match.groups(1)[0])
            new_file_version = current_file_version + 1
            spath = spath.replace(str(f'grades-{current_file_version}'), str(f'grades-{new_file_version}'))
        return Path(spath)
