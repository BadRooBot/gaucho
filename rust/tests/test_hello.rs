use gaucho_server::net::crypto::*;
use std::fs;

#[test]
fn test_decrypt_server_hello() {
    let mut data = fs::read("../tools/server_hello.bin").expect("read");
    println!("Raw len: {}", data.len());
    let mut cfb = handshake_cfb();
    cfb.decrypt(&mut data);
    println!("Decrypted len: {}", data.len());
    println!("Decrypted first 32 bytes: {:02x?}", &data[..32]);
    let seal_idx = data.windows(8).position(|w| w == SEAL_SERVER);
    println!("Contains TQServer seal? {:?}", seal_idx);
    if let Some(idx) = seal_idx {
        println!("Found TQServer at index {}!", idx);
    }
}
