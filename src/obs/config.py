"""
IF.obs Configuration Management

Manages OBS instance configurations stored in ~/.if/obs/instances.yaml
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import base64

from .models import OBSInstance


class OBSConfigError(Exception):
    """Configuration error"""
    pass


class OBSConfig:
    """
    OBS instance configuration manager.

    Philosophy: Simple YAML-based config stored in user's home directory.
    Store multiple OBS instances for easy switching.

    Config location: ~/.if/obs/instances.yaml
    Format:
        instances:
          myobs:
            host: localhost
            port: 4455
            password: <base64-encoded>
            added_at: 2025-11-12T00:00:00Z
          studio2:
            host: 192.168.1.100
            port: 4455
            password: <base64-encoded>
            added_at: 2025-11-12T01:00:00Z
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config manager.

        Args:
            config_path: Optional config file path (default: ~/.if/obs/instances.yaml)
        """
        self.config_path = config_path or Path.home() / '.if' / 'obs' / 'instances.yaml'
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
            raise OBSConfigError(f"Failed to parse config file: {e}")
        except Exception as e:
            raise OBSConfigError(f"Failed to read config file: {e}")

    def _write_config(self, config: Dict):
        """Write config to YAML file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise OBSConfigError(f"Failed to write config file: {e}")

    def _encode_password(self, password: str) -> str:
        """Encode password for storage"""
        return base64.b64encode(password.encode()).decode()

    def _decode_password(self, encoded: str) -> str:
        """Decode password from storage"""
        try:
            return base64.b64decode(encoded.encode()).decode()
        except Exception:
            # If decoding fails, assume it's already decoded (legacy support)
            return encoded

    def add_instance(self, name: str, host: str, port: int = 4455,
                    password: Optional[str] = None) -> OBSInstance:
        """
        Add OBS instance to config.

        Args:
            name: Instance name (unique identifier)
            host: OBS host IP or hostname
            port: OBS WebSocket port (default: 4455)
            password: WebSocket password (optional)

        Returns:
            OBSInstance object

        Raises:
            OBSConfigError: If instance already exists
        """
        config = self._read_config()

        if name in config['instances']:
            raise OBSConfigError(f"Instance '{name}' already exists")

        instance = OBSInstance(
            name=name,
            host=host,
            port=port,
            password=password,
            added_at=datetime.utcnow().isoformat()
        )

        instance_data = {
            'host': host,
            'port': port,
            'added_at': instance.added_at
        }

        # Store encoded password if provided
        if password:
            instance_data['password'] = self._encode_password(password)

        config['instances'][name] = instance_data
        self._write_config(config)
        return instance

    def remove_instance(self, name: str) -> bool:
        """
        Remove OBS instance from config.

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

    def get_instance(self, name: str) -> Optional[OBSInstance]:
        """
        Get OBS instance by name.

        Args:
            name: Instance name

        Returns:
            OBSInstance or None if not found
        """
        config = self._read_config()

        if name not in config['instances']:
            return None

        data = config['instances'][name]

        # Decode password if present
        password = None
        if 'password' in data and data['password']:
            password = self._decode_password(data['password'])

        return OBSInstance(
            name=name,
            host=data['host'],
            port=data.get('port', 4455),
            password=password,
            added_at=data.get('added_at')
        )

    def list_instances(self) -> List[OBSInstance]:
        """
        List all configured OBS instances.

        Returns:
            List of OBSInstance objects
        """
        config = self._read_config()
        instances = []

        for name, data in config['instances'].items():
            # Decode password if present
            password = None
            if 'password' in data and data['password']:
                password = self._decode_password(data['password'])

            instances.append(OBSInstance(
                name=name,
                host=data['host'],
                port=data.get('port', 4455),
                password=password,
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
                       port: Optional[int] = None,
                       password: Optional[str] = None) -> Optional[OBSInstance]:
        """
        Update instance configuration.

        Args:
            name: Instance name
            host: New host (optional)
            port: New port (optional)
            password: New password (optional)

        Returns:
            Updated OBSInstance or None if not found
        """
        config = self._read_config()

        if name not in config['instances']:
            return None

        if host:
            config['instances'][name]['host'] = host
        if port:
            config['instances'][name]['port'] = port
        if password is not None:
            if password:
                config['instances'][name]['password'] = self._encode_password(password)
            else:
                # Remove password if empty string provided
                config['instances'][name].pop('password', None)

        self._write_config(config)
        return self.get_instance(name)
