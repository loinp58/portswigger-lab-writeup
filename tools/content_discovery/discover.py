#!/usr/bin/env python3
"""
Content Discovery Tool
Mimics Burp Suite Pro's Engage Tools -> Discover Content
"""

import requests
import argparse
import sys
import time
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init(autoreset=True)

# Built-in wordlist — augmented by --wordlist if provided
DEFAULT_WORDS = [
    # Common directories
    "admin", "administrator", "login", "logout", "dashboard", "panel",
    "api", "v1", "v2", "v3", "graphql", "rest",
    "backup", "backups", "bak", "old", "temp", "tmp", "test",
    "upload", "uploads", "files", "file", "assets", "static", "media",
    "images", "img", "css", "js", "fonts",
    "config", "configuration", "conf", "settings", "setup",
    "install", "installer", "update", "upgrade",
    "logs", "log", "debug", "trace", "error",
    "user", "users", "account", "accounts", "profile",
    "db", "database", "sql", "phpmyadmin", "adminer",
    "wp-admin", "wp-login", "wp-content", "wordpress",
    "git", ".git", ".svn", ".env", ".htaccess", ".htpasswd",
    "robots.txt", "sitemap.xml", "crossdomain.xml", "security.txt",
    "readme", "readme.md", "readme.txt", "README",
    "changelog", "license", "LICENSE",
    "info", "phpinfo", "server-status", "server-info",
    "cgi-bin", "scripts", "bin", "include", "includes",
    "src", "source", "lib", "library", "vendor", "node_modules",
    # Common file extensions to try
    "index.php", "index.html", "index.asp", "index.aspx", "index.jsp",
    "login.php", "login.html", "admin.php",
    "config.php", "config.json", "config.yml", "config.yaml",
    ".env", ".env.local", ".env.production", ".env.backup",
    "web.config", "app.config", "appsettings.json",
    "package.json", "composer.json", "requirements.txt",
    "Dockerfile", "docker-compose.yml",
]

INTERESTING_EXTENSIONS = [
    "", ".php", ".html", ".htm", ".asp", ".aspx", ".jsp",
    ".txt", ".bak", ".old", ".orig", ".backup",
    ".json", ".xml", ".yml", ".yaml", ".conf", ".config",
    ".log", ".sql", ".db", ".zip", ".tar.gz",
]

FOUND = []
VISITED_LINKS = set()


def print_banner():
    print(f"""{Fore.CYAN}
 ██████╗ ██████╗ ███╗   ██╗████████╗███████╗███╗   ██╗████████╗
██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔════╝████╗  ██║╚══██╔══╝
██║     ██║   ██║██╔██╗ ██║   ██║   █████╗  ██╔██╗ ██║   ██║
██║     ██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██║╚██╗██║   ██║
╚██████╗╚██████╔╝██║ ╚████║   ██║   ███████╗██║ ╚████║   ██║
 ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝   ╚═╝
         DISCOVERY TOOL  —  mimics Burp Pro Discover Content
{Style.RESET_ALL}""")


def load_wordlist(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] Wordlist not found: {path}{Style.RESET_ALL}")
        sys.exit(1)


def status_color(code):
    if code == 200:
        return Fore.GREEN
    elif code in (301, 302, 307, 308):
        return Fore.YELLOW
    elif code == 403:
        return Fore.MAGENTA
    elif code == 401:
        return Fore.CYAN
    else:
        return Fore.WHITE


def probe(session, url, timeout):
    try:
        r = session.get(url, timeout=timeout, allow_redirects=False)
        return url, r.status_code, len(r.content)
    except requests.exceptions.ConnectionError:
        return url, None, 0
    except requests.exceptions.Timeout:
        return url, None, 0
    except Exception:
        return url, None, 0


def crawl_links(session, base_url, timeout):
    """Extract all hrefs/src from the page — same as Burp's passive spider."""
    found_links = set()
    try:
        r = session.get(base_url, timeout=timeout)
        soup = BeautifulSoup(r.text, "html.parser")
        base_parsed = urlparse(base_url)

        for tag in soup.find_all(["a", "link", "script", "img", "form"]):
            attr = "href" if tag.name in ("a", "link") else "src"
            if tag.name == "form":
                attr = "action"
            href = tag.get(attr)
            if not href:
                continue
            full = urljoin(base_url, href)
            parsed = urlparse(full)
            # Stay on same host
            if parsed.netloc == base_parsed.netloc:
                found_links.add(full.split("?")[0])  # strip query string
    except Exception as e:
        print(f"{Fore.RED}[CRAWL ERROR] {e}{Style.RESET_ALL}")
    return found_links


