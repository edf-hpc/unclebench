import os
import pytest
import tempbench

@pytest.fixture(scope="module")
def init_env(pytestconfig):
    """ It creates a temporary directory structure to
    test JubeBenchmarkingAPI objects"""

    config = {}
    config['main_path'] = "/tmp/ubench_pytest/"
    repository_root = os.path.join(pytestconfig.rootdir.dirname,
                                   pytestconfig.rootdir.basename)

    os.environ["UBENCH_BENCHMARK_DIR"] = os.path.join(config['main_path'],
                                                      'benchmarks')
    os.environ["UBENCH_PLATFORM_DIR"] = os.path.join(repository_root,
                                                     'platform')

    test_env = tempbench.Tempbench(config, repository_root)
    test_env.copy_files()
    os.environ["UBENCH_RUN_DIR_BENCH"] = test_env.config['run_path']
    os.environ["UBENCH_RESOURCE_DIR"] = test_env.config['resources_path']
    yield test_env
    test_env.destroy_dir_structure()