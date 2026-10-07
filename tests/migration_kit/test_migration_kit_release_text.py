"""Gate 3 of the v3.36.0 kit design pass (v336-release:R28): the release text says what the kit's code now does, and
states its limits in one place (design read 2, D-1 and D-12; R4-T15; R3-T8; REVW2's condition on B141 #6). Each test
fails on 34353311's text and passes after."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTES = (ROOT / "release-notes/v3.36.0.md").read_text()
SOP = (ROOT / "sops/SOP_fleet_migration.md").read_text()
SESSION = (ROOT / "scripts/migration_kit/BATCH_SESSION.md").read_text()
LIMITS = "What the kit guarantees, and its stated limits"


def row(step):
    return next(ln for ln in SOP.splitlines() if ln.startswith(f"| {step} |"))


def limits_section():
    i = NOTES.index(f"### {LIMITS}")
    return NOTES[i:NOTES.index("\n### ", i + 5)]


def test_r4_t15_the_hook_remedy_routes_through_the_receiver_never_a_kit_write():
    """R4-T15, J-7 text half. At 34353311 SOP B2 says "install it as a file" and the release note "install such a
    hook as a file": a write into the member's .git/hooks, which only the receiver's own session may make."""
    for text in (SOP, NOTES, SESSION):
        assert "install it as a file" not in text and "install such a hook as a file" not in text
    b2 = row("B2")
    assert "drop it" in b2 and "that receiver's own session" in b2 and "never a write by the supervisor" in b2
    assert "rehearses every member even when one is refused" in b2
    assert "among those B2 rehearsed to PASS" in row("B3")
    assert all(v in row("B7") for v in ("APPLIED", "REFUSED", "ROLLBACK-INCOMPLETE", "SKIPPED", "NOT-STARTED",
                                        "IN-PROGRESS"))


def test_r3_t8_a_zero_line_hold_is_not_described_as_a_merge_decision():
    """R3-T8 (J-1 text). At 34353311 BATCH_SESSION.md and the release note call it "for a merge decision"."""
    for text in (NOTES, SESSION):
        assert "for a merge decision" not in text
        assert "told to KEEP it" in text


def test_d12_one_limits_section_and_no_stale_claim():
    """D-12: one authoritative limits section, written from the code. At 34353311 there is none, the note says the
    apply compares bytes and not HEAD, places files with `cp -f`, and stages under workspace/.tmp."""
    assert NOTES.count(f"### {LIMITS}") == 1 and SOP.count(f"### {LIMITS}") == 0
    steps = "\n".join(ln for ln in SOP.splitlines() if re.match(r"\| B\d+[a-z]? \|", ln))   # not the version history
    for stale in ("compares bytes, not HEAD", "workspace/.tmp/", "the member's own `cp -f` follows",
                  "the member's HEAD is not"):
        assert stale not in NOTES and stale not in steps and stale not in SESSION, stale


def test_d1_session_writes_are_stated_as_detected_not_prevented():
    """D-1 (design read 2), closed by a stated limit: the limits section says session writes are detected after the
    run, not prevented, and names the case G cannot see. At 34353311 no such statement exists."""
    s = limits_section()
    assert "detected, not prevented" in s
    assert "a link made, written through and removed inside the session" in s


def test_b141_6_the_exclusive_mutation_condition_is_stated():
    """REVW2's condition for accepting B141 #6's narrowing: the release text conditions every guarantee about a
    member's files on nothing else changing its folder tree, other processes included."""
    s = limits_section()
    assert "nothing else changes that member's folder tree" in s and "not only no second kit run" in s
    assert re.search(r"folder moved after that last check is not seen", s)


def test_b148_7_the_sop_carries_the_exclusive_mutation_condition():
    """B148 finding 7 (REVW3's falsifier, widened to the operative words). B143's acceptance of B141 #6 needs the
    condition in the SOP too: the whole step, the member's tree and listed files, other processes' writes, renames and
    moves. On stage F2 only the release note carried it."""
    b7 = row("B7")
    assert "nothing else changes that member's folder tree and its listed files for the whole step" in b7
    assert "no other process, not only no second kit run, may write, rename or move anything in it" in b7
    assert "every other step that writes into a member" in b7


def test_b148_5_d1_g_names_the_population_it_reads():
    """B148 finding 5 / D-1's condition: the release note and the SOP say which paths G reads, including a `.claude/`
    file ignored by git, and what it does not read. On stage F2 both said G read every path the session wrote."""
    lim = limits_section()
    assert "every path the session wrote or changed" not in NOTES
    assert "every `.claude/` file whose bytes changed, ignored by git or not" in lim
    assert "nor a write to a path git ignores outside `.claude/`" in lim
    b8 = row("B8")
    assert "every `.claude/` file whose bytes changed (ignored or not)" in b8 and "is not read" in b8


