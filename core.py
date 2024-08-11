from pathlib import Path
import shutil
import sys
import re
import requests
import toml # type: ignore
import zipfile # type: ignore
from tqdm import tqdm # type: ignore

from errors import *
from _types import *

# ################################## Variables ###################################

package_index_repo_url: URL = URL("http://mathget-index.byethost12.com/") # free host

try:
    mathscript_install_dir: Path = Path(shutil.which("mathscript")).parent # type: ignore
except TypeError:
    err: InstallationNotFoundError = InstallationNotFoundError()
    print(err)
    sys.exit(err.code) # type: ignore

packages_install_dir: Path = mathscript_install_dir / 'user_packages'

if not packages_install_dir.exists():
    packages_install_dir.mkdir(parents=True, exist_ok=True)

(packages_install_dir / 'cached').mkdir(parents=True, exist_ok=True)
(packages_install_dir / 'metadata_files').mkdir(parents=True, exist_ok=True)
(packages_install_dir / 'metadata_files' / 'cached').mkdir(parents=True, exist_ok=True)

# ############################## Utility functions ###############################

def get_metadata_file_for_version(package_name: str, version: str = 'latest', state: str | None = None) -> Path | Error:
    path: Path = packages_install_dir / 'metadata_files' / 'cached' if state == 'cached' else packages_install_dir / 'metadata_files'
    metadata_files: list[Path] = [f for f in path.iterdir() if '-'.join(f.name.split('-')[:-1]) == package_name]

    def get_version(filename: str) -> str | Error:
        match = re.search(r'-(.*?)\.metadata$', filename)
        if match:
            return match.group(1)
        return InternalError(package_name)

    if metadata_files == []:
        return PackageMetadataNotFoundError(package_name)

    versions: list[str | Error] = [get_version(f.name) for f in metadata_files]

    err = next((item for item in versions if isinstance(item, Error)), None)
    if err:
        return err
    
    versions = sorted(versions, key=lambda v: list(map(int, v.split('.')))) # type: ignore

    if version == 'latest':
        version = versions[-1] # type: ignore
    elif version.startswith('^'):
        version = version[1:]
        version = max(version, versions[-1]) # type: ignore
    elif version.startswith('_'):
        version = version[1:]
        version = min(version, versions[0]) # type: ignore
    elif version.startswith('~'):
        version = version[1:]
        matching_versions = [v for v in versions if v.startswith(version) or v == version] # type: ignore
        version = matching_versions[-1] if matching_versions else None # type: ignore

    if version not in versions:
        return PackageMetadataNotFoundError(package_name)

    filename = f'{package_name}-{version}.metadata'

    return path / filename

def get_local_metadata(package_name: str, version: str = 'latest') -> dict | Error:
    """Gets the metadata of a package from the local package index

    Args:
    package_name (str): The name of the package to get metadata for
    version (str, optional): The version of the package to get metadata for. Defaults to 'latest'

    Returns:
    dict: The metadata of the package
    """

    package_metadata_path: Path | Error = get_metadata_file_for_version(package_name, version)

    if isinstance(package_metadata_path, Error):
        return package_metadata_path

    if not package_metadata_path.exists():
        return PackageMetadataNotFoundError(package_name)
    
    with open(package_metadata_path) as f:
        return toml.load(f)

def get_local_cached_metadata(package_name: str, version: str = 'latest') -> dict | Error:
    """Gets the metadata of a package from the local cached packages index

    Args:
    package_name (str): The name of the package to get metadata for
    version (str, optional): The version of the package to get metadata for. Defaults to 'latest'

    Returns:
    dict: The metadata of the package
    """

    package_metadata_path: Path | Error = get_metadata_file_for_version(package_name, version, 'cached')
    
    if isinstance(package_metadata_path, Error):
        return package_metadata_path

    if not package_metadata_path.exists():
        return PackageNotFoundError(package_name, 'cached')
    
    with open(package_metadata_path) as f:
        return toml.load(f)

