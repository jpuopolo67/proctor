
import os
import subprocess
import logging
import re
from datetime import datetime as dt
from pathmgr import PathManager

# TODO: Add "run external unit tests" functionality to the class

class Grader:
    """Runs units tests using JUnit and determines the ratio of passed/total, e.g., 10/15"""

    def __init__(self, builder, gradebook):
        self._logger = logging.getLogger("proctor")
        self._builder = builder
        self._gradebook = gradebook

    def grade(self, email, project_name, dir_to_grade, project_due_dt, latest_commit_dt):
        """Grades the project for the given project owner as specified by the email."""

        is_ontime, days, hours, mins = self._get_dt_diff_human_readable(project_due_dt, latest_commit_dt)

        grade_info = {'project_name': project_name, 'email': email,
                      'due_dt': project_due_dt, 'latest_commit_dt': latest_commit_dt,
                      'is_ontime': is_ontime, 'days': days, 'hours': hours, 'mins': mins}

        errors = self._builder.build_source(email, project_name, dir_to_grade)
        grade_info.update({'source_builds': errors == 0} )

        errors = self._builder.build_tests(email, project_name, dir_to_grade)
        grade_info.update({'tests_build': errors == 0})

        test_class_name = PathManager.get_project_student_test_class(project_name)
        internal_test_ratio = self._run_project_unit_tests(email, project_name, dir_to_grade, test_class_name)

        grade_info.update({'internal_test_ratio': internal_test_ratio})
        grade_info.update({'external_test_ratio': 0.0})
        grade_info.update({'grade': 'TBD'} )
        grade_info.update({'notes': ''} )

        self._gradebook.record_grade(grade_info)

    def _run_project_unit_tests(self, email, project_name, dir_to_grade, test_class_name):
        self._logger.info(f'Running tests: {email}{os.sep}{project_name}{os.sep}{test_class_name}')

        src_dir = PathManager.get_project_src_dir_name(project_name)
        path_dir = os.sep.join([str(dir_to_grade), src_dir])
        full_classpath = PathManager.get_full_classpath(java_cp=f'.:{path_dir}', junit_cp=None)

        tests_package = PathManager.get_project_tests_package(project_name)
        student_test_class = PathManager.get_project_student_test_class(project_name)
        test_suite_class = '.'.join([tests_package, student_test_class])

        result = subprocess.run(
            ['java', '-cp', full_classpath, 'org.junit.runner.JUnitCore', test_suite_class],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sresult = result.stdout.decode('utf-8')

        # Pull out the return code: 0 = all tests successful, non-0 means there were were errors
        if result.returncode == 0:
            pattern = "OK \((\d+) tests\)"
            m = re.search(pattern, sresult)
            tests_passed = m.group(1)
            self._logger.info(f'All tests passed: {tests_passed} / {tests_passed}')
            internal_test_ratio = 1.0
        else:
            pattern = "Tests run: (\d+),  Failures: (\d+)"
            m = re.search(pattern, sresult)
            tests_run = int(m.group(1))
            tests_failed = int(m.group(2))
            tests_passed = tests_run - tests_failed
            internal_test_ratio = tests_passed / tests_run
            self._logger.info(f'Test results: {tests_passed} / {tests_run}: {internal_test_ratio}')

        return internal_test_ratio

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

