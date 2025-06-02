| ✅ Status         | 📌 Feature                    | 🎯 Goal / Purpose                                         | ⚙️ How to Implement                              | ⭐ Priority |
| ---------------- | ----------------------------- | --------------------------------------------------------- | ------------------------------------------------ | ---------- |
| ✅ Done / Planned | **Host Discovery**            | Find which devices are alive on the network               | Ping sweep using `subprocess` or `scapy`         | High       |
| ✅ Planned        | **Port Scanning**             | Find which ports are open on a host                       | Use `socket` or `asyncio` with timeout           | High       |
| ✅ Planned        | **Banner Grabbing**           | Get service info or version from open ports               | Connect to port and read basic response string   | High       |
| ✅ Planned        | **CSV Export**                | Save results for viewing in Streamlit or Excel            | Use `csv` module to write scan results           | High       |
| ⏳ Optional       | **JSON Export**               | Better format for future APIs or data processing          | Use `json` module to dump results                | Medium     |
| ⏳ Optional       | **Hostname Resolution**       | Show readable names instead of just IP addresses          | Use `socket.gethostbyaddr(ip)`                   | Medium     |
| ⏳ Optional       | **Async or Threaded Scan**    | Make the scanner faster and responsive                    | Use `ThreadPoolExecutor` or `asyncio`            | High       |
| ⏳ Optional       | **Custom Port Profiles**      | Allow user to choose "fast", "full", or custom scan modes | Define port sets like `COMMON_PORTS`             | Medium     |
| ⏳ Optional       | **OS Detection**              | Guess operating system based on IP behavior               | TTL + TCP fingerprinting with `scapy`            | Low        |
| ⏳ Optional       | **Nmap Integration**          | Use external tool for deep scanning                       | Use `python-nmap`                                | Low        |
| 🕐 Later         | **Streamlit UI**              | Show scan results in a web dashboard                      | Load CSV with `pandas`, display with `Streamlit` | High       |
| 🕐 Later         | **Scan Filter/Search in UI**  | Search results by port, IP, service                       | Add filter widgets in Streamlit                  | Medium     |
| 🕐 Later         | **Charts / Graphs in UI**     | Visualize number of services, open ports, etc.            | Use Streamlit `st.bar_chart`, `st.pyplot`, etc.  | Medium     |
| ⏳ Optional       | **Scan Scheduler / Profiles** | Save scan config and schedule scans regularly             | Use config files (YAML/JSON) or SQLite           | Low        |
| ⏳ Optional       | **Notification on Complete**  | Let user know when scan ends (email or alert)             | Use `smtplib`, `notify2`, or Streamlit callback  | Low        |