def get_remote_metadata(package_name: str, version: str = 'latest') -> dict | Error:
    """Gets the metadata of a package from the remote package index

    Args:
    package_name (str): The name of the package to get metadata for
    version (str, optional): The version of the package to get metadata for. Defaults to 'latest'

    Returns:
    dict: The metadata of the package
    """
    
    try:
        response: requests.Response = requests.get(str(package_index_repo_url / 'packages' / 'metadata.php' / f'{package_name}?version={version}'))
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.ConnectionError):
            return NetworkError("Unable to connect to the package index.")
        elif isinstance(e, requests.exceptions.Timeout):
            return NetworkError("Request timed out.")
        else:
            return NetworkError(f"An error occurred while fetching package metadata: {e}")

    
    if response.status_code == 404:
        return PackageNotFoundError(package_name, 'remote')
    
    if not (200 <= response.status_code <= 299):
        return HTTPError(response.status_code)

    return toml.loads(response.text)

def download_package_from_index(package_name: str, version: str, path: Path) -> None | Error:
    """Downloads a package from the package index.

    Args:
    package_name (str): The name of the package to download.
    version (str): The version of the package to download.
    path (Path): The path to the directory where the package will be downloaded.

    Returns:
    None | Error: The error (None if there isn't)
    """
    try:
        response: requests.Response = requests.get(str(package_index_repo_url / 'packages' / 'install.php' / f'{package_name}?version={version}'), stream=True)
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.ConnectionError):
            return NetworkError("Unable to connect to the package index.")
        elif isinstance(e, requests.exceptions.Timeout):
            return NetworkError("Request timed out.")
        else:
            return NetworkError(f"An error occurred while fetching package metadata: {e}")

    if response.status_code == 404:
        return PackageNotFoundError(package_name, 'remote')
    
    if not (200 <= response.status_code <= 299):
        return HTTPError(response.status_code)

    total_size = int(response.headers.get('content-length', 0))
    with open(path, 'wb') as f:
        with tqdm(ascii=' ━', colour='#00af50', bar_format='{desc}: {percentage:3.0f}% {bar:50} {n_fmt}/{total_fmt}', total=total_size, unit='B', unit_scale=True, desc=f"Downloading {package_name}-{version}") as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    return None

def download_metadata_from_index(package_name: str, version: str, path: Path) -> None | Error:
    """Downloads a package from the package index.

    Args:
    package_name (str): The name of the package to download.
    version (str): The version of the package to download.
    path (Path): The path to the directory where the package will be downloaded.

    Returns:
    None | Error: The error (None if there isn't)
    """
    try:
        response: requests.Response = requests.get(str(package_index_repo_url / 'packages' / 'metadata.php' / f'{package_name}?version={version}'))
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.ConnectionError):
            return NetworkError("Unable to connect to the package index.")
        elif isinstance(e, requests.exceptions.Timeout):
            return NetworkError("Request timed out.")
        else:
            return NetworkError(f"An error occurred while fetching package metadata: {e}")

    if response.status_code == 404:
        return PackageNotFoundError(package_name, 'remote')
    
    if not (200 <= response.status_code <= 299):
        return HTTPError(response.status_code)

    with open(path, 'w') as f:
        f.write(response.text)

    return None

# ############################## Command functions ###############################

