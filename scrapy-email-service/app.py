from flask import Flask, request, jsonify
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process, Queue
import os
from email_verifier import EmailVerifier

app = Flask(__name__)

def run_spider(queue, domain, first_name, last_name):
    print(f"[run_spider] PROCESS STARTED - PID={os.getpid()}", flush=True)
    try:
        print(f"[run_spider] Importing dependencies...", flush=True)
        import sys
        from io import StringIO
        from scrapy.crawler import CrawlerRunner
        from scrapy import signals
        from twisted.internet import reactor, defer
        from spiders.email_spider import EmailSpider

        print(f"[run_spider] Dependencies imported successfully", flush=True)

        results = []
        print(f"[run_spider] Starting spider for {domain}, {first_name} {last_name}", flush=True)

        def item_scraped(item, response, spider):
            results.append(dict(item))
            print(f"[run_spider] Found email: {item.get('email')}", flush=True)

        def spider_opened(spider):
            print(f"[run_spider] Spider opened and starting to crawl", flush=True)

        def spider_closed(spider, reason):
            print(f"[run_spider] Spider closed: {reason}, found {len(results)} emails", flush=True)

        settings = {
            'CONCURRENT_REQUESTS': 4,
            'DOWNLOAD_DELAY': 0.5,
            'ROBOTSTXT_OBEY': False,  # Disable for testing
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'DEPTH_LIMIT': 2,
            'CLOSESPIDER_PAGECOUNT': 10,
            'DOWNLOAD_TIMEOUT': 15,
            'LOG_LEVEL': 'INFO',  # Changed from ERROR to see what's happening
            'RETRY_ENABLED': False,
            'REDIRECT_MAX_TIMES': 1,
            'CLOSESPIDER_TIMEOUT': 30,  # Force spider to close after 30 seconds
        }

        runner = CrawlerRunner(settings)
        crawler = runner.create_crawler(EmailSpider)
        crawler.signals.connect(item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider_closed, signal=signals.spider_closed)

        d = runner.crawl(
            crawler,
            domain=domain,
            first_name=first_name,
            last_name=last_name
        )

        d.addBoth(lambda _: reactor.stop())

        # Force stop reactor after 60 seconds as a safety measure
        def force_stop():
            print(f"[run_spider] Force stopping reactor after 60s timeout", flush=True)
            if reactor.running:
                reactor.stop()

        reactor.callLater(60, force_stop)

        print("[run_spider] Starting reactor...", flush=True)
        reactor.run(installSignalHandlers=False)
        print(f"[run_spider] Reactor stopped. Found {len(results)} results", flush=True)

        print(f"[run_spider] Putting {len(results)} results in queue", flush=True)
        queue.put(results)
        print(f"[run_spider] Results successfully queued", flush=True)
    except Exception as e:
        import traceback
        error_msg = f"[run_spider] EXCEPTION: {str(e)}"
        tb = traceback.format_exc()
        print(error_msg, flush=True)
        print(tb, flush=True)
        queue.put({'error': str(e), 'traceback': tb})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'scrapy-email-service'})


