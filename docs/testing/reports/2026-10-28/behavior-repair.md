# Behavioral mode repair — internal, 2026-10-28

Historical pre-0.1.1 snapshot: this experiment still used the old batch-size
direction. Its results do not certify revised decomposition-depth semantics.
See the effort-direction report linked from [current results](../../results.md).

The previous validation established profile-state transitions, not the intended
change in working strategy. It must not be treated as evidence that all five
attention axes influence actual work. Earlier results remain historical.

## Change

The skill now places five-level working decisions directly in its entry point.
It applies them before choosing reads, edits and checks. Full-reference loading
and profile resolution are optional. Workflow changes retain task context without
reloading instructions. Reconciliation compares actual contracts; it does not
mean logging a transition. Persistence requires a separate explicit request.

Focus and exploration are distinguished; batching counts meaningful changes,
not shell calls. Required checks and discovered dependencies remain mandatory.
The guide contains a concrete narrow/wide example and states the limitations.

## Fixed smoke task and evidence

Two profiles repair the same integer-cent discount and shipping-threshold bug.
Only discount.py and checkout.py may change. An unchanged external acceptance
script checks both repairs and the existing shipping API. Protected input hashes
include the installed skill. No prompt requests state files or transition logs.

- Narrow: focus=1,sync=2,batch=1,explore=1,verify=2.
- Wide: focus=5,sync=4,batch=4,explore=5,verify=4.

The CLI requests gpt-6.1-sol with medium reasoning effort. Both profiles use the
same host reasoning setting. Model identity is based on the CLI request, not
independent backend attestation. Each instruction revision uses identical skill
bytes across its two trials. The final pair uses a frozen skill snapshot.

See [captured outcomes and trace hashes](behavior-repair.json).
Raw prompts, inputs and JSONL traces remain local under
`C:/Code/attention-behavior-20261028` and its `-final` sibling; they are not
published. The local harness is `.loop/behavior-trials.py`.

For the intermediate pair, the trace shows the narrow profile editing discount,
checking it, then editing checkout. The wide profile reads shipping before
editing and groups the two related changes, followed by acceptance and boundary
checks. Both pass acceptance, preserve protected inputs and invoke no profile or
checkpoint helper. Narrow took 32.926 seconds; wide took 40.689 seconds.

The final frozen pair repeats the same observable distinction: narrow edits
discount, runs its focused assertions, then edits checkout; wide reads shipping
before either edit, changes the two components together, then runs acceptance and
boundary assertions. Both preserve protected inputs and create no profile state.

| Revision | Narrow acceptance | Wide acceptance | Narrow time | Wide time |
|---|---|---|---|---|
| Intermediate | PASS | PASS | 32.926 s | 40.689 s |
| Final, shorter persistence instructions | PASS | PASS | 50.634 s | 120.158 s |

These four new model attempts have 4 acceptance successes, 0 failures and 0
environment blocks. They are separate from the earlier 12 checkpoint-oriented
attempts. The timing increase is retained, not presented as an improvement.
Behavioral evidence is limited to the observed sequencing/batching distinction
and absence of persistence overhead, not all-axis compliance.

## Interpretation limits

This is a behavioral smoke test on one task, not a release certification or a
five-axis causal experiment. The profiles change several axes together; focus,
sync and verification are not independently established. Both profiles may read
the same small set of necessary files. A lack of extra reads is not itself a
failure. Extra tests alone do not establish a useful verification difference.

There is no randomized order, repeated final-version sample or independent
reviewer. Global host instructions, caching and service latency remain possible
confounds. No quality superiority, token savings, native thinking control or
comparison against 10–18 manual user prompts is claimed.

## Repository checks

25/25 unit tests pass under Python 3.14 and Python 3.12. Generated-resource check,
documentation navigation and git diff whitespace check pass. The initial sandbox
unit attempt encountered temporary-file permission failures; rerunning outside
the sandbox passed without changing test expectations. No commit or push.
