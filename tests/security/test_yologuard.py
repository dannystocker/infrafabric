from infrafabric.core.security.yologuard import (
    SecretRedactorV3,
    find_secret_relationships,
    confucian_relationship_score,
)

redactor = SecretRedactorV3()

SIMPLE_PASSWORD_JSON = '{"username": "alice", "password": "Th!sIsS3cret", "host": "db.host"}'
API_KEY_BLOCK = 'openai_api_key = "sk-test-example-key-1234567890"\nopenai_api_endpoint = "https://api.openai.com/v1/chat"'
JWT_HEADER = 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.K9c4gkZuUx2W-XYSmF9A4yR7f5kb1y-WD79U08AOoJo'
BASE64_SECRET = 'encoded = "QUtJQVo4NjdWRm91dFIxU1RSb2lTd0JkRz09"'
NOISE_TOKEN = 'noise=ZnVuY3Rpb25TZWFyY2g3NDU2Nzg5MGFiY2RlZg=='
LARGE_CONFIG = '\n'.join(['log_level: info', 'endpoint: https://status.example.com'] * 50)
HEX_JSON = '{"token_hex": "4d6f6f6e736861646566"}'
KEY_ENDPOINT_SCATTERED = 'sk-test-key-12345\n# random comments\nhttps://api.sensitive-host/v2/submit'


def test_detect_simple_password_relationship():
    results = redactor.scan_with_patterns(SIMPLE_PASSWORD_JSON)
    assert any('PASSWORD_REDACTED' == pattern for pattern, _ in results)
    username_pos = SIMPLE_PASSWORD_JSON.find("alice")
    relationships = find_secret_relationships("alice", SIMPLE_PASSWORD_JSON, username_pos)
    assert any(rel[0] == 'user-password' for rel in relationships)
    assert confucian_relationship_score(relationships) > 0.8


def test_api_key_endpoint_scoring():
    matches = redactor.predecode_and_rescan(API_KEY_BLOCK)
    assert any(pattern.endswith('_REDACTED') for pattern, _ in matches)
    api_key_pos = API_KEY_BLOCK.find('sk-test-example-key-1234567890')
    relationships = find_secret_relationships('sk-test-example-key-1234567890', API_KEY_BLOCK, api_key_pos)
    assert any(rel[0] == 'key-endpoint' for rel in relationships)
    assert confucian_relationship_score(relationships) > 0.6


def test_redact_jwt_header():
    redacted = redactor.redact(JWT_HEADER)
    assert 'JWT_REDACTED' in redacted
    assert 'Authorization: Bearer' in redacted


def test_decode_base64_secret():
    matches = redactor.predecode_and_rescan(BASE64_SECRET)
    assert any(pattern == 'AWS_KEY_REDACTED' for pattern, _ in matches)


def test_ignore_isolated_entropy_noise():
    matches = redactor.predecode_and_rescan(NOISE_TOKEN)
    relationships = find_secret_relationships('ZnVuY3Rpb25TZWFyY2g3NDU2Nzg5MGFiY2RlZg==', NOISE_TOKEN, NOISE_TOKEN.find('='))
    assert relationships == []
    assert matches == []


def test_large_config_no_false_positive():
    matches = redactor.predecode_and_rescan(LARGE_CONFIG)
    assert matches == []


def test_hex_encoded_json_secret():
    matches = redactor.predecode_and_rescan(HEX_JSON)
    assert any('JSON_PASSWORD_REDACTED' in pattern or 'PASSWORD_REDACTED' in pattern for pattern, _ in matches)


def test_key_endpoint_relationship_across_lines():
    relationships = find_secret_relationships('sk-test-key-12345', KEY_ENDPOINT_SCATTERED, KEY_ENDPOINT_SCATTERED.find('sk-test-key-12345'))
    assert any(rel[0] == 'key-endpoint' for rel in relationships)
    assert confucian_relationship_score(relationships) > 0.7
