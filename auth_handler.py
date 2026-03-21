from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

'''
self.path is apparently something you can just manipulate while using the http.server library. I could have just grabbed
this and gotten the same results. You can just make up self.server variables when you need them. 

self.server.code, self.server.butter, self.server.this_is_stupid.

I decided to just go with urllib after learning about it, as it formats things cleanly.

Intercept the redirect url (path) string. The .query selects the query section from the result of urlparse.

Example:
result = urlparse("http://localhost:8080/callback?code=abc123&state=xyz")
result.scheme    # 'http'
result.netloc    # 'localhost:8080'
result.path      # '/callback'
result.query     # 'code=abc123&state=xyz'
result.fragment  # ''

parse_qs takes the query section from above, and separates it into a dictionary.

Example:
'code=abc123&state=xyz' becomes {'code': ['abc123'], 'state': ['xyz']} <- Note the values are lists

wfile.write needs the b"" to be seen as bytes. 
'''
# Might want to revisit to apply a nonce
class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        if params["state"][0] == self.server.state:
            self.server.code = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authentication complete. Bitch.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"State string didn't match. Bitch.")