def test_b148_6_the_text_names_what_is_implemented_and_states_what_is_not():
    """B148 finding 6, interim narrowing (final text at F3): the R2 subset is named with the readers not yet bound;
    evidence and output writes are stated as not link-refusing; the KEEP difference record is stated as not checked;
    the table consumers are named. On stage F2 each claim was universal."""
    for text in (NOTES, SESSION):
        assert "Every result a later step reads is bound to its run" not in text
        assert "Not yet bound in this draft, and read as plain files" in text
        assert "are not written by the contained writer and can follow a link there" in text
        assert "Every tool reads these meanings from one table" not in text
        assert "Not yet read from the table in this draft" not in text   # F3: all three now read it (A10)
        assert "The scope check and the push gate read the same table" in text
    assert "checked only\n  for the receipt naming the path" not in NOTES
    assert "The difference a KEEP item asks the session to record is not checked" in NOTES


def test_b151_1_the_protocol_text_says_what_the_value_blocks_and_what_it_does_not():
    """B151 finding 1 (text). The release note names the empty allow-list and states what it does not close; the
    universal "no protocol at all" claim is gone. The code's value is the one the text names. On stage E2c the note
    claimed "allowed no protocol at all" while the value was `none`."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("launch_batch", ROOT / "scripts/migration_kit/launch_batch.py")
    LB = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(LB)
    assert LB.session_env()["GIT_ALLOW_PROTOCOL"] == ""
    assert "git allowed no\n  protocol at all" not in NOTES
    assert "`GIT_ALLOW_PROTOCOL=` with nothing after it" in NOTES and "a remote helper included" in NOTES
    assert "removes or changes that variable" in NOTES


def test_b151_2_the_confirmation_text_names_the_isolation_routine():
    """B151 finding 2 (text). The confirmation-run bullet says the clone and its siblings go through the isolation
    routine (rewrite rules removed, routes read back). On stage E2c it said push URLs only, which was what the code
    did, while the shared isolation paragraph already listed the confirmation run among its callers."""
    assert "closes the push routes git would resolve" in NOTES
    assert "first go through the isolation routine above" in NOTES


def test_b152_1_the_text_states_how_the_dead_url_is_kept_from_resolving():
    """B152 finding 1 (text). Where isolation is defined, the text says the dead URL's scheme is closed in each copy
    and that an environment reopening it is a refusal; the push-routes limit no longer says only "a real
    destination". On stage E2d "cannot resolve" was asserted with nothing keeping a helper of that name from starting."""
    for text in (NOTES, SESSION):
        assert "`protocol.no-push.allow = never`" in text and "A copy is refused when the environment reopens" in text
    assert "refuses the copy if any resolves to a real destination" not in NOTES


def test_b153_1_the_text_bounds_the_dead_scheme_claim_and_states_the_limit():
    """B153 finding 1 (text). The closure is described as the code does it (the last entry; includes read after the
    copy's file refused), "starts no remote helper of that name" is gone, and the push-route guarantee is stated as
    limited to the routes and configuration forms it checks. On stage E2e the helper claim was unconditional."""
    for text in (NOTES, SESSION):
        assert "so it starts no remote helper of that name" not in text
        assert "written as the last entry of the copy's config file" in text and "includes another file" in text
    assert "This is a check at points in" in NOTES   # E2e3: the narrower limit replaced E2e2's refused one


def test_b154_1_the_text_states_the_include_rule_its_cost_and_the_point_in_time_limit():
    """B154 finding 1 (text). The include rule where isolation is defined (release note, BATCH_SESSION.md), its cost to
    an operator in the SOP's B2 row, and the point-in-time limit in place of E2e2's refused one. On stage E2e2 none of
    these was stated and the refused limit claimed every listed form closed."""
    for text in (NOTES, SESSION):
        assert "`onbranch:` or `hasconfig:`" in text and "given a `gitdir:` condition" in text
        assert "After each checkout the kit makes in a copy, the push routes are read again." in text
    assert "This is a check at points in\n  time" in NOTES and "and the kit does not claim to close it" not in NOTES
    assert "`onbranch:` or `hasconfig:` condition, or an include of a file inside the repository: an operator" in SOP


def test_b155_the_include_refusal_text_names_the_entry_not_a_line():
    """REVW5's B155 note (text): `git config --show-origin` gives the file and the entry, not a line number; the texts
    say "the file and the entry". On stage E2e3 they said "the file and the line"."""
    for text in (NOTES, SESSION, SOP):
        assert "names the file and the line" not in text and "names the file and the entry" in text


def test_b156_1_the_push_routes_text_says_routes_are_resolved_as_pushes():
    """B156 finding 1 (text). The push-routes limit says each route is resolved as for a push, a `pushInsteadOf` rule
    included. On stage E2e4 it did not, and the code resolved non-remote candidates as fetch URLs."""
    assert "each resolved as git would resolve it for a push (a\n  `pushInsteadOf` rule included)" in NOTES


def test_e2f_the_text_states_the_contained_environment_and_what_is_still_open():
    """E2f (text). The release note states the contained environment as built (kit git acts: no transport, no copied
    hook; member code: bounded, no operator configuration, transports as they are) and no longer says git in a copy
    runs with the inherited environment. At E2e7 the "not yet changed" item said it did."""
    assert "git in a copy still runs with the inherited environment and configuration" not in NOTES
    assert "**The kit's git acts and member code in copies run in a contained environment.**" in NOTES
    # E2g closed the auditor path, so the "not yet changed" item no longer lists it (it did from E2f to E2f2)


