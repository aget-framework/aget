# Starting the supervisor's batch session

Start the session that runs a migration batch with the kit's session-only rules:

The migration kit's test-body witness requires Python 3.12+ (`sys.monitoring`); on Python 3.10/3.11 a run needing that witness returns INCONCLUSIVE by design (weekly-train:R15).

```
claude --settings scripts/migration_kit/batch_rules.json
```

Before running a batch, complete the SOP's **Set up once per release**, its batch-folder paragraph and **The migration's record** under **Kit Batch Procedure**, and **Part A — per-release inputs**. Before Wave-1 pilots, follow the SOP's **Wave Sequencing / Wave-0 Supervisor Self-Upgrade**, steps 1–3. The supervisor is not a member of the Part B batch it orchestrates. Create the absolute batch folder `B` before B0; B0 and B12 write the ledger report to `B/FLEET_LEDGER.json`, never to the authority and receipt records at `data/<slug>_ledger/records.json`.

Run ordinary receiver wake-up/wind-down smoke checks only after B8's `launch_batch.py` returns, in a separate receiver session under the SOP's **Receiver sittings**, before B8a. The headless B8 prompt and allowlist forbid these scripts; `head_after` is already recorded when the launcher returns. Inspect the receiver's `scripts/wind_down_ext.py` and git hooks for commit or push behavior first. Start that separate session with `GIT_ALLOW_PROTOCOL=''` in its environment and retain it in script subprocesses: the empty protocol whitelist prevents git transport, including pushes to explicit URLs and local paths. An ordinary receiver session does not inherit the B8 launcher's no-push protection. If pushing cannot be disabled, skip the smoke for that receiver and record why and the unverified health in B13; never report the skipped smoke as PASS.

If wind-down writes `sessions/<file>`, follow the SOP's **Part B — the fixed procedure** smoke routes: either make exactly one receiver commit directly above B8's recorded HEAD, touching only named session paths and no packet item, run B8a with `--sha <extra-sha>`, obtain the B9 push line naming that commit, then pass `--only <member> --extra-commit <extra-sha> --extra-paths sessions/<file>` at B10; or leave the session record uncommitted, run B8a at B8's recorded HEAD, record the principal's allowance for each dirty path and pass `--allow-dirty sessions/<file>=<reason>` at B10. Name every affected path. After B8a keep HEAD and the tree unchanged; rerun B8a on any new commit before B9. B10 checks HEAD and dirty paths, and its separate push act needs the recorded B9 authority. Keep pushing disabled in the smoke session.

When B9's push line names any commit, run B10 once per member with `--only <member>` (dry run, then `--push`). A member with its own extra commit passes `--extra-commit <extra-sha>` and its `--extra-paths` values. Every other member passes `--extra-commit <named-sha> --extra-paths <path>`, using one of the commits the push line names and a nonempty path value. The gate permits that member's checked commit because its HEAD still equals B8's `head_after`; the supplied extra commit does not change it. A plain B10 push without `--extra-commit` is refused with exit 6 when the push line names a commit. Keep any required `--allow-dirty` allowances for each member too. See the SOP's **Part B — the fixed procedure** smoke routes.

Why (carriage rows 62, 70, 72; v3.35 migration, 2026-09-30):

- In auto mode, the permission classifier refused two acts the principal had already authorized, and handed them
  back as commands for the principal to run by hand. Narrow allow rules for the batch tools stop that, because a
  narrow rule is resolved before the classifier.
- Rules added through `/permissions` persist, and removing them took four dialog passes. Rules passed with
  `--settings` last for that one session: nothing persists and nothing needs removing.
