
import subprocess
import os
import re
from pathmgr import PathManager
from ploggerfactory import ProctorLoggerFactory

class UnitTestRunner:
    """Runs JUnit-based tests and parses results"""
    def __init__(self):
        self._logger = ProctorLoggerFactory.getLogger()

    def run_instructor_unit_tests(self, email, project_name, dir_to_grade, suite_dir, suite_class):
        """Runs the project's unit test. Assumes JUnit as testing framework.
          :param email: Project owner's email
          :param project_name: Project being graded
          :param dir_to_grade: Root of directory tree where project files live
          :param suite_dir: Full path to  the JUnit test suite, e.g., MyTests, sans the .class extention
          :returns Ratio of passed test/all tests as a floating point number. 1.0 means all tests passed."""

        # Determine proper paths for java runtime so that we can find test classes
        src_dir = PathManager.get_project_src_dir_name(project_name)
        path_dir = os.sep.join([str(dir_to_grade), src_dir])
        full_classpath = PathManager.get_full_classpath(java_cp=f'.{os.pathsep}{path_dir}{os.pathsep}{suite_dir}',
                                                        junit_cp=None)

        # Run the tests using JUnit's command-line runner
        results = subprocess.run(
            ['java', '-cp', full_classpath, 'org.junit.runner.JUnitCore', suite_class],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Process the result of running the tests.
        return \
            self._process_test_results(results)

    def run_project_unit_tests(self, email, project_name, dir_to_grade, test_class_name):
        """Runs the project's unit test. Assumes JUnit as testing framework.
        :param email: Project owner's email
        :param project_name: Project being graded
        :param dir_to_grade: Root of directory tree where project files live
        :param test_class_name: Name of the JUnit test suite, e.g., TestSuite, sans the .class extention
        :returns Ratio of passed test/all tests as a floating point number. 1.0 means all tests passed."""

        self._logger.info(f'Running unit tests: {email}{os.sep}{project_name}{os.sep}{test_class_name}')

        # Determine proper paths and classes
        src_dir = PathManager.get_project_src_dir_name(project_name)
        path_dir = os.sep.join([str(dir_to_grade), src_dir])
        full_classpath = PathManager.get_full_classpath(java_cp=f'.{os.pathsep}{path_dir}',
                                                        junit_cp=None)
        test_suite_class = PathManager.get_student_test_suite(project_name)

        # Run the tests using JUnit's command-line runner
        results = subprocess.run(
            ['java', '-cp', full_classpath, 'org.junit.runner.JUnitCore', test_suite_class],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Process the result of running the tests.
        return \
            self._process_test_results(results)

    def _process_test_results(self, results):

        tests_run = 0
        test_ratio = 0.0

        sresults = results.stdout.decode('utf-8')

        if results.returncode == 0:  # all tests passed!
            pattern = "OK \((\d+) tests\)"
            m = re.search(pattern, sresults)
            tests_run = tests_passed = int(m.group(1))
            test_ratio = 1.0
            self._logger.info(f'All tests passed: {tests_passed} / {tests_run}')
        else:   # some failures
            pattern = "Tests run: (\d+),  Failures: (\d+)"
            m = re.search(pattern, sresults)
            tests_run = int(m.group(1))
            tests_failed = int(m.group(2))
            tests_passed = tests_run - tests_failed
            test_ratio = tests_passed / tests_run
            self._logger.info(f'Test results: {tests_passed} / {tests_run}: {test_ratio}')

        return (tests_run, test_ratio)
