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
        let query = Words::new(&self.text);
        let name = Words::new(other);
        let wanted = query.list();
        let offered = name.list();
        if wanted.is_empty() || offered.is_empty() {
            return 0.0;
        }
        let total: f64 = wanted
            .iter()
            .map(|word| {
                offered
                    .iter()
                    .map(|candidate| Word::new(word).resemblance(candidate))
                    .fold(0.0, f64::max)
            })
            .sum();
        total / f64::from(u32::try_from(wanted.len()).unwrap_or(u32::MAX))
    }
}

/// Words of a text, in lower case.
struct Words<'text> {
    /// Text to split.
    text: &'text str,
}

impl<'text> Words<'text> {
    /// Creates the words of a text.
    const fn new(text: &'text str) -> Self {
        Self { text }
    }

    /// Returns the words in lower case.
    fn list(&self) -> Vec<String> {
        self.text
            .split_whitespace()
            .map(str::to_lowercase)
            .collect()
    }
}

/// One word, compared letter by letter.
struct Word<'text> {
    /// Letters of the word.
    text: &'text str,
}

impl<'text> Word<'text> {
    /// Creates a word.
    const fn new(text: &'text str) -> Self {
        Self { text }
    }
}

impl Resembled for Word<'_> {
    fn resemblance(&self, other: &str) -> f64 {
        let mine: Vec<char> = self.text.chars().collect();
        let theirs: Vec<char> = other.chars().collect();
        let longest = mine.len().max(theirs.len());
        let mut row: Vec<usize> = (0..=theirs.len()).collect();
        for (index, letter) in mine.iter().enumerate() {
            let mut diagonal = row[0];
            row[0] = index + 1;
            for (column, candidate) in theirs.iter().enumerate() {
                let above = row[column + 1];
                row[column + 1] = (above + 1)
                    .min(row[column] + 1)
                    .min(diagonal + usize::from(letter != candidate));
                diagonal = above;
            }
        }
        let distance = u32::try_from(row[theirs.len()]).unwrap_or(u32::MAX);
        let length = u32::try_from(longest).unwrap_or(u32::MAX);
        1.0 - f64::from(distance) / f64::from(length)
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