def test_b160_1_the_text_says_the_contained_environment_is_checked_before_use():
    """B160 finding 1 (text). The contained-environment bullet says the push routes are read again under that
    environment before each run or act. On stage E2f it did not, and the code did not."""
    assert "the copy's push routes are read again under that\n  environment" in NOTES


def test_e2g_the_text_states_work_roots_run_folders_and_what_runs_inside_the_run():
    """E2g (text). The release note states the work root and its fresh run folders (refused inside a repository;
    nothing removed; run folders kept), the session rehearsal under the contained environment with LINKS after the
    run, B8a's materialized hook (INCONCLUSIVE for a link outside the member) and the auditor path; and it no longer
    says a clone's work folder may lie inside the member, that copies are made "wherever" --scratch is, or that the
    auditor's path, the rehearsal's sessions and B8a's hook are not yet changed. On stage E2f2 it said all three."""
    assert "**Each run's copies and clones go into a fresh run folder under a work root.**" in NOTES
    assert "is refused before anything is made" in NOTES and "Run folders are kept" in NOTES
    assert "**Rehearsal sessions, B8a's hook and the known-missing auditor run inside the run.**" in NOTES
    assert "`hook.run` false and the reason in `hook.why`, never PASS without the hook" in NOTES   # F3 (D1)
    for gone in ("(a clone's work folder may)", "wherever that is", "an auditor's path is not checked",
                 "sessions and B8a's pre-push hook still run as before"):
        assert gone not in NOTES, gone


def test_b162_the_text_states_names_whole_run_links_and_resolved_hook_sources():
    """B162 findings 1-3 and 5 (text). The release note says a receiver's name must be one folder name, a work root
    git cannot answer for is refused, LINKS covers the whole run folder with its declared siblings and a hooks path
    outside it is refused, and the pre-push source is classified with every link on the way followed. On stage E2g it
    said LINKS covered "every symbolic link under the copy" and classified only a link at the entry itself."""
    assert "must be a single folder name (not a path, `.` or `..`)" in NOTES
    assert "git cannot answer\n  whether it lies in a repository" in NOTES
    assert "every symbolic link under the run folder (the copy and its declared copied siblings" in NOTES
    # reworded in E2g3 (B163 finding 4): the launch refusal now also names a link in the hooks folder
    assert "A `core.hooksPath` that names a folder\n  outside the run folder, or holds a link leading outside it, refuses the launch" in NOTES
    assert "with every link on the way followed (the hooks folder itself included)" in NOTES
    assert "every symbolic link under the copy must resolve inside its run folder" not in NOTES


def test_b163_the_text_drops_the_unaccepted_hooks_path_limit_and_states_the_re_read():
    """B163 findings 1 and 4 (text). The release note no longer claims that a session's change to `core.hooksPath` is
    left unchecked (REVW6 did not accept that limit); it says the value is read again after the session, and that with
    declared siblings a narrower run folder is not accepted. On stage E2g2 it stated the limit."""
    assert "A change to `core.hooksPath` made during the session is not checked afterwards" not in NOTES
    assert "it is read again (under the\n  session's configuration, its value byte for byte) after the session" in NOTES
    assert "and a narrower folder is not accepted" in NOTES


def test_e2h_the_text_states_inrun_read_only_status_and_the_one_sibling_population():
    """E2h (text): INRUN in each remote or configuration writer, read-only status reads, one declared-sibling
    population for the post-run walk and F's confirmation (B164 finding 2), and BIND named among the open R1 sites.
    On stage E2g3 none of these was stated."""
    assert "checks for itself that it was given a run folder, that the repository lies inside it" in NOTES
    # reworded in E2h2 (B165 finding 2): every live read, not only status; and in E2h3 (B166 finding 2)
    assert "to read a live member takes no optional lock and fetches no" in NOTES
    assert "one population that F's confirmation run also copies" in NOTES
    # E2i replaces the open-site sentence with BIND itself (test_e2i_the_text_states_ignore_state_detection_its_gaps_and_bind)
    assert "**A protected-write entry acts only at its member.**" in NOTES


def test_b165_the_text_states_the_probe_under_inrun_the_act_preflight_and_unchanged_reads():
    """B165 findings 1-2 (text). The release note puts the push-route reader's short-lived remote under INRUN, says the
    kit re-asks identity and LINKS before its later checkout, add, rm and commit, and that every live read leaves the
    member's git folder unchanged. On stage E2h it named status reads only and none of the rest."""
    assert "and the short-lived remote the push-route reader adds to resolve" in NOTES
    assert "it asks the same identity test and LINKS again" in NOTES
    # reworded in E2h3 (B166 finding 2): the private index is named for the shared helper's reads only
    assert "so a stat refresh never rewrites the member's" in NOTES


