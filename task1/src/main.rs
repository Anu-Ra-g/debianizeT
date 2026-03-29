use std::{env, fs, io, path::PathBuf};

use debian_control::Control;

fn main() {
    let mut filepath = String::new();
    println!("Enter the path to the debian-package (or empty for current path): ");

    io::stdin()
        .read_line(&mut filepath)
        .expect("Failed to read input");


    let filepath = filepath.trim();

    // if path is empty, assume current directory as debian package with "debian" folder
    let path: PathBuf = match filepath.is_empty(){
        true => env::current_dir().unwrap(),
        false => PathBuf::from(filepath)
    };

    if !path.exists() {
        println!("Path does not exist");
        return;
    }

    if !path.is_dir() {
        println!("Path must be a directory (Debian source package root)");
        return;
    }

    let control_path = path.join("debian/control");

    if !control_path.is_file() {
        println!("Missing debian/control under the given path");
        return;
    }

    let contents = match fs::read_to_string(&control_path) {
        Ok(c) => c,
        Err(e) => {
            println!("Failed to read {}: {e}", control_path.display());
            return;
        }
    };

    let control_cont = Control::parse(&contents).to_result().expect("Failed to parse control file");

    println!("{}", "#".repeat(30));
    println!("These are the following binary packges inside the source: ");
    for binary in control_cont.binaries(){
        println!("Package name: {}", binary.name().unwrap());
        println!("Architecture: {}", binary.architecture().unwrap());
        println!();
    }
    println!("{}", "#".repeat(30));
}
