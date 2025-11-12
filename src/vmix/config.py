"""
IF.vmix Configuration Management

Manages vMix instance configurations stored in ~/.if/vmix/instances.yaml
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .models import VMixInstance


class VMixConfigError(Exception):
    """Configuration error"""
    pass


class VMixConfig:
    """
    vMix instance configuration manager.

    Philosophy: Simple YAML-based config stored in user's home directory.
    Store multiple vMix instances for easy switching.

    Config location: ~/.if/vmix/instances.yaml
    Format:
        instances:
          myvmix:
            host: 192.168.1.100
            port: 8088
            added_at: 2025-11-11T23:00:00Z
          studio2:
            host: 192.168.1.101
            port: 8088
            added_at: 2025-11-11T22:00:00Z
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config manager.

        Args:
            config_path: Optional config file path (default: ~/.if/vmix/instances.yaml)
        """
        self.config_path = config_path or Path.home() / '.if' / 'vmix' / 'instances.yaml'
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
            raise VMixConfigError(f"Failed to parse config file: {e}")
        except Exception as e:
            raise VMixConfigError(f"Failed to read config file: {e}")

    def _write_config(self, config: Dict):
        """Write config to YAML file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise VMixConfigError(f"Failed to write config file: {e}")

    def add_instance(self, name: str, host: str, port: int = 8088) -> VMixInstance:
        """
        Add vMix instance to config.

        Args:
            name: Instance name (unique identifier)
            host: vMix host IP or hostname
            port: vMix API port (default: 8088)

        Returns:
            VMixInstance object

        Raises:
            VMixConfigError: If instance already exists
        """
        config = self._read_config()

        if name in config['instances']:
            raise VMixConfigError(f"Instance '{name}' already exists")

        instance = VMixInstance(
            name=name,
            host=host,
            port=port,
            added_at=datetime.utcnow().isoformat()
        )

        config['instances'][name] = {
            'host': host,
            'port': port,
            'added_at': instance.added_at
        }

        self._write_config(config)
        return instance

    def remove_instance(self, name: str) -> bool:
        """
        Remove vMix instance from config.

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

    def get_instance(self, name: str) -> Optional[VMixInstance]:
        """
        Get vMix instance by name.

        Args:
            name: Instance name

        Returns:
            VMixInstance or None if not found
        """
        config = self._read_config()

        if name not in config['instances']:
            return None

        data = config['instances'][name]
        return VMixInstance(
            name=name,
            host=data['host'],
            port=data.get('port', 8088),
            added_at=data.get('added_at')
        )

    def list_instances(self) -> List[VMixInstance]:
        """
        List all configured vMix instances.

        Returns:
            List of VMixInstance objects
        """
        config = self._read_config()
        instances = []

        for name, data in config['instances'].items():
            instances.append(VMixInstance(
                name=name,
                host=data['host'],
                port=data.get('port', 8088),
                added_at=data.get('added_at')
            ))

        # Sort by name
        instances.sort(key=lambda x: x.name)
        return instances

    def instance_exists(self, name: str) -> bool:
        """Check if instance exists"""
        config = self._read_config()
        return name in config['instances']

    def update_instance(self, name: str, host: Optional[str] = None,
                       port: Optional[int] = None) -> Optional[VMixInstance]:
        """
        Update instance configuration.

        Args:
            name: Instance name
            host: New host (optional)
            port: New port (optional)

        Returns:
            Updated VMixInstance or None if not found
        """
        config = self._read_config()

        if name not in config['instances']:
            return None

        if host:
            config['instances'][name]['host'] = host
        if port:
            config['instances'][name]['port'] = port

        self._write_config(config)
        return self.get_instance(name)
