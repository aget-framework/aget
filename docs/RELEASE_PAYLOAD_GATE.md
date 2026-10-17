# Producer payload gate CLI

The producer must wire the following command into its release script immediately
before pushing tags, after creating the local template tags. From the core `aget/`
checkout, with all 13 template clones under `/path/to/aget-framework`, run:

```sh
python3 verification/validate_release_gate.py 3.37.0 --payload-only --framework-path /path/to/aget-framework
```

Substitute the release version and framework root. Continue to tag push only on
exit **0**. Exit **2** refuses publication: at least one template tag has a compiled
cache, or a repository/tag/tree could not be inspected. All 13 registered template
repositories are required. Output includes PASS/FAIL, counts, and refusal reasons.
This standalone mode does not run manager, version, changelog, skill, or network
checks. The fleet gate reads each template's complete tree at the tag
`v<version>`, including unchanged paths; working-tree cleanup cannot conceal a dirty tag.

For one repository before creating its tag, use:

```sh
python3 scripts/check_tag_payload_coherence.py --version 3.37.0 --cwd /path/to/template --pre-tag --payload-only
```

The pre-tag gate reads the committed tree at `HEAD` under its working directory
or `--cwd`, including unchanged paths. It covers only that subtree: run it from the
repository root or pass that root as `--cwd` to cover the whole repository.
`--version` labels the report. Exit **0** means
clean and **2** means refused, including an unavailable repository or HEAD.
`--payload-only` requires `--pre-tag`. This mode skips release artifact inventory
and GitHub disclosure checks and performs no network requests. It complements the
fleet tag check; it does not establish which commit a later tag points to.

Both CLIs reject case-insensitive `__pycache__` path components and `.pyc`/`.pyo`
suffixes at every depth. Existing modes retain their existing CLI and exit codes.
The producer's private repository is outside this checkout: this document supplies
the integration contract; it does not claim that the producer has installed it.
