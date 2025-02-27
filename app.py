from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """Root endpoint that displays available API endpoints."""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