def test_b166_the_text_states_the_hard_link_refusal_and_the_live_read_population():
    """B166 findings 1-2 (text). The release note says the identity test refuses a git-folder file with a second
    name outside the object store, and states what every live read does, which reads also get a private index, and
    the census test. On stage E2h2 it named symbolic links only and said every live read got a private index."""
    assert "a second name (a hard link: git appends a reflog in place" in NOTES   # reworded in E2h6 (B169)
    # reworded in E2h4 (B167 finding 1), and in E2h5 (B168 finding 1): no exemption at all
    assert "There is no exemption, the object store included" in NOTES
    assert "A test lists every git command line in the kit" in NOTES
    assert "and is given a private copy of the index, so it leaves the member's git folder as it was" not in NOTES


def test_e2i_the_text_states_ignore_state_detection_its_gaps_and_bind():
    """E2i (DESIGN clause 8, IGN, H-3/R1-T9; BIND, R1-T7) (text). The release note says git's whole ignore state is
    compared around every suite, hook and auditor run and around the live session, names the gaps clause 8 states and
    the `.git/config` consequence, and binds a protected-write entry to its register location or a rehearsal's run
    folder. On stage E2h3 it said the content of the file `core.excludesFile` names and git's default ignore file are
    not compared, and that the entry is not yet bound."""
    assert "Git's whole ignore state is also read immediately before the suite, after it and after the hook" in NOTES
    assert "**Ignore state is detection, with stated gaps.**" in NOTES
    assert "an ignore rule\n  changed and restored between two readings" in NOTES
    assert "writes the repository's own `config` reads INCONCLUSIVE as well" in NOTES.replace("\n  ", " ")
    assert "**A protected-write entry acts only at its member.**" in NOTES
    assert "the new option `--run`" in NOTES
    assert "Not compared: the content of the file that setting names" not in NOTES
    assert "Not yet changed by the design pass in this draft" not in NOTES


def test_b167_the_text_states_that_internal_links_are_followed():
    """B167 finding 1 (text). The release note says the shared-storage test follows symbolic links that stay inside
    the copy, and that only the git folder's own loose-object and pack folders are left uninspected. On stage E2h3 it
    said files "outside the object store" were inspected, and named no link."""
    assert "symbolic links that stay inside the copy are followed to the file or folder they" in NOTES
    # reworded in E2h5 (B168 finding 1): the exemption the E2h4 sentence qualified is removed
    assert "any entry or folder that cannot be inspected each refuse" in NOTES   # reworded in E2h6 (B169)
    assert "outside the object store, with a second name" not in NOTES


def test_b168_the_text_states_there_is_no_exemption_and_what_is_refused():
    """B168 finding 1 (text). The release note says the shared-storage test has no exemption, the object store
    included, that a hard-linked local clone is refused, and that every kit copy has its own files. On stage E2h4 it
    said the git folder's own loose-object and pack folders were not inspected."""
    assert "There is no exemption, the object store included" in NOTES
    assert "as a plain local `git clone` makes, is refused" in NOTES
    assert "loose-object folders and pack folder are not inspected" not in NOTES


def test_b169_the_text_states_the_allow_list_for_the_git_folder():
    """B169 findings 1-2 (text). The release note says everything reachable in the git folder must be a folder or a
    regular file with one name, that a FIFO, socket or device and a failed inspection refuse, and that only a link
    whose target does not exist is skipped. On stage E2h5 it named second names and unlistable folders only."""
    assert "is a folder or a regular file with one name" in NOTES
    assert "a FIFO, socket or device, and any entry or folder that cannot be inspected each refuse" in NOTES
    assert "only a link whose target does not exist is skipped" in NOTES


def test_c2a_the_text_states_the_bound_receipt_ci_coverage_exclusions_baseline_and_ruling_names():
    """C2a (R2-T3, T6, T13, T14, T15) (text). On stage E2i the release note listed the apply receipt among the plain
    files and said a ruling was not checked to name the comparison it passes."""
    assert "The apply receipt's entry for a member is used only when it is bound" in NOTES
    assert "a success of another workflow does not stand for a missing one (CI-INCOMPLETE)" in NOTES
    assert "B8a reads its CI exclusions at the packet's head" in NOTES
    assert "(a truncated output) is not RECORDED" in NOTES
    assert "`workflows-not-compared`" in NOTES
    assert "the ruling is not checked to name the missing comparison" not in NOTES


def test_b171_the_text_states_git_resolved_excludes_files_unreadable_inputs_and_the_copy_exception():
    """B171 findings 1-2 and its F3 note (text). On stage E2i the release note said the bytes of the file the setting
    names were compared, did not say an input unreadable at both readings is INCONCLUSIVE, and said an unreadable
    register refuses without the copy exception."""
    assert "the bytes of the file git resolves it to (asked of git" in NOTES
    assert "(at either reading, or at both), reads INCONCLUSIVE" in NOTES
    assert "location inside `--run` is admitted as a copy without requiring the register to resolve" in NOTES  # F3


def test_b172_the_text_states_every_ign_file_is_read_as_git_reads_it():
    """B172 finding 1 (text). On stage E2i2 the release note did not say where a relative name IGN reads is read
    from; the kit read it from its own folder."""
    assert "Each of these files is read as git reads it: a relative name" in NOTES
    assert "is read from the member's folder, where git runs, never from the folder the kit runs in" in NOTES


