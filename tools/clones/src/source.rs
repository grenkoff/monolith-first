//! One file of code reduced to the lines that carry meaning.

/// Line of code with its number in the file.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Line {
    /// Number of the line in the file, from one.
    number: usize,
    /// Text of the line without indentation.
    text: String,
}

impl Line {
    /// Creates a line.
    #[must_use]
    pub fn new(number: usize, text: impl Into<String>) -> Self {
        Self {
            number,
            text: text.into(),
        }
    }
}

/// Something that has a number in a file and a text.
pub trait Numbered {
    /// Returns the number of the line in its file.
    fn number(&self) -> usize;
    /// Returns the text of the line.
    fn text(&self) -> &str;
}

impl Numbered for Line {
    fn number(&self) -> usize {
        self.number
    }

    fn text(&self) -> &str {
        &self.text
    }
}

/// Code whose meaningful lines can be compared.
pub trait Meaningful {
    /// Returns the lines that carry meaning: no blank lines, no lone brackets.
    fn lines(&self) -> Vec<Line>;
}

/// Text of one file.
pub struct Source {
    /// Whole text of the file.
    text: String,
}

impl Source {
    /// Creates a source from the text of a file.
    #[must_use]
    pub fn new(text: impl Into<String>) -> Self {
        Self { text: text.into() }
    }
}

impl Meaningful for Source {
    fn lines(&self) -> Vec<Line> {
        self.text
            .lines()
            .enumerate()
            .map(|(index, text)| Line::new(index + 1, text.trim()))
            .filter(|line| line.text.chars().any(char::is_alphanumeric))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::{Line, Meaningful, Numbered, Source};

    #[test]
    fn numbers_lines_from_one_without_indentation() {
        assert_eq!(
            Source::new("first = 1\n    second = 2\n").lines(),
            [Line::new(1, "first = 1"), Line::new(2, "second = 2")]
        );
    }

    #[test]
    fn skips_blank_lines_and_lone_brackets() {
        let lines = Source::new("call(\n\n    value,\n)\n}\n  ]);\n").lines();
        let numbers: Vec<usize> = lines.iter().map(Numbered::number).collect();
        assert_eq!(numbers, [1, 3]);
    }

    #[test]
    fn keeps_the_text_of_a_line() {
        assert_eq!(Line::new(4, "value").text(), "value");
    }
}
