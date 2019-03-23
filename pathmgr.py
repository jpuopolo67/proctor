from pathlib import Path
from pconfig import ProctorConfig
import os
import shutil


class PathManager:
    """Manages directories and path information.

    In general, the class uses information from the app's configuration file. The methods herein first attempt
    to obtain the requested key=value from the project-specific section of the configuration file. If the
    project-specific section does not define the key=value, the methods check to see if there is a default
    defined. They do this by pre-pending the given key with 'default_' and then attempt to retrieve this
    new default_key=value from the [Projects] section of the configuration file."""

    @staticmethod
    def init_dest_path(dest_path_name, force):
        """Creates directory where files can be copied.
        :param dest_path_name: Name of the destination path.
        :param: force: True if existing path should be overwritten."""
        dest_path = Path(dest_path_name)
        if not dest_path.exists():
            dest_path.mkdir(parents=True)
            return
        if dest_path.exists() and force:
            shutil.rmtree(dest_path)
            dest_path.mkdir(parents=True, exist_ok=True)
            return
        raise FileExistsError("Destination path already exists. Use --force to overwrite.")

    @staticmethod
    def build_dest_path_name(working_dir, email, project_name):
        """Builds a file system path name from component parts.
        :param working_dir: Proctor's working directory name.
        :param email: Project owner's email.
        :param project_name: Name of the project being worked on.
        :return File system path name."""
        dest_path_name = os.sep.join([working_dir, project_name, email])
        return dest_path_name

    @staticmethod
    def get_project_src_dir_name(project_name):
        """Returns the name of the src_dir to use.
        :param project_name: Name of the project being worked on.
        :returns Name of the src_dir to use"""
        return PathManager._get_project_config_value(project_name, 'src_dir')

    @staticmethod
    def get_project_src_package(project_name):
        """Returns the name of the src_package to use.
        :param project_name: Name of the project being worked on.
        :returns Name of the src_package to use"""
        return PathManager._get_project_config_value(project_name, 'src_package')

    @staticmethod
    def get_project_tests_package(project_name):
        """Returns the name of the tests_package to use.
        :param project_name: Name of the project being worked on.
        :returns Name of the tests_package to use"""
        return PathManager._get_project_config_value(project_name, 'tests_package')

    @staticmethod
    def get_project_student_test_class(project_name):
        """Returns the name of the student_test_class to use.
        :param project_name: Name of the project being worked on.
        :returns Name of the student_test_class to use"""
        return PathManager._get_project_config_value(project_name, 'student_test_class')

    @staticmethod
    def get_project_instructor_test_class(project_name):
        """Returns the name of the instructor_test_class to use.
        :param project_name: Name of the project being worked on.
        :returns Name of the instructor_test_class to use"""
        return PathManager._get_project_config_value(project_name, 'instructor_test_class')

    @staticmethod
    def get_java_classpath():
        """Determines the Java classpath use use.

        First, attempt to read java_classpath from the configuration file. If it's
        not found or empty, attempt to read the environment CLASSPATH variable.
        :returns Value of the Java classpath to use or None if it cannot be determined."""
        java_classpath = ProctorConfig.get_config_value('Projects', 'java_classpath')
        if java_classpath is None or len(java_classpath) == 0:
            try:
                java_classpath = os.environ['CLASSPATH']
            except:
                pass
        return java_classpath

    @staticmethod
    def get_junit_classpath():
        """Determines the Java classpath use use for JUnit.
        :returns Value of the Java classpath to use for JUnit or None if it cannot be determined."""
        return ProctorConfig.get_config_value('Projects', 'junit_path')

    @staticmethod
    def get_full_classpath(java_cp, junit_cp):
        """Builds a full classpath by combining the Java classpath and the JUnit classpath.
        :param java_cp: Java classpath
        :param junit_cp: JUnit classpath, including proper lib (.jar) files
        :returns Full classpath that includes access to the project's Java source, tests, and JUnit lib files."""
        if java_cp is None:
            java_cp = PathManager.get_java_classpath()
        if junit_cp is None:
            junit_cp = PathManager.get_junit_classpath()
        return os.pathsep.join([java_cp, junit_cp])

    @staticmethod
    def _get_project_config_value(project_name, cfg_key):
        """Returns the value of the given configuration key or None.
        :param project_name: Project being worked on, which represents a [section] name in the configuration file.
        :param cfg_key: Key for which the value is retrieved.
        :returns Value associated with the given configuration file key, or None if not found."""
        cfg_value = ProctorConfig.get_config_value(project_name, cfg_key)
        if cfg_value is None:
            new_key = f'default_{cfg_key}'
            cfg_value = ProctorConfig.get_config_value('Projects', new_key)
        return cfg_value  # Might be None and that's OK. Caller handles.

    @staticmethod
    def path_name_to_packge_name(path_name):
        """Helper function that converts an OS path name to a Java package name.
        :param path_name: Name of the OS path to convert to a package name
        :returns Java package name."""
        package_name = path_name.replace(os.sep, '.')
        return package_name

    @staticmethod
    def package_name_to_path_name(package_name):
        """Helper function that converts a Java package name to an OS path name.
        :param package_name: Name of the Java package to convert to an OS path
        :returns OS path name."""
        path_name = package_name.replace('.', os.sep)
        return path_name
