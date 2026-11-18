//! Generates Rust code from every contract in `proto/`.

use std::env;
use std::ffi::OsStr;
use std::fs;
use std::io;
use std::path::{Path, PathBuf};

const PROTO: &str = "../proto";
const INCLUDE: &str = "contracts.rs";

/// Compiles every contract into one file of modules that `lib.rs` includes.
fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("cargo:rerun-if-changed={PROTO}");
    let found = contracts(Path::new(PROTO))?;
    if found.is_empty() {
        fs::write(Path::new(&env::var("OUT_DIR")?).join(INCLUDE), "")?;
        return Ok(());
    }
    tonic_prost_build::configure()
        .include_file(INCLUDE)
        .compile_protos(&found, &[PathBuf::from(PROTO)])?;
    Ok(())
}

/// Lists every `.proto` file under a directory, in a stable order.
fn contracts(directory: &Path) -> io::Result<Vec<PathBuf>> {
    let mut found = Vec::new();
    for entry in fs::read_dir(directory)? {
        let path = entry?.path();
        if path.is_dir() {
            found.extend(contracts(&path)?);
        } else if path.extension() == Some(OsStr::new("proto")) {
            found.push(path);
        }
    }
    found.sort();
    Ok(found)
}
