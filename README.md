## MathGet

MathGet is the official package manager for MathScript, making it easy to install, manage, and update MathScript packages. It's designed to be simple and efficient.

## Note

MathGet is installed automatically as part of the MathScript installer. You don't need to install it separately. 

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