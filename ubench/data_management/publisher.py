from ubench.core.ubench_config import UbenchConfig
from ubench.data_management.data_store_yaml import DataStoreYAML
from ubench.data_management.vcs.git import Git

class Publisher:

    def __init__(self):

        self.vcs = Git(UbenchConfig().repo_dir)

    def get_files_from_ref(self, ref):
        # return map for each bench
        files = self.vcs.get_files_from_tag(ref)
        b_map = {}
        for fl in files:
            data = DataStoreYAML()
            metadata, _ = data.load(fl)
            b_map[metadata['Benchmark_name']] = fl

        return b_map
