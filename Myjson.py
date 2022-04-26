from flask import Flask,jsonify

app=Flask(__name__)

@app.route("/")
def main():
    return 'main method'

@app.route("/value/<string:n>")
def hello_wordld(n):
    return jsonify("asim")

# if __name__ == '__main__':
app.run(debug=True)