/****************************************************************
 * Gaucho Conquer II Mobile - MITM Proxy Sniffer & Packet Logger
 * Completely transparent: 0% crash risk, decrypts both directions
 ****************************************************************/

use gaucho_server::net::crypto::{
    handshake_cfb, md5_key, Cast5, Cfb, Handshake, SEAL_CLIENT, SEAL_SERVER,
};
use gaucho_server::net::take_packets;
use num_bigint::BigUint;
use std::collections::HashMap;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::net::SocketAddr;
use std::path::Path;
use std::sync::Arc;
use std::time::Duration;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::Mutex;
use tokio::time::timeout;

struct PacketLogger {
    names: HashMap<u16, String>,
    log_file: Arc<Mutex<fs::File>>,
    json_file: Arc<Mutex<fs::File>>,
    seq: Arc<std::sync::atomic::AtomicU64>,
}

impl PacketLogger {
    fn new(names_path: &str, log_path: &str, json_path: &str) -> Self {
        let mut names = HashMap::new();
        if let Ok(content) = fs::read_to_string(names_path) {
            for line in content.lines() {
                let parts: Vec<&str> = line.trim().split_whitespace().collect();
                if parts.len() >= 2 {
                    if let Ok(id) = parts[0].parse::<u16>() {
                        names.insert(id, parts[1].to_string());
                    }
                }
            }
        }
        println!("[*] Loaded {} packet definitions.", names.len());

        let log_file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(log_path)
            .expect("open log file");
        let json_file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(json_path)
            .expect("open json file");

        Self {
            names,
            log_file: Arc::new(Mutex::new(log_file)),
            json_file: Arc::new(Mutex::new(json_file)),
            seq: Arc::new(std::sync::atomic::AtomicU64::new(1)),
        }
    }

    async fn log_packet(&self, dir: &str, ty: u16, body: &[u8]) {
        let seq = self.seq.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        let name = self.names.get(&ty).cloned().unwrap_or_else(|| format!("Unknown_{:#06X}", ty));
        let strings = extract_strings(body, 3);
        let now = chrono_fallback();

        let arrow = if dir == "C2S" {
            ">>> [CLIENT -> SERVER]"
        } else {
            "<<< [SERVER -> CLIENT]"
        };

        let header = format!(
            "{now} #{seq:04} {arrow} Type: {ty} (0x{ty:04X} {name}) Size: {}",
            body.len() + 4
        );

        println!("{}", "=".repeat(78));
        println!("{header}");
        if !strings.is_empty() {
            println!("  [STRINGS]: {strings:?}");
        }

        // Special packet parsing
        if ty == 2031 || ty == 2032 {
            // TaskDialog
            if body.len() >= 10 {
                let npc_id = u32::from_le_bytes(body[0..4].try_into().unwrap_or_default());
                let action = body.get(6).copied().unwrap_or(0);
                println!("  [NPC DIALOG]: NPC ID={npc_id} DialogAction={action}");
            }
        } else if ty == 10010 {
            // Action
            if body.len() >= 16 {
                let entity = u32::from_le_bytes(body[0..4].try_into().unwrap_or_default());
                let param = u32::from_le_bytes(body[4..8].try_into().unwrap_or_default());
                let action = u16::from_le_bytes(body[8..10].try_into().unwrap_or_default());
                println!("  [ACTION]: Entity={entity} Action={action} Param={param}");
            }
        }

        let hex_preview = hex_dump(body, 64);
        println!("  [HEX]: {hex_preview}");

        // Write to text log
        let mut f = self.log_file.lock().await;
        let _ = writeln!(f, "{header}");
        if !strings.is_empty() {
            let _ = writeln!(f, "  Strings: {strings:?}");
        }
        let _ = writeln!(f, "  Hex: {}", hex_string(body));
        let _ = writeln!(f);
        let _ = f.flush();

        // Write to JSONL
        let mut jf = self.json_file.lock().await;
        let json_entry = format!(
            "{{\"seq\":{},\"time\":\"{}\",\"dir\":\"{}\",\"type\":{},\"name\":\"{}\",\"size\":{},\"strings\":{:?},\"hex\":\"{}\"}}\n",
            seq, now, dir, ty, name, body.len() + 4, strings, hex_string(body)
        );
        let _ = jf.write_all(json_entry.as_bytes());
        let _ = jf.flush();
    }
}

