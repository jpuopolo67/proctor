import glob
import os
import subprocess
from logging import Logger
from pathlib import Path
from pathmgr import PathManager
from ploggerfactory import ProctorLoggerFactory


class Builder:
    """Builds the source and unit test files via javac."""
    _logger: Logger

    def __init__(self):
        """Initializes the Builder."""
        self._logger = ProctorLoggerFactory.getLogger()

    def build_source(self, email, project_name, dir_to_grade):
        """Builds the project source (*.java) files.
        :param email: Name of project owner. Used to find the correct directory to build.
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
        """Builds the project unit tests. JUnit assumed.
        :param email: Name of project owner. Used to find correct directory.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live
        :returns Number of compiler errors"""
        self._logger.info(f'Building student unit tests: {email}{os.sep}{project_name}')
        errors = self._compile_unit_tests(project_name, dir_to_grade)
        if errors == 0:
            self._logger.debug('Tests built OK')
        else:
            self._logger.error(f'Unit test build errors: {errors}.  Build failed.')
        return errors

    def _compile_unit_tests(self, project_name, dir_to_grade):
        """Compiles unit test code via javac. JUnit assumed.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live
        :returns Number of compiler errors"""

        self._logger.debug(f'Compiling unit tests: {dir_to_grade}')

        unit_test_file_names = self._get_unit_test_file_names(project_name, dir_to_grade)
        full_classpath = self._build_unit_test_classpath(project_name, dir_to_grade)

        self._logger.debug(f'Unit test classpath: {full_classpath}')

        build_errors = 0

        try:
            for test_file in unit_test_file_names:
                result = subprocess.run(['javac', '-classpath', full_classpath, test_file],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                result_string = "OK" if result.returncode == 0 else "FAILED"
                file_name = Path(test_file).name
                self._logger.debug(f'...{file_name} => {result_string}')
                build_errors = build_errors + result.returncode
        except Exception as ex:
            self._logger.error("Exception caught while building unit tests {}".format(str(ex)))
            build_errors += 1

        return build_errors

    def _build_unit_test_classpath(self, project_name, dir_to_grade):
        # src directory under project/student email
        src_root_dir = os.sep.join([str(dir_to_grade), PathManager.get_project_src_dir_name(project_name)])

        # full class name, including package, e.g., src/edu/wit...
        src_subdir_name = PathManager.package_name_to_path_name(
            PathManager.get_project_src_package(project_name))
        src_package_dir = os.sep.join([src_root_dir, src_subdir_name])

        # src directory and src directory + package name
        sources_dir = os.pathsep.join([src_root_dir, src_package_dir])

        # Java and JUnit libs
        java_classpath = PathManager.get_full_classpath(java_cp=f'.:{sources_dir}', junit_cp=None)

        # Put them all together to build JUnit-based tests
        return java_classpath

    def _compile_project_source(self, project_name, dir_to_grade):
        """Compiles Java source code via javac.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live
        :returns Number of compiler errors"""

        self._logger.debug(f'Compiling project source code: {dir_to_grade}')

        src_dir = PathManager.get_project_src_dir_name(project_name)
        path_dir = os.sep.join([str(dir_to_grade), src_dir])
        full_classpath = PathManager.get_full_classpath(java_cp=f'.:{path_dir}', junit_cp=None)

        self._logger.debug(f'src_dir: {src_dir}')
        self._logger.debug(f'path_dir: {path_dir}')
        self._logger.debug(f'full_classpath: {full_classpath}')

        java_file_names = self._get_java_file_names(project_name, dir_to_grade)
        build_errors = 0

        try:
            for src_file in java_file_names:
                result = subprocess.run(['javac', '-classpath', full_classpath,
                                         '-sourcepath', full_classpath, src_file],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                result_string = "OK" if result.returncode == 0 else "FAILED"
                file_name = Path(src_file).name
                self._logger.debug(f'...{file_name} => {result_string}')
                build_errors = build_errors + result.returncode
        except Exception as ex:
            self._logger.error("Exception caught while compiling source: {}".format(str(ex)))
            build_errors += 1

        return build_errors

    def _get_java_file_names(self, project_name, dir_to_grade):
        """Fetches the names of the *.java source files to compile.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live
        :returns list of file names"""
        file_names = self._get_project_file_names(project_name, dir_to_grade,
                                                  PathManager.get_project_src_package)
        return file_names

    def _get_unit_test_file_names(self, project_name, dir_to_grade):
        """Fetches the names of the *.java unit test files to compile.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live
        :returns list of file names"""
        file_names = self._get_project_file_names(project_name, dir_to_grade, PathManager.get_student_test_package)
        return file_names

    def _get_project_file_names(self, project_name, dir_to_grade, fn_package, pattern='*.java'):
        """Helper function that fetches the names of the given project's files that match the specified pattern.
        :param project_name: Name of the project being built
        :param dir_to_grade: Root of the directory tree where project files live
        :param fn_package: Function called to retrieve files. One retrieves source names, the other test names
        :param pattern: The shell file pattern to use when determining which files to fetch.
        :returns list of file names"""
        src_dir_name = PathManager.get_project_src_dir_name(project_name)
        files_package = fn_package(project_name)
        files_path = PathManager.package_name_to_path_name(files_package)
        full_path = os.sep.join([str(dir_to_grade), src_dir_name, files_path])
        file_names = glob.glob(os.sep.join([full_path, pattern]))
        return file_names
