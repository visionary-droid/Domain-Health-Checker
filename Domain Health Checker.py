import pandas as pd
import dns.resolver
import sys

def check_domain(domain):
    result = {
        "Domain": domain,
        "SPF_Fail": 1,     # assume fail, change to 0 if record found
        "DKIM_Fail": 1,
        "DMARC_Fail": 1
    }
    try:
        # SPF
        for rdata in dns.resolver.resolve(domain, "TXT"):
            txt = rdata.to_text().strip('"')
            if txt.startswith("v=spf1"):
                result["SPF_Fail"] = 0
                break
    except:
        pass

    try:
        # DMARC
        for rdata in dns.resolver.resolve(f"_dmarc.{domain}", "TXT"):
            txt = rdata.to_text().strip('"')
            if txt.startswith("v=DMARC1"):
                result["DMARC_Fail"] = 0
                break
    except:
        pass

    try:
        # DKIM default selector (best-effort)
        dns.resolver.resolve(f"default._domainkey.{domain}", "TXT")
        result["DKIM_Fail"] = 0
    except:
        pass

    return result

if __name__ == "__main__":
    infile, outfile = sys.argv[1], sys.argv[2]
    print(f"Loading Excel: {infile}")
    df = pd.read_excel(infile, sheet_name="Unique_Custom_Domains")
    domains = df["Custom/Private Domain"].dropna().unique()
    print(f"Found {len(domains)} unique domains to check...")

    results = []
    for i, d in enumerate(domains, start=1):
        print(f"[{i}/{len(domains)}] Checking {d}...")
        results.append(check_domain(d))

    outdf = pd.DataFrame(results)
    outdf.to_excel(outfile, index=False)
    print(f"\n✅ Done! Results saved to {outfile}")