def test_b173_the_text_states_names_are_taken_byte_for_byte():
    """B173 finding 1 (text). On stage E2i3 the release note did not say that each name git returns is taken byte for
    byte, nor what happens when names git lists cannot be told apart."""
    assert "each name git returns is taken byte for byte, one name per query" in NOTES
    assert "that element cannot be read" in NOTES


def test_b174_the_text_states_git_answers_which_config_files_it_reads():
    """B174 finding 1 (text). On stage E2i4 the release note did not say that whether git reads a global or system file
    is git's answer, not the kit's reading of git's environment."""
    assert "Whether git reads a global or a system configuration file at all is git's answer (`git var`)" in NOTES


def test_b175_the_text_states_every_included_file_is_read():
    """B175 finding 1 (text). On stage E2i5 the release note did not say that every file an include names is read,
    with or without settings, nor that an inactive include's file is read too."""
    assert "every file an `include.path` or `includeIf.<condition>.path` names, resolved as git resolves" in NOTES
    assert "a file named by an include whose condition does not hold is read too" in NOTES


def test_b176_the_text_states_process_includes_and_unreadable_origins():
    """B176 finding 1 (text). On stage E2i6 the release note did not say that an include from process configuration is
    read, nor that an entry from a source the kit cannot read makes the reading unavailable."""
    assert "an include set by the process's own configuration (`GIT_CONFIG_COUNT`, `-c`)" in NOTES
    assert "no entry is passed over" in NOTES


def test_b177_the_text_states_the_queries_describe_what_git_reads():
    """B177 finding 1 (text). On stage E2i7 the release note did not say that IGN's configuration queries describe what
    ordinary git commands read, whatever GIT_CONFIG names."""
    assert "These configuration queries describe what ordinary git commands read" in NOTES


def test_b179_the_text_states_distinct_names_absent_members_and_whole_ids():
    """B179 findings 1-3 (text). On stage C2a the release note did not say that same-named workflows read
    CI-INCOMPLETE, that an absent member stops preparation, or that failing ids are read whole."""
    assert "two committed workflows that share a display name read CI-INCOMPLETE" in NOTES
    assert "it stops too for a requested member the receipt has no entry for" in NOTES
    # changed at C2a3 (B180 finding 1, labelled): the sentence now says where the ids are read from
    # changed at C2a5 (B182 finding 1, labelled): the sentence was rewritten around one summary and unique ends
    # changed at C2a7 (B185 finding 1, labelled): ids are read whole from the kit's report, not from display text
    assert "Failing ids are pytest's own node ids, read from the kit's report" in NOTES


def test_b179_the_text_states_the_selected_index_and_working_tree():
    """B179 findings 4-5 (text). On stage C2a2 the release note did not say that IGN reads the working tree and the
    index git selects."""
    # changed at E2i10 (B181 findings 1-2, labelled): both sentences gained a clause inside the parenthesis
    assert "asked of git, so a `GIT_WORK_TREE` or `core.worktree`" in NOTES
    assert "the index git reads (the one `GIT_INDEX_FILE` selects, when it is set," in NOTES


def test_b180_the_text_states_the_summary_only_and_counts_by_kind():
    """B180 finding 1 (text). On stage C2a2 the release note did not say that ids are read only from pytest's own short
    summary, that an id's end must be unique, nor that FAILED and ERROR lines account for their own counts."""
    # changed at C2a7 (B185 finding 1, labelled): the source is the kit's report; the count line is a cross-check
    assert "never from pytest's display text" in NOTES
    assert "the output's one pytest count line reports as many failed and errors as the report" in NOTES
    # changed at C2a5 (B182 finding 1, labelled): "read by the same reader" was added inside the parenthesis
    assert "each file's own short-summary lines, read by the same reader, under one `short test summary info`" in NOTES


def test_b181_the_text_states_gits_repository_answer_and_the_selected_index():
    """B181 findings 1-2 (text). On stage E2i9 the release note did not say that whether the folder is a repository is
    git's answer, nor that a selected index is part of the state and an unreadable one makes the reading unavailable."""
    assert "whether the folder is a repository at all, and which, is git's answer under that environment" in NOTES
    assert "a selected index that is present but not a regular, readable file makes the reading unavailable" in NOTES


def test_b181_the_text_states_coverage_by_workflow_path():
    """B181 finding 3 (text). On stage E2i9 the release note did not say that a committed workflow is covered only by a
    run of its own path."""
    assert "A committed workflow is covered only by a successful run of its own path" in NOTES


def test_b182_the_text_states_one_summary_and_unique_ends():
    """B182 finding 1 (text). On stage C2a3 the release note did not say that the output must hold one count line and
    one summary, that a line with more than one ` - ` is not guessed, nor that the runner marks unreadable files."""
    # changed at C2a7 (B185 finding 1, labelled): the summary rules gave way to the report's invocation rules
    assert "output names exactly one invocation in that report" in NOTES
    assert "gets an `IDS-UNKNOWN` line, never an id" in NOTES


