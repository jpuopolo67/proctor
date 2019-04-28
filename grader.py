from datetime import datetime as dt
from pathmgr import PathManager
from ploggerfactory import ProctorLoggerFactory
from pconfig import ProctorConfig

class Grader:
    """Runs units tests using JUnit and determines the ratio of passed/total, e.g., 10/15"""

    def __init__(self, builder, testrunner, gradebook):
        """Initializes the Grader.
        :param builder: Builder instance that compiles Java source and tests.
        :param testrunner: UnitTestRunner that executes JUnit-based tests via shell commands.
        :param gradebook: GradeBook the records and saves the grades per application run."""
        self._logger = ProctorLoggerFactory.getLogger()
        self._builder = builder
        self._testrunner = testrunner
        self._gradebook = gradebook

    def grade(self, email, project_name, dir_to_grade, project_due_dt, latest_commit_dt):
        """Grades a project for the specified owner (email).
        :param email: Project owner's email
        :param project_name: Name of the project being graded
        :param dir_to_grade: Root of directory tree containing project files
        :param project_due_dt: Project due datetime in UTC
        :param latest_commit_dt: Project's most recent commit datetime from server in UTC"""

        # Determines if the project is on time based on due datetime vs. latest commit datetime
        is_ontime, days, hours, mins = self._get_dt_diff_human_readable(project_due_dt, latest_commit_dt)

        # Information that goes into a grade record...
        grade_info = {'project_name': project_name, 'email': email,
                      'due_dt': project_due_dt, 'latest_commit_dt': latest_commit_dt,
                      'is_ontime': is_ontime, 'days': days, 'hours': hours, 'mins': mins}

        # Running list of notes
        notes = ''

        # Build source
        self._logger.debug(f'Building source: {dir_to_grade}')
        build_source_errors = self._builder.build_source(email, project_name, dir_to_grade)
        grade_info.update({'source_builds': build_source_errors == 0})

        # Build student unit tests
        if build_source_errors == 0:
            self._logger.debug(f'Building student unit tests: {dir_to_grade}')
            build_tests_errors = self._builder.build_tests(email, project_name, dir_to_grade)
            grade_info.update({'student_tests_build': build_tests_errors == 0})
        else:
            grade_info.update({'student_tests_build': 'NA'})

        # Run project unit tests and calculate internal test ratio = passed tests / total tests
        if build_source_errors == 0 and build_tests_errors == 0:
            test_class_name = PathManager.get_student_test_class(project_name)
            if test_class_name and len(test_class_name) > 0:
                num_tests_run, test_ratio = \
                    self._run_project_unit_tests(email, project_name, dir_to_grade, test_class_name)
                if num_tests_run > 0:
                    grade_info.update({'student_tests_ratio': test_ratio})
                else:
                    grade_info.update({'student_tests_ratio': 'No tests run. Check configuration file for proper test suite name.'})
            else:
                self._logger.warning('Missing unit test class. No tests specified.')
                grade_info.update({'student_tests_ratio': 'No tests specified. Check configuration file.'})
        else:
            # Cannot run unit tests due to build errors in source or in tests
            grade_info.update({'student_tests_ratio': 'No tests run due to build failures'})

        # Run instructor (external) unit tests if there is an instructor test class defined in
        # the Proctor configuration file
        #
        # Note: The instructor unit test are assumed to have been compiled and ready to run
        # against the project. We do not build the instructor's tests. This could be added
        # as a feature in the future, should it prove necessary or valuable.

        if build_source_errors == 0:
            suite_dir, suite_class = PathManager.get_instructor_test_suite(project_name)
            if PathManager.instructor_test_suite_exists(suite_dir, suite_class):
                self._logger.info(f'Running instructor unit tests: {suite_dir}:{suite_class}')
                num_tests_run, test_ratio = \
                    self._run_instructor_unit_tests(email, project_name, dir_to_grade, suite_dir, suite_class)
                if num_tests_run > 0:
                    grade_info.update({'instructor_tests_ratio': test_ratio})
                else:
                    grade_info.update({'instructor_tests_ratio': 'No tests run!'})
            else:
                self._logger.warning('No instructor unit tests specified in the configuration file. Continuing.')
                grade_info.update({'instructor_tests_ratio': 'No tests specified. Check configuration file.'})
        else:
            self._logger.info('Skipping instructor unit tests due to source build failures')
            grade_info.update({'instructor_tests_ratio': 'No tests run due to source build failures'})

        # Record the results of grading this user's project in the gradebook.
        grade_info.update({'grade': 'TBD'})
        grade_info.update({'notes': notes})
        self._gradebook.record_grade(grade_info)

    def _run_instructor_unit_tests(self, email, project_name, dir_to_grade, suite_dir, suite_class):
        """Runs the project's unit test. Assumes JUnit as testing framework.
          :param email: Project owner's email
          :param project_name: Project being graded
          :param dir_to_grade: Root of directory tree where project files live
          :param suite_dir: Full path to the JUnit test suite, e.g., MyTests, sans the .class extension
          :param suite_class: The full package.class name of the test suite class, sans the .class extension
          :returns Ratio of passed tests/all tests as a float. 1.0 means all tests passed."""
        return \
            self._testrunner.run_instructor_unit_tests(email, project_name, dir_to_grade, suite_dir, suite_class)

    def _run_project_unit_tests(self, email, project_name, dir_to_grade, test_class_name):
        """Runs the project's unit test. Assumes JUnit as testing framework.
        :param email: Project owner's email
        :param project_name: Project being graded
        :param dir_to_grade: Root of directory tree where project files live
        :param test_class_name: Name of the JUnit test suite, e.g., TestSuite, sans the .class extention
        :returns Ratio of passed tests/all tests as a float. 1.0 means all tests passed."""
        return \
            self._testrunner.run_project_unit_tests(email, project_name, dir_to_grade, test_class_name)

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
        :param total_sec: Total number of seconds to convert
        :returns: total_sec in parts (days, hours, mins)"""
        days = total_sec // (24 * 3600)
        total_sec = total_sec % (24 * 3600)
        hours = total_sec // 3600
        total_sec %= 3600
        mins = total_sec // 60
        return (days, hours, mins)
