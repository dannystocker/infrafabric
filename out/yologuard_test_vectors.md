# Yologuard v3 Test Vectors

This plan targets the static `SecretRedactorV3`/relationship heuristics in `code/yologuard/src/IF.yologuard_v3.py`. Each case ties an input string to the expected detection outcome so the future test harness can assert both redaction and scoring behavior.

## Test cases
1. **Simple credential JSON (user/password pair)**
   - Input: `{"username": "alice", "password": "Th!sIsS3cret", "host": "db.host"}`
   - Expectation: `PASSWORD_REDACTED` match + `find_secret_relationships` returns a `user-password` tuple and a confucian score > 0.8. The redactor should replace the password string with `PASSWORD_REDACTED`.

2. **API key + endpoint pairing**
   - Input: `openai_api_key = "sk-test-example-key-1234567890"\nopenai_api_endpoint = "https://api.openai.com/v1/chat"`
   - Expectation: `API_KEY_REDACTED` or `OPENAI_KEY_REDACTED` pattern plus a `key-endpoint` relationship; redacted output contains `OPENAI_KEY_REDACTED` and the relationship score is > 0.7.

3. **JWT inside Authorization header**
   - Input: `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.K9c4gkZuUx2W-XYSmF9A4yR7f5kb1y-WD79U08AOoJo`
   - Expectation: JWT regex triggers `JWT_REDACTED`, and `predecode_and_rescan` reports a JWT match even though the token is not near other fields.

4. **High-entropy Base64 secret that needs decoding**
   - Input: `encoded = "QUtJQVo4NjdWRm91dFIxU1RSb2lTd0JkRz09"` (Base64 for `AKIAZ867VFoutR1STRoiSwBdG==`).
   - Expectation: `detect_high_entropy_tokens` surfaces the Base64 string, `predecode_and_rescan` decodes it, and the AWS key regex (`AKIA...`) triggers `AWS_KEY_REDACTED`.

5. **Confucian relationship emphasis (user + password near each other in free text)**
   - Input: `"Login as admin_user with password SuperSecret123! to reach https://admin.panel"`
   - Expectation: `find_secret_relationships` discovers the `user-password` pair and the redactor returns `PASSWORD_REDACTED` even if the field is not explicitly labeled.

6. **High-entropy noise token (no relationships)**
   - Input: `noise=ZnVuY3Rpb25TZWFyY2g3NDU2Nzg5MGFiY2RlZg==`
   - Expectation: `SecretRedactorV3.predecode_and_rescan` may identify the token but `find_secret_relationships` yields an empty list, so the overall relationship score remains 0 and `redact` should leave the text unchanged (no replacement with `*_REDACTED`).

7. **Edge case: very large benign config with repeated non-secrets**
   - Input: a long YAML snippet of logging settings (e.g., 1,000 characters of `log_level: info` and `endpoint: https://status.example.com`).
   - Expectation: `predecode_and_rescan` returns no matches and the redactor handles the file without timing out or raising; this guards against false positives in large config dumps.

8. **Hex-encoded secret inside JSON**
   - Input: `{"token_hex": "4d6f6f6e736861646566"}` (hex for `Moonshadef`).
   - Expectation: `try_decode_hex` decodes, the regex `JSON_PASSWORD_REDACTED` or similar triggers, and the redactor flags the secret even though it is nested inside JSON.

9. **Key + endpoint split across lines (relationship scatter)**
   - Input: `sk-test-key-12345\n# random comments\nhttps://api.sensitive-host/v2/submit`
   - Expectation: `key-endpoint` relationship detection still fires because the endpoint is within the 400-char window, so the token is classified as secret rather than noise.

Use these vectors to build data-driven pytest fixtures that assert both the pattern name and expected textual redaction/score outcomes.
