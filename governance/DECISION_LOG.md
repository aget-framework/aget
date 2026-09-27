# Decision Log

**What this is**: the framework's decisions and the reasons for them, written for readers outside the project.
**Started**: 2026-09-26. Decisions from that date on are logged here. A back-fill of earlier decisions that are still in
force is planned. One decision of that date is pending clarification and not yet logged.
**What is not here**: decisions about personal agents, session records and raw deliberation are never published;
decisions that name private things appear as the general principle with the names removed; one-night operational
decisions (scheduling, one batch, one go-ahead) are not logged.
**Related**: the public requirements (`requirements/`) state what the framework must do; this log says why.

---

### 2026-09-26 · A public decision log, written for outsiders

**Decision**: The framework publishes a plain log of what it decided and why, written fresh for a reader outside the project. The raw decision records stay private.

**Why**: Outsiders could see what the framework does but not why. The principal's stated reason for keeping the raw records private: the local set of agents mixes framework agents with personal ones, and the separation between them needs to be clearer first.

### 2026-09-26 · Public requirements kept current by a release check

**Decision**: The public requirements are rewritten from the principal's private requirements, and a release check fails when they fall behind.

**Why**: The public requirements had not been touched for about five months and none of the principal's recent requirements appeared in them.

### 2026-09-26 · One measured goal for framework openness

**Decision**: The framework adopts one goal: an outsider can rebuild what it does and why from the public side alone, scored at each release.

**Why**: The earlier effort on this subject could not graduate because there was no goal to graduate into.

### 2026-09-26 · What private material may reach the public log

**Decision**: Four classes: personal agents, sessions and raw deliberation are never published; decisions that name private things are published as the general principle with names removed; decisions already general are published as written; one-night operational decisions are not logged.

**Why**: Every public good needs a private space where intent is formed; the line keeps that space while publishing the reasons outsiders need.

### 2026-09-26 · Revive the April openness requirement and publish the principal's requirements

**Decision**: The April requirement that the framework be rebuildable from its public side is revived with a working test; the principal's requirements are published across the existing documents plus two new ones (interaction; agent-to-agent communication); three that read as technical contracts go to the specifications instead.

**Why**: The April requirement's target had lapsed without an instrument or owner; the principal's newer requirements existed only privately.

### 2026-09-26 · The openness goal is judged at the next release

**Decision**: The openness goal is judged at the first release after 26 September 2026.

**Why**: The principal chose the tighter of the offered windows over the recommended one. Amended the same day: the deadline is split (see below).

### 2026-09-26 · One log page, starting today, with a back-fill

**Decision**: The decision log is a single page in the core repository, starting 26 September 2026, plus a back-fill of earlier decisions still in force that fall in the publishable classes.

**Why**: Chosen over the same page without a back-fill, one page per decision in a folder, and a section in each release note.

### 2026-09-26 · Two weeks' grace before the requirements check fails

**Decision**: The release check fails when a requirement ruled more than two weeks before the release still has no public counterpart; newer ones only warn.

**Why**: Chosen over failing on any gap however new, failing only when a requirement is not even prepared for publication, and failing only on regression.

### 2026-09-26 · Openness measured by specification coverage

**Decision**: The third openness measure checks that every public specification area traces back to at least one public requirement, replacing a comparison of file counts.

**Why**: File counts compare unlike things: publishing requirements could never satisfy the old measure.

### 2026-09-26 · Antigravity CLI replaces Gemini CLI in the target set

**Decision**: The set of command-line agents the framework aims to support, for roughly the next four months, is Claude Code, Codex CLI, Antigravity CLI and OpenCode; Antigravity CLI replaces Gemini CLI there. It is not yet formally supported — its current standing is experimental.

**Why**: The vendor stopped serving Gemini CLI to individual subscription tiers on 18 June 2026 and named Antigravity CLI as its successor.

### 2026-09-26 · Skills live in one place, linked where other tools look

**Decision**: Skills stay in one folder; each gets a link in the folder other command-line agents read, and a check makes a missing link fail loudly.

