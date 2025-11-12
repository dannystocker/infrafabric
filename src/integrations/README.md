# InfraFabric Integrations

External system integrations for InfraFabric production workflows.

## Available Integrations

### Home Assistant Notifications
**File:** `ha_notifications.py`
**Status:** ✓ Production Ready
**Documentation:** [docs/HOME_ASSISTANT/notifications-integration.md](../../docs/HOME_ASSISTANT/notifications-integration.md)

Complete integration with Home Assistant for:
- Mobile and persistent notifications
- Webhook automation triggers
- Custom event firing
- Device and service control
- IF.witness logging

**Quick Start:**
```python
from integrations.ha_notifications import HomeAssistantNotifications

ha = HomeAssistantNotifications(
    ha_url="http://homeassistant.local:8123",
    ha_token="your_long_lived_token"
)

ha.send_notification("Hello from InfraFabric!")
```

See `examples.py` for comprehensive usage examples.

## Coming Soon

- VMix Control Integration
- OBS Studio WebSocket Integration
- Twitch API Integration
- YouTube Live Integration
- Discord Webhooks

## Testing

```bash
# Run tests
cd /home/user/infrafabric
python -m pytest tests/test_ha_notifications.py -v

# Run with coverage
python -m pytest tests/test_ha_notifications.py --cov=src/integrations --cov-report=html
```

## Requirements

See `requirements.txt` for dependencies.

## Contributing

When adding new integrations:
1. Follow the Home Assistant integration pattern
2. Include comprehensive error handling
3. Write full test coverage
4. Document all public methods
5. Add usage examples
6. Include IF.witness logging where appropriate

## License

See [LICENSE-CODE](../../LICENSE-CODE)