def test_b183_the_text_states_only_gits_discovery_answer_reads_plain():
    """B183 finding 1 (text). On stage E2i10 the release note did not say that only git's own discovery answer makes
    a folder plain, nor that any other failed answer is unavailable."""
    assert "only when git's whole answer is its own discovery message that no repository was found" in NOTES


def test_b184_the_text_states_a_run_list_at_its_limit():
    """B184 finding 1 (text). On stage C2a4 the release note did not say that a run list at its limit does not count
    alone."""
    assert "A run list that reaches its limit (50 runs) counts only when the Actions REST count names exactly" in NOTES


def test_b185_the_text_states_the_kit_report_and_its_completeness():
    """B185 finding 1 (text). On stage C2a6 the release note said failing ids are read from pytest's short summary; it
    did not say they come from the kit's report, that the member's environment is put back, what makes a result
    complete, that baseline equality compares node ids, that the report is not authenticated, nor that B8a needs a
    complete result for PASS."""
    assert "loads the kit's report plugin through the environment" in NOTES
    assert "put back to the member's own values before any member code runs" in NOTES
    assert "Baseline equality compares distinct failing node ids, not outcomes per phase" in NOTES
    assert "code running inside pytest can change it" in NOTES
    assert "a B8a run that exits 0 INCONCLUSIVE rather than PASS" in NOTES
    assert "the runner records the one invocation each file's output names" in NOTES


def test_b186_the_text_states_the_selected_tree_for_a_nested_folder():
    """B186 findings 1-2 (text). On stage C2a7 the release note did not say that a relative excludes file and the index
    flags are read across the working tree git selects, also for a nested folder."""
    assert "a relative name is read from the top of the working tree git selects" in NOTES
    assert "across the whole working tree git selects (not only a nested folder given)" in NOTES


def test_b188_the_text_states_the_report_grammar_storage_and_last_call():
    """B188 findings 1-2 (text), with FWK-OVSR5's C2a7 advisory (1)-(2). On stage E2i12 the release note did not say
    that a malformed or non-regular report gives no known ids, that an early stop does, nor that the last suite call
    needs its own result."""
    assert "holds a record outside the plugin's typed grammar" in NOTES
    assert "a FIFO is refused at once, never waited on" in NOTES
    assert "a run stopped early by `-x` or `--maxfail` gives no known ids" in NOTES
    assert "an earlier call's output never stands in for it" in NOTES


def test_b189_the_text_states_committed_files_are_read_only_as_regular_files():
    """B189 finding 1 (text). On stage C2a8 the release note did not say that a file judged at a commit is read only
    as a regular file, nor that a committed link reads INCONCLUSIVE."""
    assert "is read only when that commit holds it as a regular file (mode 100644 or 100755)" in NOTES
    assert "a committed symbolic link (whose stored bytes are its target)" in NOTES


def test_b190_the_text_states_the_last_calls_own_result_and_declared_deselection():
    """B190 findings 1-2 (text). On stage E2i13 the release note did not say that the result is bound to the last
    call's own id, nor that undeclared deselection or `--lf` gives no known ids."""
    assert "read from the result that carries that call's own id whatever order results arrive in" in NOTES
    assert "deselected no test beyond its own `--deselect` arguments" in NOTES
    assert "Exit 1 must name a failing test and exit 0 none" in NOTES
    assert "only the report's own name is checked for a link" in NOTES


def test_b191_the_text_states_every_committed_reader_and_the_working_tree_side():
    """B191 finding 1 (text), with FWK-OVSR5's E2i13 advisory (1). On stage C2a9 the release note named only the
    judgment, receipt and settings readers, and said nothing of links in the working tree."""
    assert "B8a's CI exclusion sources and declared deselect file, the ledger's version file" in NOTES
    assert "read the entry itself, reached with no link followed" in NOTES   # changed at E2i15 (labelled): whole path


def test_e2i15_the_text_states_no_link_followed_anywhere_on_a_working_tree_path():
    """FWK-OVSR6's E2i14 pre-read 1-3 (text). On stage E2i14 the release note said the working-tree readers read the
    entry itself, which held for the leaf only, and did not name the merge, project-settings or exclusion readers."""
    assert "reached with no link followed anywhere on its path" in NOTES
    assert "a merged file's authored lines, the launch's copy of the member's project settings" in NOTES


def test_e2i16_the_text_states_the_member_folder_and_readings_that_cannot_be_taken():
    """FWK-OVSR6's E2i15 pre-read 1-3 (text). On stage E2i15 the release note said nothing of the member folder named
    with a trailing slash, of folders above the member, or of two unreadable readings comparing equal."""
    assert "The member folder itself is opened without following a link however its name is written" in NOTES
    assert "A reading that cannot be taken (unreachable, unreadable, or only a kind) equals nothing, itself included" \
        in NOTES                                       # changed at C2a10 (labelled): a kind-only reading joins them