def build_urls(base_url, words, extensions, no_ext):
    urls = []
    base = base_url.rstrip("/")
    for word in words:
        # Try bare word as directory
        urls.append(f"{base}/{word}/")
        if no_ext:
            urls.append(f"{base}/{word}")
            continue
        for ext in extensions:
            if not ext or word.endswith(ext):
                urls.append(f"{base}/{word}")
            else:
                urls.append(f"{base}/{word}{ext}")
    return list(dict.fromkeys(urls))  # deduplicate, preserve order


def run_discovery(args):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; ContentDiscovery/1.0)",
    })
    if args.cookie:
        for pair in args.cookie.split(";"):
            k, _, v = pair.strip().partition("=")
            session.cookies.set(k.strip(), v.strip())
    if args.header:
        for pair in args.header:
            k, _, v = pair.partition(":")
            session.headers[k.strip()] = v.strip()

    base_url = args.url.rstrip("/")
    ignore_codes = set(map(int, args.ignore.split(","))) if args.ignore else {404}

    print_banner()
    print(f"{Fore.CYAN}[*] Target  : {base_url}")
    print(f"[*] Threads : {args.threads}")
    print(f"[*] Timeout : {args.timeout}s")
    print(f"[*] Ignore  : {ignore_codes}{Style.RESET_ALL}\n")

    # Phase 1: passive crawl
    print(f"{Fore.CYAN}[PHASE 1] Crawling page for existing links...{Style.RESET_ALL}")
    crawled = crawl_links(session, base_url, args.timeout)
    for link in sorted(crawled):
        if link not in VISITED_LINKS:
            VISITED_LINKS.add(link)
            print(f"  {Fore.BLUE}[LINK] {link}{Style.RESET_ALL}")
    print(f"  Found {len(crawled)} links.\n")

    # Phase 2: active brute-force
    words = DEFAULT_WORDS[:]
    if args.wordlist:
        words = load_wordlist(args.wordlist)
        print(f"{Fore.CYAN}[*] Loaded {len(words)} words from {args.wordlist}{Style.RESET_ALL}")

    extensions = INTERESTING_EXTENSIONS if not args.no_ext else [""]
    urls = build_urls(base_url, words, extensions, args.no_ext)

    print(f"{Fore.CYAN}[PHASE 2] Brute-forcing {len(urls)} paths with {args.threads} threads...{Style.RESET_ALL}\n")

    start = time.time()
    found_count = 0

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(probe, session, u, args.timeout): u for u in urls}
        try:
            for future in as_completed(futures):
                url, code, size = future.result()
                if code is None or code in ignore_codes:
                    continue
                color = status_color(code)
                print(f"  {color}[{code}] {url}  ({size} bytes){Style.RESET_ALL}")
                FOUND.append({"url": url, "status": code, "size": size})
                found_count += 1
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Interrupted by user.{Style.RESET_ALL}")

    elapsed = time.time() - start

    # Summary
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"  RESULTS: {found_count} paths found in {elapsed:.1f}s")
    print(f"{'='*60}{Style.RESET_ALL}")
    for item in sorted(FOUND, key=lambda x: x["status"]):
        color = status_color(item["status"])
        print(f"  {color}[{item['status']}] {item['url']}{Style.RESET_ALL}")

    if args.output:
        with open(args.output, "w") as f:
            f.write(f"# Content Discovery — {base_url}\n\n")
            for item in FOUND:
                f.write(f"[{item['status']}] {item['url']}  ({item['size']} bytes)\n")
        print(f"\n{Fore.GREEN}[+] Results saved to {args.output}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description="Content Discovery Tool — mimics Burp Pro Discover Content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python discover.py -u http://target.com
  python discover.py -u http://target.com -w /usr/share/wordlists/dirb/common.txt
  python discover.py -u http://target.com -t 20 --ignore 404,403
  python discover.py -u http://target.com --cookie "session=abc123" -o results.txt
        """,
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL (e.g. http://target.com)")
    parser.add_argument("-w", "--wordlist", help="Path to custom wordlist (one word per line)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")
    parser.add_argument("--ignore", default="404", help="Comma-separated status codes to ignore (default: 404)")
    parser.add_argument("--cookie", help='Cookies to send, e.g. "session=abc; user=foo"')
    parser.add_argument("--header", action="append", help='Extra header, e.g. "Authorization: Bearer token" (repeatable)')
    parser.add_argument("--no-ext", action="store_true", help="Skip extension brute-forcing, directories only")
    parser.add_argument("-o", "--output", help="Save results to file")
    args = parser.parse_args()

    run_discovery(args)


if __name__ == "__main__":
    main()