**Why**: Chosen over measuring first, a pointer file, or moving the skills' home: one source stays authoritative and every supported tool can still find the skills.

### 2026-09-26 · What the third command-line engine is for

**Decision**: Over the next four months the new engine is used as a third engine for cross-checking and research, on public or low-sensitivity work only, not for unattended work.

**Why**: Whether its consumer tier may use prompts for training has not been ruled on, so its use stays on public or low-sensitivity work until it is.

### 2026-09-26 · Typed text counts as the principal only with a checkable mark

**Decision**: Text one agent types into another agent's live session counts as the principal's instruction only when it carries a mark the receiver can check. Unmarked text is a peer request and can never give a go-ahead.

**Why**: A go-ahead typed by the principal is accepted without ceremony, so unmarked text from another agent could otherwise speak in the principal's name.

### 2026-09-26 · Agents read their own screen as styled text

**Decision**: An agent checks its own rendered replies by reading the terminal's screen as text with each character's colour, scrollback included, read-only.

**Why**: Chosen over pixel capture and combined approaches. The same setting could let scripts type into any session, so it is used read-only.

### 2026-09-26 · An agent's check on the principal's behalf stays the agent's

**Decision**: A check an agent performs at the principal's request is recorded as the agent's check, not the principal's; it does not count as independent principal review.

**Why**: Otherwise a review meant to be independent of the agent could be quietly performed by the agent itself.

### 2026-09-26 · The managing agent can check its own rendered replies

**Decision**: This framework's managing agent must be able to capture and check how its own replies render, without needing the principal's screenshot (ruled for one agent).

**Why**: A reply once showed a term as defined while the same sentence said it was undefined; only the principal's screenshot caught it.

### 2026-09-26 · Experiment: reading a peer agent's session, read-only

**Decision**: As an experiment, one agent may read another agent's terminal session, read-only; no window text is stored and input boxes are excluded.

**Why**: The earlier rule allowed reading only an agent's own window; the principal authorized this as an experiment.

### 2026-09-26 · Acting in another session stays off until the mark exists

**Decision**: Agents may not type into another agent's session until the checkable mark from the earlier decision has been designed.

**Why**: Without the mark, typed text could not be told apart from the principal's own instruction.

### 2026-09-26 · A highlighted term on a public page has a public definition

**Decision**: On a public page, every highlighted term has a definition an outsider can read, in the public vocabulary specification or the published vocabulary.

**Why**: A highlight promises one agreed definition; on a public page that promise must hold for readers without private access.

### 2026-09-26 · Publish a term's definition before the page that needs it

**Decision**: A term a public page needs that is defined only privately is published to the public vocabulary before the page ships.

**Why**: Shipping the page first would leave outsiders a highlighted word with nothing behind it.

### 2026-09-26 · Public term readability joins the openness goal

**Decision**: Making public terms readable is measured as part of the openness goal rather than as a separate goal.

**Why**: It is one aspect of an outsider being able to rebuild the framework from its public side.

### 2026-09-26 · A highlighted term is a trust sign

**Decision**: A highlighted term tells the reader the word has one agreed definition that can be relied on.

**Why**: The alternatives — a usage counter or a jump-to-definition link — either measure churn or cannot work in a terminal.

### 2026-09-26 · Highlighted terms use underscores for spaces

**Decision**: A highlighted term is written as its approved label with spaces turned into underscores; single words are allowed.

**Why**: That form already matched 428 of the 628 highlighted mentions in the sample the ruling was based on, and none used the spaced form.

### 2026-09-26 · A name shared by the two vocabularies is one definition when they agree

**Decision**: A name present in both the vocabulary specification and the published vocabulary counts as one definition when both entries mean the same thing; only a shared name with different meanings needs a disambiguator.

**Why**: Only a shared name whose meanings actually differ can mislead. About 28 names are shared; each is checked once for same meaning.

### 2026-09-26 · Letter case matters when resolving a highlighted term

**Decision**: Letter case matters when a highlighted term is resolved against the vocabulary; the plain-prose suggestion tool keeps ignoring case.

