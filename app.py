"""Flask web application for VeriGov AI"""

from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_VERIFY_URL = "https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify-sources"


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/verify', methods=['POST'])
def verify():
    """Verify a claim via API Gateway -> Lambda"""
    data = request.json or {}
    claim = data.get('claim', '').strip()
    sources = data.get('sources', [])

    if not claim:
        return jsonify({'error': 'Claim is required'}), 400

    # Filter empty sources
    if not isinstance(sources, list):
        sources = []
    sources = [s.strip() for s in sources if isinstance(s, str) and s.strip()]

    try:
        payload = {
            "claim": claim,
            "sources": sources
        }

        response = requests.post(
            API_VERIFY_URL,
            json=payload,
            timeout=60
        )

        # If API Gateway/Lambda returns non-JSON error text
        try:
            result = response.json()
        except Exception:
            return jsonify({
                'error': 'Invalid response from verification API',
                'status_code': response.status_code,
                'raw_response': response.text[:1000]
            }), 502

        if response.status_code != 200:
            return jsonify({
                'error': 'Verification API returned an error',
                'status_code': response.status_code,
                'details': result
            }), response.status_code

        return jsonify(result)

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Verification request timed out'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/audit', methods=['GET'])
def audit():
    """Placeholder audit endpoint while using Lambda-backed verification"""
    return jsonify({
        'message': 'Audit is not available from local Flask when using API Gateway verification.'
    })


@app.route('/api/whitelist', methods=['GET'])
def whitelist():
    """Placeholder whitelist endpoint while using Lambda-backed verification"""
    return jsonify({
        'message': 'Whitelist is managed in the backend verification service.'
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)