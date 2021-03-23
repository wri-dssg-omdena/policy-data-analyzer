from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/financial-incentives/', methods=['GET'])
def financial_incentives():
    return jsonify({
        "mexico": {
            "landscape restoration": [
                "policy_A.txt",
                "policy_B.txt",
            ],
            "reforestation": [
                "policy_C.txt",
                "policy_D.txt",
            ],
        },
        "guatemala": {
            "landscape restoration": [
                "policy_E.txt",
                "policy_F.txt",
            ],
            "reforestation": [
                "policy_G.txt",
            ],
        }
    })

@app.route('/policies/organizations/', methods=['GET'])
def policies_organizations():
    return jsonify({
        "mexico": {
            "PROFECO": [
                "policy_A.txt",
                "policy_B.txt",
            ],
            "CONAPRED": [
                "policy_A.txt",
                "policy_C.txt",
            ],
            "SEMARNAT": [
                "policy_B.txt",
                "policy_D.txt",
            ],
        },
    })

@app.route('/policies/topic-relevance/', methods=['GET'])
def policies_topic_relevance():
    return jsonify({
        "mexico": {
            "reforestation": {
                "policy_A.txt": 0.5,
                "policy_B.txt": 0.2,
            },
            "water": {
                "policy_A.txt": 0.3,
                "policy_B.txt": 0.4,
            },
            "landscape restoration": {
                "policy_A.txt": 0.7,
                "policy_B.txt": 0.7,
            },
        }
    })

'''
    Usage /policies/search?q=elephant%20rescue
    where %20 is a space
'''
@app.route('/policies/search', methods=['GET'])
def policies_search():
    return jsonify({
        "query": request.args.get('q'),
        "mexico": [
                "policy_A.txt",
                "policy_B.txt",
        ],
        "guatemala": [
                "policy_C.txt",
        ],
    })

if __name__ == '__main__':
    app.run()