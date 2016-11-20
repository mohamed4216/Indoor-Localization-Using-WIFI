import json
import re
import time
from random import random
from glob import glob
from os.path import basename, dirname
from os.path import sep as path_sep
from os.path import join as path_join
from datetime import datetime

from numpy import inf, array
from pandas import DataFrame
from configuration import Config

__author__ = 'luis'
methods = []


def method_list(method):
    if method not in methods:
        methods.append(method)

    return method


class Repository(object):
    def __init__(self, config):
        self.expert_locations = {}
        assert isinstance(config, Config)
        self.config = config
        self.base_path = config.base_path
        self.config_path = config.config_path
        self.sample_path = config.path_user_sample
        self.expert_data_path = config.expert_data_path
        self.users = []
        self.access_points = {}
        self.locations = {}
        self.goal_types = {}
        self.goals = {}
        self.goals_timetable = {}
        self.samples = {}
        self.expert_samples = {}
        self.expert_validation_samples = {}
        self.fingerprints = {}
        for m in methods:
            m(self)

    @method_list
    def load_users(self):
        user_file = "%s/users.json" % self.config_path
        with open(user_file) as fd:
            jf = json.load(fd)

        for u in jf:
            self.users.append(u['user_id'])

    @method_list
    def load_locations(self):
        user_file = "%s/goallist.json" % self.config_path
        with open(user_file) as fd:
            jf = json.load(fd)

        for loc in jf:
            self.locations.setdefault((loc['latitude'], loc['longitude']), set())

    @method_list
    def load_goals(self):
        file_list = glob('%s/Goals/Goals*/*.json' % self.config_path)
        for f in file_list:
            goal_type = re.match(".*_([a-z]*)", dirname(f)).group(1)
            time_name = basename(f).split(".")[0]
            ts = time.mktime(time.strptime(time_name, "%Y-%m-%d_%H-%M-%S"))
            with open(f) as fd:
                jf = json.load(fd)

            for loc in jf:
                priority = self.goals.setdefault(goal_type, {}).setdefault(ts, {})
                priority[(loc['location']['latitude'], loc['location']['longitude'])] = loc['priority']

        self.goal_types = dict([x[::-1] for x in enumerate(self.goals)])

    @method_list
    def load_expert_data(self):
        file_list = glob("%s/%s" % (self.expert_data_path, self.config.expert_data_glob_pattern))
        for f in file_list:
            user = re.match(".*StampRally_([a-z]*)/", dirname(f)).group(1)
            time_name = basename(f).split(".")[0]
            ts = time.mktime(time.strptime(time_name, "%Y-%m-%d_%H-%M-%S"))
            with open(f) as fd:
                jf = json.load(fd)

            for fingerprint in jf:
                loc = (fingerprint['location']['latitude'], fingerprint['location']['longitude'])
                for mac, v in fingerprint['fingerprint']['wifi'].items():
                    # self.access_points.setdefault(mac, set()).add(loc)
                    self.expert_locations.setdefault(loc, set()).add(mac)
                    self.expert_samples.setdefault(ts, {}).setdefault(user, {}).setdefault(loc, []).append(
                        {'level': v["level"], 'mac': mac})

    @method_list
    def load_expert_data_test(self):
        file_list = glob("%s/%s" % (self.expert_data_path, self.config.expert_data_test_glob_pattern))
        for f in file_list:
            user = re.match(".*StampRally_([a-z]*)/", dirname(f)).group(1)
            time_name = basename(f).split(".")[0]
            ts = time.mktime(time.strptime(time_name, "%Y-%m-%d_%H-%M-%S"))
            with open(f) as fd:
                jf = json.load(fd)

            for fingerprint in jf:
                loc = (fingerprint['location']['latitude'], fingerprint['location']['longitude'])
                for mac, v in fingerprint['fingerprint'].items():
                    # self.access_points.setdefault(mac, set()).add(loc)
                    self.expert_locations.setdefault(loc, set()).add(mac)
                    self.expert_validation_samples.setdefault(ts, {}).setdefault(user, {}).setdefault(loc, []).append(
                        {'level': v["level"], 'mac': mac})

    @method_list
    def load_goals_timetable(self):
        file_list = glob('%s/Goals/Users/*.json' % self.config_path)
        for f in file_list:
            time_name = basename(f).split(".")[0]
            ts = time.mktime(time.strptime(time_name, "%Y-%m-%d_%H-%M-%S"))
            with open(f) as fd:
                jf = json.load(fd)

            try:
                goal_type = jf.values()[0]
            except IndexError:
                continue

            self.goals_timetable.setdefault(ts, []).append(self.goal_types[goal_type])

    @method_list
    def load_samples(self):
        file_list = glob('%s/StampRally_*/%s/*.json' % (self.config.data_set_path, self.sample_path))
        for f in file_list:
            user = re.match(".*StampRally_([em][0-9])/", dirname(f)).group(1)
            time_name = basename(f).split(".")[0]
            ts = time.mktime(time.strptime(time_name, "%Y-%m-%d_%H-%M-%S"))
            with open(f) as fd:
                jf = json.load(fd)

            for fingerprint in jf:
                loc = (fingerprint['location']['latitude'], fingerprint['location']['longitude'])
                for mac, v in fingerprint['fingerprint']['wifi'].items():
                    self.access_points.setdefault(mac, set()).add(loc)
                    self.locations[loc].add(mac)
                    self.samples.setdefault(ts, {}).setdefault(user, {}).setdefault(loc, []).append(
                        {'level': v["level"], 'mac': mac})

    def iter_samples(self, time_filter=None, user_filter=None, loc_filter=None):
        time_filter = time_filter and time_filter or (0., inf)
        user_filter = user_filter and re.compile(user_filter) or re.compile(".*")
        for ts, users in filter(lambda x: time_filter[0] <= x[0] <= time_filter[1], self.samples.items()):
            for u, locations in filter(lambda x: user_filter.search(x[0]), users.items()):
                for loc, fingerprints in filter(lambda x: not loc_filter and True or loc_filter == x[0],
                                                locations.items()):
                    for fingerprint in fingerprints:
                        mac = fingerprint['mac']
                        value = fingerprint['level']
                        yield [ts, u, loc, mac, value]

    def iter_fingerprints(self, time_filter=None, user_filter=None, loc_filter=None, group_filter=None, src='samples'):
        time_filter = time_filter and time_filter or (0., inf)
        user_filter = user_filter and re.compile(user_filter) or re.compile(".*")
        src = getattr(self, src)
        for ts, users in src.items():
            if not (time_filter[0] <= ts <= time_filter[1]):
                continue

            for u, locations in users.items():
                if not user_filter.search(u):
                    continue

                for loc, fingerprints in locations.items():
                    if loc_filter and loc_filter != loc:
                        continue

                    if group_filter:
                        try:
                            fps = [fp for fp in fingerprints if fp['mac'] in group_filter[loc]]
                        except TypeError:
                            fps = [fp for fp in fingerprints if fp['mac'] in group_filter]
                        except KeyError:
                            fps = fingerprints

                        yield [ts, u, loc, fps]
                        continue

                    yield [ts, u, loc, fingerprints]

    def get_dataset_and_labels(self, columns=None, **kwargs):
        df = []
        labels = []
        for ts, usr, loc, fingerprint in self.iter_fingerprints(**kwargs):
            fp = dict([(m['mac'], m['level']) for m in fingerprint])
            df.append(fp)
            labels.append(loc)

        return DataFrame(df, columns=columns), array(labels)

    def create_time_series(self, time_filter=None, user_filter=None, sample_time=70):
        time_filter = time_filter and time_filter or (0., inf)
        user_filter = user_filter and re.compile(user_filter) or re.compile(".*")
        time_series = []
        for ts, users in filter(lambda x: time_filter[0] <= x[0] <= time_filter[1], self.samples.items()):
            lts = ts
            for u, locations in filter(lambda x: user_filter.search(x[0]), users.items()):
                for loc, fingerprints in locations.items():
                    for fingerprint in fingerprints:
                        mac = fingerprint['mac']
                        lts += random()
                        time_series.append([lts, mac])

                lts += sample_time

        return time_series

    @method_list
    def update_week_specs(self):
        week_stats = {}
        for ts in self.samples:
            date = datetime.fromtimestamp(ts)
            week = date.strftime("%W")
            week_stats.setdefault(week, []).append(ts)

        self.config.week_specs =  dict([("W%s" % w, (min(v), max(v))) for w, v in week_stats.items()])
        self.config.week_names = sorted(self.config.week_specs.keys(), key=lambda x: self.config.week_specs[x][0])