**Why**: Some terms differ only by case and mean different things; the suggestion tool is a helper, not the resolver.

### 2026-09-26 · Low ambiguity first, compactness second

**Decision**: When the highlighting rule can be read more than one way, the reading with less ambiguity wins; compactness comes second.

**Why**: Stated by the principal as the design intent, to settle ties.

### 2026-09-26 · One definition for an agent instance

**Decision**: The vocabulary specification's two definitions of an agent instance are merged into one, placed under the definition of an agent.

**Why**: Two definitions of one term contradicted the rule that a highlight means exactly one thing.

### 2026-09-26 · Avoid names whose meaning differs across vocabularies

**Decision**: When a name means different things in different vocabularies, use a more specific name or plain words; only if neither works, add a disambiguator right after the highlight.

**Why**: Chosen over always adding a disambiguator after or inside the highlight.

### 2026-09-26 · Preferred names and unambiguous aliases may be highlighted

**Decision**: A term may be highlighted by its preferred name, or by an alias that points to exactly one entry.

**Why**: Aliases improve readability; an alias pointing to one entry keeps the one-definition promise.

### 2026-09-26 · A term-table row counts as a vocabulary entry

**Decision**: A row in the vocabulary specification's term tables counts as an entry of that vocabulary; table and formal entries must agree.

**Why**: Otherwise the specification broke its own highlighting rule in about a hundred places.

### 2026-09-26 · The bare word 'goal' is not highlighted

**Decision**: The word 'goal' means different things in the vocabulary specification and the published vocabulary (a committed, lasting outcome versus any desired future state), so it is not highlighted bare.

**Why**: An independent reviewer found the two meanings differ; highlighting it would promise one definition where there are two.

### 2026-09-26 · The last-resort marker names the sense, not the list

**Decision**: When a disambiguator is unavoidable, it names the sense — for example 'Goal (committed outcome)' — rather than which vocabulary it came from.

**Why**: Chosen over naming the vocabulary, and over having no fallback.

### 2026-09-26 · Plurals keep their ending outside the highlight

**Decision**: A plural is written as the highlighted singular with the plural ending outside the highlight.

**Why**: Chosen over writing plurals plain or failing them.

### 2026-09-26 · A wanted but undefined term is written in italics

**Decision**: A term that is wanted but has no definition yet is written in italics in its display form: highlighted means defined, italic means wanted but not yet defined.

**Why**: It is the terminal's stand-in for a wiki's red link: highlighted means defined, italic means wanted.

### 2026-09-26 · The published plural form stays despite how GitHub draws it

**Decision**: The published plural form (ending outside the highlight) is kept even though GitHub draws the two parts slightly apart.

**Why**: Chosen over rephrasing or boxing plurals; the published text stands.

### 2026-09-26 · Openness is an accountability record

**Decision**: The framework's openness exists mainly as an accountability record: anyone, including the principal and future agents, can check why the framework is the way it is. Growing an outside audience is not a target yet.

**Why**: Chosen over community-first, adopter-first and citation-first purposes. The public side had no outside contributions or reports; the record is what the framework can keep true.

### 2026-09-26 · Lasting decisions enter the requirements list when recorded

**Decision**: When a decision with lasting force is recorded, it also gets an entry in the principal's requirements list at that moment, so the release check sees every lasting decision.

**Why**: The list held 25 requirements, while about 170 decisions sat in policy-type records (a lower-bound count by file name), so a check watching only the list could not see the lasting decisions among them.

### 2026-09-26 · The openness goal's deadline is split

**Decision**: The decision log and requirements measures are judged at the next release; specification coverage and public term readability at the release after.

**Why**: The single deadline had been set before coverage was measured (7 of 46 areas) and before the term-readability measure was added.

### 2026-09-26 · The openness position is stated publicly

**Decision**: A public requirement states plainly what kind of open the framework is: the code is Apache licensed, deliberation is private first, and the reasons are published in the decision log.

**Why**: Measured against the standards, the framework is open by license but not by development process, and nothing public said so; an unqualified 'open source' claim reads as open-washing.
