from flask import Flask, request, jsonify
import joblib
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Load the trained machine learning model
model = joblib.load('../models/phishing_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    # Get the JSON data sent from the extension
    data = request.get_json()

    # Convert the URL features into the format the model expects
    # (Here you will need to extract the necessary features from the URL)
    url_features = pd.DataFrame([data])

    # Make prediction using the loaded model
    prediction = model.predict(url_features)
    result = "Phishing" if prediction[0] == 1 else "Safe"

    # Return the result as JSON
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
