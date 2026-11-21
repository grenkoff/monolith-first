//! Python extension module `ranking`: the resemblance of names for core.

use pyo3::prelude::*;

use crate::domain::phrase::{Phrase, Resembled};

/// Adapter: a query whose resemblance to names Python asks for.
#[pyclass(frozen)]
struct Similarity {
    /// Query typed by a visitor.
    phrase: Phrase,
}

#[pymethods]
impl Similarity {
    /// Creates the similarity of a query.
    #[new]
    fn new(query: String) -> Self {
        Self {
            phrase: Phrase::new(query),
        }
    }

    /// Returns the resemblance of each name to the query, in the order given.
    fn __call__(&self, names: Vec<String>) -> Vec<f64> {
        names
            .into_iter()
            .map(|name| self.phrase.resemblance(&name))
            .collect()
    }
}

/// Python module `ranking` that exports `Similarity`.
#[pymodule]
mod ranking {
    #[pymodule_export]
    use super::Similarity;
}
