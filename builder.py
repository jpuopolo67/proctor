import os
import logging
import subprocess
import glob
from logging import Logger
from pathlib import Path
from pathmgr import PathManager


class Builder:
    """Builds the source and test files via javac."""
    _logger: Logger

    def __init__(self):
        """Initializes the Builder."""
        self._logger = logging.getLogger("proctor")

    def build_source(self, email, project_name, dir_to_grade):
        """Builds the project source (*.java) files.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live
        :returns Number of compiler errors."""
        self._logger.info(f'Building source: {email}{os.sep}{project_name}')
        errors = self._compile_project_source(project_name, dir_to_grade)
        if errors == 0:
            self._logger.debug('Build OK')
        else:
            self._logger.error(f'Build errors: {errors}.  Build failed.')
        return errors

    def build_tests(self, email, project_name, dir_to_grade):
        """Builds the project unit tests.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live
        :returns Number of compiler errors"""
        self._logger.info(f'Building unit tests: {email}{os.sep}{project_name}')
        errors = self._compile_unit_tests(project_name, dir_to_grade)
        if errors == 0:
            self._logger.debug('Tests built OK')
        else:
            self._logger.error(f'Unit test build errors: {errors}.  Build failed.')
        return errors

    def _compile_unit_tests(self, project_name, dir_to_grade):
        """Compiles unit test code via javac.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live
        :returns Number of compiler errors"""
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
            self._logger.debug(f'...{file_name} => {result_string}')
            build_errors = build_errors + result.returncode
        return build_errors

    def _compile_project_source(self, project_name, dir_to_grade):
        """Compiles Java source code via javac.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live
        :returns: Number of compiler errors"""

        src_dir = PathManager.get_project_src_dir_name(project_name)
        path_dir = os.sep.join([str(dir_to_grade), src_dir])
        full_classpath = PathManager.get_full_classpath(java_cp=f'.:{path_dir}', junit_cp=None)

        java_file_names = self._get_java_file_names(project_name, dir_to_grade)
        build_errors = 0
        for src_file in java_file_names:
            result = subprocess.run(['javac', '-classpath', full_classpath,
                                     '-sourcepath', full_classpath, src_file],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result_string = "OK" if result.returncode == 0 else "FAILED"
            file_name = Path(src_file).name
            self._logger.debug(f'...{file_name} => {result_string}')
            build_errors = build_errors + result.returncode
        return build_errors

    def _get_java_file_names(self, project_name, dir_to_grade):
        """Fetches the names of the *.java source files to compile.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live"""
        file_names = self._get_project_file_names(project_name, dir_to_grade,
                                                  PathManager.get_project_src_package)
        return file_names

    def _get_unit_test_file_names(self, project_name, dir_to_grade):
        """Fetches the names of the *.java unit test files to compile.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live"""
        file_names = self._get_project_file_names(project_name, dir_to_grade, PathManager.get_student_tests_package)
        return file_names

    def _get_project_file_names(self, project_name, dir_to_grade, fn_package, pattern="*.java"):
        """Helper function that fetches the names of the given project's files that match the specified pattern.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live
        :param fn_package: Function called to retrieve files. One retrieves source names, the other test names"""
        src_dir_name = PathManager.get_project_src_dir_name(project_name)
        files_package = fn_package(project_name)
        files_path = PathManager.package_name_to_path_name(files_package)
        full_path = os.sep.join([str(dir_to_grade), src_dir_name, files_path])
        file_names = glob.glob(os.sep.join([full_path, pattern]))
        return file_names
