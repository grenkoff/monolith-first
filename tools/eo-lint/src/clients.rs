//! gRPC clients in a service: only core calls services synchronously.

use syn::visit::{self, Visit};
use syn::{Ident, ItemUse, Path, UseTree};

use crate::finding::Finding;

/// End of the module that tonic generates for the client of a `<Name>Service`.
const CLIENT: &str = "_service_client";

/// Names that an import tree mentions.
trait Mentions {
    /// Returns every identifier of the tree, groups and nested paths included.
    fn idents(&self) -> Vec<&Ident>;
}

impl Mentions for UseTree {
    fn idents(&self) -> Vec<&Ident> {
        match self {
            Self::Path(path) => std::iter::once(&path.ident)
                .chain(path.tree.idents())
                .collect(),
            Self::Name(name) => vec![&name.ident],
            Self::Rename(rename) => vec![&rename.ident],
            Self::Group(group) => group.items.iter().flat_map(Mentions::idents).collect(),
            Self::Glob(_) => Vec::new(),
        }
    }
}

/// Visitor that collects the gRPC clients a service would call others through.
#[derive(Debug)]
pub struct Clients {
    /// Path of the inspected file.
    file: String,
    /// Violations found so far.
    findings: Vec<Finding>,
}

impl Clients {
    /// Starts the inspection of one file of a service.
    #[must_use]
    pub fn new(file: impl Into<String>) -> Self {
        Self {
            file: file.into(),
            findings: Vec::new(),
        }
    }

    /// Returns a finding when the identifier names a generated gRPC client.
    fn finding(&self, ident: &Ident) -> Option<Finding> {
        ident.to_string().ends_with(CLIENT).then(|| {
            Finding::new(
                &self.file,
                ident.span().start().line,
                "EO012",
                format!("a service calls `{ident}`; only core calls services synchronously"),
            )
        })
    }
}

impl From<Clients> for Vec<Finding> {
    fn from(clients: Clients) -> Self {
        clients.findings
    }
}

impl<'ast> Visit<'ast> for Clients {
    fn visit_item_use(&mut self, node: &'ast ItemUse) {
        let found: Vec<Finding> = node
            .tree
            .idents()
            .into_iter()
            .filter_map(|ident| self.finding(ident))
            .collect();
        self.findings.extend(found);
    }

    fn visit_path(&mut self, node: &'ast Path) {
        let found: Vec<Finding> = node
            .segments
            .iter()
            .filter_map(|segment| self.finding(&segment.ident))
            .collect();
        self.findings.extend(found);
        visit::visit_path(self, node);
    }
}
