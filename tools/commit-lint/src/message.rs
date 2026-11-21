//! A commit message and the rules it breaks.

/// Types of Conventional Commits the project allows.
const TYPES: &[&str] = &[
    "feat", "fix", "refactor", "perf", "test", "docs", "build", "ci", "chore", "style", "revert",
];

/// Longest header allowed, in characters.
const LIMIT: usize = 100;

/// Text that can be checked against the commit rules.
pub trait Checked {
    /// Returns what breaks the rules, empty when nothing does.
    fn problems(&self) -> Vec<String>;
}

/// Commit message as git stores it.
pub struct Message {
    /// Whole text of the message.
    text: String,
}

impl Message {
    /// Creates a message from its text.
    #[must_use]
    pub fn new(text: impl Into<String>) -> Self {
        Self { text: text.into() }
    }
}

impl Checked for Message {
    fn problems(&self) -> Vec<String> {
        let mut lines = self.text.trim_end().lines();
        let mut problems = Header::new(lines.next().unwrap_or_default()).problems();
        if lines.any(|line| !line.trim().is_empty()) {
            problems.push(String::from(
                "a message is one line only: no body, no footer",
            ));
        }
        problems
    }
}

/// First line of a message: `<type>(<scope>)!: <description>`.
struct Header<'text> {
    /// Text of the line.
    text: &'text str,
}

impl<'text> Header<'text> {
    /// Creates a header from its line.
    const fn new(text: &'text str) -> Self {
        Self { text }
    }
}

impl Checked for Header<'_> {
    fn problems(&self) -> Vec<String> {
        let mut problems = Vec::new();
        let length = self.text.chars().count();
        if length > LIMIT {
            problems.push(format!(
                "the header has {length} characters, at most {LIMIT}"
            ));
        }
        match self.text.split_once(": ") {
            Some((prefix, description)) => {
                problems.extend(Prefix::new(prefix).problems());
                problems.extend(Description::new(description).problems());
            }
            None => problems.push(String::from(
                "the header is not `<type>(<scope>): <description>`",
            )),
        }
        problems
    }
}

/// Part of a header before the colon: type, optional scope, optional `!`.
struct Prefix<'text> {
    /// Text of the part.
    text: &'text str,
}

impl<'text> Prefix<'text> {
    /// Creates a prefix from its text.
    const fn new(text: &'text str) -> Self {
        Self { text }
    }
}

impl Checked for Prefix<'_> {
    fn problems(&self) -> Vec<String> {
        let plain = self.text.strip_suffix('!').unwrap_or(self.text);
        let (kind, scope) = match plain.split_once('(') {
            Some((kind, rest)) => (kind, rest.strip_suffix(')')),
            None => (plain, Some("scope")),
        };
        let mut problems = Vec::new();
        if !TYPES.contains(&kind) {
            problems.push(format!("type `{kind}` is not one of {}", TYPES.join(", ")));
        }
        match scope {
            Some(name) if !name.is_empty() && name == name.to_lowercase() => {}
            Some(name) => {
                problems.push(format!("scope `{name}` must be a non-empty lowercase name"));
            }
            None => problems.push(String::from("the scope has no closing `)`")),
        }
        problems
    }
}

/// Part of a header after the colon.
struct Description<'text> {
    /// Text of the part.
    text: &'text str,
}

impl<'text> Description<'text> {
    /// Creates a description from its text.
    const fn new(text: &'text str) -> Self {
        Self { text }
    }
}

impl Checked for Description<'_> {
    fn problems(&self) -> Vec<String> {
        let mut problems = Vec::new();
        if self.text.trim().is_empty() {
            problems.push(String::from("the description is empty"));
        }
        if self.text.starts_with(char::is_uppercase) {
            problems.push(String::from(
                "the description starts with a lowercase letter",
            ));
        }
        if self.text.ends_with('.') {
            problems.push(String::from("the description has no trailing period"));
        }
        problems
    }
}

#[cfg(test)]
mod tests {
    use super::{Checked, Message};

    fn problems(text: &str) -> Vec<String> {
        Message::new(text).problems()
    }

    #[test]
    fn accepts_a_conventional_header() {
        assert_eq!(problems("feat(core): add orders"), Vec::<String>::new());
    }

    #[test]
    fn accepts_a_header_without_scope() {
        assert_eq!(problems("docs: explain the outbox"), Vec::<String>::new());
    }

    #[test]
    fn accepts_a_breaking_change() {
        assert_eq!(
            problems("feat(proto)!: remove greet v1"),
            Vec::<String>::new()
        );
    }

    #[test]
    fn accepts_the_newline_git_adds() {
        assert_eq!(
            problems("fix(core): close the pool\n\n"),
            Vec::<String>::new()
        );
    }

    #[test]
    fn refuses_a_body() {
        let found = problems("fix(core): close the pool\n\nThe pool leaked.");
        assert_eq!(found.len(), 1);
        assert!(found[0].contains("one line"), "{found:?}");
    }

    #[test]
    fn refuses_a_body_right_under_the_header() {
        assert_eq!(
            problems("fix(core): close the pool\nThe pool leaked.").len(),
            1
        );
    }

    #[test]
    fn accepts_a_header_of_one_hundred_characters() {
        let header = format!("docs: {}", "a".repeat(94));
        assert_eq!(problems(&header), Vec::<String>::new());
    }

    #[test]
    fn refuses_a_header_longer_than_one_hundred_characters() {
        let header = format!("docs: {}", "a".repeat(95));
        let found = problems(&header);
        assert_eq!(found.len(), 1);
        assert!(found[0].contains("101"), "{found:?}");
    }

    #[test]
    fn refuses_a_header_without_type() {
        let found = problems("add orders");
        assert_eq!(found.len(), 1);
        assert!(found[0].contains("<type>"), "{found:?}");
    }

    #[test]
    fn refuses_an_unknown_type() {
        let found = problems("feature(core): add orders");
        assert_eq!(found.len(), 1);
        assert!(found[0].contains("`feature`"), "{found:?}");
    }

    #[test]
    fn refuses_an_upper_case_scope() {
        let found = problems("feat(Core): add orders");
        assert_eq!(found.len(), 1);
        assert!(found[0].contains("`Core`"), "{found:?}");
    }

    #[test]
    fn refuses_an_empty_scope() {
        assert_eq!(problems("feat(): add orders").len(), 1);
    }

    #[test]
    fn refuses_an_unclosed_scope() {
        assert_eq!(problems("feat(core: add orders").len(), 1);
    }

    #[test]
    fn refuses_a_capital_description() {
        let found = problems("feat(core): Add orders");
        assert_eq!(found.len(), 1);
        assert!(found[0].contains("lowercase"), "{found:?}");
    }

    #[test]
    fn refuses_a_trailing_period() {
        let found = problems("feat(core): add orders.");
        assert_eq!(found.len(), 1);
        assert!(found[0].contains("period"), "{found:?}");
    }

    #[test]
    fn refuses_an_empty_description() {
        assert_eq!(problems("feat(core):  ").len(), 1);
    }
}
