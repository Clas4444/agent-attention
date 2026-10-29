"""Compatibility CLI for repeated multi-case Codex evaluation."""
if __package__:
    from .evaluation.suite import main
else:
    from evaluation.suite import main

if __name__ == '__main__':
    raise SystemExit(main())
