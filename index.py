def app():
  from app import app as ap
  ap.run(host="0.0.0.0", port=80, debug=False)
