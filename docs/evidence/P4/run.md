# P4 evidence — 2026-10-03T17:16Z, Python 3.14.7, fresh venv 'pip install -e .'

## unittest
Ran 32 tests in 0.202s

OK

## vikhyath doctor
Results: ✅ 52 passed, ❌ 0 failed, ⚠️  0 warnings
✅ All doctor checks passed!

## vikhyath validate
Results: ✅ 27 passed, ❌ 0 failed
✅ All validation tests passed!

## vikhyath benchmark --baseline
📊 Vikhyath AI Engineering OS — Benchmark (old-model baseline)
Token figures are ESTIMATES (bytes / 4); bytes are measured.

| Plugin | Version | Skills | Agents | Commands | Bytes | Est. tokens |
|---|---|---:|---:|---:|---:|---:|
| ecc@ecc | 2.2.2 | 292 | 68 | 94 | 120,682 | 30,170 |
| vikhyath-ai-engineering-os@vikhyath-marketplace | 1.0.1 | 5 | 3 | 0 | 841 | 210 |

Always-loaded descriptions across installed plugins: 121,523 bytes ≈ 30,380 tokens (estimate).
Not included: MCP tool schemas and hook output, which add to this cost.
