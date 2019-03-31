import os
import subprocess
import logging
import re
from datetime import datetime as dt
from pathlib import Path
from pathmgr import PathManager


class Grader:
    """Runs units tests using JUnit and determines the ratio of passed/total, e.g., 10/15"""

    def __init__(self, builder, gradebook):
        """Initializes the Grader.
        :param builder: Builder instance that compiles Java source and tests.
        :param gradebook: GradeBook the records and saves the grades per application run."""
        self._logger = logging.getLogger("proctor")
        self._builder = builder
        self._gradebook = gradebook

    def grade(self, email, project_name, dir_to_grade, project_due_dt, latest_commit_dt):
        """Grades a project for the specified owner (email).
        :param email: Project owner's email
        :param project_name: Name of the project being graded
        :param dir_to_grade: Root of directory tree containing project files
        :param project_due_dt: Project due datetime in UTC
        :param latest_commit_dt: Project's most recent commit datetime from server in UTC"""

        # Reference
        # COLS = ['project_name', 'email', 'due_dt', 'latest_commit_dt', 'is_ontime', 'days', 'hours', 'mins',
        #        'source_builds', 'student_tests_build', 'student_test_ratio', 'instructor_test_ratio', 'grade',
        #        'notes']

        # Determines if the project is on time based on due datetime vs. latest commit datetime
        is_ontime, days, hours, mins = self._get_dt_diff_human_readable(project_due_dt, latest_commit_dt)

        # Information that goes into a grade record...
        grade_info = {'project_name': project_name, 'email': email,
                      'due_dt': project_due_dt, 'latest_commit_dt': latest_commit_dt,
                      'is_ontime': is_ontime, 'days': days, 'hours': hours, 'mins': mins}

        # Build source and tests
        errors = self._builder.build_source(email, project_name, dir_to_grade)
        grade_info.update({'source_builds': errors == 0})
        errors = self._builder.build_tests(email, project_name, dir_to_grade)
        grade_info.update({'student_tests_build': errors == 0})

        # Run project unit tests and calculate internal test ratio = passed tests / total tests
        test_class_name = PathManager.get_student_test_class(project_name)
        if test_class_name and len(test_class_name) > 0:
            internal_test_ratio = self._run_project_unit_tests(email, project_name, dir_to_grade, test_class_name)
            grade_info.update({'student_tests_ratio': internal_test_ratio})
        else:
            self._logger.warning('Missing unit test class. No tests specified.')
            grade_info.update({'student_tests_ratio': 'No tests specified. Check configuration file.'})

        # Run instructor (external) unit tests if there is an instructor test class defined in
        # the Proctor configuration file
        #
        # Note: The instructor unit test are assumed to have been compiled and ready to run
        # against the project. We do not build the instructor's tests. This could be added
        # as a feature in the future, should it prove necessary or valuable.

        instructor_test_class_path = PathManager.get_instructor_test_class(project_name)
        self._logger.info(
            f'Running instructor unit tests: {instructor_test_class_path}')

        if instructor_test_class_path and Path(instructor_test_class_path).exists():
            instructor_test_ratio = self._run_instructor_unit_tests(email, project_name, dir_to_grade,
                                                                    instructor_test_class_path)
            grade_info.update({'instructor_tests_ratio': instructor_test_ratio})
        else:
            self._logger.warning('No unit tests specified or unit test class does not exist.')
            grade_info.update({'instructor_tests_ratio': 'No tests specified. Check configuration file.'})

        # Record the results of grading this user's project in the gradebook.
        grade_info.update({'grade': 'TBD'})
        grade_info.update({'notes': ''})
        self._gradebook.record_grade(grade_info)

    def _run_instructor_unit_tests(self, email, project_name, dir_to_grade, test_class_path):
        """Runs the project's unit test. Assumes JUnit as testing framework.
          :param email: Project owner's email
          :param project_name: Project being graded
          :param dir_to_grade: Root of directory tree where project files live
          :param test_class_path: Full path to  the JUnit test suite, e.g., MyTests, sans the .class extention
          :returns Ratio of passed test/all tests as a floating point number. 1.0 means all tests passed."""

        # Determine proper paths for java runtime so that we can find test classes
        src_dir = PathManager.get_project_src_dir_name(project_name)
        path_dir = os.sep.join([str(dir_to_grade), src_dir])
        full_classpath = PathManager.get_full_classpath(java_cp=f'.:{path_dir}:{test_class_path}', junit_cp=None)

        # Run the tests using JUnit's command-line runner
        result = subprocess.run(
            ['java', '-cp', full_classpath, 'org.junit.runner.JUnitCore', test_class_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Process the result of running the tests.
        # Turn the resulting byte stream into a parseable string
        sresult = result.stdout.decode('utf-8')

        # returncode: 0 = all tests successful, non-0 = some errors occurred.
        instructor_tests_ratio = 0.0

        if result.returncode == 0:
            pattern = "OK \((\d+) tests\)"
            m = re.search(pattern, sresult)
            tests_passed = m.group(1)
            self._logger.info(f'All tests passed: {tests_passed} / {tests_passed}')
            instructor_tests_ratio = 1.0
        else:
            pattern = "Tests run: (\d+),  Failures: (\d+)"
            m = re.search(pattern, sresult)
            try:
                tests_run = int(m.group(1))
                tests_failed = int(m.group(2))
                tests_passed = tests_run - tests_failed
            except:
                tests_run = 0

            if tests_run > 0:
                instructor_tests_ratio = tests_passed / tests_run
                self._logger.info(f'Test results: {tests_passed} / {tests_run}: {instructor_tests_ratio}')
            else:
                self._logger.warning("No instructor test were run. Check configuration file and class '{}'"
                                     .format(test_class_path))
        return instructor_tests_ratio

    def _run_project_unit_tests(self, email, project_name, dir_to_grade, test_class_name):
        """Runs the project's unit test. Assumes JUnit as testing framework.
        :param email: Project owner's email
        :param project_name: Project being graded
        :param dir_to_grade: Root of directory tree where project files live
        :param test_class_name: Name of the JUnit test suite, e.g., TestSuite, sans the .class extention
        :returns Ratio of passed test/all tests as a floating point number. 1.0 means all tests passed."""
        self._logger.info(f'Running unit tests: {email}{os.sep}{project_name}{os.sep}{test_class_name}')

        # Determine proper paths
        src_dir = PathManager.get_project_src_dir_name(project_name)
        path_dir = os.sep.join([str(dir_to_grade), src_dir])
        full_classpath = PathManager.get_full_classpath(java_cp=f'.:{path_dir}', junit_cp=None)

        tests_package = PathManager.get_student_tests_package(project_name)
        student_test_class = PathManager.get_student_test_class(project_name)
        test_suite_class = '.'.join([tests_package, student_test_class])

        # Run the tests using JUnit's command-line runner
        result = subprocess.run(
            ['java', '-cp', full_classpath, 'org.junit.runner.JUnitCore', test_suite_class],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Process the result of running the tests.
        # Turn the resulting byte stream into a parseable string
        sresult = result.stdout.decode('utf-8')

        # returncode: 0 = all tests successful, non-0 = some errors occurred.
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
        """Calculates the difference between project due date and user's latest commit date.
        :param project_due_date: Project due datetime in UTC
        :param latest_commit_date: Project's latest commit date on the server in UTC
        :returns Date difference in human-readable parts."""

        # All dates assumes UTC. Exmaple of project date returned from server: 2019-03-03T23:39:40.000-05:00
        dt_due = dt.strptime(project_due_date, "%Y-%m-%dT%H:%M:%S%z")
        latest_commit_date = latest_commit_date[::-1].replace(':', '', 1)[::-1]  # remove trailing ':'
        dt_latest = dt.strptime(latest_commit_date, "%Y-%m-%dT%H:%M:%S.%f%z")  # so that strptime can parse

        # Get the datetime difference and return a tuple in days, hrs, mins
        date_diff = dt_due - dt_latest
        total_sec = date_diff.total_seconds()
        is_ontime = total_sec >= 0
        total_sec = abs(total_sec)
        days, hours, mins = self._convert_secs_to_days_hrs_mins(total_sec)
        return (is_ontime, days, hours, mins)

    def _convert_secs_to_days_hrs_mins(self, total_sec):
        """Converts seconds into days, hours, mins.
        :param total_sec: Total number of seconds to convert to days, hours, mins
        :returns: (days, hours, secs)"""
        days = total_sec // (24 * 3600)
        total_sec = total_sec % (24 * 3600)
        hours = total_sec // 3600
        total_sec %= 3600
        mins = total_sec // 60
        return (days, hours, mins)
