#!/usr/bin/env python3
"""
Fuzzing Tool for Bug Bounty
A wrapper around ffuf that handles multiple wordlists, deduplication, and recursive fuzzing
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Set, Dict
from urllib.parse import urljoin, urlparse
import argparse
from datetime import datetime
import re


class FFufFuzzer:
    def __init__(self, url: str, wordlists: List[str], extensions: str = "", 
                 output_file: str = None, threads: int = 35, recursive: bool = False,
                 recursive_depth: int = 1, match_codes: str = "200,204,301,302,307,401,403"):
        """
        Initialize the fuzzer
        
        Args:
            url: Target URL to fuzz
            wordlists: List of wordlist file paths
            extensions: Extensions to test (e.g., ".php,.html,.txt")
            output_file: Output file to save results
            threads: Number of threads for ffuf (default: 35)
            recursive: Enable recursive fuzzing on discovered paths
            recursive_depth: Maximum recursion depth
            match_codes: HTTP status codes to match via ffuf -mc
        """
        self.url = url
        self.wordlists = wordlists
        self.extensions = extensions
        self.output_file = output_file or "fuzz_results.txt"
        self.threads = threads
        self.recursive = recursive
        self.recursive_depth = recursive_depth
        self.match_codes = match_codes
        self.discovered_paths: Set[str] = set()
        self.all_results: Dict[str, List[str]] = {}
        
        # Validate URL
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
        # Ensure the URL contains a 'FUZZ' placeholder; if not, append one
        if 'FUZZ' not in self.url:
            if self.url.endswith('/'):
                self.url = self.url + 'FUZZ'
            else:
                self.url = self.url + '/FUZZ'
        
        # Check if ffuf is installed
        if not self._check_ffuf_installed():
            raise RuntimeError("ffuf is not installed. Please install ffuf first: https://github.com/ffuf/ffuf")
        
        # Validate wordlists
        for wordlist in wordlists:
            if not os.path.exists(wordlist):
                raise FileNotFoundError(f"Wordlist not found: {wordlist}")
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate if URL is properly formatted"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def _check_ffuf_installed() -> bool:
        """Check if ffuf is installed"""
        try:
            subprocess.run(["ffuf", "-h"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def run_ffuf(self, wordlist: str, target_url: str = None) -> List[str]:
        """
        Run ffuf with specified wordlist
        
        Args:
            wordlist: Path to wordlist file
            target_url: Target URL (if None, uses self.url)
        
        Returns:
            List of discovered paths
        """
        if target_url is None:
            target_url = self.url
        
        print(f"[*] Fuzzing {target_url} with {Path(wordlist).name}...")

        # Build ffuf command using only allowed switches
        cmd = [
            "ffuf",
            "-u", target_url,
            "-w", wordlist,
            "-c",
            "-r",
            "-mc", self.match_codes,
            "-t", str(self.threads),
        ]

        # Add extensions if provided (allowed)
        if self.extensions:
            cmd.extend(["-e", self.extensions])

        try:
            # Run ffuf and capture stdout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            stdout = result.stdout or ""
            stderr = result.stderr or ""

            if result.returncode != 0 and not stdout:
                print(f"[-] ffuf returned non-zero exit ({result.returncode}); stderr:\n{stderr}")

            # Parse results from ffuf stdout
            paths = self._parse_ffuf_output(stdout)
            return paths

        except subprocess.TimeoutExpired:
            print(f"[-] FFuf timed out for {wordlist}")
            return []
        except Exception as e:
            print(f"[-] Error running ffuf: {e}")
            return []
    
    @staticmethod
    def _parse_ffuf_output(output: str) -> List[str]:
        """
        Parse ffuf stdout text and extract discovered paths/URLs.

        This function looks for tokens that look like paths (starting with '/')
        or full URLs and returns cleaned path strings.
        """
        paths: List[str] = []
        # Remove ANSI escape sequences (colors) to simplify parsing
        clean_output = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", output)
        # Split lines and look for common ffuf result patterns
        for line in clean_output.splitlines():
            line = line.strip()
            if not line:
                continue
            # Skip header/footer lines
            if line.startswith("ffuf") or line.startswith("---") or line.startswith("Total requests:"):
                continue

            # Try to find full URL first
            url_match = re.search(r"https?://[^\s]+", line)
            if url_match:
                found = url_match.group(0)
                # Extract path part
                try:
                    p = urlparse(found).path
                    if p:
                        paths.append(p)
                        continue
                except:
                    pass

            # Otherwise find tokens that start with '/'
            token_matches = re.findall(r"(/[A-Za-z0-9_\-./%?=&~]+)", line)
            for tok in token_matches:
                # ignore just '/' root hits
                if tok and tok != '/':
                    paths.append(tok)

        # Preserve order, remove duplicates
        unique = list(dict.fromkeys(paths))
        return unique
    
    def deduplicate_paths(self, paths: List[str]) -> List[str]:
        """
        Remove duplicate paths from results
        
        Args:
            paths: List of paths (may contain duplicates)
        
        Returns:
            List of unique paths
        """
        return list(dict.fromkeys(paths))  # Preserves order
    
    def fuzz_all_wordlists(self) -> Dict[str, List[str]]:
        """
        Run fuzzing with all provided wordlists
        
        Returns:
            Dictionary mapping wordlist names to discovered paths
        """
        results = {}
        
        for wordlist in self.wordlists:
            wordlist_name = Path(wordlist).name
            print(f"\n[+] Testing wordlist: {wordlist_name}")
            
            # Run ffuf with this wordlist
            paths = self.run_ffuf(wordlist)
            
            # Deduplicate paths
            unique_paths = self.deduplicate_paths(paths)
            
            results[wordlist_name] = unique_paths
            self.discovered_paths.update(unique_paths)
            
            print(f"[+] Found {len(unique_paths)} unique paths with {wordlist_name}")
        
        self.all_results = results
        return results
    
    def save_results(self) -> None:
        """Save all discovered paths to output file"""
        # Always save into resolve.txt and avoid adding duplicate paths
        output_path = Path("resolve.txt")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing entries from resolve.txt (ignore comments/blank lines)
        existing: Set[str] = set()
        if output_path.exists():
            try:
                with open(output_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        existing.add(line)
            except Exception:
                existing = set()

        # Merge discovered paths with existing ones (both are just path strings)
        new_paths = set(self.discovered_paths)
        merged = sorted(existing.union(new_paths))

        # Write merged, deduplicated results back to resolve.txt with header
        try:
            with open(output_path, 'w') as f:
                f.write(f"# Fuzzing Results for {self.url}\n")
                f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total unique paths found: {len(merged)}\n\n")
                for path in merged:
                    f.write(f"{path}\n")

            print(f"\n[+] Results saved to: {output_path}")
            print(f"[+] Total unique paths: {len(merged)}")
        except Exception as e:
            print(f"[-] Failed to write results: {e}")
    
    def get_base_domain(self) -> str:
        """Extract base domain from URL"""
        parsed = urlparse(self.url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def recursive_fuzz(self, current_depth: int = 0) -> None:
        """
        Recursively fuzz discovered paths
        
        Args:
            current_depth: Current recursion depth
        """
        if current_depth >= self.recursive_depth:
            print(f"[*] Reached maximum recursion depth ({self.recursive_depth})")
            return
        
        if not self.discovered_paths:
            print("[*] No paths discovered yet")
            return
        
        print(f"\n[+] Starting recursive fuzzing at depth {current_depth + 1}...")

        for path in list(self.discovered_paths):
            if not path.startswith('/'):
                path = f"/{path}"

            # Build recursive target by replacing FUZZ in the original URL
            if 'FUZZ' in self.url:
                # remove leading slash from path for insertion
                insert = path.lstrip('/')
                # ensure no duplicate slashes
                recursive_url = self.url.replace('FUZZ', insert + '/FUZZ')
            else:
                # fallback: join base domain and path then append FUZZ
                base_domain = self.get_base_domain()
                recursive_url = urljoin(base_domain, path.lstrip('/') + '/FUZZ')

            print(f"[*] Recursively fuzzing: {recursive_url}")

            for wordlist in self.wordlists:
                try:
                    recursive_paths = self.run_ffuf(wordlist, recursive_url)

                    # Add new paths found by joining with the parent path
                    for new_path in recursive_paths:
                        np = new_path.lstrip('/')
                        combined_path = f"{path.rstrip('/')}/{np}"
                        if combined_path not in self.discovered_paths:
                            self.discovered_paths.add(combined_path)
                except Exception as e:
                    print(f"[-] Error in recursive fuzzing: {e}")
                    continue
        
        # Continue recursion if enabled
        if current_depth < self.recursive_depth - 1:
            self.recursive_fuzz(current_depth + 1)
    
    def run(self) -> None:
        """Run the complete fuzzing process"""
        print(f"{'='*60}")
        print(f"FFuf Fuzzer - Bug Bounty Tool")
        print(f"{'='*60}")
        print(f"Target URL: {self.url}")
        print(f"Wordlists: {len(self.wordlists)}")
        print(f"Threads: {self.threads}")
        if self.extensions:
            print(f"Extensions: {self.extensions}")
        if self.recursive:
            print(f"Recursive Fuzzing: Enabled (Depth: {self.recursive_depth})")
        print(f"{'='*60}\n")
        
        # Phase 1: Fuzz all wordlists
        self.fuzz_all_wordlists()
        
        # Phase 2: Recursive fuzzing if enabled
        if self.recursive:
            self.recursive_fuzz()
        
        # Phase 3: Save results
        self.save_results()
        
        print(f"\n[+] Fuzzing complete!")


def main():
    parser = argparse.ArgumentParser(
        description="FFuf Fuzzer - Bug Bounty Fuzzing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic fuzzing with single wordlist
  python fuzzer.py -u http://target.com -w wordlist.txt
  
  # Multiple wordlists
  python fuzzer.py -u http://target.com -w wordlist1.txt wordlist2.txt wordlist3.txt
  
  # With extensions
  python fuzzer.py -u http://target.com -w wordlist.txt -e .php,.html,.txt
  
  # With recursive fuzzing
  python fuzzer.py -u http://target.com -w wordlist.txt -r -d 2
  
  # Custom output file and threads
  python fuzzer.py -u http://target.com -w wordlist.txt -o results.txt -t 50
        """
    )
    
    parser.add_argument("-u", "--url", required=True, help="Target URL to fuzz")
    parser.add_argument("-w", "--wordlists", nargs="+", required=True, 
                        help="Wordlist file(s) to use")
    parser.add_argument("-e", "--extensions", default="", 
                        help="Extensions to test (e.g., '.php,.html,.txt')")
    parser.add_argument("-m", "--match-codes", default="200,204,301,302,307,401,403",
                        help="HTTP status codes to match (ffuf -mc) e.g. 200,301,403")
    parser.add_argument("-o", "--output", default="fuzz_results.txt", 
                        help="Output file for results (default: fuzz_results.txt)")
    parser.add_argument("-t", "--threads", type=int, default=35, 
                        help="Number of threads for ffuf (default: 35)")
    parser.add_argument("-r", "--recursive", action="store_true", 
                        help="Enable recursive fuzzing on discovered paths")
    parser.add_argument("-d", "--depth", type=int, default=1, 
                        help="Recursion depth for recursive fuzzing (default: 1)")
    
    args = parser.parse_args()
    
    try:
        # Create fuzzer instance
        fuzzer = FFufFuzzer(
            url=args.url,
            wordlists=args.wordlists,
            extensions=args.extensions,
            output_file=args.output,
            threads=args.threads,
            recursive=args.recursive,
            recursive_depth=args.depth,
            match_codes=args.match_codes,
        )
        
        # Run fuzzing
        fuzzer.run()
        
    except Exception as e:
        print(f"[-] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
