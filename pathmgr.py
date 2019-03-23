from pathlib import Path
from pconfig import ProctorConfig
import os
import shutil


class PathManager:
    """Manages directories and path information."""

    @staticmethod
    def init_dest_path(dest_path_name, force):
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
    def get_project_src_dir_name(project_name):
        return PathManager._get_project_config_value(project_name, 'src_dir')

    @staticmethod
    def get_project_src_package(project_name):
        return PathManager._get_project_config_value(project_name, 'src_package')

    @staticmethod
    def get_project_tests_package(project_name):
        return PathManager._get_project_config_value(project_name, 'tests_package')

    @staticmethod
    def get_project_student_test_class(project_name):
        return PathManager._get_project_config_value(project_name, 'student_test_class')

    @staticmethod
    def get_project_instructor_test_class(project_name):
        return PathManager._get_project_config_value(project_name, 'instructor_test_class')

    @staticmethod
    def get_java_classpath():
        java_classpath = ProctorConfig.get_config_value('Projects', 'java_classpath')
        if java_classpath is None or len(java_classpath) == 0:
            try:
                java_classpath = os.environ['CLASSPATH']
            except:
                pass
        return java_classpath

    @staticmethod
    def get_junit_classpath():
        return ProctorConfig.get_config_value('Projects', 'junit_path')

    @staticmethod
    def get_full_classpath(java_cp, junit_cp):
        if java_cp is None:
            java_cp = PathManager.get_java_classpath()
        if junit_cp is None:
            junit_cp = PathManager.get_junit_classpath()
        return os.pathsep.join([java_cp, junit_cp])


    @staticmethod
    def _get_project_config_value(project_name, cfg_key):
        cfg_value = ProctorConfig.get_config_value(project_name, cfg_key)
        if cfg_value is None:
            new_key = f'default_{cfg_key}'
            cfg_value = ProctorConfig.get_config_value('Projects', new_key)
        return cfg_value  # Might be None and that's OK. Caller handles.

    @staticmethod
    def path_name_to_packge_name(path_name):
        package_name = path_name.replace(os.sep, '.')
        return package_name

    @staticmethod
    def package_name_to_path_name(package_name):
        path_name = package_name.replace('.', os.sep)
        return path_name
