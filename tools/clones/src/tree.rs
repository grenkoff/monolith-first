//! Directory trees whose Python and Rust files are searched.

use std::fs;

use walkdir::WalkDir;

use crate::corpus::Document;
use crate::source::{Meaningful, Source};

/// Directories that hold no hand-written code.
const SKIPPED: &[&str] = &["target", ".git", ".venv", "node_modules", "migrations"];

/// Directory of generated gRPC code inside the monolith.
const GENERATED: &str = "server/contracts";

/// Extensions of the files that are searched.
const EXTENSIONS: &[&str] = &["py", "rs"];

/// Why files could not be collected.
#[derive(Debug, thiserror::Error)]
pub enum Failure {
    /// A file could not be read.
    #[error("cannot read {0}: {1}")]
    Read(String, std::io::Error),
    /// A directory could not be walked.
    #[error("cannot walk directories: {0}")]
    Walk(#[from] walkdir::Error),
}

/// Place that holds documents of code.
pub trait Collected {
    /// Returns the documents of every Python and Rust file in it.
    fn documents(&self) -> Result<Vec<Document>, Failure>;
}

/// Directory tree under one root.
pub struct Tree {
    /// Root directory of the tree.
    root: String,
}

impl Tree {
    /// Creates a tree under the given root.
    #[must_use]
    pub fn new(root: impl Into<String>) -> Self {
        Self { root: root.into() }
    }
}

impl Collected for Tree {
    fn documents(&self) -> Result<Vec<Document>, Failure> {
        let mut documents = Vec::new();
        let walk = WalkDir::new(&self.root)
            .sort_by_file_name()
            .into_iter()
            .filter_entry(|entry| {
                !SKIPPED.contains(&entry.file_name().to_string_lossy().as_ref())
                    && !entry.path().ends_with(GENERATED)
            });
        for entry in walk {
            let entry = entry?;
            let path = entry.path();
            let code = entry.file_type().is_file()
                && path
                    .extension()
                    .and_then(|extension| extension.to_str())
                    .is_some_and(|extension| EXTENSIONS.contains(&extension));
            if code {
                let name = path.display().to_string();
                let text =
                    fs::read_to_string(path).map_err(|error| Failure::Read(name.clone(), error))?;
                documents.push(Document::new(name, Source::new(text).lines()));
            }
        }
        Ok(documents)
    }
}

#[cfg(test)]
mod tests {
    use std::fs;
    use std::path::PathBuf;

    use super::{Collected, Tree};
    use crate::corpus::{Corpus, Repeating};

    fn tree(name: &str, files: &[(&str, &str)]) -> PathBuf {
        let root = std::env::temp_dir().join(format!("clones-{}-{name}", std::process::id()));
        let _ = fs::remove_dir_all(&root);
        for (path, text) in files {
            let file = root.join(path);
            fs::create_dir_all(file.parent().unwrap()).unwrap();
            fs::write(file, text).unwrap();
        }
        root
    }

    const BLOCK: &str = "alpha = 1\nbeta = 2\ngamma = 3\n";

    #[test]
    fn searches_python_and_rust_files() {
        let root = tree(
            "languages",
            &[("a.py", BLOCK), ("b.rs", BLOCK), ("c.txt", BLOCK)],
        );
        let documents = Tree::new(root.display().to_string()).documents().unwrap();
        assert_eq!(Corpus::new(documents, 3).duplicates().len(), 1);
    }

    #[test]
    fn skips_migrations_generated_contracts_and_builds() {
        let root = tree(
            "skipped",
            &[
                ("app/models.py", BLOCK),
                ("app/migrations/0001_initial.py", BLOCK),
                ("server/contracts/hello_pb2.py", BLOCK),
                ("target/debug/build.rs", BLOCK),
            ],
        );
        let documents = Tree::new(root.display().to_string()).documents().unwrap();
        assert_eq!(documents.len(), 1);
    }

    #[test]
    fn fails_on_a_missing_root() {
        let root = std::env::temp_dir().join("clones-no-such-root");
        assert!(Tree::new(root.display().to_string()).documents().is_err());
    }
}