def install(package_name: str | None = None, requirements_file: str | None = None, force: bool = False) -> None | Error:
    """Installs a package
    
    Args:
    package_name (str | None): The name of the package to install. Defaults to None.
    requirements_file (str | None): The path to the requirements file. Defaults to None.
    force (bool): Whether to force the installation of the package Defaults to False.

    Returns:
    None | Error: The error (None if there isn't)
    """

    if package_name is not None:
        metadata: dict | Error = get_remote_metadata(package_name)

        if isinstance(metadata, Error):
            return metadata

        if not force:
            local_metadata: dict | Error = get_local_metadata(package_name)
            if isinstance(local_metadata, dict):
                if local_metadata['package']['version'] == metadata['package']['version']:
                    print(f'Package "{package_name}" is already installed.\nVersion {metadata["package"]["version"]} is already installed.\nUse `mathget update` to update the package.')
                    return None
        
        package_dir: Path = packages_install_dir / f'{package_name}'
        if package_dir.exists():
            shutil.rmtree(package_dir)

        package_dir.mkdir(parents=True, exist_ok=True)

        zip_file_path: Path = packages_install_dir / 'cached' / f'{package_name}-{metadata["package"]["version"]}.zip'
        
        err: Error | None = download_package_from_index(package_name, metadata['package']['version'], zip_file_path) # type: ignore
        if err:
            return err

        print(f'Unzipping {package_name}-{metadata["package"]["version"]}.')
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            with tqdm(ascii=' ━', colour='#00af50', bar_format='{desc}: {percentage:3.0f}% {bar:50} {n_fmt}/{total_fmt} ', total=len(zip_ref.infolist()), unit='files', desc="Unzipping") as pbar:
                for i, file in enumerate(zip_ref.infolist()):
                    zip_ref.extract(file, package_dir)
                    pbar.update(1)

        zip_file_path.unlink()

        print(f'Package "{package_name}" installed.\nVersion {metadata["package"]["version"]} installed.')

        err: Error | None = download_metadata_from_index(package_name, metadata['package']['version'], packages_install_dir / 'metadata_files' / f'{package_name}-{metadata["package"]["version"]}.metadata') # type: ignore
        if err:
            return err

        err: Error | None = download_metadata_from_index(package_name, metadata['package']['version'], packages_install_dir / 'metadata_files' / 'cached' / f'{package_name}-{metadata["package"]["version"]}.metadata') # type: ignore
        if err:
            return err

        if 'dependencies' in metadata and metadata['dependencies']:
            for dependency in metadata['dependencies']:
                if dependency == 'mathscript': continue
                err: Error | None = install(dependency, force=True) # type: ignore
                if err:
                    return err

        return None
    elif requirements_file is not None:
        requirements_file_path = Path(requirements_file)

        if not requirements_file_path.exists() or not requirements_file_path.is_file():
            return FileOrDirectoryNotFoundError(requirements_file)
        
        with open(requirements_file_path, 'r') as f:
            requirements = f.readlines()

        for requirement in requirements:
            requirement = requirement.strip()
            if requirement:
                err: Error | None = install(requirement, force=force) # type: ignore
                if err:
                    return err
        return None

    return InvalidArgumentsError('package', '-r/--requirements')

def list_packages() -> None | Error:
    """Lists all packages in the package index.
    
    Returns:
    None | Error: The error (None if there isn't)
    """

    print('Installed packages:\n')

    packages_path_list = [
        path for path in packages_install_dir.iterdir()
        if path.is_dir() and path.name not in ('metadata_files',)
        and (path / 'init.mscr').exists() and (path / 'init.mscr').is_file()
    ]

    if packages_path_list == []:
        print('(None)')

    for package_path in packages_path_list:
        metadata = get_local_metadata(package_path.name)

        if isinstance(metadata, Error):
            return metadata
        
        name = package_path.name
        version = metadata['package']['version']
        print(f'{name}=={version}')

    return None

def uninstall(package_name: str | None = None, requirements_file: str | None = None, force: bool = False) -> None | Error:
    """Uninstalls a package.

    Args:
    package_name (str | None): The name of the package to uninstall. Defaults to None.
    requirements_file (str | None): The path to the requirements file. Defaults to None.
    force (bool): Whether to force the uninstallation of the package Defaults to False.

    Returns:
    None | Error: The error (None if there isn't)
    """

    if package_name is not None:
        package_dir: Path = packages_install_dir / f'{package_name}'

        if not package_dir.exists():
            return PackageNotFoundError(package_name)

        metadata: dict | Error = get_local_metadata(package_name)

        if isinstance(metadata, Error):
            return metadata

        if not force:
            confirm = input(f'Are you sure you want to uninstall package "{package_name}"? (y/N) ')

            if confirm.lower() != 'y':
                print('Aborting uninstallation.')
                return None

        print(f'Uninstalling package "{package_name}" version {metadata["package"]["version"]}.')

        with tqdm(ascii=' ━', colour='#00af50', bar_format='{desc}: {percentage:3.0f}% {bar:50} {n_fmt}/{total_fmt} ', total=len(list(package_dir.iterdir())), unit='files', desc="Deleting files") as pbar:
            for file in package_dir.iterdir():
                if file.is_file():
                    file.unlink()
                    pbar.update(1)

        print('Deleting directories...')
        shutil.rmtree(package_dir)

        metadata_file_path: Path = packages_install_dir / 'metadata_files' / f'{package_name}-{metadata["package"]["version"]}.metadata'
        if metadata_file_path.exists():
            metadata_file_path.unlink()

        metadata_file_path: Path = packages_install_dir / 'metadata_files' / 'cached' / f'{package_name}-{metadata["package"]["version"]}.metadata' # type: ignore
        if metadata_file_path.exists():
            metadata_file_path.unlink()

        print(f'Package "{package_name}" uninstalled.')

        return None
    elif requirements_file is not None:
        requirements_file_path = Path(requirements_file)

        if not requirements_file_path.exists() or not requirements_file_path.is_file():
            return FileOrDirectoryNotFoundError(requirements_file)
        
        with open(requirements_file_path, 'r') as f:
            requirements = f.readlines()

        for requirement in requirements:
            requirement = requirement.strip()
            if requirement:
                err: Error | None = uninstall(requirement, force=force) # type: ignore
                if err:
                    return err
        return None

    return InvalidArgumentsError('package', '-r/--requirements')

