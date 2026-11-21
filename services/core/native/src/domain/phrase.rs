//! A phrase and how much other names resemble it.

/// Text that other texts may resemble.
pub trait Resembled {
    /// Returns from 0 for nothing in common to 1 for the same words.
    fn resemblance(&self, other: &str) -> f64;
}

/// Phrase typed by a person, such as a search query.
pub struct Phrase {
    /// Text of the phrase.
    text: String,
}

impl Phrase {
    /// Creates a phrase.
    #[must_use]
    pub fn new(text: impl Into<String>) -> Self {
        Self { text: text.into() }
    }
}

impl Resembled for Phrase {
    fn resemblance(&self, other: &str) -> f64 {
        if self.text.is_empty() && other.is_empty() {
            1.0
        } else {
            0.5
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{Phrase, Resembled};

    fn resemblance(query: &str, name: &str) -> f64 {
        Phrase::new(query).resemblance(name)
    }

    #[test]
    fn equal_names_resemble_fully() {
        assert!((resemblance("green tea", "green tea") - 1.0).abs() < f64::EPSILON);
    }

    #[test]
    fn names_with_nothing_in_common_do_not_resemble() {
        assert!(resemblance("abc", "xyz").abs() < f64::EPSILON);
    }

    #[test]
    fn case_does_not_matter() {
        assert!((resemblance("Tea", "tea") - 1.0).abs() < f64::EPSILON);
    }

    #[test]
    fn a_word_is_matched_against_the_closest_word_of_the_name() {
        assert!((resemblance("tea", "Green tea") - 1.0).abs() < f64::EPSILON);
    }

    #[test]
    fn a_typo_keeps_a_high_resemblance() {
        let score = resemblance("tee", "Green tea");
        assert!((score - 2.0 / 3.0).abs() < 1e-9, "{score}");
    }

    #[test]
    fn a_typo_scores_above_another_word() {
        assert!(resemblance("tee", "Green tea") > resemblance("tee", "Black coffee"));
    }

    #[test]
    fn every_word_of_the_query_counts() {
        let score = resemblance("green coffee", "Green tea");
        assert!((score - 7.0 / 12.0).abs() < 1e-9, "{score}");
    }

    #[test]
    fn an_empty_query_resembles_nothing() {
        assert!(resemblance("", "Green tea").abs() < f64::EPSILON);
    }

    #[test]
    fn a_query_resembles_nothing_in_an_empty_name() {
        assert!(resemblance("tea", "").abs() < f64::EPSILON);
    }
}
