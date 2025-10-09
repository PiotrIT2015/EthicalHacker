Accessing web server log files containing JSESSIONID or PHPSESSID is a serious security risk known as session hijacking. 
An attacker with access to these logs can steal valid session IDs, impersonate users, and gain unauthorized access to their accounts. 
For this reason, web server administrators and developers must take steps to prevent these identifiers from being logged. 
The security threat
A session ID is a unique token used to authenticate a user's session with a web server. 
It is the key that verifies a user's identity after they have logged in. Attackers can exploit logged session IDs in several ways:
Session hijacking: If an attacker obtains a valid session ID from a log file, they can set that same ID in their own browser cookies. 
The web server will then treat the attacker's requests as though they originated from the legitimate user, 
granting them full access to the user's account.
Predicting session IDs: If a system uses a weak, predictable method for generating session IDs, 
an attacker can analyze a pattern of session IDs in the logs to guess other valid IDs and gain access to user accounts.
Data exposure: Log files with unredacted session IDs may be accessible to a wide range of individuals, 
such as system administrators, developers, and third-party services. This increases the risk of accidental exposure or malicious exploitation. 
Mitigation strategies and best practices
The search query intext:JSESSIONID OR intext:PHPSESSID inurl:access.log ext:log is likely being used by 
security professionals, penetration testers, or malicious actors to find vulnerable systems. 
The solution is to prevent these queries from being successful.
To prevent session IDs from being exposed, web administrators should follow these best practices:
Never log session IDs in web server logs: The core security principle is to never write sensitive data to log files in the first place. 
Log files should only capture non-sensitive information.
Filter sensitive data from logs: Web server configurations should be set to filter out session ID information before it is written 
to log files. For example, in Apache, you can use the CustomLog directive to specify a log format that excludes the cookie header 
that contains the session ID.
Use secure cookies: Configure your web application to use the HttpOnly and Secure cookie attributes.
HttpOnly prevents client-side scripts, like JavaScript, from accessing the cookie. This protects against cross-site scripting (XSS) attacks, 
which could be used to steal session cookies.
Secure ensures the cookie is only sent over encrypted HTTPS connections, preventing eavesdropping and man-in-the-middle (MITM) attacks.
Regenerate session IDs: Session IDs should be regenerated after any privilege level change, 
such as a user logging in or escalating permissions.
Store session IDs as cookies, not in the URL: Passing a session ID in the URL (e.g., ?JSESSIONID=...) is an insecure practice. 
It makes the ID susceptible to being exposed in web server logs, HTTP referrer headers, and browser history.
Use a secure session ID generator: Generate session IDs using a cryptographically secure pseudorandom number generator (CSPRNG). 
Session IDs should be long and have high entropy to make them unpredictable and resistant to brute-force attacks.
Use a central, secure logging service: For highly distributed systems, forward logs to a centralized, 
hardened logging server. This prevents attackers from tampering with logs on compromised nodes. 
Detecting and investigating compromises
Even with proactive measures, it is crucial to have a plan for detecting and investigating compromises.
Monitor logs for unusual activity: Look for patterns that could indicate session hijacking, such as unusual user agents, 
frequent login attempts, or requests from unexpected IP addresses.
Hash session IDs in logs: As an alternative to completely omitting session IDs, 
some organizations log a one-way cryptographic hash of the session ID. This allows for activity tracking while preventing the 
actual ID from being exposed. This approach requires that the session ID is generated randomly and that a secure hash function is used.
Track user activity with linkable identifiers: Use non-sensitive, linkable identifiers to trace user activity across different logs. 
For example, Microsoft Entra logs can use a "Session ID" attribute to link activities without exposing the user's actual session token. 