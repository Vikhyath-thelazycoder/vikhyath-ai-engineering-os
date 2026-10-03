"""Diagnostics: doctor, validate, benchmark."""


class Report:
    """Collects check results and prints them in the v1.0.1 doctor/validate style."""

    def __init__(self, title):
        self.title = title
        self.passed = self.failed = self.warned = 0
        print(title)
        print("=" * len(title))
        print()

    def section(self, name):
        print(name)

    def end_section(self):
        print()

    def check(self, ok, message, fail_message=None):
        if ok:
            self.ok(message)
        else:
            self.fail(fail_message or message)
        return ok

    def ok(self, message):
        print(f"  ✅ {message}")
        self.passed += 1

    def fail(self, message):
        print(f"  ❌ {message}")
        self.failed += 1

    def warn(self, message):
        print(f"  ⚠️  {message}")
        self.warned += 1
