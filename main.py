import argparse
from argparse import RawTextHelpFormatter
import json
from exception import InvalidPackageException
from pydependence import PyDependence


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PyDependence', formatter_class=RawTextHelpFormatter)
    
    option_choices = ['init', 'refresh', 'package', 'dependence', 'unique', 'visualize']
    parser.add_argument('option', type=str, choices=option_choices, help="init: initial package information;\n"
                                                 "refresh: refresh package information;\n"
                                                 "package: show all package information;\n"
                                                 "dependence: show the dependence of special package, you can specify package name by -p or --package\n"
                                                 "unique: show the unique dependence of special package，you can specify package name by -p or --package\n"
                                                 "visualize: visualize dependence graph of all package, you can specify package name by -p or --package."
                                                 "Program will show dependence of all packages if not specify.\n")

    parser.add_argument('-p', '--package', type=str, default='', help='the package name. For example, pydependence dependence -p package_name\n')

    args = parser.parse_args()
    option = args.option
    if option == 'init' or option == 'refresh':
        PyDependence.update_package_info()
    elif option == 'package':
        PyDependence.output_all_packages()
    elif option == 'dependence'or option == 'unique':
        if args.package == '':
            print('please input package name')
            exit(-1)
        else:
            try:
                if option == 'dependence':
                    dependence = PyDependence.get_all_dependence(args.package)
                    print('\nAll {} unique dependences of {} are as follows:\n'.format(len(dependence), args.package))
                else:
                    dependence = PyDependence.get_unique_dependence(args.package)
                    print('\nAll {} dependences of {} are as follows:\n'.format(len(dependence), args.package))
                dependence.sort()
                [print(i) for i in dependence]
                
            except InvalidPackageException as e:
                print(e)
                print('{} is not a valid package, please refresh package information and try again if your package environment had changed.'.format(args.package))
                exit(-1)

    elif option == 'visualize':
        PyDependence.plot_dependence(args.package)
    else:
        print("please input valid arguments, '--help' for help")
