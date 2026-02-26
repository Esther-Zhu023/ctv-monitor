#!/usr/bin/env python3
"""
简单的HTTP API服务器
可用于接收webhook触发或健康检查
"""

from flask import Flask, jsonify
import subprocess
import json
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'CTV Monitor'
    })

@app.route('/run', methods=['POST', 'GET'])
def run_monitor():
    """手动触发监控"""
    try:
        result = subprocess.run(
            ['python3', 'monitor.py'],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/report', methods=['GET'])
def get_report():
    """获取最新报告"""
    try:
        with open('reports/latest_report.json', 'r') as f:
            report = json.load(f)
        return jsonify(report)
    except FileNotFoundError:
        return jsonify({'error': 'Report not found'}), 404

@app.route('/status', methods=['GET'])
def status():
    """获取系统状态"""
    # 检查文件
    files_exist = {
        'monitor.py': os.path.exists('monitor.py'),
        'known_entities.json': os.path.exists('known_entities.json'),
        'reports': os.path.exists('reports'),
        'logs': os.path.exists('logs')
    }

    # 获取最新报告时间
    latest_report = None
    if os.path.exists('reports/latest_report.json'):
        with open('reports/latest_report.json', 'r') as f:
            report = json.load(f)
            latest_report = report.get('date') or report.get('report_date')

    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'files': files_exist,
        'latest_report': latest_report,
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
