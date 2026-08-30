// Development domain per feature: which disciplines have to build it.
//
// This is curated, not derived. It began as a derivation from the requirement
// wording, but the reviewer corrected ten of the eighty-two, and a rule that is
// wrong one time in eight is worse than a list — a list at least shows you what
// it thinks. Every feature therefore has an explicit entry here, and the build
// fails if a feature has none, so a new feature cannot ship untagged.
//
//   iOS, Android — application work, per platform
//   Backend      — the feature places an obligation on the server
//   Algo         — algorithm or image-processing work
//   Content      — copy that has to be written and approved
//   Process      — a development or verification process obligation
//
// Order is normalised on output, so the order written here does not matter.

const ORDER = ["iOS", "Android", "Backend", "Algo", "Content", "Process"];

const DOMAIN = {
  "F01.1": ["iOS", "Android"],
  "F01.2": ["iOS", "Android"],
  "F01.3": ["iOS", "Android"],
  "F01.4": ["iOS", "Android"],
  "F01.5": ["iOS", "Android"],
  "F01.6": ["iOS", "Android"],
  "F01.7": ["iOS", "Android"],
  "F01.8": ["iOS", "Android", "Algo"],   // updated at review
  "F01.9": ["iOS", "Android", "Backend"],
  "F02.1": ["iOS", "Android", "Backend"],   // updated at review
  "F02.2": ["iOS", "Android", "Backend"],
  "F02.3": ["iOS", "Android", "Backend"],
  "F02.4": ["iOS", "Android", "Backend"],
  "F02.5": ["iOS", "Android", "Backend"],
  "F02.6": ["iOS", "Android"],
  "F02.8": ["iOS", "Android"],
  "F02.7": ["iOS", "Android"],
  "F03.1": ["iOS", "Android", "Backend"],
  "F03.2": ["iOS", "Android", "Backend"],   // updated at review
  "F04.1": ["iOS", "Android"],
  "F04.2": ["iOS", "Android"],
  "F04.3": ["iOS", "Android"],
  "F04.4": ["iOS", "Android"],
  "F04.7": ["iOS", "Android"],
  "F04.6": ["iOS", "Android"],
  "F04.8": ["iOS", "Android"],
  "F04.5": ["iOS", "Android"],
  "F05.1": ["iOS", "Android"],
  "F05.2": ["iOS", "Android"],
  "F05.3": ["iOS", "Android"],
  "F05.4": ["iOS", "Android"],
  "F05.5": ["iOS", "Android"],
  "F05.6": ["iOS", "Android"],
  "F06.1": ["iOS", "Android", "Algo"],   // updated at review
  "F06.2": ["iOS", "Android", "Algo"],   // updated at review
  "F06.3": ["iOS", "Android", "Algo"],   // updated at review
  "F06.6": ["Algo", "iOS", "Android"],
  "F06.4": ["iOS", "Android"],
  "F06.5": ["Algo"],
  "F07.1": ["Content"],
  "F07.2": ["Content"],
  "F07.3": ["Content"],
  "F07.4": ["Content"],
  "F08.1": ["Backend", "Algo"],
  "F08.2": ["Backend"],
  "F08.3": ["Algo"],
  "F08.4": ["iOS", "Android", "Backend", "Algo"],   // updated at review
  "F09.1": ["iOS", "Android", "Backend"],
  "F09.2": ["iOS", "Android"],
  "F09.4": ["iOS", "Android", "Backend"],
  "F10.1": ["iOS", "Android", "Backend"],
  "F10.2": ["iOS", "Android", "Backend"],
  "F10.3": ["iOS", "Android", "Backend"],
  "F10.4": ["iOS", "Android"],
  "F10.5": ["iOS", "Android"],
  "F10.6": ["iOS", "Android"],
  "F11.1": ["Backend"],
  "F11.2": ["Backend"],
  "F11.3": ["Backend", "iOS", "Android"],
  "F11.4": ["iOS", "Android"],
  "F11.5": ["iOS", "Android"],
  "F11.6": ["iOS", "Android"],
  "F11.7": ["iOS", "Android"],
  "F12.1": ["iOS", "Android"],
  "F12.2": ["iOS", "Android", "Backend"],
  "F12.3": ["iOS", "Android"],
  "F12.4": ["iOS", "Android", "Backend"],   // updated at review
  "F13.1": ["iOS", "Android"],
  "F13.2": ["iOS", "Android"],
  "F13.3": ["iOS", "Android"],
  "F13.4": ["iOS", "Android", "Backend"],   // updated at review
  "F13.5": ["iOS", "Android", "Backend"],
  "F14.1": ["iOS", "Android"],
  "F14.2": ["iOS", "Android"],
  "F14.3": ["iOS", "Android"],
  "F14.4": ["iOS", "Android", "Backend"],   // updated at review
  "F15.1": ["Process"],
  "F15.2": ["Process"],
  "F15.3": ["Process"],
  "F15.4": ["Process"],
  "F15.5": ["Process"],
  "F15.6": ["Process"],
};

module.exports = function domainsFor(featureId) {
  const d = DOMAIN[featureId];
  if (!d) return null;                       // the caller reports this as a failure
  return ORDER.filter(x => d.includes(x));
};

module.exports.DOMAIN = DOMAIN;
module.exports.ORDER = ORDER;
