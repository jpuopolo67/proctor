
from proctorconfig import ProctorConfig
from gradebook import GradeBook
from pathlib import Path
from datetime import datetime as dt
import os
import subprocess

class Grader:
    """Runs units tests using JUnit and determines the ratio of passed/total, e.g., 10/15"""
    def __init__(self, gradebook):
        self._gradebook = gradebook
        self._gradebook.open()

    def grade(self, email, project_name, dir_to_grade, project_due_dt, latest_commit_dt):
        """Grades the project for the given project owner as specificed by the email."""
        is_ontime, days, hours, mins = self._get_dt_diff_human_readable(project_due_dt, latest_commit_dt)

        self._compile_source(project_name, dir_to_grade)
        self._run_project_unit_tests(project_name, dir_to_grade)

        self._gradebook.record_grade(email, project_due_dt, latest_commit_dt,
                                     is_ontime, days, hours, mins, 'TBD')
        pass


    def _compile_source(self, project_name, dir_to_grade):
        # TODO: Compile all source files, capture output, parse to make sure all OK
        src_path = ProctorConfig.get_config_value(project_name, 'src_path')
        full_path = dir_to_grade / src_path

        java_files = full_path.rglob("*.java")
        #result = subprocess.call(['javac', cmd])
        pass


    def _run_project_unit_tests(self, project_name, dir_to_grade):
        # TODO: Compile all test files
        # TODO: Run the tests against the compiled source
        # TODO: Capture test output, parse and evaluate

        print(f"Run unit tests for {dir_to_grade} here!")
        pass


    def _get_dt_diff_human_readable(self, project_due_date, latest_commit_date):

        # Exmaple of project date returned from server: 2019-03-03T23:39:40.000-05:00
        dt_due = dt.strptime(project_due_date, "%Y-%m-%dT%H:%M:%S%z")

        # Remove last ':' so that strptime can parse correcly
        latest_commit_date = latest_commit_date[::-1].replace(':', '', 1)[::-1]
        dt_latest = dt.strptime(latest_commit_date, "%Y-%m-%dT%H:%M:%S.%f%z")

        # Get the datetime difference and return a tuple in days, hrs, mins
        date_diff = dt_due - dt_latest
        total_sec = date_diff.total_seconds()
        is_ontime = total_sec >= 0
        total_sec = abs(total_sec)
        days, hours, mins = self._convert_secs_to_days_hrs_mins(total_sec)
        return (is_ontime, days, hours, mins)


    def _convert_secs_to_days_hrs_mins(self, total_sec):
        days = total_sec // (24 * 3600)
        total_sec = total_sec % (24 * 3600)
        hours = total_sec // 3600
        total_sec %= 3600
        mins = total_sec // 60
        return (days, hours, mins)


    def __del__(self):
        self._gradebook.close()





