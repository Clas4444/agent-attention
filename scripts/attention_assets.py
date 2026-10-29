"""Stable CLI for the canonical resource generators in scripts/generators."""
if __package__:
    from .generators.assets import check, main, playground, reference
else:
    from generators.assets import check, main, playground, reference

if __name__ == '__main__':
    raise SystemExit(main())
