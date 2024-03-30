# chashao<sup>1</sup>

Incredibly minimalist dynamic DNS client for Porkbun *with IPv6 support!*  
Inspired somewhat by [porkbun-dynamic-dns-python](https://github.com/porkbundomains/porkbun-dynamic-dns-python).

## USAGE:

Rename `example.config.toml` to `config.toml` and add your API key and domain name to it.  
**Make sure you've enabled API access for the domain you're trying to use!**  
Also, if your machine is IPv6 only, set `v6only` to `true`.

When ran with `dryrun` disabled, the script **will** change your DNS settings, and replaces **ALL** old records for the requested (sub)domain. Make sure you aren't running it on the wrong domain!

***

1. [叉烧 (chāshāo)](https://en.wikipedia.org/wiki/Char_siu) is a type of barbecued pork, which is often used as a filling in buns.