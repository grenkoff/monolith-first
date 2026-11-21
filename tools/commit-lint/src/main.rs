//! Command line entry of commit-lint: messages separated by NUL on the standard input.

use std::io::{Read, Write};
use std::process::ExitCode;

use commit_lint::message::{Checked, Message};

/// Checks every message read from the standard input and reports each problem.
fn main() -> ExitCode {
    let mut input = String::new();
    if std::io::stdin().read_to_string(&mut input).is_err() {
        return ExitCode::from(2);
    }
    let mut out = std::io::stdout().lock();
    let mut total = 0_usize;
    for text in input.split('\0').filter(|text| !text.trim().is_empty()) {
        let header = text.lines().next().unwrap_or_default();
        for problem in Message::new(text).problems() {
            if writeln!(out, "{header}\n  {problem}").is_err() {
                return ExitCode::FAILURE;
            }
            total += 1;
        }
    }
    if total == 0 {
        ExitCode::SUCCESS
    } else {
        let _ = writeln!(out, "commit-lint: {total} problem(s) in commit messages");
        ExitCode::FAILURE
    }
}