def update(package_name: str | None = None, requirements_file: str | None = None, force: bool = False) -> None | Error:
    """Updates a package to the latest version available in the package index.

    Args:
    package_name (str | None): The name of the package to update. Defaults to None.
    requirements_file (str | None): The path to the requirements file. Defaults to None.
    force (bool): Whether to force the update of the package. Defaults to False.

    Returns:
    None | Error: The error (None if there isn't)
    """

    if package_name is not None:
        metadata: dict | Error = get_remote_metadata(package_name)

        if isinstance(metadata, Error):
            return metadata

        local_metadata: dict | Error = get_local_metadata(package_name)
        if isinstance(local_metadata, Error):
            return local_metadata

        if local_metadata['package']['version'] == metadata['package']['version'] and force == False:
            print(f'Package "{package_name}" is already up to date.\nVersion {metadata["package"]["version"]} is already installed.')
            return None

        print(f'Updating package "{package_name}" to version {metadata["package"]["version"]}.')

        package_dir: Path = packages_install_dir / package_name
        if package_dir.exists():
            shutil.rmtree(package_dir)

        package_dir.mkdir(parents=True, exist_ok=True)

        zip_file_path: Path = packages_install_dir / 'cached' / f'{package_name}-{metadata["package"]["version"]}.zip'
        
        err: Error | None = download_package_from_index(package_name, metadata['package']['version'], zip_file_path) # type: ignore
        if isinstance(err, Error):
            return err

        print(f'Unzipping {package_name}-{metadata["package"]["version"]}.')
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            with tqdm(ascii=' ━', colour='#00af50', bar_format='{desc}: {percentage:3.0f}% {bar:50} {n_fmt}/{total_fmt} ', total=len(zip_ref.infolist()), unit='files', desc="Unzipping") as pbar:
                for i, file in enumerate(zip_ref.infolist()):
                    zip_ref.extract(file, package_dir)
                    pbar.update(1)

        zip_file_path.unlink()

        err: Error = download_metadata_from_index(package_name, metadata['package']['version'], packages_install_dir / 'metadata_files' / f'{package_name}-{metadata["package"]["version"]}.metadata') # type: ignore
        if err:
            return err

        err: Error = download_metadata_from_index(package_name, metadata['package']['version'], packages_install_dir / 'metadata_files' / 'cached' / f'{package_name}-{metadata["package"]["version"]}.metadata') # type: ignore
        if err:
            return err

        if 'dependencies' in metadata and metadata['dependencies']:
            for dependency in metadata['dependencies']:
                if dependency == 'mathscript': continue
                err: Error = update(dependency, force=True) # type: ignore
                if err:
                    return err

        print(f'Package "{package_name}" updated to version {metadata["package"]["version"]}.')

        return None
    elif requirements_file is not None:
        requirements_file_path = Path(requirements_file)

        if not requirements_file_path.exists() or not requirements_file_path.is_file():
            return FileOrDirectoryNotFoundError(requirements_file)
        
        with open(requirements_file_path, 'r') as f:
            requirements = f.readlines()

        for requirement in requirements:
            requirement = requirement.strip()
            if requirement:
                err: Error = update(requirement, force=force) # type: ignore
                if err:
                    return err
        return None

    return InvalidArgumentsError('package', '-r/--requirements')