- Each rule takes a command out of the classifier's check, with any arguments. `python3 scripts/migration_kit/push_batch.py --push`, and
  `python3 scripts/migration_kit/launch_batch.py --launch` without `--copy-root`, check the principal's typed line themselves (`batch_authority.py`;
  exit 6 without it). `python3 scripts/migration_kit/launch_batch.py --launch --copy-root <dir>` makes no authority check. It refuses the folder
  (exit 2, reason printed) unless `git remote` prints nothing there, the folder is apart from the member's own folder
  (not the same folder, not inside it, not containing it, not sharing its `.git` through a link), git run in the
  folder names the folder as its working tree and the folder's own `.git` as its git folder and common folder, its
  `.git` folder holds the marker file `aget_rehearsal_copy.json` naming the digest of the packet file's bytes and
  the member, and its HEAD equals the packet's HEAD for that member. The git test asks git itself (`git rev-parse
  --show-toplevel --absolute-git-dir --git-common-dir`, with the environment the session gets): a copy whose
  `core.worktree` setting names the member, a linked worktree, a `commondir` file and a bare repository are refused,
  and so is an environment that holds `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`, `GIT_INDEX_FILE`,
  `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` or `GIT_NAMESPACE`. It does not read the object
  store's `alternates` file, hooks, or what a session does after it starts. The session rehearsal
  (`rehearse_v37.py`) uses that form. Before it removes or copies anything it refuses a copy folder that is the
  member's own folder, holds it or lies inside it; after the copy it makes the same git test, before any other git
  command, the apply or a launch; and it writes the marker into the `.git` folder of the copy before it launches
  there (a copy whose `.git` is a link or is not a folder gets no marker and is not launched). The marker is a plain
  file: anyone able to write it can forge it in another folder with no remote at the packet's HEAD, so these tests
  do not prove a throwaway copy. Using that
  form nowhere else is an operator rule, not enforced by the tool beyond these folder tests.
  `tests/migration_kit/test_migration_kit_batch_rules.py` fails if a ruled tool's source holds no call to the check;
  it does not test every path through the tool.
- The check is per act. `launch_batch.py` asks for the launch and `push_batch.py` for the push. A launch line need not
  name the launch. In addition to the provenance, prefix, length and batch checks, the recorded line must not match
  the tool's recognized launch-exclusion pattern. A push reads only a line recorded for the push (key `<batch>:push`,
  written by `python3 scripts/migration_kit/record_authority.py --act push`): the batch's launch line is never push authority, whatever it says, and
  `python3 scripts/migration_kit/push_batch.py --push` exits 6 when no push line is recorded. A push line must have the one fixed form below.
- Scope evidence never authorizes launch for any batch. Every prompt containing a recorded scope quote is tainted,
  including older and newer matches, and copies in resumed or forked transcripts. Identity is timestamp plus normalized
  full text, never the filename; scope history is searched across all readable transcripts for this project. Record
  every scope instruction, then type launch in a separate prompt containing no recorded scope quote and record it with
  `python3 scripts/migration_kit/record_authority.py --key N --act launch --line "..." --session <id>`. Recorder and gate share the scope predicate;
  a refused launch record leaves the ledger unchanged (observed scope evidence may be archived). Any old-format entry anywhere in the active records file blocks every
  authority-checked launch for every batch, regardless of its Aget, batch list, wording, quotes or storage key.
  Rehearsal launches with `python3 scripts/migration_kit/launch_batch.py --launch --copy-root` make no authority check, as before.
  Current format requires a dict with a `batches` list and a non-empty `history` list whose EVERY item is a dict
  with a non-empty string `line`. Every entry batch must be named in at least one history item's `batches_added`
  list (batch names are case-insensitive). An entry with any batch lacking this per-line coverage is old-format too.
  The recorder refuses `--scope-override` onto an existing old-format entry without writing.
  The refusal names every offending entry key. Ask the principal to confirm the old scope override no longer applies
  in a whole typed prompt naming that Aget, for example `GO supervisor - the old scope override for example-core-aget no longer applies`.
  Run `python3 scripts/migration_kit/record_authority.py --session <id> --retire-scope <aget-key> --principal-line "<typed confirmation>"`.
  The recorder verifies that whole prompt in the session, archives the full raw entry, and only then removes it.
  If fresh scope is needed, record it from the principal's typed line under an unused batch key (existing batch
  authority is never replaced). Retired scope quotes remain tainted permanently; use a separate launch prompt.
  The recorder refuses `--act launch` in the same state with the same reason. Push authority (`--act push`, fixed push form) is unaffected.
  With an all-current ledger, unverifiable history fails closed for the batches it governs and the reason identifies
  the history to restore or repair; unrelated unverifiable history with a valid batch list does not block a first
  launch. A missing or invalid batch list cannot establish which batches are governed and refuses all launches.
  Scope quote matches are case-sensitive after collapsing whitespace, with word boundaries at word-bearing edges:
  `batch 1` does not match `batch 12`.
  Scope taint also lives in permanent `scope_archive.jsonl`, by default `../scope_archive.jsonl`
  relative to the records file's directory, beside the ledger directories. Commit `scope_archive.jsonl`
  and the records file together after every recorder operation. Never delete or edit the archive.
  The records file carries `scope_archive_anchor = {"path": "../scope_archive.jsonl", "rows": N, "chain": HEX}`.
  The path is relative to that records file, never the CWD. Genesis chain is the empty string; for each row,
  `chain_n = sha256((chain_previous + row.sha256).encode("ascii")).hexdigest()`.
  `AGET_MIGRATION_SCOPE_ARCHIVE` is honored only with `AGET_MIGRATION_TEST_MODE=1`; tests resolve even a relative
  override from the records directory and refuse a path different from an existing anchor. Production always uses
  `<supervisor-root>/data/scope_archive.jsonl`, with the root taken lexically from the kit's configured location. Active records
  must be `<supervisor-root>/data/<name>_ledger/records.json`, without `..`. Test mode uses the passed records path lexically.
  A symlink at the active records file, ledger directory, root or archive (including archive directory components),
  or a disagreement between the lexical and resolved path, refuses launches and recorder scope/launch writes.
  Replace the symlink with the real file/directory; the ledger and archive must live in the kit's data directory.
  An anchor path resolving elsewhere refuses every launch and archive
  mutation with "anchor path is not the ledger root's archive; restore the anchor". The recorder writes only the
  fixed relative path in production. The archive must be a regular file separate from records.json; `/dev/null` refuses.
  Each JSONL row retains `recorded_at`, absolute source `ledger` for provenance, root-relative `ledger_relative`,
  `aget`, `batches`, complete raw `entry`,
  `fields` mapping JSON pointers to every raw string, `content_sha256` for deduplication, and `sha256` over the
  canonical sorted compact row excluding `sha256` itself. The recorder locks, validates, appends and fsyncs the
  archive first, then atomically replaces and fsyncs the records file and its directory while holding the lock.
  It captures complete old and new scope entries in that transaction. The gate only reads; it never appends,
  creates a missing archive, or writes an anchor. Every dry run writes nothing, including to the archive.
  Before seeding, verify the release's annotated tag and peeled commit, physically copy the whole
  `scripts/migration_kit/` into the supervisor, ensure the supervisor session's `python3` imports PyYAML and pytest (the kit runs both), checked with `python3 -c "import yaml, pytest"`, and configure
  `.aget/migration_target.json` with `to` set to `<target>` (e.g. `3.37.0`). Run
  the SOP's release-age adoption check after reviewing or declaring `.aget/adoption_policy.json` (skew limits, minimum release age and Wave-1 soak), then run
  `python3 scripts/migration_kit/check_fleet_skew.py --json` before ledger creation or permanent archive seeding;
  stop on BLOCKED or UNAVAILABLE. Then create `data/<slug>_ledger/records.json` containing `{}` if absent,
  preserving existing history. `<slug>` is `v` plus the target's major and minor digits (e.g. `v337` for `3.37.0`).
  The release's migration message gives the complete setup, target configuration and seeding block; follow the SOP's declared Wave-1 soak before Wave 2.
  All commands below run from the supervisor root; the kit resolves that root from its physical installation,
  not an arbitrary data-root CLI flag. If the active ledger is missing, the refusal ends
  `repair or move it out of the data folder`; create the active `{}` ledger first, then repeat seeding.
  Before launching from a fresh ledger, run `python3 scripts/migration_kit/record_authority.py --archive-ledger <previous-ledger>/records.json`
  for each earlier ledger that exists and has scope history AND run
  `python3 scripts/migration_kit/record_authority.py --archive-ledger data/<slug>_ledger/records.json`
  for the active ledger, before any launch and before moving a ledger or removing entries. This seeds the ACTIVE archive and
  updates the ACTIVE anchor, leaving a different source
  ledger unchanged. The output names the archive and reports the count actually appended (zero on a repeat).
  A source outside the active ledger root (the records directory's parent) requires `--allow-foreign-ledger`;
  its absolute source path is retained in each row. Use `--retire-scope` for removal. Its whole typed confirmation
  has exactly the form `<prefix>the old scope override for <aget-key> no longer applies`.

  Every checked launch scans the lexical `<root>/*_ledger/records.json`, plus the active ledger. Only folders named
  `*_ledger` are ledgers; seed every previous ledger before renaming anything. Symlinked sibling ledger directories
  and records files refuse, including aliases to another ledger inside the root and dangling links.
  Every raw scope entry, in any format, must have its exact content hash in the archive, using the ledger path
  relative to the root and the Aget key. Moving or cloning the data folder with the same relative layout keeps new
  seeded entries seeded. Absolute source provenance is excluded from the content hash. Older archive rows remain
  readable, tainted and seeded at their original root; seed again with `--archive-ledger` before moving the data
  folder to append portable content hashes for those entries without rewriting history.
  Unseeded ledgers are named with a separate
  `python3 scripts/migration_kit/record_authority.py --archive-ledger <that records.json>` remedy for each. A missing archive refuses whenever
  any scanned ledger has scope history or an anchor. Every ledger's anchor must match the archive prefix of its
  declared length. A shorter archive or changed prefix refuses launch, seeding and `--anchor-archive`, including
  from a fresh ledger. Seeding can proceed one ledger at a time; launches remain blocked until all are seeded.

  The process caches ledger documents/content hashes and validated archive rows/content hashes/prefix chains by
  `(lexical absolute path, mtime_ns, size)`. Each check validates path components, enumerates the root and stats
  files again. The archive cache also includes the lexical root for legacy content membership. Cold scan cost is linear
  in directory entries, ledger/archive bytes and scope entries. Warm scan cost is directory enumeration plus
  O(L + E) metadata and hash-membership work for L ledgers and E scope entries; each anchor prefix check is O(1).
  Transcript matching and archived quote matching have their existing additional costs.

  Every checked launch, for every batch, refuses the conditions below. Run remedies against the active ledger
  unless the refusal names an unseeded source ledger to pass to `--archive-ledger`.

  | Refusal | Exact remedy |
  |---|---|
  | Scope history without an anchor, no archive yet | Run `python3 scripts/migration_kit/record_authority.py --archive-ledger <active records.json>` to seed and anchor it. |
  | Any root ledger has unarchived raw scope entries | Run the named `python3 scripts/migration_kit/record_authority.py --archive-ledger <that records.json>` command for each unseeded ledger. |
  | Existing previous-round archive without an anchor | Verify the complete archive, then run `python3 scripts/migration_kit/record_authority.py --anchor-archive`. |
  | Missing archive, fewer rows, or anchored chain mismatch | Restore archive and records file together from the last intact committed pair; re-anchoring cannot bless loss or a changed prefix. |
  | Extra valid rows after the anchor (interrupted ledger save or another ledger's append) | Verify the entire archive, then re-anchor with `python3 scripts/migration_kit/record_authority.py --anchor-archive`; commit both files together. |
  | Invalid/torn row or unreadable archive | Preserve the damaged file separately; restore the complete archive and records pair from committed copies and source ledgers, restoring read permissions if needed, then `--anchor-archive`. Never discard evidence or trim the tail. |
  | Invalid anchor or archive equal to ledger/non-regular file | Restore the committed anchor and separate regular archive together; remove any invalid test override. |
  | Production anchor path differs from the ledger root's archive | Restore the anchor to `../scope_archive.jsonl`; do not redirect the archive. |
  | Symlinked root, ledger directory, records file, archive or sibling ledger; lexical/resolved paths disagree | Replace the symlink with the real file/directory; the ledger and archive must live in the kit's data directory. |
  | Corrupt/unreadable records.json in a `*_ledger` folder | Repair the named file or move it out of the data folder. |
  | Test override resolves to a different anchored path | Remove the test override or set it to the anchored path. |
  | Source ledger outside active ledger root | Explicitly pass `--allow-foreign-ledger` to seed it into the active archive. |

  Archive taint refuses launch for **every batch** if any archived history `line` occurs in the full prompt, or if
  the normalized full prompt occurs inside any archived raw string field. This reverse containment catches old
  `source`, `source_7t`, `reason` and other embedded quotes. It requires at least **24 characters after whitespace
  normalization**, so trivial prompts do not match incidental metadata everywhere. Both rules are case-sensitive;
  the minimum applies only to reverse containment. Removing an entry or starting a new ledger never erases archived taint.
  Selected launch transcripts with invalid UTF-8 refuse with the file and line to repair. The all-project scope scan
  decodes each row separately and retains valid rows before and after damage. Recognized affirmative scope wording
  also refuses (including `write_scope`, plural scopes, widening and extensions), while incidental denials such as
  "scope overrides: none", "no need for a scope override", and "outside the scope of this batch" pass. Wording
  detection cannot infer neutral scope instructions that were never recorded, or their unrecorded edited retypes.
- The launch check binds the batch's name, not the packet. `launch_batch.py` passes it the packet's `batch` value
  and nothing else of the packet, so another packet file with the same `batch` value passes the launch check on
  the same recorded line, whatever receivers it lists. Operator rule, not enforced by the tool: launch with the
  packet that was rehearsed and approved for that batch. The push is bound to its packet: the push line is
  recorded with `--packet`, and `python3 scripts/migration_kit/push_batch.py --push` refuses a push from any other packet file, even one with
  the same `batch` value.
- A push line is accepted in one fixed form only (`PUSH_FORM` in `batch_authority.py`): the prefix, then
  `push the commits of batch N`, optionally more batches (`batches 10t and 10`), optionally ` with commit SHA` (or
  `commits SHA, SHA and SHA`, each 7 to 40 hexadecimal characters), and nothing else. With the default prefix the
  shortest line is `GO supervisor - push the commits of batch 1`. Runs of whitespace are not compared, and after the prefix
  letter case is not compared either; the prefix itself keeps its letter case (`go supervisor - ...` is refused). Every other line is refused, and the reason states the form. "The push is not approved yet", "the push
  remains unapproved", "the push is prohibited", "the push is held" and "push tomorrow" are refused. This is a test
  of form, not a reading of meaning: an affirmative line worded another way ("batch 1, push the verified commits",
  "no problem, push it") is refused too, and the principal types the form. A commit id in a push line must be
  passed as `--extra-commit` at the push (the `--extra-commit` item below). The push
  line must also equal the whole typed prompt it is found in, once runs of whitespace are collapsed: the newest prompt
  holding the line is compared, and words typed before or after the line refuse it. A pasted block among other words
  of that prompt is left out of the comparison, so a condition that exists only inside such a paste is not seen; a
  later prompt that withholds the push without repeating the line is not read either. A launch line is tested
  differently: the transcript test looks for it inside what was typed, and it is read as excluding the launch only
  when a recognized exclusion phrase comes shortly before the word launch, within 30 characters, in the same clause
  ("do not launch").
- For a push the tool reads only a recorded push entry, and the newest prompt that holds the recorded line must
  equal it (runs of whitespace collapsed; a pasted block among other words is left out of the comparison). Operator
  rule for a push, not enforced by the tool: you record nothing if the principal withholds or conditions the push
  where the tool does not read it (a paste typed beside the line, a later prompt that does not repeat the line).
  Record the
  push line on its own: `python3 scripts/migration_kit/record_authority.py --key N --act push --line "..." --session <id> --packet <packet>`. The recorder refuses `--act push` without `--packet` and keeps the packet file's digest with the line, so `python3 scripts/migration_kit/push_batch.py --push` refuses a push from any other packet file. The recorder runs the
  same line check as the push tool (`batch_authority.verify` with the push act) before writing and writes nothing when
  it refuses; the push tool runs the check again at the push.
- `python3 scripts/migration_kit/prepare_write_list.py --drop` marks a member blocked in the write list only. The apply step skips it. The
  launcher reads the packet and never the list, so it still launches a dropped member unless the packet is rebuilt
  without it or every launch names the remaining members with `--only`. Select the remaining members explicitly
  for apply and push too.
- `--extra-paths` and `--allow-dirty` on `push_batch.py` come from the command line alone; no typed line is
  compared. `--extra-commit` must be a commit the recorded push line names (` with commit SHA`, the shorter id a
  prefix of the longer); when HEAD moved since the launch check, HEAD is compared with the longer id. With HEAD unchanged, a supplied extra commit does not change the checked commit the gate permits. The one accepted push form has a place for commit ids and none for a path, so the
  principal's word for an extra path or an allowed dirty path is a separate line of theirs, quoted in the batch's
  record (operator rule, not enforced by the tool).
- Every copy and clone the kit makes goes through one isolation routine (`scripts/migration_kit/copy_isolation.py`): the packet rehearsal (B2) and the repair rehearsal, the session rehearsal (B3) and the `--copy-root` launch, the suite check at the commit (B8a) and the after-run confirmation run. Before anything is removed, copied or cloned, the environment must hold no variable that tells git where a repository is (`GIT_DIR`, `GIT_INDEX_FILE` and the five others the routine names), and the folder to be filled must not be the member's own folder or a declared sibling's source folder, hold one or lie inside one; it is made inside a fresh run folder under a work root that is refused inside any git repository and where it is, holds or lies inside a member, a declared sibling's source folder or the framework root, and nothing is removed to make room. After the copy or the clone (a clone is made with nothing checked out), and before any other git command, apply, hook or test in it, git run in the copy must name the copy as its working tree and the copy's own `.git` as its git folder and common folder: a copy that inherits a `core.worktree` setting, a `.git` file or link, or a `commondir` file is refused with nothing run in it, and so is one in whose `.git` folder an entry, such as `config`, is a symbolic link leading outside the copy. Every copy, a plain sibling folder included, is refused when any symbolic link in it, in the working tree or in `.git`, leads outside the run's folder (the copy, or the folder that holds the copy and its declared siblings); a clone, and the repair rehearsal's copy, is asked again after each checkout the kit makes in it, and the `--copy-root` launch asks again at each launch. Remotes defined by files under `.git/remotes/` or `.git/branches/` (an older form that `git remote` does not list and git still pushes to) are deleted. A copy of the member then loses its other remotes, and a clone of it gets a push URL that cannot resolve on each remote; each copied sibling folder that is a git repository keeps its remotes with such a push URL. The push URL git would use is read back after it is set, so a URL rewrite rule that redirects it is a refusal. That URL's scheme, `no-push`, is closed in each copy's own configuration: `protocol.no-push.allow = never` is written as the last entry of the copy's config file (so anything that file includes earlier, conditionally or not, is overridden) and read back as git will use it. A copy is refused when the environment reopens the scheme (a `GIT_ALLOW_PROTOCOL` naming it, or configuration given through the environment), or when configuration git reads after the copy's own file (a worktree configuration, or configuration from the environment or the command line) includes another file. A copy is also refused when any git configuration it reads (the member's own, global or system) holds a conditional include whose condition can change after isolation (`onbranch:` or `hasconfig:`), or an include of a file inside the repository, since a checkout or a configuration change could make either redirect a remote later. An operator whose global or system git configuration uses such an include is refused until it is moved out of that file for the run or given a `gitdir:` condition; the refusal names the file and the entry. Unconditional and `gitdir:` includes of files outside the repository are kept: they are in force when the routes are read. After each checkout the kit makes in a copy, the push routes are read again. Only that scheme is closed: a copy's other transports are left as they were. A copy of a member that has no `.git` of its own (a member that is a folder inside a shared repository) is refused with nothing run in it: git run in it would act on the shared repository. A sibling folder with no `.git` at its top is copied as it is and only the link test is asked of it, and git run in its copy acts on whatever repository encloses the copy folder. Not closed: a repository nested deeper inside a copied sibling, a symbolic link that code running in the copy makes after the link test, a submodule, a branch whose remote is a path with no remote section, a remote added during the run, a push to an explicit URL or path, the object store's `alternates` file, hooks, and what code does after it starts. A hook that the member installed as a symbolic link into its own tree (such as `.git/hooks/pre-commit -> ../../scripts/pre-commit`) is admitted, and git runs it through the link whenever it runs the copy's hooks. A hook link leading outside the run's folder makes its copy refused like any other such link: at B2 that member reads `REFUSED` and the other members are still rehearsed. Such a member is dropped from the batch, or its hook is changed by the principal's line in that receiver's own session (procedure B2), never by the kit or the supervisor. No tool refuses an output or evidence folder (`--evidence`, `--out`, `--receipt-dir`) placed inside a member's repository or inside a repository that holds a member: keep them outside (operator rule). `--scratch` is a work root and is refused there.
- A protected file is replaced only when it is byte for byte an upstream version. `prepare_batch.py` classifies a protected payload file; `prepare_launch.py` skips protected paths and applies the same rule to an unprotected payload file. Either class is `write-upstream` (replaced) when it differs from both release tags but its bytes equal one version of that path at some tag of a local template clone or core. A file whose every line some upstream version holds, but which equals none of them (lines deleted, reordered, re-indented or repeated), has no line of its own that a count can show, and the difference may still be the member's own: it is a `hold` of kind `unattributed`, and its member is told to KEEP it (keep its copy, do not take the release bytes, record both digests), gets no edit permission for it, and the after-run check requires its bytes to be unchanged. A `hold` with lines of its own is a MERGE: the session may edit it, and the after-run check requires every one of those lines to survive. A path with no release source is a `hold` of kind `no-source`, kept the same way. The tools that place, permit, instruct and judge payload items read these meanings from one table (`scripts/migration_kit/item_meaning.py`). An item whose classification has no entry there is refused before any other use: by the apply's plan; by the launch packet's prompt, write set, allowlist and placing commands; by the launch's check before any session; by the packet and repair rehearsals; and by the B4 approval check. It reads INCONCLUSIVE at the after-run check. The scope check and the push gate read the same table, and the ledger reads its payload expectations from a closed set in the same module (an unknown one is a finding). The launch derives each receiver's allowlist and write set again from its items and refuses that receiver's launch, before its session starts, when the packet's rules differ. The apply receipt records each held protected file with its whole list entry, and the after-run check A compares a held file whose row keeps it as it was (`unattributed`, `no-source`) with its listed `pre` by identity; a receipt that names held paths only, as one written by an earlier kit does, reads INCONCLUSIVE. The KEEP line for an `unattributed` hold names the release digest, and a hold with no release digest stops the packet's preparation.
- The kit's own writes into members, copies and the packet root are made at the act and never go through a link. The apply (B7), the rehearsals' writes in their copies, the stage written at B1 and the baselines written at B6 go through one contained writer (`copy_isolation.contained_write` and its folder, delete and remove siblings): it reaches the target's folder by opening each folder from the member (or the copy, or the packet root) down without following a link, opens that path again and compares identities immediately before each act (each folder it makes, the temp file, the rename), refuses a target that is a link, is not a regular file, or has a second name (a hard link, whose other name the write would change), writes a new temp file, reads it back and renames it onto the name. It never truncates a file in place. A payload path that is or goes through a link, or resolves outside the member, is `unsafe` in both the protected-write list and the launch packet: never written, the member's session told to leave it, and the after-run check INCONCLUSIVE, so the member is not pushed with that path unmigrated. A member's session places its release files with the packet's sealed placer (`python3 <packet root>/stage/kit/place_file.py ...`, the same act), not with `cp -f` and `mkdir -p`. Evidence and output files the tools write into the folders you name (`--evidence`, `--out`, `--receipt-dir`, `--scratch`; for example `baseline_record.json`) are not written by the contained writer and can follow a link there: keep those folders outside every member and free of links (operator rule). Stated limits: the release note's "What the kit guarantees, and its stated limits".
- The apply step (B7) is all or nothing per member. Protected payloads with equal bytes but a different release executable bit are listed as writes; the protected writer carries the release mode into its receipt. A wrong-bit payload `noop` refuses as `RELEASE MODE MISMATCH`, including an older list without a mode field. `apply_protected.py` plans every member before it writes anything, and refuses a member (nothing written there) whose listed files or HEAD differ from the list, whose list entry names no HEAD, or whose listed path is unsafe or not a regular file. It then writes one member at a time: its receipt is first written with that member IN-PROGRESS, the plan is made again and must agree, and every file is written or none. A failure after the first write is rolled back and read back: the member reads REFUSED only when every file reads back as before, otherwise ROLLBACK-INCOMPLETE, which names each path restored and not restored. One member's failure never stops the others. An interrupt (Ctrl-C, or a SIGTERM) stops the batch: the member in flight is rolled back as above, the members not reached read NOT-STARTED, the receipt is written and the exit is 130. A run killed outright leaves the receipt with that member IN-PROGRESS. Every list is prepared again for this release: lists now carry each member's HEAD.
- The results of the three rehearsals and of the after-run check are bound to their runs (`scripts/migration_kit/result_binding.py`). A tool's first act, before it parses its arguments or reads an input, records a run in `runs.jsonl` beside its result file and writes the result as not finished; when it has written its result it records the digest of those bytes. A result counts only when it is the last run started for that file, that run finished, and the bytes read are the bytes it wrote. So a later run of the same output that failed, even with a usage error, makes the earlier result unmet when its arguments name that output (read as argparse reads them: the last occurrence counts, and a value such as `-1` is a value, not an option); a run whose arguments name no output path records no run, and an earlier result there stays current (read each tool's exit). A result copied from another folder is refused even when it names this list's digest. The B4 approval check, the push gate (for the after-run verdict and the receipt) and the ledger read results this way. The apply receipt, the B8a suite record and the baseline record are bound to their runs the same way, and the push gate and the after-run check read each only as the current run. Not yet bound in this draft, and read as plain files: the receipts the rehearsals read in their own copies (each takes the receipt its own apply wrote). The after-run verdict must also name the member and the session the launch record names; a hand re-judge is a new run of the same session and replaces the launch's own check. The session rehearsal takes the apply receipt that its own apply wrote, never one chosen by file name.
- Some help texts, printed messages and generated receiver prompts still state stronger authorization or copy
  guarantees than the tools establish (for example a launch prompt says "on the principal's authorization" even on
  the `--copy-root` route). They are not evidence of authorization.
- Exit code 0 is not a pass: once the members' migration sessions have run, `launch_batch.py` exits 0 whatever its
  after-run checks said, and `push_batch.py` prints NOT PUSHED for a receiver its gate refuses without that refusal
  changing the exit code. Read the printed verdict for each member.
- Run the tools as `python3 scripts/migration_kit/<tool>.py ...` from the repository root. For the three tools the
  rules name, the command must begin with `python3 scripts/migration_kit/`: anything in front of it
  (`cd <folder> &&`, `VAR=...;`, `env -u ...`, `export ...;`) stops the rule from matching, and the permission
  checker decides in its place. `launch_batch.py`, `push_batch.py` and `suite_at_commit.py` drop variables whose names end
  in `API_KEY` from the sessions and the suite they start; `rehearse_batch2.py`'s suite runs on the copy and the
  after-run check's confirmation run do not.
- The suite check at the commit to be pushed compares with no baseline: it reads PASS only when its run ends with no
  failure and the member's pre-push hook, where one exists, exits 0, and neither left a change read below. The
  command-line tool reads the clone's HEAD and `git status --porcelain` before the suite, after it and after the
  hook, and with each status line the content of the paths it names (a file's bytes and permission bits, a
  link's target, the files under a folder git lists as one entry), and a snapshot of every file, link and folder of
  the working tree that git does not ignore: a moved HEAD, or, outside the paths named with the repeatable option
  `--allow-path PATH` (an exact repository-relative path, or a folder prefix ending in `/`; command line only, not
  read from the packet), a new status line, a status line that is gone, or any other change to a file, link or folder of the working tree that git does not ignore, tracked or not (a file's bytes or permission bits, a link's target, a folder's permission bits), reads
  INCONCLUSIVE, which the push tool does not push. So a file of a sibling folder copied inside the clone, listed
  before the suite and rewritten by it, is read as a change (the record shows its line with ` (content changed)`).
  Unless the suite timed out or moved HEAD, `suite_at_commit.json`
  keeps the status lines read (the first 40 of each reading); it always keeps the paths allowed. Not read as a
  change: a file git ignores, an untracked file under a `__pycache__` or `.pytest_cache` folder, a change made and undone between two readings, an empty folder added or removed, times and owners, a change inside a `.git`
  folder, and anything written outside the clone. A run that fails tests and also
  leaves such a change outside the allowed paths reads INCONCLUSIVE, not FAIL, so a baseline-equal ruling does
  not pass it until the written paths are named with `--allow-path` and the check is run again. The run leaves out
  what the tool finds excluded in the member's CI workflows (a `--deselect` test id, an `--ignore` path, an id in a
  `tests/...known...txt` file the workflows name) and lists it in `suite_at_commit.json`. When the principal rules a
  failure baseline-equal, record the typed ruling with `python3 scripts/migration_kit/record_authority.py --session <id> --baseline-equal
  AGET=<commit> --ruling-line "..." --evidence <batch>/evidence`; never write the ruling file by hand (operator rule,
  not enforced by the tool: the push tool reads the file as found). The push tool checks that the ruling's line is
  found typed, has the one fixed form (the prefix, then `the failures at SHA are baseline-equal`, SHA being 7 to 40
  characters the commit's id starts with; for example `GO supervisor - the failures at abc1234 are baseline-equal`),
  and equals the whole typed prompt it is found in. That is a test of form, not a reading of meaning (a ruling
  worded any other way, "same failures as before" or "abc1234 baseline ruling remains unapproved", is refused), and
  the line does not name the member.
- The kit reads this session's transcripts under `~/.claude/projects/`, headless sessions write theirs there,
  `suite_at_commit.py` and the reference run of `rehearse_batch2.py` clone members under
  `~/.cache/aget-suite-at-commit/`, and the rehearsal tools (`rehearse_batch2.py`, `rehearse_v37.py`,
  `rehearse_repair.py`) copy members into a fresh run folder under the `--scratch` work root you name; the tools
  refuse a work root inside any git repository or where it is, holds or lies inside a member, a declared sibling's
  source folder or the framework root, remove nothing, and keep each run folder.
- Name the folder holding the framework clones as `framework_root` in `.aget/migration_target.json`, beside the
  release target. Shell state does not persist between a session's commands, so a variable set with `export` would
  have to prefix every command, and the prefix stops the rule from matching.
- A line given as the session's launch argument (`claude "GO supervisor - ..."`) is recorded like a typed prompt, so
  it is refused as authority (`check_principal_line.py` exit 5). The principal types it again in the open session.
  The launch, push and baseline-equal checks also count as typed a line whose newest match is a human-origin entry
  queued mid-turn, whose prompt source the tool does not read (`check_principal_line.py` exit 4). The launch or
  push tool that accepts such a line prints `typed mid-turn`; for a baseline-equal ruling the push tool does not.
- A session cannot see its own launch settings. To confirm it was started with these rules, run
  `ps -o args= -p $PPID` in it: the session's own command line must show `--settings`.
- Before ending a turn on an act handed to a receiver, arm `python3 scripts/migration_kit/watch_receiver.py
  <receiver folder>`. It is read-only and exits on the receiver's turn end, HEAD move or a move of `refs/heads/main`
  on its `origin` remote (`--ref` names another ref); it also exits with no event at its `--timeout` (3600 seconds
  by default, exit 3) or when a git probe fails (exit 2). Each turn-end event names its session; add
  `--session <id>` when the folder may hold another live session: it narrows the turn-end watch alone, and a HEAD
  or remote move still ends the watch.
- Before the first command: install the kit's one dependency (`python3 -m pip install -r
  scripts/migration_kit/requirements.txt`) and make sure your fleet register is committed at
  `.aget/fleet/FLEET_STATE.yaml`. A supervisor built from the template has neither yet.
- The kit is built, tested and rehearsed with Claude Code only. A supervisor or receiver session run with another
  command-line tool is outside what this release has shown to work. The rehearsals and the live run used the kit
  before eight later behaviour fixes (the push line and ruling forms, the isolation of every copy and clone the kit
  makes, the session rehearsal's verdict from its own run only, the confirmation
  run's push URL, the changed-clone test at the suite check, the ledger's reading of workflow checks that were not
  compared, the protected-write classification and the refusal to write through a symbolic link); those eight have unit-test coverage and the later second outcome run exercised the worker path, returning FAIL accepted as R59 named limits.
- The trial run of the protected write is `python3 scripts/migration_kit/plan_protected.py --list <list>`, which contains no write.
  `apply_protected.py` is run only to write.
- If the supervisor Aget is not named `supervisor`, set `AGET_MIGRATION_LINE_PREFIX` (for example `GO overseer - `),
  and the principal types batch lines with that prefix.
- The typed-line check reads this repository's Claude Code transcripts from
  `~/.claude/projects/<the repository path, each non-alphanumeric character as "-">`. If the supervisor's session
  runs from another folder, set `AGET_MIGRATION_PROJECTS_DIR` to that session's transcript folder.

**Validation evidence.** The second outcome test ran on 2026-10-06: a fresh template-built supervisor took two worker members from 3.35.1 to v3.36.0 through apply, launch, push to local remotes and the ledger. Its result was FAIL: P3 exceeded the principal-line count and P6 exceeded the principal-wait time. The principal accepted that FAIL as named limits under weekly-train:R59, including F-3/F-5/F-6/F-8 and the hooks refusal; F-5 was subsequently fixed by the cache-free default. Supervisor-template members stay INCONCLUSIVE. This fixture run is not evidence of real-fleet deployment or GitHub continuous integration.

**Round 2 source tests.** Round 2 and Round 2b name the two pre-publication correction passes: documentation and behaviour fixes, followed by protected-mode, after-run consumer and provenance fixes. Historical Round 2 verification: `python3 -m pytest tests/migration_kit -q -p no:cacheprovider` gave 1523 passed on Python 3.14.8 and Python 3.12.13 before the protected-mode changes. The later protected-mode and after-run consumer corrections also passed the full local kit suite on both interpreters before this text-only amendment. These are local source-test results, not GitHub CI results or a further outcome run. Re-run the kit suite on the tagged checkout and record its measured count; the prior candidate result does not establish verification of the amended commit. The after-run A check compares a mode-bearing protected receipt with the working-tree executable bit and, where tracked, the regular-file mode in HEAD; ignored/untracked protected files need no HEAD entry. Ordinary D payloads still require the release mode in HEAD, and unavailable Git readings remain INCONCLUSIVE.