fn frame_c2s(ty: u16, body: &[u8]) -> Vec<u8> {
    let mut f = Vec::with_capacity(body.len() + 12);
    f.extend_from_slice(&((body.len() + 4) as u16).to_le_bytes());
    f.extend_from_slice(&ty.to_le_bytes());
    f.extend_from_slice(body);
    f.extend_from_slice(SEAL_CLIENT);
    f
}

fn frame_s2c(ty: u16, body: &[u8]) -> Vec<u8> {
    let mut f = Vec::with_capacity(body.len() + 12);
    f.extend_from_slice(&((body.len() + 4) as u16).to_le_bytes());
    f.extend_from_slice(&ty.to_le_bytes());
    f.extend_from_slice(body);
    f.extend_from_slice(SEAL_SERVER);
    f
}

fn extract_strings(data: &[u8], min_len: usize) -> Vec<String> {
    let mut out = Vec::new();
    let mut cur = Vec::new();
    for &b in data {
        if (32..=126).contains(&b) {
            cur.push(b);
        } else {
            if cur.len() >= min_len {
                if let Ok(s) = std::str::from_utf8(&cur) {
                    if !s.trim().is_empty() {
                        out.push(s.to_string());
                    }
                }
            }
            cur.clear();
        }
    }
    if cur.len() >= min_len {
        if let Ok(s) = std::str::from_utf8(&cur) {
            if !s.trim().is_empty() {
                out.push(s.to_string());
            }
        }
    }
    out
}

fn hex_string(data: &[u8]) -> String {
    data.iter().map(|b| format!("{b:02x}")).collect()
}

fn hex_dump(data: &[u8], max: usize) -> String {
    let n = data.len().min(max);
    let mut s = hex_string(&data[..n]);
    if data.len() > max {
        s.push_str("...");
    }
    s
}

fn chrono_fallback() -> String {
    let now = std::time::SystemTime::now();
    let d = now.duration_since(std::time::UNIX_EPOCH).unwrap_or_default();
    let secs = d.as_secs() % 86400;
    let (h, m, s) = (secs / 3600, (secs % 3600) / 60, secs % 60);
    let ms = d.subsec_millis();
    format!("{h:02}:{m:02}:{s:02}.{ms:03}")
}

// Parse Server Hello TLV fields: [len u32][bytes]...
struct ServerHelloFields {
    iv_dec: [u8; 8],
    iv_enc: [u8; 8],
    prime_hex: String,
    generator: u32,
    server_pub_hex: String,
}

fn parse_server_hello(wire: &[u8]) -> Option<ServerHelloFields> {
    let mut d = wire.to_vec();
    handshake_cfb().decrypt(&mut d);

    let seal = d.windows(8).rposition(|w| w == SEAL_SERVER)?;
    let body = &d[15..seal]; // skip random prefix (11) + len (4)

    let mut r = &body[..];
    let mut fields: Vec<Vec<u8>> = Vec::new();
    while r.len() >= 4 {
        let flen = u32::from_le_bytes(r[0..4].try_into().unwrap()) as usize;
        r = &r[4..];
        if r.len() < flen {
            break;
        }
        fields.push(r[..flen].to_vec());
        r = &r[flen..];
    }

    if fields.len() < 6 {
        return None;
    }

    let iv_dec: [u8; 8] = fields[1].as_slice().try_into().ok()?;
    let iv_enc: [u8; 8] = fields[2].as_slice().try_into().ok()?;
    let prime_hex = String::from_utf8(fields[3].clone()).ok()?;
    let generator_str = String::from_utf8(fields[4].clone()).ok()?;
    let generator: u32 = generator_str.parse().unwrap_or(2);
    let server_pub_hex = String::from_utf8(fields[5].clone()).ok()?;

    Some(ServerHelloFields {
        iv_dec,
        iv_enc,
        prime_hex,
        generator,
        server_pub_hex,
    })
}

