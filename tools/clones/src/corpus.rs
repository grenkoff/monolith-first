//! Documents of code and the blocks they repeat.

use std::collections::{BTreeMap, HashMap};
use std::fmt;

use crate::source::{Line, Numbered};

/// Lines of one file and the path they come from.
pub struct Document {
    /// Path of the file.
    path: String,
    /// Meaningful lines of the file.
    lines: Vec<Line>,
}

impl Document {
    /// Creates a document.
    #[must_use]
    pub fn new(path: impl Into<String>, lines: Vec<Line>) -> Self {
        Self {
            path: path.into(),
            lines,
        }
    }
}

/// Place of a block: a file and its first and last line.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Span {
    /// Path of the file.
    path: String,
    /// First line of the block.
    first: usize,
    /// Last line of the block.
    last: usize,
}

impl Span {
    /// Creates a span.
    #[must_use]
    pub fn new(path: impl Into<String>, first: usize, last: usize) -> Self {
        Self {
            path: path.into(),
            first,
            last,
        }
    }
}

impl fmt::Display for Span {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}:{}-{}", self.path, self.first, self.last)
    }
}

/// Block of code found in two places.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Duplicate {
    /// Where the block appears first.
    original: Span,
    /// Where it appears again.
    copy: Span,
}

impl Duplicate {
    /// Creates a duplicate.
    #[must_use]
    pub const fn new(original: Span, copy: Span) -> Self {
        Self { original, copy }
    }
}

impl fmt::Display for Duplicate {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{} repeats {}", self.copy, self.original)
    }
}

/// Code that may repeat itself.
pub trait Repeating {
    /// Returns every block repeated in the code.
    fn duplicates(&self) -> Vec<Duplicate>;
}

/// Documents searched for blocks of at least `size` meaningful lines.
pub struct Corpus {
    /// Documents to search.
    documents: Vec<Document>,
    /// Fewest meaningful lines a reported block has.
    size: usize,
}

impl Corpus {
    /// Creates a corpus.
    #[must_use]
    pub const fn new(documents: Vec<Document>, size: usize) -> Self {
        Self { documents, size }
    }
}

/// Window of `size` lines: the document and the index of its first line.
type Window = (usize, usize);

/// Starts of matching windows by the two documents and the distance between them.
type Matches = BTreeMap<(usize, usize, usize), Vec<usize>>;

impl Corpus {
    /// Returns the matching windows, grouped by the pair of places they belong to.
    fn matches(&self) -> Matches {
        let mut first: HashMap<Vec<&str>, Window> = HashMap::new();
        let mut matches = Matches::new();
        for (document, lines) in self.documents.iter().enumerate() {
            for (start, window) in lines.lines.windows(self.size).enumerate() {
                let key: Vec<&str> = window.iter().map(Numbered::text).collect();
                match first.get(&key) {
                    Some(&(original, from))
                        if original != document || from + self.size <= start =>
                    {
                        matches
                            .entry((original, document, start.wrapping_sub(from)))
                            .or_default()
                            .push(from);
                    }
                    Some(_) => {}
                    None => {
                        first.insert(key, (document, start));
                    }
                }
            }
        }
        matches
    }

    /// Returns the span of the block of windows from `start` to `end` in a document.
    fn span(&self, document: usize, start: usize, end: usize) -> Span {
        let found = &self.documents[document];
        Span::new(
            &found.path,
            found.lines[start].number(),
            found.lines[end + self.size - 1].number(),
        )
    }
}

impl Repeating for Corpus {
    fn duplicates(&self) -> Vec<Duplicate> {
        let mut duplicates = Vec::new();
        for ((original, copy, distance), starts) in self.matches() {
            let mut runs: Vec<(usize, usize)> = Vec::new();
            for start in starts {
                match runs.last_mut() {
                    Some(run) if run.1 + 1 == start => run.1 = start,
                    _ => runs.push((start, start)),
                }
            }
            duplicates.extend(runs.into_iter().map(|(start, end)| {
                Duplicate::new(
                    self.span(original, start, end),
                    self.span(
                        copy,
                        start.wrapping_add(distance),
                        end.wrapping_add(distance),
                    ),
                )
            }));
        }
        duplicates
    }
}

#[cfg(test)]
mod tests {
    use super::{Corpus, Document, Repeating};
    use crate::source::{Meaningful, Source};

    fn document(path: &str, text: &str) -> Document {
        Document::new(path, Source::new(text).lines())
    }

    fn found(documents: Vec<Document>) -> Vec<String> {
        Corpus::new(documents, 3)
            .duplicates()
            .iter()
            .map(ToString::to_string)
            .collect()
    }

    const BLOCK: &str = "alpha = 1\nbeta = 2\ngamma = 3\ndelta = 4\n";

    #[test]
    fn finds_a_block_repeated_in_two_files() {
        let first = document("a.py", &format!("start = 0\n{BLOCK}"));
        let second = document("b.py", BLOCK);
        assert_eq!(found(vec![first, second]), ["b.py:1-4 repeats a.py:2-5"]);
    }

    #[test]
    fn ignores_a_block_shorter_than_the_size() {
        let first = document("a.py", "alpha = 1\nbeta = 2\nend = 0\n");
        let second = document("b.py", "alpha = 1\nbeta = 2\nstop = 0\n");
        assert_eq!(found(vec![first, second]), Vec::<String>::new());
    }

    #[test]
    fn finds_a_block_repeated_in_one_file() {
        let text = format!("{BLOCK}middle = 0\n{BLOCK}");
        assert_eq!(
            found(vec![document("a.py", &text)]),
            ["a.py:6-9 repeats a.py:1-4"]
        );
    }

    #[test]
    fn ignores_a_line_repeated_in_a_row() {
        let text = "same = 1\n".repeat(5);
        assert_eq!(found(vec![document("a.py", &text)]), Vec::<String>::new());
    }

    #[test]
    fn counts_lines_of_the_file_across_blank_lines() {
        let first = document("a.rs", "alpha = 1\n\nbeta = 2\n}\ngamma = 3\n");
        let second = document("b.rs", "alpha = 1\nbeta = 2\ngamma = 3\n");
        assert_eq!(found(vec![first, second]), ["b.rs:1-3 repeats a.rs:1-5"]);
    }

    #[test]
    fn reports_each_further_copy_against_the_first() {
        let documents = vec![
            document("a.py", BLOCK),
            document("b.py", BLOCK),
            document("c.py", BLOCK),
        ];
        assert_eq!(
            found(documents),
            ["b.py:1-4 repeats a.py:1-4", "c.py:1-4 repeats a.py:1-4"]
        );
    }

    #[test]
    fn reports_two_separate_blocks_of_the_same_files_apart() {
        let other = "one = 1\ntwo = 2\nthree = 3\n";
        let first = document("a.py", &format!("{BLOCK}start = 0\n{other}"));
        let second = document("b.py", &format!("{BLOCK}finish = 0\n{other}"));
        assert_eq!(
            found(vec![first, second]),
            ["b.py:1-4 repeats a.py:1-4", "b.py:6-8 repeats a.py:6-8"]
        );
    }
}
