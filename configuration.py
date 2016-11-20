from os.path import sep as path_sep
from os.path import join as path_join


class Config(object):
    base_path = "."
    date_format = "%Y-%m-%d_%H-%M-%S"
    recording_start = 1390202100.0
    stages = []
    var_fill = -200.
    knn_var_fill = -90.
    week_specs = {"W03": (1390202100.6, 1390589153.57),
                  "W04": (1390806000.32, 1391193208.91),
                  "W05": (1391410800.65, 1391797033.75),
                  "W06": (1392015600.01, 1392398212.78)}
    week_names = sorted(week_specs.keys())
    week_for_evaluation = week_names
    path_user_sample=path_join("Uploads", "TrainData")
    expert_data_glob_pattern = path_join("StampRally_*", "Uploads", "TrainData", "*.json")
    expert_data_test_glob_pattern = path_join("StampRally_*", "ValidationData", "*.json")
    k = 50

    @property
    def data_set_path(self):
        return path_join(self.base_path, "SCSUT2014v1", "EXP201312")

    @property
    def expert_data_path(self):
        return path_join(self.base_path, "SCSUT2014v1", "TESTDATA") 

    @property
    def config_path(self):
        return path_join(self.data_set_path, "StampRally")

    @property
    def results_path(self):
        return path_join(self.base_path, "results")

    @property
    def rules_path(self):
        return path_join(self.results_path, 'rules')

    @property
    def unified_time_series_path(self):
        return path_join(self.results_path, 'timeseries') 

    @property
    def titarl_configs_path(self):
        return path_join(self.base_path, 'titarl_cfg')

    @property
    def rule_learning_template(self):
        return path_join(self.base_path, "learning_config_e0.xml")

    @property
    def learn_all_file(self):
        return path_join(self.base_path, "learn_all.bat")

    @property
    def log_path(self):
        return path_join(self.base_path, "logs")

    @property
    def trees_path(self):
        return path_join(self.results_path, "trees")


config = Config()


paths = []
for attrib in dir(config):
    if "_path" in attrib:
        paths.append(attrib)

for path in [config.titarl_configs_path, config.unified_time_series_path, config.rules_path, config.trees_path]:
    paths.append("%s%squarterly" % (path, path_sep))

config.paths = paths
