# Reading the AGET concept vocabulary

This vocabulary contains 36 records: the 34 previously published records, plus the existing Agent and Cognitive Entity. Preferred names and permanent identities of existing concepts are unchanged. Definitions distinguish kinds from associations; reciprocal links are included within this published subset.

Within this repository, a reference of the form aget:concept/X resolves by exact equality with an entry’s uri field in ontology/ONTOLOGY_personal_ai_systems_v1.0.yaml. This is a local record lookup; no HTTP or w3id expansion is implied. It is not the separate vocabulary published under the w3id.org/aget/vocab identifier scheme. A compact reference needs its declared expansion and the intended vocabulary version; syntax alone does not establish a normative binding.

## Supporting meanings

These ordinary senses explain the genera used by the definitions. They are an explanatory glossary, not additional ontology records, certified vocabulary highlights or new compliance obligations.

**axis**: A distinguishable aspect used to describe an entity.

**coordination mechanism**: An arrangement through which agents align or combine their activities.

**ordinal grading**: An assignment of a level from an ordered scale, where the order expresses relative degree without requiring equal intervals.

**anti-pattern**: A recurring arrangement or practice that produces undesirable consequences for its intended purpose.

**failure mode**: A way in which a practice or system fails to achieve an intended result.

**discipline**: A practice directed by rules or standards.

**URI reference**: A URI or a relative reference that identifies a resource in a stated context.

**linkage**: An explicit relationship connecting specified entities.

**relationship field**: A field in a structured record that stores references expressing relationships to other records or resources.

**role**: A context-dependent set of responsibilities that an entity may bear.

**machine-readable label**: A textual value stored in a form that software can read and interpret according to its stated convention.

**reliance**: Dependence on a capability, tool, source or body of evidence in carrying out an activity, including one’s own prior work.

**governed state**: A condition or position in a lifecycle whose permitted transitions are subject to governance rules.

**governance strategy**: A planned approach to allocating decision authority, setting rules and assessing compliance.

**enforcement posture**: A chosen way of responding to compliance with, or deviation from, a rule.

**operation**: An action performed on or by an entity.

**promise**: An undertaking by an agent to perform future action.

## Cognitive capacity and directed action

A Cognitive_Entity is an Entity capable of performing cognitive processes, such as perception, memory, reasoning, learning, or decision-making.

Capacity for cognitive processing is required; consciousness is not asserted. An individual or collective qualifies only when it has that capacity; legal or organizational status alone is insufficient. Cognition here means interpreting and using information to support the entity’s own understanding or behaviour. Mere storage or fixed-rule switching by itself does not establish the capacity, and a single memory operation is not a membership test. Cognitive capacity alone does not grant a principal role or authorization. Agent denotes the existing perceiving-and-goal-directed-acting genus. Directed action and cognitive capacity are distinct criteria; neither alone establishes the other in this model. Cognitive Entity and Agent have a reciprocal related association. Principal has Cognitive Entity as its one direct parent and retains its Agent association. This is an explicitly stipulative AGET genus, not a claim of scientific consensus.


Agent (aget:concept/Agent) retains its existing definition: An entity that perceives some part of its environment and acts on it in pursuit of goals — its own, or those of another party on whose behalf it acts. The genus is neutral about substrate: people, organizations, software and collectives can all be agents. What sets an agent apart from other entities is directed action, not what it is made of.


Cognitive Entity (aget:concept/CognitiveEntity) and Agent are associated, with neither asserted as a subtype of the other. Principal is a direct child of Cognitive Entity; its existing Agent association is retained.

## Definition sentence example

A Principal_(Agency) is a Cognitive_Entity that AI_Agents serve and that retains ultimate authority over their system.

Underscore-joined phrases are display notation, not record identifiers. AI agents are artificial cases of the existing Agent genus, not an additional published record. The named-subject definition-sentence correction covers the 34 reviewed records and new Cognitive Entity; the existing Agent definition remains unchanged. This is a display example, not a preferred-name or identifier change. Principal remains aget:concept/Principal. A wiki writer uses its own naming, linking and source standards.

## Compatibility and interpretation

Five former aliases are removed: Appropriate Reliance from Trust Calibration; Top Concept, Conceptual Root and Universal from Thing; and SHALL-Binding Discipline from Normative Concept Binding. Appropriate Reliance denotes the existing reliance concept. Top Concept and Conceptual Root describe the intended role of Thing rather than its members. Consumers should review uses of these aliases; existing preferred names and URIs continue to identify the same records.

Entity Lifecycle State is ratified as active. Its required shared core permits specialized lifecycle vocabularies; activation does not certify that existing Plan, Goal or Initiative enums conform. The former provisional state is treated as proposed-for-ratification for this one transition only.

Examples marked source-era are historical illustrations, not claims about current deployment or compliance. Bibliographic references and internal source annotations are contextual; membership conditions are stated in the definition and required scope. Thing has an intended root role, without claiming every existing concept reaches it.

## Reading source-era shorthand

In the release contract’s historical note, R denotes a particular release, {S} its specified skills and {O} its optional or adoptable skills. The four strict routing exceptions concern mandatory skill invocation; they do not create a runtime guarantee for the whole release contract. In Agent’s context, an instance denotes an artificial agent and a clone denotes an artifact that realizes it; the actor and its realization remain distinct.

The existing metadata version is 1.0.0. Identify the corrected publication by its commit and exact file digest; the Concept Pinning example’s v8.10.0 refers to the historical canonical vocabulary, not this subset file.
