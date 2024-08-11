<div align="center">

<h1 style="display: flex; justify-content: center; align-items: center; gap: 0.2em;">MathGet</h1>

[![GitHub Releases](https://img.shields.io/github/downloads/foxypiratecove37350/MathGet/total?labelColor=0c0d10&color=ee3333&style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyLjI1IDM4LjVIMzUuNzVDMzYuNzE2NSAzOC41IDM3LjUgMzkuMjgzNSAzNy41IDQwLjI1QzM3LjUgNDEuMTY4MiAzNi43OTI5IDQxLjkyMTIgMzUuODkzNSA0MS45OTQyTDM1Ljc1IDQySDEyLjI1QzExLjI4MzUgNDIgMTAuNSA0MS4yMTY1IDEwLjUgNDAuMjVDMTAuNSAzOS4zMzE4IDExLjIwNzEgMzguNTc4OCAxMi4xMDY1IDM4LjUwNThMMTIuMjUgMzguNUgzNS43NUgxMi4yNVpNMjMuNjA2NSA2LjI1NThMMjMuNzUgNi4yNUMyNC42NjgyIDYuMjUgMjUuNDIxMiA2Ljk1NzExIDI1LjQ5NDIgNy44NTY0N0wyNS41IDhWMjkuMzMzTDMwLjI5MzEgMjQuNTQwN0MzMC45NzY1IDIzLjg1NzMgMzIuMDg0NiAyMy44NTczIDMyLjc2OCAyNC41NDA3QzMzLjQ1MTQgMjUuMjI0MiAzMy40NTE0IDI2LjMzMjIgMzIuNzY4IDI3LjAxNTZMMjQuOTg5OCAzNC43OTM4QzI0LjMwNjQgMzUuNDc3MiAyMy4xOTg0IDM1LjQ3NzIgMjIuNTE1IDM0Ljc5MzhMMTQuNzM2OCAyNy4wMTU2QzE0LjA1MzQgMjYuMzMyMiAxNC4wNTM0IDI1LjIyNDIgMTQuNzM2OCAyNC41NDA3QzE1LjQyMDIgMjMuODU3MyAxNi41MjgyIDIzLjg1NzMgMTcuMjExNyAyNC41NDA3TDIyIDI5LjMyOVY4QzIyIDcuMDgxODMgMjIuNzA3MSA2LjMyODgxIDIzLjYwNjUgNi4yNTU4TDIzLjc1IDYuMjVMMjMuNjA2NSA2LjI1NThaIiBmaWxsPSIjZWUzMzMzIi8+Cjwvc3ZnPg==)](https://github.com/foxypiratecove37350/MathScript/releases)

<p>MathGet, the package manager to install and manage MathScript packages</p>

</div>

MathGet is the official package manager for MathScript, making it easy to install, manage, and update MathScript packages. It's designed to be simple and efficient.

## Installation

MathGet is installed automatically by the MathScript Installer. You can still install it separately in the GitHub release.

## Usage

**Commands:**

| Command                               | Description                                           |
|---------------------------------------|-------------------------------------------------------|
| `mathget install <package-name>`      | Installs a package.                                   |
| `mathget list`                        | Lists all installed packages.                         |
| `mathget uninstall <package-name>`    | Uninstalls a package.                                 |
| `mathget update <package-name>`       | Updates a package to the latest version.              |
| `mathget search <keyword>`            | Searches for packages matching the given keyword.     |
| `mathget info <package-name>`         | Shows detailed information about a package.           |
| `mathget dependencies <package-name>` | Shows dependencies for a package.                     |
| `mathget versions <package-name>`     | Lists available versions for a package.               |
| `mathget changelog <package-name>`    | Shows the changelog for a package.                    |
| `mathget license <package-name>`      | Shows the license information for a package.          |
| `mathget doc <package-name>`          | Opens the documentation for a package (if available). |
| `mathget source <package-name>`       | Shows the source code for a package (if available).   |
| `mathget issues <package-name>`       | Shows open issues for a package (if available).       |

**Specifying Package Versions:**

| Operator | Description                                                          | Example                                 |
|----------|----------------------------------------------------------------------|-----------------------------------------|
| `==`     | Installs the exact specified version.                                | `mathget install <package-name>==1.2.3` |
| `~=`     | Installs the latest compatible version for the major version.        | `mathget install <package-name>~=1.2`   |
| `>=`     | Installs any version greater than or equal to the specified version. | `mathget install <package-name>>=1.2`   |
| `<=`     | Installs any version less than or equal to the specified version.    | `mathget install <package-name><=1.2`   |

## Features

- **Easy Installation:** Install packages with a single command.
- **Version Management:** Install specific versions or version ranges.
- **Dependency Resolution:** Automatically installs required dependencies.
- **Package Updates:** Keep your packages up-to-date with `mathget update`.
- **Package Information:** Get detailed information about installed packages.
- **Search Capabilities:** Find new packages using `mathget search`.
- **User-Friendly Interface:** Simple commands and clear output.

## Contributing

Contributions to MathGet are always welcome! Feel free to submit issues, pull requests, or suggest new features.

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Make your changes.
4. Test your changes thoroughly.
5. Submit a pull request.

## License

MathGet is licensed under the GNU General Public License v2.0. See the [`LICENSE`](./LICENSE) file for details.