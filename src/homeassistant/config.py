"""
IF.homeassistant Configuration Management

Manages Home Assistant instance configurations stored in ~/.if/home-assistant/instances.yaml
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .models import HAInstance


class HAConfigError(Exception):
    """Configuration error"""
    pass


class HAConfig:
    """
    Home Assistant instance configuration manager.

    Philosophy: Simple YAML-based config stored in user's home directory.
    Store multiple HA instances for easy switching.

    Config location: ~/.if/home-assistant/instances.yaml
    Format:
        instances:
          myhome:
            url: http://homeassistant.local:8123
            token: eyJ0eXAiOiJKV1Qi...
            added_at: 2025-11-12T00:00:00Z
          remote:
            url: https://ha.example.com
            token: eyJ0eXAi...
            added_at: 2025-11-11T22:00:00Z
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config manager.

        Args:
            config_path: Optional config file path (default: ~/.if/home-assistant/instances.yaml)
        """
        self.config_path = config_path or Path.home() / '.if' / 'home-assistant' / 'instances.yaml'
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize config file if it doesn't exist
        if not self.config_path.exists():
            self._write_config({'instances': {}})

    def _read_config(self) -> Dict:
        """Read config from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {'instances': {}}
        except yaml.YAMLError as e:
            raise HAConfigError(f"Failed to parse config file: {e}")
        except Exception as e:
            raise HAConfigError(f"Failed to read config file: {e}")

    def _write_config(self, config: Dict):
        """Write config to YAML file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise HAConfigError(f"Failed to write config file: {e}")

    def add_instance(self, name: str, url: str, token: str) -> HAInstance:
        """
        Add Home Assistant instance to config.

        Args:
            name: Instance name (unique identifier)
            url: Home Assistant URL (e.g., http://homeassistant.local:8123)
            token: Long-lived access token

        Returns:
            HAInstance object

        Raises:
            HAConfigError: If instance already exists
        """
        config = self._read_config()

        if name in config['instances']:
            raise HAConfigError(f"Instance '{name}' already exists")

        # Ensure URL doesn't have trailing slash
        url = url.rstrip('/')

        instance = HAInstance(
            name=name,
            url=url,
            token=token,
            added_at=datetime.utcnow().isoformat()
        )

        config['instances'][name] = {
            'url': url,
            'token': token,
            'added_at': instance.added_at
        }

        self._write_config(config)
        return instance

    def remove_instance(self, name: str) -> bool:
        """
        Remove Home Assistant instance from config.

        Args:
            name: Instance name

        Returns:
            True if removed, False if not found
        """
        config = self._read_config()

        if name not in config['instances']:
            return False

        del config['instances'][name]
        self._write_config(config)
        return True

    def get_instance(self, name: str) -> Optional[HAInstance]:
        """
        Get Home Assistant instance by name.

        Args:
            name: Instance name

        Returns:
            HAInstance or None if not found
        """
        config = self._read_config()

        if name not in config['instances']:
            return None

        data = config['instances'][name]
        return HAInstance(
            name=name,
            url=data['url'],
            token=data['token'],
            added_at=data.get('added_at')
        )

    def list_instances(self) -> List[HAInstance]:
        """
        List all configured Home Assistant instances.

        Returns:
            List of HAInstance objects
        """
        config = self._read_config()
        instances = []

        for name, data in config['instances'].items():
            instances.append(HAInstance(
                name=name,
                url=data['url'],
                token=data['token'],
                added_at=data.get('added_at')
            ))

        # Sort by name
        instances.sort(key=lambda x: x.name)
        return instances

    def instance_exists(self, name: str) -> bool:
        """Check if instance exists"""
        config = self._read_config()
        return name in config['instances']

    def update_instance(self, name: str, url: Optional[str] = None,
                       token: Optional[str] = None) -> Optional[HAInstance]:
        """
        Update instance configuration.

        Args:
            name: Instance name
            url: New URL (optional)
            token: New token (optional)

        Returns:
            Updated HAInstance or None if not found
        """
        config = self._read_config()

        if name not in config['instances']:
            return None

        if url:
            config['instances'][name]['url'] = url.rstrip('/')
        if token:
            config['instances'][name]['token'] = token

        self._write_config(config)
        return self.get_instance(name)