def test_c2a10_the_text_states_the_final_exit_ownership_population_and_non_readings():
    """B192 findings 1-3 and FWK-OVSR6's E2i16 pre-read 1-3 (text). On stage E2i16 the release note said nothing of
    the exit after the session-finish hooks, of ids reused by other calls or later wrapped runs, of collection
    narrowed outside the command line or exclusions as identities, or of non-readings in B and B8a."""
    assert "written after every session-finish hook and wrapper has run" in NOTES
    assert "a call id used by any other call, or a call or result without an id" in NOTES
    assert "leaves the ids unknown rather than crediting the run before it" in NOTES
    assert "a declared test id excludes that test only" in NOTES
    # changed at C2a11 (labelled; B194 finding 6): the narrowed-population sentence became the standing-policy one
    assert "a population whose recorded selection" in NOTES
    assert "A member folder written with `.` or `..` in its name is refused" in NOTES
    assert "a path in B8a's clone whose content could not be read" in NOTES


def test_c2a11_the_text_states_the_standing_selection_policy_and_uncreated_candidates():
    """B194 finding 6 (text). On stage C2a10 the release note said any narrowing outside the command line gives no
    known ids, which refused a member's standing configuration, and said nothing of uncreated candidates."""
    assert "equals the selection the member's baseline recorded as its standing policy" in NOTES
    assert "left no test candidate uncreated by a collection hook" in NOTES
    assert "collected a population no input outside its own command line narrowed" not in NOTES


def test_c2b_the_text_states_bound_push_evidence_after_run_inputs_and_push_authority():
    """R2-T10, R2-T11, R2-T12 (text). On stage C2a the release note did not say how the push gate's B8a, baseline and
    snapshot readings are bound, that unbound after-run inputs read INCONCLUSIVE, or that a push line is bound to its
    packet; it said --extra-commit is compared with no typed line."""
    assert "the push gate takes a B8a record only when it names the member and its tree check was enforced" in NOTES
    assert "A migrating member judged without its suite command reads INCONCLUSIVE" in NOTES
    assert "a settings watch that does not cover the session" in NOTES
    assert "a push from any other packet, even one with the same batch number, is refused" in NOTES
    assert "`--extra-commit` must be a commit the recorded push line names" in NOTES
    assert "Three push options are compared with no typed line" not in NOTES


def test_c2c_the_text_states_b8a_and_baseline_are_bound_to_their_runs():
    """R2-T16 (c), R2-T17 (text). On stage C2b the release note said the B8a and baseline records were read as plain
    files, not for a current run."""
    assert "The push gate and the after-run check read each only as the current run" in NOTES
    assert "though not for a current run" not in NOTES


def test_c2d_the_text_states_the_apply_receipt_is_bound_to_its_run():
    """R2-T17 (text). On stage C2c the release note named the apply receipt's run as not yet bound."""
    assert "writes its final receipt as that run's result" in NOTES
    assert "the apply receipt's run (its entry is checked, below)" not in NOTES


# --- F3: every reason the suite-verdict path can emit has its limit sentence (weekly-train:R15; D-12) -------------

F3_REASON_SENTENCES = {   # reason class (gate3/F3_REASON_LIMIT_MAP_D2.md) -> a phrase its limit sentence must hold
    "[5] no output path": "whose arguments name no output path is refused by argparse and records no run",
    "[7] B8a setup": "cannot clone the member, check out the tested commit, copy a declared sibling folder",
    "[8] packet head": "is not in the member's history",
    "[12] timeouts": "gives the suite 2400 seconds and the pre-push hook as long",
    "[16] nothing passed or failed": "reports no passed and no failed test",
    "[27] baseline witness": "F reads INCONCLUSIVE when the baseline holds no selection record",
    "[28] whole witness": "F compares the whole selection record with the baseline's whether or not anything narrows",
    "[29] parallel file set": "a run whose set of test files differs from the baseline's reads INCONCLUSIVE",
    "[31] producer hooks": "implements a test-producing hook",
    "[32] execution hooks": "implements `pytest_pyfunc_call`, `pytest_runtest_protocol`",
    "[33] runtest / TestCase": "`IsolatedAsyncioTestCase` overrides five of them",
    "[34] pytest internals": "changes pytest's own collection or run functions",
    "[35] census unavailable": "The census, an independent `pytest --collect-only` run with no conftest, is unavailable",
    "[36] pytest_plugins": "loads a plugin through `pytest_plugins`",
    "[37] census import": "cannot import without the member's conftest",
    "[38] outside params": "Parameters added outside the test's own module",
    "[39] swapped item": "puts into the run without collection creating it",
    "[40] identity": "proves an executed call of every declared test's collected function code",
    "[40] identity data": "are not independently compared for suite completeness",
    "[40] unreadable identity": "a test whose code cannot be read by value",
    "[40] wraps limit": "a decorator that does not keep `__wrapped__`",
    "[40] witness tool": "a free tool id (3 or 4)",
    "[40] other process": "A test run in another process (xdist workers)",
    "[40] setup swaps": "a failure that lived only in a swapped helper is not detected",
    "[40] passed only": "Every call reported passed must show that code starting and then returning there",
    "[40] frame check": "from a frame running that very code object",
    "[40] swallowed": "a wrapper that swallows the failure",
    "[40] any run raised": "raised in any of its runs during its call",
    "[40] activation paired": "paired by activation: the same run of the code (its frame) must begin in the call",
    "[40] setup return": "a return from a run that began during setup never counts",
    "[40] other thread": "own code runs on another thread during its call reads INCONCLUSIVE, even when that run completes",
    "[40] unfinished run": "begins a run in its call that has not finished when the call ends",
    "[40] non-authentication": "it does not authenticate against member code altering the kit's loaded observer/state",
    "[41] unittest static separate": "count as static: a test skipped by one is a known disposition",
    "[40] tool taken": "frees, takes or re-registers the kit's monitoring tool",
    "[41] unittest static": "decorators are read at collection",
    "[34] per-test check": "as each test is about to run",
    "[32] hook owner": "judged by the file of the function that implements it",
    "[32] hook home": "be the object its module, loaded from pytest's files, holds under its name",
    "R17 baseline": "the baseline is not RECORDED, until an approval of that exact selection is",
    "[41] runtime skips": "skipped or xfailed at run time for a reason its own static marks do not give",
    "[43] sessions": "holds records of another session",
    "[44] judged form": "never ran its declared suite command in a form F judges",
    "[46] unresolved program": "whose program the kit cannot name without the shell expanding it",
    "[47] later pytest output": "whose output shows a pytest run",
    "[50] attempt heading": "mentions an attempt and is not `## Attempt <id>`",
    "[52] receipt batch/location": "this batch's and its entry was applied at the member's own location",
    "C2 no report line": "holds no kit report line",
    "C3 -k/-m": "A `-k` or `-m` in the suite command",
    "C5 program word": "`pip install pytest`",
    "C9 narrowing approval": "recording a selection is not approving it",
    "R17 approval route": "the principal's approval of that exact selection is recorded",
    "C10 write scope": "declares no write scope has its write scope not proven",
    "C17 older receipt": "names held protected files by path only",
    "C19 non-regular config": "`GIT_CONFIG_GLOBAL=/dev/null`",
    "C20 singleton glob": "A write-set glob is checked by its literal prefix",
    "C20 LAUNCHED reuse": "keeps the members an invocation launched in a module-level set",
}


