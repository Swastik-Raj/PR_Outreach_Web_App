import re
import dns.resolver
import socket
import smtplib
from email.utils import parseaddr

class EmailVerifier:

    @staticmethod
    def is_valid_format(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def check_dns_mx(domain):
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return len(mx_records) > 0, [str(record.exchange) for record in mx_records]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
            return False, []
        except Exception as e:
            print(f"DNS check error for {domain}: {e}")
            return False, []

    @staticmethod
    def verify_smtp(email, mx_host, timeout=10):
        try:
            server = smtplib.SMTP(timeout=timeout)
            server.connect(mx_host)
            server.helo('emailverifier.local')
            server.mail('verify@emailverifier.local')
            code, message = server.rcpt(email)
            server.quit()

            return code == 250
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, socket.timeout):
            return None
        except Exception as e:
            print(f"SMTP verification error for {email}: {e}")
            return None

    @classmethod
    def verify_email(cls, email):
        result = {
            'email': email,
            'valid_format': False,
            'dns_valid': False,
            'smtp_valid': None,
            'mx_records': [],
            'deliverable': False,
            'confidence': 0
        }

        if not cls.is_valid_format(email):
            return result

        result['valid_format'] = True

        domain = email.split('@')[1]
        dns_valid, mx_records = cls.check_dns_mx(domain)
        result['dns_valid'] = dns_valid
        result['mx_records'] = mx_records

        if not dns_valid:
            result['confidence'] = 20
            return result

        if mx_records:
            primary_mx = mx_records[0].rstrip('.')
            smtp_result = cls.verify_smtp(email, primary_mx)
            result['smtp_valid'] = smtp_result

            if smtp_result is True:
                result['deliverable'] = True
                result['confidence'] = 95
            elif smtp_result is False:
                result['deliverable'] = False
                result['confidence'] = 30
            else:
                result['deliverable'] = None
                result['confidence'] = 70
        else:
            result['confidence'] = 60

        return result

    @classmethod
    def verify_emails_batch(cls, emails):
        results = []
        for email in emails:
            verification = cls.verify_email(email)
            results.append(verification)

        results.sort(key=lambda x: x['confidence'], reverse=True)
        return results
