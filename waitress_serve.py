from waitress import serve
from main import main

if __name__=='__main__':
    serve(main, host='0.0.0.0', port=8000)