def test_f3_every_suite_verdict_reason_class_has_its_limit_sentence():
    """F3 (D-12; weekly-train:R15; the after-run checker fails P2 on an INCONCLUSIVE row with no quoted release-note
    limit): each reason class BILD16's map found on D2's suite-verdict path, and each availability cost the reviewers
    accepted on condition of F3 wording, has its sentence inside the one limits section, and each sentence names the
    verdict. On D3's text 25 classes had none."""
    s = limits_section()
    missing = [k for k, phrase in F3_REASON_SENTENCES.items() if phrase not in s]
    assert not missing, missing
    group = s.split("**What reads INCONCLUSIVE because the kit cannot prove it (weekly-train:R15).**")[1]
    for line in (ln for ln in group.splitlines() if ln.startswith("  - ")):
        assert any(w in line for w in ("INCONCLUSIVE", "not proven", "no known ids", "CI-INCOMPLETE", "stays current",
                                       "known disposition")), line[:120]


def test_f3_the_contradictions_with_the_code_are_corrected():
    """F3 (BILD16's checklist audit of D3's text): statements the code contradicts are gone from the release note,
    BATCH_SESSION.md and the procedure, and their corrections are present."""
    for gone in ("The commit ids in the line are compared with nothing", "(a clone's work folder may)",
                 "The tool removes whatever folder already sits at", "leaves those two folders there",
                 "Not compared: the content of the file that setting names", "without reading the register",
                 "Not yet read from the table in this draft",
                 "the push gate's reading of the B8a suite record, the baseline record and the apply receipt"):
        assert gone not in NOTES and gone not in SOP and gone not in SESSION, gone
    assert "makes the earlier result unmet when its arguments name that output" in NOTES
    assert "the push check binds the packet" in NOTES and "--packet B/LAUNCH_PACKET.json" in SOP


def test_r62_f5_is_fixed_by_default_across_the_release_text():
    """All current F-5 claims describe the cache-free default rather than an override requirement."""
    for path in ("release-notes/v3.36.0.md", "CHANGELOG.md", "DEPLOYMENT_SPEC_v3.36.0.yaml",
                 "handoffs/RELEASE_HANDOFF_v3.36.0.md", "handoffs/REMOTE_MIGRATION_MESSAGE_v3.36.0.md"):
        text = (ROOT / path).read_text()
        assert "F-5 — Fixed." in text or "F-5 - Fixed." in text, path
        assert "F-5 — Named limit." not in text, path
        assert "The default member suite command" in text and "python3 -m pytest -q -p no:cacheprovider" in text
        assert "K-1 remains a named cost" in text, path
    for step in ("B1", "B8"):
        text = row(step)
        assert "F-5 is fixed" in text and "python3 -m pytest -q -p no:cacheprovider" in text
        assert "Named limits F-5 and F-6" not in text
    assert "K-1 remains a named cost" in SOP
    handoff = (ROOT / "handoffs/RELEASE_HANDOFF_v3.36.0.md").read_text()
    assert "**Release outcome fixes and known gaps a supervisor may meet**" in handoff
    assert "Known gaps a supervisor may meet (listed, not fixed in this release)" not in handoff
