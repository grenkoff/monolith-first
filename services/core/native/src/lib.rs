//! Ranks names by their resemblance to a query, as a Python extension module of core.

pub mod domain;
#[cfg(feature = "python")]
mod python;
