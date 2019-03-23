from pconfig import ProctorConfig
from pathmgr import PathManager
from gradebook import GradeBook
from pathlib import Path
from datetime import datetime as dt
import os
import subprocess
import glob
import logging
import re

# TODO: Add "run external unit tests" functionality to the class

class Grader:
    """Runs units tests using JUnit and determines the ratio of passed/total, e.g., 10/15"""

    def __init__(self, gradebook):
        self._logger = logging.getLogger("proctor")
        self._gradebook = gradebook

    def grade(self, email, project_name, dir_to_grade, project_due_dt, latest_commit_dt):
        """Grades the project for the given project owner as specificed by the email."""

        is_ontime, days, hours, mins = self._get_dt_diff_human_readable(project_due_dt, latest_commit_dt)

        grade_info = {'project_name': project_name, 'email': email,
                      'due_dt': project_due_dt, 'latest_commit_dt': latest_commit_dt,
                      'is_ontime': is_ontime, 'days': days, 'hours': hours, 'mins': mins}

        errors = self._build_source(email, project_name, dir_to_grade)
        grade_info.update({'source_builds': errors == 0} )

        errors = self._build_tests(email, project_name, dir_to_grade)
        grade_info.update({'tests_build': errors == 0})

        test_class_name = PathManager.get_project_student_test_class(project_name)
        internal_test_ratio = self._run_project_unit_tests(email, project_name, dir_to_grade, test_class_name)

        grade_info.update({'internal_test_ratio': internal_test_ratio})
        grade_info.update({'external_test_ratio': 0.0})
        grade_info.update({'grade': 'TBD'} )
        grade_info.update({'notes': 'this is pretty cool!'} )

        self._gradebook.record_grade(grade_info)

    def _run_project_unit_tests(self, email, project_name, dir_to_grade, test_class_name):
        self._logger.info(f'Running unit test harness {email}{os.sep}{project_name}{os.sep}{test_class_name}')

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

        # TODO: Replace hard-coded values with calculated values once the GitLab
        # TODO: server is back online



    def _build_source(self, email, project_name, dir_to_grade):
        self._logger.info(f'Building {email}{os.sep}{project_name}')
        errors = self._compile_project_source(project_name, dir_to_grade)
        if errors == 0:
            self._logger.info('Build succeeded')
        else:
            self._logger.error(f'BUILD ERRORS: {errors}.  Build failed.')
        return errors

    def _build_tests(self, email, project_name, dir_to_grade):
        self._logger.info(f'Building tests for {email}{os.sep}{project_name}')
        errors = self._compile_unit_tests(project_name, dir_to_grade)
        if errors == 0:
            self._logger.info('Tests built OK')
        else:
            self._logger.error(f'TEST BUILD ERRORS: {errors}.  Build failed.')
        return errors

    def _compile_unit_tests(self, project_name, dir_to_grade):
        unit_test_file_names = self._get_unit_test_file_names(project_name, dir_to_grade)
        src_dir = PathManager.get_project_src_dir_name(project_name)
        path_dir = os.sep.join([str(dir_to_grade), src_dir])
        full_classpath = PathManager.get_full_classpath(java_cp=f'.:{path_dir}', junit_cp=None)

        build_errors = 0
        for test_file in unit_test_file_names:
            result = subprocess.run(['javac', '-classpath', full_classpath, test_file],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result_string = "OK" if result.returncode == 0 else "FAILED"
            file_name = Path(test_file).name
            self._logger.info(f'...{file_name} => {result_string}')
            build_errors = build_errors + result.returncode
        return build_errors

    def _compile_project_source(self, project_name, dir_to_grade):
        java_file_names = self._get_java_file_names(project_name, dir_to_grade)
        build_errors = 0
        for src_file in java_file_names:
            result = subprocess.run(['javac', src_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result_string = "OK" if result.returncode == 0 else "FAILED"
            file_name = Path(src_file).name
            self._logger.info(f'...{file_name} => {result_string}')
            build_errors = build_errors + result.returncode
        return build_errors

    def _get_java_file_names(self, project_name, dir_to_grade):
        file_names = self._get_project_file_names(project_name, dir_to_grade,
                                                  PathManager.get_project_src_package)
        return file_names

    def _get_unit_test_file_names(self, project_name, dir_to_grade):
        file_names = self._get_project_file_names(project_name, dir_to_grade, PathManager.get_project_tests_package)
        return file_names

    def _get_project_file_names(self, project_name, dir_to_grade, fn_package, pattern="*.java"):
        src_dir_name = PathManager.get_project_src_dir_name(project_name)
        files_package = fn_package(project_name)
        files_path = PathManager.package_name_to_path_name(files_package)
        full_path = os.sep.join([str(dir_to_grade), src_dir_name, files_path])
        file_names = glob.glob(os.sep.join([full_path, pattern]))
        return file_names

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

