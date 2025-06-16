from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/temperature', methods=['GET','POST'])
def receive_temperature():
    data = request.get_json()
    # 예: {"temperature":24.5, "timestamp":"2025-05-22 15:00:00"}
    print("받은 데이터:", data)
    # 여기서 data를 DB에 저장하거나, 다른 로직을 실행하면 됩니다.
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    # 0.0.0.0 으로 바인딩해야 외부(같은 LAN)에서 접근 가능
    app.run(host='0.0.0.0', port=5000)