def search(keyword: str, package_index_url: str | None = None) -> None | Error: # type: ignore
    """Searches the package index for packages matching the keyword.

    Args:
    keyword (str): The keyword to search for
    package_index_url (str | None): The URL of the package index. Defaults to None.
    """

    if package_index_url is not None:
        package_index_url: URL = URL(package_index_url) # type: ignore
    else:
        package_index_url: URL = package_index_repo_url # type: ignore

    try:
        response: requests.Response = requests.get(str(package_index_url / 'search.php' / keyword)) # type: ignore
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.ConnectionError):
            return NetworkError("Unable to connect to the package index.")
        elif isinstance(e, requests.exceptions.Timeout):
            return NetworkError("Request timed out.")
        else:
            return NetworkError(f"An error occurred while fetching package metadata: {e}")

    if response.status_code == 404:
        return PackageNotFoundError(keyword, 'remote')
    
    if not (200 <= response.status_code <= 299):
        return HTTPError(response.status_code)

    packages = toml.loads(response.text)['packages']
    
    print(f'Found {len(packages)} packages matching the keyword "{keyword}":')

    if packages == []:
        print('(None)')
    else:
        for package in packages:
            print(f'- {package["name"]}=={package["version"]} (License: {package["license"] if "license" in package else "Not specified"})')

    return None

def get_info(package_name: str) -> None | Error:
    """Retrieves information about a package from the package index.

    Args:
    packaged_name (str): The name of the package to retrieve informations about

    Returns:
    None | Error: The error (None if there isn't)
    """

    metadata: dict | Error = get_remote_metadata(package_name)

    if isinstance(metadata, Error):
        return metadata

    print(f'Package: {metadata["package"]["name"]}')
    print(f'Version: {metadata["package"]["version"]}')
    print(f'Description: {metadata["package"]["description"] if "description" in metadata["package"] else "Not specified"}')
    print(f'Author: {metadata["package"]["author"] if "author" in metadata["package"] else "Not specified"}')
    print(f'License: {metadata["package"]["license"] if "license" in metadata["package"] else "Not specified"}')
    print(f'Homepage: {metadata["package"]["homepage"] if "homepage" in metadata["package"] else "Not specified"}')
    
    if 'keywords' in metadata['package'] and metadata['package']['keywords']:
        print(f'Keywords:')
        for keyword in metadata['package']['keywords']:
            print(f'- {keyword}')
    else:
        print(f'Keywords: (None)')

    if 'dependencies' in metadata and metadata['dependencies']:
        print(f'Dependencies:')
        for dependency_name, dependency_version in metadata['dependencies'].items():
            op = ('>' if dependency_version.startswith('^')
                  else '<' if dependency_version.startswith('_')
                  else '~' if dependency_version.startswith('~')
                  else '=')
            if op != '=':
                dependency_version = dependency_version[1:]

            print(f'- {dependency_name}{op}={dependency_version}')
    else:
        print(f'Dependencies: (None)')

    return None

def get_dependencies(package_name: str) -> None | Error:
    """Retrieves the dependencies of a package from the package index.

    Args:
    packaged_name (str): The name of the package to retrive dependencies of

    Returns:
    None | Error: The error (None if there isn't)
    """

    metadata: dict | Error = get_remote_metadata(package_name)

    if isinstance(metadata, Error):
        return metadata
    
    if 'dependencies' in metadata and metadata['dependencies']:
        print(f'Dependencies:')
        for dependency_name, dependency_version in metadata['dependencies'].items():
            op = ('>' if dependency_version.startswith('^')
                  else '<' if dependency_version.startswith('_')
                  else '~' if dependency_version.startswith('~')
                  else '=')
            if op != '=':
                dependency_version = dependency_version[1:]

            print(f'- {dependency_name}{op}={dependency_version}')
    else:
        print(f'Dependencies for {metadata["package"]["name"]}: (None)')

    return None

