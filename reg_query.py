import os
import winreg
from typing import Any, Tuple, Callable

# Constants for registry access
WIN64READ = winreg.KEY_READ | winreg.KEY_WOW64_64KEY
WIN32READ = winreg.KEY_READ | winreg.KEY_WOW64_32KEY

# Mapping of string representation to registry hives
str2hive = {
    'HKCR': winreg.HKEY_CLASSES_ROOT,
    'HKCU': winreg.HKEY_CURRENT_USER,
    'HKLM': winreg.HKEY_LOCAL_MACHINE,
    'HKU': winreg.HKEY_USERS,
    'HKPD': winreg.HKEY_PERFORMANCE_DATA,
    'HKCC': winreg.HKEY_CURRENT_CONFIG,
}

def parse_registry_path(path: str) -> Tuple[int, str]:
    """Parse a registry path into its hive and subkey.

    Args:
        path: The registry path (e.g., 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion').

    Returns:
        A tuple containing the hive and subkey.

    Raises:
        ValueError: If the hive is invalid.
    """
    parts = path.split('\\', 1)
    hive_str = parts[0]
    hive = str2hive.get(hive_str)
    
    if hive is None:
        raise ValueError(f"Invalid registry hive: {hive_str}")
    
    subkey = parts[1] if len(parts) > 1 else ''
    return hive, subkey

def traverse(reg_path: str, match: Callable[[Any], Tuple[bool, Any]], access: int = winreg.KEY_READ) -> Any:
    """Traverse registry keys to find a value matching a specific condition.

    Args:
        reg_path: The registry path to traverse.
        match: A callable that checks if a value matches.
        access: The access rights for the registry keys.

    Returns:
        The value if found, or None if not found or an error occurs.
    """
    try:
        hive, path = parse_registry_path(reg_path)
        with winreg.OpenKey(hive, path, 0, access) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                subkey_name = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, subkey_name, 0, access) as subkey:
                    try:
                        found, value = match(subkey)
                        if found:
                            return value
                    except FileNotFoundError:
                        continue
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error accessing registry: {e}")
        return None

if __name__ == '__main__':
    # example to find the install location of 7-Zip
    def match_displayname(app_name: str) -> Callable[[Any], Tuple[bool, Any]]:
        def matcher(subkey):
            value, _ = winreg.QueryValueEx(subkey, "DisplayName")
            if app_name.lower() in value.lower():
                iloc, _ = winreg.QueryValueEx(subkey, 'InstallLocation')
                return True, iloc
            return False, None
        return matcher

    reg_path = r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
    result = traverse(reg_path, match_displayname('7-Zip'))
    if result:
        print(f"Found: {result}")
    else:
        print("Not found.")
