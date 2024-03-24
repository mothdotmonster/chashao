# chashao

Incredibly minimalist dynamic DNS client for Porkbun *with IPv6 support!*

## USAGE:

Rename `example.config.toml` to `config.toml` and add your API key and domain name to it.  
**Make sure you've enabled API access for the domain you're trying to use!**  
Also, if your machine is IPv6 only, set `v6only` to `true`.

When ran, the script **will** change your DNS settings, and replaces **ALL** old records for the requested (sub)domain. Make sure you aren't running it on the wrong domain!