// The one place document revisions are declared.
//
// Every builder interpolates from here. Nothing else in the generator may contain
// a literal revision string, and consistency-check.py fails the build if one does.
//
// This module exists because it was got wrong. A global find-and-replace of
// "Rev 1.9" -> "Rev 1.10" across build-epics.js bumped the footer correctly, missed
// the front-matter row (which reads "1.9 — Draft for review", with no "Rev" prefix),
// and corrupted the "Derived from" row, which cites the *functional requirements*
// revision and so should never have matched the epic map's own number at all.
// Rev 1.10 shipped saying three different things about itself.

module.exports = {
  // QACR-APP-FR-01 Functional Requirements
  FR: "1.25",
  // QACR-APP-EPIC-01 Epic and Feature Map, and the board generated beside it
  EPIC: "1.19",

  // Bump these, rebuild, run the checks. Do not edit a revision anywhere else.
  //
  // When FR changes, EPIC must be bumped too, not merely rebuilt. Both the epic map
  // and the board cite the FR revision in their prose, so leaving EPIC alone would put
  // two different documents into circulation under the same revision number.
  status: "Draft for review",
};
