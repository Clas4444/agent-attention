"""Compatibility CLI for the opt-in benchmark runner; installed skill helpers stay separate."""
if __package__:
    from .evaluation.runner import (ROOT, FILES, TASK, PROFILES, ORDER, assess_usage,
                                    classify_trial, digest, environment_failure, main, run, subprocess)
else:
    from evaluation.runner import (ROOT, FILES, TASK, PROFILES, ORDER, assess_usage,
                                   classify_trial, digest, environment_failure, main, run, subprocess)

if __name__ == '__main__':
    main()
