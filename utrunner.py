import subprocess
import os
import re
from pathmgr import PathManager
from ploggerfactory import ProctorLoggerFactory

class UnitTestRunner:
    """Runs JUnit-based tests and parses results"""
    def __init__(self):
        """Initializes UnitTestRunner"""
        self._logger = ProctorLoggerFactory.getLogger()

    def run_instructor_unit_tests(self, email, project_name, dir_to_grade, suite_dir, suite_class):
        """Runs the project's unit test. Assumes JUnit as testing framework.
          :param email: Project owner's email
          :param project_name: Project being graded
          :param dir_to_grade: Root of directory tree where project files live
          :param suite_dir: Full path to  the JUnit test suite, e.g., Grading, sans the .class extention;
          :param suite_class: Name of test suite class, sans the .class extension
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
            self._process_test_results(suite_class, results)

    def run_project_unit_tests(self, email, project_name, dir_to_grade, test_class_name):
        """Runs the project's unit test. Assumes JUnit as testing framework.
        :param email: Project owner's email
        :param project_name: Project being graded
        :param dir_to_grade: Root of directory tree where project files live
        :param test_class_name: Name of the JUnit test suite, e.g., TestSuite, sans the .class extension
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
            self._process_test_results(test_suite_class, results)

    def _process_test_results(self, test_suite_class, results):
        """Parses the output of the JUnit tests to determine the ratio of passed tests to executed tests.
        :param Byte-stream results captured from stdout and stderr from running JUnit tests
        :returns Tuple (number of tests executed, ratio of tests-passed / tests-executed)"""

        # Turn the byte stream into a string so that we can parse it easily
        sresults = results.stdout.decode('utf-8')

        # Test stats
        num_tests_executed = 0
        test_ratio = 0.0

        # This parsing code is specific to the how JUnit (4.x) renders output to the console.
        # May need to update it if and when we upgrade JUnit versions.
        try:
            if results.returncode == 0:
                # all tests passed!
                pattern = "OK \((\d+) tests\)"
                m = re.search(pattern, sresults)
                num_tests_executed = tests_passed = int(m.group(1))
                test_ratio = 1.0
            else:
                # some failures
                pattern = "Tests run: (\d+),  Failures: (\d+)"
                m = re.search(pattern, sresults)
                num_tests_executed = int(m.group(1))
                tests_failed = int(m.group(2))
                tests_passed = num_tests_executed - tests_failed
                test_ratio = tests_passed / num_tests_executed

            self._logger.info(f'Test results: {tests_passed} / {num_tests_executed} = {test_ratio}')
        except Exception as ex:
            # Something went wrong...
            self._logger.warning('Error while running unit tests!')
            self._logger.warning(f"Check test suite class '{test_suite_class}' exists and is compatible with the project under test.")

        return (num_tests_executed, test_ratio)
