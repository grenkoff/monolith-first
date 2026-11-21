//! Command line entry of clones: reports blocks repeated under the given directories.

use std::io::Write;
use std::process::ExitCode;

use clones::corpus::{Corpus, Repeating};
use clones::tree::{Collected, Tree};

/// Fewest meaningful lines a reported block has.
const SIZE: usize = 8;

/// Searches the given directories and reports every repeated block.
fn main() -> ExitCode {
    let mut out = std::io::stdout().lock();
    let mut documents = Vec::new();
    for root in std::env::args().skip(1) {
        match Tree::new(root).documents() {
            Ok(found) => documents.extend(found),
            Err(error) => {
                let _ = writeln!(out, "clones: {error}");
                return ExitCode::from(2);
            }
        }
    }
    let duplicates = Corpus::new(documents, SIZE).duplicates();
    for duplicate in &duplicates {
        if writeln!(out, "{duplicate}").is_err() {
            return ExitCode::FAILURE;
        }
    }
    if duplicates.is_empty() {
        ExitCode::SUCCESS
    } else {
        let _ = writeln!(
            out,
            "clones: {} repeated block(s) of {SIZE} or more lines, extract them",
            duplicates.len()
        );
        ExitCode::FAILURE
    }
}
