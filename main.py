import sys
import argparse
import core

arg_parser = argparse.ArgumentParser(description='MathGet, the package manager to update and manage MathScript packages')
command_parser = arg_parser.add_subparsers(dest='command', required=True)

# install
parser_install = command_parser.add_parser('install', help='Install a package')
parser_install.add_argument('package', help='The package to install')
parser_install.add_argument('-f', '--force', action='store_true', help='Force the installation even if the package is already installed')
parser_install.add_argument('-r', '--requirements', metavar='req_file', help='The mathsget.req file from where find the list of packages to install')

# list
parser_list = command_parser.add_parser('list', help='List all installed packages')

# uninstall
parser_uninstall = command_parser.add_parser('uninstall', help='Uninstall a package')
parser_uninstall.add_argument('package', help='The package to uninstall')
parser_uninstall.add_argument('-f', '--force', action='store_true', help='Don\'t ask for confirmation of uninstall deletions.')
parser_uninstall.add_argument('-r', '--requirements', metavar='req_file', help='The mathsget.req file from where find the list of packages to uninstall')

# update
parser_update = command_parser.add_parser('update', help='Update package to the latest version')
parser_update.add_argument('package', help='The package to update')
parser_update.add_argument('-f', '--force', action='store_true', help='Force the update even if the package is already updated')
parser_update.add_argument('-r', '--requirements', metavar='req_file', help='The mathsget.req file from where find the list of packages to update')

# search
parser_search = command_parser.add_parser('search', help='Search for packages matching the given keyword.')
parser_search.add_argument('keyword', help='The keyword to search')
parser_search.add_argument('-i', '--index', metavar='url', help='The URL of the package index')

# info
parser_info = command_parser.add_parser('info', help='Show detailed information about a package.')
parser_info.add_argument('package', help='The package to get information about')

# dependencies
parser_dependencies = command_parser.add_parser('dependencies', help='Shows dependencies for a package.')
parser_dependencies.add_argument('package', help='The package to get dependencies for')

# versions
parser_versions = command_parser.add_parser('versions', help='Lists available versions for a package.')
parser_versions.add_argument('package', help='The package to get versions for')

# changelog
parser_changelog = command_parser.add_parser('changelog', help='Shows the changelog for a package.')
parser_changelog.add_argument('package', help='The package to get the changelog for')

# license
parser_license = command_parser.add_parser('license', help='Shows the license information for a package.')
parser_license.add_argument('package', help='The package to get the license information for')

# doc
parser_doc = command_parser.add_parser('doc', help='Opens the documentation for a package (if available).')
parser_doc.add_argument('package', help='The package to open the documentation for')

# source
parser_source = command_parser.add_parser('source', help='Shows the source code for a package (if available).')
parser_source.add_argument('package', help='The package to show the source code for')

# issues
parser_issues = command_parser.add_parser('issues', help='Shows open issues for a package (if available).')
parser_issues.add_argument('package', help='The package to show open issues for')

if __name__ == '__main__':
    args = arg_parser.parse_args()
    
    match args.command:
        case 'install':
            result = core.install(args.package, args.requirements, args.force)
        case 'list':
            result = core.list_packages()
        case 'uninstall':
            result = core.uninstall(args.package, args.requirements, args.force)
        case 'update':
            result = core.update(args.package, args.requirements, args.force)
        case 'search':
            result = core.search(args.keyword, args.index)
        case 'info':
            result = core.get_info(args.package)
        case 'dependencies':
            result = core.get_dependencies(args.package)
        case 'versions':
            result = core.get_versions(args.package)
        case 'changelog':
            result = core.get_changelog(args.package)
        case 'license':
            result = core.get_license(args.package)
        case 'doc':
            result = core.open_doc(args.package)
        case 'source':
            result = core.show_source(args.package)
        case 'issues':
            result = core.open_issues(args.package)
        case _:
            result = core.InvalidCommandError(args.command)

    if isinstance(result, core.Error):
        print(result)
        sys.exit(result.code)