#[tokio::main]
async fn main() {
    println!("{}", "=".repeat(78));
    println!(" Conquer II Mobile (Gaucho) - Real-time MITM Proxy Sniffer");
    println!("{}", "=".repeat(78));

    let bind_port = std::env::var("PROXY_PORT").unwrap_or_else(|_| "8020".to_string());
    let target_server = std::env::var("TARGET_SERVER").unwrap_or_else(|_| "170.33.9.35:8020".to_string());
    let names_path = std::env::var("NAMES_FILE").unwrap_or_else(|_| "../mobile-packets-ids-names.txt".to_string());
    let log_dir = Path::new("../tools/logs");
    let _ = fs::create_dir_all(log_dir);

    let timestamp = chrono_fallback().replace(':', "").replace('.', "_");
    let log_path = log_dir.join(format!("proxy_packets_{timestamp}.txt"));
    let json_path = log_dir.join(format!("proxy_packets_{timestamp}.jsonl"));

    println!("[*] Listening on: 0.0.0.0:{bind_port}");
    println!("[*] Forwarding to: {target_server}");
    println!("[*] Log file: {}", log_path.display());

    let logger = Arc::new(PacketLogger::new(
        &names_path,
        log_path.to_str().unwrap(),
        json_path.to_str().unwrap(),
    ));

    let listener = TcpListener::bind(format!("0.0.0.0:{bind_port}"))
        .await
        .unwrap_or_else(|e| panic!("Failed to bind port {bind_port}: {e}"));

    println!("\n[+] Proxy running and ready for game connections!");
    println!("[*] Waiting for game to connect...\n");

    while let Ok((client_socket, client_addr)) = listener.accept().await {
        println!("[+] New connection from client: {client_addr}");
        let target = target_server.clone();
        let logger = logger.clone();

        tokio::spawn(async move {
            if let Err(e) = handle_connection(client_socket, client_addr, &target, logger).await {
                eprintln!("[-] Connection error {client_addr}: {e}");
            }
        });
    }
}

