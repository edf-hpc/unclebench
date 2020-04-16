from ubench.data_management.data_store_yaml import DataStoreYAML


def test_result_filter():

    data = DataStoreYAML()
    d_filter = data.get_result_filter({'jube_wp_abspath': '000000_exec'},
                                      None,
                                      "data/bench_results.yaml")

    assert d_filter == {'comp_version': 'gnu', 'host_p': 'Hostname_id', 'mpi_version': 'OpenMPI-2.0.2'}


def test_result_filter_opts():

    data = DataStoreYAML()
    d_filter = data.get_result_filter({'jube_wp_abspath': '000000_exec'},
                                      {'comp_version': 'gnu'},
                                      "data/bench_results.yaml")

    assert d_filter == {'comp_version': 'gnu', 'host_p': 'Hostname_id', 'mpi_version': 'OpenMPI-2.0.2'}
