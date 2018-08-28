# Cloudflare-Update

This project is designed to point cloudflare DNS records to any given server.
The config file (config.json) needs to be edited with your own:
  - cloudflare login email
  - cloudflare global api key (viewable on cloudflare profile page)
  - the domains/subdomains you wish to point to your IP
  
To point A records for www.example.com and example.com to your IP the domains value should be:
```json
{"example.com":{"":"A", "www": "A"}}
```

You can point subdomains from multiple domains by adding extra domains to the dictionary. 
The following would point A records of www.test.com, git.test.com, and www.example.com to your IP:
```json
{"example.com":{"www":"A"},"test.com":{"www":"A","git":"A"}}
```
'''json
{"example.com":{"":"A", "www": "A"}}
```

You can point subdomains from multiple domains by adding extra domains to the dictionary. 
The following would point A records of www.test.com, git.test.com, and www.example.com to your IP

```json
{"example.com":{"www":"A"},"test.com":{"www":"A","git":"A"}}.
```

If you are looking for a free domain, check out freenom.com for a .tk domain. 
It is recommended this script is run via cron or some other scheduler to ensure your server is accessible at all times.

All that remain to access your server is to forward ports on your router. Do so at your own risk. 
