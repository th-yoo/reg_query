# reg\_query
**reg_query** is a Python library for querying the Windows Registry to find specified values and keys efficiently.

## Installation
```powershell
PS > pip install reg_query
```

## Usage
### Find 7-Zip Install Location from the Registry
This example demonstrates how to find the install location of 7-Zip by querying the Windows Registry.

```python
import winreg
from typing import Callable, Any, Tuple
from reg_query import traverse

def match_displayname(app_name: str) -> Callable[[Any], Tuple[bool, Any]]:
    """Matcher function to find the install location based on display name."""
    def matcher(subkey):
        value, _ = winreg.QueryValueEx(subkey, "DisplayName")
        if app_name.lower() in value.lower():
    	iloc, _ = winreg.QueryValueEx(subkey, 'InstallLocation')
    	return True, iloc
        return False, None
    return matcher

# Specify the registry path for installed applications
reg_path = r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'

# Traverse the registry using the matcher
result = traverse(reg_path, match_displayname('7-Zip'))

if result:
    print(f"Found: {result}")
else:
    print("Not found.")
```
## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For any questions or support, please reach out to me via [GitHub Issues](https://github.com/th-yoo/reg_query/issues).