async fn handle_connection(
    mut client_stream: TcpStream,
    client_addr: SocketAddr,
    target_addr: &str,
    logger: Arc<PacketLogger>,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    client_stream.set_nodelay(true)?;

    // 1. Connect to Real Server
    println!("[*] Connecting to real server {target_addr}...");
    let mut server_stream = TcpStream::connect(target_addr).await?;
    server_stream.set_nodelay(true)?;
    println!("[+] Connected to real server {target_addr}!");

    // 2. Read Server Hello from Real Server
    let mut server_hello_raw = vec![0u8; 1024];
    let n = timeout(Duration::from_secs(5), server_stream.read(&mut server_hello_raw)).await??;
    server_hello_raw.truncate(n);
    println!("[*] Received ServerHello from Real Server: {n} bytes");

    let parsed_srv = parse_server_hello(&server_hello_raw)
        .ok_or_else(|| "Failed to parse Real ServerHello")?;

    // 3. Compute Real Server DH shared secret & key
    let prime = BigUint::parse_bytes(parsed_srv.prime_hex.as_bytes(), 16)
        .ok_or("Invalid prime hex")?;
    let gen = BigUint::from(parsed_srv.generator);

    // Generate proxy-to-server DH keypair
    let proxy_to_srv_priv = {
        use rand::RngCore;
        let mut rng = rand::thread_rng();
        let mut priv_bytes = [0u8; 128];
        rng.fill_bytes(&mut priv_bytes);
        BigUint::from_bytes_be(&priv_bytes) % (&prime - &BigUint::from(2u32)) + BigUint::from(2u32)
    };
    let proxy_to_srv_pub = gen.modpow(&proxy_to_srv_priv, &prime).to_str_radix(16).to_uppercase();

    let srv_pub = BigUint::parse_bytes(parsed_srv.server_pub_hex.as_bytes(), 16)
        .ok_or("Invalid server pub")?;
    let srv_shared = srv_pub.modpow(&proxy_to_srv_priv, &prime).to_bytes_be();
    let srv_key = Cast5::new(&md5_key(&srv_shared)[..16]);

    // Send correct DH reply to Real Server (Length prefix + pub hex + SEAL_CLIENT)
    let mut srv_reply = Vec::new();
    srv_reply.extend_from_slice(&(proxy_to_srv_pub.len() as u32).to_le_bytes());
    srv_reply.extend_from_slice(proxy_to_srv_pub.as_bytes());
    srv_reply.extend_from_slice(SEAL_CLIENT);
    handshake_cfb().encrypt(&mut srv_reply);
    server_stream.write_all(&srv_reply).await?;
    println!("[+] Handshake with Real Server complete!");

    // 4. Handshake with Client: Send Proxy's ServerHello
    let proxy_client_hs = Handshake::new();
    client_stream.write_all(&proxy_client_hs.server_hello()).await?;

    // Read Client reply
    let mut client_buf = Vec::new();
    let mut chunk = vec![0u8; 4096];
    let mut client_key = None;
    for _ in 0..10 {
        let n = timeout(Duration::from_secs(5), client_stream.read(&mut chunk)).await??;
        if n == 0 {
            return Err("Client closed connection".into());
        }
        client_buf.extend_from_slice(&chunk[..n]);

        if client_buf.len() >= 10 {
            client_key = proxy_client_hs
                .client_reply(&client_buf[2..])
                .or_else(|| proxy_client_hs.client_reply(&client_buf));
            if client_key.is_some() {
                break;
            }
        }
    }

    let client_key = client_key.ok_or("Client DH handshake failed")?;
    println!("[+] Handshake with Client complete! Encryption fully established!");

    // 5. Setup Ciphers
    // For Client:
    let mut client_dec = Cfb::new(client_key.clone(), proxy_client_hs.iv_enc);
    let mut client_enc = Cfb::new(client_key, proxy_client_hs.iv_dec);

    // For Server:
    let mut srv_dec = Cfb::new(srv_key.clone(), parsed_srv.iv_dec);
    let mut srv_enc = Cfb::new(srv_key, parsed_srv.iv_enc);

    let (mut client_rd, mut client_wr) = client_stream.into_split();
    let (mut srv_rd, mut srv_wr) = server_stream.into_split();

    // 6. Spawn Client -> Server Pump
    let logger_c2s = logger.clone();
    let c2s_pump = tokio::spawn(async move {
        let mut buf = vec![0u8; 8192];
        let mut acc = Vec::new();
        while let Ok(n) = client_rd.read(&mut buf).await {
            if n == 0 {
                break;
            }
            let mut chunk = buf[..n].to_vec();
            client_dec.decrypt(&mut chunk);
            acc.extend_from_slice(&chunk);

            for (ty, body) in take_packets(&mut acc) {
                logger_c2s.log_packet("C2S", ty, &body).await;
                // Frame packet for server with SEAL_CLIENT
                let mut pkt = frame_c2s(ty, &body);
                srv_enc.encrypt(&mut pkt);
                if srv_wr.write_all(&pkt).await.is_err() {
                    return;
                }
            }
        }
    });

    // 7. Spawn Server -> Client Pump
    let logger_s2c = logger.clone();
    let s2c_pump = tokio::spawn(async move {
        let mut buf = vec![0u8; 8192];
        let mut acc = Vec::new();
        while let Ok(n) = srv_rd.read(&mut buf).await {
            if n == 0 {
                break;
            }
            let mut chunk = buf[..n].to_vec();
            srv_dec.decrypt(&mut chunk);
            acc.extend_from_slice(&chunk);

            for (ty, body) in take_packets(&mut acc) {
                logger_s2c.log_packet("S2C", ty, &body).await;
                // Frame packet for client with SEAL_SERVER
                let mut pkt = frame_s2c(ty, &body);
                client_enc.encrypt(&mut pkt);
                if client_wr.write_all(&pkt).await.is_err() {
                    return;
                }
            }
        }
    });

    let _ = tokio::try_join!(c2s_pump, s2c_pump);
    println!("[-] Session with {client_addr} ended.");
    Ok(())
}
