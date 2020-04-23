from ubench.data_management.data_store_yaml import DataStoreYAML


def test_result_filter(data_dir):
    """ Test if we can get variable values for a given run.

    Benchmark files are composed of several runs. This method help us to get only the value of certain
    fields for a given run"""
    data = DataStoreYAML()
    d_filter = data.get_result_filter({'jube_wp_abspath': '000000_exec'},
                                      None,
                                      data_dir.bench_results)

    assert d_filter == {'comp_version': 'gnu', 'host_p': 'Hostname_id', 'mpi_version': 'OpenMPI-2.0.2'}


def test_result_filter_opts(data_dir):

    data = DataStoreYAML()
    d_filter = data.get_result_filter({'jube_wp_abspath': '000000_exec'},
                                      {'comp_version': 'gnu'},
                                      data_dir.bench_results)

    assert d_filter == {'comp_version': 'gnu', 'host_p': 'Hostname_id', 'mpi_version': 'OpenMPI-2.0.2'}
