import os
import json
from command import get_package_info, get_all_package
from exception import CommandException, InvalidPackageException


class Package:
    def __init__(self, pkg_info, from_json=False):
        try:
            if from_json:
                name, val = pkg_info
                self.name = name
                self.version = val['Version']
                self.location = val['Location']
                self.require_list = val['Requires']
                self.required_by_list = val['Required-by']
            else:
                self.name = pkg_info['Name'].replace(' ', '').lower()
                self.version = pkg_info['Version']
                self.location = pkg_info['Location']
                require_str, required_by_str = pkg_info['Requires'], pkg_info['Required-by']
                require_str, required_by_str = require_str.replace(' ', ''), required_by_str.replace(' ', '')
                self.require_list = require_str.lower().split(',') if require_str else []
                self.required_by_list = required_by_str.lower().split(',') if required_by_str else []
        except KeyError as e:
            print(e)

    def add_require(self, pkg):
        self.require_list.append(pkg)

    def add_required_by(self, pkg):
        self.required_by_list.append(pkg)
    
    def formatted_output(self):
        return "Name: {}\nVersion: {}\nLocation: {}\nRequires: {}\nRequired-by: {}".format(
            self.name, self.version, self.location, self.require_list, self.required_by_list)

    def __repr__(self) -> str:
        return self.name


class DependenceGraph:
    def __init__(self, pkgs):
        try:
            import networkx as nx
        except ImportError as e:
            print(e)
            print("please install networkx package if you want visualize dependence of packages.")
            exit(-1)

        self.graph = nx.DiGraph()
        for pkg in pkgs.keys():
            self.graph.add_node(pkg)
        for pkg, pkg_obj in pkgs.items():
            for require_pkg in pkg_obj.require_list:
                self.graph.add_edge(pkg, require_pkg)

    def plot_graph(self):
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
        except ImportError as e:
            print(e)
            print("please install matplotlib package if you want visualize dependence of packages.")
            exit(-1)

        plt.figure(0)
        pos = nx.spring_layout(self.graph)
        label = {}
        for node in self.graph.nodes():
            label[node] = node

        nx.draw_networkx_labels(self.graph, pos, labels=label, font_size=8)
        nx.draw_networkx_nodes(self.graph, pos=pos, node_size=1000, alpha=0.8)
        nx.draw_networkx_edges(self.graph, pos=pos, node_size=1000, width=0.5, alpha=0.8)
        plt.show()

class PipDependence:
    store_path = '.'
    store_filename = 'package.json'

    def __init__(self):
        pass

    @staticmethod
    def scan_package():
        try:
            pkgs = get_all_package()
            pkg_objs = {}
            for p in pkgs:
                pkg_info = get_package_info(p)
                obj = Package(pkg_info)
                pkg_objs[obj.name] = obj
            return pkg_objs

        except CommandException as e:
            print(e)
            exit(-1)
    
    @staticmethod
    def parse_dependence(pkgs, pkg_name):
        dependence = set()
        dependence.add(pkg_name)
        try:
            pkg_obj = pkgs[pkg_name]
        except KeyError:
            raise InvalidPackageException('Invalid pacakge name')

        queue = [pkg_obj]
        while queue:
            pkg_obj = queue.pop(0)
            for require_pkg in pkg_obj.require_list:
                len1 = len(dependence)
                dependence.add(require_pkg)
                len2 = len(dependence)
                if len1 != len2:
                    require_pkg_obj = pkgs[require_pkg]
                    queue.append(require_pkg_obj)
        return list(dependence)

    @classmethod
    def store_package(cls, pkgs):
        pkgs_dict = {}
        for name, obj in pkgs.items():
            pkgs_dict[name] = {
                "Version": obj.version, 
                "Location": obj.location,
                "Requires": obj.require_list,
                "Required-by": obj.required_by_list}

        with open(cls.store_file_path, 'w') as f:
            json.dump({"number": len(pkgs_dict), "package": pkgs_dict}, f, indent=4)

    @classmethod
    def update_package_info(cls):
        print('Updateing package information')
        pkg_objs = cls.scan_package()
        cls.store_package(pkg_objs)
        print('package information had saved to file {}'.format(cls.store_file_path))


    @classmethod
    def load_package_info(cls):
        """
        Return: a dict contains all Package object, the key of dict is the package name and the value is Package object
        """
        if not os.path.exists(cls.store_file_path):
            pkg_objs = cls.scan_package()
            cls.store_package(pkg_objs)
            print('package information had saved to file {}'.format(cls.store_file_path))
            return pkg_objs
        else:
            print('loading from file {}'.format(cls.store_file_path))
            with open(cls.store_file_path, 'r') as f:
                try:
                    pkg_info = json.load(f)
                except json.JSONDecodeError as e:
                    print(e)
                    print('parse {} failed, please delete this file and try again!'.format(cls.store_file_path))
                    exit(-1)
                # check validation of package file 

                pkg_objs = {}
                for name, obj in pkg_info["package"].items():
                    pkg_objs[name] = Package((name, obj), from_json=True)
                return pkg_objs
    
    @classmethod
    def output_all_packages(cls):
        pkgs = cls.load_package_info()
        print("Total {} packages".format(len(pkgs)))
        for i, obj in enumerate(pkgs.values()):
            print(i)
            print(obj.formatted_output())
            print()

    @classmethod
    def get_all_dependence(cls, pkg_name):
        pkgs = cls.load_package_info()
        return cls.parse_dependence(pkgs, pkg_name)
        
    @classmethod
    def get_unique_dependence(cls, pkg_name):
        pkgs = cls.load_package_info()
        dependence = cls.parse_dependence(pkgs, pkg_name)

        dependence_set = set(dependence)
        shared_set = set()
        for pkg in dependence_set:
            if pkg in shared_set:
                continue

            pkg_obj = pkgs[pkg]
            for required_by_pkg in pkg_obj.required_by_list:
                if (required_by_pkg not in dependence_set) or (required_by_pkg in shared_set):
                    required_by_pkg_dependence = cls.parse_dependence(pkgs, required_by_pkg)
                    shared_set = shared_set.union(set(required_by_pkg_dependence))
        return list(dependence_set - shared_set)

    @classmethod
    def plot_dependence(cls, pkg_name):
        pkgs = cls.load_package_info()

        try:
            dependence =cls.parse_dependence(pkgs, pkg_name)
            new_pkgs = {pkg: pkgs[pkg] for pkg in dependence}
        except InvalidPackageException:
            print('package {} is not a valid package, please refresh package information and try again if your package environment had changed.\n'
            'Showing dependence of all packages.'.format(pkg_name))
            new_pkgs = pkgs

        graph = DependenceGraph(new_pkgs)
        graph.plot_graph()

    @classmethod
    @property
    def store_file_path(cls):
        return os.path.join(cls.store_path, cls.store_filename)
