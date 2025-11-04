import json
import os
from typing import Any, Dict

class ConfigLoader:
    """Simple JSON config loader for API config-driven behavior"""

    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.getcwd()
        self.config_cache: Dict[str, Any] = {}
        self.main_config = self._load_json(os.path.join('config', 'config.json'))

    def _resolve_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.join(self.base_path, path)

    def _load_json(self, rel_path: str) -> Dict[str, Any]:
        abs_path = self._resolve_path(rel_path)
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Config load error at {rel_path}: {e}")
            return {}

    def get_main(self) -> Dict[str, Any]:
        return self.main_config

    def get_geometry_mappings(self) -> Dict[str, Any]:
        path = self.main_config.get('geometry', {}).get('mappings_file', '')
        return self._load_json(path) if path else {}

    def get_geometry_operations(self) -> Dict[str, Any]:
        path = self.main_config.get('geometry', {}).get('operation_tcodes_file', '')
        return self._load_json(path) if path else {}

    def get_geometry_shapes(self) -> Dict[str, Any]:
        path = self.main_config.get('geometry', {}).get('shapes_file', '')
        return self._load_json(path) if path else {}

    def get_version_config(self, version: str) -> Dict[str, Any]:
        versions_path = self.main_config.get('versions_path', 'config/versions')
        rel = os.path.join(versions_path, f"{version}.json")
        cfg = self._load_json(rel)
        if not cfg:
            # fallback to default version
            default_version = self.main_config.get('default_version', 'fx799')
            rel = os.path.join(versions_path, f"{default_version}.json")
            cfg = self._load_json(rel)
        return cfg

    def get_encoding_options(self) -> Dict[str, Any]:
        return self.main_config.get('encoding', {})
