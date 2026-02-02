from flask import Flask, request, jsonify
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process, Queue
import os
from email_verifier import EmailVerifier

app = Flask(__name__)

def run_spider(queue, domain, first_name, last_name):
    try:
        from scrapy.crawler import CrawlerRunner
        from twisted.internet import reactor
        from scrapy import signals
        from spiders.email_spider import EmailSpider

        results = []
        spider_instance = None

        def spider_opened(spider):
            nonlocal spider_instance
            spider_instance = spider

        def item_scraped(item, response, spider):
            results.append(dict(item))

        settings = {
            'CONCURRENT_REQUESTS': 2,
            'DOWNLOAD_DELAY': 1,
            'ROBOTSTXT_OBEY': True,
            'USER_AGENT': 'Mozilla/5.0 (compatible; EmailFinderBot/1.0)',
            'DEPTH_LIMIT': 3,
            'CLOSESPIDER_PAGECOUNT': 20,
            'LOG_LEVEL': 'WARNING',
        }

        runner = CrawlerRunner(settings)

        crawler = runner.create_crawler(EmailSpider)
        crawler.signals.connect(spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(item_scraped, signal=signals.item_scraped)

        d = runner.crawl(
            crawler,
            domain=domain,
            first_name=first_name,
            last_name=last_name
        )

        d.addBoth(lambda _: reactor.stop())
        reactor.run(installSignalHandlers=False)

        queue.put(results)
    except Exception as e:
        queue.put({'error': str(e)})


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

    queue = Queue()
    process = Process(target=run_spider, args=(queue, domain, first_name, last_name))
    process.start()
    process.join(timeout=60)

    if process.is_alive():
        process.terminate()
        return jsonify({'error': 'Scraping timeout'}), 504

    results = queue.get() if not queue.empty() else []

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
    process.join(timeout=60)

    if process.is_alive():
        process.terminate()
        return jsonify({'error': 'Scraping timeout'}), 504

    results = queue.get() if not queue.empty() else []

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
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