def get_versions(package_name: str) -> None | Error:
    """Retrieves the versions of a package from the package index.

    Args:
    packaged_name (str): The name of the package to retrive its versions

    Returns:
    None | Error: The error (None if there isn't)
    """

    try:
        response: requests.Response = requests.get(str(package_index_repo_url / 'packages' / 'versions.php' / f'{package_name}'))
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.ConnectionError):
            return NetworkError("Unable to connect to the package index.")
        elif isinstance(e, requests.exceptions.Timeout):
            return NetworkError("Request timed out.")
        else:
            return NetworkError(f"An error occurred while fetching package metadata: {e}")

    if response.status_code == 404:
        return PackageNotFoundError(package_name, 'remote')
    
    if not (200 <= response.status_code <= 299):
        return HTTPError(response.status_code)

    versions = toml.loads(response.text)['versions']

    if versions == []:
        print(f'No versions found for package "{package_name}".')
    else:
        print(f'Versions for package "{package_name}":')
        for version in versions:
            print(f'- {version}')
    
    return None

def get_changelog(package_name: str) -> None | Error:
    """Retrieves the changelog of a package from the package index.

    Args:
    packaged_name (str): The name of the package to retrive its changelog

    Returns:
    None | Error: The error (None if there isn't)
    """

    metadata = get_remote_metadata(package_name)
    if isinstance(metadata, Error):
        return metadata
    
    changelog = metadata['package']['changelog'] if 'changelog' in metadata['package'] else []

    if changelog == []:
        print(f'No changelog found for package "{package_name}".')
    else:
        print(f'Changelog for package "{package_name}":')
        for change in changelog:
            print(f'- {change}')

    return None

def get_license(package_name: str) -> None | Error:
    """Retrieves the license of a package from the package index.

    Args:
    packaged_name (str): The name of the package to retrive its license

    Returns:
    None | Error: The error (None if there isn't)
    """

    metadata: dict | Error = get_remote_metadata(package_name)

    if isinstance(metadata, Error):
        return metadata

    if 'license' in metadata['package']:
        print(f'License for package "{metadata["package"]["name"]}": {metadata["package"]["license"]}')
    else:
        print(f'License for package "{metadata["package"]["name"]}": Not specified.')
    
    return None

def open_doc(package_name: str) -> None | Error:
    """Opens the documentation of a package in the default browser.

    Args:
    packaged_name (str): The name of the package to open its documentation

    Returns:
    None | Error: The error (None if there isn't)
    """

    metadata: dict | Error = get_remote_metadata(package_name)

    if isinstance(metadata, Error):
        return metadata

    if 'homepage' in metadata['package']:
        try:
            import webbrowser
            webbrowser.open_new_tab(metadata['package']['homepage'])
        except ImportError:
            return InternalError("The `webbrowser` module is not available.")
    else:
        print(f'No documentation found for package "{metadata["package"]["name"]}".')
    
    return None

def show_source(package_name: str) -> None | Error:
    """Opens the source code of a package in the default editor.

    Args:
    packaged_name (str): The name of the package to open its source code

    Returns:
    None | Error: The error (None if there isn't)
    """

    metadata: dict | Error = get_remote_metadata(package_name)

    if isinstance(metadata, Error):
        return metadata

    try:
        import webbrowser
        webbrowser.open_new_tab(f'{metadata["package"]["homepage"]}')
    except ImportError:
        return InternalError("The `webbrowser` module is not available.")
    
    return None

def open_issues(package_name: str) -> None | Error:
    """Opens the issues of a package in the default browser.

    Args:
    packaged_name (str): The name of the package to open its issues

    Returns:
    None | Error: The error (None if there isn't)
    """

    metadata: dict | Error = get_remote_metadata(package_name)

    if isinstance(metadata, Error):
        return metadata

    if 'homepage' in metadata['package']:
        try:
            import webbrowser
            webbrowser.open_new_tab(f'{metadata["package"]["homepage"]}/issues')
        except ImportError:
            return InternalError("The `webbrowser` module is not available.")
    else:
        print(f'No issues found for package "{metadata["package"]["name"]}".')
    
    return None