@app.route('/find-email', methods=['POST'])
def find_email():
    data = request.json

    first_name = data.get('firstName')
    last_name = data.get('lastName')
    domain = data.get('domain')

    if not all([first_name, last_name, domain]):
        return jsonify({'error': 'firstName, lastName, and domain are required'}), 400

    domain = domain.replace('https://', '').replace('http://', '').split('/')[0]

    print(f"[find-email] Searching for: {first_name} {last_name} @ {domain}", flush=True)

    queue = Queue()
    process = Process(target=run_spider, args=(queue, domain, first_name, last_name))
    process.start()
    process.join(timeout=120)  # Increased timeout

    if process.is_alive():
        print(f"[find-email] TIMEOUT after 120s for {domain}", flush=True)
        process.terminate()
        process.join()
        return jsonify({'error': 'Scraping timeout'}), 504

    try:
        if not queue.empty():
            results = queue.get(timeout=5)
            print(f"[endpoint] Got results from queue: {len(results) if isinstance(results, list) else 'error'}", flush=True)
        else:
            print(f"[endpoint] Queue is empty", flush=True)
            results = []
    except Exception as e:
        print(f"[endpoint] Error getting queue results: {e}", flush=True)
        results = []

    if isinstance(results, dict) and 'error' in results:
        return jsonify(results), 500

    if not results:
        return jsonify({
            'email': None,
            'confidence': 0,
            'source': 'scrapy',
            'message': 'No email found'
        })

    best_match = max(results, key=lambda x: x.get('match_score', 0))

    response = {
        'email': best_match['email'],
        'confidence': best_match['match_score'],
        'source': 'scrapy',
        'match_type': best_match.get('match_type', 'unknown'),
        'source_url': best_match.get('source_url', ''),
        'all_matches': results
    }

    return jsonify(response)


@app.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'error': 'email is required'}), 400

    result = EmailVerifier.verify_email(email)
    return jsonify(result)


@app.route('/verify-emails-batch', methods=['POST'])
def verify_emails_batch():
    data = request.json
    emails = data.get('emails', [])

    if not emails or not isinstance(emails, list):
        return jsonify({'error': 'emails array is required'}), 400

    results = EmailVerifier.verify_emails_batch(emails)
    return jsonify({'results': results})


@app.route('/find-and-verify', methods=['POST'])
def find_and_verify():
    data = request.json

    first_name = data.get('firstName')
    last_name = data.get('lastName')
    domain = data.get('domain')

    if not all([first_name, last_name, domain]):
        return jsonify({'error': 'firstName, lastName, and domain are required'}), 400

    domain = domain.replace('https://', '').replace('http://', '').split('/')[0]

    queue = Queue()
    process = Process(target=run_spider, args=(queue, domain, first_name, last_name))
    process.start()
    process.join(timeout=120)  # Increased timeout

    if process.is_alive():
        process.terminate()
        process.join()
        return jsonify({'error': 'Scraping timeout'}), 504

    try:
        if not queue.empty():
            results = queue.get(timeout=5)
            print(f"[endpoint] Got results from queue: {len(results) if isinstance(results, list) else 'error'}", flush=True)
        else:
            print(f"[endpoint] Queue is empty", flush=True)
            results = []
    except Exception as e:
        print(f"[endpoint] Error getting queue results: {e}", flush=True)
        results = []

    if isinstance(results, dict) and 'error' in results:
        return jsonify(results), 500

    if not results:
        return jsonify({
            'email': None,
            'confidence': 0,
            'verified': False,
            'source': 'scrapy',
            'message': 'No email found'
        })

    emails_to_verify = [r['email'] for r in results[:5]]
    verified_results = EmailVerifier.verify_emails_batch(emails_to_verify)

    best_verified = None
    for v_result in verified_results:
        if v_result['deliverable'] is True:
            best_verified = v_result
            break

    if not best_verified:
        best_verified = verified_results[0] if verified_results else None

    if best_verified:
        scraped_data = next((r for r in results if r['email'] == best_verified['email']), {})

        combined_confidence = (
            best_verified['confidence'] * 0.6 +
            scraped_data.get('match_score', 50) * 0.4
        )

        response = {
            'email': best_verified['email'],
            'confidence': int(combined_confidence),
            'source': 'scrapy+verification',
            'verified': best_verified['deliverable'],
            'dns_valid': best_verified['dns_valid'],
            'smtp_valid': best_verified['smtp_valid'],
            'match_type': scraped_data.get('match_type', 'unknown'),
            'source_url': scraped_data.get('source_url', ''),
            'verification_details': best_verified
        }

        return jsonify(response)

    return jsonify({
        'email': None,
        'confidence': 0,
        'verified': False,
        'source': 'scrapy',
        'message': 'No verified email found'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
