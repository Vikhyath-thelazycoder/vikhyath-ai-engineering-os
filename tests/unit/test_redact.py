"""P18 (spec §78–79): planted secrets never survive redaction; harmless structure does."""
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from agylite.events.redact import redact, redact_text  # noqa: E402

# Synthetic credentials shaped like the real formats (none of these are valid keys).
PLANTED = {
    "aws": "AKIAIOSFODNN7EXAMPLE",
    "github": "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8",
    "github-pat": "github_pat_" + "11ABCDEFG0123456789_abcdefghijklmnopqrstuvwxyz",
    "slack": "xoxb-1234567890-abcdefghij",
    "stripe": "sk_live_" + "51HxyzABCDEFghijklmnop",
    "openai": "sk-proj-" + "abcdefghijklmnopqrstuvwxyz123456",
    "anthropic": "sk-ant-api03-" + "abcdefghijklmnopqrstuvwxyz",
    "google": "AIza" + "SyA1234567890abcdefghijklmnopqrstuv",
    "jwt": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
    "password": "hunter2-correct-horse",
    "url": "s3cr3tpassw0rd",
}


class TestRedact(unittest.TestCase):
    def test_planted_secrets_in_free_text(self):
        text = (f"aws {PLANTED['aws']} gh {PLANTED['github']} pat {PLANTED['github-pat']} slack {PLANTED['slack']} "
                f"stripe {PLANTED['stripe']} oai {PLANTED['openai']} ant {PLANTED['anthropic']} g {PLANTED['google']}\n"
                f"Authorization: Bearer {PLANTED['jwt']}\n"
                f"DB_PASSWORD={PLANTED['password']} curl https://admin:{PLANTED['url']}@db.example.com/x\n"
                "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA\n-----END RSA PRIVATE KEY-----")
        out = redact_text(text)
        for name, secret in PLANTED.items():
            self.assertNotIn(secret, out, name)
        self.assertNotIn("MIIEowIBAAKCAQEA", out)
        for kind in ("aws-access-key", "github-token", "slack-token", "stripe-key", "openai-key", "anthropic-key",
                     "google-api-key", "authorization", "secret-assignment", "url-credentials", "private-key"):
            self.assertIn(f"[REDACTED:{kind}]", out, kind)
        self.assertIn("db.example.com/x", out)   # structure around the secret is kept

    def test_sensitive_keys_and_nesting(self):
        data = {"details": {"api_key": "abc123", "headers": {"Authorization": "Basic dXNlcjpwYXNz", "Accept": "json"},
                            "token": 42, "est_tokens": 1234, "cmd": f"export GITHUB_TOKEN={PLANTED['github']}",
                            "items": [f"password: {PLANTED['password']}", "plain"]},
                "flag": True}
        out = redact(data)
        d = out["details"]
        self.assertEqual(d["api_key"], "[REDACTED:sensitive-key]")
        self.assertEqual(d["headers"]["Authorization"], "[REDACTED:sensitive-key]")
        self.assertEqual(d["headers"]["Accept"], "json")
        self.assertEqual(d["token"], "[REDACTED:sensitive-key]")
        self.assertEqual(d["est_tokens"], 1234)
        self.assertNotIn(PLANTED["github"], d["cmd"])
        self.assertNotIn(PLANTED["password"], d["items"][0])
        self.assertEqual((d["items"][1], out["flag"]), ("plain", True))

    def test_harmless_text_unchanged(self):
        for text in ("Fix the payment webhook security.", "est. tokens 8000 · files 12", "sk-short", "AKIA-not-a-key",
                     "the token budget is 1500"):
            self.assertEqual(redact_text(text), text)


if __name__ == "__main__":
    unittest.main()
