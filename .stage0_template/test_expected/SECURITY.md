# Security

## Security Features

The api_utils package implements several security measures to protect applications that use it:

### Authentication and Authorization
- **JWT-based authentication** - Token class validates JWT tokens with signature verification
- **Token validation** - JWT tokens are validated for signature, expiration, issuer, and audience
- **Fail-fast security** - The application will not start if JWT_SECRET is not explicitly configured

### Input Validation
- **Token header validation** - Authorization headers are validated for proper Bearer token format
- **JWT claim validation** - Standard JWT claims (iss, aud, exp) are validated when signature verification is enabled

### Configuration Security
- **Secret masking** - Secret values in config_items are automatically masked to prevent exposure in logs or API responses
- **Multi-source configuration** - Support for file-based, environment variable, and default configuration values
- **JWT_SECRET validation** - Prevents application startup with default/insecure JWT_SECRET

## Production Security Requirements

**CRITICAL: The following must be configured before deploying to production:**

### 1. JWT Configuration

**MUST** change `JWT_SECRET` from default value to a strong, randomly generated secret:

```bash
# Generate a secure random secret (example using openssl)
export JWT_SECRET=$(openssl rand -base64 32)
```

**MUST** configure `JWT_ISSUER` and `JWT_AUDIENCE` to match your identity provider:

```bash
export JWT_ISSUER="your-identity-provider"
export JWT_AUDIENCE="your-api-identifier"
```

### 2. Network Security

- **MUST** use HTTPS/TLS in production (configure via reverse proxy or load balancer)
- **SHOULD** restrict network access to API servers
- **SHOULD** use a reverse proxy (nginx, Traefik, etc.) for additional security layers
- **SHOULD** configure CORS policies appropriate for your deployment

### 3. MongoDB Security (if using MongoIO)

- **MUST** use authentication for MongoDB connections
- **MUST** use encrypted connections (TLS/SSL) for MongoDB
- **SHOULD** limit MongoDB user privileges to minimum required
- **SHOULD** use network isolation for MongoDB instances

### 4. Container Security (if deploying in containers)

- **SHOULD** run containers as non-root user
- **SHOULD** use read-only file systems where possible
- **SHOULD** limit container capabilities
- **SHOULD** scan container images for vulnerabilities
- **SHOULD** use secrets management for JWT_SECRET and connection strings

### 5. Monitoring and Logging

- **SHOULD** monitor for failed authentication attempts
- **SHOULD** log all authentication and authorization events
- **SHOULD** set up alerts for suspicious activity
- **SHOULD** regularly review logs for security issues

## Known Limitations and Security Considerations

### JWT Signature Verification

**Token class behavior:**
- Tokens are always verified with signature validation, issuer, and audience checks when `JWT_SECRET` is set
- Startup fails if `JWT_SECRET` is left at the insecure default; requests are rejected if `JWT_SECRET` is missing at runtime

**Production requirement:** Always configure `JWT_SECRET` with a strong secret from your secrets manager.

### Secret Management

- Secrets are masked in config_items tracking (showing "secret" instead of actual values)
- However, secrets are accessible via Config attributes (e.g., `config.JWT_SECRET`)
- Applications using api_utils must protect Config instances and not expose them via APIs

### Configuration Files

- Configuration files (when using file-based config) should have appropriate file permissions
- Secret files should be readable only by the application user
- Use environment variables or secure secret management systems in production

## Security Best Practices

### 1. Principle of Least Privilege

- Grant users only the minimum roles/claims needed
- Use RBAC in consuming applications to restrict access
- Run applications with minimal system privileges
- Use separate service accounts for different components

### 2. Defense in Depth

- Use multiple security layers (network, application, data)
- Implement monitoring and alerting
- Regular security audits and updates
- Keep dependencies up to date

### 3. Secure Configuration

- Use strong, randomly generated secrets
- Store secrets in secure secret management systems (not in code or config files)
- Rotate secrets regularly
- Use different secrets for different environments

### 4. Secure Development

- Review code changes for security implications
- Use security linters and static analysis tools
- Test with security in mind
- Follow secure coding practices

### 5. Monitoring and Incident Response

- Monitor authentication failures
- Log all security-relevant events
- Set up alerts for suspicious activity
- Have an incident response plan
- Regularly review security logs

## Threat Model

### What api_utils Protects Against

The package is designed to protect against:
- ✅ Unauthorized access (via JWT authentication when properly configured)
- ✅ Token forgery (via JWT signature verification)
- ✅ Secret exposure in logs (via secret masking in config_items)
- ✅ Accidental production deployment with default secrets (via fail-fast validation)

### What api_utils Does NOT Protect Against

The package does **NOT** protect against:
- ❌ Application-level authorization bugs (consuming applications must implement RBAC)
- ❌ MongoDB injection attacks (consuming applications must validate inputs)
- ❌ Network-based attacks (requires proper network configuration)
- ❌ Insider threats (users with valid tokens can access what their roles allow)
- ❌ Physical access to systems (requires system-level security)

## Consumer Application Responsibilities

Applications using api_utils are responsible for:

1. **Implementing authorization logic** - api_utils provides authentication, but applications must implement authorization (RBAC, permissions, etc.)

2. **Input validation** - Applications must validate all user inputs before processing

3. **Secure data handling** - Applications must protect sensitive data in databases and logs

4. **Error handling** - Applications must handle errors securely without exposing sensitive information

5. **Security testing** - Applications must test their own security including integration with api_utils

## Security Updates

### Updating api_utils

- Keep api_utils updated to get security fixes
- Review changelogs for security-related changes
- Test updates in non-production environments first
- Have a rollback plan for updates

### Dependency Management

- Regularly update dependencies (Flask, PyJWT, PyMongo, etc.)
- Monitor security advisories for dependencies
- Use dependency scanning tools
- Pin dependency versions for reproducible builds

## Reporting Security Issues

If you discover a security vulnerability in api_utils, please report it responsibly:

- **DO NOT** open a public GitHub issue
- Contact the maintainers directly
- Provide detailed information about the vulnerability
- Allow time for the issue to be addressed before public disclosure

## Security Checklist for Production Deployment

Use this checklist before deploying to production:

- [ ] JWT_SECRET is set to a strong, randomly generated value
- [ ] JWT_ISSUER and JWT_AUDIENCE are configured for your environment
- [ ] HTTPS/TLS is configured and enforced
- [ ] MongoDB uses authentication and encrypted connections
- [ ] Network access is restricted appropriately
- [ ] Secrets are stored in secure secret management system
- [ ] Monitoring and alerting are configured
- [ ] Logs are being collected and reviewed
- [ ] All dependencies are up to date
- [ ] Security testing has been performed
- [ ] Incident response plan is in place
- [ ] Backup and recovery procedures are tested

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [MongoDB Security Checklist](https://docs.mongodb.com/manual/administration/security-checklist/)
- [Flask Security Considerations](https://flask.palletsprojects.com/en/latest/security/)
