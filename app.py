"""Flask web application for VeriGov AI"""

from flask import Flask, render_template, request, jsonify
from src.verigov.main import VeriGovApp

app = Flask(__name__)
verigov = VeriGovApp()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/verify', methods=['POST'])
def verify():
    """Verify a claim via API"""
    data = request.json
    claim = data.get('claim', '')
    sources = data.get('sources', [])
    
    if not claim:
        return jsonify({'error': 'Claim is required'}), 400
    
    # Filter empty sources
    sources = [s.strip() for s in sources if s.strip()]
    
    try:
        result = verigov.verify_claim(claim, sources if sources else None)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/audit', methods=['GET'])
def audit():
    """Get recent audit entries"""
    limit = request.args.get('limit', 10, type=int)
    entries = verigov.audit.query(limit=limit)
    return jsonify(entries)


@app.route('/api/whitelist', methods=['GET'])
def whitelist():
    """Get whitelisted sources"""
    return jsonify({'sources': verigov.whitelist.sources})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
