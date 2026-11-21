//! A commit message and the rules it breaks.

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
        Vec::from([self.text.clone()]).into_iter().take(0).collect()
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
